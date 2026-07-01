"""Pydantic response models — the typed shapes the API returns to the frontend."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    report_id: str
    filename: str
    pages: int
    chunks: int
    preview: str  # first ~500 chars of extracted text


class ReportSummary(BaseModel):
    id: str
    filename: str
    pages: int
    chunks: int
    created_at: str
    analyzed: bool


class AnalysisResult(BaseModel):
    summary: str
    key_observations: list[str]
    risk_areas: list[str]


class ExtractResponse(BaseModel):
    report_id: str
    findings_count: int


class FindingOut(BaseModel):
    report_id: str
    filename: str
    title: str
    theme: str
    risk_area: str
    severity: str
    weakness: str
    observation: str
    agencies: list[str]
    recommendation: str = ""


class ExecutiveSummaryOut(BaseModel):
    executive_summary: str
    key_insights: list[str]


class QARequest(BaseModel):
    question: str


class Source(BaseModel):
    id: int
    filename: str
    chunk_index: int | None = None


class QAResponse(BaseModel):
    answer: str
    sources: list[Source]
