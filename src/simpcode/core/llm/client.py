import os
from typing import List, Dict, Any, Optional
from .base import LLMProvider
from .openai_provider import OpenAICompatibleProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from simpcode.core.config import global_config
from simpcode.core.prompts import registry
from simpcode.core.state import TokenLogger

class LLMClient:
    """
    SimpCode LLM Orchestrator: Factory that instantiates the correct provider 
    based on global configuration.
    """
    def __init__(self, provider: Optional[str] = None, model_id: Optional[str] = None):
        self.config = global_config.get_active_config()
        
        # Priority: Constructor Args > Config File > Environment Variables
        self.provider_name = provider or (self.config.provider if self.config else os.getenv("SIMP_LLM_PROVIDER", "groq"))
        self.model_id = model_id or (self.config.model_id if self.config else os.getenv("SIMP_LLM_MODEL", "llama-3.3-70b-versatile"))
        self.api_key = (self.config.api_key if self.config else None) or os.getenv(f"{self.provider_name.upper()}_API_KEY")
        
        self.logger = TokenLogger()
        self.provider = self._instantiate_provider()

    def _instantiate_provider(self) -> LLMProvider:
        if self.provider_name == "anthropic":
            return AnthropicProvider(self.model_id, self.api_key)
        elif self.provider_name == "google":
            return GoogleProvider(self.model_id, self.api_key)
        elif self.provider_name == "groq":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://api.groq.com/openai/v1", "groq")
        elif self.provider_name == "openrouter":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://openrouter.ai/api/v1", "openrouter")
        elif self.provider_name == "openai":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://api.openai.com/v1", "openai")
        elif self.provider_name == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            return OpenAICompatibleProvider(self.model_id, "ollama", base_url, "ollama")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider_name}")

    def chat(self, messages: List[Dict[str, str]], system_instruction: Optional[str] = None) -> str:
        # Hierarchical Composition
        full_system = system_instruction or registry.load("base_principles")
        
        response = self.provider.chat(messages, full_system)
        
        # Log usage
        usage = self.provider.get_token_usage()
        self.logger.log_usage(self.model_id, usage["input"], usage["output"])
        
        return response

    def structured_output(self, prompt: str, schema: Any, system_instruction: Optional[str] = None) -> Any:
        # Ensure base principles are included
        full_system = system_instruction or registry.load("base_principles")
        if "---" not in full_system:
             full_system = registry.load("base_principles") + "\n\n---\n\n" + (system_instruction or "")
             
        response = self.provider.structured_output(prompt, schema, full_system)
        
        # Log usage
        usage = self.provider.get_token_usage()
        self.logger.log_usage(self.model_id, usage["input"], usage["output"])
        
        return response
