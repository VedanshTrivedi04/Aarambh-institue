"""
app/core/rate_limit.py
----------------------
Multi-tier rate limiting engine for FastAPI endpoints using Redis with
resilient in-memory fallback. Enforces IP-tier, User-tier, and Tenant-tier limits
with RFC-compliant headers and 429 Too Many Requests responses.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Literal

from fastapi import Depends, Request, Response

from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger

logger = get_logger(__name__)


class _MemoryRateLimiter:
    """In-memory sliding window counter for dev, test suites, or Redis outages."""

    def __init__(self) -> None:
        self._counts: dict[str, tuple[int, float]] = {}
        self._lock = asyncio.Lock()

    async def check(self, key: str, limit: int, window_seconds: int = 60) -> tuple[bool, int, int]:
        now = time.monotonic()
        async with self._lock:
            entry = self._counts.get(key)
            if not entry or now >= entry[1]:
                # New window
                expire_at = now + window_seconds
                self._counts[key] = (1, expire_at)
                return True, limit - 1, window_seconds

            current_count, expire_at = entry
            reset_in = max(1, int(expire_at - now))
            new_count = current_count + 1
            self._counts[key] = (new_count, expire_at)

            allowed = new_count <= limit
            remaining = max(0, limit - new_count)
            return allowed, remaining, reset_in

    async def reset(self) -> None:
        async with self._lock:
            self._counts.clear()


class RateLimiter:
    def __init__(self) -> None:
        self._memory = _MemoryRateLimiter()

    def _get_redis(self) -> Any:
        try:
            from app.core.lifespan import redis_client
            return redis_client
        except Exception:
            return None

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
    ) -> tuple[bool, int, int]:
        """
        Check rate limit for a given key.
        Returns: (is_allowed, remaining_quota, reset_in_seconds)
        """
        redis = self._get_redis()
        if redis:
            try:
                # Use Redis atomic pipeline
                pipe = redis.pipeline(transaction=True)
                pipe.incr(key)
                pipe.ttl(key)
                results = await pipe.execute()
                current_count = results[0]
                ttl = results[1]

                if ttl == -1 or ttl is None:
                    await redis.expire(key, window_seconds)
                    ttl = window_seconds

                reset_in = max(1, ttl)
                allowed = current_count <= limit
                remaining = max(0, limit - current_count)
                return allowed, remaining, reset_in
            except Exception as exc:
                logger.warning("Redis rate limit check failed, using memory fallback", key=key, error=str(exc))
                return await self._memory.check(key, limit, window_seconds)
        else:
            return await self._memory.check(key, limit, window_seconds)


rate_limiter = RateLimiter()


def rate_limit(
    requests_per_minute: int = 60,
    tier: Literal["ip", "user", "tenant"] = "user",
) -> Callable[..., Any]:
    """
    FastAPI dependency that enforces rate limits and injects rate limit headers.
    """
    async def dependency(request: Request, response: Response) -> None:
        # 1. Determine key based on tier
        client_ip = request.client.host if request.client else "unknown"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

        identifier: str = client_ip
        if tier == "user":
            user = getattr(request.state, "user", None)
            if user and hasattr(user, "id"):
                identifier = f"user:{user.id}"
            else:
                identifier = f"ip:{client_ip}"
        elif tier == "tenant":
            tenant_id = getattr(request.state, "institute_id", None)
            if not tenant_id:
                user = getattr(request.state, "user", None)
                if user and hasattr(user, "institute_id"):
                    tenant_id = user.institute_id
            if tenant_id:
                identifier = f"tenant:{tenant_id}"
            else:
                identifier = f"ip:{client_ip}"
        else:
            identifier = f"ip:{client_ip}"

        path = request.url.path.rstrip("/")
        rate_key = f"aarambh:ratelimit:{tier}:{identifier}:{path}"

        # 2. Check quota
        allowed, remaining, reset_in = await rate_limiter.check_rate_limit(
            rate_key,
            limit=requests_per_minute,
            window_seconds=60,
        )

        # 3. Add standard RFC headers
        response.headers["X-RateLimit-Limit"] = str(requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                tier=tier,
                identifier=identifier,
                path=path,
                limit=requests_per_minute,
                reset_in=reset_in,
            )
            raise RateLimitExceededError(
                detail=f"Rate limit of {requests_per_minute} requests per minute exceeded. Try again in {reset_in} seconds.",
                retry_after=reset_in,
            )

    return Depends(dependency)
