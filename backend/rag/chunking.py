"""
Section-aware chunking engine that preserves table integrity, heading hierarchies,
and page boundaries for accurate Document RAG.
"""
import re
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    filename: str
    title: str
    page: int
    section: str
    content: str
    content_hash: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SectionAwareChunker:
    """
    Intelligently splits Markdown and Text files by sections, preserving tables
    and preventing small fragment leakage.
    """

    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        text: str,
        filename: str,
        document_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> List[DocumentChunk]:
        """Splits document text into metadata-enriched chunks."""
        doc_id = document_id or hashlib.md5(filename.encode("utf-8")).hexdigest()[:12]
        doc_title = title or filename.replace("_", " ").replace(".md", "").replace(".txt", "")

        # Split into pages if page markers exist
        pages = re.split(r"(?:---\s*Page\s*(\d+)\s*---)", text, flags=re.IGNORECASE)
        page_chunks: List[DocumentChunk] = []

        if len(pages) > 1:
            # First element might be header before Page 1
            current_page = 1
            idx = 0
            while idx < len(pages):
                part = pages[idx].strip()
                if not part:
                    idx += 1
                    continue
                # If this part is a page number token
                if part.isdigit() and idx + 1 < len(pages):
                    current_page = int(part)
                    page_content = pages[idx + 1].strip()
                    chunks = self._chunk_page_content(page_content, doc_id, filename, doc_title, current_page)
                    page_chunks.extend(chunks)
                    idx += 2
                else:
                    chunks = self._chunk_page_content(part, doc_id, filename, doc_title, current_page)
                    page_chunks.extend(chunks)
                    idx += 1
        else:
            page_chunks = self._chunk_page_content(text, doc_id, filename, doc_title, page=1)

        # Fallback if empty
        if not page_chunks and text.strip():
            c_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            page_chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc_id}_c0",
                    document_id=doc_id,
                    filename=filename,
                    title=doc_title,
                    page=1,
                    section="General",
                    content=text.strip(),
                    content_hash=c_hash,
                    metadata={"char_count": len(text.strip())},
                )
            )

        # _chunk_page_content() resets its local chunk_seq counter to 0 on every
        # call, so when chunk_document() invokes it more than once for the same
        # document (multiple page segments), chunk_ids can collide (e.g. two
        # different chunks both named "{doc_id}_p1_c0"). That silently drops
        # data: Qdrant upserts by point id derived from chunk_id, so a colliding
        # chunk overwrites the previous one instead of being stored alongside
        # it. Renumber to a flat, per-document sequence so every chunk_id is
        # guaranteed unique regardless of how many page segments were produced;
        # the page number itself is preserved separately on each chunk.
        for i, ch in enumerate(page_chunks):
            ch.chunk_id = f"{doc_id}_c{i}"

        return page_chunks

    def _chunk_page_content(
        self, content: str, doc_id: str, filename: str, title: str, page: int
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        # Split by markdown headers (#, ##, ###) while retaining headers
        sections = re.split(r"(?=(?:^|\n)#{1,3}\s+)", content)

        chunk_seq = 0
        for section_block in sections:
            section_block = section_block.strip()
            if not section_block:
                continue

            # Extract section heading if present
            heading_match = re.match(r"^#{1,3}\s+(.+)$", section_block, flags=re.MULTILINE)
            section_name = heading_match.group(1).strip() if heading_match else "Overview"

            # Check if section contains a table (Markdown table starts with |)
            # We preserve tables intact to avoid destroying structured row relations!
            if "|" in section_block and re.search(r"\|.*\|.*\n\s*\|[-:| ]+\|", section_block):
                # Contains a table: keep whole section or table unit together
                c_hash = hashlib.sha256(section_block.encode("utf-8")).hexdigest()
                chunk_id = f"{doc_id}_p{page}_c{chunk_seq}"
                chunk_seq += 1
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        filename=filename,
                        title=title,
                        page=page,
                        section=section_name,
                        content=section_block,
                        content_hash=c_hash,
                        metadata={"has_table": True, "char_count": len(section_block)},
                    )
                )
            elif len(section_block) > self.target_chunk_size * 2:
                # Sub-split long text paragraphs while keeping sentences together
                paragraphs = re.split(r"\n\s*\n", section_block)
                current_sub = ""
                for p in paragraphs:
                    p = p.strip()
                    if not p:
                        continue
                    if len(current_sub) + len(p) < self.target_chunk_size:
                        current_sub = f"{current_sub}\n\n{p}".strip()
                    else:
                        if current_sub:
                            c_hash = hashlib.sha256(current_sub.encode("utf-8")).hexdigest()
                            chunk_id = f"{doc_id}_p{page}_c{chunk_seq}"
                            chunk_seq += 1
                            chunks.append(
                                DocumentChunk(
                                    chunk_id=chunk_id,
                                    document_id=doc_id,
                                    filename=filename,
                                    title=title,
                                    page=page,
                                    section=section_name,
                                    content=f"## {section_name}\n\n{current_sub}" if not current_sub.startswith("#") else current_sub,
                                    content_hash=c_hash,
                                    metadata={"has_table": False, "char_count": len(current_sub)},
                                )
                            )
                        current_sub = p

                if current_sub:
                    c_hash = hashlib.sha256(current_sub.encode("utf-8")).hexdigest()
                    chunk_id = f"{doc_id}_p{page}_c{chunk_seq}"
                    chunk_seq += 1
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=doc_id,
                            filename=filename,
                            title=title,
                            page=page,
                            section=section_name,
                            content=f"## {section_name}\n\n{current_sub}" if not current_sub.startswith("#") else current_sub,
                            content_hash=c_hash,
                            metadata={"has_table": False, "char_count": len(current_sub)},
                        )
                    )
            else:
                c_hash = hashlib.sha256(section_block.encode("utf-8")).hexdigest()
                chunk_id = f"{doc_id}_p{page}_c{chunk_seq}"
                chunk_seq += 1
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        filename=filename,
                        title=title,
                        page=page,
                        section=section_name,
                        content=section_block,
                        content_hash=c_hash,
                        metadata={"has_table": False, "char_count": len(section_block)},
                    )
                )

        return chunks


chunker = SectionAwareChunker()
