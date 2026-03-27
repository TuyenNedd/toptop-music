"""Pydantic schemas for sounds module."""


from pydantic import BaseModel


class SoundResponse(BaseModel):
    """Sound data in API responses."""

    id: int
    tiktok_sound_id: str
    title: str
    artist: str
    cover_url: str | None
    duration: int
    usage_count: int
    trend_rank: int | None
    is_original: bool
    cached: bool

    model_config = {"from_attributes": True}


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total: int
    has_next: bool
