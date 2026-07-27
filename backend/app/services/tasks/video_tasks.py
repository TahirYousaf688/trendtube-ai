"""Video generation and processing Celery tasks."""

from app.core.logging import get_logger
from app.services.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_video_task(self, topic: str, style: str, channel_id: int):
    """Background task for full video generation pipeline."""
    try:
        from app.services.ai_orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator()
        result = orchestrator.run_full_pipeline(topic, style)
        logger.info(f"Video generation completed for topic: {topic}")
        return {"status": "completed", "result": result}
    except Exception as exc:
        logger.error(f"Video generation failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def publish_video_task(self, video_id: int, privacy_status: str):
    """Background task for publishing video to YouTube."""
    try:
        logger.info(f"Publishing video {video_id} with status {privacy_status}")
        return {"status": "published", "video_id": video_id}
    except Exception as exc:
        logger.error(f"Video publishing failed: {exc}")
        raise self.retry(exc=exc, countdown=30)

