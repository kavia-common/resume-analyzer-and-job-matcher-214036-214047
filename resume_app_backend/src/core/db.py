import asyncio
from typing import Optional

import asyncpg

from src.core.config import get_settings

_pool: Optional[asyncpg.Pool] = None


# PUBLIC_INTERFACE
async def init_db_pool() -> asyncpg.Pool:
    """Initialize and return a global asyncpg connection pool.

    Uses DATABASE_URL from settings. Safe to call multiple times;
    subsequent calls will return the existing pool.
    """
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()

    # Create a pool with reasonable defaults for API workloads
    _pool = await asyncpg.create_pool(
        dsn=str(settings.DATABASE_URL),
        min_size=1,
        max_size=10,
        timeout=10.0,
        command_timeout=30.0,
    )
    return _pool


# PUBLIC_INTERFACE
async def close_db_pool() -> None:
    """Close the global asyncpg connection pool if it exists."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


# PUBLIC_INTERFACE
def get_db_pool() -> asyncpg.Pool:
    """Return the current connection pool; raises if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Ensure app startup has run.")
    return _pool


# PUBLIC_INTERFACE
async def health_check_db() -> bool:
    """Run a lightweight DB health check query. Returns True if OK."""
    try:
        pool = get_db_pool()
        async with pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1;")
            return val == 1
    except Exception:
        return False


# Convenience function for synchronous contexts (not for production paths)
def init_db_pool_sync() -> None:
    """Initialize DB pool from a synchronous context (e.g., scripts)."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db_pool())
