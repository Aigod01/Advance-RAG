"""
Conditional edges and routing decisions for LangGraph multi-agent execution.
"""
from typing import Literal
from backend.config import settings
from backend.graph.state import AgentState


def route_after_critic(state: AgentState) -> Literal["retry_router", "synthesizer"]:
    """
    Decides whether to trigger self-correction retry or proceed to synthesis.
    Enforces MAX_RETRIES hard ceiling.
    """
    critique = state.get("critique", {})
    retry_count = state.get("retry_count", 0)
    max_retries = settings.MAX_RETRIES

    # Check if critic flagged retry and retry limit not exceeded
    if critique.get("retry", False) and retry_count < max_retries:
        return "retry_router"

    return "synthesizer"
