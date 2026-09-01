"""
Cross-Encoder Neural Reranker for deep semantic passage re-scoring.
"""
import logging
from typing import List, Dict, Any, Tuple
from backend.config import settings

logger = logging.getLogger(__name__)

_reranker_instance = None


class CrossEncoderReranker:
    """Neural Cross-Encoder reranker to refine top-k retrieval candidates."""

    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self._model = None
        self._load_model()

    def _load_model(self):
        global _reranker_instance
        if _reranker_instance is not None:
            self._model = _reranker_instance
            return

        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading cross-encoder reranker model: {self.model_name}")
            self._model = CrossEncoder(self.model_name)
            _reranker_instance = self._model
        except Exception as e:
            logger.warning(f"Could not load CrossEncoder model ({e}). Using heuristic term-proximity reranker.")
            self._model = None

    def rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Reranks candidates based on deep query-document cross attention scores."""
        if not candidates:
            return []

        if self._model is not None:
            try:
                pairs = [[query, c["content"]] for c in candidates]
                scores = self._model.predict(pairs)
                # Sigmoid or min-max normalization
                import numpy as np
                norm_scores = 1.0 / (1.0 + np.exp(-np.array(scores)))

                reranked = []
                for score, item in zip(norm_scores, candidates):
                    item_copy = item.copy()
                    item_copy["rerank_score"] = float(round(score, 4))
                    # Combine original score and rerank score (70% reranker, 30% initial)
                    combined = 0.7 * float(score) + 0.3 * float(item.get("score", 0.5))
                    item_copy["final_score"] = round(combined, 4)
                    reranked.append(item_copy)

                reranked.sort(key=lambda x: x["final_score"], reverse=True)
                return reranked[:top_k]
            except Exception as e:
                logger.error(f"Neural reranker prediction error: {e}. Falling back to heuristic reranking.")

        # Heuristic fallback reranker
        return self._heuristic_rerank(query, candidates, top_k)

    def _heuristic_rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        q_terms = set(query.lower().split())
        reranked = []
        for c in candidates:
            content_lower = c["content"].lower()
            overlap = sum(1 for t in q_terms if t in content_lower)
            term_ratio = overlap / max(len(q_terms), 1)

            base_score = float(c.get("score", 0.5))
            final_s = 0.6 * base_score + 0.4 * term_ratio
            c_copy = c.copy()
            c_copy["rerank_score"] = round(term_ratio, 4)
            c_copy["final_score"] = round(final_s, 4)
            reranked.append(c_copy)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked[:top_k]


reranker = CrossEncoderReranker()
