"""Script schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScriptGenerateRequest(BaseModel):
    topic_id: int
    research_id: Optional[int] = None
    style: str = "educational"
    duration_seconds: int = 600
    tone: Optional[str] = None
    additional_instructions: Optional[str] = None


class ScriptResponse(BaseModel):
    id: int
    topic_id: int
    research_id: Optional[int] = None
    style: str
    title: Optional[str] = None
    content: str
    hook: Optional[str] = None
    body: Optional[str] = None
    call_to_action: Optional[str] = None
    estimated_duration_seconds: int
    word_count: int
    reading_ease_score: Optional[float] = None
    seo_score: Optional[float] = None
    is_optimized: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScriptUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    style: Optional[str] = None


class ScriptListResponse(BaseModel):
    items: list[ScriptResponse]
    total: int


class ScriptOptimizeRequest(BaseModel):
    script_id: int
    target_style: Optional[str] = None
    target_duration: Optional[int] = None

