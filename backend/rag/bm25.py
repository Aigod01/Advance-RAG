"""
Lexical BM25 Indexer and Retriever using Okapi BM25 algorithm.
"""
import re
import math
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from backend.rag.chunking import DocumentChunk


def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenization and lowercase normalization."""
    return re.findall(r"\b[a-zA-Z0-9_\-\$]+\b", text.lower())


class BM25Retriever:
    """In-memory BM25 indexer for lexical keyword retrieval."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.corpus_tokens: List[List[str]] = []
        self.bm25: BM25Okapi = None

    def index_chunks(self, chunks: List[DocumentChunk]):
        """Builds or extends the BM25 index."""
        if not chunks:
            return

        # Deduplicate existing chunk_ids
        existing_ids = {c.chunk_id for c in self.chunks}
        new_chunks = [c for c in chunks if c.chunk_id not in existing_ids]

        self.chunks.extend(new_chunks)
        self.corpus_tokens = [tokenize(f"{c.title} {c.section} {c.content}") for c in self.chunks]
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)

    def search_sparse(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches BM25 index and returns ranked list with normalized scores."""
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0

        # Pair scores with chunks
        scored_pairs: List[Tuple[float, DocumentChunk]] = [
            (score, self.chunks[i]) for i, score in enumerate(scores) if score > 0.0
        ]
        scored_pairs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, chunk in scored_pairs[:top_k]:
            normalized_score = float(score / max_score)
            results.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "title": chunk.title,
                "page": chunk.page,
                "section": chunk.section,
                "content": chunk.content,
                "score": round(normalized_score, 4),
                "raw_score": float(score),
                "metadata": chunk.metadata,
                "retriever": "sparse_bm25",
            })
        return results

    def count_chunks(self) -> int:
        return len(self.chunks)


bm25_retriever = BM25Retriever()
