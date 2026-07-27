"""Analytics routes."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Analytics, ChannelAnalytics, User, Video
from app.schemas.analytics import (
    AnalyticsResponse,
    AnalyticsSummaryResponse,
    ChannelAnalyticsResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/videos/{video_id}", response_model=list[AnalyticsResponse])
def get_video_analytics(
    video_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get analytics for a specific video."""
    start_date = date.today() - timedelta(days=days)
    analytics = (
        db.query(Analytics)
        .filter(
            Analytics.video_id == video_id,
            Analytics.recorded_at >= start_date,
        )
        .order_by(Analytics.recorded_at.desc())
        .all()
    )
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analytics found for this video")
    return [AnalyticsResponse.model_validate(a) for a in analytics]


@router.get("/channels/{channel_id}", response_model=list[ChannelAnalyticsResponse])
def get_channel_analytics(
    channel_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get analytics for a channel."""
    start_date = date.today() - timedelta(days=days)
    analytics = (
        db.query(ChannelAnalytics)
        .filter(
            ChannelAnalytics.channel_id == channel_id,
            ChannelAnalytics.recorded_at >= start_date,
        )
        .order_by(ChannelAnalytics.recorded_at.desc())
        .all()
    )
    return [ChannelAnalyticsResponse.model_validate(a) for a in analytics]


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analytics summary across all channels."""
    # Get all channels for user
    channels = db.query(Video).filter(Video.channel_id.in_(
        db.query(Video.channel_id).filter(Video.id.isnot(None))
    ))

    # Aggregate metrics
    total_views = db.query(func.sum(Analytics.views)).scalar() or 0
    total_watch_time = db.query(func.sum(Analytics.watch_time_minutes)).scalar() or 0
    total_revenue = db.query(func.sum(Analytics.estimated_revenue_usd)).scalar() or 0
    avg_ctr = db.query(func.avg(Analytics.ctr)).scalar() or 0

    return AnalyticsSummaryResponse(
        total_views=int(total_views),
        total_watch_time=float(total_watch_time),
        total_subscribers=0,
        total_estimated_revenue=float(total_revenue),
        average_ctr=float(avg_ctr),
        top_videos=[],
        views_trend=[],
        subscriber_trend=[],
        revenue_trend=[],
    )

