# Getting Started with JARVIS Desktop AI

## 🚀 Zero to Running in 10 Minutes

This guide will get JARVIS up and running as fast as possible.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Windows 11** (or Windows 10)
- [ ] **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- [ ] **Git** ([Download](https://git-scm.com/downloads))
- [ ] **USB Microphone** (or built-in laptop mic)
- [ ] **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))
- [ ] **Internet connection** (for downloading models)

**Optional**:
- [ ] ESP32 DevKit (for hardware features)
- [ ] NVIDIA GPU with CUDA (for faster STT)

---

## Step 1: Install & Setup (5 minutes)

### 1.1 Clone Repository

Open PowerShell or Command Prompt:

```powershell
git clone <your-repo-url>
cd jarvis
```

### 1.2 Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### 1.3 Install Dependencies

```powershell
pip install -r requirements.txt
```

This takes ~2-3 minutes.

---

## Step 2: Download Models (5 minutes)

```powershell
python scripts/download_models.py
```

This downloads:
- ✅ Whisper STT model (~500MB)
- ✅ Embedding model (~100MB)
- ✅ TTS model (~200MB)
- ✅ Playwright browser

**Total download**: ~1GB

---

## Step 3: Configure (2 minutes)

### 3.1 Create Config File

```powershell
copy config.example.yaml app\config.yaml
```

### 3.2 Add Your API Key

Open `app\config.yaml` in a text editor and find:

```yaml
cloud_llm:
  api_key: "YOUR_API_KEY_HERE"  # ← CHANGE THIS
```

Replace `YOUR_API_KEY_HERE` with your actual OpenAI API key.

**Get API Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3.3 (Optional) Adjust Settings

Most defaults work well, but you can customize:

```yaml
stt:
  model: "small"  # Change to "tiny" for faster (less accurate)
  device: "cuda"  # Change to "cpu" if no GPU

tts:
  engine: "coqui"  # Or "pyttsx3" for faster but lower quality

mcu:
  enabled: false  # Set to true if using ESP32
```

---

## Step 4: Run JARVIS! (30 seconds)

```powershell
python app/main.py
```

You should see:

```
JARVIS ESP32 Starting... (if ESP32 enabled)
✓ All components initialized
🤖 JARVIS online
```

A **blue system tray icon** appears in your taskbar!

---

## Step 5: Test Voice Commands (2 minutes)

### First Test: Open Chrome

1. Press **Ctrl + Space** (push-to-talk)
2. Say: **"Open Chrome"**
3. Release key
4. Wait 5-10 seconds
5. Chrome should open! 🎉

### More Tests

Try these commands:

**System Operations**:
```
"What time is it?"
"Open Calculator"
"Take a screenshot"
```

**Browser**:
```
"Go to YouTube"
"Go to GitHub"
```

**Memory**:
```
"Remember my name is [Your Name]"
(wait)
"What's my name?"
```

**File Search**:
```
"Search my downloads for PDF"
```

---

## Troubleshooting

### Nothing happens when I speak

**Check**:
- Is your microphone working? (test in Windows settings)
- Did you press Ctrl+Space?
- Is the system tray icon green (listening)?

**Fix**:
- Check microphone permissions in Windows settings
- Try different microphone in `config.yaml`:
  ```yaml
  audio:
    device_index: 0  # Try 1, 2, etc.
  ```

### "API key not configured" error

**Fix**:
- Open `app\config.yaml`
- Add your OpenAI API key
- Restart JARVIS

### "Module not found" error

**Fix**:
```powershell
pip install -r requirements.txt
```

### STT is very slow

**Fix 1**: Use smaller model
```yaml
stt:
  model: "tiny"  # Faster but less accurate
```

**Fix 2**: Use GPU (if you have NVIDIA GPU)
```yaml
stt:
  device: "cuda"
```

### "Playwright not installed" error

**Fix**:
```powershell
playwright install chromium
```

### ESP32 not connecting

**Fix**:
1. Open Device Manager → Ports (COM & LPT)
2. Find your ESP32 (e.g., "COM3")
3. Update `config.yaml`:
   ```yaml
   mcu:
     serial_port: "COM3"  # Use your actual port
   ```

---

## Next Steps

### Customize Commands

Edit `router/routing_policy.yaml` to add your own commands.

### Add More Tools

Create new tools in `tools/` folder. See `ARCHITECTURE.md` for details.

### Set Up ESP32 Hardware

See `esp32_firmware/README.md` for wiring guide.

### Read Full Documentation

- **README.md** - Project overview
- **SETUP_GUIDE.md** - Detailed installation
- **ARCHITECTURE.md** - Technical details
- **PROJECT_SUMMARY.md** - Complete feature list

---

## Hotkey Reference

| Hotkey | Action |
|--------|--------|
| **Ctrl + Space** | Push-to-talk (start listening) |
| **Ctrl + Shift + K** | Kill switch (emergency stop) |
| **Ctrl + Shift + M** | Mute/unmute microphone |

---

## System Tray Icon Colors

| Color | Status |
|-------|--------|
| 🔵 Blue | Idle (ready) |
| 🟢 Green | Listening |
| 🟡 Yellow | Thinking/processing |
| 🔴 Red | Speaking |
| 🔴 Dark Red | Error |

---

## Common Commands Cheat Sheet

### System
```
"Open [app name]"
"Close [app name]"
"What time is it?"
"Get system info"
"Take a screenshot"
```

### Files
```
"Search my [location] for [query]"
"List files in [folder]"
```

### Browser
```
"Go to [website]"
"Open Chrome"
"Navigate to [URL]"
```

### Memory
```
"Remember [fact]"
"What did I say about [topic]?"
```

---

## Getting Help

### Documentation
- Check `SETUP_GUIDE.md` for detailed instructions
- Read `ARCHITECTURE.md` for technical details
- See `PROJECT_SUMMARY.md` for feature list

### Common Issues
- Search `SETUP_GUIDE.md` for "Troubleshooting"
- Check logs in `logs/errors.log`
- Review `logs/audit.log` for action history

### Community
- GitHub Issues: [Report bugs]
- Discussions: [Ask questions]
- Discord: [Coming soon]

---

## Tips for Best Results

### Voice Input
- Speak clearly and at normal pace
- Avoid background noise
- Use natural language
- Be specific: "Open Google Chrome" not just "Chrome"

### Complex Tasks
- Break into smaller steps if needed
- Review action preview before confirming
- Use explicit commands for clarity

### Performance
- Use GPU if available (much faster)
- Close other heavy applications
- Use smaller Whisper model for speed

---

## What's Next?

Once JARVIS is running:

1. **Explore Commands**: Try different voice commands
2. **Add Memory**: Teach JARVIS facts about yourself
3. **Customize**: Edit permissions and routing rules
4. **Add ESP32**: Build the hardware interface
5. **Extend Tools**: Create custom automation tools

---

## Success Checklist

After following this guide, you should have:

- [x] JARVIS running and responding to voice
- [x] System tray icon showing status
- [x] Successfully opened an app via voice
- [x] Tested memory commands
- [x] Understood basic hotkeys

**Congratulations! You now have a working JARVIS!** 🎉

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         JARVIS QUICK REFERENCE          │
├─────────────────────────────────────────┤
│ START:     python app/main.py          │
│ TALK:      Ctrl + Space                 │
│ STOP ALL:  Ctrl + Shift + K             │
│ MUTE:      Ctrl + Shift + M             │
├─────────────────────────────────────────┤
│ TEST COMMANDS:                          │
│   "Open Chrome"                         │
│   "What time is it?"                    │
│   "Remember my name is X"               │
│   "Search downloads for invoice"        │
└─────────────────────────────────────────┘
```

---

**Ready to experience the future of desktop interaction!** 🚀

For detailed documentation, see:
- `README.md` - Overview
- `SETUP_GUIDE.md` - Full setup
- `ARCHITECTURE.md` - Tech details

**Need help?** Check the Troubleshooting section above or open an issue on GitHub.

---

*Made with ❤️ by the JARVIS community*
