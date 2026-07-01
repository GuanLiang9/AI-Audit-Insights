"""Google Gemini implementation of the LLMProvider contract.

Uses the current unified `google-genai` SDK (the older `google-generativeai`
package is deprecated).
"""

import json
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel

from .base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        # The Client holds the API key and talks to the Gemini Developer API.
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        config = (
            types.GenerateContentConfig(system_instruction=system) if system else None
        )
        response = self._client.models.generate_content(
            model=self._model, contents=prompt, config=config
        )
        # .text concatenates the text parts of the response.
        return response.text

    def generate_structured(
        self,
        prompt: str,
        *,
        schema: type[BaseModel],
        system: str | None = None,
        max_output_tokens: int = 16384,
    ) -> Any:
        # response_mime_type + response_schema put Gemini in constrained-decoding mode:
        # the model can only emit tokens that keep the output valid against the schema.
        # thinking_budget=0 disables 2.5-flash's internal reasoning tokens, which would
        # otherwise consume the output budget and truncate the JSON.
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=schema,
            max_output_tokens=max_output_tokens,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        response = self._client.models.generate_content(
            model=self._model, contents=prompt, config=config
        )
        # The SDK parses the JSON into a `schema` instance on .parsed; fall back to
        # manual parse if that's unavailable.
        if getattr(response, "parsed", None) is not None:
            return response.parsed
        return schema.model_validate(json.loads(response.text))
