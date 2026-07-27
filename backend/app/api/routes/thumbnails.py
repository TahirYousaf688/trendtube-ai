"""Thumbnail generation routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Thumbnail, User, Video
from app.schemas.thumbnails import (
    ThumbnailABTestRequest,
    ThumbnailGenerateRequest,
    ThumbnailListResponse,
    ThumbnailResponse,
    ThumbnailSelectRequest,
)

router = APIRouter(prefix="/thumbnails", tags=["Thumbnails"])


@router.get("", response_model=ThumbnailListResponse)
def list_thumbnails(
    video_id: int,
    db: Session = Depends(get_db),
):
    """List thumbnails for a video."""
    thumbnails = db.query(Thumbnail).filter(Thumbnail.video_id == video_id).all()
    return ThumbnailListResponse(
        items=[ThumbnailResponse.model_validate(t) for t in thumbnails],
        total=len(thumbnails),
    )


@router.post("/generate", response_model=list[ThumbnailResponse], status_code=status.HTTP_201_CREATED)
def generate_thumbnails(
    payload: ThumbnailGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate thumbnail options using AI."""
    video = db.query(Video).filter(Video.id == payload.video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    generated = []
    for i in range(payload.count):
        thumbnail = Thumbnail(
            video_id=payload.video_id,
            storage_key=f"thumbnails/{payload.video_id}/option_{i+1}.jpg",
            url=f"https://assets.trendtube.ai/thumbnails/{payload.video_id}/option_{i+1}.jpg",
            width=1280,
            height=720,
            ctr_score=0.0,
            generation_prompt=payload.prompt or f"Thumbnail option {i+1} for: {video.title}",
        )
        db.add(thumbnail)
        db.commit()
        db.refresh(thumbnail)
        generated.append(thumbnail)

    return [ThumbnailResponse.model_validate(t) for t in generated]


@router.post("/select", response_model=ThumbnailResponse)
def select_thumbnail(
    payload: ThumbnailSelectRequest,
    db: Session = Depends(get_db),
):
    """Select a thumbnail as the primary one."""
    thumbnail = db.query(Thumbnail).filter(Thumbnail.id == payload.thumbnail_id).first()
    if not thumbnail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found")

    # Deselect all other thumbnails for this video
    db.query(Thumbnail).filter(
        Thumbnail.video_id == thumbnail.video_id,
        Thumbnail.is_selected == True,  # noqa: E712
    ).update({"is_selected": False})
    db.commit()

    thumbnail.is_selected = True
    db.commit()
    db.refresh(thumbnail)
    return ThumbnailResponse.model_validate(thumbnail)


@router.post("/ab-test", response_model=dict)
def start_ab_test(
    payload: ThumbnailABTestRequest,
    db: Session = Depends(get_db),
):
    """Start an A/B test between two thumbnails."""
    thumb_a = db.query(Thumbnail).filter(Thumbnail.id == payload.thumbnail_a_id).first()
    thumb_b = db.query(Thumbnail).filter(Thumbnail.id == payload.thumbnail_b_id).first()

    if not thumb_a or not thumb_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found")

    thumb_a.is_a_b_test = True
    thumb_b.is_a_b_test = True
    db.commit()

    return {
        "message": f"A/B test started between thumbnails {payload.thumbnail_a_id} and {payload.thumbnail_b_id}",
        "duration_hours": payload.duration_hours,
        "thumbnail_a_id": payload.thumbnail_a_id,
        "thumbnail_b_id": payload.thumbnail_b_id,
    }

