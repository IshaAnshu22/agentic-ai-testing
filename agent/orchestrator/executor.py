from utils.logger import setup_logger

logger = setup_logger("executor")

class WorkflowExecutor:
    def __init__(self, tools: list):
        self.tools = {t.name: t for t in tools}

    def execute_plan(self, plan: list) -> list:
        results = []
        for step in plan:
            tool_name = step.get("tool")
            args = step.get("args", {})
            
            logger.info(f"Executing step: {tool_name}")
            
            if tool_name not in self.tools:
                error_msg = f"Tool '{tool_name}' not found."
                logger.error(error_msg)
                results.append({"tool": tool_name, "status": "error", "result": error_msg})
                continue
                
            tool_instance = self.tools[tool_name]
            try:
                result = tool_instance.execute(**args)
                results.append({"tool": tool_name, "status": "success", "result": result})
                logger.debug(f"Step '{tool_name}' completed.", extra={"extra_info": {"result": result}})
            except Exception as e:
                error_msg = f"Execution failed: {e}"
                logger.error(error_msg)
                results.append({"tool": tool_name, "status": "error", "result": error_msg})
                
        return results
