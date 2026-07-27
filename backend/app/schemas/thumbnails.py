"""Thumbnail schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ThumbnailGenerateRequest(BaseModel):
    video_id: int
    prompt: Optional[str] = None
    style: str = "modern"
    count: int = 3


class ThumbnailResponse(BaseModel):
    id: int
    video_id: int
    storage_key: str
    url: Optional[str] = None
    width: int
    height: int
    ctr_score: float
    is_selected: bool
    is_a_b_test: bool
    generation_prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ThumbnailListResponse(BaseModel):
    items: list[ThumbnailResponse]
    total: int


class ThumbnailSelectRequest(BaseModel):
    thumbnail_id: int


class ThumbnailABTestRequest(BaseModel):
    thumbnail_a_id: int
    thumbnail_b_id: int
    duration_hours: int = 24

