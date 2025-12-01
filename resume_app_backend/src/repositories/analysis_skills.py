from typing import List

from src.repositories.base import BaseRepository


class AnalysisSkillRepository(BaseRepository):
    """CRUD operations for analysis_skills (junction table)."""

    async def create(self, analysis_id: int, skill_id: int, confidence: float | None) -> int:
        rec_id = await self.fetchval(
            """
            INSERT INTO analysis_skills (analysis_id, skill_id, confidence)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            analysis_id,
            skill_id,
            confidence,
        )
        return int(rec_id)

    async def list_by_analysis(self, analysis_id: int) -> List[dict]:
        rows = await self.fetch(
            """
            SELECT ask.*, s.name as skill_name, s.type as skill_type
            FROM analysis_skills ask
            JOIN skills s ON s.id = ask.skill_id
            WHERE ask.analysis_id = $1
            ORDER BY ask.confidence DESC NULLS LAST, s.name ASC;
            """,
            analysis_id,
        )
        return [dict(r) for r in rows]
