"""Provider selection. Callers ask for *an* LLM, not a specific vendor."""

from functools import lru_cache

from ..config import get_settings
from .base import LLMProvider
from .gemini import GeminiProvider


@lru_cache
def get_llm() -> LLMProvider:
    """Build (once) and return the configured LLM provider."""
    settings = get_settings()
    if settings.llm_provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.llm_model)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}")
