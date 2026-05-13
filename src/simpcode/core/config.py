import json
import os
from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel, Field

class LLMProviderConfig(BaseModel):
    provider: str
    model_id: str
    api_key: str
    base_url: Optional[str] = None

class SimpConfig(BaseModel):
    active_provider: str = "groq"
    providers: Dict[str, LLMProviderConfig] = Field(default_factory=dict)
    
from simpcode.utils.paths import PathManager

class ConfigManager:
    """
    SimpCode Config Manager: Handles global and local settings.
    Uses PathManager to resolve writable locations.
    """

    def __init__(self, root: Optional[Path] = None):
        if root is None:
            root = PathManager.find_project_root()
            
        self.config_path = PathManager.resolve_writable_path(root, "config.json")
        self._writable = self.config_path is not None
        self.config = self._load()

    def _load(self) -> SimpConfig:
        try:
            if self._writable and self.config_path.exists():
                data = json.loads(self.config_path.read_text())
                return SimpConfig(**data)
        except Exception:
            pass
        return SimpConfig()

    def save(self, config: SimpConfig):
        self.config = config
        if self._writable:
            try:
                self.config_path.write_text(config.model_dump_json(indent=2))
            except (PermissionError, OSError):
                self._writable = False

    def get_active_config(self) -> Optional[LLMProviderConfig]:
        return self.config.providers.get(self.config.active_provider)


# Global instance (Defaults to CWD root)
global_config = ConfigManager()
