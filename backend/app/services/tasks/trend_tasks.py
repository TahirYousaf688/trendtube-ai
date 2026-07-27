"""Trend discovery and analysis Celery tasks."""

from app.core.logging import get_logger
from app.services.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def discover_trends_task(self):
    """Background task for trend discovery from all sources."""
    try:
        from app.services.agents import TrendAgent

        agent = TrendAgent()
        trends = agent.discover()
        logger.info(f"Discovered {len(trends)} trending topics")
        return {"status": "completed", "trends_count": len(trends)}
    except Exception as exc:
        logger.error(f"Trend discovery failed: {exc}")
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, max_retries=3)
def research_topic_task(self, topic_id: int):
    """Background task for researching a specific topic."""
    try:
        from app.services.agents import ResearchAgent

        agent = ResearchAgent()
        research = agent.research(f"topic_{topic_id}")
        logger.info(f"Research completed for topic {topic_id}")
        return {"status": "completed", "topic_id": topic_id}
    except Exception as exc:
        logger.error(f"Research failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

