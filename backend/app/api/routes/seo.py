"""SEO optimization routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import SEOMetadata, User, Video
from app.schemas.seo import SEOGenerateRequest, SEOResponse, SEOUpdateRequest

router = APIRouter(prefix="/seo", tags=["SEO"])


@router.get("/{video_id}", response_model=SEOResponse)
def get_seo(
    video_id: int,
    db: Session = Depends(get_db),
):
    """Get SEO metadata for a video."""
    seo = db.query(SEOMetadata).filter(SEOMetadata.video_id == video_id).first()
    if not seo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SEO metadata not found")
    return SEOResponse.model_validate(seo)


@router.post("/generate", response_model=SEOResponse, status_code=status.HTTP_201_CREATED)
def generate_seo(
    payload: SEOGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate optimized SEO metadata using AI (SEO Agent)."""
    video = db.query(Video).filter(Video.id == payload.video_id).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # Mock SEO generation
    seo = SEOMetadata(
        video_id=payload.video_id,
        title=video.title,
        description=f"🚀 {video.title}\n\nIn this video, we explore the latest trends and insights. "
                     "Perfect for anyone interested in staying ahead of the curve.\n\n"
                     "📌 Key Topics Covered:\n"
                     "• Industry insights and analysis\n"
                     "• Expert opinions and predictions\n"
                     "• Actionable strategies\n\n"
                     "Don't forget to like, subscribe, and hit the bell for more content! 🔔",
        tags=[
            video.title.lower().replace(" ", ""),
            "trending",
            "viral",
            "aitools",
            "contentcreation",
            "youtubeautomation",
        ],
        hashtags=["#" + w.lower() for w in video.title.split()[:5]],
        chapters=[
            {"title": "Introduction", "time": "0:00"},
            {"title": "Key Insights", "time": "1:30"},
            {"title": "Deep Dive", "time": "3:45"},
            {"title": "Final Thoughts", "time": "7:00"},
        ],
        pinned_comment="What topic should we cover next? Drop your suggestions below! 👇",
        community_post="New video just dropped! Check out our latest deep dive 🔥",
        seo_score=85.0,
        is_optimized=True,
    )
    db.add(seo)
    db.commit()
    db.refresh(seo)
    return SEOResponse.model_validate(seo)


@router.put("/{video_id}", response_model=SEOResponse)
def update_seo(
    video_id: int,
    payload: SEOUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update SEO metadata manually."""
    seo = db.query(SEOMetadata).filter(SEOMetadata.video_id == video_id).first()
    if not seo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SEO metadata not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seo, field, value)
    db.commit()
    db.refresh(seo)
    return SEOResponse.model_validate(seo)

