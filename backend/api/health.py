"""
Health check and system status endpoint.
"""
from fastapi import APIRouter
from backend.config import settings
from backend.rag.vector_store import vector_store
from backend.rag.bm25 import bm25_retriever
from backend.database.postgres import db_manager

router = APIRouter(tags=["Health & Status"])


@router.get("/health")
@router.get("/api/health")
async def health_check():
    """Returns system status, active vector points, and database connectivity."""
    db_ok = False
    try:
        rows, st = db_manager.execute_read_query("SELECT 1 AS ok")
        db_ok = st == "SUCCESS"
    except Exception:
        db_ok = False

    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "database_connected": db_ok,
        "qdrant_points": vector_store.count_chunks(),
        "bm25_chunks": bm25_retriever.count_chunks(),
        "strategy_learning_enabled": settings.ENABLE_STRATEGY_LEARNING,
    }
