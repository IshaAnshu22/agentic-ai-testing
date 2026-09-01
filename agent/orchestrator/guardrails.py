import yaml
import os
from utils.logger import setup_logger

logger = setup_logger("guardrails")

class GuardrailManager:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f).get("guardrails", {})
        except Exception as e:
            logger.error(f"Failed to load guardrails config: {e}")
            self.config = {"input": {"enabled": False}, "output": {"enabled": False}}

    def check_input(self, text: str) -> tuple[bool, str]:
        """
        Returns (is_valid, reason)
        """
        input_config = self.config.get("input", {})
        if not input_config.get("enabled", False):
            return True, ""

        blocked_keywords = input_config.get("blocked_keywords", [])
        text_lower = text.lower()
        
        for keyword in blocked_keywords:
            if keyword.lower() in text_lower:
                reason = f"Input contained blocked keyword: '{keyword}'"
                logger.warning(f"Input guardrail triggered.", extra={"extra_info": {"reason": reason}})
                return False, reason
                
        return True, ""

    def check_output(self, text: str) -> tuple[bool, str]:
        """
        Returns (is_valid, reason)
        """
        output_config = self.config.get("output", {})
        if not output_config.get("enabled", False):
            return True, ""

        blocked_keywords = output_config.get("blocked_keywords", [])
        text_lower = text.lower()
        
        for keyword in blocked_keywords:
            if keyword.lower() in text_lower:
                reason = f"Output contained blocked keyword: '{keyword}'"
                logger.warning(f"Output guardrail triggered.", extra={"extra_info": {"reason": reason}})
                return False, reason
                
        return True, ""
