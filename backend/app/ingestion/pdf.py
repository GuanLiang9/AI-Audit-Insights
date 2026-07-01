"""PDF text extraction with PyMuPDF (imported as `fitz`).

PyMuPDF parses the PDF's content streams and returns the text in natural reading
order per page — no OCR, so it only works on PDFs that contain a real text layer
(not scanned images).
"""

import fitz  # PyMuPDF


def extract_pages(data: bytes) -> list[dict]:
    """Return one dict per page: {"page": <1-based int>, "text": <str>}.

    Opens the PDF from an in-memory byte stream so we never touch disk.
    """
    pages: list[dict] = []
    # `with` ensures the document handle is released even if a page raises.
    with fitz.open(stream=data, filetype="pdf") as doc:
        for index, page in enumerate(doc, start=1):
            pages.append({"page": index, "text": page.get_text("text")})
    return pages
