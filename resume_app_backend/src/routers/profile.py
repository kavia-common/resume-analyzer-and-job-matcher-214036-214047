from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.repositories.profiles import ProfileRepository
from src.services.analysis_orchestrator import AnalysisOrchestratorService

router = APIRouter()


class SubmitUrlRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    profile_url: str = Field(..., description="URL of the profile to analyze")


@router.post("/profiles/submit-url", tags=["Profiles"], status_code=202)
async def submit_profile_url(req: SubmitUrlRequest):
    """
    Submit a profile URL for analysis.
    """
    # In a real app, this would trigger a background job to scrape the URL.
    # For now, we'll just create a placeholder profile and analysis.
    profile_repo = ProfileRepository()
    profile_id = await profile_repo.create(
        user_id=req.user_id,
        platform="linkedin",  # Assuming linkedin for now
        url=req.profile_url,
        headline="Placeholder Headline",
        summary="Placeholder Summary",
        data_json={},
    )

    orchestrator = AnalysisOrchestratorService()
    analysis_id = await orchestrator.analyze_text(user_id=req.user_id, text="Placeholder Summary")

    return {"profile_id": profile_id, "analysis_id": analysis_id}
