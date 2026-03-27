"""Tests for core security — password hashing (Story 2.1)."""

from app.core.security import hash_password, verify_password


def test_hash_password_returns_bcrypt_hash() -> None:
    """hash_password returns a bcrypt hash string."""
    hashed = hash_password("testpassword")
    assert hashed.startswith("$2b$")
    assert len(hashed) == 60


def test_verify_password_correct() -> None:
    """verify_password returns True for correct password."""
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_incorrect() -> None:
    """verify_password returns False for wrong password."""
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_hash_uses_12_rounds() -> None:
    """bcrypt hash uses 12 rounds (cost factor)."""
    hashed = hash_password("test")
    # bcrypt format: $2b$12$...
    assert "$2b$12$" in hashed
