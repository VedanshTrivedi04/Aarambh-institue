"""
app/db/session.py
-----------------
Async SQLAlchemy engine and session factory.

async_engine       — shared engine instance (one per process)
AsyncSessionLocal  — sessionmaker that yields AsyncSession objects
get_db()           — FastAPI dependency that yields an AsyncSession per request

All queries in services use `async with db.begin():` for explicit
transaction control (backend.md §3, rules.md §6).
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_settings = get_settings()

# ---------------------------------------------------------------------------
# Engine — created once, shared across all requests in the process.
# Pool settings tuned for a coaching-institute load profile:
#   - pool_size=10: adequate for peak evening class hours
#   - max_overflow=20: headroom for spikes on fee-due dates
#   - pool_pre_ping=True: avoids stale connection errors on long idle periods
# ---------------------------------------------------------------------------
async_engine = create_async_engine(
    _settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,           # recycle connections every 5 mins to prevent stale cloud proxies
    pool_pre_ping=True,
    echo=_settings.DEBUG,       # SQL echo only in debug mode
    future=True,
)

# ---------------------------------------------------------------------------
# Session factory
# expire_on_commit=False prevents SQLAlchemy from expiring attributes after
# commit, which is important in async code where lazy loading is unavailable.
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a per-request async database session.

    Usage in a router:
        @router.get("/batches")
        async def list_batches(db: AsyncSession = Depends(get_db)):
            ...

    The session is automatically closed at the end of the request.
    Services should manage their own transaction boundaries using:
        async with db.begin():
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
