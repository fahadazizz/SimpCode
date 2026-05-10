import os
import json
import httpx
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from simpcode.core.state import TokenLogger

class LLMClient:
    def __init__(self, provider: str = "groq", model_id: str = "llama-3.3-70b-versatile"):
        self.provider = provider
        self.model_id = model_id
        self.logger = TokenLogger()
        
        if provider == "groq":
            self.api_key = os.getenv("GROQ_API_KEY")
            self.base_url = "https://api.groq.com/openai/v1"
        elif provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = "https://openrouter.ai/api/v1"
        else:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"

        if not self.api_key:
            raise ValueError(f"No API key found for {provider}. Set GROQ_API_KEY, OPENROUTER_API_KEY, or GOOGLE_API_KEY.")

    def chat(self, messages: List[Dict[str, str]], system_instruction: Optional[str] = None) -> str:
        payload_messages = []
        if system_instruction:
            payload_messages.append({"role": "system", "content": system_instruction})
        payload_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://simpcode.ai"
            headers["X-Title"] = "SimpCode"

        payload = {
            "model": self.model_id,
            "messages": payload_messages
        }

        max_retries = 3
        for attempt in range(max_retries):
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 429:
                    # Rate limited - exponential backoff
                    wait_time = 5 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                
                if response.status_code != 200:
                    raise ValueError(f"LLM API Error ({response.status_code}): {response.text}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                usage = data.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                self.logger.log_usage(self.model_id, input_tokens, output_tokens)
                
                return content
        
        raise ValueError("Max retries exceeded for LLM API.")

    def structured_output(self, prompt: str, schema: Optional[Any], system_instruction: Optional[str] = None) -> Any:
        # Instruction to force JSON
        if schema:
            json_instruction = f"\nOutput ONLY a valid JSON object matching this schema: {schema.model_json_schema()}"
        else:
            json_instruction = "\nOutput ONLY a valid JSON object."
            
        full_system = (system_instruction or "") + json_instruction
        
        response_text = self.chat([{"role": "user", "content": prompt}], full_system)
        
        try:
            cleaned = response_text.strip()
            # Remove potential markdown formatting
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {response_text}")
