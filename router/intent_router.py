"""
Intent Router - Determines local vs cloud processing
"""

import asyncio
import yaml
import structlog
from pathlib import Path
from typing import Optional
from utils.schemas import Utterance, ParsedCommand

logger = structlog.get_logger(__name__)


class IntentRouter:
    """Routes intents to local or cloud processing"""
    
    def __init__(self, config):
        self.config = config
        
        # Load routing policy
        policy_file = config.get("router.routing_policy_file", "router/routing_policy.yaml")
        self.policy = self._load_policy(policy_file)
        
        self.confidence_threshold = config.get("router.confidence_threshold", 0.7)
        
        logger.info("Intent router initialized")
        
    def _load_policy(self, policy_file: str) -> dict:
        """Load routing policy from YAML"""
        try:
            with open(policy_file, 'r', encoding='utf-8') as f:
                policy = yaml.safe_load(f)
            logger.info("Routing policy loaded", file=policy_file)
            return policy
        except Exception as e:
            logger.error("Failed to load routing policy", error=str(e))
            return {"local_capable": [], "cloud_required": []}
            
    async def route(self, utterance: Utterance, vector_store=None) -> ParsedCommand:
        """
        Route utterance to appropriate intent handler
        
        Returns ParsedCommand with intent, slots, and routing info
        """
        text = utterance.text.lower().strip()
        
        # Rule-based intent classification (MVP)
        intent, confidence, slots = await self._classify_intent_rules(text)
        
        # Determine if cloud required
        cloud_required = self._requires_cloud(intent, confidence)
        
        # Try RAG context if available
        rag_context = []
        if vector_store and intent in ["simple_qa", "recall_fact"]:
            rag_context = await vector_store.query(text, top_k=3)
            
        logger.info(
            "Intent routed",
            intent=intent,
            confidence=confidence,
            cloud_required=cloud_required,
            rag_hits=len(rag_context)
        )
        
        # Create ParsedCommand
        command = ParsedCommand(
            utterance_id=utterance.utterance_id,
            intent=intent,
            intent_confidence=confidence,
            slots=slots,
            text=text,
            provenance={
                "router": "rule_based",
                "cloud_required": cloud_required,
                "cloud_used": False,  # Will be set by planner
                "rag_context": rag_context
            }
        )
        
        return command
        
    async def _classify_intent_rules(self, text: str) -> tuple[str, float, dict]:
        """
        Rule-based intent classification using keywords
        
        Returns: (intent, confidence, slots)
        """
        intent_keywords = self.policy.get("intent_keywords", {})
        
        # Check each intent's keywords
        matches = []
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    matches.append((intent, len(keyword)))
                    break
                    
        if not matches:
            # Default to simple_qa
            return ("simple_qa", 0.5, {})
            
        # Pick intent with longest matching keyword (more specific)
        best_intent = max(matches, key=lambda x: x[1])[0]
        
        # Extract slots based on intent
        slots = await self._extract_slots(text, best_intent)
        
        # Calculate confidence based on keyword match quality
        confidence = 0.8 if len(matches) == 1 else 0.6
        
        return (best_intent, confidence, slots)
        
    async def _extract_slots(self, text: str, intent: str) -> dict:
        """Extract slot values from text based on intent"""
        slots = {}
        
        if intent == "open_app":
            # Extract app name (words after "open"/"launch"/"start")
            for trigger in ["open", "launch", "start", "run"]:
                if trigger in text:
                    parts = text.split(trigger, 1)
                    if len(parts) > 1:
                        app_name = parts[1].strip()
                        slots["app_name"] = app_name
                        break
                        
        elif intent == "search_files":
            # Extract search query
            for trigger in ["search", "find", "look for"]:
                if trigger in text:
                    parts = text.split(trigger, 1)
                    if len(parts) > 1:
                        query = parts[1].strip().replace(" for ", "").replace(" in ", "")
                        slots["search_query"] = query
                        break
                        
        elif intent == "navigate_to":
            # Extract URL or site name
            for trigger in ["go to", "navigate", "visit"]:
                if trigger in text:
                    parts = text.split(trigger, 1)
                    if len(parts) > 1:
                        target = parts[1].strip()
                        slots["target"] = target
                        break
                        
        elif intent == "remember_fact":
            # Extract fact
            for trigger in ["remember", "save", "note that"]:
                if trigger in text:
                    parts = text.split(trigger, 1)
                    if len(parts) > 1:
                        fact = parts[1].strip()
                        slots["fact"] = fact
                        break
                        
        return slots
        
    def _requires_cloud(self, intent: str, confidence: float) -> bool:
        """Determine if intent requires cloud processing"""
        
        # Always use cloud if confidence is very low
        if confidence < self.confidence_threshold:
            return True
            
        # Check explicit cloud required list
        cloud_required = self.policy.get("cloud_required", [])
        if intent in cloud_required:
            return True
            
        # Check explicit local capable list
        local_capable = self.policy.get("local_capable", [])
        if intent in local_capable:
            return False
            
        # Default to cloud for unknown intents
        return True
