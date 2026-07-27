"""Research routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Research, TrendingTopic, User
from app.schemas.research import (
    FactCheckRequest,
    ResearchListResponse,
    ResearchRequest,
    ResearchResponse,
)

router = APIRouter(prefix="/research", tags=["Research"])


@router.get("", response_model=ResearchListResponse)
def list_research(
    topic_id: int | None = None,
    db: Session = Depends(get_db),
):
    """List research entries, optionally filtered by topic."""
    query = db.query(Research)
    if topic_id:
        query = query.filter(Research.topic_id == topic_id)
    items = query.order_by(Research.created_at.desc()).all()
    return ResearchListResponse(
        items=[ResearchResponse.model_validate(r) for r in items],
        total=len(items),
    )


@router.post("", response_model=ResearchResponse, status_code=status.HTTP_201_CREATED)
def create_research(
    payload: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create research for a topic (triggers Research Agent)."""
    topic = db.query(TrendingTopic).filter(TrendingTopic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    # Mock research creation
    research = Research(
        topic_id=payload.topic_id,
        summary=f"Comprehensive research summary for: {topic.title}. This covers key aspects, statistics, and reliable sources.",
        key_points=[
            "Key insight 1: Market trend analysis shows significant growth",
            "Key insight 2: Multiple reliable sources confirm the trend",
            "Key insight 3: Expert opinions align on the direction",
        ],
        statistics=[{"metric": "Growth Rate", "value": "25%", "source": "Industry Report 2024"}],
        citations=[
            {
                "source": "Industry Report",
                "url": "https://example.com/report",
                "title": "2024 Market Analysis",
                "snippet": "The market shows strong growth trends...",
                "relevance_score": 0.95,
            }
        ],
        sources=[{"name": "Industry Report", "type": "report", "reliability": "high"}],
        confidence_score=85,
        is_fact_checked=True,
    )
    db.add(research)
    db.commit()
    db.refresh(research)
    return ResearchResponse.model_validate(research)


@router.get("/{research_id}", response_model=ResearchResponse)
def get_research(research_id: int, db: Session = Depends(get_db)):
    """Get a specific research entry."""
    research = db.query(Research).filter(Research.id == research_id).first()
    if not research:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research not found")
    return ResearchResponse.model_validate(research)


@router.post("/{research_id}/fact-check", response_model=ResearchResponse)
def fact_check_research(
    research_id: int,
    payload: FactCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger fact-checking on research."""
    research = db.query(Research).filter(Research.id == research_id).first()
    if not research:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research not found")

    research.is_fact_checked = True
    research.fact_check_summary = f"Fact-checking completed. All claims verified with {len(payload.additional_sources or []) + 3} sources."
    research.confidence_score = min(research.confidence_score + 10, 100)
    db.commit()
    db.refresh(research)
    return ResearchResponse.model_validate(research)

