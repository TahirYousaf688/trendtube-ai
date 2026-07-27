"""Research schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic_id: int
    depth: str = "standard"  # quick, standard, deep
    custom_sources: Optional[list[str]] = None


class CitationResponse(BaseModel):
    source: str
    url: str
    title: str
    snippet: str
    relevance_score: float


class ResearchResponse(BaseModel):
    id: int
    topic_id: int
    summary: str
    key_points: list
    statistics: list
    citations: list
    sources: list
    confidence_score: int
    misinformation_flags: list
    is_fact_checked: bool
    fact_check_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResearchListResponse(BaseModel):
    items: list[ResearchResponse]
    total: int


class FactCheckRequest(BaseModel):
    research_id: int
    additional_sources: Optional[list[str]] = None

