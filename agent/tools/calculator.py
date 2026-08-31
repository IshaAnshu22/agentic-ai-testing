from tools.base import BaseTool
from utils.logger import setup_logger

logger = setup_logger("calculator_tool")

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Useful for performing mathematical calculations. Requires 'expression' string like '2 + 2'."

    def execute(self, **kwargs) -> str:
        expression = kwargs.get("expression")
        if not expression:
            return "Error: Missing 'expression' parameter."

        try:
            # Safe eval with restricted builtins
            allowed_names = {"__builtins__": None}
            result = eval(expression, allowed_names, {})
            logger.debug(f"Calculator executed: {expression} = {result}")
            return str(result)
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return f"Error evaluating expression: {e}"
