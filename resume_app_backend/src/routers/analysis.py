from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path

from src.domain.schemas import Analysis, AnalysisStatus
from src.repositories.analyses import AnalysisRepository
from src.repositories.findings import FindingRepository
from src.repositories.suggestions import SuggestionRepository

router = APIRouter()


@router.get(
    "/analysis/{id}/status",
    tags=["Analysis"],
    response_model=AnalysisStatus,
)
async def get_analysis_status(
    analysis_id: UUID = Path(..., alias="id"),
    repo: AnalysisRepository = Depends(),
):
    """
    Get the status of an analysis.
    """
    analysis = await repo.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return AnalysisStatus(
        status=analysis["status"], score_overall=analysis.get("score_overall")
    )


@router.get("/analysis/{id}/results", tags=["Analysis"])
async def get_analysis_results(
    analysis_id: UUID = Path(..., alias="id"),
    analysis_repo: AnalysisRepository = Depends(),
    findings_repo: FindingRepository = Depends(),
    suggestions_repo: SuggestionRepository = Depends(),
):
    """
    Get the full results of a completed analysis.
    """
    analysis = await analysis_repo.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    findings = await findings_repo.list_by_analysis(analysis_id)
    suggestions = await suggestions_repo.list_by_analysis(analysis_id)

    return {"analysis": analysis, "findings": findings, "suggestions": suggestions}


@router.post(
    "/analysis/{id}/suggestions/ack",
    tags=["Analysis"],
    status_code=204,
)
async def acknowledge_suggestion(
    analysis_id: UUID = Path(..., alias="id"),
    suggestion_id: int = Body(..., embed=True),
):
    """
    Acknowledge a suggestion.
    """
    # In a real app, this would update the suggestion's state.
    # For now, this is a no-op.
    return


@router.post("/analysis/{id}/cancel", tags=["Analysis"], status_code=204)
async def cancel_analysis(
    analysis_id: UUID = Path(..., alias="id"),
    repo: AnalysisRepository = Depends(),
):
    """
    Cancel an ongoing analysis.
    """
    analysis = await repo.get(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    await repo.update_status(analysis_id, "cancelled")
    return


@router.get(
    "/users/{userId}/analyses",
    tags=["Users"],
    response_model=List[Analysis],
)
async def get_user_analyses(
    user_id: int = Path(..., alias="userId"),
    repo: AnalysisRepository = Depends(),
):
    """
    Get all analyses for a user.
    """
    analyses = await repo.list_by_user(user_id)
    return analyses
