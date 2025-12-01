from typing import List, Optional

from src.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository):
    """CRUD operations for analyses table."""

    async def create(
        self,
        user_id: int,
        resume_id: Optional[int],
        profile_id: Optional[int],
        target_role: Optional[str],
        status: str,
        score_overall: Optional[float] = None,
    ) -> int:
        analysis_id = await self.fetchval(
            """
            INSERT INTO analyses (user_id, resume_id, profile_id, target_role, status, score_overall)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
            """,
            user_id,
            resume_id,
            profile_id,
            target_role,
            status,
            score_overall,
        )
        return int(analysis_id)

    async def get(self, analysis_id: int) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM analyses WHERE id = $1;", analysis_id)
        return self.record_to_dict(rec)

    async def update_status(self, analysis_id: int, status: str, score_overall: Optional[float] = None) -> None:
        await self.execute(
            "UPDATE analyses SET status = $1, score_overall = COALESCE($2, score_overall) WHERE id = $3;",
            status,
            score_overall,
            analysis_id,
        )

    async def list_by_user(self, user_id: int) -> List[dict]:
        rows = await self.fetch("SELECT * FROM analyses WHERE user_id = $1 ORDER BY created_at DESC;", user_id)
        return [dict(r) for r in rows]
