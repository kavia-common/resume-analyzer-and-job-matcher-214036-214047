import logging
from typing import List, Optional
from uuid import UUID

from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ResumeRepository(BaseRepository):
    """CRUD operations for resumes table."""

    async def create(
        self,
        user_id: UUID,
        file_name: str,
        content_type: str,
        content_text: Optional[str] = None,
        storage_path: Optional[str] = None,
    ) -> int:
        logger.info(
            f"Persisting resume to DB: user_id='{user_id}', file_name='{file_name}', "
            f"content_type='{content_type}', has_content_text={content_text is not None}"
        )
        try:
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
            logger.info(f"Successfully persisted resume with id={resume_id}")
            return int(resume_id)
        except Exception as e:
            logger.error(
                f"DB error creating resume for user_id='{user_id}': {e}", exc_info=True
            )
            raise

    async def get(self, resume_id: int) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM resumes WHERE id = $1;", resume_id)
        return self.record_to_dict(rec)

    async def list_by_user(self, user_id: UUID) -> List[dict]:
        rows = await self.fetch(
            "SELECT * FROM resumes WHERE user_id = $1 ORDER BY created_at DESC;", user_id
        )
        return [dict(r) for r in rows]
