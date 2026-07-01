"""FastAPI application entrypoint.

Run from the backend/ directory:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import get_settings
from .storage import db

# Load + validate config at import time so a missing GEMINI_API_KEY fails fast
# (clear startup error) instead of surfacing deep inside a request later.
settings = get_settings()

# Ensure the SQLite schema exists before the first request.
db.init_db()

app = FastAPI(title="AI Audit Insights API", version="0.1.0")

# Allow the React dev server (different origin/port) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
