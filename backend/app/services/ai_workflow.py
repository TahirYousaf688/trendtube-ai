from __future__ import annotations

from typing import Any, Dict, List

try:
    from langgraph.graph import StateGraph  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    StateGraph = None


class TrendTubeWorkflow:
    def __init__(self) -> None:
        self.steps: List[str] = ["trend_discovery", "research", "script_generation", "voice_generation", "publish"]

    def run(self, topic: str, style: str = "educational") -> Dict[str, Any]:
        if StateGraph is not None:
            return self._run_with_langgraph(topic, style)
        return self._run_fallback(topic, style)

    def _run_fallback(self, topic: str, style: str) -> Dict[str, Any]:
        return {
            "workflow_id": "wf-demo-001",
            "topic": topic,
            "style": style,
            "status": "queued",
            "summary": "Workflow prepared for trend discovery, research synthesis, and publishing.",
            "steps": self.steps,
        }

    def _run_with_langgraph(self, topic: str, style: str) -> Dict[str, Any]:
        graph = StateGraph(dict)
        graph.add_node("trend", lambda state: {**state, "topic": topic})
        graph.add_node("research", lambda state: {**state, "research": f"Researching {topic}"})
        graph.add_node("script", lambda state: {**state, "script_style": style})
        graph.add_edge("trend", "research")
        graph.add_edge("research", "script")
        compiled = graph.compile()
        state = compiled.invoke({"topic": topic})
        return {
            "workflow_id": "wf-langgraph-001",
            "topic": state.get("topic"),
            "style": style,
            "status": "queued",
            "summary": "LangGraph workflow executed successfully.",
            "steps": self.steps,
        }
