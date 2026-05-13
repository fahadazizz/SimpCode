import json
from typing import List, Dict, Any, Optional
from .base import LLMProvider
import anthropic

class AnthropicProvider(LLMProvider):
    """
    Native implementation for Anthropic using the official SDK.
    """
    def __init__(self, model_id: str, api_key: str):
        self.model_id = model_id
        self.client = anthropic.Anthropic(api_key=api_key)
        self.last_usage = {"input": 0, "output": 0}

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        # Convert messages to Anthropic format (ensure they start with 'user')
        response = self.client.messages.create(
            model=self.model_id,
            system=system_instruction,
            messages=messages,
            max_tokens=4096,
            temperature=0.0
        )
        
        self.last_usage = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
        return response.content[0].text

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        # Anthropic uses tool-use or forced instruction for JSON
        schema_json = schema.model_json_schema() if hasattr(schema, 'model_json_schema') else {}
        instruction = f"{system_instruction}\n\nOUTPUT CONTRACT: You MUST return a single valid JSON object matching this schema: {json.dumps(schema_json)}"
        
        response_text = self.chat([{"role": "user", "content": prompt}], instruction)
        
        try:
            cleaned = response_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            decoder = json.JSONDecoder()
            json_start = cleaned.find("{")
            if json_start >= 0:
                data, _ = decoder.raw_decode(cleaned[json_start:])
            else:
                data = json.loads(cleaned)
            return schema(**data) if schema else data
        except Exception as e:
            raise ValueError(f"[Anthropic] Structured Output Failure: {e}\nRaw: {response_text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
