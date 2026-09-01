"""Evaluation package initialization."""
from backend.evaluation.dataset import get_benchmark_dataset, BENCHMARK_DATASET
from backend.evaluation.metrics import (
    calculate_retrieval_metrics,
    calculate_groundedness_and_faithfulness,
    calculate_citation_coverage,
)
from backend.evaluation.evaluator import evaluator, BenchmarkEvaluator
from backend.evaluation.experiments import run_retrieval_ablations

__all__ = [
    "get_benchmark_dataset",
    "BENCHMARK_DATASET",
    "calculate_retrieval_metrics",
    "calculate_groundedness_and_faithfulness",
    "calculate_citation_coverage",
    "evaluator",
    "BenchmarkEvaluator",
    "run_retrieval_ablations",
]
