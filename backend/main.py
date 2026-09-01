"""
Main FastAPI Application Entrypoint.
Initializes Database, Ingests Document Corpus, Configures CORS, and Mounts API Routers.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.config import settings
from backend.database.seed_data import seed_database
from backend.rag.ingestion import ingestion_pipeline
from backend.api import (
    chat_router,
    documents_router,
    feedback_router,
    runs_router,
    evaluation_router,
    health_router,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("multi_agent_rag")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database and corporate document corpus on startup."""
    logger.info("Initializing Multi-Agent Collaborative RAG Backend...")
    try:
        # Seed database
        seed_database()
    except Exception as e:
        logger.warning(f"Database seed initialization note: {e}")

    try:
        # Ingest document corpus
        res = ingestion_pipeline.ingest_directory()
        logger.info(f"Corpus ingestion complete: {res.get('total_files')} files ({res.get('total_chunks')} chunks indexed).")
    except Exception as e:
        logger.warning(f"Document ingestion note: {e}")

    logger.info(f"System ready on http://{settings.HOST}:{settings.PORT}")
    yield
    logger.info("Shutting down Multi-Agent Collaborative RAG Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent Collaborative RAG system with Adaptive Strategy Learning and LangGraph Orchestration",
    lifespan=lifespan,
)

# Configure CORS. Explicit origin allow-list (rather than "*") so credentials
# and browser preflight behave correctly for both local dev and the Dockerized
# frontend, which normally talk to this API same-origin through a proxy anyway.
_allowed_origins = list(dict.fromkeys(filter(None, [
    settings.FRONTEND_ORIGIN,
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
])))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(runs_router)
app.include_router(evaluation_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
