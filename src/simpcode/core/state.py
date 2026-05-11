import json
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from simpcode.core.paths import get_registry_path, get_token_log_path, get_logs_dir, get_sessions_dir

class SessionMessage(BaseModel):
    role: str
    content: str
    timestamp: float = Field(default_factory=time.time)

class SessionState(BaseModel):
    session_id: str
    project_root: str
    history: List[SessionMessage] = []
    current_provider: str = "groq"
    current_model: str = "llama-3.3-70b-versatile"
    last_updated: float = Field(default_factory=time.time)

class SessionManager:
    """
    Manages persistence and recovery of interactive engineering sessions.
    Stored in .simp/sessions/
    """
    def __init__(self, project_root: Optional[str] = None):
        self.sessions_dir = get_sessions_dir()
        self.project_root = project_root

    def save_session(self, state: SessionState):
        state.last_updated = time.time()
        file_path = self.sessions_dir / f"{state.session_id}.json"
        with open(file_path, "w") as f:
            f.write(state.model_dump_json(indent=2))

    def load_session(self, session_id: str) -> Optional[SessionState]:
        file_path = self.sessions_dir / f"{session_id}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                return SessionState(**json.load(f))
        return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        sessions = []
        for f in self.sessions_dir.glob("*.json"):
            try:
                with open(f, "r") as src:
                    data = json.load(src)
                    sessions.append({
                        "id": data["session_id"],
                        "last_updated": data["last_updated"],
                        "preview": data["history"][-1]["content"][:50] if data["history"] else "Empty session"
                    })
            except:
                continue
        return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)

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
