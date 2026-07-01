"""Extract structured findings from one report's text via the LLM (JSON mode)."""

from ..llm.factory import get_llm
from ..models.findings import ExtractionResult, Finding

_SYSTEM = (
    "You are a senior IT auditor extracting structured findings from a government "
    "audit report. Extract only findings supported by the text. Map each finding to "
    "the closest theme and risk area from the provided enums. Be precise and factual; "
    "never invent agencies or numbers."
)

_PROMPT = """Extract the most significant audit findings from the report below.
Return up to {max_findings} findings, prioritising IT controls, technology risk, and
control weaknesses. For each finding, name the specific agencies/systems involved.

REPORT TEXT:
\"\"\"
{text}
\"\"\""""

# Long-context model handles the whole report; cap defends against pathological sizes
# and keeps us within the free-tier token budget.
_MAX_CHARS = 200_000
_MAX_FINDINGS = 25


def extract_findings(full_text: str) -> list[Finding]:
    llm = get_llm()
    result = llm.generate_structured(
        _PROMPT.format(text=full_text[:_MAX_CHARS], max_findings=_MAX_FINDINGS),
        schema=ExtractionResult,
        system=_SYSTEM,
        max_output_tokens=16384,
    )
    # Provider returns an ExtractionResult (or dict-like) — normalise to a list.
    if isinstance(result, ExtractionResult):
        return result.findings
    return ExtractionResult.model_validate(result).findings
