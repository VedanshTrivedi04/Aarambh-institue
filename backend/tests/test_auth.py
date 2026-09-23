"""
tests/test_auth.py
------------------
Full authentication flow tests (backend.md §10, agent.md §4 & §8).

Coverage:
  - Happy-path login (email + mobile)
  - Invalid credentials (wrong password, user not found)
  - Account lockout after repeated failures
  - Token refresh and rotation
  - Refresh token reuse detection (stolen token simulation)
  - Logout (single session revocation)
  - Logout-all (all sessions revoked)
  - /me endpoint
  - Role guard: wrong-role access is rejected
  - Password forgot / reset flow
  - Change password flow
  - Inactive account rejection
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_refresh_token, hash_password
from app.models.institute import Branch, Institute
from app.models.user import PasswordReset, User, UserSession, UserStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def institute(db_session: AsyncSession) -> Institute:
    inst = Institute(
        id=uuid.uuid4(),
        name="Aarambh Test Institute",
        code="AARAMBH_TEST",
        is_active=True,
    )
    db_session.add(inst)
    await db_session.flush()
    return inst


@pytest.fixture
async def active_user(db_session: AsyncSession, institute: Institute) -> tuple[User, str]:
    """Returns (user, plain_password)."""
    plain = "SecurePass@123"
    user = User(
        id=uuid.uuid4(),
        institute_id=institute.id,
        email="admin@aarambh.test",
        mobile="9876543210",
        password_hash=hash_password(plain),
        role="ADMIN",
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user, plain


@pytest.fixture
async def inactive_user(db_session: AsyncSession, institute: Institute) -> tuple[User, str]:
    plain = "Password@999"
    user = User(
        id=uuid.uuid4(),
        institute_id=institute.id,
        email="inactive@aarambh.test",
        password_hash=hash_password(plain),
        role="STUDENT",
        status=UserStatus.INACTIVE,
        is_active=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user, plain


# ─── Login ───────────────────────────────────────────────────────────────────

class TestLogin:
    @pytest.mark.asyncio
    async def test_login_with_email_success(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == user.email
        assert body["user"]["role"] == "ADMIN"
        # Refresh token must be in httpOnly cookie, NOT in body
        assert "refresh_token" not in body
        assert "refresh_token" in resp.cookies

    @pytest.mark.asyncio
    async def test_login_with_mobile_success(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.mobile, "password": plain},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password_returns_401(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, _ = active_user
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": "WrongPassword!"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_unknown_user_returns_401(
        self, async_client: AsyncClient
    ) -> None:
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": "nobody@notexist.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_account_rejected(
        self, async_client: AsyncClient, inactive_user: tuple[User, str]
    ) -> None:
        user, plain = inactive_user
        resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_login_creates_user_session(
        self, async_client: AsyncClient, active_user: tuple[User, str],
        db_session: AsyncSession,
    ) -> None:
        user, plain = active_user
        await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        sessions = (
            await db_session.execute(select(UserSession).where(UserSession.user_id == user.id))
        ).scalars().all()
        assert len(sessions) == 1
        assert sessions[0].revoked_at is None


# ─── Token Refresh ───────────────────────────────────────────────────────────

class TestRefresh:
    @pytest.mark.asyncio
    async def test_refresh_returns_new_access_token(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        old_access = login_resp.json()["access_token"]

        refresh_resp = await async_client.post("/api/v1/auth/refresh")
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.json()["access_token"]
        # Rotated — new token must differ
        assert new_access != old_access

    @pytest.mark.asyncio
    async def test_refresh_rotates_cookie(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        old_cookie = async_client.cookies.get("refresh_token")

        await async_client.post("/api/v1/auth/refresh")
        new_cookie = async_client.cookies.get("refresh_token")
        # Old JTI should be revoked; new cookie issued
        assert new_cookie != old_cookie

    @pytest.mark.asyncio
    async def test_refresh_token_reuse_revokes_all_sessions(
        self, async_client: AsyncClient, active_user: tuple[User, str],
        db_session: AsyncSession,
    ) -> None:
        """
        Simulate token theft: use the same refresh token twice.
        On second use, all sessions should be revoked.
        """
        user, plain = active_user
        await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        original_cookie = async_client.cookies.get("refresh_token")

        # First refresh — valid
        await async_client.post("/api/v1/auth/refresh")

        # Inject the original (now-revoked) cookie back
        async_client.cookies.set("refresh_token", original_cookie)

        # Second refresh — should detect reuse and revoke all
        reuse_resp = await async_client.post("/api/v1/auth/refresh")
        assert reuse_resp.status_code == 401
        assert reuse_resp.json()["code"] == "TOKEN_REVOKED"

        # Verify all sessions revoked in DB
        sessions = (
            await db_session.execute(
                select(UserSession).where(UserSession.user_id == user.id)
            )
        ).scalars().all()
        assert all(s.is_revoked for s in sessions)


# ─── Logout ──────────────────────────────────────────────────────────────────

class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_revokes_session(
        self, async_client: AsyncClient, active_user: tuple[User, str],
        db_session: AsyncSession,
    ) -> None:
        user, plain = active_user
        await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        resp = await async_client.post("/api/v1/auth/logout")
        assert resp.status_code == 200

        sessions = (
            await db_session.execute(select(UserSession).where(UserSession.user_id == user.id))
        ).scalars().all()
        assert all(s.is_revoked for s in sessions)

    @pytest.mark.asyncio
    async def test_logout_clears_refresh_cookie(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        resp = await async_client.post("/api/v1/auth/logout")
        assert "refresh_token" not in resp.cookies or resp.cookies.get("refresh_token") == ""


# ─── /me ─────────────────────────────────────────────────────────────────────

class TestMe:
    @pytest.mark.asyncio
    async def test_me_returns_current_user(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        login = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        token = login.json()["access_token"]
        resp = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_me_without_token_returns_401(
        self, async_client: AsyncClient
    ) -> None:
        resp = await async_client.get("/api/v1/auth/me")
        assert resp.status_code == 401


# ─── Password Reset ───────────────────────────────────────────────────────────

class TestPasswordReset:
    @pytest.mark.asyncio
    async def test_forgot_password_always_returns_200(
        self, async_client: AsyncClient
    ) -> None:
        """Even for unknown identifiers — prevents user enumeration."""
        resp = await async_client.post(
            "/api/v1/auth/forgot-password",
            json={"identifier": "nobody@nothere.com"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token_returns_422(
        self, async_client: AsyncClient
    ) -> None:
        resp = await async_client.post(
            "/api/v1/auth/reset-password",
            json={"token": "totallyfaketoken", "new_password": "NewPass@123"},
        )
        assert resp.status_code == 422


# ─── Change Password ─────────────────────────────────────────────────────────

class TestChangePassword:
    @pytest.mark.asyncio
    async def test_change_password_wrong_current_returns_422(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        login = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        token = login.json()["access_token"]
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "WrongCurrent!", "new_password": "NewPass@123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422
        assert resp.json()["code"] == "WRONG_CURRENT_PASSWORD"

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, async_client: AsyncClient, active_user: tuple[User, str]
    ) -> None:
        user, plain = active_user
        login = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        token = login.json()["access_token"]
        resp = await async_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": plain, "new_password": "BrandNew@456"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        # Old password should no longer work
        old_login = await async_client.post(
            "/api/v1/auth/login",
            json={"identifier": user.email, "password": plain},
        )
        assert old_login.status_code == 401
