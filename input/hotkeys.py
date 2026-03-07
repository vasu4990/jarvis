"""
Global hotkey manager for JARVIS
"""

import keyboard
import structlog
from typing import Callable, Awaitable

logger = structlog.get_logger(__name__)


class HotkeyManager:
    """Manages global keyboard shortcuts"""
    
    def __init__(self, config, callback: Callable[[str], Awaitable]):
        self.config = config
        self.callback = callback
        self.active = False
        
        # Load hotkey mappings
        self.hotkeys = {
            "push_to_talk": config.get("hotkeys.push_to_talk", "ctrl+space"),
            "kill_switch": config.get("hotkeys.kill_switch", "ctrl+shift+k"),
            "open_console": config.get("hotkeys.open_console", "ctrl+shift+j"),
            "mute_toggle": config.get("hotkeys.mute_toggle", "ctrl+shift+m")
        }
        
    def start(self):
        """Register all hotkeys"""
        if self.active:
            return
            
        try:
            for name, combo in self.hotkeys.items():
                keyboard.add_hotkey(
                    combo,
                    lambda n=name: self._on_hotkey(n),
                    suppress=False
                )
                logger.info(f"Registered hotkey", name=name, combo=combo)
                
            self.active = True
            logger.info("Hotkey manager started")
            
        except Exception as e:
            logger.error("Failed to register hotkeys", error=str(e))
            
    def stop(self):
        """Unregister all hotkeys"""
        if not self.active:
            return
            
        try:
            keyboard.unhook_all()
            self.active = False
            logger.info("Hotkey manager stopped")
        except Exception as e:
            logger.error("Failed to unregister hotkeys", error=str(e))
            
    def _on_hotkey(self, name: str):
        """Handle hotkey press"""
        import asyncio
        try:
            # Create task in event loop
            loop = asyncio.get_event_loop()
            loop.create_task(self.callback(name))
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(self.callback(name))
