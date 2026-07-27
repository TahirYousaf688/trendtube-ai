"""Celery application configuration."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "trendtube",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.services.tasks.video_tasks",
        "app.services.tasks.trend_tasks",
        "app.services.tasks.analytics_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
)

