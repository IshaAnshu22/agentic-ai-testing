import requests
import yaml
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from utils.logger import setup_logger

logger = setup_logger("llm_client")

class LLMClient(ABC):
    """Base interface for LLM clients."""
    @abstractmethod
    def generate(self, prompt: str, system: str = "", response_format: str = None) -> str:
        pass


class OllamaLLMClient(LLMClient):
    """Production LLM client connecting to Ollama."""
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(project_root, "config.yaml")
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f).get("llm", {})
        except Exception as e:
            logger.error(f"Failed to load LLM config: {e}")
            self.config = {}

        self.base_url = self.config.get("base_url", "http://localhost:11434/api/generate")
        self.model = self.config.get("model", "llama3")
        self.temperature = self.config.get("temperature", 0.1)
        self.timeout = self.config.get("timeout", 180)

    def generate(self, prompt: str, system: str = "", response_format: str = None) -> str:
        # We explicitly log the prompt that is about to go to the LLM for testing tracebility
        logger.debug("Sending prompt to LLM.", extra={"extra_info": {"prompt": prompt, "system": system, "model": self.model}})
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "temperature": self.temperature,
            "stream": False
        }
        
        if response_format:
            payload["format"] = response_format

        try:
            response = requests.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json().get("response", "")
            
            logger.debug("Received response from LLM.", extra={"extra_info": {"response": result}})
            return result
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Error: LLM API request failed - {e}"


