from typing import Dict, Any, List
from orchestrator.supervisor import Supervisor
from testing.harness.testcase import AgentTestCase
from testing.harness.assertions import AgentAssertions
from testing.trace.validator import TraceValidator

class AgentTestRunner:
    def __init__(self, supervisor: Supervisor, trace_file: str):
        self.supervisor = supervisor
        self.trace_file = trace_file

    def run_case(self, case: AgentTestCase) -> Dict[str, Any]:
        """Runs a single test case through the supervisor and returns results."""
        # Clear trace before run
        open(self.trace_file, 'w').close()
        
        # Execute
        response = self.supervisor.run(case.user_input)
        
        # Validate
        validator = TraceValidator(self.trace_file)
        logs = validator.read_logs()
        
        result = {
            "test_id": case.test_id,
            "status": "passed",
            "error": None
        }
        
        try:
            if case.expected_guardrail_block:
                AgentAssertions.assert_guardrail_blocked(response)
            else:
                for tool in case.expected_tools:
                    AgentAssertions.assert_tool_used(logs, tool)
                if case.expected_response_contains:
                    AgentAssertions.assert_response_contains(response, case.expected_response_contains)
                if case.expected_plan_steps is not None:
                    AgentAssertions.assert_plan_length(logs, case.expected_plan_steps)
        except AssertionError as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
        return result
