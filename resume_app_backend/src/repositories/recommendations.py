from typing import List

from src.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository):
    """CRUD operations for recommendations."""

    async def create(self, analysis_id: int, job_id: int, score: float) -> int:
        rec_id = await self.fetchval(
            """
            INSERT INTO recommendations (analysis_id, job_id, score)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            analysis_id,
            job_id,
            score,
        )
        return int(rec_id)

    async def list_by_analysis(self, analysis_id: int) -> List[dict]:
        rows = await self.fetch(
            "SELECT * FROM recommendations WHERE analysis_id = $1 ORDER BY score DESC;",
            analysis_id,
        )
        return [dict(r) for r in rows]
