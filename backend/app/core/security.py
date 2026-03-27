"""Security utilities — password hashing, JWT, HMAC signing."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.config import settings

# --- Password hashing ---


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# --- JWT tokens ---


def create_access_token(user_id: int, role: str) -> str:
    """Create a JWT access token with user_id and role."""
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")  # type: ignore[no-any-return]


def decode_access_token(token: str) -> dict[str, object]:
    """Decode and validate a JWT access token. Raises JWTError on failure."""
    payload: dict[str, object] = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
    )
    return payload


# --- Refresh tokens ---


def create_refresh_token() -> str:
    """Generate a cryptographically secure refresh token string."""
    return secrets.token_urlsafe(48)


# --- HMAC signed URLs for audio streaming ---


def create_signed_stream_url(sound_id: int, user_id: int, expires: int) -> str:
    """Generate HMAC-SHA256 signed token for audio streaming."""
    message = f"{sound_id}:{user_id}:{expires}"
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return signature


def verify_signed_stream_url(
    sound_id: int, user_id: int, expires: int, token: str
) -> bool:
    """Verify HMAC-SHA256 signed stream token."""
    expected = create_signed_stream_url(sound_id, user_id, expires)
    return hmac.compare_digest(expected, token)
