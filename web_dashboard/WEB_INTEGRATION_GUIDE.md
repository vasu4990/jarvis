# JARVIS Web Integration Guide

## 🌐 Complete Web Interface System

This guide explains how to integrate the web dashboard and mobile interface with your existing JARVIS Python backend.

---

## 📁 Project Structure

```
jarvis/
├── web_dashboard/          ← NEW: Web interfaces
│   ├── index.html          # Desktop dashboard
│   ├── mobile.html         # Mobile command interface
│   ├── css/
│   │   ├── dashboard.css
│   │   └── mobile.css
│   ├── js/
│   │   ├── dashboard.js
│   │   └── mobile.js
│   └── websocket_server.py # WebSocket server code
│
├── app/
│   └── main.py            # Add WebSocket integration here
│
└── ... (existing JARVIS files)
```

---

## 🚀 Step 1: Install Dependencies

Add to your `requirements.txt`:

```txt
websockets>=12.0
```

Install:

```bash
pip install websockets
```

---

## 🔧 Step 2: Integrate WebSocket Server

### Option A: Modify Existing `app/main.py`

Add this to your `JarvisCore` class:

```python
from pathlib import Path
import sys

# Add web_dashboard to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'web_dashboard'))
from websocket_server import JarvisWebSocketServer


class JarvisCore:
    def __init__(self, config_path: str = "app/config.yaml"):
        # ... existing initialization ...
        
        # Add WebSocket server
        self.ws_server = JarvisWebSocketServer(
            host="0.0.0.0",  # Allow connections from any device
            port=8765
        )
        
    def _init_components(self):
        # ... existing component initialization ...
        
        # Link orchestrator to WebSocket server
        self.ws_server.orchestrator = self.orchestrator
        
    async def run(self):
        """Main run loop"""
        self.running = True
        self.logger.info("jarvis_starting")
        
        # Start WebSocket server in background
        asyncio.create_task(self.ws_server.start())
        self.logger.info("websocket_server_started", port=8765)
        
        # ... existing run logic ...
        
    async def broadcast_activity(self, message: str, icon: str = "fa-info-circle"):
        """Send activity updates to web clients"""
        if self.ws_server and self.ws_server.clients:
            await self.ws_server.send_activity(message, icon)
            
    async def broadcast_system_stats(self):
        """Send system stats to web clients (call periodically)"""
        import psutil
        
        stats = {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": f"{psutil.virtual_memory().used / (1024**3):.1f} / {psutil.virtual_memory().total / (1024**3):.1f} GB",
            "gpu": 0  # Add GPU monitoring if needed
        }
        
        if self.ws_server and self.ws_server.clients:
            await self.ws_server.send_system_stats(stats)
```

### Option B: Copy `websocket_server.py` to `app/`

```bash
copy web_dashboard\websocket_server.py app\websocket_server.py
```

Then import in `app/main.py`:

```python
from app.websocket_server import JarvisWebSocketServer
```

---

## 🖥️ Step 3: Start the System

### Start JARVIS Backend

```bash
cd jarvis
python app/main.py
```

You should see:
```
[INFO] websocket_server_starting host=0.0.0.0 port=8765
[INFO] websocket_server_running url=ws://0.0.0.0:8765
```

### Access Web Interfaces

1. **Desktop Dashboard**: 
   - Open `web_dashboard/index.html` in Chrome/Edge
   - Or serve with: `python -m http.server 8080` in `web_dashboard/` folder
   - Access: `http://localhost:8080/index.html`

2. **Mobile Interface**:
   - Option 1: Open `web_dashboard/mobile.html` on your phone browser
   - Option 2: Serve with HTTP server and access via phone
   - Make sure your phone is on the same network as your laptop

---

## 📱 Step 4: Mobile Access Setup

### Find Your Laptop's IP Address

**Windows**:
```cmd
ipconfig
```

Look for `IPv4 Address` under your active network adapter (e.g., `192.168.1.100`)

### Access from Mobile

1. **Serve the web interface**:
   ```bash
   cd jarvis/web_dashboard
   python -m http.server 8080
   ```

2. **On your phone browser**, navigate to:
   ```
   http://YOUR_LAPTOP_IP:8080/mobile.html
   ```
   Example: `http://192.168.1.100:8080/mobile.html`

3. **Configure WebSocket** (if needed):
   - Tap **Settings** in mobile app
   - Enter server address: `YOUR_LAPTOP_IP:8765`
   - Save settings

### Firewall Configuration

Allow connections on ports 8080 and 8765:

**Windows Firewall**:
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "JARVIS HTTP" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "JARVIS WebSocket" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
```

---

## 🔄 Step 5: Test the Integration

### Test Desktop Dashboard

1. Open `web_dashboard/index.html`
2. Check connection status (top right) - should show "Online"
3. Try a quick action: Click "Open Chrome"
4. Check activity feed for updates

### Test Mobile Interface

1. Open mobile.html on your phone
2. Connection indicator (top right) should be green
3. Tap the large microphone button
4. Say "open chrome" or type a command
5. Check for response

### Test Commands

Try these commands:
- "open chrome"
- "what time is it"
- "take screenshot"
- "system info"

---

## 🔧 Troubleshooting

### "Not connected" / Offline Status

**Check 1**: Is JARVIS backend running?
```bash
# Should show Python process
tasklist | findstr python
```

**Check 2**: Is WebSocket server running?
```
# Look for this in JARVIS logs
[INFO] websocket_server_running url=ws://0.0.0.0:8765
```

**Check 3**: Firewall blocking connections?
```powershell
# Test if port is open
Test-NetConnection -ComputerName localhost -Port 8765
```

**Check 4**: Browser console errors?
- Press F12 in browser
- Check Console tab for errors

### Mobile Can't Connect

**Issue**: "Connection lost, retrying..."

**Fix 1**: Check same network
- Laptop and phone must be on same WiFi
- Check with: `ping YOUR_LAPTOP_IP` from phone

**Fix 2**: Update server address in mobile settings
- Tap Settings → Enter `YOUR_LAPTOP_IP:8765`

**Fix 3**: Disable VPN/Firewall temporarily
- Some VPNs block local network access

### Commands Not Executing

**Issue**: Commands show "Processing..." but never complete

**Fix**: Verify orchestrator integration
```python
# In app/main.py, check this line exists:
self.ws_server.orchestrator = self.orchestrator
```

### Voice Input Not Working

**Desktop**: Use Chrome or Edge (Firefox doesn't support Web Speech API well)

**Mobile**: 
- Grant microphone permission in browser
- Check Settings → Voice Language is correct

---

## 🎯 Advanced Features

### Real-time System Monitoring

Add this to your `JarvisCore.run()` method:

```python
async def run(self):
    # ... existing code ...
    
    # Start periodic stats broadcast
    asyncio.create_task(self.periodic_stats_broadcast())
    
async def periodic_stats_broadcast(self):
    """Send system stats every 5 seconds"""
    while self.running:
        await self.broadcast_system_stats()
        await asyncio.sleep(5)
```

### Activity Feed Integration

Modify your tool execution to broadcast activity:

```python
# In agent/orchestrator.py
async def execute_tool(self, tool_name, params):
    # ... existing code ...
    
    # Broadcast to web clients
    if hasattr(self, 'jarvis_core'):
        await self.jarvis_core.broadcast_activity(
            f"Executing tool: {tool_name}",
            "fa-cogs"
        )
```

### Memory Count Updates

In `memory/vectorstore.py`:

```python
async def add_document(self, text, metadata):
    # ... existing code ...
    
    # Update web clients
    count = self.collection.count()
    if hasattr(self, 'ws_server'):
        await self.ws_server.send_memory_update(count)
```

---

## 🌐 Production Deployment

### Use HTTPS/WSS (Secure WebSocket)

For public internet access, use SSL certificates:

1. Get SSL certificate (Let's Encrypt)
2. Modify WebSocket server:

```python
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

async with websockets.serve(self.handler, self.host, self.port, ssl=ssl_context):
    # ...
```

### Use Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your_domain.com;
    
    location / {
        root /path/to/web_dashboard;
        index mobile.html;
    }
    
    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 API Reference

### WebSocket Message Types

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

1. **Command Response**:
```json
{
  "type": "command_response",
  "command": "open chrome",
  "response": "Chrome opened successfully",
  "success": true,
  "timestamp": "2024-02-24T10:30:00"
}
```

2. **Activity Update**:
```json
{
  "type": "activity",
  "message": "Executing: open chrome",
  "icon": "fa-terminal",
  "timestamp": "2024-02-24T10:30:00"
}
```

3. **System Stats**:
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

---

## ✅ Integration Checklist

- [ ] Install websockets package
- [ ] Copy websocket_server.py to project
- [ ] Modify app/main.py to include WebSocket server
- [ ] Link orchestrator to WebSocket server
- [ ] Start JARVIS backend (verify WebSocket starts)
- [ ] Configure firewall rules
- [ ] Test desktop dashboard locally
- [ ] Find laptop IP address
- [ ] Test mobile interface from phone
- [ ] Verify commands execute from web interface
- [ ] Test voice input on mobile
- [ ] Check activity feed updates
- [ ] Monitor system stats display

---

## 🎉 You're All Set!

Your JARVIS system now has:
- ✅ Desktop web dashboard for monitoring
- ✅ Mobile command interface
- ✅ Real-time WebSocket communication
- ✅ Voice input from phone
- ✅ Activity feed and logging
- ✅ System resource monitoring

**Next Steps**:
- Add more quick commands in mobile interface
- Customize dashboard with your favorite tools
- Set up 24/7 service (see `24_7_SERVICE_GUIDE.md`)
- Build AGI Research Portal

**Need Help?**
- Check JARVIS logs for errors
- Use browser console (F12) for debugging
- Review WebSocket server logs
