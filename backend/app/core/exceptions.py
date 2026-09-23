"""
app/core/exceptions.py
----------------------
Domain exceptions and FastAPI exception handlers.

Rules (from rules.md §4, backend.md §7):
- Services raise typed domain exceptions — never raw HTTPException deep inside services.
- Central handlers in main.py translate these to a consistent JSON error contract:
    { "detail": "...", "code": "ERROR_CODE", "request_id": "..." }
- request_id is injected from context so clients can reference it when filing support issues.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from app.core.logging import get_logger, request_id_ctx_var

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Domain exception hierarchy
# ---------------------------------------------------------------------------


class AppException(Exception):
    """Base for all application-level exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str, code: str | None = None, **context: Any) -> None:
        self.detail = detail
        if code:
            self.code = code
        self.context = context
        super().__init__(detail)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class ForbiddenError(AppException):
    """Caller is authenticated but does not own the requested resource."""
    status_code = status.HTTP_403_FORBIDDEN
    code = "FORBIDDEN"


class UnauthorizedError(AppException):
    """No valid credentials provided or token expired."""
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UNAUTHORIZED"


class ConflictError(AppException):
    """Duplicate resource or conflicting state."""
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"


class ValidationError(AppException):
    """Business-rule validation failed (distinct from Pydantic schema errors)."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "VALIDATION_ERROR"


class BatchFullError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "BATCH_FULL"


class DuplicateEnrollmentError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "ENROLLMENT_ALREADY_EXISTS"


class InstallmentAlreadyPaidError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "INSTALLMENT_ALREADY_PAID"


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"


class TokenExpiredError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "TOKEN_EXPIRED"


class TokenRevokedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "TOKEN_REVOKED"


class AccountInactiveError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "ACCOUNT_INACTIVE"


class CrossTenantAccessError(AppException):
    """Attempt to access a resource belonging to another institute/branch."""
    status_code = status.HTTP_403_FORBIDDEN
    code = "CROSS_TENANT_ACCESS"


class RateLimitExceededError(AppException):
    """Client has exceeded the permitted request rate limit."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "RATE_LIMIT_EXCEEDED"

    def __init__(
        self,
        detail: str = "Rate limit exceeded. Please try again later.",
        retry_after: int = 60,
        **context: Any,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(detail, code="RATE_LIMIT_EXCEEDED", retry_after=retry_after, **context)


# ---------------------------------------------------------------------------
# Helper to build a uniform error response body
# ---------------------------------------------------------------------------


def _error_body(code: str, detail: str) -> dict[str, Any]:
    return {
        "detail": detail,
        "code": code,
        "request_id": request_id_ctx_var.get(""),
    }


# ---------------------------------------------------------------------------
# Handler registration
# ---------------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all domain and framework exception handlers.
    Call this once inside the FastAPI app factory (main.py).
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
        logger.warning(
            "Domain exception",
            code=exc.code,
            detail=exc.detail,
            path=request.url.path,
            **exc.context,
        )
        headers: dict[str, str] = {}
        if isinstance(exc, RateLimitExceededError):
            headers["Retry-After"] = str(exc.retry_after)

        return ORJSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.detail),
            headers=headers if headers else None,
        )

    from fastapi.exceptions import RequestValidationError
    from pydantic import ValidationError as PydanticValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> ORJSONResponse:
        logger.warning("Request validation error", errors=exc.errors(), path=request.url.path)
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed",
                "code": "REQUEST_VALIDATION_ERROR",
                "errors": exc.errors(),
                "request_id": request_id_ctx_var.get(""),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        logger.exception("Unhandled exception", path=request.url.path)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred"),
        )
