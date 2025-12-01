from uuid import UUID
from fastapi import APIRouter, Query, Path, Depends

from src.repositories.recommendations import RecommendationRepository

router = APIRouter()


@router.get("/recommendations", tags=["Jobs"])
async def get_recommendations(
    analysis_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RecommendationRepository = Depends(),
):
    """
    Get job recommendations for a given analysis.
    """
    recommendations = await repo.list_by_analysis_with_jobs(analysis_id, limit, offset)
    return recommendations


@router.patch("/recommendations/{id}", tags=["Jobs"], status_code=204)
async def update_recommendation_status(recommendation_id: int = Path(..., alias="id"), status: str = Query(...)):
    """
    Update the status of a recommendation (e.g., saved, hidden).
    """
    # In a real app, this would update the recommendation's state.
    # For now, this is a no-op.
    return
