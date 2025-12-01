from typing import List, Optional

from src.repositories.base import BaseRepository


class SkillRepository(BaseRepository):
    """CRUD operations for skills table."""

    async def get_or_create(self, name: str, type: Optional[str]) -> int:
        # Try find by name
        rec = await self.fetchrow("SELECT id FROM skills WHERE name = $1;", name)
        if rec:
            return int(rec["id"])
        # Create
        skill_id = await self.fetchval(
            """
            INSERT INTO skills (name, type)
            VALUES ($1, $2)
            RETURNING id;
            """,
            name,
            type,
        )
        return int(skill_id)

    async def list_all(self) -> List[dict]:
        rows = await self.fetch("SELECT * FROM skills ORDER BY name ASC;")
        return [dict(r) for r in rows]
