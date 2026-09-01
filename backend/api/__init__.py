"""API routers package initialization."""
from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.api.feedback import router as feedback_router
from backend.api.runs import router as runs_router
from backend.api.evaluation_api import router as evaluation_router
from backend.api.health import router as health_router

__all__ = [
    "chat_router",
    "documents_router",
    "feedback_router",
    "runs_router",
    "evaluation_router",
    "health_router",
]
