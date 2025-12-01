import asyncio
import logging
from typing import Optional

import asyncpg

from src.core.config import get_settings

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


# PUBLIC_INTERFACE
async def init_db_pool() -> Optional[asyncpg.Pool]:
    """Initialize and return a global asyncpg connection pool if a DSN is available.

    Safe to call multiple times; subsequent calls will return the existing pool.
    Returns None if no usable DSN is configured.
    """
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    dsn = settings.database_dsn()
    if not dsn:
        logger.info("Database settings not provided; continuing without database.")
        return None

    try:
        _pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=1,
            max_size=10,
            timeout=10.0,
            command_timeout=30.0,
        )
        logger.info("Database pool initialized.")
    except Exception as exc:
        # Do not crash service; just run without DB
        logger.warning("Failed to initialize database pool: %s. Service will run without DB.", exc)
        _pool = None
    return _pool


# PUBLIC_INTERFACE
async def close_db_pool() -> None:
    """Close the global asyncpg connection pool if it exists."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed.")


# PUBLIC_INTERFACE
def get_db_pool() -> asyncpg.Pool:
    """Return the current connection pool; raises if not initialized.

    This is intentionally strict to ensure repositories fail fast if DB is unavailable.
    """
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Ensure app startup has run and DB settings are configured.")
    return _pool


# PUBLIC_INTERFACE
async def health_check_db() -> bool:
    """Run a lightweight DB health check query. Returns True if OK; False if DB missing or unhealthy."""
    try:
        if _pool is None:
            return False
        async with _pool.acquire() as conn:
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
