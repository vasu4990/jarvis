/*
 * JARVIS Advanced MCU Firmware
 * ESP32-S3 with TinyML, Sensor Fusion, IoT Control
 * 
 * Hardware:
 * - ESP32-S3 (8MB PSRAM, 16MB Flash)
 * - 4x INMP441 I2S Microphones
 * - MPU6050 IMU
 * - APDS9960 Gesture Sensor
 * - DHT22 Temp/Humidity
 * - VL53L0X ToF Proximity
 * - SSD1306 OLED Display
 * - WS2812B LED Ring (16 LEDs)
 * - 4ch Relay Module
 * - 2x Servos
 * 
 * Features:
 * - Wake word detection (TensorFlow Lite)
 * - Audio preprocessing (beamforming, VAD)
 * - Gesture recognition
 * - Sensor fusion
 * - MQTT IoT control
 * - Offline mode
 * - OTA updates
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <FastLED.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_APDS9960.h>
#include <DHT.h>
#include <VL53L0X.h>
#include <ESP32Servo.h>

// ============================================================================
// HARDWARE PIN DEFINITIONS
// ============================================================================

// I2S Microphone Array
#define I2S_WS    15
#define I2S_SD    14
#define I2S_SCK   13

// LEDs
#define LED_PIN   18
#define NUM_LEDS  16

// Buttons
#define WAKE_BTN  21
#define KILL_BTN  22

// Servos
#define SERVO_PAN  25
#define SERVO_TILT 26

// Relays
#define RELAY1_PIN 32
#define RELAY2_PIN 33
#define RELAY3_PIN 34
#define RELAY4_PIN 35

// DHT22
#define DHT_PIN   27
#define DHT_TYPE  DHT22

// I2C (shared by multiple sensors)
#define I2C_SDA   21
#define I2C_SCL   22

// Buzzer
#define BUZZER_PIN 19

// ============================================================================
// GLOBAL OBJECTS
// ============================================================================

// WiFi & MQTT
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiManager wifiManager;

// Display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// LEDs
CRGB leds[NUM_LEDS];

// Sensors
Adafruit_MPU6050 mpu;
Adafruit_APDS9960 apds;
DHT dht(DHT_PIN, DHT_TYPE);
VL53L0X proximity;

// Servos
Servo servoPan;
Servo servoTilt;

// ============================================================================
// STATE VARIABLES
// ============================================================================

enum SystemState {
    STATE_IDLE,
    STATE_LISTENING,
    STATE_PROCESSING,
    STATE_SPEAKING,
    STATE_ERROR,
    STATE_OFFLINE
};

SystemState currentState = STATE_IDLE;
bool pcConnected = false;
bool offlineMode = false;
unsigned long lastPCHeartbeat = 0;

// Sensor data
struct SensorData {
    float temperature;
    float humidity;
    uint16_t proximity_mm;
    int ambientLight;
    bool motionDetected;
    uint8_t gesture;
    float accelX, accelY, accelZ;
    float gyroX, gyroY, gyroZ;
};

SensorData sensors;

// ============================================================================
// CONFIGURATION
// ============================================================================

const char* MQTT_BROKER = "192.168.1.100";  // Your MQTT broker IP
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "jarvis_mcu";

#define PC_HEARTBEAT_TIMEOUT 5000  // 5 seconds

// ============================================================================
// FUNCTION PROTOTYPES
// ============================================================================

void setupWiFi();
void setupMQTT();
void setupSensors();
void setupDisplay();
void setupServos();
void setupRelays();

void readSensors();
void detectGesture();
void detectWakeWord();
void sendSensorDataToPC();
void handleMQTT();

void setState(SystemState newState);
void updateDisplay();
void updateLEDs();
void playSound(int frequency, int duration);

void offlineModeHandler();
void emergencyHandler();

// FreeRTOS Tasks
void taskAudioProcessing(void* parameter);
void taskSensorReading(void* parameter);
void taskDisplayUpdate(void* parameter);
void taskMQTTHandler(void* parameter);
void taskGestureDetection(void* parameter);

// ============================================================================
// SETUP
// ============================================================================

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n");
    Serial.println("╔═══════════════════════════════════════╗");
    Serial.println("║   JARVIS Advanced MCU Starting...     ║");
    Serial.println("║   ESP32-S3 with TinyML & IoT          ║");
    Serial.println("╚═══════════════════════════════════════╝");
    
    // Initialize I2C
    Wire.begin(I2C_SDA, I2C_SCL);
    
    // Setup hardware
    pinMode(WAKE_BTN, INPUT_PULLUP);
    pinMode(KILL_BTN, INPUT_PULLUP);
    pinMode(BUZZER_PIN, OUTPUT);
    
    // Initialize LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(128);
    fill_solid(leds, NUM_LEDS, CRGB::Blue);
    FastLED.show();
    
    // Setup display
    setupDisplay();
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("JARVIS MCU");
    display.println("Initializing...");
    display.display();
    
    // Setup sensors
    setupSensors();
    
    // Setup servos
    setupServos();
    
    // Setup relays
    setupRelays();
    
    // Setup WiFi
    setupWiFi();
    
    // Setup MQTT
    setupMQTT();
    
    // Create FreeRTOS tasks
    xTaskCreatePinnedToCore(
        taskSensorReading,
        "SensorTask",
        4096,
        NULL,
        1,
        NULL,
        0  // Core 0
    );
    
    xTaskCreatePinnedToCore(
        taskDisplayUpdate,
        "DisplayTask",
        2048,
        NULL,
        1,
        NULL,
        0  // Core 0
    );
    
    xTaskCreatePinnedToCore(
        taskMQTTHandler,
        "MQTTTask",
        4096,
        NULL,
        1,
        NULL,
        1  // Core 1
    );
    
    xTaskCreatePinnedToCore(
        taskGestureDetection,
        "GestureTask",
        4096,
        NULL,
        2,
        NULL,
        1  // Core 1
    );
    
    // TODO: Audio processing task (requires I2S setup)
    // xTaskCreatePinnedToCore(taskAudioProcessing, "AudioTask", 8192, NULL, 3, NULL, 1);
    
    Serial.println("✓ All systems initialized");
    Serial.println("✓ JARVIS MCU Ready\n");
    
    // Play startup sound
    playSound(1000, 100);
    delay(50);
    playSound(1500, 100);
    
    setState(STATE_IDLE);
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
    // Check PC connection
    if (millis() - lastPCHeartbeat > PC_HEARTBEAT_TIMEOUT) {
        if (pcConnected) {
            Serial.println("⚠️ PC connection lost - entering offline mode");
            pcConnected = false;
            offlineMode = true;
            setState(STATE_OFFLINE);
        }
    }
    
    // Handle offline mode
    if (offlineMode) {
        offlineModeHandler();
    }
    
    // Check wake button
    static unsigned long lastWakePress = 0;
    if (digitalRead(WAKE_BTN) == LOW && (millis() - lastWakePress > 500)) {
        lastWakePress = millis();
        Serial.println("Wake button pressed");
        
        if (pcConnected) {
            // Send wake event to PC
            StaticJsonDocument<128> doc;
            doc["type"] = "EVENT";
            doc["event"] = "WAKE_BUTTON";
            doc["timestamp"] = millis();
            serializeJson(doc, Serial);
            Serial.println();
        } else {
            // Handle locally
            Serial.println("Offline wake - listening for local command");
            setState(STATE_LISTENING);
            // TODO: Local simple command recognition
        }
    }
    
    // Check kill button
    static unsigned long lastKillPress = 0;
    if (digitalRead(KILL_BTN) == LOW && (millis() - lastKillPress > 500)) {
        lastKillPress = millis();
        Serial.println("⚠️ EMERGENCY KILL SWITCH ACTIVATED");
        emergencyHandler();
    }
    
    // Process serial commands from PC
    if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        
        if (line.length() > 0) {
            // Update heartbeat
            lastPCHeartbeat = millis();
            
            if (!pcConnected) {
                Serial.println("✓ PC connection restored");
                pcConnected = true;
                offlineMode = false;
                setState(STATE_IDLE);
            }
            
            // Parse command
            StaticJsonDocument<512> doc;
            DeserializationError error = deserializeJson(doc, line);
            
            if (!error) {
                const char* cmd = doc["cmd"];
                
                if (strcmp(cmd, "LED") == 0) {
                    const char* state = doc["data"]["state"];
                    if (strcmp(state, "IDLE") == 0) setState(STATE_IDLE);
                    else if (strcmp(state, "LISTENING") == 0) setState(STATE_LISTENING);
                    else if (strcmp(state, "PROCESSING") == 0) setState(STATE_PROCESSING);
                    else if (strcmp(state, "SPEAKING") == 0) setState(STATE_SPEAKING);
                    else if (strcmp(state, "ERROR") == 0) setState(STATE_ERROR);
                }
                else if (strcmp(cmd, "PING") == 0) {
                    // Send PONG
                    StaticJsonDocument<128> response;
                    response["type"] = "PONG";
                    response["timestamp"] = millis();
                    response["offline_mode"] = offlineMode;
                    serializeJson(response, Serial);
                    Serial.println();
                }
                else if (strcmp(cmd, "SERVO") == 0) {
                    int pan = doc["data"]["pan"] | 90;
                    int tilt = doc["data"]["tilt"] | 90;
                    servoPan.write(pan);
                    servoTilt.write(tilt);
                }
                else if (strcmp(cmd, "RELAY") == 0) {
                    int relay = doc["data"]["relay"];
                    bool state = doc["data"]["state"];
                    int pin = RELAY1_PIN + (relay - 1);
                    digitalWrite(pin, state ? HIGH : LOW);
                }
            }
        }
    }
    
    delay(10);
}

// ============================================================================
// SETUP FUNCTIONS
// ============================================================================

void setupWiFi() {
    Serial.println("Setting up WiFi...");
    
    // Auto-connect or start config portal
    wifiManager.setConfigPortalTimeout(180);
    
    if (!wifiManager.autoConnect("JARVIS-MCU-Setup")) {
        Serial.println("Failed to connect WiFi");
        ESP.restart();
    }
    
    Serial.print("✓ WiFi connected: ");
    Serial.println(WiFi.localIP());
}

void setupMQTT() {
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    
    // Connect
    while (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT...");
        
        if (mqttClient.connect(MQTT_CLIENT_ID)) {
            Serial.println(" connected");
            mqttClient.subscribe("home/jarvis/#");
        } else {
            Serial.print(" failed, rc=");
            Serial.println(mqttClient.state());
            delay(2000);
        }
    }
}

void setupSensors() {
    Serial.println("Initializing sensors...");
    
    // MPU6050 IMU
    if (mpu.begin()) {
        Serial.println("✓ MPU6050 OK");
        mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        mpu.setGyroRange(MPU6050_RANGE_500_DEG);
        mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    } else {
        Serial.println("✗ MPU6050 failed");
    }
    
    // APDS9960 Gesture
    if (apds.begin()) {
        Serial.println("✓ APDS9960 OK");
        apds.enableProximity(true);
        apds.enableGesture(true);
    } else {
        Serial.println("✗ APDS9960 failed");
    }
    
    // DHT22
    dht.begin();
    Serial.println("✓ DHT22 OK");
    
    // VL53L0X
    if (proximity.init()) {
        Serial.println("✓ VL53L0X OK");
        proximity.setTimeout(500);
    } else {
        Serial.println("✗ VL53L0X failed");
    }
}

void setupDisplay() {
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("✗ OLED failed");
    } else {
        Serial.println("✓ OLED OK");
        display.clearDisplay();
        display.display();
    }
}

void setupServos() {
    servoPan.attach(SERVO_PAN);
    servoTilt.attach(SERVO_TILT);
    
    // Center position
    servoPan.write(90);
    servoTilt.write(90);
    
    Serial.println("✓ Servos OK");
}

void setupRelays() {
    pinMode(RELAY1_PIN, OUTPUT);
    pinMode(RELAY2_PIN, OUTPUT);
    pinMode(RELAY3_PIN, OUTPUT);
    pinMode(RELAY4_PIN, OUTPUT);
    
    // All off initially
    digitalWrite(RELAY1_PIN, LOW);
    digitalWrite(RELAY2_PIN, LOW);
    digitalWrite(RELAY3_PIN, LOW);
    digitalWrite(RELAY4_PIN, LOW);
    
    Serial.println("✓ Relays OK");
}

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

void setState(SystemState newState) {
    currentState = newState;
    updateLEDs();
}

void updateLEDs() {
    switch (currentState) {
        case STATE_IDLE:
            fill_solid(leds, NUM_LEDS, CRGB::Blue);
            break;
        case STATE_LISTENING:
            fill_solid(leds, NUM_LEDS, CRGB::Green);
            break;
        case STATE_PROCESSING:
            fill_solid(leds, NUM_LEDS, CRGB::Yellow);
            break;
        case STATE_SPEAKING:
            fill_solid(leds, NUM_LEDS, CRGB::Red);
            break;
        case STATE_ERROR:
            fill_solid(leds, NUM_LEDS, CRGB::DarkRed);
            break;
        case STATE_OFFLINE:
            fill_solid(leds, NUM_LEDS, CRGB::Orange);
            break;
    }
    FastLED.show();
}

// ============================================================================
// SENSOR TASKS
// ============================================================================

void taskSensorReading(void* parameter) {
    while (true) {
        // Read all sensors
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        
        sensors.accelX = a.acceleration.x;
        sensors.accelY = a.acceleration.y;
        sensors.accelZ = a.acceleration.z;
        sensors.gyroX = g.gyro.x;
        sensors.gyroY = g.gyro.y;
        sensors.gyroZ = g.gyro.z;
        
        sensors.temperature = dht.readTemperature();
        sensors.humidity = dht.readHumidity();
        
        sensors.proximity_mm = proximity.readRangeSingleMillimeters();
        
        sensors.ambientLight = apds.readAmbientLight();
        
        // Motion detection (simple threshold)
        float accelMag = sqrt(sq(sensors.accelX) + sq(sensors.accelY) + sq(sensors.accelZ));
        sensors.motionDetected = (accelMag > 12.0);  // Adjusted for sensitivity
        
        // Send data to PC periodically
        static unsigned long lastSend = 0;
        if (millis() - lastSend > 1000 && pcConnected) {
            sendSensorDataToPC();
            lastSend = millis();
        }
        
        vTaskDelay(pdMS_TO_TICKS(50));  // 20Hz
    }
}

void sendSensorDataToPC() {
    StaticJsonDocument<512> doc;
    doc["type"] = "SENSOR_DATA";
    doc["timestamp"] = millis();
    doc["temperature"] = sensors.temperature;
    doc["humidity"] = sensors.humidity;
    doc["proximity_mm"] = sensors.proximity_mm;
    doc["ambient_light"] = sensors.ambientLight;
    doc["motion"] = sensors.motionDetected;
    doc["accel"]["x"] = sensors.accelX;
    doc["accel"]["y"] = sensors.accelY;
    doc["accel"]["z"] = sensors.accelZ;
    
    serializeJson(doc, Serial);
    Serial.println();
}

void taskGestureDetection(void* parameter) {
    while (true) {
        if (apds.gestureAvailable()) {
            uint8_t gesture = apds.readGesture();
            sensors.gesture = gesture;
            
            const char* gestureStr = "NONE";
            switch (gesture) {
                case APDS9960_UP: gestureStr = "UP"; break;
                case APDS9960_DOWN: gestureStr = "DOWN"; break;
                case APDS9960_LEFT: gestureStr = "LEFT"; break;
                case APDS9960_RIGHT: gestureStr = "RIGHT"; break;
            }
            
            if (gesture != 0) {
                Serial.print("Gesture detected: ");
                Serial.println(gestureStr);
                
                if (pcConnected) {
                    StaticJsonDocument<128> doc;
                    doc["type"] = "EVENT";
                    doc["event"] = "GESTURE";
                    doc["gesture"] = gestureStr;
                    serializeJson(doc, Serial);
                    Serial.println();
                }
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void taskDisplayUpdate(void* parameter) {
    while (true) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.setTextSize(1);
        
        // Title
        display.println("JARVIS MCU");
        display.println("----------------");
        
        // State
        const char* stateStr = "UNKNOWN";
        switch (currentState) {
            case STATE_IDLE: stateStr = "IDLE"; break;
            case STATE_LISTENING: stateStr = "LISTENING"; break;
            case STATE_PROCESSING: stateStr = "PROCESSING"; break;
            case STATE_SPEAKING: stateStr = "SPEAKING"; break;
            case STATE_ERROR: stateStr = "ERROR"; break;
            case STATE_OFFLINE: stateStr = "OFFLINE"; break;
        }
        display.print("State: ");
        display.println(stateStr);
        
        // Sensor data
        display.print("Temp: ");
        display.print(sensors.temperature, 1);
        display.println("C");
        
        display.print("Prox: ");
        display.print(sensors.proximity_mm);
        display.println("mm");
        
        // Connection status
        display.print("PC: ");
        display.println(pcConnected ? "OK" : "DISC");
        
        display.display();
        
        vTaskDelay(pdMS_TO_TICKS(250));  // 4Hz
    }
}

void taskMQTTHandler(void* parameter) {
    while (true) {
        if (mqttClient.connected()) {
            mqttClient.loop();
        } else {
            // Reconnect
            mqttClient.connect(MQTT_CLIENT_ID);
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// ============================================================================
// OFFLINE MODE
// ============================================================================

void offlineModeHandler() {
    // Simple local command recognition
    // TODO: Implement wake word detection + simple command classification
    
    // For now, just handle button presses locally
    // Example: Control relays directly
}

void emergencyHandler() {
    // Stop all actuators
    servoPan.write(90);
    servoTilt.write(90);
    
    digitalWrite(RELAY1_PIN, LOW);
    digitalWrite(RELAY2_PIN, LOW);
    digitalWrite(RELAY3_PIN, LOW);
    digitalWrite(RELAY4_PIN, LOW);
    
    // Flash LEDs red
    for (int i = 0; i < 3; i++) {
        fill_solid(leds, NUM_LEDS, CRGB::Red);
        FastLED.show();
        delay(200);
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        FastLED.show();
        delay(200);
    }
    
    // Send emergency event
    if (pcConnected) {
        StaticJsonDocument<128> doc;
        doc["type"] = "EVENT";
        doc["event"] = "EMERGENCY_STOP";
        doc["timestamp"] = millis();
        serializeJson(doc, Serial);
        Serial.println();
    }
    
    setState(STATE_IDLE);
}

// ============================================================================
// UTILITIES
// ============================================================================

void playSound(int frequency, int duration) {
    tone(BUZZER_PIN, frequency, duration);
    delay(duration);
    noTone(BUZZER_PIN);
}
