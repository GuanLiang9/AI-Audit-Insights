"""LLM provider interface.

Business logic depends on this abstract contract, never on a concrete SDK. Swapping
Gemini for Claude/OpenAI means adding one subclass and changing one config value.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Return the model's text response for a single-turn prompt.

        `system` is an optional instruction describing the model's role/output rules.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        *,
        schema: type[BaseModel],
        system: str | None = None,
        max_output_tokens: int = 8192,
    ) -> Any:
        """Return a validated instance of `schema`.

        Providers use their native structured-output feature (Gemini: response_schema;
        OpenAI/Anthropic: JSON mode / tool calling). The model is forced to emit JSON
        matching the schema, so callers get typed data instead of free text to parse.
        """
        raise NotImplementedError
