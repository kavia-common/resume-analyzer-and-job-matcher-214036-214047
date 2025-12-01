from typing import Any, Dict, List, Optional, Sequence

import asyncpg

from src.core.db import get_db_pool


class BaseRepository:
    """Lightweight async repository base for executing SQL with asyncpg."""

    def __init__(self) -> None:
        self.pool = get_db_pool()

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            rows: List[asyncpg.Record] = await conn.fetch(query, *args)
            return rows

    async def fetchval(self, query: str, *args: Any) -> Any:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def executemany(self, query: str, args_seq: Sequence[Sequence[Any]]) -> None:
        async with self.pool.acquire() as conn:
            await conn.executemany(query, args_seq)

    @staticmethod
    def record_to_dict(record: Optional[asyncpg.Record]) -> Optional[Dict[str, Any]]:
        if record is None:
            return None
        return dict(record)
