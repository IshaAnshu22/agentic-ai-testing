import json
from abc import ABC, abstractmethod
from llm.client import LLMClient, OllamaLLMClient
from utils.logger import setup_logger

logger = setup_logger("planners")

class BasePlanner(ABC):
    @abstractmethod
    def plan(self, user_input: str, tools_list: list) -> list:
        pass

class RuleBasedPlanner(BasePlanner):
    """
    A simple rule-based planner for testing purposes.
    It returns hardcoded tool sequences based on keyword matching.
    """
    def plan(self, user_input: str, tools_list: list) -> list:
        logger.info("Using RuleBasedPlanner")
        user_input_lower = user_input.lower()
        
        plan = []
        if "calculate" in user_input_lower or "+" in user_input_lower:
            plan.append({"tool": "calculator", "args": {"expression": "2 + 2"}})
        if "search" in user_input_lower or "rag" in user_input_lower:
            plan.append({"tool": "rag_search", "args": {"query": user_input}})
            
        if not plan:
             # Default fallback
             plan.append({"tool": "text_utils", "args": {"text": user_input, "action": "count_words"}})
             
        logger.debug(f"RuleBasedPlanner generated plan", extra={"extra_info": {"plan": plan}})
        return plan

class LLMBasedPlanner(BasePlanner):
    """
    Uses an LLM to dynamically generate a sequence of tool calls.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client if llm_client is not None else OllamaLLMClient()

    def plan(self, user_input: str, tools_list: list) -> list:
        logger.info("Using LLMBasedPlanner")
        
        tools_description = "\n".join([f"- {t.name}: {t.description}" for t in tools_list])
        
        system_prompt = f"""You are a planner agent. Your goal is to break down the user's request into a sequence of tool calls.
Available tools:
{tools_description}

You must respond ONLY with a valid JSON list of objects, where each object represents a step in the plan.
Format:
[
  {{"tool": "tool_name", "args": {{"arg_name": "arg_value"}}}},
  ...
]
Do not add any markdown, explanation, or conversational text. Just the raw JSON array.
If no tools are needed, return an empty list [].
"""
        
        prompt = f"User Request: {user_input}"
        response_text = self.llm.generate(prompt=prompt, system=system_prompt, response_format="json")
        
        if response_text.startswith("Error:"):
            logger.error(f"LLMBasedPlanner aborted due to LLM error: {response_text}")
            return []
            
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                
            plan = json.loads(cleaned.strip())
            
            if isinstance(plan, dict):
                plan = [plan]
            elif not isinstance(plan, list):
                logger.warning(f"Planner returned invalid JSON type: {type(plan)}. Defaulting to empty list.")
                plan = []
                
            logger.debug(f"LLMBasedPlanner generated plan", extra={"extra_info": {"plan": plan}})
            return plan
        except Exception as e:
            logger.error(f"LLMBasedPlanner failed to parse JSON: {e}", extra={"extra_info": {"raw_response": response_text}})
            return []
