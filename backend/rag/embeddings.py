"""
Embedding service using the Hugging Face Inference API, with a deterministic
local fallback that requires no model weights or GPU/CPU inference at all.

This intentionally does NOT depend on sentence-transformers/torch. Loading
those locally was the single largest contributor to this app's memory
footprint and Docker image size -- calling a hosted model over HTTP instead
keeps the backend lightweight enough to run on free-tier hosts.
"""
import logging
from typing import List
import numpy as np
from backend.config import settings

logger = logging.getLogger(__name__)

_client_instance = None


def _to_full_model_id(model_name: str) -> str:
    """The local sentence-transformers loader accepted short names like
    'all-MiniLM-L6-v2' and auto-prefixed them; the raw Hugging Face Hub API
    needs the full repo id ('sentence-transformers/all-MiniLM-L6-v2')."""
    return model_name if "/" in model_name else f"sentence-transformers/{model_name}"


class EmbeddingProvider:
    """Provides dense vector embeddings for documents and queries via the
    Hugging Face Inference API, falling back to a deterministic hash-based
    vectorizer if no HF_TOKEN is configured or the API call fails."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL, dim: int = settings.EMBEDDING_DIM):
        self.model_name = _to_full_model_id(model_name)
        self.dim = dim
        self._client = None
        self._load_client()

    def _load_client(self):
        global _client_instance
        if not settings.HF_TOKEN:
            logger.warning(
                "HF_TOKEN not set. Embeddings will use the deterministic hash "
                "fallback vectorizer -- fine for smoke-testing, but retrieval "
                "quality will suffer. Set HF_TOKEN to use real embeddings."
            )
            return

        if _client_instance is not None:
            self._client = _client_instance
            return

        try:
            from huggingface_hub import InferenceClient
            self._client = InferenceClient(provider="hf-inference", api_key=settings.HF_TOKEN)
            _client_instance = self._client
            logger.info(f"Using Hugging Face Inference API for embeddings: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not initialize HF InferenceClient ({e}). Using deterministic fallback vectorizer.")
            self._client = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of document texts."""
        if not texts:
            return []

        if self._client is not None:
            try:
                return [self._embed_one(t) for t in texts]
            except Exception as e:
                logger.error(f"HF embedding API error: {e}. Falling back to hash vectorizer.")

        # Fallback deterministic pseudo-embeddings for zero-dependency operation
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single search query."""
        res = self.embed_documents([text])
        return res[0] if res else [0.0] * self.dim

    def _embed_one(self, text: str) -> List[float]:
        vector = self._client.feature_extraction(text, model=self.model_name)
        arr = np.array(vector, dtype=np.float32)
        # Some models return per-token embeddings (2D) rather than a single
        # pooled sentence vector; mean-pool defensively so this keeps working
        # even if the hosted model's output shape isn't already pooled.
        if arr.ndim > 1:
            arr = arr.mean(axis=0)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()

    def _fallback_embed(self, text: str) -> List[float]:
        """Deterministic TF-hash vectorizer mapped to embedding dimension."""
        np.random.seed(abs(hash(text)) % (2**32))
        words = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)
        for w in words:
            h = abs(hash(w)) % self.dim
            vec[h] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec = np.random.randn(self.dim).astype(np.float32)
            vec /= np.linalg.norm(vec)
        return vec.tolist()


embedding_provider = EmbeddingProvider()
