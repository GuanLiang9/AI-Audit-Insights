"""Retrieval-Augmented Generation Q&A over the indexed report chunks.

Flow: embed the question with the SAME model used for indexing -> find the nearest
chunks in ChromaDB -> hand those chunks to the LLM as the only allowed context ->
answer with [n] citations. This is the right tool for open-ended questions; it is
NOT used for corpus-wide counting (that's the aggregation engine).
"""

from ..llm.factory import get_llm
from ..vectorstore.embeddings import embed
from ..vectorstore.store import query

_SYSTEM = (
    "You answer questions about government audit reports using ONLY the provided "
    "context. Cite sources inline as [1], [2]. If the context does not contain the "
    "answer, say so plainly. Do not use outside knowledge. Write in plain prose; if you "
    "list items, start each line with '- '. Do not use markdown bold, asterisks, or headers."
)


def answer_question(question: str, k: int = 6) -> dict:
    question = question.strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": []}

    result = query(embed([question])[0], n_results=k)
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "No reports have been indexed yet, so there is nothing to search.",
            "sources": [],
        }

    blocks, sources = [], []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        label = f"{meta.get('filename', '?')} (chunk {meta.get('chunk_index', '?')})"
        blocks.append(f"[{i}] {label}\n{doc}")
        sources.append(
            {
                "id": i,
                "filename": meta.get("filename", "?"),
                "chunk_index": meta.get("chunk_index"),
            }
        )

    prompt = (
        f"CONTEXT:\n{chr(10).join(blocks)}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer with inline [n] citations."
    )
    return {"answer": get_llm().generate(prompt, system=_SYSTEM), "sources": sources}
