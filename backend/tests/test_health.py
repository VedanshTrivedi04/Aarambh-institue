"""
tests/test_health.py
--------------------
Tests for liveness (/health) and readiness (/ready) endpoints.

These tests run against the full FastAPI app (including middleware stack)
using the test DB session fixture from conftest.py.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestLiveness:
    """GET /api/v1/health — always 200 if the process is alive."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_body(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/health")
        body = response.json()
        assert body["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_has_request_id_header(self, async_client: AsyncClient) -> None:
        """Every response should carry X-Request-ID (injected by RequestIdMiddleware)."""
        response = await async_client.get("/api/v1/health")
        assert "x-request-id" in response.headers


class TestReadiness:
    """GET /api/v1/ready — 200 if DB is reachable; 503 otherwise."""

    @pytest.mark.asyncio
    async def test_ready_returns_200_when_db_ok(self, async_client: AsyncClient) -> None:
        """Assumes the test DB is available (set up by conftest.py fixtures)."""
        response = await async_client.get("/api/v1/ready")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_ready_response_structure(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/ready")
        body = response.json()
        assert "status" in body
        assert "checks" in body
        assert "database" in body["checks"]

    @pytest.mark.asyncio
    async def test_ready_database_check_ok(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/ready")
        body = response.json()
        assert body["checks"]["database"] == "ok"


class TestNotFound:
    """Verify the 404 error contract."""

    @pytest.mark.asyncio
    async def test_unknown_route_returns_404(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/does-not-exist")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_request_id_present_on_error(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/api/v1/does-not-exist")
        assert "x-request-id" in response.headers
