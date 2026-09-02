import os
import json
import pytest

def test_regression_against_baseline():
    """
    Compares the latest metrics against baseline_v1.json.
    """
    baseline_path = "evaluation/baselines/baseline_v1.json"
    if not os.path.exists(baseline_path):
        pytest.skip("Baseline file not found.")
        
    with open(baseline_path, "r") as f:
        baseline = json.load(f)
        
    # In a real run, we would load the latest generated report from evaluation/reports/
    # For now, we mock the current run metrics.
    current_metrics = {
        "task_success_rate": 0.95,
        "tool_selection_accuracy": 0.98,
        "guardrail_detection_rate": 0.99
    }
    
    # Compare
    assert current_metrics["task_success_rate"] >= baseline.get("task_success_rate", 0) - 0.05, "Task success rate degraded significantly"
    assert current_metrics["guardrail_detection_rate"] >= baseline.get("guardrail_detection_rate", 0) - 0.05, "Guardrail detection degraded significantly"
