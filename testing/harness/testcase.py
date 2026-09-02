import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger("testing.testcase")

@dataclass
class AgentTestCase:
    test_id: str
    name: str
    user_input: str
    expected_tools: List[str] = field(default_factory=list)
    expected_response_contains: List[str] = field(default_factory=list)
    expected_plan_steps: Optional[int] = None
    expected_guardrail_block: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTestCase":
        return cls(
            test_id=data.get("test_id", "UNKNOWN"),
            name=data.get("name", "Unnamed Test"),
            user_input=data.get("user_input", ""),
            expected_tools=data.get("expected_tools", []),
            expected_response_contains=data.get("expected_response_contains", []),
            expected_plan_steps=data.get("expected_plan_steps"),
            expected_guardrail_block=data.get("expected_guardrail_block", False)
        )

def load_test_cases(file_path: str) -> List[AgentTestCase]:
    cases = []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            for item in data:
                cases.append(AgentTestCase.from_dict(item))
    except Exception as e:
        logger.error(f"Failed to load test cases from {file_path}: {e}")
    return cases
