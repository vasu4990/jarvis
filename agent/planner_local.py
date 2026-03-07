"""
Local Planner - Simple task planning without cloud
"""

import structlog
from utils.schemas import ParsedCommand, ActionPlan, Step
from uuid import uuid4

logger = structlog.get_logger(__name__)


class LocalPlanner:
    """Plans simple tasks locally using templates"""
    
    def __init__(self, config):
        self.config = config
        self.enabled = config.get("local_planner.enabled", True)
        self.max_steps = config.get("local_planner.max_steps", 5)
        
    async def plan(self, command: ParsedCommand) -> ActionPlan:
        """Generate action plan from parsed command"""
        
        intent = command.intent
        slots = command.slots
        
        logger.info("Local planning", intent=intent, slots=slots)
        
        # Template-based planning
        steps = []
        
        if intent == "open_app":
            steps = [Step(
                step_id="s1",
                tool="os_adapter",
                type="open_app",
                params={"app_name": slots.get("app_name", "")},
                permission_level="allow",
                postconditions=["process_exists"]
            )]
            
        elif intent == "search_files":
            steps = [Step(
                step_id="s1",
                tool="os_adapter",
                type="search_files",
                params={"query": slots.get("search_query", "")},
                permission_level="allow"
            )]
            
        elif intent == "navigate_to":
            target = slots.get("target", "")
            # Add http if not present
            if not target.startswith("http"):
                if "." in target:
                    target = f"https://{target}"
                else:
                    # Search query
                    target = f"https://www.google.com/search?q={target}"
                    
            steps = [
                Step(
                    step_id="s1",
                    tool="playwright",
                    type="open_browser",
                    params={},
                    permission_level="allow"
                ),
                Step(
                    step_id="s2",
                    tool="playwright",
                    type="navigate_url",
                    params={"url": target},
                    permission_level="allow"
                )
            ]
            
        elif intent == "remember_fact":
            # Memory write (special handling in orchestrator)
            steps = [Step(
                step_id="s1",
                tool="memory",
                type="save_fact",
                params={"fact": slots.get("fact", "")},
                permission_level="allow"
            )]
            
        else:
            # Unknown intent - no plan
            logger.warning("No local plan for intent", intent=intent)
            return None
            
        if not steps:
            return None
            
        # Create action plan
        plan = ActionPlan(
            command_id=command.command_id,
            steps=steps,
            created_by="local_planner_v1"
        )
        
        logger.info("Plan created", steps=len(steps))
        return plan
