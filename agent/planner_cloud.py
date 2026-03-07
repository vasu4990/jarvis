"""
Cloud Planner - Complex reasoning using LLM
"""

import asyncio
import structlog
import json
from openai import AsyncOpenAI
from utils.schemas import ParsedCommand, ActionPlan, Step
from typing import Optional

logger = structlog.get_logger(__name__)


class CloudPlanner:
    """Plans complex tasks using cloud LLM"""
    
    SYSTEM_PROMPT = """You are JARVIS, an AI desktop assistant. Your job is to create execution plans for user requests.

You have access to these tools:
- os_adapter: open_app, close_app, search_files, get_system_info
- playwright: open_browser, navigate_url, click_selector, type_selector, fill_form
- pyautogui: click_xy, type_text, press_key

Create a JSON plan with steps. Each step must have:
- step_id: unique ID
- tool: which tool to use
- type: action type
- params: parameters as dict
- permission_level: "allow" or "ask"

Example:
{
  "steps": [
    {"step_id": "s1", "tool": "playwright", "type": "open_browser", "params": {}, "permission_level": "allow"},
    {"step_id": "s2", "tool": "playwright", "type": "navigate_url", "params": {"url": "https://google.com"}, "permission_level": "allow"}
  ]
}

Return ONLY valid JSON."""

    def __init__(self, config):
        self.config = config
        
        api_key = config.get("cloud_llm.api_key")
        model = config.get("cloud_llm.model", "gpt-4-turbo-preview")
        
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            logger.warning("Cloud LLM API key not configured")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = model
            logger.info("Cloud planner initialized", model=model)
            
    async def plan(self, command: ParsedCommand, vector_store=None) -> Optional[ActionPlan]:
        """Generate complex plan using LLM"""
        
        if not self.client:
            logger.error("Cloud LLM not configured")
            return None
            
        try:
            # Build prompt with context
            user_prompt = f"User request: {command.text}\n\nIntent: {command.intent}\nSlots: {json.dumps(command.slots)}"
            
            # Add RAG context if available
            rag_context = command.provenance.get("rag_context", [])
            if rag_context:
                context_str = "\n".join([f"- {c['text']}" for c in rag_context])
                user_prompt += f"\n\nRelevant context from memory:\n{context_str}"
                
            logger.info("Requesting cloud plan", prompt_len=len(user_prompt))
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            plan_data = json.loads(content)
            
            # Convert to ActionPlan
            steps = [
                Step(**step_dict) for step_dict in plan_data.get("steps", [])
            ]
            
            if not steps:
                logger.warning("Cloud plan has no steps")
                return None
                
            plan = ActionPlan(
                command_id=command.command_id,
                steps=steps,
                created_by="cloud_planner_v1"
            )
            
            logger.info("Cloud plan created", steps=len(steps))
            return plan
            
        except Exception as e:
            logger.error("Cloud planning failed", error=str(e), exc_info=True)
            return None
            
    async def simple_answer(self, question: str) -> str:
        """Get simple Q&A answer from cloud"""
        
        if not self.client:
            return "I'm not configured to answer that."
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are JARVIS, a helpful desktop AI assistant. Answer briefly and clearly."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=256
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error("Simple answer failed", error=str(e))
            return "Sorry, I couldn't process that."
