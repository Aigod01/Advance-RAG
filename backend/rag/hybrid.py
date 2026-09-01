"""
Hybrid Search combiner using Reciprocal Rank Fusion (RRF).
Fuses Dense vector search results and Lexical BM25 results.
"""
from typing import List, Dict, Any
from backend.rag.vector_store import vector_store
from backend.rag.bm25 import bm25_retriever


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]], k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combines multiple ranked lists into a single ranked list using RRF:
    RRF_score(d) = sum(1 / (k + rank_i(d)))
    """
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            chunk_id = item["chunk_id"]
            if chunk_id not in doc_map:
                doc_map[chunk_id] = item.copy()

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0

            rrf_scores[chunk_id] += 1.0 / (k + rank)

    # Normalize RRF scores to 0-1 range
    if not rrf_scores:
        return []

    max_score = max(rrf_scores.values()) if rrf_scores else 1.0

    fused_results = []
    for chunk_id, total_score in rrf_scores.items():
        item = doc_map[chunk_id]
        norm_score = float(total_score / max_score)
        item["score"] = round(norm_score, 4)
        item["rrf_raw_score"] = total_score
        item["retriever"] = "hybrid_rrf"
        fused_results.append(item)

    fused_results.sort(key=lambda x: x["score"], reverse=True)
    return fused_results


class HybridRetriever:
    """Combines Qdrant Dense Vector search and BM25 Sparse search."""

    def __init__(self, dense_store=vector_store, sparse_store=bm25_retriever):
        self.dense_store = dense_store
        self.sparse_store = sparse_store

    def search(
        self,
        query: str,
        top_k: int = 8,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5,
        rrf_k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Executes dense and sparse searches in parallel/sequence and fuses candidate pools.
        """
        fetch_k = max(top_k * 2, 10)
        dense_results = self.dense_store.search_dense(query, top_k=fetch_k)
        sparse_results = self.sparse_store.search_sparse(query, top_k=fetch_k)

        fused = reciprocal_rank_fusion([dense_results, sparse_results], k=rrf_k)
        return fused[:top_k]


hybrid_retriever = HybridRetriever()
