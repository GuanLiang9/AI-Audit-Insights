"""HTTP routes: health, upload (ingest+embed+store), list, analyze."""

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..analysis.analyze import analyze_report
from ..config import get_settings
from ..extraction.extractor import extract_findings
from ..ingestion.chunk import chunk_text
from ..ingestion.pdf import extract_pages
from ..insights.aggregate import build_insights
from ..insights.summary import generate_executive_summary
from ..models.schemas import (
    AnalysisResult,
    ExecutiveSummaryOut,
    ExtractResponse,
    FindingOut,
    QARequest,
    QAResponse,
    ReportSummary,
    UploadResponse,
)
from ..qa.rag import answer_question
from ..storage import db
from ..vectorstore.embeddings import embed
from ..vectorstore.store import add_chunks

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Liveness probe + a peek at the active model configuration."""
    s = get_settings()
    return {
        "status": "ok",
        "llm_provider": s.llm_provider,
        "llm_model": s.llm_model,
        "embedding_model": s.embedding_model,
    }


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    """Ingest one PDF: extract text → chunk → embed → store in Chroma + SQLite."""
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    data = await file.read()
    try:
        pages = extract_pages(data)
    except Exception as exc:  # malformed/corrupt PDF
        raise HTTPException(400, f"Could not read PDF: {exc}") from exc

    full_text = "\n\n".join(p["text"] for p in pages)
    if not full_text.strip():
        raise HTTPException(422, "No extractable text found (scanned/image-only PDF?).")

    s = get_settings()
    chunks = chunk_text(full_text, s.chunk_size, s.chunk_overlap)
    add_chunks(
        report_id := uuid.uuid4().hex[:12],
        file.filename,
        chunks,
        embed(chunks),
    )
    db.insert_report(report_id, file.filename, len(pages), len(chunks), full_text)

    return UploadResponse(
        report_id=report_id,
        filename=file.filename,
        pages=len(pages),
        chunks=len(chunks),
        preview=full_text[:500],
    )


@router.get("/reports", response_model=list[ReportSummary])
def reports() -> list[ReportSummary]:
    """List uploaded reports (most recent first)."""
    return [ReportSummary(**r) for r in db.list_reports()]


@router.post("/analyze/{report_id}", response_model=AnalysisResult)
def analyze(report_id: str) -> AnalysisResult:
    """Run (and cache) the basic AI analysis for one report."""
    row = db.get_report(report_id)
    if row is None:
        raise HTTPException(404, "Report not found.")

    result = analyze_report(row["full_text"])
    db.save_analysis(report_id, result)
    return AnalysisResult(**result)


# --- Day 2: structured findings, cross-report insights, Q&A ------------------


@router.post("/extract/{report_id}", response_model=ExtractResponse)
def extract(report_id: str) -> ExtractResponse:
    """Extract structured findings for one report and store them."""
    row = db.get_report(report_id)
    if row is None:
        raise HTTPException(404, "Report not found.")

    findings = extract_findings(row["full_text"])
    db.replace_findings(report_id, findings)
    return ExtractResponse(report_id=report_id, findings_count=len(findings))


@router.post("/insights/build")
def insights_build() -> dict:
    """Extract findings for any not-yet-processed report, then return aggregation.

    One-click entry point for the dashboard: makes sure every report has findings
    before computing the corpus-wide insights.
    """
    reports = db.list_reports()
    if not reports:
        raise HTTPException(400, "No reports uploaded yet.")

    newly_processed = 0
    for r in reports:
        if not db.report_has_findings(r["id"]):
            row = db.get_report(r["id"])
            db.replace_findings(r["id"], extract_findings(row["full_text"]))
            newly_processed += 1

    return {"newly_processed": newly_processed, "insights": build_insights()}


@router.get("/insights")
def insights() -> dict:
    """Return the cross-report aggregation over already-extracted findings."""
    return build_insights()


@router.get("/findings", response_model=list[FindingOut])
def findings() -> list[FindingOut]:
    """All structured findings across all reports."""
    return [FindingOut(**f) for f in db.list_findings()]


@router.post("/insights/summary", response_model=ExecutiveSummaryOut)
def insights_summary() -> ExecutiveSummaryOut:
    """LLM executive summary synthesised from the aggregated insights."""
    data = build_insights()
    if data["total_findings"] == 0:
        raise HTTPException(400, "No findings yet. Build insights first.")
    return ExecutiveSummaryOut(**generate_executive_summary(data))


@router.post("/qa", response_model=QAResponse)
def qa(body: QARequest) -> QAResponse:
    """Answer a free-form question via RAG over the indexed chunks."""
    return QAResponse(**answer_question(body.question))
