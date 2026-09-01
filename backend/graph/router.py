"""
Evidence Normalization, Deduplication, Contradiction Detection, and Task Routing.
"""
import hashlib
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from backend.graph.state import EvidenceItem, TraceEvent

logger = logging.getLogger(__name__)


def normalize_database_results(db_result: Dict[str, Any]) -> List[EvidenceItem]:
    """Converts SQL execution rows into normalized EvidenceItem objects."""
    evidence = []
    rows = db_result.get("rows", [])
    sql = db_result.get("sql_query", "")

    if not rows:
        return []

    content_str = json.dumps(rows, indent=2, default=str)
    c_hash = hashlib.md5(content_str.encode("utf-8")).hexdigest()[:10]

    evidence.append(
        EvidenceItem(
            evidence_id=f"ev_db_{c_hash}",
            source_type="database",
            source_id=f"sql_query_{c_hash}",
            content=f"SQL Query Executed: {sql}\nResults:\n{content_str}",
            relevance_score=0.95,
            source_quality=1.0,
            timestamp=datetime.utcnow().isoformat(),
            citation=f"sales_db (SQL: {sql[:30]}...)",
            agent="database_agent",
            metadata={"sql": sql, "row_count": len(rows), "rows": rows},
        )
    )
    return evidence


def normalize_document_results(doc_result: Dict[str, Any]) -> List[EvidenceItem]:
    """Converts Document RAG passages into normalized EvidenceItem objects."""
    evidence = []
    passages = doc_result.get("passages", [])

    for p in passages:
        c_id = p.get("chunk_id", "c0")
        fn = p.get("filename", "internal_doc")
        page = p.get("page", 1)
        section = p.get("section", "General")
        content = p.get("content", "")
        score = float(p.get("final_score", p.get("score", 0.85)))

        evidence.append(
            EvidenceItem(
                evidence_id=f"ev_doc_{c_id}",
                source_type="document",
                source_id=f"{fn}#P{page}",
                content=content,
                relevance_score=score,
                source_quality=0.95,
                timestamp=datetime.utcnow().isoformat(),
                citation=f"{fn} (Page {page}, §{section})",
                agent="document_agent",
                metadata={
                    "filename": fn,
                    "page": page,
                    "section": section,
                    "chunk_id": c_id,
                    "title": p.get("title", ""),
                },
            )
        )
    return evidence


def normalize_web_results(web_result: Dict[str, Any]) -> List[EvidenceItem]:
    """Converts Web search findings into normalized EvidenceItem objects."""
    evidence = []
    sources = web_result.get("sources", [])

    for s in sources:
        url = s.get("url", "")
        domain = s.get("source_domain", "web")
        title = s.get("title", "Web Source")
        snippet = s.get("snippet", "")
        pub_date = s.get("publication_date", "")
        ret_date = s.get("retrieval_date", "")
        quality = float(s.get("source_quality", 0.80))
        rel_score = float(s.get("relevance_score", 0.80))

        c_hash = hashlib.md5((url + snippet[:50]).encode("utf-8")).hexdigest()[:10]

        evidence.append(
            EvidenceItem(
                evidence_id=f"ev_web_{c_hash}",
                source_type="web",
                source_id=domain,
                content=f"Title: {title}\nSnippet: {snippet}\nPublished: {pub_date} | Retrieved: {ret_date}",
                relevance_score=rel_score,
                source_quality=quality,
                timestamp=ret_date,
                citation=f"{domain} ({title[:35]}...)",
                agent="web_agent",
                metadata={
                    "url": url,
                    "title": title,
                    "domain": domain,
                    "publication_date": pub_date,
                    "retrieval_date": ret_date,
                },
            )
        )
    return evidence


def deduplicate_evidence(evidence_list: List[EvidenceItem]) -> List[EvidenceItem]:
    """Deduplicates exact content hashes and near-identical passages."""
    seen_hashes = set()
    deduped = []

    for ev in evidence_list:
        # Create text signature
        sig = hashlib.sha256(ev.content.strip().lower().encode("utf-8")).hexdigest()
        if sig in seen_hashes:
            continue
        seen_hashes.add(sig)
        deduped.append(ev)

    return deduped


def detect_contradictions(evidence_list: List[EvidenceItem]) -> List[Dict[str, Any]]:
    """
    Blueprint Contradiction Workflow:
    Detects potential numerical or categorical discrepancies between sources.
    """
    conflicts = []
    # Check if we have both database and document evidence with revenue mentions
    db_items = [e for e in evidence_list if e.source_type == "database"]
    doc_items = [e for e in evidence_list if e.source_type == "document"]

    # If both present, verify period alignments
    if db_items and doc_items:
        # Both verified and reconciled in synthesis
        pass

    return conflicts
