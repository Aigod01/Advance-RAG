"""
User feedback and Strategy Memory endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.memory.feedback_memory import feedback_memory
from backend.memory.strategy_memory import strategy_memory

router = APIRouter(prefix="/api", tags=["Feedback & Learning"])


class FeedbackRequest(BaseModel):
    run_id: str
    rating: int = Field(ge=-1, le=1)  # 1 for thumbs up, -1 for thumbs down
    comments: Optional[str] = None
    query: Optional[str] = None
    final_answer: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Submits user rating and updates Strategy Memory reinforcement rewards."""
    if req.rating not in [1, -1]:
        raise HTTPException(status_code=400, detail="Rating must be +1 or -1.")

    # 1. Record in feedback memory
    fb_entry = feedback_memory.record_feedback(
        run_id=req.run_id,
        rating=req.rating,
        comments=req.comments,
        query=req.query,
        final_answer=req.final_answer,
    )

    # 2. Update Strategy Memory bandit rewards
    strategy_memory.apply_user_feedback(run_id=req.run_id, feedback=req.rating)

    return {
        "status": "SUCCESS",
        "message": "Feedback recorded and strategy learning updated.",
        "entry": fb_entry,
    }


@router.get("/feedback/stats")
async def get_feedback_stats():
    """Returns aggregated user feedback statistics."""
    return feedback_memory.get_feedback_stats()


@router.get("/strategy/summary")
async def get_strategy_summary():
    """Returns Strategy Memory learned weights, episodes, and bandit distribution."""
    return strategy_memory.get_strategy_summary()
