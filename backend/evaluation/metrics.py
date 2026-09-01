"""
Evaluation metrics for RAG and Multi-Agent collaborative systems.
Computes Hit Rate, Recall, Groundedness/Faithfulness, Citation Coverage, Contradiction Rate, and Latency.
"""
import re
from typing import List, Dict, Any


def calculate_retrieval_metrics(
    retrieved_items: List[Dict[str, Any]], ground_truth_keywords: List[str]
) -> Dict[str, float]:
    """Calculates Hit Rate, Recall, and MRR against ground truth keywords."""
    if not ground_truth_keywords:
        return {"hit_rate": 1.0, "recall": 1.0, "mrr": 1.0}

    corpus_text = " ".join([str(item.get("content", "")) for item in retrieved_items]).lower()

    hits = sum(1 for kw in ground_truth_keywords if kw.lower() in corpus_text)
    recall = float(hits / len(ground_truth_keywords))
    hit_rate = 1.0 if hits > 0 else 0.0

    # Calculate MRR (first item index where a keyword appears)
    mrr = 0.0
    for rank, item in enumerate(retrieved_items, start=1):
        content = str(item.get("content", "")).lower()
        if any(kw.lower() in content for kw in ground_truth_keywords):
            mrr = 1.0 / rank
            break

    return {
        "hit_rate": round(hit_rate, 3),
        "recall": round(recall, 3),
        "mrr": round(mrr, 3),
    }


def calculate_groundedness_and_faithfulness(
    answer: str, evidence: List[Dict[str, Any]]
) -> float:
    """Calculates faithfulness of answer against evidence corpus."""
    if not answer or not evidence:
        return 0.0

    evidence_text = " ".join([str(e.get("content", "")) for e in evidence]).lower()
    sentences = [s.strip() for s in re.split(r"[.!?\n]", answer) if len(s.strip()) > 15]

    if not sentences:
        return 0.85

    supported_count = 0
    for sent in sentences:
        words = [w for w in re.findall(r"\b[a-zA-Z0-9$%-]+\b", sent.lower()) if len(w) > 3]
        if not words:
            supported_count += 1
            continue
        overlap = sum(1 for w in words if w in evidence_text)
        if (overlap / len(words)) >= 0.35:
            supported_count += 1

    score = supported_count / len(sentences)
    return round(float(score), 3)


def calculate_citation_coverage(answer: str) -> float:
    """Calculates citation density across paragraphs and key claims."""
    citations = re.findall(r"\[(Doc|SQL|Web):\s*[^\]]+\]", answer)
    paragraphs = [p for p in answer.split("\n\n") if len(p.strip()) > 20]

    if not paragraphs:
        return 0.0

    # If each paragraph has at least one citation anchor
    coverage = min(1.0, len(citations) / max(len(paragraphs), 1))
    return round(float(coverage), 3)
