"""Structured findings schema + controlled taxonomy.

A "finding" is one audit observation, normalised into fields we can COUNT across
reports. The enums (theme, risk area, severity) are a controlled vocabulary: by
forcing the LLM to pick from a fixed list, "Access Control" and "user access
management" collapse into the same bucket, which is what makes cross-report
aggregation (recurring themes, common weaknesses) reliable. The trade-off is some
loss of nuance — captured in the free-text fields (title, weakness, observation).
"""

from enum import Enum

from pydantic import BaseModel, Field


class ControlTheme(str, Enum):
    ACCESS_CONTROL = "Access Control"
    CHANGE_MANAGEMENT = "Change Management"
    VULNERABILITY_PATCH = "Vulnerability & Patch Management"
    BACKUP_RECOVERY = "Backup & Recovery"
    LOGGING_MONITORING = "Logging & Monitoring"
    DATA_GOVERNANCE = "Data Governance & Privacy"
    THIRD_PARTY = "Third-Party / Vendor Management"
    IT_GOVERNANCE = "IT Governance & Policy"
    PROCUREMENT = "Procurement & Contract Management"
    FINANCIAL_CONTROLS = "Financial Controls"
    GRANTS_MANAGEMENT = "Grants Management"
    PHYSICAL_SECURITY = "Physical & Environmental Security"
    OTHER = "Other"


class RiskArea(str, Enum):
    CYBERSECURITY = "Cybersecurity"
    DATA_PROTECTION = "Data Protection"
    SYSTEM_AVAILABILITY = "System Availability & Resilience"
    FINANCIAL_LOSS = "Financial Loss / Value for Money"
    COMPLIANCE = "Regulatory & Policy Compliance"
    OPERATIONAL = "Operational Effectiveness"
    FRAUD = "Fraud & Integrity"
    OTHER = "Other"


class Severity(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Finding(BaseModel):
    title: str = Field(description="Short title of the observation (<= 12 words)")
    theme: ControlTheme = Field(description="The control theme this finding belongs to")
    risk_area: RiskArea = Field(description="The primary technology/risk area")
    severity: Severity = Field(description="Assessed severity")
    weakness: str = Field(description="The specific control weakness, one sentence")
    observation: str = Field(description="What was observed, 1-3 sentences, factual")
    agencies: list[str] = Field(
        default_factory=list,
        description="Agencies, ministries, or systems named in this finding",
    )
    recommendation: str = Field(
        default="", description="Recommended remediation, if stated"
    )


class ExtractionResult(BaseModel):
    """Container so the LLM returns one object whose `findings` is the list."""

    findings: list[Finding] = Field(default_factory=list)
