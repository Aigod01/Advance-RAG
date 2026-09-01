"""
Qdrant Vector Store wrapper for indexing and dense semantic similarity search.
Supports in-memory (concurrent safe), local directory, or remote Qdrant cluster.
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from backend.config import settings
from backend.rag.chunking import DocumentChunk
from backend.rag.embeddings import embedding_provider

logger = logging.getLogger(__name__)


class QdrantStore:
    """Manages Qdrant vector database operations with robust fallback."""

    def __init__(
        self,
        url: str = settings.QDRANT_URL,
        api_key: Optional[str] = settings.QDRANT_API_KEY,
        collection_name: str = settings.QDRANT_COLLECTION_NAME,
        vector_dim: int = settings.EMBEDDING_DIM,
    ):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self._init_client()

    def _init_client(self):
        try:
            if self.url == ":memory:":
                self.client = QdrantClient(location=":memory:")
            elif self.url.startswith("http://") or self.url.startswith("https://"):
                self.client = QdrantClient(url=self.url, api_key=self.api_key)
            else:
                try:
                    self.client = QdrantClient(path=self.url)
                except Exception as lock_err:
                    logger.warning(f"Qdrant file lock issue on {self.url} ({lock_err}). Using in-memory client.")
                    self.client = QdrantClient(location=":memory:")
        except Exception as e:
            logger.warning(f"Error initializing Qdrant client ({e}). Using in-memory fallback.")
            self.client = QdrantClient(location=":memory:")

        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.warning(f"Qdrant collection setup note: {e}")

    def index_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Embeds and indexes document chunks into Qdrant."""
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = embedding_provider.embed_documents(texts)

        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            point_id = abs(hash(chunk.chunk_id)) % (2**63 - 1)
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "filename": chunk.filename,
                "title": chunk.title,
                "page": chunk.page,
                "section": chunk.section,
                "content": chunk.content,
                "content_hash": chunk.content_hash,
                "metadata": chunk.metadata,
            }
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))

        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def search_dense(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Performs dense cosine vector similarity search."""
        query_vector = embedding_provider.embed_query(query)
        try:
            hits = []
            if hasattr(self.client, "search"):
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold if score_threshold > 0 else None,
                )
                for hit in results:
                    hits.append({
                        "chunk_id": hit.payload.get("chunk_id"),
                        "document_id": hit.payload.get("document_id"),
                        "filename": hit.payload.get("filename"),
                        "title": hit.payload.get("title"),
                        "page": hit.payload.get("page", 1),
                        "section": hit.payload.get("section", "General"),
                        "content": hit.payload.get("content", ""),
                        "score": float(hit.score),
                        "metadata": hit.payload.get("metadata", {}),
                        "retriever": "dense_qdrant",
                    })
            elif hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    score_threshold=score_threshold if score_threshold > 0 else None,
                )
                for hit in response.points:
                    hits.append({
                        "chunk_id": hit.payload.get("chunk_id"),
                        "document_id": hit.payload.get("document_id"),
                        "filename": hit.payload.get("filename"),
                        "title": hit.payload.get("title"),
                        "page": hit.payload.get("page", 1),
                        "section": hit.payload.get("section", "General"),
                        "content": hit.payload.get("content", ""),
                        "score": float(hit.score),
                        "metadata": hit.payload.get("metadata", {}),
                        "retriever": "dense_qdrant",
                    })
            return hits
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []

    def count_chunks(self) -> int:
        """Returns total indexed chunks in collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0


vector_store = QdrantStore()
