"""
app/core/cache.py
-----------------
Multi-tenant Redis caching service with resilient in-memory fallback,
structured key namespacing, pattern-based invalidation, and automatic
serialization of UUIDs, datetimes, and Pydantic models.
"""

from __future__ import annotations

import asyncio
import functools
import time
import uuid
from datetime import date, datetime
from typing import Any, Callable

import orjson
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)


def _orjson_default(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if hasattr(obj, "value"):
        return obj.value
    raise TypeError(f"Type is not JSON serializable: {type(obj)}")


class _MemoryCache:
    """Thread-safe in-memory cache with TTL expiration for dev/testing or Redis failure fallback."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> str | None:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            val, expire_at = entry
            if time.monotonic() > expire_at:
                del self._store[key]
                return None
            return val

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        async with self._lock:
            expire_at = time.monotonic() + ttl_seconds
            self._store[key] = (value, expire_at)

    async def delete(self, key: str) -> bool:
        async with self._lock:
            return self._store.pop(key, None) is not None

    async def delete_pattern(self, pattern: str) -> int:
        """Simple prefix/wildcard match for in-memory store."""
        prefix = pattern.replace("*", "")
        deleted = 0
        async with self._lock:
            keys_to_del = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_del:
                del self._store[k]
                deleted += 1
        return deleted

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()


class CacheService:
    """
    Tenant-aware cache abstraction.
    Uses Redis if available, otherwise seamlessly falls back to memory cache.
    """

    def __init__(self) -> None:
        self._memory = _MemoryCache()

    def _get_redis(self) -> Any:
        try:
            from app.core.lifespan import redis_client
            return redis_client
        except Exception:
            return None

    def build_key(
        self,
        tenant_id: uuid.UUID | str,
        namespace: str,
        subkey: str,
    ) -> str:
        """Format: aarambh:{tenant_id}:{namespace}:{subkey}"""
        return f"aarambh:{tenant_id}:{namespace}:{subkey}"

    async def get(self, key: str) -> Any | None:
        """Retrieve and deserialize value from cache."""
        redis = self._get_redis()
        raw_val: str | None = None
        if redis:
            try:
                raw_val = await redis.get(key)
            except Exception as exc:
                logger.warning("Redis get failed, falling back to memory cache", key=key, error=str(exc))
                raw_val = await self._memory.get(key)
        else:
            raw_val = await self._memory.get(key)

        if raw_val is None:
            return None

        try:
            return orjson.loads(raw_val)
        except Exception as exc:
            logger.error("Failed to deserialize cached value", key=key, error=str(exc))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> bool:
        """Serialize and store value in cache with TTL."""
        try:
            raw_val = orjson.dumps(value, default=_orjson_default).decode("utf-8")
        except Exception as exc:
            logger.error("Failed to serialize cache value", key=key, error=str(exc))
            return False

        redis = self._get_redis()
        if redis:
            try:
                await redis.set(key, raw_val, ex=ttl_seconds)
                return True
            except Exception as exc:
                logger.warning("Redis set failed, falling back to memory cache", key=key, error=str(exc))
                await self._memory.set(key, raw_val, ttl_seconds)
                return True
        else:
            await self._memory.set(key, raw_val, ttl_seconds)
            return True

    async def delete(self, key: str) -> bool:
        """Delete specific key from cache."""
        redis = self._get_redis()
        deleted = False
        if redis:
            try:
                count = await redis.delete(key)
                deleted = bool(count)
            except Exception as exc:
                logger.warning("Redis delete failed", key=key, error=str(exc))
                deleted = await self._memory.delete(key)
        else:
            deleted = await self._memory.delete(key)
        return deleted

    async def delete_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        redis = self._get_redis()
        total_deleted = 0
        if redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        del_count = await redis.delete(*keys)
                        total_deleted += del_count
                    if cursor == 0:
                        break
            except Exception as exc:
                logger.warning("Redis scan/delete failed, falling back to memory cache", pattern=pattern, error=str(exc))
                total_deleted = await self._memory.delete_pattern(pattern)
        else:
            total_deleted = await self._memory.delete_pattern(pattern)

        return total_deleted

    async def invalidate_tenant_namespace(
        self,
        tenant_id: uuid.UUID | str,
        namespace: str,
    ) -> int:
        """Clear all cached entries for a specific tenant and feature namespace."""
        pattern = f"aarambh:{tenant_id}:{namespace}:*"
        count = await self.delete_pattern(pattern)
        logger.debug("Invalidated tenant cache namespace", tenant_id=str(tenant_id), namespace=namespace, keys_cleared=count)
        return count

    def is_redis_active(self) -> bool:
        return self._get_redis() is not None


# Global singleton instance
cache_service = CacheService()


def cached(
    namespace: str,
    ttl_seconds: int = 300,
    key_func: Callable[..., str] | None = None,
):
    """
    Decorator for async service or API functions.
    Expects tenant_id or institute_id in keyword arguments.
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            tenant_id = kwargs.get("institute_id") or kwargs.get("tenant_id")
            if not tenant_id:
                # Bypass cache if tenant cannot be derived
                return await func(*args, **kwargs)

            subkey = key_func(*args, **kwargs) if key_func else func.__name__
            cache_key = cache_service.build_key(tenant_id, namespace, subkey)

            cached_data = await cache_service.get(cache_key)
            if cached_data is not None:
                return cached_data

            result = await func(*args, **kwargs)
            if result is not None:
                await cache_service.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator
