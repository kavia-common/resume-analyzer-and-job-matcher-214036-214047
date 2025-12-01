from typing import Optional
from uuid import UUID, uuid4

from src.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """CRUD operations for users table."""

    async def create(self, email: str, full_name: Optional[str]) -> UUID:
        user_id = await self.fetchval(
            """
            INSERT INTO users (id, email, full_name)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            uuid4(),
            email,
            full_name,
        )
        return user_id

    async def get_by_id(self, user_id: UUID) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM users WHERE id = $1;", user_id)
        return self.record_to_dict(rec)

    async def get_by_email(self, email: str) -> Optional[dict]:
        rec = await self.fetchrow("SELECT * FROM users WHERE email = $1;", email)
        return self.record_to_dict(rec)
