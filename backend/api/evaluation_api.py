"""
Research Evaluation and Benchmark API endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from backend.evaluation.evaluator import evaluator
from backend.evaluation.experiments import run_retrieval_ablations
from backend.evaluation.dataset import get_benchmark_dataset

router = APIRouter(prefix="/api/evaluation", tags=["Research & Evaluation Benchmark"])

LATEST_EVALUATION_RESULTS: Dict[str, Any] = {}


class EvalRequest(BaseModel):
    max_questions: int = 5


@router.post("/run")
async def run_benchmark(req: EvalRequest = EvalRequest()):
    """Runs the 4-paradigm benchmark evaluation (Baseline vs Agentic vs Multi-Agent vs Adaptive)."""
    global LATEST_EVALUATION_RESULTS
    results = evaluator.evaluate_all(max_questions=req.max_questions)
    LATEST_EVALUATION_RESULTS = results
    return results


@router.get("/results")
async def get_benchmark_results():
    """Retrieves latest evaluation benchmark results or runs initial evaluation."""
    global LATEST_EVALUATION_RESULTS
    if not LATEST_EVALUATION_RESULTS:
        LATEST_EVALUATION_RESULTS = evaluator.evaluate_all(max_questions=4)
    return LATEST_EVALUATION_RESULTS


@router.get("/ablations")
async def get_retrieval_ablations():
    """Runs and returns retrieval ablation studies (dense vs sparse vs hybrid vs reranker)."""
    return run_retrieval_ablations()


@router.get("/dataset")
async def get_dataset():
    """Returns benchmark questions dataset."""
    return get_benchmark_dataset()
