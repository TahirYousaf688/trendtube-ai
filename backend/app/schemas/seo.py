"""SEO schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SEOGenerateRequest(BaseModel):
    video_id: int
    title_suggestions: Optional[list[str]] = None
    target_keywords: Optional[list[str]] = None


class SEOResponse(BaseModel):
    id: int
    video_id: int
    title: str
    description: Optional[str] = None
    tags: list
    hashtags: list
    chapters: list
    pinned_comment: Optional[str] = None
    community_post: Optional[str] = None
    seo_score: float
    suggestions: list
    is_optimized: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SEOUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    hashtags: Optional[list[str]] = None
    chapters: Optional[list] = None
    pinned_comment: Optional[str] = None
    community_post: Optional[str] = None

