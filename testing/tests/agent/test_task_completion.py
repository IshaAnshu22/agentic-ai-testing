import pytest
from testing.harness.testcase import AgentTestCase
from testing.harness.runner import AgentTestRunner

def test_task_completion_deterministic(supervisor, empty_trace, mock_llm_client):
    """
    End-to-end task success test using deterministic MockLLM.
    We test if the supervisor successfully processes a request, generates the right plan (via planner),
    and gives the final response.
    """
    
    # Setup mock LLM behavior
    # First call will be the planner (if using LLMBasedPlanner) - but wait, the planner expects JSON.
    # To make this robust regardless of config, we'll supply a plan if it's LLMBased.
    import yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    if config.get("orchestrator", {}).get("planner_type") == "llm_based":
        mock_llm_client.predefined_responses = [
            '[{"tool": "calculator", "args": {"expression": "125 * 48 + 300"}}]', # Plan
            'The final result is 6300.' # Final answer
        ]
    else:
        mock_llm_client.predefined_responses = [
            'The final result is 6300.' # Final answer only
        ]

    case = AgentTestCase(
        test_id="TASK_001",
        name="Calculate expression and get final result",
        user_input="Calculate 125 * 48 + 300",
        expected_tools=["calculator"],
        expected_response_contains=["6300"],
        expected_plan_steps=1
    )
    
    runner = AgentTestRunner(supervisor, empty_trace)
    result = runner.run_case(case)
    
    assert result["status"] == "passed", f"Agent failed to complete task: {result.get('error')}"
