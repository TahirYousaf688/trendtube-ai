"""Script generation routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Research, Script, TrendingTopic, User
from app.schemas.scripts import (
    ScriptGenerateRequest,
    ScriptListResponse,
    ScriptOptimizeRequest,
    ScriptResponse,
    ScriptUpdateRequest,
)

router = APIRouter(prefix="/scripts", tags=["Scripts"])


@router.get("", response_model=ScriptListResponse)
def list_scripts(
    topic_id: int | None = None,
    style: str | None = None,
    db: Session = Depends(get_db),
):
    """List scripts with optional filters."""
    query = db.query(Script)
    if topic_id:
        query = query.filter(Script.topic_id == topic_id)
    if style:
        query = query.filter(Script.style == style)
    items = query.order_by(Script.created_at.desc()).all()
    return ScriptListResponse(
        items=[ScriptResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.post("/generate", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
def generate_script(
    payload: ScriptGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a script using AI (triggers Script Writer Agent)."""
    topic = db.query(TrendingTopic).filter(TrendingTopic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    research = None
    if payload.research_id:
        research = db.query(Research).filter(Research.id == payload.research_id).first()

    # Mock script generation
    hook = f"Did you know that {topic.title} is changing the way we think about content creation?"
    body = f"""
In this video, we dive deep into {topic.title}. 

{'Research shows' if research else 'Industry experts reveal'} that this trend is gaining massive traction across multiple platforms.

Here are the key things you need to know:
1. The market is growing at an unprecedented rate
2. Early adopters are seeing remarkable results
3. The technology is becoming more accessible every day

Let's break down what this means for creators and businesses alike.
    """

    word_count = len(body.split())
    estimated_duration = max(payload.duration_seconds, int(word_count / 150 * 60))

    script = Script(
        topic_id=payload.topic_id,
        research_id=payload.research_id,
        style=payload.style,
        title=f"The Complete Guide to {topic.title}",
        content=f"# {hook}\n\n{body}\n\n## Call to Action\n\nIf you found this valuable, like and subscribe for more insights!",
        hook=hook,
        body=body,
        call_to_action="If you found this valuable, like and subscribe for more insights!",
        estimated_duration_seconds=estimated_duration,
        word_count=word_count,
        reading_ease_score=65.5,
        seo_score=78.3,
        version=1,
    )
    db.add(script)
    db.commit()
    db.refresh(script)
    return ScriptResponse.model_validate(script)


@router.get("/{script_id}", response_model=ScriptResponse)
def get_script(script_id: int, db: Session = Depends(get_db)):
    """Get a specific script."""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
    return ScriptResponse.model_validate(script)


@router.put("/{script_id}", response_model=ScriptResponse)
def update_script(
    script_id: int,
    payload: ScriptUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a script."""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(script, field, value)
    script.version += 1
    db.commit()
    db.refresh(script)
    return ScriptResponse.model_validate(script)


@router.post("/{script_id}/optimize", response_model=ScriptResponse)
def optimize_script(
    script_id: int,
    payload: ScriptOptimizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Optimize a script for SEO and engagement."""
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")

    script.is_optimized = True
    script.seo_score = 92.0
    script.reading_ease_score = 70.0
    script.version += 1
    db.commit()
    db.refresh(script)
    return ScriptResponse.model_validate(script)

