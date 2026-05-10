import json
import time
from typing import Dict, Any
from simpcode.core.paths import get_registry_path, get_token_log_path

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

    def log_usage(self, mode: str, input_tokens: int, output_tokens: int):
        log_entry = {
            "timestamp": time.time(),
            "mode": mode,
            "input": input_tokens,
            "output": output_tokens
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
