"""SQLite persistence for report metadata, extracted text, and cached analysis.

We open a fresh connection per call. SQLite connections are not safe to share
across threads, and FastAPI handles requests on a thread pool — a connection per
operation is the simplest correct approach at this scale.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone

from ..config import get_settings


def _connect() -> sqlite3.Connection:
    path = get_settings().db_path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts (row["filename"])
    return conn


def init_db() -> None:
    """Create tables if they don't exist (called on startup)."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id          TEXT PRIMARY KEY,
                filename    TEXT NOT NULL,
                pages       INTEGER NOT NULL,
                chunks      INTEGER NOT NULL,
                created_at  TEXT NOT NULL,
                full_text   TEXT NOT NULL,
                analysis    TEXT            -- JSON string, NULL until analysed
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id       TEXT NOT NULL,
                title           TEXT NOT NULL,
                theme           TEXT NOT NULL,
                risk_area       TEXT NOT NULL,
                severity        TEXT NOT NULL,
                weakness        TEXT NOT NULL,
                observation     TEXT NOT NULL,
                agencies        TEXT NOT NULL,   -- JSON array
                recommendation  TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
            """
        )


def insert_report(
    report_id: str, filename: str, pages: int, chunks: int, full_text: str
) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO reports (id, filename, pages, chunks, created_at, full_text) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                report_id,
                filename,
                pages,
                chunks,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                full_text,
            ),
        )


def get_report(report_id: str) -> sqlite3.Row | None:
    with _connect() as conn:
        cur = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        return cur.fetchone()


def list_reports() -> list[dict]:
    """Lightweight list for the UI — excludes the heavy full_text column."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, filename, pages, chunks, created_at, "
            "(analysis IS NOT NULL) AS analyzed "
            "FROM reports ORDER BY created_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]


def save_analysis(report_id: str, analysis: dict) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE reports SET analysis = ? WHERE id = ?",
            (json.dumps(analysis), report_id),
        )


# --- Findings ---------------------------------------------------------------


def replace_findings(report_id: str, findings: list) -> None:
    """Store a report's findings, replacing any previous ones (idempotent re-extract).

    `findings` is a list of Finding pydantic models.
    """
    with _connect() as conn:
        conn.execute("DELETE FROM findings WHERE report_id = ?", (report_id,))
        conn.executemany(
            "INSERT INTO findings "
            "(report_id, title, theme, risk_area, severity, weakness, observation, "
            " agencies, recommendation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    report_id,
                    f.title,
                    f.theme.value,
                    f.risk_area.value,
                    f.severity.value,
                    f.weakness,
                    f.observation,
                    json.dumps(f.agencies),
                    f.recommendation,
                )
                for f in findings
            ],
        )


def list_findings() -> list[dict]:
    """All findings joined with their report filename; agencies decoded to a list."""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT f.*, r.filename FROM findings f "
            "JOIN reports r ON r.id = f.report_id "
            "ORDER BY f.report_id"
        )
        rows = [dict(row) for row in cur.fetchall()]
    for row in rows:
        row["agencies"] = json.loads(row["agencies"])
    return rows


def report_has_findings(report_id: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "SELECT 1 FROM findings WHERE report_id = ? LIMIT 1", (report_id,)
        )
        return cur.fetchone() is not None
