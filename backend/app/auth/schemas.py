"""Pydantic schemas for auth module."""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Registration request body."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    invite_code: str | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Username must be alphanumeric with underscores/hyphens only."""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            msg = (
                "Username must contain only letters, numbers, underscores, and hyphens"
            )
            raise ValueError(msg)
        return v


class UserResponse(BaseModel):
    """User data in API responses (never includes password)."""

    id: int
    username: str
    email: str
    role: str
    status: str

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Login request body."""

    username_or_email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Token response after successful login."""

    access_token: str
    token_type: str = "bearer"
