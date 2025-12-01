from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.db import close_db_pool, health_check_db, init_db_pool

app = FastAPI(
    title="Resume Analyzer & Job Matcher API",
    description=(
        "Backend service for analyzing resumes and profiles for ATS compliance, "
        "extracting skills, and recommending job openings."
    ),
    version="0.1.0",
    contact={"name": "Resume Analyzer", "url": "https://example.com"},
    license_info={"name": "Proprietary"},
)

# Load settings once
settings = get_settings()

# CORS configuration from settings; if empty, default to permissive for local dev
cors_origins = settings.cors_origins() or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize resources such as the database pool."""
    await init_db_pool()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Gracefully shutdown resources such as the database pool."""
    await close_db_pool()


@app.get(
    "/",
    summary="Health Check",
    description="Basic service and database health check.",
    tags=["Health"],
)
async def health_check() -> Dict[str, object]:
    db_ok = await health_check_db()
    return {"message": "Healthy", "database": db_ok}
