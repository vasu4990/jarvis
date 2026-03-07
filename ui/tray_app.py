"""
System tray application for JARVIS
"""

import structlog
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from typing import Callable
import threading

logger = structlog.get_logger(__name__)


class TrayApp:
    """System tray icon and menu"""
    
    def __init__(self, config, action_callback: Callable):
        self.config = config
        self.action_callback = action_callback
        
        self.icon = None
        self.current_status = "idle"
        
        # Status colors
        self.status_colors = {
            "idle": "#4A90E2",      # Blue
            "listening": "#50C878",  # Green
            "thinking": "#FFB800",   # Yellow
            "speaking": "#FF6B6B",   # Red
            "error": "#D32F2F"       # Dark red
        }
        
    def run(self):
        """Start tray app (blocking)"""
        logger.info("Starting system tray")
        
        # Create icon
        image = self._create_icon_image(self.current_status)
        
        # Create menu
        menu = Menu(
            MenuItem("JARVIS", None, enabled=False),
            MenuItem("Status: Idle", None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Open Console", lambda: self.action_callback("open_console")),
            MenuItem("Settings", lambda: self.action_callback("settings")),
            Menu.SEPARATOR,
            MenuItem("Exit", lambda: self.action_callback("exit"))
        )
        
        self.icon = Icon(
            "JARVIS",
            image,
            "JARVIS AI Assistant",
            menu
        )
        
        # Run (blocking)
        self.icon.run()
        
    def set_status(self, status: str):
        """Update status indicator"""
        if status == self.current_status:
            return
            
        self.current_status = status
        
        if self.icon:
            # Update icon
            self.icon.icon = self._create_icon_image(status)
            
            # Update menu
            status_text = status.capitalize()
            self.icon.title = f"JARVIS - {status_text}"
            
        logger.debug("Tray status updated", status=status)
        
    def stop(self):
        """Stop tray app"""
        if self.icon:
            self.icon.stop()
            logger.info("Tray app stopped")
            
    def _create_icon_image(self, status: str) -> Image:
        """Create icon image with status color"""
        # Create a simple circle icon
        size = 64
        image = Image.new('RGB', (size, size), 'white')
        draw = ImageDraw.Draw(image)
        
        color = self.status_colors.get(status, "#4A90E2")
        
        # Draw circle
        margin = 4
        draw.ellipse(
            [margin, margin, size-margin, size-margin],
            fill=color,
            outline='black',
            width=2
        )
        
        return image
