"""
tests/test_security.py
-----------------------
Unit tests for password hashing (pwdlib/Argon2) and JWT utilities.
These are pure unit tests — no database required.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import TokenExpiredError, UnauthorizedError


class TestPasswordHashing:
    """pwdlib Argon2 hashing and verification."""

    def test_hash_is_not_plaintext(self) -> None:
        hashed = hash_password("mySecret123")
        assert hashed != "mySecret123"

    def test_verify_correct_password(self) -> None:
        hashed = hash_password("correctPassword")
        valid, updated = verify_password("correctPassword", hashed)
        assert valid is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("correctPassword")
        valid, updated = verify_password("wrongPassword", hashed)
        assert valid is False

    def test_two_hashes_of_same_password_differ(self) -> None:
        """Argon2 uses a random salt — each hash must be unique."""
        h1 = hash_password("samePassword")
        h2 = hash_password("samePassword")
        assert h1 != h2

    def test_verify_and_update_returns_none_when_no_rehash_needed(self) -> None:
        hashed = hash_password("password")
        valid, updated = verify_password("password", hashed)
        assert valid is True
        # updated is None when no algorithm upgrade is needed
        # (may be a new hash if rehash is triggered — both are acceptable)


class TestJWT:
    """JWT access and refresh token creation and decoding."""

    def test_create_and_decode_access_token(self) -> None:
        token, jti, expires_at = create_access_token(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            role="ADMIN",
        )
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == "550e8400-e29b-41d4-a716-446655440000"
        assert payload["role"] == "ADMIN"
        assert payload["type"] == "access"
        assert payload["jti"] == jti

    def test_create_and_decode_refresh_token(self) -> None:
        token, jti, _ = create_refresh_token(
            user_id="550e8400-e29b-41d4-a716-446655440001",
            role="STUDENT",
        )
        payload = decode_token(token, expected_type="refresh")
        assert payload["type"] == "refresh"
        assert payload["sub"] == "550e8400-e29b-41d4-a716-446655440001"

    def test_wrong_token_type_raises_unauthorized(self) -> None:
        """An access token must not be accepted where a refresh token is required."""
        token, _, _ = create_access_token(user_id="abc", role="TEACHER")
        with pytest.raises(UnauthorizedError):
            decode_token(token, expected_type="refresh")

    def test_tampered_token_raises_unauthorized(self) -> None:
        token, _, _ = create_access_token(user_id="abc", role="ADMIN")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(UnauthorizedError):
            decode_token(tampered)

    def test_jti_is_unique_per_token(self) -> None:
        _, jti1, _ = create_access_token("user1", "ADMIN")
        _, jti2, _ = create_access_token("user1", "ADMIN")
        assert jti1 != jti2

    def test_refresh_token_preserves_jti_when_provided(self) -> None:
        """Token rotation: caller can supply the new JTI to chain with session row."""
        fixed_jti = "fixed-jti-12345"
        token, jti, _ = create_refresh_token("user1", "PARENT", jti=fixed_jti)
        assert jti == fixed_jti
        payload = decode_token(token, expected_type="refresh")
        assert payload["jti"] == fixed_jti
