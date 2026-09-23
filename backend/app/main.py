"""
app/main.py
-----------
FastAPI application factory.

Responsibilities:
  - Create the FastAPI app with metadata and lifespan.
  - Register middleware (CORS, RequestId).
  - Register exception handlers.
  - Mount versioned API routers.

Do NOT put business logic here — it stays in services/.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import RequestIdMiddleware, get_logger

logger = get_logger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Aarambh Institute ERP — backend API for the Admin, Teacher, "
            "Student, and Parent portals."
        ),
        docs_url="/docs" if settings.DEBUG else None,   # Hide Swagger in prod
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        default_response_class=ORJSONResponse,          # Faster JSON via orjson
        lifespan=lifespan,
    )

    _register_middleware(app)
    register_exception_handlers(app)
    _register_routers(app)

    return app


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


def _register_middleware(app: FastAPI) -> None:
    # 1. CORS — origins come entirely from env, never hard-coded.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=settings.CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 2. Request-ID injection (also adds X-Request-ID to every response).
    app.add_middleware(RequestIdMiddleware)

    # 3. Request timing log (DEBUG only — helps profile slow endpoints).
    if settings.DEBUG:
        @app.middleware("http")
        async def log_request_time(request: Request, call_next):  # type: ignore[no-untyped-def]
            start = time.perf_counter()
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=round(elapsed_ms, 2),
            )
            return response


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------


def _register_routers(app: FastAPI) -> None:
    # Root level liveness probe for cloud platform health checks (Render, AWS, GCP)
    @app.get("/health", include_in_schema=False)
    async def root_health() -> ORJSONResponse:
        return ORJSONResponse({"status": "ok"})

    @app.get("/", include_in_schema=False)
    async def root_index() -> ORJSONResponse:
        return ORJSONResponse({
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "online",
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
        })

    app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# WSGI/ASGI entry-point
# ---------------------------------------------------------------------------

app = create_app()
