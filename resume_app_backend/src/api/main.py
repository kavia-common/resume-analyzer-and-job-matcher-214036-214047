from typing import Dict
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.config import get_settings
from src.core.db import close_db_pool, health_check_db, init_db_pool
from src.services import AnalysisOrchestratorService
from src.routers import upload, profile, analysis, jobs

openapi_tags = [
    {"name": "Health", "description": "Service liveness and readiness."},
    {"name": "Analysis", "description": "Run ATS analysis and view results."},
    {"name": "Resumes", "description": "Upload and manage resumes."},
    {"name": "Profiles", "description": "Manage user profiles from external sites."},
    {"name": "Jobs", "description": "Get job recommendations."},
    {"name": "Users", "description": "Manage users."},
]

app = FastAPI(
    title="Resume Analyzer & Job Matcher API",
    description=(
        "Backend service for analyzing resumes and profiles for ATS compliance, "
        "extracting skills, and recommending job openings."
    ),
    version="0.1.0",
    contact={"name": "Resume Analyzer", "url": "https://example.com"},
    license_info={"name": "Proprietary"},
    openapi_tags=openapi_tags,
)

# Load settings once
settings = get_settings()

# CORS configuration from settings; default to http://localhost:3000 (handled in settings.cors_origins)
cors_origins = settings.cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize resources such as the database pool, if possible."""
    await init_db_pool()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Gracefully shutdown resources such as the database pool."""
    await close_db_pool()


@app.get(
    "/",
    summary="Health Check",
    description="Basic service health check that does not require database connectivity.",
    tags=["Health"],
)
async def health_check() -> Dict[str, object]:
    """Health check route that returns service status and DB readiness (if configured)."""
    db_ok = await health_check_db()
    return {"message": "Healthy", "database": db_ok}


app.include_router(upload.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")


class AnalyzeTextRequest(BaseModel):
    """Request model for text analysis."""
    user_id: int = Field(..., description="User identifier for whom the analysis is created")
    text: str | None = Field(None, description="Plain text content to analyze")
    target_role: str | None = Field(None, description="Target role to guide suggestions")


class AnalyzeTextResponse(BaseModel):
    """Response containing analysis id and status."""
    analysis_id: UUID = Field(..., description="Created analysis id")
    status: str = Field(..., description="Analysis status after orchestration")


@app.post(
    "/analysis/text",
    summary="Run text-based analysis",
    description="Create an analysis for a given plain text (e.g., extracted resume text).",
    tags=["Analysis"],
    response_model=AnalyzeTextResponse,
)
async def analyze_text(req: AnalyzeTextRequest) -> AnalyzeTextResponse:
    """Run analysis orchestration for provided text and return the analysis id."""
    svc = AnalysisOrchestratorService()
    analysis_id = await svc.analyze_text(user_id=req.user_id, text=req.text, target_role=req.target_role)
    return AnalyzeTextResponse(analysis_id=analysis_id, status="complete")
