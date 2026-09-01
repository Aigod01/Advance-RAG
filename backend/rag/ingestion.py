"""
Document Ingestion Pipeline.
Handles validation, text extraction, deduplication via SHA-256 hashes,
section-aware chunking, and dual indexing into Qdrant vector store & BM25.
"""
import os
import glob
import hashlib
import logging
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.rag.chunking import chunker, DocumentChunk
from backend.rag.vector_store import vector_store
from backend.rag.bm25 import bm25_retriever

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Manages document ingestion, deduplication, and indexing."""

    def __init__(self):
        self.indexed_files: Dict[str, Dict[str, Any]] = {}

    def extract_text_from_file(self, file_path: str) -> str:
        """Extracts text from markdown, txt, docx, or pdf files."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".md", ".txt", ".json", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = []
                for i, page in enumerate(reader.pages, start=1):
                    t = page.extract_text() or ""
                    pages_text.append(f"--- Page {i} ---\n{t}")
                return "\n\n".join(pages_text)
            except Exception as e:
                logger.error(f"PDF extraction error for {file_path}: {e}")
                return ""
        elif ext in [".docx", ".doc"]:
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                logger.error(f"DOCX extraction error for {file_path}: {e}")
                return ""
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def ingest_file(self, file_path: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Ingests a single file into the RAG system."""
        filename = os.path.basename(file_path)
        content = self.extract_text_from_file(file_path)
        if not content.strip():
            return {"status": "EMPTY", "filename": filename, "chunks": 0}

        # Compute content hash to prevent duplicate document indexing
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        doc_id = hashlib.md5(filename.encode("utf-8")).hexdigest()[:12]

        if doc_id in self.indexed_files and self.indexed_files[doc_id]["content_hash"] == content_hash:
            logger.info(f"File {filename} is already indexed with identical hash. Skipping.")
            return {
                "status": "ALREADY_INDEXED",
                "document_id": doc_id,
                "filename": filename,
                "chunks": self.indexed_files[doc_id]["chunks"],
            }

        # Chunk document
        chunks = chunker.chunk_document(
            text=content, filename=filename, document_id=doc_id, title=title
        )

        # Index into Qdrant & BM25
        vector_store.index_chunks(chunks)
        bm25_retriever.index_chunks(chunks)

        self.indexed_files[doc_id] = {
            "document_id": doc_id,
            "filename": filename,
            "title": title or filename.replace("_", " ").replace(".md", ""),
            "content_hash": content_hash,
            "chunks": len(chunks),
            "char_count": len(content),
            "path": file_path,
        }

        logger.info(f"Successfully indexed {filename} ({len(chunks)} chunks).")
        return {
            "status": "INDEXED",
            "document_id": doc_id,
            "filename": filename,
            "chunks": len(chunks),
        }

    def ingest_directory(self, dir_path: str = None) -> Dict[str, Any]:
        """Ingests all documents in directory."""
        target_dir = dir_path or os.path.join(settings.STORAGE_PATH, "documents")
        if not os.path.exists(target_dir):
            target_dir = os.path.join(os.getcwd(), "data", "documents")

        patterns = ["*.md", "*.txt", "*.pdf", "*.docx"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(target_dir, p)))

        results = []
        total_chunks = 0
        for f in files:
            res = self.ingest_file(f)
            results.append(res)
            total_chunks += res.get("chunks", 0)

        return {
            "total_files": len(files),
            "total_chunks": total_chunks,
            "qdrant_count": vector_store.count_chunks(),
            "bm25_count": bm25_retriever.count_chunks(),
            "files": list(self.indexed_files.values()),
        }

    def get_document_catalog(self) -> List[Dict[str, Any]]:
        """Returns list of indexed documents and their summary metadata."""
        return list(self.indexed_files.values())


ingestion_pipeline = IngestionPipeline()
