from tools.base import BaseTool
from utils.logger import setup_logger

logger = setup_logger("text_utils_tool")

class TextUtilsTool(BaseTool):
    name = "text_utils"
    description = "Useful for text operations. Action can be 'count_words', 'upper', 'lower'. Requires 'text' and 'action'."

    def execute(self, **kwargs) -> str:
        text = kwargs.get("text", "")
        action = kwargs.get("action", "")
        
        if not text or not action:
            return "Error: Missing 'text' or 'action' parameter."

        try:
            if action == "count_words":
                result = str(len(text.split()))
            elif action == "upper":
                result = text.upper()
            elif action == "lower":
                result = text.lower()
            else:
                return f"Error: Unknown action '{action}'"
                
            logger.debug(f"TextUtils executed action '{action}' on text.")
            return result
        except Exception as e:
            logger.error(f"Text utils error: {e}")
            return f"Error processing text: {e}"
