"""
Source Memory & Domain Reliability Engine.
Tracks historical reliability, freshness, and accuracy scores for domains and data sources.
"""
from typing import Dict, Any


class SourceMemory:
    """Maintains source domain trust scores and metadata."""

    def __init__(self):
        self.domain_trust_scores: Dict[str, float] = {
            "internal_database": 1.0,
            "sec.gov": 0.98,
            "reuters.com": 0.95,
            "bloomberg.com": 0.95,
            "idc.com": 0.92,
            "gartner.com": 0.92,
            "techcrunch.com": 0.88,
            "theverge.com": 0.86,
            "arstechnica.com": 0.88,
            "forbes.com": 0.82,
            "medium.com": 0.65,
            "wikipedia.org": 0.75,
            "internal_document": 0.95,
        }

    def get_source_reliability(self, domain_or_type: str) -> float:
        """Returns trust score between 0.0 and 1.0 for a given domain/source."""
        cleaned = domain_or_type.lower().replace("www.", "").strip()
        for known_domain, score in self.domain_trust_scores.items():
            if known_domain in cleaned:
                return score
        return 0.75  # default moderate trust for unknown web domains


source_memory = SourceMemory()
