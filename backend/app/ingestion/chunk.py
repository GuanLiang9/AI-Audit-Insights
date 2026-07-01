"""Split long report text into overlapping chunks.

Why chunk? Embedding models have a fixed input window and produce ONE vector per
input, so a whole report would collapse into a single blurry vector. Splitting into
~1k-char passages gives many focused vectors, which makes later semantic search
precise. The overlap keeps sentences that straddle a boundary retrievable from both
neighbouring chunks.
"""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []

    step = max(1, chunk_size - overlap)  # how far the window advances each step
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks
