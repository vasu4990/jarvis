# JARVIS 24/7 Always-On Service Guide

## 🚀 Run JARVIS as a Windows Service

This guide explains how to make JARVIS run 24/7 in the background, automatically start on boot, and stay online even when you're not logged in.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: NSSM (Easiest)](#method-1-nssm-easiest)
3. [Method 2: Windows Task Scheduler](#method-2-windows-task-scheduler)
4. [Method 3: Python Service (Advanced)](#method-3-python-service-advanced)
5. [Configuration](#configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

✅ JARVIS system is working correctly  
✅ Python virtual environment set up  
✅ All dependencies installed  
✅ Configuration file (`app/config.yaml`) created  

---

## Method 1: NSSM (Easiest)

**NSSM** (Non-Sucking Service Manager) is the easiest way to run Python scripts as Windows services.

### Step 1: Download NSSM

1. Download from: https://nssm.cc/download
2. Extract to `C:\nssm\`
3. Add to PATH or use full path

### Step 2: Create Service

Open **PowerShell as Administrator**:

```powershell
# Navigate to JARVIS directory
cd C:\path\to\jarvis

# Create the service
C:\nssm\nssm.exe install JARVISService

# NSSM GUI will open
```

### Step 3: Configure in NSSM GUI

**Application Tab**:
- **Path**: `C:\path\to\jarvis\venv\Scripts\python.exe`
- **Startup directory**: `C:\path\to\jarvis`
- **Arguments**: `app\main.py`

**Details Tab**:
- **Display name**: JARVIS AI Assistant
- **Description**: JARVIS Desktop AI with voice control
- **Startup type**: Automatic (Delayed Start)

**Log on Tab**:
- Select: **This account**
- Enter your Windows username and password
- (This allows JARVIS to access your desktop for automation)

**I/O Tab**:
- **Output (stdout)**: `C:\path\to\jarvis\logs\service_stdout.log`
- **Error (stderr)**: `C:\path\to\jarvis\logs\service_stderr.log`

**File rotation Tab**:
- **Rotate files**: Checked
- **Restrict file size**: 10000000 (10 MB)

### Step 4: Start the Service

```powershell
# Start service
nssm start JARVISService

# Check status
nssm status JARVISService

# View in Services
services.msc
```

### Step 5: Management Commands

```powershell
# Stop service
nssm stop JARVISService

# Restart service
nssm restart JARVISService

# Remove service (if needed)
nssm remove JARVISService confirm

# Edit service
nssm edit JARVISService
```

---

## Method 2: Windows Task Scheduler

No external tools required, built into Windows.

### Step 1: Create Batch Script

Create `start_jarvis.bat` in your JARVIS folder:

```batch
@echo off
cd /d C:\path\to\jarvis
call venv\Scripts\activate
python app\main.py
```

### Step 2: Create Scheduled Task

1. Open **Task Scheduler** (`taskschd.msc`)
2. Click **Create Task** (not "Create Basic Task")

### Step 3: General Tab

- **Name**: JARVIS Service
- **Description**: JARVIS AI Assistant - Always On
- ✅ **Run whether user is logged on or not**
- ✅ **Run with highest privileges**
- ✅ **Hidden** (optional)
- **Configure for**: Windows 10/11

### Step 4: Triggers Tab

Click **New**:
- **Begin the task**: At startup
- ✅ **Enabled**

Add another trigger:
- **Begin the task**: On connection to user session
- **Specific user**: Your username
- ✅ **Enabled**

### Step 5: Actions Tab

Click **New**:
- **Action**: Start a program
- **Program/script**: `C:\path\to\jarvis\start_jarvis.bat`
- **Start in**: `C:\path\to\jarvis`

### Step 6: Conditions Tab

- ⬜ **Start the task only if the computer is on AC power** (uncheck this!)
- ✅ **Wake the computer to run this task**
- ✅ **Start only if the following network connection is available**: Any connection

### Step 7: Settings Tab

- ✅ **Allow task to be run on demand**
- ✅ **Run task as soon as possible after a scheduled start is missed**
- ✅ **If the task fails, restart every**: 1 minute
- **Attempt to restart up to**: 3 times
- ✅ **If the running task does not end when requested, force it to stop**

### Step 8: Save and Test

1. Enter your Windows password when prompted
2. Right-click task → **Run**
3. Check if JARVIS starts

### View Logs

```powershell
# View Task Scheduler logs
Get-EventLog -LogName Application -Source "Task Scheduler" -Newest 50
```

---

## Method 3: Python Service (Advanced)

For advanced users who want a native Python Windows service.

### Step 1: Install PyWin32

```bash
pip install pywin32
```

### Step 2: Create Service Script

Create `jarvis_service.py`:

```python
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import JarvisCore
import asyncio


class JarvisService(win32serviceutil.ServiceFramework):
    _svc_name_ = "JARVISService"
    _svc_display_name_ = "JARVIS AI Assistant"
    _svc_description_ = "JARVIS Desktop AI with voice control and automation"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.jarvis = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.jarvis:
            self.jarvis.stop()
            
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        try:
            self.jarvis = JarvisCore()
            asyncio.run(self.jarvis.run())
        except Exception as e:
            servicemanager.LogErrorMsg(f"JARVIS Service Error: {str(e)}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(JarvisService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(JarvisService)
```

### Step 3: Install Service

```powershell
# Install
python jarvis_service.py install

# Start
python jarvis_service.py start

# Stop
python jarvis_service.py stop

# Remove
python jarvis_service.py remove
```

---

## Configuration

### Environment Variables

Create `.env` file in JARVIS root:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Server settings
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8765

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/jarvis.log
```

### Auto-activate Virtual Environment

Add to `start_jarvis.bat`:

```batch
@echo off
REM Set working directory
cd /d %~dp0

REM Activate virtual environment
call venv\Scripts\activate

REM Load environment variables
if exist .env (
    for /f "tokens=*" %%a in (.env) do set %%a
)

REM Start JARVIS
python app\main.py

REM Keep window open if error
if errorlevel 1 pause
```

---

## Monitoring & Logging

### Log File Structure

```
jarvis/
├── logs/
│   ├── jarvis.log           # Main application log
│   ├── service_stdout.log   # Service output
│   ├── service_stderr.log   # Service errors
│   ├── websocket.log        # WebSocket connections
│   └── commands.log         # Command history
```

### Enable Detailed Logging

In `app/config.yaml`:

```yaml
logging:
  level: DEBUG
  file: logs/jarvis.log
  max_size_mb: 50
  backup_count: 5
  console: false  # Disable for service
```

### Monitor Service Status

**PowerShell Script** (`check_jarvis.ps1`):

```powershell
# Check if JARVIS service is running
$service = Get-Service -Name "JARVISService" -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "Service Status: $($service.Status)"
    
    if ($service.Status -ne "Running") {
        Write-Host "Starting JARVIS service..."
        Start-Service -Name "JARVISService"
    }
} else {
    Write-Host "JARVIS service not found!"
}

# Check log for errors
$log = Get-Content "C:\path\to\jarvis\logs\jarvis.log" -Tail 20
if ($log -match "ERROR|CRITICAL") {
    Write-Host "Recent errors found in log!"
    $log | Select-String "ERROR|CRITICAL"
}
```

### Web Dashboard Monitoring

Access `http://localhost:8080/index.html` to see:
- Real-time system status
- Command history
- Resource usage
- Activity feed

---

## Auto-restart on Failure

### Using NSSM

NSSM automatically restarts services on failure.

Configure restart policy:

```powershell
nssm set JARVISService AppThrottle 1500
nssm set JARVISService AppRestartDelay 5000
```

### Using Task Scheduler

Already configured in Step 7 of Method 2:
- Restart every 1 minute
- Up to 3 attempts

### Manual Watchdog Script

Create `watchdog.ps1`:

```powershell
while ($true) {
    $process = Get-Process python -ErrorAction SilentlyContinue | 
                Where-Object { $_.Path -like "*jarvis*" }
    
    if (-not $process) {
        Write-Host "JARVIS not running! Starting..."
        Start-Process "C:\path\to\jarvis\start_jarvis.bat"
    }
    
    Start-Sleep -Seconds 60
}
```

Run watchdog as a separate scheduled task.

---

## Troubleshooting

### Service Won't Start

**Issue**: Service starts then immediately stops

**Solution 1**: Check logs
```powershell
Get-Content C:\path\to\jarvis\logs\service_stderr.log -Tail 50
```

**Solution 2**: Test manually first
```powershell
cd C:\path\to\jarvis
.\start_jarvis.bat
```

**Solution 3**: Check Python path
```powershell
# In NSSM, verify Python.exe path is correct
C:\path\to\jarvis\venv\Scripts\python.exe --version
```

### Permission Denied Errors

**Issue**: Service can't access files/devices

**Solution**: Run service as your user account (not LocalSystem)
- In NSSM → Log on tab → Select "This account"
- In Task Scheduler → General tab → Change user

### High CPU/Memory Usage

**Issue**: JARVIS consuming too many resources

**Solution 1**: Limit model sizes
```yaml
# In config.yaml
whisper:
  model: tiny  # or base, instead of medium/large
```

**Solution 2**: Reduce polling intervals
```python
# In app/main.py
await asyncio.sleep(0.1)  # Increase sleep times
```

**Solution 3**: Monitor with Task Manager
- Find python.exe process
- Right-click → Set affinity (limit CPU cores)
- Right-click → Set priority → Below normal

### WebSocket Won't Connect

**Issue**: Dashboard shows "Offline"

**Solution 1**: Check firewall
```powershell
Test-NetConnection -ComputerName localhost -Port 8765
```

**Solution 2**: Verify WebSocket started
```
# Check logs for:
[INFO] websocket_server_running url=ws://0.0.0.0:8765
```

**Solution 3**: Allow through firewall
```powershell
New-NetFirewallRule -DisplayName "JARVIS WebSocket" `
    -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
```

---

## Performance Optimization

### Reduce Startup Time

1. **Preload models** in background
2. **Lazy load** tools
3. **Cache** embeddings

### Reduce Memory Usage

1. Use **smaller models** (whisper tiny, MiniLM)
2. **Limit** vector database size
3. **Clear** old command history

### Optimize for 24/7

```python
# In app/main.py

# Periodic cleanup
async def periodic_cleanup(self):
    while self.running:
        # Clear old logs
        # Compact database
        # Free memory
        await asyncio.sleep(3600)  # Every hour
```

---

## ✅ 24/7 Service Checklist

- [ ] JARVIS works correctly when run manually
- [ ] Virtual environment is activated
- [ ] All dependencies installed
- [ ] Configuration file created
- [ ] Logs directory exists
- [ ] Firewall rules configured
- [ ] Service installed (NSSM or Task Scheduler)
- [ ] Service set to auto-start
- [ ] Service runs as your user account
- [ ] Service starts successfully
- [ ] WebSocket server accessible
- [ ] Web dashboard connects
- [ ] Mobile interface connects
- [ ] Commands execute correctly
- [ ] Monitoring script set up
- [ ] Auto-restart configured

---

## 🎉 Success!

Your JARVIS is now:
- ✅ Running 24/7
- ✅ Auto-starts on boot
- ✅ Restarts on failure
- ✅ Accessible from web/mobile
- ✅ Monitored and logged

**Test it**: Restart your computer and verify JARVIS auto-starts!

**Access from anywhere**:
- Desktop: `http://localhost:8080/index.html`
- Mobile: `http://YOUR_IP:8080/mobile.html`

---

**Need help?** Check the logs and review the troubleshooting section.
