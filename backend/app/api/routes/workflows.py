"""Workflow orchestration routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.domain import Task, User, WorkflowRun
from app.schemas.workflows import (
    TaskListResponse,
    TaskResponse,
    WorkflowRunListResponse,
    WorkflowRunResponse,
    WorkflowTriggerRequest,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=WorkflowRunListResponse)
def list_workflows(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List workflow runs."""
    query = db.query(WorkflowRun)
    if status_filter:
        query = query.filter(WorkflowRun.status == status_filter)
    items = query.order_by(WorkflowRun.created_at.desc()).limit(50).all()
    return WorkflowRunListResponse(
        items=[WorkflowRunResponse.model_validate(w) for w in items],
        total=len(items),
    )


@router.post("/trigger", response_model=WorkflowRunResponse, status_code=status.HTTP_201_CREATED)
def trigger_workflow(
    payload: WorkflowTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a new workflow run."""
    workflow = WorkflowRun(
        workflow_name=payload.workflow_name,
        topic_id=payload.topic_id,
        status="queued",
        progress=0.0,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return WorkflowRunResponse.model_validate(workflow)


@router.get("/{workflow_id}", response_model=WorkflowRunResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get workflow run details."""
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowRunResponse.model_validate(workflow)


@router.post("/{workflow_id}/cancel", response_model=WorkflowRunResponse)
def cancel_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a running workflow."""
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    workflow.status = "cancelled"
    db.commit()
    db.refresh(workflow)
    return WorkflowRunResponse.model_validate(workflow)


@router.get("/{workflow_id}/tasks", response_model=TaskListResponse)
def list_workflow_tasks(
    workflow_id: int,
    db: Session = Depends(get_db),
):
    """List tasks for a workflow."""
    tasks = db.query(Task).filter(Task.workflow_run_id == workflow_id).order_by(Task.created_at).all()
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=len(tasks),
    )

