# JARVIS Desktop AI - Complete Setup Guide

## Overview

This is a **production-ready, no-compromise JARVIS** implementation for Windows 11 with ESP32 hardware integration.

**Key Features:**
- ✅ Hybrid architecture (local routing + cloud reasoning)
- ✅ Voice & keyboard input
- ✅ ESP32 hardware buttons & LEDs
- ✅ Multi-step task planning & execution
- ✅ Vector memory (Chroma DB)
- ✅ Permission gating & audit logs
- ✅ OS automation (PowerShell + UIA)
- ✅ Browser automation (Playwright)
- ✅ Evaluator with postcondition verification
- ✅ System tray app
- ✅ Action preview dialogs

---

## Quick Start (5 Minutes)

### Step 1: Prerequisites

Ensure you have:
- **Python 3.10+** installed
- **Git** installed
- **Windows 11** (for OS-specific features)
- **USB microphone**
- (Optional) **ESP32** board for hardware features

### Step 2: Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd jarvis

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models (takes 5-10 minutes)
python scripts/download_models.py

# Install Playwright browsers
playwright install chromium
```

### Step 3: Configure

```bash
# Copy config template
copy config.example.yaml app\config.yaml

# Edit app\config.yaml
# IMPORTANT: Add your OpenAI API key for cloud reasoning
```

Edit `app/config.yaml`:
```yaml
cloud_llm:
  api_key: "sk-your-actual-api-key-here"
```

### Step 4: Run JARVIS

```bash
python app/main.py
```

You should see:
```
🤖 JARVIS online
```

System tray icon will appear!

### Step 5: Test Voice Commands

1. Press **Ctrl+Space** (push-to-talk)
2. Say: **"Open Chrome"**
3. JARVIS should open Chrome!

Try more:
- "Search my downloads for invoice"
- "Go to YouTube"
- "Remember my PC name is ORION"
- "What's my PC name?"

---

## ESP32 Hardware Setup (Optional but Recommended)

### Hardware You'll Need

- ESP32 DevKit (~$5-10)
- WS2812B LED ring, 16 LEDs (~$5)
- Push button (~$1)
- Resistors: 330Ω, 10kΩ
- Capacitor: 1000µF
- Breadboard & wires

### Quick Wire Guide

```
ESP32 GPIO 21 → Button → GND
ESP32 GPIO 18 → LED Data (via 330Ω resistor)
ESP32 5V → LED VCC
ESP32 GND → LED GND
```

### Flash Firmware

```bash
cd esp32_firmware

# Install PlatformIO
pip install platformio

# Upload firmware
pio run --target upload

# Monitor output
pio device monitor
```

See `esp32_firmware/README.md` for detailed wiring diagrams.

### Configure PC Connection

In `app/config.yaml`:
```yaml
mcu:
  enabled: true
  serial_port: "COM3"  # Check Device Manager
```

Now you have:
- 🔵 Blue LED when idle
- 🟢 Green LED when listening
- 🟡 Yellow LED when thinking
- 🔴 Red LED when speaking
- Physical wake button!
- Long-press (3s) = emergency kill switch

---

## Usage Guide

### Hotkeys

| Hotkey | Action |
|--------|--------|
| **Ctrl+Space** | Push-to-talk (start listening) |
| **Ctrl+Shift+K** | Kill switch (stop all actions) |
| **Ctrl+Shift+J** | Open console (not yet implemented) |
| **Ctrl+Shift+M** | Mute toggle |

### Voice Commands

**System Operations:**
- "Open [app name]" → Opens application
- "Search [location] for [query]" → File search
- "What time is it?" → Get current time
- "Take a screenshot" → Captures screen

**Browser:**
- "Go to [website]" → Navigate to URL
- "Open Chrome" → Launch browser
- "Go to YouTube and search for AI tutorials"

**Memory:**
- "Remember [fact]" → Save to long-term memory
- "What did I say about [topic]?" → Recall memory

**Examples:**
```
You: "Open Chrome and go to GitHub"
JARVIS: *Opens Chrome, navigates to GitHub*

You: "Search my downloads for invoice PDF"
JARVIS: *Lists found PDFs*

You: "Remember my meeting is at 4pm tomorrow"
JARVIS: *Saves to memory*
```

### Typed Commands

Click the console window and type commands directly (no voice needed).

### Permission System

JARVIS uses 3-level permissions:

1. **Allow** (auto-executed, no confirmation)
   - Open apps, navigate URLs, read files, get info

2. **Ask** (requires confirmation)
   - Type text, click buttons, create files, send emails
   - You'll see a preview dialog

3. **Deny** (blocked by default)
   - Delete files, install software, system changes
   - Requires admin override

You can customize in `agent/policy_gate.py`.

---

## Architecture Deep Dive

### Data Flow

```
Input → STT → Router → Planner → Policy Gate → Tools → Evaluator → Output
  ↓                       ↓                                          ↓
Audio              Memory (RAG)                                    TTS
```

### Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Input** | Hotkeys, Audio, ESP32 | Capture user intent |
| **STT** | Whisper (local) | Speech→Text |
| **Router** | Rule-based + LLM | Local vs cloud decision |
| **NLU** | Intent classifier | Extract intent & slots |
| **Agent** | Planner, Orchestrator | Multi-step planning |
| **Tools** | PowerShell, Playwright, PyAutoGUI | Execute actions |
| **Memory** | Chroma, SQLite | Remember & retrieve |
| **Output** | TTS, UI | Respond to user |

### Hybrid Reasoning

**Local (fast, private):**
- Intent routing
- Simple commands (open app, search files)
- Memory retrieval
- Policy checks

**Cloud (powerful, complex):**
- Multi-step planning
- Complex reasoning
- Long-context tasks
- Document generation

The router automatically decides based on task complexity.

---

## Configuration Reference

See `config.example.yaml` for all options. Key settings:

### Audio
```yaml
audio:
  sample_rate: 16000
  vad_aggressiveness: 3  # 0-3, higher = more aggressive
```

### STT
```yaml
stt:
  model: "small"  # tiny, base, small, medium
  device: "cuda"  # cuda or cpu
```

### Cloud LLM
```yaml
cloud_llm:
  provider: "openai"
  model: "gpt-4-turbo-preview"
  api_key: "sk-..."
```

### Memory
```yaml
memory:
  vector_db:
    persist_directory: "./data/vectordb"
  embeddings:
    model: "sentence-transformers/all-MiniLM-L6-v2"
```

### Tools
```yaml
tools:
  playwright:
    headless: false  # Show browser window
    timeout: 30000
```

---

## Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### STT is slow
- Use smaller Whisper model: `stt.model: "tiny"`
- Enable GPU: `stt.device: "cuda"`

### ESP32 not connecting
- Check COM port in Device Manager
- Try different USB cable
- Update `config.yaml` with correct port

### Browser automation fails
```bash
playwright install chromium
```

### Permission errors (PowerShell)
Run as Administrator (for testing only):
```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Cloud API errors
- Verify API key in `config.yaml`
- Check internet connection
- Verify account billing/quota

---

## Project Structure

```
jarvis/
├── app/main.py              # Entry point ⭐
├── config.yaml              # Your settings ⚙️
├── input/                   # Audio, hotkeys, ESP32
├── stt/                     # Speech-to-text
├── router/                  # Intent routing
├── agent/                   # Planning & orchestration
├── tools/                   # OS/browser automation
├── memory/                  # Vector DB & SQLite
├── tts/                     # Text-to-speech
├── ui/                      # Tray app & dialogs
├── mcu_bridge/              # ESP32 communication
└── esp32_firmware/          # Arduino firmware
```

---

## Development

### Adding New Tools

1. Create `tools/my_tool.py`
2. Implement `execute(action_type, params)` method
3. Register in `tool_manifest.json`
4. Add permission rules in `policy_gate.py`

### Adding New Intents

1. Add to `routing_policy.yaml`
2. Update `intent_router.py` slot extraction
3. Add plan template in `planner_local.py`

### Custom Commands

Edit `router/routing_policy.yaml`:
```yaml
intent_keywords:
  my_command:
    - "do the thing"
    - "perform action"
```

---

## Security Best Practices

✅ **DO:**
- Run as normal user (not administrator)
- Review action previews before approving
- Keep audit logs enabled
- Use API keys from secure storage
- Regularly review permissions

❌ **DON'T:**
- Auto-approve dangerous actions
- Disable audit logging
- Store API keys in code
- Run untrusted tool scripts
- Bypass permission gates

---

## Performance Tuning

### For Faster Response:
- Use Whisper "tiny" model
- Enable GPU acceleration
- Use streaming STT (future feature)
- Reduce `vad_aggressiveness`

### For Better Accuracy:
- Use Whisper "medium" model
- Increase `stt.beam_size`
- Use better microphone/mic array
- Reduce background noise

### For Lower Cost:
- Use local LLM for more tasks
- Reduce cloud API calls
- Cache common responses
- Use smaller context windows

---

## Roadmap

### v1.1 (Next)
- [ ] Wake word detection (openWakeWord)
- [ ] Streaming STT
- [ ] Multi-agent planning (AutoGen)
- [ ] Knowledge graph (Neo4j)
- [ ] Voice biometrics

### v1.2
- [ ] Vision input (webcam gestures)
- [ ] IoT integration (MQTT)
- [ ] Mobile companion app
- [ ] Cloud memory sync
- [ ] Custom voice cloning

### v2.0
- [ ] Advanced GUI understanding
- [ ] Autonomous workflow learning
- [ ] Multi-device orchestration
- [ ] Enterprise SSO

---

## FAQ

**Q: Do I need an ESP32?**
A: No, it's optional. You can use keyboard hotkeys only.

**Q: Does this work offline?**
A: Partially. STT, TTS, memory, and simple commands work offline. Complex reasoning requires cloud API.

**Q: Can I use a different LLM?**
A: Yes! Edit `cloud_llm` config to use Anthropic, or run local LLM via Ollama.

**Q: Is my data private?**
A: Local components (STT, memory, tools) never leave your PC. Only cloud reasoning sends data to OpenAI (if configured).

**Q: Can I customize wake word?**
A: Yes, when wake word feature is added. Currently uses push-to-talk.

**Q: Does it work on Mac/Linux?**
A: Core features yes, but OS automation tools are Windows-specific. PRs welcome for cross-platform!

---

## Contributing

We welcome contributions!

**Areas needing help:**
- macOS/Linux tool implementations
- Additional browser automation actions
- New voice commands
- UI improvements
- Documentation

See `CONTRIBUTING.md` for guidelines.

---

## License

MIT License - See `LICENSE`

---

## Credits

**Built with:**
- OpenAI Whisper (STT)
- sentence-transformers (embeddings)
- Chroma (vector DB)
- Playwright (browser automation)
- Coqui TTS (speech)
- FastLED (ESP32 LEDs)

**Inspired by:**
- Iron Man's JARVIS
- Notion AI
- GitHub Copilot
- Rabbit R1

---

## Support & Community

- **Issues**: [GitHub Issues]
- **Discussions**: [GitHub Discussions]
- **Discord**: [Coming Soon]
- **Twitter**: [@YourHandle]

---

**🚀 Ready to transform your desktop experience with JARVIS!**

For detailed component documentation, see:
- `esp32_firmware/README.md` - Hardware setup
- `tools/README.md` - Tool development
- `ARCHITECTURE.md` - System design

**Happy building!** 🤖✨
