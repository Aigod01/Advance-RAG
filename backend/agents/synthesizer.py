"""
Synthesizer Agent: Generates fully grounded answers with structured citations,
contradiction surfacing, and calibrated confidence computation.
"""
import re
import logging
from typing import Dict, Any, List, Tuple
from backend.llm.provider import llm_provider

logger = logging.getLogger(__name__)

SYNTHESIZER_SYSTEM_PROMPT = """You are the Grounded Synthesis Agent for an enterprise Multi-Agent Collaborative RAG system.
Your job is to synthesize an authoritative, structured, and factually grounded response to the user query using strictly the accepted evidence provided.

CRITICAL SYNTHESIS RULES:
1. CITATION INTEGRITY: Every factual statement, number, or claim MUST have an inline citation anchor:
   - For database results: [SQL: <query_or_table>]
   - For internal documents: [Doc: <filename>#P<page>]
   - For external web sources: [Web: <domain_or_url>]
2. CONTRADICTION HANDLING: If there is any discrepancy between data sources (e.g. database sales vs executive report), explicitly explain the difference and note if definitions/dates differ.
3. UNCERTAINTY & ABSTENTION: If evidence is insufficient for any sub-question, explicitly state what could not be determined.
4. STRUCTURE: Use markdown headings, bullet points, and tables to present clear executive takeaways.
"""


def calculate_calibrated_confidence(
    evidence_list: List[Dict[str, Any]],
    critic_score: float,
    citation_count: int,
    conflicts: List[Any],
) -> float:
    """
    Computes mathematically calibrated confidence score based on observable signals:
    Confidence = 0.35 * avg_relevance + 0.35 * critic_score + 0.20 * source_agreement + 0.10 * citation_coverage
    """
    if not evidence_list:
        return 0.20

    # 1. Average relevance of evidence
    relevance_scores = [float(e.get("relevance_score", 0.7)) for e in evidence_list]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5

    # 2. Source agreement (penalize if unresolved conflicts exist)
    conflict_penalty = len(conflicts) * 0.15
    source_agreement = max(0.2, 1.0 - conflict_penalty)

    # 3. Citation coverage ratio
    citation_coverage = min(1.0, citation_count / 3.0)

    # Calibrated linear combination
    confidence = (
        0.35 * avg_relevance
        + 0.35 * critic_score
        + 0.20 * source_agreement
        + 0.10 * citation_coverage
    )

    return round(float(min(0.99, max(0.10, confidence))), 3)


class SynthesizerAgent:
    """Combines verified evidence into grounded answers with citations and confidence metrics."""

    def __init__(self, llm=llm_provider):
        self.llm = llm

    def synthesize(
        self,
        user_query: str,
        evidence_list: List[Dict[str, Any]],
        critic_result: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generates grounded answer and citation claims."""
        critic_data = critic_result or {"score": 0.85, "conflicts": []}

        # Build evidence text for prompt
        evidence_text_blocks = []
        for i, ev in enumerate(evidence_list, start=1):
            src_type = ev.get("source_type", "document")
            citation = ev.get("citation", f"source_{i}")
            content = ev.get("content", "")
            meta = ev.get("metadata", {})
            evidence_text_blocks.append(f"[{i}] SOURCE TYPE: {src_type.upper()} | CITATION: {citation}\nCONTENT: {content}\n")

        evidence_corpus = "\n".join(evidence_text_blocks)

        prompt = f"""User Question:
"{user_query}"

Accepted Evidence:
{evidence_corpus}

Synthesize a comprehensive, executive-ready grounded answer. Include explicit citations [SQL: ...], [Doc: ...], and [Web: ...]."""

        try:
            answer = self.llm.generate(prompt, system_prompt=SYNTHESIZER_SYSTEM_PROMPT, temperature=0.1)
        except Exception as e:
            logger.error(f"Synthesis generation error: {e}")
            answer = "Unable to synthesize answer due to generation error."

        # Extract citations from answer
        citations_found = re.findall(r"\[(Doc|SQL|Web):\s*([^\]]+)\]", answer)
        formatted_citations = [
            {"source_type": c[0].lower(), "source_id": c[1].strip(), "raw_tag": f"[{c[0]}: {c[1]}]"}
            for c in citations_found
        ]

        # Calculate calibrated confidence
        confidence = calculate_calibrated_confidence(
            evidence_list=evidence_list,
            critic_score=critic_data.get("score", 0.85),
            citation_count=len(formatted_citations),
            conflicts=critic_data.get("conflicts", []),
        )

        return {
            "answer": answer,
            "citations": formatted_citations,
            "citation_count": len(formatted_citations),
            "confidence": confidence,
            "abstention": confidence < 0.40,
        }


synthesizer_agent = SynthesizerAgent()
