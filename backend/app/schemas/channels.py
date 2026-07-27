"""Channel schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class YouTubeAuthRequest(BaseModel):
    authorization_code: str


class ChannelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    youtube_handle: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ChannelUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ChannelResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    platform: str
    youtube_channel_id: Optional[str] = None
    youtube_handle: Optional[str] = None
    avatar_url: Optional[str] = None
    subscriber_count: int
    video_count: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChannelListResponse(BaseModel):
    items: list[ChannelResponse]
    total: int


class PlaylistResponse(BaseModel):
    id: int
    channel_id: int
    youtube_playlist_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    is_public: bool

    class Config:
        from_attributes = True


class PlaylistCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = True

