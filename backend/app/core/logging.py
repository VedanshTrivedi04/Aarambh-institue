"""
app/core/logging.py
-------------------
Structured JSON logging with per-request correlation IDs.

Usage:
    from app.core.logging import get_logger, request_id_ctx_var

    logger = get_logger(__name__)
    logger.info("Batch attendance marked", batch_id=batch_id, count=len(entries))

Sensitive fields listed in REDACTED_KEYS are automatically replaced with
"[REDACTED]" before emission so secrets never reach log sinks.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

import orjson
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable that stores the correlation ID for the current request.
# Every log record emitted during a request will carry this ID.
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")

# Keys whose values are NEVER written to logs regardless of level.
REDACTED_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "password_hash",
        "hashed_password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "secret_key",
        "otp",
        "pin",
        "card_number",
        "cvv",
    }
)


def _redact(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive keys from a mapping."""
    result: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in REDACTED_KEYS:
            result[k] = "[REDACTED]"
        elif isinstance(v, dict):
            result[k] = _redact(v)
        else:
            result[k] = v
    return result


class _JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON using orjson for speed."""

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx_var.get(""),
        }

        # Attach any extra keyword arguments passed by the caller.
        if hasattr(record, "extra_fields"):
            log_object.update(_redact(record.extra_fields))  # type: ignore[arg-type]

        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return orjson.dumps(log_object).decode("utf-8")


def _build_handler() -> logging.StreamHandler:  # type: ignore[type-arg]
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    return handler


def configure_logging(level: str = "INFO") -> None:
    """Call once at application startup to set up the root logger."""
    root = logging.getLogger()
    root.setLevel(level)
    # Remove any existing handlers (e.g. uvicorn defaults) and add ours.
    root.handlers.clear()
    root.addHandler(_build_handler())


class StructuredLogger(logging.LoggerAdapter):  # type: ignore[type-arg]
    """Drop-in replacement for stdlib logger that accepts keyword args."""

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        extra_fields = kwargs.pop("extra_fields", {})
        # Collect any caller kwargs (e.g. batch_id=1) as extra_fields.
        inline = {k: v for k, v in list(kwargs.items()) if k not in {"exc_info", "stack_info"}}
        for k in inline:
            kwargs.pop(k)
        extra_fields.update(inline)
        self.extra["extra_fields"] = extra_fields  # type: ignore[index]
        return msg, kwargs


def get_logger(name: str) -> StructuredLogger:
    base = logging.getLogger(name)
    return StructuredLogger(base, extra={"extra_fields": {}})


# ---------------------------------------------------------------------------
# Middleware: inject request_id into context var on every request
# ---------------------------------------------------------------------------

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Assigns a UUID to each request and exposes it via `X-Request-ID`
    response header and the `request_id_ctx_var` context variable.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx_var.set(rid)
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_ctx_var.reset(token)
