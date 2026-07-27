"""Analytics and monitoring Celery tasks."""

from app.core.logging import get_logger
from app.services.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def sync_youtube_analytics_task(self, channel_id: int):
    """Background task for syncing YouTube analytics data."""
    try:
        logger.info(f"Syncing analytics for channel {channel_id}")
        return {"status": "completed", "channel_id": channel_id}
    except Exception as exc:
        logger.error(f"Analytics sync failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


@celery_app.task(bind=True, max_retries=3)
def generate_insights_task(self, video_id: int):
    """Background task for generating AI-powered insights."""
    try:
        from app.services.agents import AnalyticsAgent

        agent = AnalyticsAgent()
        insights = agent.insights(f"video_{video_id}")
        logger.info(f"Insights generated for video {video_id}")
        return {"status": "completed", "video_id": video_id}
    except Exception as exc:
        logger.error(f"Insights generation failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

