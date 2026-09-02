import json
import os
import datetime
from typing import Dict, Any, List

class EvaluationReporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def write_report(self, run_name: str, results: List[Dict[str, Any]], metadata: Dict[str, Any]):
        passed = sum(1 for r in results if r.get("status") == "passed")
        total = len(results)
        
        report = {
            "test_run": datetime.datetime.utcnow().isoformat(),
            "name": run_name,
            "metadata": metadata,
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "results": results
        }
        
        report_path = os.path.join(self.output_dir, f"{run_name}_latest.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report_path
