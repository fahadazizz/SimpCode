import json
from typing import List, Dict, Any, Optional, Iterator
from .base import LLMProvider

try:
    from google import genai  # type: ignore
    from google.genai import types  # type: ignore
    _HAS_GOOGLE = True
except Exception:  # ImportError or namespace issues
    genai = None  # type: ignore
    types = None  # type: ignore
    _HAS_GOOGLE = False

class GoogleProvider(LLMProvider):
    """
    Native implementation for Google Gemini using the official SDK.
    """
    def __init__(self, model_id: str, api_key: str):
        if not _HAS_GOOGLE:
            raise RuntimeError("Google GenAI SDK not available. Install the 'google-genai' SDK to use GoogleProvider.")
        self.model_id = model_id
        self.client = genai.Client(api_key=api_key)
        self.last_usage = {"input": 0, "output": 0}

    def _build_contents(self, messages: List[Dict[str, str]]) -> List[Any]:
        gemini_contents = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                # Gemini uses a dedicated system_instruction field; do not drop it silently.
                continue

            gemini_role = "user" if role == "user" else "model"
            content_type = getattr(types, "Content", None)
            part_type = getattr(types, "Part", None)

            if content_type is not None and part_type is not None and hasattr(part_type, "from_text"):
                gemini_contents.append(
                    content_type(role=gemini_role, parts=[part_type.from_text(text=content)])
                )
            else:
                gemini_contents.append({"role": gemini_role, "parts": [{"text": content}]})

        return gemini_contents

    def chat(self, messages: List[Dict[str, str]], system_instruction: str) -> str:
        gemini_contents = self._build_contents(messages)
            
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=gemini_contents,
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

    def stream_chat(self, messages: List[Dict[str, str]], system_instruction: str) -> Iterator[str]:
        gemini_contents = self._build_contents(messages)

        stream_method = getattr(self.client.models, "generate_content_stream", None)
        if not callable(stream_method):
            stream_method = getattr(self.client.models, "stream_generate_content", None)

        if not callable(stream_method):
            yield self.chat(messages, system_instruction)
            return

        stream = stream_method(
            model=self.model_id,
            contents=gemini_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            ),
        )

        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

        self.last_usage = {"input": 0, "output": 0}

    def structured_output(self, prompt: str, schema: Any, system_instruction: str) -> Any:
        # Gemini has native JSON schema support
        for attempt in range(2):
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
                data = json.loads(response.text)
                return schema(**data) if schema else data
            except Exception as e:
                if attempt == 0:
                    prompt += f"\n\nPrevious attempt failed with error: {e}. Ensure the response strictly follows the schema."
                    continue
                raise ValueError(f"[Google] Structured Output Failure: {e}\nRaw: {response.text}")

    def get_token_usage(self) -> Dict[str, int]:
        return self.last_usage
