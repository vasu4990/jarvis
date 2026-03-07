"""
PowerShell-based OS automation for Windows
"""

import asyncio
import subprocess
import structlog
from pathlib import Path
from utils.schemas import ExecutionResult

logger = structlog.get_logger(__name__)


class PowerShellTool:
    """Windows OS operations via PowerShell"""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config.get("tools.os_adapter.powershell_timeout", 30)
        
    async def execute(self, action_type: str, params: dict) -> ExecutionResult:
        """Execute OS action"""
        
        try:
            if action_type == "open_app":
                return await self._open_app(params)
            elif action_type == "search_files":
                return await self._search_files(params)
            elif action_type == "get_system_info":
                return await self._get_system_info()
            elif action_type == "get_time":
                return await self._get_time()
            elif action_type == "screenshot":
                return await self._screenshot(params)
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Unknown action: {action_type}"
                )
        except Exception as e:
            logger.error("PowerShell tool error", action=action_type, error=str(e))
            return ExecutionResult(success=False, error=str(e))
            
    async def _open_app(self, params: dict) -> ExecutionResult:
        """Open application by name"""
        app_name = params.get("app_name", "").strip()
        
        if not app_name:
            return ExecutionResult(success=False, error="No app name provided")
            
        # Common app mappings
        app_map = {
            "chrome": "chrome",
            "google chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "microsoft edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "calc": "calc",
            "explorer": "explorer",
            "file explorer": "explorer",
            "cmd": "cmd",
            "command prompt": "cmd",
            "powershell": "powershell",
            "terminal": "wt",  # Windows Terminal
            "windows terminal": "wt"
        }
        
        exec_name = app_map.get(app_name.lower(), app_name)
        
        # Try to launch
        ps_command = f"Start-Process '{exec_name}'"
        
        result = await self._run_powershell(ps_command)
        
        if result["success"]:
            return ExecutionResult(
                success=True,
                message=f"Opened {app_name}",
                data={"app": exec_name}
            )
        else:
            return ExecutionResult(
                success=False,
                error=f"Failed to open {app_name}: {result['error']}"
            )
            
    async def _search_files(self, params: dict) -> ExecutionResult:
        """Search for files"""
        query = params.get("query", "").strip()
        search_path = params.get("path", str(Path.home() / "Downloads"))
        
        if not query:
            return ExecutionResult(success=False, error="No search query")
            
        # PowerShell search command
        ps_command = f"""
Get-ChildItem -Path '{search_path}' -Recurse -Filter '*{query}*' -ErrorAction SilentlyContinue |
Select-Object -First 10 FullName |
ConvertTo-Json
"""
        
        result = await self._run_powershell(ps_command)
        
        if result["success"]:
            try:
                import json
                files = json.loads(result["output"]) if result["output"] else []
                if isinstance(files, str):
                    files = [files]
                    
                return ExecutionResult(
                    success=True,
                    message=f"Found {len(files)} files",
                    data={"files": files}
                )
            except:
                return ExecutionResult(
                    success=True,
                    message="Search complete",
                    data={"raw": result["output"]}
                )
        else:
            return ExecutionResult(success=False, error=result["error"])
            
    async def _get_system_info(self) -> ExecutionResult:
        """Get system information"""
        ps_command = """
$info = @{
    ComputerName = $env:COMPUTERNAME
    UserName = $env:USERNAME
    OS = (Get-CimInstance Win32_OperatingSystem).Caption
    FreeMemoryGB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)
}
$info | ConvertTo-Json
"""
        
        result = await self._run_powershell(ps_command)
        
        if result["success"]:
            import json
            try:
                info = json.loads(result["output"])
                return ExecutionResult(
                    success=True,
                    message="System info retrieved",
                    data=info
                )
            except:
                return ExecutionResult(success=True, data={"raw": result["output"]})
        else:
            return ExecutionResult(success=False, error=result["error"])
            
    async def _get_time(self) -> ExecutionResult:
        """Get current time"""
        from datetime import datetime
        now = datetime.now()
        return ExecutionResult(
            success=True,
            message=now.strftime("%I:%M %p"),
            data={"time": now.isoformat()}
        )
        
    async def _screenshot(self, params: dict) -> ExecutionResult:
        """Take screenshot"""
        save_path = params.get("path", str(Path.home() / "Desktop" / "screenshot.png"))
        
        ps_command = f"""
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save('{save_path}')
$graphics.Dispose()
$bitmap.Dispose()
"""
        
        result = await self._run_powershell(ps_command)
        
        if result["success"]:
            return ExecutionResult(
                success=True,
                message=f"Screenshot saved to {save_path}",
                artifacts=[save_path]
            )
        else:
            return ExecutionResult(success=False, error=result["error"])
            
    async def _run_powershell(self, command: str) -> dict:
        """Run PowerShell command"""
        try:
            process = await asyncio.create_subprocess_exec(
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode('utf-8', errors='ignore').strip()
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='ignore').strip()
                }
                
        except asyncio.TimeoutError:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
