import os
import time
import functools
from typing import List, Dict, Any, Optional, Iterator

from .anthropic_provider import AnthropicProvider
from .base import LLMProvider
from .google_provider import GoogleProvider
from .openai_provider import OpenAICompatibleProvider
from simpcode.core.config import LLMProviderConfig, global_config
from simpcode.core.paths import get_project_root
from simpcode.core.prompts import registry
from simpcode.core.state import TokenLogger


_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 529}


def _is_retryable_error(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    if status_code in _RETRYABLE_STATUS_CODES:
        return True

    response = getattr(error, "response", None)
    if response is not None and getattr(response, "status_code", None) in _RETRYABLE_STATUS_CODES:
        return True

    error_msg = str(error).lower()
    return any(code in error_msg for code in ["429", "529", "too many requests", "rate limit", "502", "503", "500"])

def with_backoff(max_retries=3, base_delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if _is_retryable_error(e):
                        if attempt == max_retries - 1:
                            raise
                        print(f"API rate limit or server error ({e}). Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise
        return wrapper
    return decorator

class LLMClient:
    """
    SimpCode LLM orchestrator.

    Resolves provider settings from persisted config first, then environment
    variables. Long-lived callers can refresh the active provider/model through
    `refresh()` after session or config changes.
    """

    def __init__(self, provider: Optional[str] = None, model_id: Optional[str] = None):
        self.logger = TokenLogger()
        self._requested_provider = provider
        self._requested_model_id = model_id
        self.provider_name = provider or self._resolve_active_provider()
        self.model_id = self._resolve_model_id(self.provider_name, model_id)
        self.api_key = self._resolve_api_key(self.provider_name)
        self.base_url = self._resolve_base_url(self.provider_name)
        self.provider = self._instantiate_provider()

    def _resolve_active_provider(self) -> str:
        config = global_config.config
        if config and config.active_provider:
            return config.active_provider
        return os.getenv("SIMP_LLM_PROVIDER", "groq")

    def _provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        config = global_config.config
        if config and provider_name in config.providers:
            return config.providers[provider_name]
        return None

    def _resolve_model_id(self, provider_name: str, requested_model_id: Optional[str]) -> str:
        if requested_model_id:
            return requested_model_id

        provider_config = self._provider_config(provider_name)
        if provider_config and provider_config.model_id:
            return provider_config.model_id

        return os.getenv("SIMP_LLM_MODEL", "llama-3.3-70b-versatile")

    def _resolve_api_key(self, provider_name: str) -> str:
        provider_config = self._provider_config(provider_name)
        if provider_config and provider_config.api_key:
            return provider_config.api_key

        return os.getenv(f"{provider_name.upper()}_API_KEY", "")

    def _resolve_base_url(self, provider_name: str) -> Optional[str]:
        provider_config = self._provider_config(provider_name)
        if provider_config and provider_config.base_url:
            return provider_config.base_url

        if provider_name == "ollama":
            return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        return None

    def refresh(self, provider: Optional[str] = None, model_id: Optional[str] = None) -> None:
        """Refresh provider/model settings from the latest persisted config."""
        next_provider = provider or self._requested_provider or self._resolve_active_provider()
        next_model = model_id or self._requested_model_id

        resolved_model = self._resolve_model_id(next_provider, next_model)
        resolved_api_key = self._resolve_api_key(next_provider)
        resolved_base_url = self._resolve_base_url(next_provider)

        if (
            next_provider != self.provider_name
            or resolved_model != self.model_id
            or resolved_api_key != self.api_key
            or resolved_base_url != self.base_url
        ):
            self._requested_provider = provider or self._requested_provider
            self._requested_model_id = model_id or self._requested_model_id
            self.provider_name = next_provider
            self.model_id = resolved_model
            self.api_key = resolved_api_key
            self.base_url = resolved_base_url
            self.provider = self._instantiate_provider()

    def _instantiate_provider(self) -> LLMProvider:
        if self.provider_name == "anthropic":
            return AnthropicProvider(self.model_id, self.api_key)
        if self.provider_name == "google":
            return GoogleProvider(self.model_id, self.api_key)
        if self.provider_name == "groq":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://api.groq.com/openai/v1", "groq")
        if self.provider_name == "openrouter":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://openrouter.ai/api/v1", "openrouter")
        if self.provider_name == "openai":
            return OpenAICompatibleProvider(self.model_id, self.api_key, "https://api.openai.com/v1", "openai")
        if self.provider_name == "ollama":
            base_url = self.base_url or self._resolve_base_url("ollama") or "http://localhost:11434/v1"
            return OpenAICompatibleProvider(self.model_id, self.api_key, base_url, "ollama")
        raise ValueError(f"Unsupported LLM provider: {self.provider_name}")

    def _build_system_instruction(self, system_instruction: Optional[str], is_structured: bool = False) -> str:
        base = registry.load("base_principles")
        if is_structured and system_instruction and "---" not in (system_instruction or ""):
            if "---" not in base:
                base = base + "\n\n---\n\n" + system_instruction
            else:
                base = system_instruction
        else:
            base = system_instruction or base

        try:
            root = get_project_root()
            simp_path = root / "SIMP.md"
            if simp_path.exists():
                simp_content = simp_path.read_text().strip()
                if "---" in base:
                    return f"{simp_content}\n\n{base}"
                else:
                    return f"{simp_content}\n\n---\n\n{base}"
        except Exception:
            pass

        return base

    @with_backoff()
    def chat(self, messages: List[Dict[str, str]], system_instruction: Optional[str] = None) -> str:
        self.refresh()
        full_system = self._build_system_instruction(system_instruction)

        response = self.provider.chat(messages, full_system)

        usage = self.provider.get_token_usage()
        self.logger.log_usage(self.model_id, usage["input"], usage["output"])

        return response

    def stream_chat(self, messages: List[Dict[str, str]], system_instruction: Optional[str] = None) -> Iterator[str]:
        """Streams chat output when the active provider supports it, otherwise yields one full response."""
        self.refresh()
        full_system = self._build_system_instruction(system_instruction)
        stream_method = getattr(self.provider, "stream_chat", None)

        if not callable(stream_method):
            yield self.chat(messages, system_instruction)
            return

        chunks: List[str] = []
        for chunk in stream_method(messages, full_system):
            if not chunk:
                continue
            chunks.append(chunk)
            yield chunk

        usage = self.provider.get_token_usage()
        self.logger.log_usage(self.model_id, usage["input"], usage["output"])

    @with_backoff()
    def structured_output(self, prompt: str, schema: Any, system_instruction: Optional[str] = None) -> Any:
        self.refresh()
        full_system = self._build_system_instruction(system_instruction, is_structured=True)
        attempt_system = full_system

        for attempt in range(2):
            try:
                response = self.provider.structured_output(prompt, schema, attempt_system)

                usage = self.provider.get_token_usage()
                self.logger.log_usage(self.model_id, usage["input"], usage["output"])

                return response
            except Exception as error:
                if attempt == 0 and not _is_retryable_error(error):
                    attempt_system = (
                        f"{full_system}\n\n"
                        f"Previous structured response failed with error: {error}. "
                        f"Return only valid JSON matching the requested schema and no extra text."
                    )
                    continue
                raise
