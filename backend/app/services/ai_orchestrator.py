"""LangGraph-based AI workflow orchestrator for TrendTube AI."""

from typing import Any, Dict, List

from app.services.agents import (
    AnalyticsAgent,
    FactCheckerAgent,
    MonetizationAgent,
    PublisherAgent,
    RecommendationAgent,
    ResearchAgent,
    SEOAgent,
    ScriptWriterAgent,
    ThumbnailAgent,
    TrendAgent,
    VideoEditorAgent,
    VoiceAgent,
)


class AIOrchestrator:
    """Orchestrates AI agents using LangGraph for video production pipeline."""

    def __init__(self):
        self.agents = {
            "trend": TrendAgent(),
            "research": ResearchAgent(),
            "fact_checker": FactCheckerAgent(),
            "script_writer": ScriptWriterAgent(),
            "voice": VoiceAgent(),
            "thumbnail": ThumbnailAgent(),
            "seo": SEOAgent(),
            "video_editor": VideoEditorAgent(),
            "publisher": PublisherAgent(),
            "analytics": AnalyticsAgent(),
            "recommendation": RecommendationAgent(),
            "monetization": MonetizationAgent(),
        }
        self.workflow_steps = [
            "trend_discovery",
            "research",
            "fact_checking",
            "script_generation",
            "voice_generation",
            "thumbnail_generation",
            "seo_optimization",
            "video_editing",
            "publishing",
            "analytics_tracking",
        ]

    async def run_full_pipeline(self, topic: str, style: str = "educational") -> Dict[str, Any]:
        """Execute the full video production pipeline."""
        state = {"topic": topic, "style": style, "status": "running", "progress": 0}

        try:
            # Step 1: Trend Discovery
            state["progress"] = 10
            trend_agent = self.agents["trend"]
            trend_data = await trend_agent.analyze(topic)
            state["trend_analysis"] = trend_data

            # Step 2: Research
            state["progress"] = 25
            research_agent = self.agents["research"]
            research_data = await research_agent.research(topic)
            state["research"] = research_data

            # Step 3: Fact Checking
            state["progress"] = 35
            fact_checker = self.agents["fact_checker"]
            fact_check_data = await fact_checker.cross_reference(
                research_data["summary"],
                research_data.get("sources_used", []),
            )
            state["fact_check"] = fact_check_data

            # Step 4: Script Generation
            state["progress"] = 50
            script_agent = self.agents["script_writer"]
            script_data = await script_agent.generate(topic, style)
            state["script"] = script_data

            # Step 5: Voice Generation
            state["progress"] = 60
            voice_agent = self.agents["voice"]
            voice_data = await voice_agent.generate(script_data["body"])
            state["voice"] = voice_data

            # Step 6: Thumbnail Generation
            state["progress"] = 70
            thumbnail_agent = self.agents["thumbnail"]
            thumbnail_data = await thumbnail_agent.generate(script_data["title"])
            state["thumbnails"] = thumbnail_data

            # Step 7: SEO Optimization
            state["progress"] = 80
            seo_agent = self.agents["seo"]
            seo_data = await seo_agent.optimize(
                script_data["title"],
                script_data["body"],
                [topic.lower().replace(" ", "")],
            )
            state["seo"] = seo_data

            # Step 8: Video Composition
            state["progress"] = 90
            editor_agent = self.agents["video_editor"]
            video_data = await editor_agent.compose(
                script_data["body"],
                [],
                voice_data["audio_url"],
            )
            state["video"] = video_data

            state["status"] = "completed"
            state["progress"] = 100

        except Exception as e:
            state["status"] = "failed"
            state["error"] = str(e)

        return state

    async def run_step(self, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_agent_map = {
            "trend_discovery": "trend",
            "research": "research",
            "fact_checking": "fact_checker",
            "script_generation": "script_writer",
            "voice_generation": "voice",
            "thumbnail_generation": "thumbnail",
            "seo_optimization": "seo",
            "video_editing": "video_editor",
            "publishing": "publisher",
            "analytics_tracking": "analytics",
        }

        agent_key = step_agent_map.get(step)
        if not agent_key:
            return {"status": "failed", "error": f"Unknown step: {step}"}

        agent = self.agents[agent_key]
        return await agent.process(data) if hasattr(agent, 'process') else {"status": "completed", "data": data}

