"""
Configuration settings for Multi-Agent Collaborative RAG.
Loads from environment variables and .env file with sensible defaults.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "Multi-Agent Collaborative RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    JWT_SECRET: str = "super-secret-key-change-in-production-32chars"
    STORAGE_PATH: str = "./data"

    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "openai", "gemini", "anthropic", "groq", "ollama", "mock"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048

    # Per-provider API keys (read directly from the matching env var so users
    # don't have to remap e.g. GROQ_API_KEY -> LLM_API_KEY themselves).
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Embedding & Reranker (served via the Hugging Face Inference API --
    # see backend/rag/embeddings.py and backend/rag/reranker.py. No local
    # model weights, no torch. Falls back to a deterministic/heuristic local
    # implementation if HF_TOKEN isn't set.)
    HF_TOKEN: Optional[str] = None
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # Database
    DATABASE_URL: str = "sqlite:///./data/enterprise_sales.db"
    DB_TIMEOUT_SECONDS: int = 10
    DB_MAX_ROWS: int = 100

    # Vector DB (Qdrant)
    QDRANT_URL: str = "./data/qdrant_storage"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "corporate_documents"

    # Web Search
    WEB_SEARCH_PROVIDER: str = "duckduckgo"  # "duckduckgo", "tavily", "serper", "brave"
    WEB_SEARCH_API_KEY: Optional[str] = None
    WEB_SEARCH_MAX_RESULTS: int = 5
    WEB_SEARCH_TIMEOUT: int = 10

    # Orchestration & Multi-Agent Limits
    MAX_RETRIES: int = 2
    CONFIDENCE_THRESHOLD: float = 0.70
    GRAPH_TIMEOUT_SECONDS: int = 60
    ENABLE_STRATEGY_LEARNING: bool = True

    # Observability
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "multi-agent-rag"


settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.STORAGE_PATH, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "documents"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "evaluation"), exist_ok=True)
if settings.QDRANT_URL.startswith("./"):
    os.makedirs(settings.QDRANT_URL, exist_ok=True)
