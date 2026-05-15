import json
from typing import List, Dict, Any, Optional, Iterator
from .base import LLMProvider

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    anthropic = None  # type: ignore
    _HAS_ANTHROPIC = False

class AnthropicProvider(LLMProvider):
    """
    Native implementation for Anthropic using the official SDK.
    Preserves full turn sequence, normalizes roles for compatibility,
    and safely handles SDK variations by falling back to plain payload dicts.
    """
    def __init__(self, model_id: str, api_key: str):
        if not _HAS_ANTHROPIC:
            raise RuntimeError("Anthropic SDK not available. Install the 'anthropic' package to use AnthropicProvider.")
        self.model_id = model_id
        self.client = anthropic.Anthropic(api_key=api_key)
        self.last_usage = {"input": 0, "output": 0}

    def _build_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Normalize roles and build message list for Anthropic API.
        Filters system messages (Anthropic uses system_instruction instead).
        Normalizes user → "user", assistant → "assistant".
        Falls back to plain dict if SDK classes change.
        """
        normalized_messages = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                # Anthropic uses dedicated system_instruction; skip system messages in content
                continue

            # Normalize role for Anthropic (user and assistant are standard)
            normalized_role = "user" if role == "user" else "assistant"
            normalized_messages.append({"role": normalized_role, "content": content})

        return normalized_messages

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        # Normalize messages and preserve full turn sequence
        normalized_messages = self._build_messages(messages)
        response = self.client.messages.create(
            model=self.model_id,
            system=system_instruction,
            messages=normalized_messages,
            max_tokens=4096,
            temperature=0.0
        )
        
        self.last_usage = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
        return response.content[0].text

    def stream_chat(self, messages: List[Dict[str, str]], system_instruction: str) -> Iterator[str]:
        # Normalize messages and preserve full turn sequence
        normalized_messages = self._build_messages(messages)
        stream_factory = getattr(self.client.messages, "stream", None)
        if not callable(stream_factory):
            yield self.chat(messages, system_instruction)
            return

        with stream_factory(
            model=self.model_id,
            system=system_instruction,
            messages=normalized_messages,
            max_tokens=4096,
            temperature=0.0,
        ) as stream:
            text_stream = getattr(stream, "text_stream", None)
            if text_stream is not None:
                for text in text_stream:
                    if text:
                        yield text
            else:
                for event in stream:
                    text = getattr(event, "text", None)
                    if text:
                        yield text

        self.last_usage = {"input": 0, "output": 0}

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        # Anthropic uses tool-use or forced instruction for JSON
        schema_json = schema.model_json_schema() if hasattr(schema, 'model_json_schema') else {}
        instruction = f"{system_instruction}\n\nOUTPUT CONTRACT: You MUST return a single valid JSON object matching this schema: {json.dumps(schema_json)}"
        
        for attempt in range(2):
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
                if attempt == 0:
                    prompt += f"\n\nPrevious attempt failed to parse as JSON with error: {e}. Please correct the formatting and ensure you output ONLY valid JSON matching the schema."
                    continue
                raise ValueError(f"[Anthropic] Structured Output Failure: {e}\nRaw: {response_text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
