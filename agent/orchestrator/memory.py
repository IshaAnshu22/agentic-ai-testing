import json
import os
import yaml
from utils.logger import setup_logger

logger = setup_logger("memory")

class MemoryManager:
    def __init__(self, storage_path=None):
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        if storage_path is None:
            config_path = os.path.join(project_root, "config.yaml")
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f).get("orchestrator", {})
                    storage_path = config.get("memory_path", "memory.json")
            except Exception as e:
                logger.error(f"Failed to load Memory config: {e}")
                storage_path = "memory.json"
                
        self.storage_path = os.path.join(project_root, storage_path)
        self.history = []
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.history = json.load(f)
                    logger.debug("Memory loaded from disk.", extra={"extra_info": {"count": len(self.history)}})
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                self.history = []
        else:
            self.history = []

    def _save_memory(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.history, f, indent=2)
                logger.debug("Memory saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def add_message(self, role, content):
        """
        Add a message to the memory.
        role: "user", "assistant", "system", "tool"
        """
        message = {"role": role, "content": content}
        self.history.append(message)
        self._save_memory()
        logger.debug(f"Added message to memory.", extra={"extra_info": {"role": role, "content_preview": str(content)[:100]}})

    def get_history(self):
        return self.history

    def clear(self):
        self.history = []
        self._save_memory()
        logger.info("Memory cleared.")
