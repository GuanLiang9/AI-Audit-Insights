"""Basic per-report AI analysis (Day 1).

Sends an excerpt of the report to the LLM and asks for a structured JSON summary.
Day 2 replaces this with full structured-findings extraction + cross-report
aggregation; this is the minimal "it thinks about the document" pass.
"""

import json

from ..llm.factory import get_llm

_SYSTEM = (
    "You are a senior IT auditor. You analyse government audit reports precisely and "
    "factually. You never invent findings that are not supported by the text."
)

_PROMPT = """Analyse the audit report below and respond with ONLY a JSON object of this shape:
{{
  "summary": "<3-4 sentence executive summary>",
  "key_observations": ["<concise observation>", ...],
  "risk_areas": ["<technology or control risk area>", ...]
}}
Use 3-7 key_observations and up to 5 risk_areas. Do not wrap the JSON in markdown.

REPORT:
\"\"\"
{text}
\"\"\""""

# Cap input so we stay well within the model context window and the free quota.
_MAX_CHARS = 15000


def analyze_report(full_text: str) -> dict:
    llm = get_llm()
    raw = llm.generate(_PROMPT.format(text=full_text[:_MAX_CHARS]), system=_SYSTEM)
    return _parse_json(raw)


def _parse_json(raw: str) -> dict:
    """Tolerantly extract the JSON object from the model's reply.

    LLMs sometimes wrap JSON in ```json fences or add stray prose, so we slice
    from the first '{' to the last '}' before parsing.
    """
    text = raw.strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Never crash the request on a malformed reply — degrade gracefully.
        return {"summary": raw.strip(), "key_observations": [], "risk_areas": []}

    return {
        "summary": str(data.get("summary", "")).strip(),
        "key_observations": [str(x) for x in data.get("key_observations", [])],
        "risk_areas": [str(x) for x in data.get("risk_areas", [])],
    }
