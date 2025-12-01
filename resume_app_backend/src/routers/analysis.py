from fastapi import APIRouter, Path, Body
from typing import List

from src.repositories.analyses import AnalysisRepository
from src.repositories.findings import FindingRepository
from src.repositories.suggestions import SuggestionRepository
from src.domain.schemas import Analysis

router = APIRouter()


@router.get("/analysis/{id}/status", tags=["Analysis"])
async def get_analysis_status(analysis_id: int = Path(..., alias="id")):
    """
    Get the status of an analysis.
    """
    repo = AnalysisRepository()
    analysis = await repo.get(analysis_id)
    if not analysis:
        return {"status": "not_found"}
    return {"status": analysis["status"]}


@router.get("/analysis/{id}/results", tags=["Analysis"])
async def get_analysis_results(analysis_id: int = Path(..., alias="id")):
    """
    Get the full results of a completed analysis.
    """
    analysis_repo = AnalysisRepository()
    findings_repo = FindingRepository()
    suggestions_repo = SuggestionRepository()

    analysis = await analysis_repo.get(analysis_id)
    findings = await findings_repo.list_by_analysis(analysis_id)
    suggestions = await suggestions_repo.list_by_analysis(analysis_id)

    return {"analysis": analysis, "findings": findings, "suggestions": suggestions}


@router.post("/analysis/{id}/suggestions/ack", tags=["Analysis"], status_code=204)
async def acknowledge_suggestion(analysis_id: int = Path(..., alias="id"), suggestion_id: int = Body(..., embed=True)):
    """
    Acknowledge a suggestion.
    """
    # In a real app, this would update the suggestion's state.
    # For now, this is a no-op.
    return


@router.post("/analysis/{id}/cancel", tags=["Analysis"], status_code=204)
async def cancel_analysis(analysis_id: int = Path(..., alias="id")):
    """
    Cancel an ongoing analysis.
    """
    repo = AnalysisRepository()
    await repo.update_status(analysis_id, "cancelled")
    return


@router.get("/users/{userId}/analyses", tags=["Users"], response_model=List[Analysis])
async def get_user_analyses(user_id: int = Path(..., alias="userId")):
    """
    Get all analyses for a user.
    """
    repo = AnalysisRepository()
    analyses = await repo.list_by_user(user_id)
    return analyses
