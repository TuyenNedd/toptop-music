"""Tests for JWT token creation and decoding (Story 2.3)."""

import pytest
from jose import JWTError

from app.core.security import create_access_token, decode_access_token


def test_create_and_decode_access_token() -> None:
    """Created token can be decoded with correct payload."""
    token = create_access_token(user_id=42, role="member")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "member"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_invalid_token_raises() -> None:
    """Invalid token raises JWTError."""
    with pytest.raises(JWTError):
        decode_access_token("invalid.token.here")


def test_token_is_string() -> None:
    """Access token is a non-empty string."""
    token = create_access_token(user_id=1, role="admin")
    assert isinstance(token, str)
    assert len(token) > 0
