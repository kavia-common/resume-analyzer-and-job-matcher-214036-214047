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

    async def list_by_analysis_with_jobs(
        self, analysis_id: int, limit: int, offset: int
    ) -> List[dict]:
        rows = await self.fetch(
            """
            SELECT r.id, r.analysis_id, r.job_id, r.score, r.created_at,
                   j.title, j.company, j.location, j.url
            FROM recommendations r
            JOIN jobs j ON r.job_id = j.id
            WHERE r.analysis_id = $1
            ORDER BY r.score DESC
            LIMIT $2 OFFSET $3;
            """,
            analysis_id,
            limit,
            offset,
        )
        return [dict(r) for r in rows]
