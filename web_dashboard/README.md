# 🌐 JARVIS Web Dashboard & Mobile Interface

## Complete Web-Based Control System for JARVIS AI Assistant

This system provides **desktop dashboard** and **mobile command interface** for controlling your JARVIS AI assistant from any device.

---

## ✨ Features

### 🖥️ Desktop Dashboard (`index.html`)
- **Real-time System Monitoring** - CPU, memory, GPU usage
- **Activity Feed** - Live updates of JARVIS actions
- **Command Interface** - Text and voice input
- **Quick Actions** - One-click common commands
- **System Stats** - Performance metrics and uptime
- **AGI Research Portal** - Track research progress
- **Beautiful UI** - Cyberpunk-themed glassmorphic design

### 📱 Mobile Interface (`mobile.html`)
- **Optimized for Touch** - Mobile-first responsive design
- **Voice Commands** - Tap-to-speak interface
- **Quick Command Grid** - Common actions at your fingertips
- **Settings Panel** - Configure server address, language, feedback
- **Offline Support** - Auto-reconnect on network changes
- **Vibration Feedback** - Haptic responses
- **Activity History** - Recent commands and responses

### 🔌 WebSocket Server (`websocket_server.py`)
- **Real-time Communication** - Bidirectional WebSocket protocol
- **Multi-client Support** - Multiple devices simultaneously
- **Command Routing** - Execute JARVIS commands remotely
- **Activity Broadcasting** - Updates pushed to all connected clients
- **System Stats Streaming** - Live resource monitoring

---

## 🚀 Quick Start

### 1. **Prerequisites**

✅ JARVIS system installed and working  
✅ Python 3.9+ with virtual environment  
✅ All JARVIS dependencies installed  

### 2. **Install WebSocket Dependency**

```bash
pip install websockets
```

### 3. **Integrate WebSocket Server**

See **[WEB_INTEGRATION_GUIDE.md](WEB_INTEGRATION_GUIDE.md)** for detailed instructions.

**Quick integration** in `app/main.py`:

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'web_dashboard'))
from websocket_server import JarvisWebSocketServer

class JarvisCore:
    def __init__(self, config_path: str = "app/config.yaml"):
        # ... existing code ...
        self.ws_server = JarvisWebSocketServer(host="0.0.0.0", port=8765)
    
    async def run(self):
        asyncio.create_task(self.ws_server.start())
        # ... existing code ...
```

### 4. **Start JARVIS Backend**

```bash
cd jarvis
python app/main.py
```

Look for:
```
[INFO] websocket_server_running url=ws://0.0.0.0:8765
```

### 5. **Access Web Interfaces**

**Option A: Direct File Access**
- Open `web_dashboard/index.html` in browser (for desktop)
- Open `web_dashboard/mobile.html` on phone (for mobile)

**Option B: HTTP Server** (Recommended)
```bash
cd web_dashboard
python -m http.server 8080
```

Then access:
- Desktop: `http://localhost:8080/index.html`
- Mobile: `http://YOUR_LAPTOP_IP:8080/mobile.html`

---

## 📱 Mobile Setup

### 1. Find Your Laptop IP

**Windows**:
```cmd
ipconfig
```

Look for **IPv4 Address** (e.g., `192.168.1.100`)

### 2. Configure Firewall

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "JARVIS HTTP" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "JARVIS WebSocket" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
```

### 3. Access from Phone

1. Make sure phone is on same WiFi as laptop
2. Open browser on phone
3. Navigate to: `http://YOUR_LAPTOP_IP:8080/mobile.html`
4. Tap Settings → Enter `YOUR_LAPTOP_IP:8765` if needed
5. Start using voice/text commands!

---

## 🗂️ Project Structure

```
web_dashboard/
├── index.html                    # Desktop dashboard
├── mobile.html                   # Mobile interface
├── agi_portal.html               # AGI research portal
│
├── css/
│   ├── dashboard.css             # Desktop styles
│   └── mobile.css                # Mobile styles
│
├── js/
│   ├── dashboard.js              # Desktop logic
│   └── mobile.js                 # Mobile logic
│
├── websocket_server.py           # Python WebSocket server
│
├── WEB_INTEGRATION_GUIDE.md      # Integration instructions
├── 247_SERVICE_GUIDE.md          # 24/7 setup guide
└── README.md                     # This file
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[WEB_INTEGRATION_GUIDE.md](WEB_INTEGRATION_GUIDE.md)** | Step-by-step integration with JARVIS backend |
| **[247_SERVICE_GUIDE.md](247_SERVICE_GUIDE.md)** | Run JARVIS 24/7 as Windows service |
| **[websocket_server.py](websocket_server.py)** | WebSocket server implementation |

---

## 🎯 Usage Examples

### Desktop Dashboard

1. **Execute Commands**
   - Type in command box or click microphone
   - Try: "open chrome", "what time is it", "system info"

2. **Quick Actions**
   - One-click buttons for common tasks
   - Chrome, Time, Screenshot, System Info

3. **Monitor Activity**
   - Real-time feed of JARVIS actions
   - System resource usage graphs

4. **AGI Research**
   - Click "AGI Research" tab
   - Access research roadmap and resources

### Mobile Interface

1. **Voice Commands**
   - Tap large microphone button
   - Speak your command
   - Get instant response

2. **Text Commands**
   - Type in bottom input bar
   - Tap send button or press Enter

3. **Quick Commands**
   - Grid of common actions
   - Tap any card to execute

4. **Settings**
   - Configure server address
   - Change voice language
   - Toggle auto-speak responses
   - Enable/disable vibration

---

## 🔧 Configuration

### WebSocket Server Settings

In `app/main.py`:

```python
self.ws_server = JarvisWebSocketServer(
    host="0.0.0.0",      # Listen on all interfaces (for mobile access)
    port=8765             # WebSocket port
)
```

### Mobile App Settings

In mobile app → Settings:
- **Server Address**: `YOUR_LAPTOP_IP:8765`
- **Voice Language**: Choose from en-US, en-GB, es-ES, fr-FR, de-DE
- **Auto-speak**: Toggle text-to-speech responses
- **Vibration**: Toggle haptic feedback

---

## 🛠️ Troubleshooting

### "Not Connected" / Offline Status

**Problem**: Dashboard shows offline

**Solutions**:
1. Check JARVIS backend is running (`python app/main.py`)
2. Verify WebSocket server started (check logs)
3. Test port: `Test-NetConnection -ComputerName localhost -Port 8765`
4. Check firewall isn't blocking port 8765

### Mobile Can't Connect

**Problem**: "Connection lost, retrying..."

**Solutions**:
1. Verify phone and laptop on same WiFi network
2. Ping laptop IP from phone browser
3. Update server address in mobile Settings
4. Disable VPN on phone
5. Check firewall rules allow inbound connections

### Commands Not Executing

**Problem**: Commands stuck on "Processing..."

**Solutions**:
1. Verify orchestrator linked: `self.ws_server.orchestrator = self.orchestrator`
2. Check JARVIS logs for errors
3. Test commands work from main JARVIS interface first

### Voice Input Not Working

**Problem**: Microphone button doesn't work

**Solutions**:
- **Desktop**: Use Chrome or Edge (Firefox has limited support)
- **Mobile**: Grant microphone permission in browser
- Check voice language setting matches your speech

### High Latency

**Problem**: Slow response times

**Solutions**:
1. Use WiFi 5GHz band instead of 2.4GHz
2. Reduce distance between phone and router
3. Close other apps using network
4. Check JARVIS system resources

---

## 🔐 Security Considerations

### For Local Network Only

Current setup is designed for **local network use**. Do NOT expose to the public internet without:

1. **SSL/TLS Encryption** - Use WSS instead of WS
2. **Authentication** - Add token-based auth
3. **Rate Limiting** - Prevent abuse
4. **Input Validation** - Sanitize all commands

### Recommended Network Setup

- ✅ Use on trusted home/office WiFi only
- ✅ Firewall rules limit to local network
- ✅ Disable UPnP on router
- ❌ Do NOT port forward WebSocket port
- ❌ Do NOT use on public WiFi

### For Public Internet Access

See production deployment section in **WEB_INTEGRATION_GUIDE.md** for:
- HTTPS/WSS with Let's Encrypt
- Nginx reverse proxy setup
- Authentication implementation
- Rate limiting configuration

---

## 🎨 Customization

### Add Custom Quick Commands

**Desktop** (`index.html`):
```html
<button class="action-btn" data-command="your command here">
    <i class="fas fa-icon-name"></i>
    <span>Label</span>
</button>
```

**Mobile** (`mobile.html`):
```html
<button class="command-card" data-command="your command here">
    <i class="fas fa-icon-name"></i>
    <span>Label</span>
</button>
```

### Change Color Theme

Edit CSS variables in `css/dashboard.css` or `css/mobile.css`:

```css
:root {
    --primary-color: #00d9ff;     /* Change primary color */
    --secondary-color: #0099ff;   /* Change secondary color */
    --bg-dark: #0a0e1a;           /* Change background */
    /* ... */
}
```

### Add Custom Activity Icons

Use Font Awesome icon classes:

```javascript
this.addActivity('Your message', 'fa-custom-icon');
```

Browse icons: https://fontawesome.com/icons

---

## 📊 API Reference

### WebSocket Message Protocol

**Client → Server**:
```json
{
  "type": "command",
  "command": "open chrome",
  "source": "mobile",
  "timestamp": 1234567890
}
```

**Server → Client**:

**Command Response**:
```json
{
  "type": "command_response",
  "command": "open chrome",
  "response": "Chrome opened successfully",
  "success": true,
  "timestamp": "2024-02-24T10:30:00"
}
```

**Activity Update**:
```json
{
  "type": "activity",
  "message": "Executing tool: PowerShell",
  "icon": "fa-terminal",
  "timestamp": "2024-02-24T10:30:00"
}
```

**System Stats**:
```json
{
  "type": "system_stats",
  "stats": {
    "cpu": 25,
    "memory": "4.2 / 16 GB",
    "gpu": 12
  },
  "timestamp": "2024-02-24T10:30:00"
}
```

**Memory Update**:
```json
{
  "type": "memory_update",
  "count": 247,
  "timestamp": "2024-02-24T10:30:00"
}
```

---

## 🚀 Advanced Features

### Real-time System Monitoring

Broadcast stats every 5 seconds:

```python
async def periodic_stats_broadcast(self):
    while self.running:
        await self.broadcast_system_stats()
        await asyncio.sleep(5)
```

### Activity Feed Integration

Send updates from tools:

```python
await self.ws_server.send_activity(
    "Executing PowerShell script",
    "fa-terminal"
)
```

### Custom WebSocket Handlers

Extend `websocket_server.py`:

```python
async def handle_message(self, websocket, message: str):
    data = json.loads(message)
    
    if data.get("type") == "custom_action":
        # Your custom logic here
        pass
```

---

## 🎯 Use Cases

### 1. **Remote Control**
Control JARVIS from anywhere in your home/office via mobile

### 2. **Monitoring**
Keep an eye on JARVIS activity from your desk with dashboard

### 3. **Hands-free Operation**
Use voice commands from phone while away from computer

### 4. **Multi-device Access**
Desktop and mobile access simultaneously

### 5. **AGI Research Tracking**
Document your progress on 5 AGI research paths

---

## 🔄 Updates & Maintenance

### Check for Issues

```bash
# View WebSocket server logs
tail -f logs/websocket.log

# Check JARVIS main logs
tail -f logs/jarvis.log

# Monitor browser console
# Press F12 → Console tab
```

### Clear Browser Cache

If changes don't appear:
1. Press `Ctrl+Shift+Delete`
2. Clear cached images and files
3. Refresh page

### Update Dependencies

```bash
pip install --upgrade websockets
```

---

## ✅ Checklist

### Initial Setup
- [ ] JARVIS backend working
- [ ] websockets package installed
- [ ] WebSocket server integrated in `app/main.py`
- [ ] Firewall rules configured
- [ ] HTTP server running (`python -m http.server 8080`)

### Desktop Dashboard
- [ ] `index.html` loads successfully
- [ ] Connection status shows "Online"
- [ ] Commands execute correctly
- [ ] Activity feed updates
- [ ] System stats display
- [ ] Voice input works

### Mobile Interface
- [ ] `mobile.html` accessible from phone
- [ ] Connection indicator green
- [ ] Voice commands work
- [ ] Text commands work
- [ ] Quick commands execute
- [ ] Settings save correctly
- [ ] Auto-reconnect works

### 24/7 Operation
- [ ] Service installed (NSSM or Task Scheduler)
- [ ] Auto-start on boot configured
- [ ] Auto-reconnect enabled
- [ ] Monitoring set up
- [ ] Logs rotating properly

---

## 🆘 Support

**Documentation**:
- [WEB_INTEGRATION_GUIDE.md](WEB_INTEGRATION_GUIDE.md) - Integration steps
- [247_SERVICE_GUIDE.md](247_SERVICE_GUIDE.md) - 24/7 setup
- [websocket_server.py](websocket_server.py) - Server code

**Debugging**:
1. Check JARVIS logs: `logs/jarvis.log`
2. Check WebSocket logs: `logs/websocket.log`
3. Check browser console: Press F12
4. Review this README troubleshooting section

**Common Issues**:
- Connection problems → Check firewall and network
- Command failures → Verify orchestrator integration
- Voice not working → Check browser/language settings
- High latency → Use 5GHz WiFi, reduce distance

---

## 📝 License

Part of the JARVIS Desktop AI Assistant project.  
See parent directory LICENSE file.

---

## 🎉 You're Ready!

Your JARVIS system now has:
- ✅ Beautiful web dashboard
- ✅ Mobile command interface
- ✅ Real-time WebSocket communication
- ✅ Voice control from any device
- ✅ 24/7 operation capability
- ✅ AGI research portal

**Start controlling JARVIS from anywhere! 🚀**

---

**Version**: 1.0.0  
**Last Updated**: February 24, 2024  
**Status**: Production Ready ✅
