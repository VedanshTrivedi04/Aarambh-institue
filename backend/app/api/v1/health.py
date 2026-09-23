"""
app/api/v1/health.py
--------------------
Liveness and readiness endpoints.

GET /health  — liveness: the process is alive.
GET /ready   — readiness: DB and Redis are reachable, app can serve traffic.

These are intentionally unauthenticated — needed by load balancers and
orchestrators (Docker health-check, Kubernetes probes) before any JWT is issued.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from sqlalchemy import text

from app.core.lifespan import redis_client
from app.core.logging import get_logger
from app.db.session import async_engine

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get(
    "/health",
    summary="Liveness probe",
    description="Returns 200 if the application process is running.",
    include_in_schema=True,
)
async def health() -> ORJSONResponse:
    return ORJSONResponse({"status": "ok"})


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns 200 only if the database and Redis are reachable.",
    include_in_schema=True,
)
async def ready() -> ORJSONResponse:
    checks: dict[str, str] = {}
    overall_ok = True

    # --- Database ---
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.error("Readiness: database check failed", error=str(exc))
        checks["database"] = "unavailable"
        overall_ok = False

    # --- Redis ---
    if redis_client is not None:
        try:
            await redis_client.ping()
            checks["redis"] = "ok"
            checks["cache"] = "redis"
        except Exception as exc:
            logger.warning("Readiness: redis check failed", error=str(exc))
            checks["redis"] = "unavailable"
            checks["cache"] = "memory_fallback"
            # Redis failure degrades (caching/rate-limiting) but doesn't block traffic.
    else:
        checks["redis"] = "not_configured"
        checks["cache"] = "memory_fallback"

    status_code = 200 if overall_ok else 503
    return ORJSONResponse(
        status_code=status_code,
        content={"status": "ready" if overall_ok else "not_ready", "checks": checks},
    )
