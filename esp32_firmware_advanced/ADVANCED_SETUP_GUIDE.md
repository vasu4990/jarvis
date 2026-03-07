# 🚀 Advanced MCU JARVIS - Complete Setup Guide

## Overview

This guide will help you build an **advanced MCU-based JARVIS** with:
- Wake word detection on-device
- Sensor fusion (IMU, gesture, environment)
- IoT control hub (MQTT)
- Offline intelligence
- Real-time actuation

---

## 📦 Required Components

### Core (Essential)
| Item | Specs | Qty | Est. Cost |
|------|-------|-----|-----------|
| ESP32-S3 DevKit | 8MB PSRAM, 16MB Flash | 1 | $15 |
| INMP441 I2S Mic | Digital microphone | 4 | $20 |
| MPU6050 | 6-axis IMU | 1 | $3 |
| APDS9960 | Gesture + Light + Proximity | 1 | $5 |
| DHT22 | Temperature + Humidity | 1 | $5 |
| VL53L0X | ToF Distance sensor | 1 | $6 |
| SSD1306 OLED | 128x64 I2C display | 1 | $8 |
| WS2812B LED Ring | 16 pixels | 1 | $8 |
| 4-ch Relay Module | 5V/10A relays | 1 | $5 |
| **Subtotal** | | | **$75** |

### Actuation
| Item | Specs | Qty | Est. Cost |
|------|-------|-----|-----------|
| SG90 Servo | Micro servo motor | 2 | $4 |
| Buzzer | 5V active buzzer | 1 | $1 |
| Vibration motor | 3V coin motor | 1 | $2 |
| **Subtotal** | | | **$7** |

### Audio Output (Optional)
| Item | Specs | Qty | Est. Cost |
|------|-------|-----|-----------|
| MAX98357A | I2S amplifier | 1 | $5 |
| Speaker | 4Ω 3W | 1 | $3 |
| **Subtotal** | | | **$8** |

### Power & Connectivity
| Item | Specs | Qty | Est. Cost |
|------|-------|-----|-----------|
| 5V 3A Power Supply | Barrel jack | 1 | $10 |
| Breadboard | 830 points | 1 | $5 |
| Jumper wires | Male-female, male-male | 1 set | $5 |
| **Subtotal** | | | **$20** |

### Advanced (Optional)
| Item | Purpose | Cost |
|------|---------|------|
| ESP32-CAM | Vision processing | $10 |
| PN532 NFC | Authentication | $8 |
| SD Card Module | Data logging | $3 |
| 18650 Battery + Holder | Offline power | $15 |
| 3D Printed Enclosure | Housing | $20 |

**Total Core Build**: ~$110
**Total with Optional**: ~$160

---

## 🔌 Wiring Diagram

### I2C Bus (Shared - SDA=GPIO21, SCL=GPIO22)
Connect all I2C devices in parallel:
```
ESP32 SDA (21) → MPU6050 SDA → APDS9960 SDA → OLED SDA → VL53L0X SDA
ESP32 SCL (22) → MPU6050 SCL → APDS9960 SCL → OLED SCL → VL53L0X SCL
ESP32 3.3V → All sensor VCC
ESP32 GND → All sensor GND
```

### I2S Microphone Array
```
INMP441 Mic 1:
  VDD → 3.3V
  GND → GND
  SD → GPIO14
  WS → GPIO15
  SCK → GPIO13
  L/R → GND (left channel)

INMP441 Mic 2,3,4:
  (Connect in parallel for beamforming)
  SD → separate GPIO (e.g., 12, 27, 26)
```

### LED Ring (WS2812B)
```
ESP32 GPIO18 → DIN (via 330Ω resistor)
5V → VCC
GND → GND
+ 1000µF capacitor between VCC and GND
```

### Relays (4-channel module)
```
ESP32 GPIO32 → IN1
ESP32 GPIO33 → IN2
ESP32 GPIO34 → IN3
ESP32 GPIO35 → IN4
ESP32 5V → VCC
ESP32 GND → GND
```

### Servos
```
Servo Pan:
  Signal → GPIO25
  VCC → 5V
  GND → GND

Servo Tilt:
  Signal → GPIO26
  VCC → 5V
  GND → GND
```

### Buttons
```
Wake Button:
  One side → GPIO21
  Other side → GND
  (Internal pull-up enabled)

Kill Button:
  One side → GPIO22
  Other side → GND
```

### DHT22
```
VCC → 3.3V
Data → GPIO27
GND → GND
+ 10kΩ pull-up resistor between Data and VCC
```

### Buzzer
```
+ → GPIO19
- → GND
```

---

## 💻 Software Setup

### 1. Install PlatformIO

**Option A: VSCode Extension**
1. Install VSCode
2. Install "PlatformIO IDE" extension
3. Restart VSCode

**Option B: CLI**
```bash
pip install platformio
```

### 2. Clone & Build

```bash
cd jarvis/esp32_firmware_advanced

# Build firmware
pio run

# Upload to ESP32
pio run --target upload

# Monitor serial output
pio device monitor
```

### 3. First Boot Configuration

On first boot, ESP32 creates WiFi AP:
```
SSID: JARVIS-MCU-Setup
Password: (none)
```

1. Connect to this network
2. Browser opens automatically to config portal
3. Enter your WiFi credentials
4. Save & reboot

### 4. Configure MQTT Broker

Edit `src/main.cpp`:
```cpp
const char* MQTT_BROKER = "192.168.1.100";  // Your broker IP
```

**Don't have MQTT broker?**

Install Mosquitto:
```bash
# Windows (Chocolatey)
choco install mosquitto

# Ubuntu/Debian
sudo apt install mosquitto mosquitto-clients

# macOS
brew install mosquitto
```

Start broker:
```bash
mosquitto -v
```

---

## 🧠 TinyML Wake Word Training

### Using Edge Impulse (Recommended)

1. **Create Account**
   - Go to [edgeimpulse.com](https://edgeimpulse.com)
   - Create free account
   - Create new project "JARVIS Wake Word"

2. **Collect Data**
   - Use Edge Impulse CLI or mobile app
   - Record 100+ samples of "Hey Jarvis"
   - Record 100+ samples of background noise
   - Split: 80% training, 20% testing

3. **Design Impulse**
   - Time series data (1000ms window, 500ms stride)
   - Processing block: MFCC (Audio)
   - Learning block: Classification (Keras)

4. **Train Model**
   - Click "Start Training"
   - Wait 5-10 minutes
   - Check accuracy (target: >95%)

5. **Export for ESP32**
   - Deployment tab
   - Select "Arduino library"
   - Download ZIP

6. **Install Library**
   ```bash
   # Extract to Arduino libraries folder
   unzip ei-jarvis-wakeword-arduino-1.0.0.zip -d ~/Arduino/libraries/
   ```

7. **Integrate into Firmware**
   ```cpp
   #include <jarvis-wakeword_inferencing.h>
   
   // In taskAudioProcessing()
   void detectWakeWord() {
       signal_t signal;
       signal.total_length = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE;
       signal.get_data = &get_audio_signal_data;
       
       ei_impulse_result_t result = {0};
       EI_IMPULSE_ERROR r = run_classifier(&signal, &result, false);
       
       if (r == EI_IMPULSE_OK) {
           if (result.classification[0].value > 0.8) {  // "Hey Jarvis"
               Serial.println("Wake word detected!");
               sendWakeEventToPC();
           }
       }
   }
   ```

---

## 🎯 Testing Each Subsystem

### Test 1: LED Ring
```cpp
// Should show blue LEDs
// Upload firmware and observe
```

### Test 2: OLED Display
```
Display should show:
JARVIS MCU
--------------
State: IDLE
Temp: 25.3C
Prox: 1234mm
PC: DISC
```

### Test 3: Sensors
Monitor serial output:
```json
{
  "type": "SENSOR_DATA",
  "temperature": 25.3,
  "humidity": 45.2,
  "proximity_mm": 1234,
  "ambient_light": 450,
  "motion": false,
  "accel": {"x": 0.1, "y": 0.2, "z": 9.8}
}
```

### Test 4: Gestures
Wave hand over APDS9960:
```
Gesture detected: RIGHT
Gesture detected: LEFT
```

### Test 5: Relays
Send command via Serial Monitor:
```json
{"cmd": "RELAY", "data": {"relay": 1, "state": true}}
```
Relay 1 should click ON.

### Test 6: Servos
```json
{"cmd": "SERVO", "data": {"pan": 45, "tilt": 60}}
```
Servos should move to 45° and 60°.

### Test 7: MQTT
Subscribe to topics:
```bash
mosquitto_sub -h localhost -t "home/jarvis/#" -v
```

ESP32 should publish status.

---

## 🔗 PC Integration

### Update PC Bridge

Edit `mcu_bridge/serial_bridge.py`:

```python
async def _handle_message(self, message: dict):
    msg_type = message.get("type", "")
    
    if msg_type == "SENSOR_DATA":
        # Store sensor context
        self.sensor_context = message
        logger.info("Sensor data updated", temp=message.get("temperature"))
        
    elif msg_type == "EVENT":
        event_name = message.get("event", "")
        
        if event_name == "GESTURE":
            # Handle gesture
            gesture = message.get("gesture")
            await self.handle_gesture(gesture)
```

### Sensor Context in Planning

Modify `agent/planner_cloud.py`:

```python
async def plan(self, command: ParsedCommand, vector_store=None, sensor_context=None):
    # Add sensor context to prompt
    if sensor_context:
        context_str = f"""
        Current environment:
        - Temperature: {sensor_context.get('temperature')}°C
        - User present: {sensor_context.get('proximity_mm') < 1000}
        - Ambient light: {sensor_context.get('ambient_light')} lux
        - Motion: {sensor_context.get('motion')}
        """
        
        user_prompt += f"\n\nEnvironment context:\n{context_str}"
```

---

## 🏠 IoT Device Control

### Example: Control Philips Hue Lights

**Via MQTT**:
```cpp
// In ESP32 firmware
void controlHueLights(bool on) {
    if (on) {
        mqttClient.publish("home/lights/living_room", "ON");
    } else {
        mqttClient.publish("home/lights/living_room", "OFF");
    }
}
```

**Voice Command Flow**:
```
User: "Turn on living room lights"
  ↓
PC: Routes to local planner
  ↓
PC: Sends MQTT command via ESP32
  ↓
ESP32: Publishes MQTT message
  ↓
Hue Bridge: Turns on lights
```

### Example: Smart Thermostat

```cpp
void checkTemperature() {
    float temp = sensors.temperature;
    
    if (temp > 28.0) {
        // Too hot - turn on AC
        mqttClient.publish("home/ac/living_room", "ON");
        mqttClient.publish("home/ac/living_room/temp", "24");
    }
    else if (temp < 18.0) {
        // Too cold - turn on heater
        mqttClient.publish("home/heater/living_room", "ON");
    }
}
```

---

## 🚨 Offline Mode Capabilities

When PC disconnected, ESP32 can still:

### 1. Simple Voice Commands
```cpp
// Pseudo-code (requires wake word model)
void offlineModeHandler() {
    if (detectWakeWord()) {
        String command = classifySimpleCommand();  // TinyML model
        
        if (command == "lights_on") {
            digitalWrite(RELAY1_PIN, HIGH);
            mqttClient.publish("home/lights/all", "ON");
        }
        else if (command == "lights_off") {
            digitalWrite(RELAY1_PIN, LOW);
            mqttClient.publish("home/lights/all", "OFF");
        }
        else if (command == "fan_on") {
            digitalWrite(RELAY2_PIN, HIGH);
        }
    }
}
```

### 2. Emergency Routines
```cpp
void emergencyRoutineHandler() {
    // Detect emergency (e.g., smoke sensor)
    if (smokeDetected) {
        // Turn on all lights
        for (int relay = 0; relay < 4; relay++) {
            digitalWrite(RELAY1_PIN + relay, HIGH);
        }
        
        // Flash LEDs red
        flashLEDs(CRGB::Red);
        
        // Sound alarm
        playAlarmSound();
        
        // Send alert via MQTT
        mqttClient.publish("home/alerts/emergency", "SMOKE_DETECTED");
    }
}
```

### 3. Scheduled Actions
```cpp
void checkSchedule() {
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    
    // 7 AM wake up routine
    if (timeinfo->tm_hour == 7 && timeinfo->tm_min == 0) {
        // Turn on lights gradually
        for (int brightness = 0; brightness <= 255; brightness += 5) {
            fill_solid(leds, NUM_LEDS, CHSV(160, 255, brightness));
            FastLED.show();
            delay(100);
        }
        
        // Publish MQTT
        mqttClient.publish("home/routine", "MORNING_WAKEUP");
    }
}
```

---

## 🎨 LED Animations

Add advanced visual feedback:

```cpp
void breathingEffect(CRGB color) {
    static uint8_t brightness = 0;
    static int8_t direction = 1;
    
    brightness += direction * 5;
    
    if (brightness >= 255 || brightness <= 50) {
        direction *= -1;
    }
    
    fill_solid(leds, NUM_LEDS, color);
    FastLED.setBrightness(brightness);
    FastLED.show();
}

void spinningEffect(CRGB color) {
    static uint8_t position = 0;
    
    fill_solid(leds, NUM_LEDS, CRGB::Black);
    leds[position] = color;
    leds[(position + 1) % NUM_LEDS] = color;
    leds[(position + 2) % NUM_LEDS] = color;
    
    position = (position + 1) % NUM_LEDS;
    FastLED.show();
}

void rainbowEffect() {
    static uint8_t hue = 0;
    fill_rainbow(leds, NUM_LEDS, hue, 7);
    hue++;
    FastLED.show();
}
```

---

## 📊 Performance Optimization

### FreeRTOS Task Priorities
```
Priority 3: Audio Processing (highest - real-time)
Priority 2: Gesture Detection
Priority 1: Sensor Reading, Display, MQTT
Priority 0: Main loop
```

### Memory Usage
```
ESP32-S3 (8MB PSRAM):
- Firmware: ~1.5MB
- TinyML models: ~500KB
- Audio buffers: ~100KB
- PSRAM for DMA: 4MB
- Free: ~2MB
```

### Latency Targets
- Wake word detection: <100ms
- Gesture recognition: <50ms
- Sensor reading: 50ms (20Hz)
- MQTT publish: <100ms
- Servo response: <20ms

---

## 🐛 Troubleshooting

### Sensors not detected
```cpp
// Add debug output in setup()
Serial.println("Scanning I2C bus...");
for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
        Serial.print("Found device at 0x");
        Serial.println(address, HEX);
    }
}
```

Expected addresses:
- MPU6050: 0x68
- APDS9960: 0x39
- OLED: 0x3C
- VL53L0X: 0x29

### MQTT not connecting
- Check broker IP
- Ensure firewall allows port 1883
- Test with `mosquitto_sub`

### Wake word not detecting
- Check microphone orientation
- Increase sensitivity in model
- Re-train with more samples
- Monitor classification confidence

### LEDs not working
- Check data pin connection
- Verify 5V power adequate
- Add 330Ω resistor on data line
- Check FastLED library version

---

## 🎓 Next Steps

1. **Train Wake Word Model** (Edge Impulse)
2. **Add More Gestures** (train gesture classifier)
3. **Integrate Smart Devices** (MQTT topics)
4. **Create Custom Routines** (scheduled actions)
5. **Add Voice Feedback** (I2S audio out)
6. **Build Enclosure** (3D print or acrylic case)
7. **Add Camera** (ESP32-CAM for vision)
8. **Deploy Multiple Units** (ESP-NOW mesh)

---

## 📚 Resources

- [Edge Impulse Docs](https://docs.edgeimpulse.com/)
- [ESP32-S3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
- [TensorFlow Lite Micro](https://www.tensorflow.org/lite/microcontrollers)

---

**You now have a TRUE MCU JARVIS!** 🤖✨

Not just a peripheral, but an intelligent co-processor with real-time sensor fusion, IoT control, and offline capabilities.

