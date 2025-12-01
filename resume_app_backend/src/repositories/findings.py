from typing import List, Optional

from src.repositories.base import BaseRepository


class FindingRepository(BaseRepository):
    """CRUD operations for findings table."""

    async def create(
        self,
        analysis_id: int,
        category: str,
        severity: str,
        message: str,
        detail_json: Optional[dict],
    ) -> int:
        finding_id = await self.fetchval(
            """
            INSERT INTO findings (analysis_id, category, severity, message, detail_json)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
            """,
            analysis_id,
            category,
            severity,
            message,
            detail_json,
        )
        return int(finding_id)

    async def list_by_analysis(self, analysis_id: int) -> List[dict]:
        rows = await self.fetch("SELECT * FROM findings WHERE analysis_id = $1 ORDER BY created_at ASC;", analysis_id)
        return [dict(r) for r in rows]
