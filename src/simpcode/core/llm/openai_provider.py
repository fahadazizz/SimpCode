import json
import httpx
from typing import List, Dict, Any, Optional
from .base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    """
    Base implementation for OpenAI-compatible APIs (OpenAI, Groq, OpenRouter, Ollama).
    """
    def __init__(self, model_id: str, api_key: str, base_url: str, provider_name: str = "openai"):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = provider_name
        self.last_usage = {"input": 0, "output": 0}

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        payload_messages = [{"role": "system", "content": system_instruction}]
        payload_messages.extend(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenRouter specific headers
        if self.provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://simpcode.ai"
            headers["X-Title"] = "SimpCode"

        payload = {
            "model": self.model_id,
            "messages": payload_messages,
            "temperature": 0.0
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if response.status_code != 200:
                raise ValueError(f"[{self.provider_name}] Error {response.status_code}: {response.text}")
            
            data = response.json()
            usage = data.get("usage", {})
            self.last_usage = {
                "input": usage.get("prompt_tokens", 0),
                "output": usage.get("completion_tokens", 0)
            }
            return data["choices"][0]["message"]["content"]

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        import re
        # Most compatible approach: append schema to instruction
        schema_json = schema.model_json_schema() if hasattr(schema, 'model_json_schema') else {}
        instruction = f"{system_instruction}\n\nOUTPUT CONTRACT: You MUST return a single valid JSON object matching this schema: {json.dumps(schema_json)}"
        
        response_text = self.chat([{"role": "user", "content": prompt}], instruction)
        
        try:
            cleaned = response_text.strip()
            # Attempt to extract JSON broadly using regex to ignore any conversational padding.
            match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(1)
            
            data = json.loads(cleaned)
            return schema(**data) if schema else data
        except Exception as e:
            raise ValueError(f"[{self.provider_name}] Structured Output Failure: {e}\nRaw: {response_text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
