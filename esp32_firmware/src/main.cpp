/*
 * JARVIS ESP32 Firmware
 * Handles wake button, LED status, and kill switch
 */

#include <Arduino.h>
#include <ArduinoJson.h>
#include <FastLED.h>

// Pin definitions
#define BUTTON_PIN 21        // Wake/kill button
#define LED_PIN 18           // NeoPixel data pin
#define NUM_LEDS 16          // Number of LEDs in ring

// Button debounce
#define DEBOUNCE_MS 50
#define LONG_PRESS_MS 3000

// LED settings
#define LED_BRIGHTNESS 128

// Objects
CRGB leds[NUM_LEDS];

// State variables
unsigned long lastButtonPress = 0;
unsigned long buttonPressStart = 0;
bool buttonPressed = false;
bool longPressTriggered = false;

// LED state
enum LEDState {
    STATE_IDLE,
    STATE_LISTENING,
    STATE_THINKING,
    STATE_SPEAKING,
    STATE_ERROR
};

LEDState currentState = STATE_IDLE;

// Function prototypes
void handleButton();
void updateLEDs();
void processSerialCommand();
void sendEvent(const char* eventName);
void setLEDColor(CRGB color);
void breathingEffect(CRGB color);

void setup() {
    // Initialize serial
    Serial.begin(115200);
    while (!Serial && millis() < 3000); // Wait max 3s for serial
    
    Serial.println("JARVIS ESP32 Starting...");
    
    // Initialize button
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    // Initialize LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(LED_BRIGHTNESS);
    setLEDColor(CRGB::Blue);  // Idle = Blue
    
    Serial.println("✓ JARVIS ESP32 Ready");
    
    // Send ready event
    sendEvent("READY");
}

void loop() {
    // Handle button input
    handleButton();
    
    // Update LED effects
    updateLEDs();
    
    // Process serial commands from PC
    if (Serial.available()) {
        processSerialCommand();
    }
    
    delay(10);  // Small delay for stability
}

void handleButton() {
    bool buttonState = digitalRead(BUTTON_PIN) == LOW;  // Active LOW with pullup
    
    unsigned long now = millis();
    
    // Debounce
    if (buttonState && !buttonPressed && (now - lastButtonPress > DEBOUNCE_MS)) {
        // Button pressed
        buttonPressed = true;
        buttonPressStart = now;
        longPressTriggered = false;
        lastButtonPress = now;
        
        Serial.println("Button pressed");
    }
    
    // Check for long press
    if (buttonPressed && !longPressTriggered && (now - buttonPressStart > LONG_PRESS_MS)) {
        // Long press = Kill switch
        longPressTriggered = true;
        Serial.println("Long press detected");
        sendEvent("KILL_SWITCH");
        
        // Flash red
        for (int i = 0; i < 3; i++) {
            setLEDColor(CRGB::Red);
            delay(200);
            setLEDColor(CRGB::Black);
            delay(200);
        }
        setLEDColor(CRGB::Blue);  // Back to idle
    }
    
    // Button released
    if (!buttonState && buttonPressed) {
        buttonPressed = false;
        unsigned long pressDuration = now - buttonPressStart;
        
        Serial.print("Button released after ");
        Serial.print(pressDuration);
        Serial.println(" ms");
        
        // If not long press, send wake event
        if (!longPressTriggered) {
            sendEvent("WAKE_BUTTON");
        }
    }
}

void updateLEDs() {
    // Implement breathing effect for some states
    if (currentState == STATE_LISTENING || currentState == STATE_THINKING) {
        static unsigned long lastUpdate = 0;
        static uint8_t brightness = 128;
        static int8_t direction = 1;
        
        if (millis() - lastUpdate > 20) {
            brightness += direction * 5;
            
            if (brightness >= 255 || brightness <= 50) {
                direction *= -1;
            }
            
            FastLED.setBrightness(brightness);
            FastLED.show();
            lastUpdate = millis();
        }
    } else {
        FastLED.setBrightness(LED_BRIGHTNESS);
    }
}

void processSerialCommand() {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() == 0) return;
    
    // Parse JSON
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, line);
    
    if (error) {
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        return;
    }
    
    const char* cmd = doc["cmd"];
    
    if (strcmp(cmd, "LED") == 0) {
        // LED command
        const char* state = doc["data"]["state"];
        
        if (strcmp(state, "IDLE") == 0) {
            currentState = STATE_IDLE;
            setLEDColor(CRGB::Blue);
        }
        else if (strcmp(state, "LISTENING") == 0) {
            currentState = STATE_LISTENING;
            setLEDColor(CRGB::Green);
        }
        else if (strcmp(state, "THINKING") == 0) {
            currentState = STATE_THINKING;
            setLEDColor(CRGB::Yellow);
        }
        else if (strcmp(state, "SPEAKING") == 0) {
            currentState = STATE_SPEAKING;
            setLEDColor(CRGB::Red);
        }
        else if (strcmp(state, "ERROR") == 0) {
            currentState = STATE_ERROR;
            setLEDColor(CRGB::DarkRed);
        }
        
        Serial.print("LED state set to: ");
        Serial.println(state);
    }
    else if (strcmp(cmd, "PING") == 0) {
        // Respond to ping
        StaticJsonDocument<128> response;
        response["type"] = "PONG";
        response["timestamp"] = millis();
        
        serializeJson(response, Serial);
        Serial.println();
    }
    else if (strcmp(cmd, "BUZZER") == 0) {
        // Buzzer command (not implemented, just acknowledge)
        Serial.println("Buzzer command received (not implemented)");
    }
}

void sendEvent(const char* eventName) {
    StaticJsonDocument<128> doc;
    doc["type"] = "EVENT";
    doc["event"] = eventName;
    doc["timestamp"] = millis();
    
    serializeJson(doc, Serial);
    Serial.println();
}

void setLEDColor(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}
