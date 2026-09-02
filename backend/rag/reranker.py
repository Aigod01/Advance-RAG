"""
Reranker using the Hugging Face Inference API's sentence-similarity task,
with a heuristic term-overlap fallback that needs no model at all.

Note: the original local model (cross-encoder/ms-marco-MiniLM-L-6-v2) isn't
currently hosted by any Hugging Face Inference Provider, so the default
model here is BAAI/bge-reranker-base, which is. Set RERANKER_MODEL to
override if you want a different hosted reranker.
"""
import logging
from typing import List, Dict, Any
from backend.config import settings

logger = logging.getLogger(__name__)

_client_instance = None


class CrossEncoderReranker:
    """Reranks retrieval candidates using a hosted reranker model, refining
    the top-k results from hybrid dense+sparse retrieval."""

    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self._client = None
        self._load_client()

    def _load_client(self):
        global _client_instance
        if not settings.HF_TOKEN:
            logger.warning(
                "HF_TOKEN not set. Reranking will use the heuristic "
                "term-overlap fallback. Set HF_TOKEN to use a real reranker."
            )
            return

        if _client_instance is not None:
            self._client = _client_instance
            return

        try:
            from huggingface_hub import InferenceClient
            self._client = InferenceClient(provider="hf-inference", api_key=settings.HF_TOKEN)
            _client_instance = self._client
            logger.info(f"Using Hugging Face Inference API for reranking: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not initialize HF InferenceClient ({e}). Using heuristic term-proximity reranker.")
            self._client = None

    def rerank(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Reranks candidates using the hosted cross-encoder/reranker model."""
        if not candidates:
            return []

        if self._client is not None:
            try:
                scores = self._client.sentence_similarity(
                    query,
                    other_sentences=[c["content"] for c in candidates],
                    model=self.model_name,
                )

                reranked = []
                for score, item in zip(scores, candidates):
                    score = max(0.0, min(1.0, float(score)))  # defensive clamp
                    item_copy = item.copy()
                    item_copy["rerank_score"] = round(score, 4)
                    # Combine original score and rerank score (70% reranker, 30% initial)
                    combined = 0.7 * score + 0.3 * float(item.get("score", 0.5))
                    item_copy["final_score"] = round(combined, 4)
                    reranked.append(item_copy)

                reranked.sort(key=lambda x: x["final_score"], reverse=True)
                return reranked[:top_k]
            except Exception as e:
                logger.error(f"HF reranker API error: {e}. Falling back to heuristic reranking.")

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
