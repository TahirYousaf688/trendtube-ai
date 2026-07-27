"""Trend discovery schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TrendSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    enabled: bool
    fetch_interval_minutes: int
    last_fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrendSourceUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    fetch_interval_minutes: Optional[int] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class TrendingTopicResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    topic_type: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    score: int
    search_volume: int
    engagement_rate: float
    competition_level: float
    growth_rate: float
    virality_score: float
    is_processed: bool
    discovered_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TrendingTopicListResponse(BaseModel):
    items: list[TrendingTopicResponse]
    total: int
    page: int = 1
    page_size: int = 20


class TrendDiscoveryRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: ["all"])
    categories: list[str] = Field(default_factory=lambda: ["all"])
    min_score: int = 50
    max_results: int = 20


class TrendRankingResponse(BaseModel):
    topic: TrendingTopicResponse
    rank: int
    recommendation: str
    confidence: float

