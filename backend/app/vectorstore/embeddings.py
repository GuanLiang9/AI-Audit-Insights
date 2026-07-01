"""Local text embeddings via sentence-transformers.

An embedding turns text into a fixed-length vector (all-MiniLM-L6-v2 → 384 numbers)
where semantically similar text lands close together. Running it locally means no
API cost, no rate limits, and the data never leaves the machine.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from ..config import get_settings


@lru_cache
def _model() -> SentenceTransformer:
    # Loaded once and cached. First call downloads the weights (~80 MB) and caches
    # them under the HuggingFace cache dir; later calls are instant.
    return SentenceTransformer(get_settings().embedding_model)


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of strings into a list of vectors.

    normalize_embeddings=True scales each vector to unit length, so cosine
    similarity (what the vector store uses) behaves correctly.
    """
    vectors = _model().encode(texts, normalize_embeddings=True)
    return vectors.tolist()
