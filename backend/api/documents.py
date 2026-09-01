"""
Document management and ingestion endpoints.
"""
import os
import shutil
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from backend.rag.ingestion import ingestion_pipeline
from backend.config import settings

router = APIRouter(prefix="/api/documents", tags=["Document Management"])


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    title: str
    chunks: int
    char_count: int


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
):
    """Uploads and indexes a document (PDF, Markdown, TXT, DOCX) into Qdrant & BM25."""
    allowed_exts = [".pdf", ".md", ".txt", ".docx", ".doc", ".json", ".csv"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Allowed: {', '.join(allowed_exts)}",
        )

    # Save to disk
    save_dir = os.path.join(settings.STORAGE_PATH, "documents")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingest file
    result = ingestion_pipeline.ingest_file(file_path, title=title)
    return result


@router.get("", response_model=List[Dict[str, Any]])
async def list_documents():
    """Lists all indexed corporate documents and chunk stats."""
    return ingestion_pipeline.get_document_catalog()


@router.post("/reindex")
async def reindex_all_documents():
    """Triggers complete re-ingestion of the documents folder."""
    return ingestion_pipeline.ingest_directory()
