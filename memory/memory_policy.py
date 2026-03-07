"""
Memory write policy - determines what to save to long-term memory
"""

import structlog

logger = structlog.get_logger(__name__)


class MemoryWritePolicy:
    """Determines which information should be persisted"""
    
    def __init__(self, config):
        self.config = config
        self.auto_save = config.get("memory.auto_save_facts", True)
        self.min_confidence = config.get("memory.min_confidence_to_save", 0.8)
        
    async def should_save(self, command, result) -> tuple[bool, str]:
        """
        Determine if command result should be saved to memory
        
        Returns: (should_save: bool, reason: str)
        """
        intent = command.intent
        confidence = command.intent_confidence
        
        # Always save explicit memory commands
        if intent == "remember_fact":
            return (True, "Explicit memory command")
            
        # Don't save low-confidence interactions
        if confidence < self.min_confidence:
            return (False, f"Low confidence ({confidence:.2f})")
            
        # Don't save failed actions
        if not result.success:
            return (False, "Action failed")
            
        # Save user preferences
        if intent in ["set_preference", "configure"]:
            return (True, "User preference")
            
        # Don't save routine operations
        if intent in ["open_app", "navigate_to", "search_files"]:
            return (False, "Routine operation")
            
        # Default: don't save unless explicitly requested
        return (False, "Not eligible for auto-save")
