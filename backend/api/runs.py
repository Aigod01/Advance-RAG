"""
Run status, operational trace, and source metadata inspection endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.api.chat import ACTIVE_RUNS
from backend.memory.source_memory import source_memory

router = APIRouter(prefix="/api", tags=["Runs & Tracing"])


@router.get("/runs/{run_id}")
async def get_run_status(run_id: str):
    """Retrieves full run state, answers, and evidence."""
    if run_id not in ACTIVE_RUNS:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return ACTIVE_RUNS[run_id]


@router.get("/runs/{run_id}/trace")
async def get_run_trace(run_id: str):
    """Retrieves operational execution timeline for the run."""
    if run_id not in ACTIVE_RUNS:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    run = ACTIVE_RUNS[run_id]
    return {
        "run_id": run_id,
        "query": run.get("user_query", ""),
        "execution_time_ms": run.get("execution_time_ms", 0.0),
        "trace_events": run.get("trace_events", []),
        "task_results": run.get("task_results", []),
        "critique": run.get("critique", {}),
    }


@router.get("/sources/{source_id}")
async def get_source_metadata(source_id: str):
    """Returns reliability and domain quality metadata for a source."""
    trust = source_memory.get_source_reliability(source_id)
    return {
        "source_id": source_id,
        "reliability_score": trust,
        "status": "VERIFIED" if trust >= 0.85 else "PROVISIONAL",
    }
