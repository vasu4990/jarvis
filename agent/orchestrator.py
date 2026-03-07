"""
Orchestrator - Executes action plans via tools
"""

import asyncio
import structlog
import json
from datetime import datetime
from utils.schemas import ActionPlan, TaskState, ExecutionResult, AuditLogEntry
from agent.policy_gate import PolicyGate
from agent.evaluator import Evaluator

logger = structlog.get_logger(__name__)


class Orchestrator:
    """Coordinates tool execution"""
    
    def __init__(self, config, policy_gate: PolicyGate, evaluator: Evaluator, relational_db):
        self.config = config
        self.policy_gate = policy_gate
        self.evaluator = evaluator
        self.relational_db = relational_db
        
        self.tools = {}  # Will be loaded from tool registry
        self.active_tasks = {}  # Track running tasks
        
    async def execute(self, plan: ActionPlan, action_preview_manager) -> ExecutionResult:
        """Execute action plan"""
        
        logger.info("Executing plan", action_id=plan.action_id, steps=len(plan.steps))
        
        # Verify permissions
        policy_result = await self.policy_gate.verify_plan(plan)
        
        if not policy_result["allowed"]:
            logger.warning("Plan denied by policy", reason=policy_result["reason"])
            return ExecutionResult(
                success=False,
                error=policy_result["reason"]
            )
            
        # Check if confirmation needed
        if policy_result.get("requires_user_approval"):
            # Show action preview
            approved = await action_preview_manager.show_preview(
                plan,
                policy_result["steps_requiring_confirmation"]
            )
            
            if not approved:
                logger.info("Plan rejected by user")
                return ExecutionResult(
                    success=False,
                    message="Action cancelled by user"
                )
                
        # Create task state
        task_state = TaskState(
            action_id=plan.action_id,
            pending_steps=[s.step_id for s in plan.steps],
            status="running"
        )
        
        self.active_tasks[task_state.task_id] = task_state
        
        # Execute steps
        final_result = ExecutionResult(success=True, message="Completed")
        
        for step in plan.steps:
            task_state.current_step = step.step_id
            task_state.pending_steps.remove(step.step_id)
            
            logger.info("Executing step", step_id=step.step_id, tool=step.tool, type=step.type)
            
            # Execute step
            step_result = await self._execute_step(step)
            
            # Log execution
            task_state.execution_log.append({
                "step_id": step.step_id,
                "status": "success" if step_result.success else "failed",
                "timestamp": datetime.now().isoformat(),
                "message": step_result.message
            })
            
            # Write audit log
            await self._write_audit_log(step, step_result)
            
            if not step_result.success:
                logger.error("Step failed", step_id=step.step_id, error=step_result.error)
                final_result = step_result
                task_state.status = "failed"
                task_state.error = step_result.error
                break
                
            # Evaluate postconditions
            if self.evaluator.verify_postconditions:
                validated, validation_msg = await self.evaluator.validate(step, step_result)
                
                if not validated:
                    logger.warning("Step validation failed", step_id=step.step_id, message=validation_msg)
                    # Could retry here
                    final_result = ExecutionResult(
                        success=False,
                        error=f"Validation failed: {validation_msg}"
                    )
                    task_state.status = "failed"
                    task_state.error = validation_msg
                    break
                    
        if task_state.status != "failed":
            task_state.status = "success"
            
        # Cleanup
        del self.active_tasks[task_state.task_id]
        
        logger.info("Execution complete", task_id=task_state.task_id, status=task_state.status)
        return final_result
        
    async def _execute_step(self, step) -> ExecutionResult:
        """Execute single step via appropriate tool"""
        
        tool_name = step.tool
        
        # Load tool if not cached
        if tool_name not in self.tools:
            await self._load_tool(tool_name)
            
        if tool_name not in self.tools:
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' not available"
            )
            
        tool = self.tools[tool_name]
        
        try:
            # Execute via tool
            result = await tool.execute(step.type, step.params)
            return result
            
        except Exception as e:
            logger.error("Tool execution error", tool=tool_name, error=str(e), exc_info=True)
            return ExecutionResult(
                success=False,
                error=f"Tool error: {str(e)}"
            )
            
    async def _load_tool(self, tool_name: str):
        """Lazy-load tool"""
        try:
            if tool_name == "os_adapter":
                from tools.os_powershell import PowerShellTool
                self.tools[tool_name] = PowerShellTool(self.config)
                
            elif tool_name == "playwright":
                from tools.playwright_tool import PlaywrightTool
                self.tools[tool_name] = PlaywrightTool(self.config)
                
            elif tool_name == "pyautogui":
                from tools.pyautogui_fallback import PyAutoGUITool
                self.tools[tool_name] = PyAutoGUITool(self.config)
                
            elif tool_name == "memory":
                # Special internal tool (handled separately)
                pass
                
            else:
                logger.warning("Unknown tool", tool=tool_name)
                
        except Exception as e:
            logger.error("Failed to load tool", tool=tool_name, error=str(e))
            
    async def _write_audit_log(self, step, result: ExecutionResult):
        """Write to audit log"""
        entry = AuditLogEntry(
            actor="orchestrator_v1",
            action=f"{step.tool}.{step.type}",
            target=step.tool,
            input_data=step.params,
            result={
                "success": result.success,
                "message": result.message,
                "error": result.error
            }
        )
        
        # Write to file log
        log_file = self.config.get("logging.audit_log", "logs/audit.log")
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.dict()) + "\n")
        except Exception as e:
            logger.error("Failed to write audit log", error=str(e))
            
    async def cancel_all(self):
        """Emergency stop - cancel all running tasks"""
        logger.warning("Cancelling all tasks", count=len(self.active_tasks))
        
        for task_id in list(self.active_tasks.keys()):
            task_state = self.active_tasks[task_id]
            task_state.status = "cancelled"
            task_state.error = "Emergency stop"
            del self.active_tasks[task_id]
            
        # TODO: Send kill signals to running tools
