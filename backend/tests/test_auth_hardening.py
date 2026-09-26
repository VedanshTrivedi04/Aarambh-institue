"""
tests/test_auth_hardening.py
----------------------------
Regression tests for authentication hardening. These are DB-free on purpose:
the shared test client overrides get_db without the production rollback-on-error
behaviour, so anything that depends on "was this committed before the exception
propagated" has to be asserted directly on the service.

Covers:
  - failed-login counters are committed (lockout used to be silently discarded)
  - lock after N failures; counter resets once a lock has expired
  - unknown users still pay the password-hash cost (no timing enumeration)
  - account status is not revealed before the password is verified
  - X-Forwarded-For is only trusted TRUSTED_PROXY_COUNT hops from the right
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request

from app.core import client_ip
from app.core.exceptions import AccountInactiveError, InvalidCredentialsError
from app.core.security import hash_password
from app.models.user import UserStatus
from app.services import auth_service

PASSWORD = "SecurePass@123"


def _user(**overrides):
    base = dict(
        id=uuid.uuid4(),
        password_hash=hash_password(PASSWORD),
        status=UserStatus.ACTIVE,
        failed_login_attempts=0,
        locked_until=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _db_returning(user):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    return db


# ─── Failed-attempt tracking ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_failed_attempt_is_committed_before_error_propagates() -> None:
    db, user = AsyncMock(), _user()
    await auth_service._record_failed_attempt(db, user)
    assert user.failed_login_attempts == 1
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_account_locks_after_max_failed_attempts() -> None:
    db = AsyncMock()
    user = _user(failed_login_attempts=auth_service._MAX_FAILED_ATTEMPTS - 1)
    await auth_service._record_failed_attempt(db, user)
    assert user.locked_until is not None and user.locked_until > datetime.now(UTC)


@pytest.mark.asyncio
async def test_wrong_password_records_failure_and_raises() -> None:
    user = _user()
    db = _db_returning(user)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(db, "x@y.test", "wrong-password")
    assert user.failed_login_attempts == 1
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_locked_account_rejects_correct_password() -> None:
    user = _user(failed_login_attempts=5, locked_until=datetime.now(UTC) + timedelta(minutes=10))
    with pytest.raises(AccountInactiveError) as exc:
        await auth_service.authenticate_user(_db_returning(user), "x@y.test", PASSWORD)
    assert exc.value.code == "ACCOUNT_LOCKED"


@pytest.mark.asyncio
async def test_expired_lock_starts_a_fresh_window() -> None:
    user = _user(failed_login_attempts=5, locked_until=datetime.now(UTC) - timedelta(minutes=1))
    db = _db_returning(user)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(db, "x@y.test", "wrong-password")
    # One typo after a lock expires must not re-lock the account immediately.
    assert user.failed_login_attempts == 1
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_successful_login_after_expired_lock_clears_state() -> None:
    user = _user(failed_login_attempts=5, locked_until=datetime.now(UTC) - timedelta(minutes=1))
    result = await auth_service.authenticate_user(_db_returning(user), "x@y.test", PASSWORD)
    assert result is user
    assert user.failed_login_attempts == 0 and user.locked_until is None


# ─── Enumeration resistance ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unknown_user_still_spends_hash_time(monkeypatch: pytest.MonkeyPatch) -> None:
    burn = MagicMock()
    monkeypatch.setattr(auth_service, "burn_password_check", burn)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(_db_returning(None), "nobody@x.test", "whatever")
    burn.assert_called_once_with("whatever")


@pytest.mark.asyncio
async def test_inactive_status_not_revealed_without_valid_password() -> None:
    user = _user(status=UserStatus.INACTIVE)
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(_db_returning(user), "x@y.test", "wrong-password")


@pytest.mark.asyncio
async def test_inactive_status_reported_after_valid_password() -> None:
    user = _user(status=UserStatus.INACTIVE)
    with pytest.raises(AccountInactiveError):
        await auth_service.authenticate_user(_db_returning(user), "x@y.test", PASSWORD)


# ─── Client IP resolution ────────────────────────────────────────────────────

def _request(xff: str | None, peer: str = "10.0.0.1") -> Request:
    headers = [(b"x-forwarded-for", xff.encode())] if xff is not None else []
    return Request({"type": "http", "headers": headers, "client": (peer, 1234)})


def _trust(monkeypatch: pytest.MonkeyPatch, hops: int) -> None:
    monkeypatch.setattr(client_ip, "get_settings", lambda: SimpleNamespace(TRUSTED_PROXY_COUNT=hops))


def test_forwarded_header_ignored_when_no_proxy_trusted(monkeypatch: pytest.MonkeyPatch) -> None:
    _trust(monkeypatch, 0)
    assert client_ip.get_client_ip(_request("6.6.6.6")) == "10.0.0.1"


def test_spoofed_leftmost_entry_is_not_used(monkeypatch: pytest.MonkeyPatch) -> None:
    _trust(monkeypatch, 1)
    # Client sent "1.2.3.4"; the trusted proxy appended the real address.
    assert client_ip.get_client_ip(_request("1.2.3.4, 203.0.113.9")) == "203.0.113.9"


def test_two_trusted_hops(monkeypatch: pytest.MonkeyPatch) -> None:
    _trust(monkeypatch, 2)
    assert client_ip.get_client_ip(_request("spoofed, 203.0.113.9, 172.16.0.5")) == "203.0.113.9"


def test_falls_back_to_peer_without_header(monkeypatch: pytest.MonkeyPatch) -> None:
    _trust(monkeypatch, 1)
    assert client_ip.get_client_ip(_request(None)) == "10.0.0.1"
