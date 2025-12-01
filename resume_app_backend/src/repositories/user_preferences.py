from typing import Optional
from uuid import UUID

from src.repositories.base import BaseRepository


class UserPreferenceRepository(BaseRepository):
    """CRUD operations for user_preferences."""

    async def upsert(
        self,
        user_id: UUID,
        locations: Optional[list[str]],
        roles: Optional[list[str]],
        remote_ok: Optional[bool],
        salary_min: Optional[int],
        data_json: Optional[dict],
    ) -> int:
        pref_id = await self.fetchval(
            """
            INSERT INTO user_preferences (user_id, locations, roles, remote_ok, salary_min, data_json)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id)
            DO UPDATE SET locations = EXCLUDED.locations,
                          roles = EXCLUDED.roles,
                          remote_ok = EXCLUDED.remote_ok,
                          salary_min = EXCLUDED.salary_min,
                          data_json = EXCLUDED.data_json
            RETURNING id;
            """,
            user_id,
            locations,
            roles,
            remote_ok,
            salary_min,
            data_json,
        )
        return int(pref_id)

    async def get_by_user(self, user_id: UUID) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM user_preferences WHERE user_id = $1;", user_id)
        return self.record_to_dict(rec)
