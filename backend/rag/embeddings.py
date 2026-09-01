"""
Embedding service with SentenceTransformers and robust fallback support.
"""
import logging
from typing import List
import numpy as np
from backend.config import settings

logger = logging.getLogger(__name__)

_model_instance = None


class EmbeddingProvider:
    """Provides dense vector embeddings for documents and queries."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL, dim: int = settings.EMBEDDING_DIM):
        self.model_name = model_name
        self.dim = dim
        self._model = None
        self._load_model()

    def _load_model(self):
        global _model_instance
        if _model_instance is not None:
            self._model = _model_instance
            return

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            _model_instance = self._model
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic fallback vectorizer.")
            self._model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of document texts."""
        if not texts:
            return []

        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Embedding error with model: {e}. Falling back to hash vectorizer.")

        # Fallback deterministic pseudo-embeddings for fast testing / zero GPU setup
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single search query."""
        res = self.embed_documents([text])
        return res[0] if res else [0.0] * self.dim

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
