from typing import Optional

from src.repositories.base import BaseRepository


class ProfileRepository(BaseRepository):
    """CRUD operations for profiles table."""

    async def create(
        self,
        user_id: int,
        platform: str,
        url: str,
        headline: Optional[str],
        summary: Optional[str],
        data_json: Optional[dict],
    ) -> int:
        profile_id = await self.fetchval(
            """
            INSERT INTO profiles (user_id, platform, url, headline, summary, data_json)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
            """,
            user_id,
            platform,
            url,
            headline,
            summary,
            data_json,
        )
        return int(profile_id)

    async def get(self, profile_id: int) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM profiles WHERE id = $1;", profile_id)
        return self.record_to_dict(rec)
