from typing import List
from uuid import UUID

from src.repositories.base import BaseRepository


class SuggestionRepository(BaseRepository):
    """CRUD operations for suggestions."""

    async def create(self, analysis_id: UUID, title: str, message: str, priority: str) -> int:
        suggestion_id = await self.fetchval(
            """
            INSERT INTO suggestions (analysis_id, title, message, priority)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
            """,
            analysis_id,
            title,
            message,
            priority,
        )
        return int(suggestion_id)

    async def list_by_analysis(self, analysis_id: UUID) -> List[dict]:
        rows = await self.fetch("SELECT * FROM suggestions WHERE analysis_id = $1 ORDER BY created_at ASC;", analysis_id)
        return [dict(r) for r in rows]
