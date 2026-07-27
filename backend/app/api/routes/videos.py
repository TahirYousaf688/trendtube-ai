"""Video generation and management routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Channel, Script, TrendingTopic, User, Video, WorkflowRun
from app.schemas.videos import (
    VideoCreateRequest,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoListResponse,
    VideoPublishRequest,
    VideoResponse,
    VideoUpdateRequest,
)

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("", response_model=VideoListResponse)
def list_videos(
    channel_id: int | None = None,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List videos with filters."""
    query = db.query(Video)
    if channel_id:
        query = query.filter(Video.channel_id == channel_id)
    if status_filter:
        query = query.filter(Video.status == status_filter)

    total = query.count()
    videos = query.order_by(Video.created_at.desc()).offset(offset).limit(limit).all()

    return VideoListResponse(
        items=[VideoResponse.model_validate(v) for v in videos],
        total=total,
        page=(offset // limit) + 1,
        page_size=limit,
    )


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get a specific video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return VideoResponse.model_validate(video)


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
def create_video(
    payload: VideoCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new video entry."""
    channel = db.query(Channel).filter(Channel.id == payload.channel_id).first()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    video = Video(
        channel_id=payload.channel_id,
        script_id=payload.script_id,
        topic_id=payload.topic_id,
        title=payload.title,
        description=payload.description,
        privacy_status=payload.privacy_status,
        made_for_kids=payload.made_for_kids,
        category_id=payload.category_id,
        language=payload.language,
        is_short=payload.is_short,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return VideoResponse.model_validate(video)


@router.put("/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    payload: VideoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update video details."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)
    db.commit()
    db.refresh(video)
    return VideoResponse.model_validate(video)


@router.post("/generate", response_model=VideoGenerationResponse)
def generate_video(
    payload: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full video generation pipeline: research → script → voice → video → thumbnail → SEO → publish."""
    from app.services.ai_workflow import TrendTubeWorkflow

    # Find or create topic
    topic = db.query(TrendingTopic).filter(TrendingTopic.title.ilike(f"%{payload.topic}%")).first()
    if not topic:
        topic = TrendingTopic(
            title=payload.topic,
            topic_type="general",
            score=75,
            is_processed=True,
            discovered_at=datetime.now(timezone.utc),
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)

    # Create workflow run
    workflow = WorkflowRun(
        workflow_name="full_pipeline",
        topic_id=topic.id,
        status="queued",
        progress=0.0,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Execute AI workflow
    ai_workflow = TrendTubeWorkflow()
    result = ai_workflow.run(payload.topic, payload.style)

    # Create video placeholder
    video = Video(
        channel_id=payload.channel_id,
        topic_id=topic.id,
        title=f"AI Generated: {payload.topic}",
        status="researching",
        resolution=payload.resolution,
        language=payload.language,
        is_short=False,
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return VideoGenerationResponse(
        video_id=video.id,
        workflow_id=workflow.id,
        status=workflow.status,
        summary=result.get("summary", "Video generation workflow started"),
    )


@router.post("/{video_id}/publish", response_model=VideoResponse)
def publish_video(
    video_id: int,
    payload: VideoPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish or schedule a video to YouTube."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    video.status = "publishing" if not payload.publish_at else "draft"
    video.privacy_status = payload.privacy_status
    video.published_at = payload.publish_at or datetime.now(timezone.utc)
    db.commit()
    db.refresh(video)
    return VideoResponse.model_validate(video)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    db.delete(video)
    db.commit()

