"""
Serial protocol definitions for ESP32 communication
"""

# Message types (PC → ESP32)
CMD_LED = "LED"
CMD_BUZZER = "BUZZER"
CMD_PING = "PING"
CMD_STATUS = "STATUS"

# Event types (ESP32 → PC)
EVENT_WAKE_BUTTON = "WAKE_BUTTON"
EVENT_KILL_SWITCH = "KILL_SWITCH"
EVENT_MUTE_TOGGLE = "MUTE_TOGGLE"
EVENT_SENSOR = "SENSOR"

# LED states
LED_STATE_IDLE = "IDLE"
LED_STATE_LISTENING = "LISTENING"
LED_STATE_THINKING = "THINKING"
LED_STATE_SPEAKING = "SPEAKING"
LED_STATE_ERROR = "ERROR"

# Protocol format (JSON over newline-delimited serial)
"""
PC → ESP32:
{
  "cmd": "LED",
  "data": {"state": "LISTENING"},
  "timestamp": "ISO-8601"
}

ESP32 → PC:
{
  "type": "EVENT",
  "event": "WAKE_BUTTON",
  "data": {},
  "timestamp": "ISO-8601"
}
"""
