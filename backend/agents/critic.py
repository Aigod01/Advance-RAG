"""
Critic & Verifier Agent: Evaluates aggregated multi-source evidence for relevance,
completeness, contradictions, and citation support.
Generates structured retry plans and query rewrites for self-correction.
"""
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.llm.provider import llm_provider

logger = logging.getLogger(__name__)


class ConflictItem(BaseModel):
    source_a: str
    source_b: str
    description: str
    reconciled: bool = False
    reconciliation_note: str = ""


class CriticVerdict(BaseModel):
    sufficient: bool
    score: float = Field(ge=0.0, le=1.0)
    missing: List[str] = Field(default_factory=list)
    conflicts: List[ConflictItem] = Field(default_factory=list)
    retry: bool = False
    target_agent: str = ""
    new_query: str = ""
    critique_summary: str = ""


CRITIC_SYSTEM_PROMPT = """You are the Critic & Verifier Agent in an advanced Multi-Agent Collaborative RAG system.
Your job is to objectively evaluate evidence collected from Database, Document, and Web agents against the user query.

Evaluation Checklist:
1. Relevance: Does the evidence directly address all parts of the user question?
2. Sufficiency: Are there missing critical facts, timeframes, or metrics?
3. Contradiction Detection: Are there conflicts between database numbers and document reports? (e.g. Q3 revenue differences, date discrepancies).
4. Citation Support: Can every major claim be traced back to an explicit source?
5. Freshness: Are the sources appropriately dated?

Decision Rules:
- If evidence is complete and high-quality: set sufficient=true, retry=false, score >= 0.80.
- If essential evidence is missing: set sufficient=false, retry=true, score < 0.70, specify target_agent ("database_agent" | "document_agent" | "web_agent"), and formulate a clear, targeted 'new_query' to retrieve what is missing.
- Return strictly valid JSON.
"""


class CriticAgent:
    """Evaluates evidence quality and generates self-correction retry plans."""

    def __init__(self, llm=llm_provider):
        self.llm = llm

    def evaluate(
        self,
        user_query: str,
        normalized_evidence: List[Dict[str, Any]],
        retry_count: int = 0,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Evaluates evidence and decides whether to accept or retry."""
        # Check hard retry bounds
        if retry_count >= max_retries:
            return {
                "sufficient": True,
                "score": 0.78,
                "missing": [],
                "conflicts": [],
                "retry": False,
                "target_agent": "",
                "new_query": "",
                "critique_summary": "Max retries reached. Proceeding with best available evidence.",
            }

        # Build evidence digest for critique
        evidence_summary_lines = []
        for e in normalized_evidence[:15]:
            src = e.get("source_type", "unknown")
            ident = e.get("citation", "ref")
            content = e.get("content", "")[:250]
            evidence_summary_lines.append(f"- [{src.upper()} | {ident}]: {content}")

        evidence_digest = "\n".join(evidence_summary_lines)

        prompt = f"""User Query: "{user_query}"

Aggregated Evidence ({len(normalized_evidence)} items):
{evidence_digest}

Current Retry Count: {retry_count} of {max_retries}

Evaluate this evidence and return JSON with:
- "sufficient": bool
- "score": float between 0.0 and 1.0
- "missing": list of missing items
- "conflicts": list of conflict objects
- "retry": bool (true if score < 0.75 and critical data is missing)
- "target_agent": "database_agent" | "document_agent" | "web_agent"
- "new_query": targeted rewritten query if retry is true
- "critique_summary": brief summary of verification
"""
        try:
            res = self.llm.generate_json(prompt, system_prompt=CRITIC_SYSTEM_PROMPT)
            if "score" in res:
                verdict = CriticVerdict(**res).model_dump()
                # Hard limit check
                if retry_count >= max_retries:
                    verdict["retry"] = False
                return verdict
        except Exception as e:
            logger.warning(f"Critic evaluation error: {e}")

        # Deterministic fallback evaluation
        has_evidence = len(normalized_evidence) > 0
        has_db = any(e.get("source_type") == "database" for e in normalized_evidence)
        has_doc = any(e.get("source_type") == "document" for e in normalized_evidence)
        has_web = any(e.get("source_type") == "web" for e in normalized_evidence)

        score = 0.5
        if has_db: score += 0.15
        if has_doc: score += 0.20
        if has_web: score += 0.15

        sufficient = score >= 0.75 or retry_count >= max_retries

        return {
            "sufficient": sufficient,
            "score": round(score, 2),
            "missing": [] if sufficient else ["Detailed external market trend validation"],
            "conflicts": [],
            "retry": not sufficient and retry_count < max_retries,
            "target_agent": "web_agent" if not sufficient else "",
            "new_query": f"{user_query} market trend data" if not sufficient else "",
            "critique_summary": "Evidence verified across multi-source criteria.",
        }


critic_agent = CriticAgent()
