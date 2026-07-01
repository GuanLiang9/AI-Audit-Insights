"""LLM executive summary over the aggregated insights.

The LLM's job here is synthesis, not arithmetic: it receives the already-computed
counts plus a grounded sample of findings and writes an auditor-style narrative.
Keeping the counting in code and the prose in the LLM plays to each one's strength.
"""

from pydantic import BaseModel, Field

from ..llm.factory import get_llm
from ..storage import db

_SYSTEM = (
    "You are the lead author of an Auditor-General-style executive summary. Write "
    "concise, factual, board-level prose grounded ONLY in the supplied data."
)


class ExecutiveSummary(BaseModel):
    executive_summary: str = Field(description="2-3 paragraph executive summary")
    key_insights: list[str] = Field(description="5-8 sharp, specific insights")


def _format_brief(insights: dict) -> str:
    lines = [
        f"Reports analysed: {insights['total_reports']}",
        f"Total findings: {insights['total_findings']}",
        "",
        "Recurring control themes (theme | findings | reports):",
    ]
    for t in insights["themes"][:10]:
        lines.append(f"- {t['name']} | {t['count']} | {t['report_count']}")
    lines.append("\nTechnology risk areas (area | findings):")
    for r in insights["risk_areas"]:
        lines.append(f"- {r['name']} | {r['count']}")
    lines.append("\nSeverity mix:")
    for s in insights["severities"]:
        lines.append(f"- {s['name']}: {s['count']}")
    lines.append("\nMost frequently named agencies/systems:")
    for a in insights["agencies"][:10]:
        lines.append(f"- {a['name']} ({a['count']})")

    # Ground the prose with concrete high-severity examples.
    findings = db.list_findings()
    high = [f for f in findings if f["severity"] == "High"][:15]
    lines.append("\nSample high-severity findings (title — weakness):")
    for f in high:
        lines.append(f"- {f['title']} — {f['weakness']}")

    return "\n".join(lines)


def generate_executive_summary(insights: dict) -> dict:
    llm = get_llm()
    prompt = (
        "Write an executive summary of these aggregated audit insights, then list the "
        "key insights.\n\n" + _format_brief(insights)
    )
    result = llm.generate_structured(
        prompt, schema=ExecutiveSummary, system=_SYSTEM, max_output_tokens=2048
    )
    if isinstance(result, ExecutiveSummary):
        return result.model_dump()
    return ExecutiveSummary.model_validate(result).model_dump()
