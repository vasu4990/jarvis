"""
Evaluator - Verifies action results and postconditions
"""

import asyncio
import structlog
import psutil
from pathlib import Path
from utils.schemas import Step, ExecutionResult

logger = structlog.get_logger(__name__)


class Evaluator:
    """Verifies tool execution results"""
    
    def __init__(self, config):
        self.config = config
        self.verify_postconditions = config.get("evaluator.verify_postconditions", True)
        self.max_retries = config.get("evaluator.max_retries", 2)
        self.retry_delay = config.get("evaluator.retry_delay", 2)
        
    async def validate(self, step: Step, result: ExecutionResult) -> tuple[bool, str]:
        """
        Validate execution result against postconditions
        
        Returns: (success: bool, message: str)
        """
        if not self.verify_postconditions or not step.postconditions:
            # No validation needed
            return (result.success, "No postconditions to check")
            
        if not result.success:
            # Already failed
            return (False, result.error or "Execution failed")
            
        logger.info("Evaluating postconditions", step=step.step_id, conditions=step.postconditions)
        
        # Check each postcondition
        for condition in step.postconditions:
            passed, message = await self._check_condition(condition, step, result)
            
            if not passed:
                logger.warning(
                    "Postcondition failed",
                    step=step.step_id,
                    condition=condition,
                    message=message
                )
                return (False, f"Postcondition '{condition}' failed: {message}")
                
        logger.info("All postconditions passed", step=step.step_id)
        return (True, "All postconditions satisfied")
        
    async def _check_condition(self, condition: str, step: Step, result: ExecutionResult) -> tuple[bool, str]:
        """Check individual postcondition"""
        
        if condition == "process_exists":
            # Check if process started
            app_name = step.params.get("app_name", "")
            if self._find_process(app_name):
                return (True, f"Process '{app_name}' is running")
            else:
                return (False, f"Process '{app_name}' not found")
                
        elif condition == "window_visible":
            # Check if window exists (basic check via process for now)
            app_name = step.params.get("app_name", "")
            if self._find_process(app_name):
                return (True, f"Window for '{app_name}' should be visible")
            else:
                return (False, f"No window found for '{app_name}'")
                
        elif condition == "file_exists":
            # Check if file was created
            file_path = step.params.get("file_path", "")
            if Path(file_path).exists():
                return (True, f"File '{file_path}' exists")
            else:
                return (False, f"File '{file_path}' not found")
                
        elif condition == "folder_exists":
            # Check if folder was created
            folder_path = step.params.get("folder_path", "")
            if Path(folder_path).is_dir():
                return (True, f"Folder '{folder_path}' exists")
            else:
                return (False, f"Folder '{folder_path}' not found")
                
        elif condition == "browser_open":
            # Check if browser process exists
            for browser in ["chrome", "firefox", "msedge", "brave"]:
                if self._find_process(browser):
                    return (True, f"Browser '{browser}' is running")
            return (False, "No browser process found")
            
        else:
            # Unknown condition - log warning and pass
            logger.warning("Unknown postcondition", condition=condition)
            return (True, "Unknown condition (skipped)")
            
    def _find_process(self, name: str) -> bool:
        """Check if process with name exists"""
        name_lower = name.lower()
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if name_lower in proc_name or proc_name in name_lower:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return False
