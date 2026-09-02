import pytest
import os
import json
from orchestrator.supervisor import Supervisor
from llm.client import MockLLMClient

@pytest.fixture
def mock_llm_client():
    return MockLLMClient()

@pytest.fixture
def supervisor(mock_llm_client):
    # Ensure memory is clean
    if os.path.exists("memory.json"):
        os.remove("memory.json")
        
    s = Supervisor(llm_client=mock_llm_client)
    # Ensure we use deterministic rule-based planner for unit/integration tests unless specified
    # Or we can let it be whatever is in config but inject mock responses
    return s

@pytest.fixture
def empty_trace():
    trace_file = "logs/trace.log"
    os.makedirs(os.path.dirname(trace_file), exist_ok=True)
    open(trace_file, 'w').close()
    return trace_file
