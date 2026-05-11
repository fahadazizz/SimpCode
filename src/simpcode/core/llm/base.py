from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    Ensures a consistent interface for the SimpCode orchestration layer.
    """
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        """
        Performs a standard chat completion.
        Returns the text content of the response.
        """
        pass

    @abstractmethod
    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        """
        Performs a completion that is guaranteed to follow a specific JSON schema.
        Returns the parsed data (usually a Pydantic model instance).
        """
        pass

    @abstractmethod
    def get_token_usage(self) -> Dict[str, int]:
        """
        Returns the token usage of the last request.
        """
        pass
