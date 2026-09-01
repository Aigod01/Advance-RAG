"""
Document tools for inspecting indexed corpus and chunk metadata.
"""
from typing import List, Dict, Any
from backend.rag.ingestion import ingestion_pipeline


def get_indexed_documents() -> List[Dict[str, Any]]:
    """Returns all indexed corporate documents in the catalog."""
    return ingestion_pipeline.get_document_catalog()
