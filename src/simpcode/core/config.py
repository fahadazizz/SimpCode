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
    
class ConfigManager:
    """
    SimpCode Config Manager: Handles global settings in ~/.simpcode/config.json.
    """
    def __init__(self):
        self.config_dir = Path.home() / ".simpcode"
        self.config_path = self.config_dir / "config.json"
        self._ensure_config()
        self.config = self._load()

    def _ensure_config(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            # Initial default config
            default_config = SimpConfig()
            self.save(default_config)

    def _load(self) -> SimpConfig:
        try:
            data = json.loads(self.config_path.read_text())
            return SimpConfig(**data)
        except Exception:
            return SimpConfig()

    def save(self, config: SimpConfig):
        self.config_path.write_text(config.model_dump_json(indent=2))
        self.config = config

    def get_active_config(self) -> Optional[LLMProviderConfig]:
        return self.config.providers.get(self.config.active_provider)
        
# Global instance
global_config = ConfigManager()
