import yaml
import os
from orchestrator.memory import MemoryManager
from orchestrator.guardrails import GuardrailManager
from orchestrator.planners import RuleBasedPlanner, LLMBasedPlanner
from orchestrator.executor import WorkflowExecutor
from tools.calculator import CalculatorTool
from tools.text_utils import TextUtilsTool
from tools.rag_tool import RAGTool
from llm.client import LLMClient, OllamaLLMClient
from utils.logger import setup_logger

logger = setup_logger("supervisor")

class Supervisor:
    def __init__(self, llm_client: LLMClient = None):
        project_root = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(project_root, "config.yaml")
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f).get("orchestrator", {})
        except Exception as e:
            logger.error(f"Failed to load Supervisor config: {e}")
            self.config = {}

        self.memory = MemoryManager()
        self.guardrails = GuardrailManager()
        
        self.tools = [CalculatorTool(), TextUtilsTool(), RAGTool()]
        self.executor = WorkflowExecutor(self.tools)
        self.llm = llm_client if llm_client is not None else OllamaLLMClient()
        
        planner_type = self.config.get("planner_type", "rule_based")
        if planner_type == "llm_based":
            self.planner = LLMBasedPlanner(llm_client=self.llm)
        else:
            self.planner = RuleBasedPlanner()
            
        logger.info(f"Supervisor initialized with {planner_type} planner.")

    def run(self, user_input: str) -> str:
        logger.info("Supervisor received new task.", extra={"extra_info": {"user_input": user_input}})
        self.memory.add_message("user", user_input)
        
        # 1. Input Guardrails
        is_valid, reason = self.guardrails.check_input(user_input)
        if not is_valid:
            response = f"Input blocked by guardrails: {reason}"
            self.memory.add_message("assistant", response)
            return response
            
        # 2. Plan
        plan = self.planner.plan(user_input, self.tools)
        if not plan:
            logger.warning("Planner returned empty plan.")
            
        # 3. Execute Workflow
        execution_results = self.executor.execute_plan(plan)
        
        # 4. Generate Final Response using LLM
        context = f"User Request: {user_input}\n\nTool Execution Results:\n"
        for res in execution_results:
            context += f"- Tool: {res['tool']} | Status: {res['status']} | Output: {res['result']}\n"
            
        system_prompt = "You are an assistant. Answer the user's request based on the tool execution results provided. Keep your answer concise."
        
        final_output = self.llm.generate(prompt=context, system=system_prompt)
        
        # 5. Output Guardrails
        is_valid, reason = self.guardrails.check_output(final_output)
        if not is_valid:
            final_output = f"Output blocked by guardrails: {reason}"
            
        self.memory.add_message("assistant", final_output)
        logger.info("Supervisor workflow completed.")
        
        return final_output
