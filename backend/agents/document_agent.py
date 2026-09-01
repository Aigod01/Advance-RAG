"""
Document RAG Agent: Ingests and retrieves internal documents using adaptive hybrid search & reranking.
Consults Strategy Memory for dynamically learned retrieval parameters.
"""
import time
import logging
from typing import Dict, Any, List
from backend.tools.retrieval_tools import search_internal_documents
from backend.memory.strategy_memory import strategy_memory
from backend.llm.provider import llm_provider

logger = logging.getLogger(__name__)


class DocumentAgent:
    """Specialized agent for retrieving and synthesizing evidence from internal corporate documents."""

    def __init__(self, llm=llm_provider):
        self.llm = llm

    def execute_task(
        self,
        task_description: str,
        user_query: str = "",
        override_strategy: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Runs the document retrieval workflow with learned strategy configuration."""
        start_time = time.time()
        combined_query = f"{task_description} {user_query}".strip()

        # 1. Retrieve optimal strategy from Strategy Memory
        if override_strategy:
            strategy = override_strategy
        else:
            strategy = strategy_memory.recommend_strategy(combined_query, agent_name="document_agent")

        retriever_type = strategy.get("retriever", "hybrid")
        top_k = strategy.get("top_k", 6)
        use_reranker = strategy.get("reranker", "cross_encoder") != "none"

        logger.info(f"DocumentAgent executing with strategy: {strategy}")

        # 2. Search internal document corpus
        passages = search_internal_documents(
            query=combined_query,
            strategy=retriever_type,
            top_k=top_k,
            use_reranker=use_reranker,
        )

        elapsed_ms = (time.time() - start_time) * 1000

        return {
            "agent": "document_agent",
            "task": task_description,
            "query": combined_query,
            "strategy": strategy,
            "passages": passages,
            "passage_count": len(passages),
            "latency_ms": round(elapsed_ms, 2),
        }


document_agent = DocumentAgent()
