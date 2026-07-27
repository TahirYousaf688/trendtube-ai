"""Analytics schemas."""

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    id: int
    video_id: int
    views: int
    watch_time_minutes: float
    average_view_duration_seconds: float
    ctr: float
    impressions: int
    likes: int
    dislikes: int
    comments: int
    shares: int
    subscribers_gained: int
    subscribers_lost: int
    estimated_revenue_usd: float
    rpm: float
    audience_retention: Dict[str, Any]
    traffic_sources: Dict[str, Any]
    top_countries: list
    top_keywords: list
    demographics: Dict[str, Any]
    recorded_at: date

    class Config:
        from_attributes = True


class ChannelAnalyticsResponse(BaseModel):
    id: int
    channel_id: int
    total_views: int
    total_watch_time_minutes: float
    total_subscribers: int
    total_videos: int
    estimated_revenue_usd: float
    recorded_at: date

    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    total_views: int
    total_watch_time: float
    total_subscribers: int
    total_estimated_revenue: float
    average_ctr: float
    top_videos: list[dict]
    views_trend: list[dict]
    subscriber_trend: list[dict]
    revenue_trend: list[dict]


class AnalyticsTimeRange(BaseModel):
    start_date: date
    end_date: date

