import json
from typing import List, Dict, Any, Optional
from .base import LLMProvider
from google import genai
from google.genai import types

class GoogleProvider(LLMProvider):
    """
    Native implementation for Google Gemini using the official SDK.
    """
    def __init__(self, model_id: str, api_key: str):
        self.model_id = model_id
        self.client = genai.Client(api_key=api_key)
        self.last_usage = {"input": 0, "output": 0}

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        # Convert to Gemini format
        # Gemini handles history better via Chat session
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=messages[-1]["content"], # Simplified for stateless chat()
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        
        self.last_usage = {
            "input": response.usage_metadata.prompt_token_count,
            "output": response.usage_metadata.candidates_token_count
        }
        return response.text

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        # Gemini has native JSON schema support
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0
            )
        )
        
        self.last_usage = {
            "input": response.usage_metadata.prompt_token_count,
            "output": response.usage_metadata.candidates_token_count
        }
        
        try:
            return json.loads(response.text)
        except Exception as e:
            raise ValueError(f"[Google] Structured Output Failure: {e}\nRaw: {response.text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
