"""Typed application configuration.

All settings are loaded once from environment variables (and a local `.env` file),
validated by Pydantic, and cached. Required values with no default cause a clear
startup error instead of the app silently running with `None`.
"""

from functools import lru_cache

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads from process env first, then a local .env file. Field names map to
    # UPPER_CASE env vars case-insensitively (gemini_api_key <- GEMINI_API_KEY).
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # --- LLM provider ---
    llm_provider: str = "gemini"
    gemini_api_key: str  # required: no default -> missing key fails fast at startup
    llm_model: str = "gemini-2.5-flash"

    # --- Embeddings + vector store ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_dir: str = "./data/chroma"
    chroma_collection: str = "audit_chunks"

    # --- Local storage ---
    db_path: str = "./data/app.db"
    upload_dir: str = "./data/uploads"

    # --- Ingestion (chunking) ---
    chunk_size: int = 1000      # characters per chunk
    chunk_overlap: int = 150    # characters shared between adjacent chunks

    # --- API ---
    cors_origins: list[str] = ["http://localhost:5173"]  # Vite dev server


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings, or raise a readable error if config is missing."""
    try:
        return Settings()
    except ValidationError as exc:
        missing = [str(e["loc"][0]) for e in exc.errors() if e["type"] == "missing"]
        raise RuntimeError(
            f"Missing required configuration: {', '.join(missing) or 'see below'}.\n"
            "Copy backend/.env.example to backend/.env and fill in the values.\n"
            f"{exc}"
        ) from exc
