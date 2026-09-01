"""
Ablation Experiments Runner.
Conducts controlled ablation studies:
1. No Reranker (Hybrid without Cross-Encoder)
2. No Critic / Self-Correction
3. No Strategy Memory (Static retrieval)
4. Dense-only vs BM25-only vs Hybrid
5. Top-k variations (k=3 vs k=8 vs k=15)
"""
from typing import Dict, Any, List
from backend.evaluation.dataset import get_benchmark_dataset
from backend.tools.retrieval_tools import search_internal_documents
from backend.evaluation.metrics import calculate_retrieval_metrics


def run_retrieval_ablations() -> Dict[str, Any]:
    """Runs ablation experiments on retrieval methods across the benchmark dataset."""
    dataset = get_benchmark_dataset()
    configurations = [
        {"name": "Dense Only (Qdrant)", "strategy": "dense", "reranker": False, "top_k": 6},
        {"name": "Sparse Only (BM25)", "strategy": "sparse", "reranker": False, "top_k": 6},
        {"name": "Hybrid (No Reranker)", "strategy": "hybrid", "reranker": False, "top_k": 6},
        {"name": "Hybrid + Cross-Encoder Reranker", "strategy": "hybrid", "reranker": True, "top_k": 6},
        {"name": "Hybrid + Reranker (Top-K=12)", "strategy": "hybrid", "reranker": True, "top_k": 12},
    ]

    results = []
    for config in configurations:
        recalls = []
        hit_rates = []
        mrrs = []

        for q in dataset:
            keywords = q["ground_truth_keywords"]
            items = search_internal_documents(
                query=q["question"],
                strategy=config["strategy"],
                top_k=config["top_k"],
                use_reranker=config["reranker"],
            )
            m = calculate_retrieval_metrics(items, keywords)
            recalls.append(m["recall"])
            hit_rates.append(m["hit_rate"])
            mrrs.append(m["mrr"])

        n = len(dataset)
        results.append({
            "configuration": config["name"],
            "avg_recall": round(sum(recalls) / n, 3),
            "avg_hit_rate": round(sum(hit_rates) / n, 3),
            "avg_mrr": round(sum(mrrs) / n, 3),
        })

    return {
        "benchmark_questions": len(dataset),
        "ablation_results": results,
    }
