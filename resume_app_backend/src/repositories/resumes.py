from typing import List, Optional

from src.repositories.base import BaseRepository


class ResumeRepository(BaseRepository):
    """CRUD operations for resumes table."""

    async def create(
        self,
        user_id: int,
        file_name: str,
        content_type: str,
        content_text: Optional[str] = None,
        storage_path: Optional[str] = None,
    ) -> int:
        resume_id = await self.fetchval(
            """
            INSERT INTO resumes (user_id, file_name, content_type, content_text, storage_path)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
            """,
            user_id,
            file_name,
            content_type,
            content_text,
            storage_path,
        )
        return int(resume_id)

    async def get(self, resume_id: int) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM resumes WHERE id = $1;", resume_id)
        return self.record_to_dict(rec)

    async def list_by_user(self, user_id: int) -> List[dict]:
        rows = await self.fetch("SELECT * FROM resumes WHERE user_id = $1 ORDER BY created_at DESC;", user_id)
        return [dict(r) for r in rows]
