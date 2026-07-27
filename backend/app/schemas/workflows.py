"""Workflow schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WorkflowRunResponse(BaseModel):
    id: int
    workflow_name: str
    topic_id: Optional[int] = None
    video_id: Optional[int] = None
    status: str
    current_step: Optional[str] = None
    progress: float
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowRunListResponse(BaseModel):
    items: list[WorkflowRunResponse]
    total: int


class TaskResponse(BaseModel):
    id: int
    task_type: str
    workflow_run_id: Optional[int] = None
    status: str
    priority: int
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int


class WorkflowTriggerRequest(BaseModel):
    topic_id: int
    workflow_name: str = "full_pipeline"
    auto_publish: bool = False
    review_before_publish: bool = True

