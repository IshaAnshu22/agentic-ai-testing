import json
import os
from typing import List, Dict, Any

class TraceValidator:
    def __init__(self, log_path: str):
        self.log_path = log_path

    def read_logs(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.log_path):
            return []
            
        logs = []
        with open(self.log_path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    # Our logger outputs json-like structured logs
                    # (Assuming it's JSONL or can be parsed. If not, basic string parsing might be needed)
                    # Let's assume standard json format for the sake of structured testing
                    # If it's a standard Python logger string format, we might need a regex
                    log_data = json.loads(line)
                    logs.append(log_data)
                except json.JSONDecodeError:
                    # Fallback for plain text logs
                    logs.append({"raw": line})
        return logs

    def count_tool_calls(self) -> int:
        logs = self.read_logs()
        count = 0
        for log in logs:
             # Basic heuristic if raw logs:
             if "raw" in log and "Executing step:" in log["raw"]:
                 count += 1
             elif log.get("message", "").startswith("Executing step:"):
                 count += 1
        return count
