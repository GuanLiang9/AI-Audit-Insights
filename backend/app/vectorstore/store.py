"""ChromaDB persistent vector store.

Chroma keeps the vectors + their source text + metadata on disk and answers
nearest-neighbour queries. We supply our own embeddings (from embeddings.py) so
Chroma never calls an external embedding API.
"""

from functools import lru_cache

import chromadb

from ..config import get_settings


@lru_cache
def _collection():
    s = get_settings()
    client = chromadb.PersistentClient(path=s.chroma_dir)
    # hnsw:space=cosine matches our normalized embeddings.
    return client.get_or_create_collection(
        s.chroma_collection, metadata={"hnsw:space": "cosine"}
    )


def add_chunks(
    report_id: str, filename: str, chunks: list[str], embeddings: list[list[float]]
) -> None:
    """Store every chunk of a report with a stable, unique id."""
    ids = [f"{report_id}:{i}" for i in range(len(chunks))]
    metadatas = [
        {"report_id": report_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    _collection().add(
        ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas
    )


def query(embedding: list[float], n_results: int = 5) -> dict:
    """Return the n most similar chunks to a query embedding (used by Day-2 Q&A)."""
    return _collection().query(query_embeddings=[embedding], n_results=n_results)
