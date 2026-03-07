"""
Configuration management for JARVIS
"""

import yaml
from pathlib import Path
from typing import Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class Config:
    """Configuration manager with nested key access"""
    
    def __init__(self, config_path: str = "app/config.yaml"):
        self.config_path = Path(config_path)
        self._data = {}
        self.load()
        
    def load(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.warning(
                "Config file not found, using defaults",
                path=str(self.config_path)
            )
            self._load_defaults()
            return
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f) or {}
            logger.info("Configuration loaded", path=str(self.config_path))
        except Exception as e:
            logger.error("Failed to load config", error=str(e))
            self._load_defaults()
            
    def _load_defaults(self):
        """Load default configuration"""
        self._data = {
            "app": {
                "name": "JARVIS",
                "version": "1.0.0-mvp",
                "log_level": "INFO"
            }
        }
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get("audio.sample_rate", 16000)
        """
        keys = key_path.split('.')
        value = self._data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        data = self._data
        
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
            
        data[keys[-1]] = value
        
    def save(self):
        """Save configuration back to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self._data, f, default_flow_style=False)
            logger.info("Configuration saved", path=str(self.config_path))
        except Exception as e:
            logger.error("Failed to save config", error=str(e))
            
    @property
    def data(self) -> dict:
        """Get raw configuration dictionary"""
        return self._data
