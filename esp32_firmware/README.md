# ESP32 Firmware for JARVIS

## Hardware Setup

### Required Components

- ESP32 DevKit (any variant)
- WS2812B NeoPixel LED ring (16 LEDs recommended)
- Momentary push button
- Resistors: 330Ω (for LED data), 10kΩ (for button pull-up, if needed)
- Capacitor: 1000µF (for LED power stability)
- Breadboard and jumper wires
- USB cable

### Wiring Diagram

```
ESP32 Pin Connections:
┌────────────────────────────────┐
│ ESP32         Component         │
├────────────────────────────────┤
│ GPIO 21   →   Button (one side)│
│ GND       →   Button (other)   │
│                                 │
│ GPIO 18   →   LED Data In      │
│ 5V        →   LED VCC (+)      │
│ GND       →   LED GND (-)      │
└────────────────────────────────┘

Button:
- Connect between GPIO 21 and GND
- Internal pull-up enabled in firmware
- Short press = Wake
- Long press (3s) = Kill switch

NeoPixel Ring:
- Connect DATA IN to GPIO 18 via 330Ω resistor
- Connect VCC to 5V (or 3.3V for smaller rings)
- Connect GND to GND
- Add 1000µF capacitor between VCC and GND near LEDs
```

### LED Ring Mounting

Position the LED ring:
- Visible from your desk
- Near your work area
- Angled for easy viewing

### Button Placement

Mount button:
- Easy to reach
- Won't be pressed accidentally
- Consider a nice mechanical button for tactile feedback

## Software Setup

### 1. Install PlatformIO

```bash
# Install PlatformIO Core (CLI)
pip install platformio

# OR use PlatformIO IDE extension for VSCode
```

### 2. Build & Upload Firmware

```bash
cd esp32_firmware

# Build firmware
pio run

# Upload to ESP32 (connect via USB first)
pio run --target upload

# Monitor serial output
pio device monitor
```

### 3. Test Connection

After upload, you should see:
```
JARVIS ESP32 Starting...
✓ JARVIS ESP32 Ready
```

Test the button:
- Short press: should send `EVENT WAKE_BUTTON`
- Long press (3s): should send `EVENT KILL_SWITCH` and flash red

### 4. Configure PC Connection

In `app/config.yaml`, set:
```yaml
mcu:
  enabled: true
  serial_port: "COM3"  # Check Device Manager
  baud_rate: 115200
```

Find your COM port:
- Windows: Device Manager → Ports (COM & LPT)
- Linux: `ls /dev/ttyUSB*` or `/dev/ttyACM*`
- macOS: `ls /dev/cu.usb*`

## LED Status Indicators

| Color       | State         | Meaning                    |
|-------------|---------------|----------------------------|
| 🔵 Blue     | IDLE          | Ready, waiting for input   |
| 🟢 Green    | LISTENING     | Recording your voice       |
| 🟡 Yellow   | THINKING      | Processing/planning        |
| 🔴 Red      | SPEAKING      | JARVIS is responding       |
| 🔴 Dark Red | ERROR         | Something went wrong       |

## Troubleshooting

### ESP32 not connecting
- Check USB cable (must be data cable, not charge-only)
- Try different USB port
- Press BOOT button while uploading
- Check COM port in Device Manager

### LEDs not working
- Check wiring (especially data pin)
- Verify 5V power supply is sufficient
- Add capacitor if not already present
- Reduce `LED_BRIGHTNESS` in firmware

### Button not responding
- Test with multimeter (should read LOW when pressed)
- Check GPIO 21 connection
- Increase `DEBOUNCE_MS` if button is noisy

### Serial communication issues
- Verify baud rate (115200)
- Check config.yaml COM port setting
- Monitor with `pio device monitor` to see raw output

## Customization

### Change Pin Numbers

Edit `src/main.cpp`:
```cpp
#define BUTTON_PIN 21     // Change this
#define LED_PIN 18        // Change this
#define NUM_LEDS 16       // Change this
```

### Adjust LED Brightness

```cpp
#define LED_BRIGHTNESS 128  // 0-255
```

### Change Long Press Duration

```cpp
#define LONG_PRESS_MS 3000  // milliseconds
```

## Advanced Features (Future)

- [ ] Add second button (mute toggle)
- [ ] Add rotary encoder (volume control)
- [ ] Add OLED display (status messages)
- [ ] Add temperature/humidity sensor
- [ ] Add PIR motion sensor
- [ ] Add buzzer for audio feedback
- [ ] Wireless operation (BLE/Wi-Fi)

## Protocol Reference

### ESP32 → PC Messages

```json
{"type": "EVENT", "event": "WAKE_BUTTON", "timestamp": 12345}
{"type": "EVENT", "event": "KILL_SWITCH", "timestamp": 12346}
{"type": "PONG", "timestamp": 12347}
```

### PC → ESP32 Commands

```json
{"cmd": "LED", "data": {"state": "LISTENING"}, "timestamp": "..."}
{"cmd": "PING", "data": {}, "timestamp": "..."}
{"cmd": "BUZZER", "data": {"pattern": "chime"}, "timestamp": "..."}
```

## Safety Notes

⚠️ **Important**:
- Don't exceed 5V on LED VCC
- Use proper resistors on data lines
- Add capacitors for power stability
- Don't draw >500mA from USB (use external power for large LED arrays)
- Button should be normally open (not normally closed)

## Support

If you encounter issues:
1. Check wiring carefully
2. Monitor serial output with `pio device monitor`
3. Test components individually
4. Check GitHub issues for similar problems

---

**Ready to bring JARVIS to life!** 🤖💡
