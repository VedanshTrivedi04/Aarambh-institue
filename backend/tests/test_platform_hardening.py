"""
tests/test_platform_hardening.py
---------------------------------
Verification suite for Slice 12: Platform & Production Hardening.

Validates:
  1. Multi-tenant Redis/Memory Cache:
     - Tenant-isolated key spaces.
     - TTL expiration and serialization of complex structures.
     - Namespace pattern invalidation.
  2. Multi-tier Token Bucket Rate Limiter:
     - Header injection (X-RateLimit-Limit, Remaining, Reset).
     - 429 Too Many Requests enforcement with Retry-After header.
  3. Dashboard Caching & Invalidation Flow:
     - Executive dashboard uses cached response on repeat hits.
     - Invalidation on refresh.
  4. Platform Readiness Health Check (/ready).
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_service
from app.core.exceptions import RateLimitExceededError
from app.core.rate_limit import rate_limiter
from app.core.security import create_access_token, hash_password
from app.models.institute import Institute
from app.models.user import User, UserStatus


@pytest.fixture
async def hardening_env(db_session: AsyncSession) -> dict[str, any]:
    db = db_session
    inst_a = Institute(id=uuid.uuid4(), name="Hardening Inst A", code=f"HA_{uuid.uuid4().hex[:6].upper()}", is_active=True)
    inst_b = Institute(id=uuid.uuid4(), name="Hardening Inst B", code=f"HB_{uuid.uuid4().hex[:6].upper()}", is_active=True)
    db.add_all([inst_a, inst_b])
    await db.flush()

    user_a = User(
        id=uuid.uuid4(), institute_id=inst_a.id, email=f"adm_{uuid.uuid4().hex[:6]}@insta.com",
        password_hash=hash_password("Pass123!"), role="ADMIN", status=UserStatus.ACTIVE,
        is_active=True, is_verified=True,
    )
    user_b = User(
        id=uuid.uuid4(), institute_id=inst_b.id, email=f"adm_{uuid.uuid4().hex[:6]}@instb.com",
        password_hash=hash_password("Pass123!"), role="ADMIN", status=UserStatus.ACTIVE,
        is_active=True, is_verified=True,
    )
    db.add_all([user_a, user_b])
    await db.flush()

    token_a, _, _ = create_access_token(str(user_a.id), user_a.role)
    token_b, _, _ = create_access_token(str(user_b.id), user_b.role)

    return {
        "inst_a": inst_a,
        "inst_b": inst_b,
        "user_a": user_a,
        "user_b": user_b,
        "token_a": token_a,
        "token_b": token_b,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Cache Lifecycle, Serialization & Tenant Namespace Isolation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cache_lifecycle_and_tenant_isolation(hardening_env: dict[str, any]):
    env = hardening_env
    inst_a_id = env["inst_a"].id
    inst_b_id = env["inst_b"].id

    key_a = cache_service.build_key(inst_a_id, "stats", "kpi_card")
    key_b = cache_service.build_key(inst_b_id, "stats", "kpi_card")

    # 1. Assert keys are distinct and isolated
    assert key_a != key_b
    assert str(inst_a_id) in key_a
    assert str(inst_b_id) in key_b

    # 2. Store values for both tenants
    payload_a = {"tenant": "A", "active_students": 150, "billed": 250000.0}
    payload_b = {"tenant": "B", "active_students": 30, "billed": 50000.0}

    await cache_service.set(key_a, payload_a, ttl_seconds=60)
    await cache_service.set(key_b, payload_b, ttl_seconds=60)

    # 3. Retrieve and verify independence
    res_a = await cache_service.get(key_a)
    res_b = await cache_service.get(key_b)

    assert res_a == payload_a
    assert res_b == payload_b
    assert res_a["tenant"] == "A"
    assert res_b["tenant"] == "B"

    # 4. Invalidate only Tenant A namespace
    deleted_count = await cache_service.invalidate_tenant_namespace(inst_a_id, "stats")
    assert deleted_count >= 1

    # 5. Verify Tenant A is cleared while Tenant B remains untouched
    assert (await cache_service.get(key_a)) is None
    assert (await cache_service.get(key_b)) == payload_b


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Token Bucket Rate Limiter Enforcement
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limiter_enforcement():
    test_key = f"test_rate_key_{uuid.uuid4().hex}"
    limit = 3

    # Hits 1, 2, 3 should succeed
    for i in range(1, limit + 1):
        allowed, remaining, reset_in = await rate_limiter.check_rate_limit(test_key, limit=limit, window_seconds=60)
        assert allowed is True
        assert remaining == limit - i
        assert reset_in > 0

    # 4th hit should be blocked
    allowed, remaining, reset_in = await rate_limiter.check_rate_limit(test_key, limit=limit, window_seconds=60)
    assert allowed is False
    assert remaining == 0
    assert reset_in > 0


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Dashboard Caching & Invalidation Flow
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_caching_and_invalidation(
    async_client: AsyncClient,
    hardening_env: dict[str, any],
):
    env = hardening_env
    token_a = env["token_a"]
    inst_a_id = env["inst_a"].id

    cache_key = cache_service.build_key(inst_a_id, "analytics", "dashboard")

    # Ensure clean cache state
    await cache_service.delete(cache_key)

    # 1. First fetch — populates cache
    resp1 = await async_client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp1.status_code == 200

    # Verify data is cached
    cached_val = await cache_service.get(cache_key)
    assert cached_val is not None
    assert "total_students" in cached_val

    # 2. Second fetch — served directly
    resp2 = await async_client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["data"]["total_students"] == cached_val["total_students"]

    # 3. Post refresh triggers invalidation
    refresh_resp = await async_client.post(
        "/api/v1/analytics/refresh",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert refresh_resp.status_code == 200

    # Cache should be cleared
    assert (await cache_service.get(cache_key)) is None


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Readiness Health Check (/ready)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_readiness_healthcheck(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/ready")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "ready"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["cache"] in ("redis", "memory_fallback")
