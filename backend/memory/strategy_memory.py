"""
Collaborative Retrieval Learning: Strategy Memory with Contextual-Bandit Strategy Selection.
Learns optimal retrieval parameters (retriever type, top_k, reranking) from recorded
critic scores, user feedback, latency, and success history.
"""
import json
import os
import random
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class StrategyEpisode:
    episode_id: str
    timestamp: str
    domain: str  # e.g., 'financial', 'operational', 'supply_chain', 'technical', 'market'
    question_type: str  # e.g., 'comparison', 'factual', 'aggregation', 'trend', 'cause_effect'
    original_query: str
    rewritten_query: Optional[str]
    agent: str  # 'document_agent', 'database_agent', 'web_agent'
    strategy: Dict[str, Any]  # e.g. {"retriever": "hybrid", "top_k": 8, "reranker": "cross_encoder"}
    critic_score: float
    user_feedback: Optional[int]  # +1, -1, or None
    latency_ms: float
    success: bool
    retries_needed: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StrategyMemory:
    """
    Experience & Strategy memory engine that models retrieval configuration selection
    as a contextual bandit problem with exploration and exploitation.
    """

    def __init__(self, persistence_file: str = None):
        self.persistence_file = persistence_file or os.path.join(
            settings.STORAGE_PATH, "strategy_memory.json"
        )
        self.episodes: List[StrategyEpisode] = []
        self.exploration_rate: float = 0.15  # epsilon for exploration vs exploitation
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.episodes = [StrategyEpisode(**item) for item in data]
                logger.info(f"Loaded {len(self.episodes)} strategy episodes from {self.persistence_file}")
            except Exception as e:
                logger.warning(f"Could not load strategy memory: {e}")
                self._seed_default_experience()
        else:
            self._seed_default_experience()

    def _save_memory(self):
        try:
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in self.episodes], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving strategy memory: {e}")

    def _seed_default_experience(self):
        """Pre-seeds prior baseline experience so system starts with intelligent defaults."""
        seed_episodes = [
            StrategyEpisode(
                episode_id="seed_1",
                timestamp=datetime.utcnow().isoformat(),
                domain="financial",
                question_type="comparison",
                original_query="Why did revenue fall last quarter?",
                rewritten_query="Q3 2025 revenue decline laptop division Shinra delay",
                agent="document_agent",
                strategy={"retriever": "hybrid", "top_k": 8, "reranker": "cross_encoder"},
                critic_score=0.92,
                user_feedback=1,
                latency_ms=240.0,
                success=True,
                retries_needed=0,
            ),
            StrategyEpisode(
                episode_id="seed_2",
                timestamp=datetime.utcnow().isoformat(),
                domain="market",
                question_type="trend",
                original_query="Laptop industry global shipment trends",
                rewritten_query="global laptop market shipment trend 2025 2026 decline percentage",
                agent="web_agent",
                strategy={"retriever": "web_search", "top_k": 5, "reranker": "heuristic"},
                critic_score=0.88,
                user_feedback=1,
                latency_ms=450.0,
                success=True,
                retries_needed=0,
            ),
            StrategyEpisode(
                episode_id="seed_3",
                timestamp=datetime.utcnow().isoformat(),
                domain="financial",
                question_type="aggregation",
                original_query="Calculate laptop revenue in Q2 vs Q3",
                rewritten_query="SELECT category, SUM(unit_price * quantity) FROM sales",
                agent="database_agent",
                strategy={"retriever": "sql_query", "top_k": 100, "reranker": "none"},
                critic_score=0.98,
                user_feedback=1,
                latency_ms=65.0,
                success=True,
                retries_needed=0,
            ),
        ]
        self.episodes.extend(seed_episodes)
        self._save_memory()

    def classify_query_intent(self, query: str) -> Dict[str, str]:
        """Classifies query domain and question type."""
        q = query.lower()

        # Domain
        if any(w in q for w in ["revenue", "sales", "profit", "margin", "quarter", "q1", "q2", "q3", "q4", "cost", "price"]):
            domain = "financial"
        elif any(w in q for w in ["supply", "supplier", "chip", "factory", "delay", "shortage", "logistics"]):
            domain = "supply_chain"
        elif any(w in q for w in ["market", "industry", "competitor", "global", "trend", "macro", "sector"]):
            domain = "market"
        elif any(w in q for w in ["spec", "firmware", "ram", "processor", "gpu", "battery", "display"]):
            domain = "technical"
        else:
            domain = "general"

        # Question Type
        if any(w in q for w in ["compare", "vs", "versus", "difference", "differ"]):
            qtype = "comparison"
        elif any(w in q for w in ["how much", "total", "sum", "average", "count", "highest", "lowest", "max", "min"]):
            qtype = "aggregation"
        elif any(w in q for w in ["why", "reason", "cause", "explain", "factor", "driver"]):
            qtype = "cause_effect"
        elif any(w in q for w in ["trend", "forecast", "outlook", "projection", "growing"]):
            qtype = "trend"
        else:
            qtype = "factual"

        return {"domain": domain, "question_type": qtype}

    def compute_strategy_score(
        self, episode: StrategyEpisode, target_domain: str, target_qtype: str
    ) -> float:
        """
        Calculates blueprint strategy score formula:
        strategy_score = historical_success * domain_similarity * question_type_similarity * source_reliability
        """
        domain_sim = 1.0 if episode.domain == target_domain else 0.4
        qtype_sim = 1.0 if episode.question_type == target_qtype else 0.5
        source_rel = 0.95  # baseline reliability

        # Historical success: critic score weighted with user feedback and retry penalty
        feedback_multiplier = 1.2 if episode.user_feedback == 1 else (0.6 if episode.user_feedback == -1 else 1.0)
        retry_penalty = max(0.4, 1.0 - (episode.retries_needed * 0.25))

        historical_success = (episode.critic_score * feedback_multiplier * retry_penalty)

        score = historical_success * domain_sim * qtype_sim * source_rel
        return round(float(score), 4)

    def recommend_strategy(
        self, query: str, agent_name: str = "document_agent"
    ) -> Dict[str, Any]:
        """
        Selects optimal retrieval strategy using Contextual Bandit formulation with epsilon-exploration.
        """
        intent = self.classify_query_intent(query)
        domain = intent["domain"]
        qtype = intent["question_type"]

        # Epsilon-greedy exploration
        if random.random() < self.exploration_rate and len(self.episodes) > 5:
            # Explore alternative candidate configuration
            candidate_retrievers = ["hybrid", "dense", "sparse"]
            chosen_retriever = random.choice(candidate_retrievers)
            chosen_top_k = random.choice([5, 8, 10])
            chosen_reranker = random.choice(["cross_encoder", "heuristic"])
            return {
                "retriever": chosen_retriever,
                "top_k": chosen_top_k,
                "reranker": chosen_reranker,
                "domain": domain,
                "question_type": qtype,
                "mode": "exploration",
                "predicted_score": 0.75,
            }

        # Exploitation: find highest-scoring strategy from history for this agent
        agent_episodes = [e for e in self.episodes if e.agent == agent_name]
        if not agent_episodes:
            # Default strong fallback strategy
            return {
                "retriever": "hybrid",
                "top_k": 8,
                "reranker": "cross_encoder",
                "domain": domain,
                "question_type": qtype,
                "mode": "default",
                "predicted_score": 0.85,
            }

        best_score = -1.0
        best_strategy = None

        for ep in agent_episodes:
            score = self.compute_strategy_score(ep, domain, qtype)
            if score > best_score:
                best_score = score
                best_strategy = ep.strategy.copy()

        if best_strategy is None:
            best_strategy = {"retriever": "hybrid", "top_k": 8, "reranker": "cross_encoder"}

        return {
            **best_strategy,
            "domain": domain,
            "question_type": qtype,
            "mode": "exploitation",
            "predicted_score": best_score if best_score > 0 else 0.85,
        }

    def record_outcome(
        self,
        query: str,
        agent: str,
        strategy: Dict[str, Any],
        critic_score: float,
        latency_ms: float,
        retries_needed: int,
        rewritten_query: Optional[str] = None,
        user_feedback: Optional[int] = None,
    ) -> StrategyEpisode:
        """Records an execution episode to learn from measured outcomes."""
        intent = self.classify_query_intent(query)
        episode_id = f"ep_{int(datetime.utcnow().timestamp() * 1000)}"

        success = critic_score >= 0.70

        episode = StrategyEpisode(
            episode_id=episode_id,
            timestamp=datetime.utcnow().isoformat(),
            domain=intent["domain"],
            question_type=intent["question_type"],
            original_query=query,
            rewritten_query=rewritten_query,
            agent=agent,
            strategy={
                "retriever": strategy.get("retriever", "hybrid"),
                "top_k": strategy.get("top_k", 8),
                "reranker": strategy.get("reranker", "cross_encoder"),
            },
            critic_score=round(critic_score, 4),
            user_feedback=user_feedback,
            latency_ms=round(latency_ms, 2),
            success=success,
            retries_needed=retries_needed,
        )

        self.episodes.append(episode)
        # Keep last 1000 episodes
        if len(self.episodes) > 1000:
            self.episodes = self.episodes[-1000:]

        self._save_memory()
        logger.info(f"Recorded strategy outcome: episode={episode_id}, score={critic_score:.2f}")
        return episode

    def apply_user_feedback(self, run_id: str, feedback: int):
        """Updates user feedback on recorded episode and persists memory."""
        updated = False
        for ep in reversed(self.episodes):
            # Match recent run
            if ep.user_feedback is None:
                ep.user_feedback = feedback
                updated = True
                break

        if updated:
            self._save_memory()

    def get_strategy_summary(self) -> Dict[str, Any]:
        """Provides summary metrics of strategy memory for dashboard."""
        if not self.episodes:
            return {"total_episodes": 0, "avg_critic_score": 0.0, "success_rate": 0.0}

        total = len(self.episodes)
        avg_score = sum(e.critic_score for e in self.episodes) / total
        successes = sum(1 for e in self.episodes if e.success)
        avg_latency = sum(e.latency_ms for e in self.episodes) / total

        # Strategy breakdown
        retriever_counts = {}
        for e in self.episodes:
            r = e.strategy.get("retriever", "hybrid")
            retriever_counts[r] = retriever_counts.get(r, 0) + 1

        return {
            "total_episodes": total,
            "avg_critic_score": round(avg_score, 3),
            "success_rate": round(successes / total, 3),
            "avg_latency_ms": round(avg_latency, 1),
            "retriever_distribution": retriever_counts,
            "recent_episodes": [e.to_dict() for e in self.episodes[-10:]],
        }


strategy_memory = StrategyMemory()
