"""
app/core/lifespan.py
--------------------
FastAPI application lifespan — startup and shutdown resource management.

Handles:
  - Async database engine warm-up / teardown
  - Redis connection pool warm-up / teardown
  - Structured logging of each lifecycle phase
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import async_engine

logger = get_logger(__name__)

# Module-level redis client; populated during startup.
redis_client: aioredis.Redis | None = None  # type: ignore[type-arg]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Startup:
      1. Configure structured JSON logging.
      2. Verify database connectivity.
      3. Initialise Redis connection pool.

    Shutdown:
      1. Dispose database engine (returns pooled connections to the pool, then closes).
      2. Close Redis client.
    """
    global redis_client
    s = get_settings()

    # ------------------------------------------------------------------ #
    # STARTUP
    # ------------------------------------------------------------------ #
    configure_logging(level="DEBUG" if s.DEBUG else "INFO")
    logger.info("Starting Aarambh ERP API", env=s.APP_ENV, version=s.APP_VERSION)

    # Verify database is reachable.
    try:
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as exc:
        logger.exception("Database unreachable at startup", error=str(exc))
        raise

    # Initialise Redis.
    try:
        redis_client = aioredis.from_url(s.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connection verified")
    except Exception as exc:
        # Redis is not strictly required for the app to start; log and continue.
        logger.warning("Redis unreachable at startup — caching and rate limiting disabled", error=str(exc))
        redis_client = None

    logger.info("Application startup complete")
    yield  # <-- application is now serving requests

    # ------------------------------------------------------------------ #
    # SHUTDOWN
    # ------------------------------------------------------------------ #
    logger.info("Shutting down application…")

    await async_engine.dispose()
    logger.info("Database engine disposed")

    if redis_client:
        await redis_client.aclose()
        logger.info("Redis client closed")

    logger.info("Application shutdown complete")
