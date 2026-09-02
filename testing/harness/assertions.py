from typing import List, Dict, Any

class AgentAssertions:
    """Reusable assertions for deterministic Agent SUT testing."""
    
    @staticmethod
    def assert_tool_used(trace_logs: List[Dict[str, Any]], expected_tool: str):
        """Asserts that a specific tool was used in the execution trace."""
        tool_used = False
        for log in trace_logs:
            if "extra_info" in log and "plan" in log["extra_info"]:
                plan = log["extra_info"]["plan"]
                if any(step.get("tool") == expected_tool for step in plan):
                    tool_used = True
                    break
        assert tool_used, f"Expected tool '{expected_tool}' was not used."

    @staticmethod
    def assert_guardrail_blocked(response: str):
        """Asserts that the response was blocked by guardrails."""
        assert "blocked by guardrails" in response.lower(), "Expected guardrail block, but none occurred."

    @staticmethod
    def assert_response_contains(response: str, expected_substrings: List[str]):
        """Asserts that the final response contains all expected substrings."""
        for substring in expected_substrings:
            assert substring.lower() in response.lower(), f"Expected substring '{substring}' not found in response: '{response}'"
            
    @staticmethod
    def assert_plan_length(trace_logs: List[Dict[str, Any]], expected_length: int):
        """Asserts the planner generated exactly expected_length steps."""
        for log in trace_logs:
            if "extra_info" in log and "plan" in log["extra_info"]:
                plan = log["extra_info"]["plan"]
                assert len(plan) == expected_length, f"Expected plan length {expected_length}, got {len(plan)}"
                return
        assert False, "No plan found in trace logs."
