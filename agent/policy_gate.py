"""
Permission System (Policy Gate)
Enforces security rules for tool execution
"""

import structlog
from typing import Dict, List
from utils.schemas import Step, ActionPlan

logger = structlog.get_logger(__name__)


class PolicyGate:
    """Enforces permission rules for actions"""
    
    # Default permission rules
    PERMISSION_RULES = {
        "allow": [
            # Read-only operations
            "open_app",
            "navigate_url",
            "read_clipboard",
            "get_time",
            "get_date",
            "search_files",
            "list_directory",
            "get_system_info",
            "screenshot",
            
            # Safe browser ops
            "open_browser",
            "close_browser",
        ],
        
        "ask": [
            # State-changing operations
            "type_text",
            "click_element",
            "send_email",
            "create_file",
            "create_folder",
            "fill_form",
            "submit_form",
            "write_clipboard",
            "move_file",
            "rename_file",
            
            # App control
            "close_app",
            "switch_window",
        ],
        
        "deny": [
            # Dangerous operations
            "delete_file",
            "delete_folder",
            "install_software",
            "uninstall_software",
            "registry_edit",
            "run_executable",
            "run_script",
            "shutdown_system",
            "restart_system",
            "kill_process",
            "modify_system_settings",
        ]
    }
    
    def __init__(self, config):
        self.config = config
        self.require_confirmation = config.get("permissions.require_confirmation_for_ask", True)
        self.auto_deny_dangerous = config.get("permissions.auto_deny_dangerous", True)
        
        logger.info(
            "Policy gate initialized",
            require_confirmation=self.require_confirmation,
            auto_deny=self.auto_deny_dangerous
        )
        
    async def verify_plan(self, plan: ActionPlan) -> Dict[str, any]:
        """
        Verify entire action plan against permissions
        
        Returns: {
            "allowed": bool,
            "steps_requiring_confirmation": List[str],
            "denied_steps": List[str],
            "reason": str
        }
        """
        results = {
            "allowed": True,
            "steps_requiring_confirmation": [],
            "denied_steps": [],
            "reason": ""
        }
        
        for step in plan.steps:
            permission = self._check_permission(step.type)
            
            if permission == "deny":
                results["denied_steps"].append(step.step_id)
                if self.auto_deny_dangerous:
                    results["allowed"] = False
                    results["reason"] = f"Step '{step.type}' is denied by security policy"
                    logger.warning(
                        "Action denied",
                        step_id=step.step_id,
                        action=step.type
                    )
                    break
                    
            elif permission == "ask":
                if self.require_confirmation:
                    results["steps_requiring_confirmation"].append(step.step_id)
                    
        # If any steps need confirmation, plan is not auto-allowed
        if results["steps_requiring_confirmation"]:
            results["requires_user_approval"] = True
            
        return results
        
    async def verify_step(self, step: Step) -> tuple[bool, str]:
        """
        Verify single step
        
        Returns: (allowed: bool, reason: str)
        """
        permission = self._check_permission(step.type)
        
        if permission == "allow":
            return (True, "Auto-allowed")
            
        elif permission == "deny":
            if self.auto_deny_dangerous:
                return (False, "Denied by security policy")
            else:
                # Still require user override
                return (False, "Requires admin override")
                
        else:  # "ask"
            # Requires user confirmation (handled by caller)
            return (None, "Requires user confirmation")
            
    def _check_permission(self, action_type: str) -> str:
        """
        Check permission level for action type
        
        Returns: "allow" | "ask" | "deny"
        """
        # Check each permission level
        for level in ["allow", "ask", "deny"]:
            if action_type in self.PERMISSION_RULES[level]:
                return level
                
        # Default to "ask" for unknown actions
        logger.warning("Unknown action type, defaulting to 'ask'", action=action_type)
        return "ask"
        
    def get_permission_summary(self) -> Dict[str, List[str]]:
        """Get human-readable permission summary"""
        return {
            "Auto-allowed (no confirmation)": self.PERMISSION_RULES["allow"],
            "Requires confirmation": self.PERMISSION_RULES["ask"],
            "Denied": self.PERMISSION_RULES["deny"]
        }
