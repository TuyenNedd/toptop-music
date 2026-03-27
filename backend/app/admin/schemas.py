"""Pydantic schemas for admin module."""

from datetime import datetime

from pydantic import BaseModel, Field


class InviteCodeCreateRequest(BaseModel):
    """Request to generate a new invite code."""

    expiration_days: int = Field(ge=1, le=365, default=7)


class InviteCodeResponse(BaseModel):
    """Invite code data in API responses."""

    id: int
    code: str
    status: str  # "unused", "used", "expired"
    created_at: datetime
    expires_at: datetime
    used_by_username: str | None = None

    model_config = {"from_attributes": True}


class AdminUserResponse(BaseModel):
    """User data for admin views."""

    id: int
    username: str
    email: str
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
