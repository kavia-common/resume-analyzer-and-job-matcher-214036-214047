from typing import List, Optional

from src.repositories.base import BaseRepository


class JobRepository(BaseRepository):
    """CRUD operations for jobs."""

    async def upsert_by_external(self, external_id: str, source: str, title: str, company: str,
                                 location: Optional[str], description: Optional[str],
                                 url: Optional[str], skills_json: Optional[list[str]]) -> int:
        job_id = await self.fetchval(
            """
            INSERT INTO jobs (external_id, source, title, company, location, description, url, skills_json)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (external_id, source)
            DO UPDATE SET title = EXCLUDED.title,
                          company = EXCLUDED.company,
                          location = EXCLUDED.location,
                          description = EXCLUDED.description,
                          url = EXCLUDED.url,
                          skills_json = EXCLUDED.skills_json
            RETURNING id;
            """,
            external_id,
            source,
            title,
            company,
            location,
            description,
            url,
            skills_json,
        )
        return int(job_id)

    async def list_recent(self, limit: int = 50) -> List[dict]:
        rows = await self.fetch("SELECT * FROM jobs ORDER BY created_at DESC LIMIT $1;", limit)
        return [dict(r) for r in rows]
