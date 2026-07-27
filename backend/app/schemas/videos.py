"""Video schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class VideoCreateRequest(BaseModel):
    channel_id: int
    script_id: int
    topic_id: Optional[int] = None
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    privacy_status: str = "unlisted"
    made_for_kids: bool = False
    category_id: Optional[int] = None
    language: str = "en"
    is_short: bool = False
    publish_at: Optional[datetime] = None


class VideoGenerationRequest(BaseModel):
    topic: str
    style: str = "educational"
    channel_id: int
    duration_seconds: int = 600
    resolution: str = "1080p"
    language: str = "en"
    voice_id: Optional[int] = None
    background_music: bool = True
    auto_subtitles: bool = True
    generate_thumbnail: bool = True
    optimize_seo: bool = True
    publish_immediately: bool = False


class VideoResponse(BaseModel):
    id: int
    channel_id: int
    script_id: Optional[int] = None
    topic_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    duration_seconds: int
    resolution: str
    privacy_status: str
    is_short: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    privacy_status: Optional[str] = None
    category_id: Optional[int] = None
    made_for_kids: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class VideoListResponse(BaseModel):
    items: list[VideoResponse]
    total: int
    page: int = 1
    page_size: int = 20


class VideoPublishRequest(BaseModel):
    video_id: int
    privacy_status: str = "public"
    publish_at: Optional[datetime] = None
    notify_subscribers: bool = True


class VideoGenerationResponse(BaseModel):
    video_id: int
    workflow_id: int
    status: str
    summary: str

