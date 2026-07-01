"""Cross-report aggregation — deterministic counting over stored findings.

No LLM here: once findings are structured, the insights auditors want ("which themes
recur", "which agencies appear most", "severity mix") are plain group-by counts.
Doing this in code (not via the LLM) makes the numbers exact, reproducible, and cheap.
"""

from collections import Counter

from ..storage import db


def _sorted_counts(counter: Counter) -> list[dict]:
    """Counter -> [{"name", "count"}] sorted by count desc, then name."""
    return [
        {"name": name, "count": count}
        for name, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def build_insights() -> dict:
    findings = db.list_findings()
    report_ids = {f["report_id"] for f in findings}

    theme_counter: Counter = Counter()
    theme_reports: dict[str, set] = {}
    risk_counter: Counter = Counter()
    severity_counter: Counter = Counter()
    agency_counter: Counter = Counter()

    for f in findings:
        theme_counter[f["theme"]] += 1
        theme_reports.setdefault(f["theme"], set()).add(f["report_id"])
        risk_counter[f["risk_area"]] += 1
        severity_counter[f["severity"]] += 1
        for agency in f["agencies"]:
            name = agency.strip()
            if name:
                agency_counter[name] += 1

    # Themes annotated with how many DISTINCT reports they appear in.
    themes = [
        {
            "name": name,
            "count": count,
            "report_count": len(theme_reports.get(name, set())),
        }
        for name, count in sorted(theme_counter.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    # "Recurring across reports" = a theme seen in more than one report.
    recurring_themes = [t for t in themes if t["report_count"] > 1]

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    severities = sorted(
        _sorted_counts(severity_counter),
        key=lambda s: severity_order.get(s["name"], 9),
    )

    return {
        "total_reports": len(report_ids),
        "total_findings": len(findings),
        "themes": themes,
        "recurring_themes": recurring_themes,
        "risk_areas": _sorted_counts(risk_counter),
        "severities": severities,
        "agencies": _sorted_counts(agency_counter)[:15],
    }
