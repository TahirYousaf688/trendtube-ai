"""Trend discovery routes."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import TrendSource, TrendingTopic, User
from app.schemas.trends import (
    TrendDiscoveryRequest,
    TrendRankingResponse,
    TrendSourceResponse,
    TrendSourceUpdateRequest,
    TrendingTopicListResponse,
    TrendingTopicResponse,
)

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/sources", response_model=list[TrendSourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """List all trend sources."""
    sources = db.query(TrendSource).all()
    return [TrendSourceResponse.model_validate(s) for s in sources]


@router.put("/sources/{source_id}", response_model=TrendSourceResponse)
def update_source(
    source_id: int,
    payload: TrendSourceUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update a trend source configuration."""
    source = db.query(TrendSource).filter(TrendSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trend source not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return TrendSourceResponse.model_validate(source)


@router.get("", response_model=TrendingTopicListResponse)
def list_trends(
    topic_type: Optional[str] = Query(None, description="Filter by topic type"),
    min_score: int = Query(0, description="Minimum trend score"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List trending topics with optional filters."""
    query = db.query(TrendingTopic)

    if topic_type:
        query = query.filter(TrendingTopic.topic_type == topic_type)
    if min_score > 0:
        query = query.filter(TrendingTopic.score >= min_score)

    total = query.count()
    topics = query.order_by(TrendingTopic.score.desc()).offset(offset).limit(limit).all()

    return TrendingTopicListResponse(
        items=[TrendingTopicResponse.model_validate(t) for t in topics],
        total=total,
        page=(offset // limit) + 1,
        page_size=limit,
    )


@router.get("/{topic_id}", response_model=TrendingTopicResponse)
def get_trend(topic_id: int, db: Session = Depends(get_db)):
    """Get a specific trending topic."""
    topic = db.query(TrendingTopic).filter(TrendingTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trending topic not found")
    return TrendingTopicResponse.model_validate(topic)


@router.post("/discover", response_model=list[TrendRankingResponse])
def discover_trends(
    payload: TrendDiscoveryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger trend discovery from configured sources."""
    # In production, this would trigger the Trend Agent
    # For now, return mock ranked results
    mock_topics = []
    sources = ["Google Trends", "YouTube Trending", "Reddit", "Hacker News"]
    categories = ["AI", "Technology", "Finance", "Science"]

    for i, source in enumerate(sources[:3]):
        topic = TrendingTopic(
            title=f"Emerging trend in {categories[i]}: AI-driven content creation",
            topic_type=categories[i].lower(),
            source_name=source,
            score=85 - i * 10,
            search_volume=50000 - i * 10000,
            engagement_rate=0.75 - i * 0.1,
            growth_rate=0.25 + i * 0.05,
            virality_score=0.8 - i * 0.1,
            is_processed=False,
            discovered_at=datetime.now(timezone.utc),
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        mock_topics.append(topic)

    results = []
    for idx, topic in enumerate(mock_topics):
        results.append(
            TrendRankingResponse(
                topic=TrendingTopicResponse.model_validate(topic),
                rank=idx + 1,
                recommendation="High potential for video content" if idx == 0 else "Consider for future content",
                confidence=0.9 - idx * 0.1,
            )
        )
    return results


@router.post("/{topic_id}/process", response_model=TrendingTopicResponse)
def process_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a trending topic as processed and trigger research workflow."""
    topic = db.query(TrendingTopic).filter(TrendingTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trending topic not found")

    topic.is_processed = True
    db.commit()
    db.refresh(topic)
    return TrendingTopicResponse.model_validate(topic)

