import json
import time
from typing import Dict, Any, Optional
from simpcode.core.paths import get_registry_path, get_token_log_path, get_logs_dir

class HashRegistry:
    def __init__(self):
        self.path = get_registry_path()
        self.data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self.path.exists():
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def set_hash(self, file_path: str, file_hash: str):
        self.data[file_path] = file_hash
        self.save()

    def get_hash(self, file_path: str) -> str:
        return self.data.get(file_path)

class TokenLogger:
    def __init__(self):
        self.path = get_token_log_path()

    def log_usage(self, model: str, input_tokens: int, output_tokens: int):
        log_entry = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "model": model,
            "input": input_tokens,
            "output": output_tokens,
            "cost_est": (input_tokens * 0.000001) + (output_tokens * 0.000003) # Placeholder
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

class ExecutionLogger:
    """
    Logs detailed tool execution traces for auditability and 'Get Better' mode.
    """
    def __init__(self, session_id: str):
        self.log_path = get_logs_dir() / f"exec_{session_id}.jsonl"

    def log_event(self, tool: str, args: Dict[str, Any], result: str, status: str = "success"):
        entry = {
            "timestamp": time.time(),
            "tool": tool,
            "args": args,
            "result_summary": result[:500],
            "status": status
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
