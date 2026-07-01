# AI Audit Insights

An AI application that analyses **multiple government audit reports together** and surfaces
cross-report insight: recurring IT control themes, common control weaknesses, technology risk
areas, most-affected agencies, an executive summary, and a cited Q&A chat.

> Verified end-to-end on 4 real Auditor-General's Office (AGO) annual reports → **109 structured
> findings**, with *Procurement & Contract Management* recurring across **all four** reports.

![Insights dashboard](assets/screenshots/insights.png)

---

## Solution Approach

**The problem.** An auditor has many long audit reports and needs insight *across* the whole set —
recurring control themes, common weaknesses, most-affected agencies — not a summary of any single
report. That word "across" is the crux: the value is in aggregating over the corpus.

**The decomposition.** I split the problem into five independent stages:
**ingest** (PDF → text → chunks) → **understand** (LLM extracts structured findings) →
**store** (SQLite + vector index) → **aggregate** (count patterns across reports) →
**present** (dashboard + Q&A). Each stage is swappable without touching the others.

**The core idea.** There are two different kinds of questions, and using one tool for both is the
classic mistake:

| Question | Approach | Why |
|---|---|---|
| **"Which themes recur across all reports?"** (count / pattern) | **Structured extraction → aggregation in code** | Counting must see *every* finding, deterministically |
| **"What did they say about privileged accounts?"** (lookup) | **RAG** (vector retrieval → LLM) | Only a few relevant passages matter |

The LLM is used for what only it can do — **turning messy report prose into structured findings**
against a fixed taxonomy — and plain code does the **exact counting**. RAG is reserved for the
open-ended Q&A. A pure-RAG app cannot reliably answer "how often across all reports" questions,
because top-k retrieval only ever sees a handful of chunks.

---

## Features

- **Upload & index** audit PDFs → text extraction, chunking, local embeddings, vector store.
- **Cross-report insights** → recurring themes, technology risk areas, severity mix, most-affected
  agencies, and which themes recur across multiple reports.
- **Executive summary** → LLM narrative synthesised from the aggregated numbers.
- **Q&A chat (RAG)** → ask anything; answers are grounded in retrieved passages **with citations**.
- **Swappable LLM** → provider abstraction (Gemini today; another vendor is a one-file change).

| Reports | Q&A (RAG with citations) |
|---|---|
| ![Reports](assets/screenshots/reports.png) | ![Q&A](assets/screenshots/qa.png) |

---

## AI Approach

The design principle is **use the LLM only where it is uniquely strong, and use code where code is
better.** Three distinct AI roles:

1. **Structured extraction (LLM).** Each report's full text is sent to the LLM in
   **JSON/schema-constrained mode** (Gemini `response_schema`); the output is validated against a
   Pydantic model (`backend/app/models/findings.py`). Each finding is mapped onto a **fixed
   taxonomy** — `theme`, `risk_area`, `severity` are enums — so the same concept is always labelled
   the same way. This is what makes the findings *countable*.
2. **Deterministic aggregation (code, no LLM).** Recurring themes, severity mix, most-affected
   agencies, and "recurs across N reports" are plain group-by counts in
   `backend/app/insights/aggregate.py` — exact and reproducible. Counting is not an LLM job.
3. **Retrieval-Augmented Generation (LLM + vectors).** For open-ended questions, the query is
   embedded with the same local MiniLM model, ChromaDB returns the top-k nearest chunks, and the
   LLM answers **using only that context, with `[n]` citations** (`backend/app/qa/rag.py`).

The **executive summary** (`backend/app/insights/summary.py`) is an LLM *synthesis* of the
already-computed numbers plus a grounded sample of high-severity findings — narrative, not counting.

**Reliability / anti-hallucination:** schema-constrained decoding guarantees valid, on-taxonomy
output; system prompts instruct the model to extract only what the text supports; the Q&A path is
restricted to retrieved context and forced to cite sources.

**Model & abstraction:** Gemini 2.5 Flash (free tier, long context, native JSON mode) sits behind
an `LLMProvider` interface (`backend/app/llm/`) exposing `generate` and `generate_structured`, so
switching vendor is a one-file change. Internal "thinking" is disabled for structured calls to keep
the full token budget for the JSON output.

---

## Architecture

```
Browser (React + Tailwind + Recharts)
        │  /api  (Vite proxy)
        ▼
FastAPI
  Ingestion:  PDF → PyMuPDF → chunk → MiniLM embed → ChromaDB
  Extraction: full text → LLM (JSON mode) → Findings → SQLite
  Insights:   SQLite → aggregate (code) → counts → LLM exec summary
  Q&A:        question → embed → ChromaDB top-k → LLM answer + citations
  LLM behind a provider abstraction (Gemini, swappable)
        │                         │
        ▼                         ▼
   ChromaDB (vectors)      SQLite (reports + findings)
```

---

## Technology Stack

| Concern | Choice | Why |
|---|---|---|
| Backend | **FastAPI** | async, Pydantic validation, auto OpenAPI docs |
| Frontend | **React + Tailwind + Recharts** | responsive UI + charts |
| PDF parsing | **PyMuPDF** | fast, robust text extraction |
| Embeddings | **sentence-transformers MiniLM (local)** | free, no quota, data stays local |
| Vector DB | **ChromaDB** | zero-infra persistent vector store |
| Structured store | **SQLite** | exact aggregation, zero setup |
| LLM | **Gemini 2.5 Flash** (swappable) | free tier, long context, native JSON mode |

---

## Assumptions

- Input PDFs contain a real text layer (not scanned images) and are in English.
- Reports are AGO-style government audit reports; the finding taxonomy is tuned to that domain.
- The most significant ~25 findings per report are sufficient for insight (extraction cap).
- A whole report fits the model's context window; input is capped at ~200k characters as a guard.
- Single-user, single-node, local/demo scope — authentication is out of scope for this exercise.
- Outbound access to the Gemini API is available and free-tier latency/limits are acceptable.
- Agency/system names are taken as written in the reports (no external entity resolution).

---

## Getting started

**Prerequisites:** Python 3.13 (3.14 lacks ML wheels), Node 18+, a free Gemini API key
(https://aistudio.google.com/apikey).

### Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate            # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt   # heavy first install (torch); first run downloads MiniLM (~80 MB)
cp .env.example .env              # then set GEMINI_API_KEY
uvicorn app.main:app --reload     # http://localhost:8000  (interactive docs at /docs)
```

### Frontend
```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Then: **Reports** → upload a PDF (samples in `materials/`) · **Insights** → *Generate insights* ·
**Q&A** → ask a question.

---

## API

| Method | Path | Purpose |
|---|---|---|
| GET  | `/health` | liveness + active model config |
| POST | `/upload` | PDF → extract → chunk → embed → store |
| GET  | `/reports` | list uploaded reports |
| POST | `/analyze/{id}` | basic per-report analysis |
| POST | `/extract/{id}` | extract structured findings for one report |
| POST | `/insights/build` | extract findings for all reports, then aggregate |
| GET  | `/insights` | cross-report aggregation |
| GET  | `/findings` | all structured findings |
| POST | `/insights/summary` | LLM executive summary |
| POST | `/qa` | RAG question answering with citations |

---

## Project structure

```
backend/app/
  api/routes.py       endpoints
  config.py           typed settings (fail-fast on missing key)
  llm/                provider abstraction (base, gemini, factory)
  ingestion/          pdf (PyMuPDF) + chunk
  extraction/         full text -> structured Findings (LLM JSON mode)
  models/             findings taxonomy + API schemas
  vectorstore/        embeddings (MiniLM) + ChromaDB
  insights/           aggregate (code) + executive summary (LLM)
  qa/                 RAG question answering
  storage/            SQLite (reports + findings)
frontend/src/         React app (Reports / Insights / Q&A)
materials/            sample audit reports
```

---

## Challenges Encountered

- **Pure RAG can't aggregate.** Early on, a RAG-for-everything approach couldn't answer
  "how often across all reports" — top-k retrieval only sees a handful of chunks. This drove the
  headline decision: structured extraction + code aggregation for counts, RAG for lookups.
- **Consistent categories for counting.** Free-text themes don't aggregate ("Access Control" vs
  "IAM"). Solved with a fixed enum taxonomy enforced by schema-constrained LLM output.
- **Model availability.** `gemini-1.5-flash` returned `404 NOT_FOUND` (retired); I listed the
  models available to the key via the API and switched to `gemini-2.5-flash`.
- **Thinking-model truncation.** 2.5-flash is a reasoning model — its internal "thinking" consumed
  the output-token budget and truncated the JSON. Fixed by disabling thinking (`thinking_budget=0`)
  and raising `max_output_tokens` for structured calls.
- **Deprecated SDK.** Migrated from the deprecated `google-generativeai` package to the current
  unified `google-genai` SDK.
- **Charts blank in captured screenshots.** Recharts' entry animation left bars empty in headless
  captures; disabling animation fixed the screenshots and made the dashboard render instantly.

---

## Limitations & future work

- **Extraction quality is the ceiling** — a missed finding isn't counted; the aggregation itself
  is exact. Next step: an evaluation harness + human spot-checks.
- **No OCR** — scanned/image-only PDFs yield no text (detected, returns a clear error).
- **Insights build is sequential** — LLM extraction calls run one after another; would
  parallelise / move to a background job.
- **Single-node stores** — SQLite + Chroma suit this scope; production → Postgres + pgvector,
  plus authentication, rate limiting, and observability.
