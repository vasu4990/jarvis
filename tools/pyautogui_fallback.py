"""
PyAutoGUI fallback tool for GUI automation
"""

import asyncio
import structlog
import pyautogui
from utils.schemas import ExecutionResult

logger = structlog.get_logger(__name__)


class PyAutoGUITool:
    """GUI automation fallback using PyAutoGUI"""
    
    def __init__(self, config):
        self.config = config
        self.pause = config.get("tools.pyautogui.pause", 0.5)
        self.failsafe = config.get("tools.pyautogui.failsafe", True)
        
        # Configure PyAutoGUI
        pyautogui.PAUSE = self.pause
        pyautogui.FAILSAFE = self.failsafe
        
    async def execute(self, action_type: str, params: dict) -> ExecutionResult:
        """Execute GUI action"""
        
        try:
            if action_type == "click_xy":
                return await self._click_xy(params)
            elif action_type == "type_text":
                return await self._type_text(params)
            elif action_type == "press_key":
                return await self._press_key(params)
            elif action_type == "hotkey":
                return await self._hotkey(params)
            elif action_type == "move_mouse":
                return await self._move_mouse(params)
            else:
                return ExecutionResult(success=False, error=f"Unknown action: {action_type}")
        except Exception as e:
            logger.error("PyAutoGUI tool error", action=action_type, error=str(e))
            return ExecutionResult(success=False, error=str(e))
            
    async def _click_xy(self, params: dict) -> ExecutionResult:
        """Click at coordinates"""
        x = params.get("x")
        y = params.get("y")
        clicks = params.get("clicks", 1)
        button = params.get("button", "left")
        
        if x is None or y is None:
            return ExecutionResult(success=False, error="Missing x or y coordinates")
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pyautogui.click(x, y, clicks=clicks, button=button)
            )
            
            return ExecutionResult(
                success=True,
                message=f"Clicked at ({x}, {y})"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def _type_text(self, params: dict) -> ExecutionResult:
        """Type text"""
        text = params.get("text", "")
        interval = params.get("interval", 0.0)
        
        if not text:
            return ExecutionResult(success=False, error="No text provided")
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pyautogui.typewrite(text, interval=interval)
            )
            
            return ExecutionResult(
                success=True,
                message=f"Typed text (length={len(text)})"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def _press_key(self, params: dict) -> ExecutionResult:
        """Press key"""
        key = params.get("key", "")
        presses = params.get("presses", 1)
        
        if not key:
            return ExecutionResult(success=False, error="No key provided")
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pyautogui.press(key, presses=presses)
            )
            
            return ExecutionResult(
                success=True,
                message=f"Pressed {key}"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def _hotkey(self, params: dict) -> ExecutionResult:
        """Press hotkey combination"""
        keys = params.get("keys", [])
        
        if not keys:
            return ExecutionResult(success=False, error="No keys provided")
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pyautogui.hotkey(*keys)
            )
            
            return ExecutionResult(
                success=True,
                message=f"Pressed hotkey {'+'.join(keys)}"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
            
    async def _move_mouse(self, params: dict) -> ExecutionResult:
        """Move mouse"""
        x = params.get("x")
        y = params.get("y")
        duration = params.get("duration", 0.0)
        
        if x is None or y is None:
            return ExecutionResult(success=False, error="Missing x or y coordinates")
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: pyautogui.moveTo(x, y, duration=duration)
            )
            
            return ExecutionResult(
                success=True,
                message=f"Moved mouse to ({x}, {y})"
            )
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e))
