"""Admin panel routes for system management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.domain import (
    AgentRun,
    AuditLog,
    BillingPlan,
    Channel,
    PromptTemplate,
    Subscription,
    Task,
    TrendingTopic,
    User,
    Video,
    WorkflowRun,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get overall system statistics."""
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "active_users": db.query(func.count(User.id)).filter(User.is_active == True).scalar(),  # noqa: E712
        "total_channels": db.query(func.count(Channel.id)).scalar(),
        "total_videos": db.query(func.count(Video.id)).scalar(),
        "published_videos": db.query(func.count(Video.id)).filter(Video.status == "published").scalar(),
        "total_topics": db.query(func.count(TrendingTopic.id)).scalar(),
        "active_subscriptions": db.query(func.count(Subscription.id)).filter(Subscription.status == "active").scalar(),
        "pending_tasks": db.query(func.count(Task.id)).filter(Task.status == "queued").scalar(),
        "running_workflows": db.query(func.count(WorkflowRun.id)).filter(WorkflowRun.status == "running").scalar(),
    }


@router.get("/users", response_model=list[dict])
def list_all_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    users = db.query(User).offset(offset).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "role": u.role.value if hasattr(u.role, 'value') else u.role,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        }
        for u in users
    ]


@router.get("/prompts", response_model=list[dict])
def list_prompt_templates(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all prompt templates (admin only)."""
    prompts = db.query(PromptTemplate).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "agent_type": p.agent_type,
            "version": p.version,
            "is_active": p.is_active,
            "variables": p.variables,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in prompts
    ]


@router.put("/prompts/{prompt_id}")
def update_prompt_template(
    prompt_id: int,
    content: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a prompt template (admin only)."""
    prompt = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt template not found")
    prompt.content = content
    prompt.version += 1
    db.commit()
    return {"message": "Prompt template updated", "version": prompt.version}


@router.get("/logs", response_model=list[dict])
def list_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    action: str | None = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List audit logs (admin only)."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/agent-runs", response_model=list[dict])
def list_agent_runs(
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List AI agent runs (admin only)."""
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "agent_type": r.agent_type,
            "tokens_used": r.tokens_used,
            "cost_usd": float(r.cost_usd) if r.cost_usd else 0,
            "duration_ms": r.duration_ms,
            "model_used": r.model_used,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


@router.get("/system-health")
def system_health(admin: User = Depends(require_admin)):
    """Get system health status."""
    import platform
    import time

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "services": {
            "api": "running",
            "database": "connected",
            "redis": "unknown",
            "celery": "unknown",
        },
    }

