import json
import httpx
from typing import List, Dict, Any, Optional, Iterator
from .base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    """
    Base implementation for OpenAI-compatible APIs (OpenAI, Groq, OpenRouter, Ollama).
    Preserves full turn sequence, normalizes roles for compatibility,
    and safely builds messages with proper system instruction handling.
    """
    def __init__(self, model_id: str, api_key: str, base_url: str, provider_name: str = "openai"):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = provider_name
        self.last_usage = {"input": 0, "output": 0}

    def _build_messages(self, messages: List[Dict[str, str]], system_instruction: str) -> List[Dict[str, str]]:
        """
        Normalize roles and build message list for OpenAI-compatible API.
        Ensures system instruction is first message with role "system".
        Normalizes user → "user", assistant → "model" or "assistant" depending on context.
        Filters out any existing system messages and replaces with provided system_instruction.
        Preserves full turn sequence.
        """
        normalized_messages = [{"role": "system", "content": system_instruction}]
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                # Skip system messages; use system_instruction instead
                continue

            # Normalize role for OpenAI-compatible APIs (user and assistant are standard)
            normalized_role = "user" if role == "user" else "assistant"
            normalized_messages.append({"role": normalized_role, "content": content})

        return normalized_messages

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        # Normalize messages with proper role handling and ensure system instruction is first
        payload_messages = self._build_messages(messages, system_instruction)
        
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

    def stream_chat(self, messages: List[Dict[str, str]], system_instruction: str) -> Iterator[str]:
        # Normalize messages with proper role handling and ensure system instruction is first
        payload_messages = self._build_messages(messages, system_instruction)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://simpcode.ai"
            headers["X-Title"] = "SimpCode"

        payload = {
            "model": self.model_id,
            "messages": payload_messages,
            "temperature": 0.0,
            "stream": True,
        }

        collected = []
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    raise ValueError(f"[{self.provider_name}] Error {response.status_code}: {response.text}")

                for raw_line in response.iter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.decode() if isinstance(raw_line, bytes) else raw_line
                    if not line.startswith("data:"):
                        continue

                    data_line = line[len("data:"):].strip()
                    if data_line == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data_line)
                    except Exception:
                        continue

                    choices = chunk.get("choices", [])
                    if not choices:
                        continue

                    delta = choices[0].get("delta", {})
                    text = delta.get("content")
                    if text:
                        collected.append(text)
                        yield text

        self.last_usage = {"input": 0, "output": 0}

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        # Most compatible approach: append schema to instruction
        schema_json = schema.model_json_schema() if hasattr(schema, 'model_json_schema') else {}
        instruction = f"{system_instruction}\n\nOUTPUT CONTRACT: You MUST return a single valid JSON object matching this schema: {json.dumps(schema_json)}"
        
        for attempt in range(2):
            response_text = self.chat([{"role": "user", "content": prompt}], instruction)
            
            try:
                cleaned = response_text.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

                decoder = json.JSONDecoder()
                json_start = cleaned.find("{")
                if json_start >= 0:
                    data, _ = decoder.raw_decode(cleaned[json_start:])
                else:
                    data = json.loads(cleaned)
                return schema(**data) if schema else data
            except Exception as e:
                if attempt == 0:
                    prompt += f"\n\nPrevious attempt failed to parse as JSON with error: {e}. Please correct the formatting and ensure you output ONLY valid JSON matching the schema."
                    continue
                raise ValueError(f"[{self.provider_name}] Structured Output Failure: {e}\nRaw: {response_text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
