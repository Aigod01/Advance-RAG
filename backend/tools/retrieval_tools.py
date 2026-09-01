"""
Retrieval tools providing configurable dense, sparse, hybrid, and reranked RAG searches.
"""
from typing import List, Dict, Any
from backend.rag.hybrid import hybrid_retriever
from backend.rag.vector_store import vector_store
from backend.rag.bm25 import bm25_retriever
from backend.rag.reranker import reranker


def search_internal_documents(
    query: str,
    strategy: str = "hybrid",  # "hybrid", "dense", "sparse"
    top_k: int = 6,
    use_reranker: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieves internal document chunks using the specified retrieval strategy.
    """
    if strategy == "dense":
        candidates = vector_store.search_dense(query, top_k=top_k * 2)
    elif strategy == "sparse":
        candidates = bm25_retriever.search_sparse(query, top_k=top_k * 2)
    else:  # hybrid
        candidates = hybrid_retriever.search(query, top_k=top_k * 2)

    if use_reranker and candidates:
        results = reranker.rerank(query, candidates, top_k=top_k)
    else:
        results = candidates[:top_k]

    return results
