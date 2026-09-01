"""
Chat API endpoints: synchronous run and streaming SSE execution.
"""
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from backend.graph.graph import run_collaborative_rag, orchestration_graph
from backend.graph.state import AgentState

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Chat & Multi-Agent Execution"])

# In-memory run store
ACTIVE_RUNS: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    query: str
    run_id: Optional[str] = None


class ChatResponse(BaseModel):
    run_id: str
    query: str
    answer: str
    confidence: float
    citations: list
    evidence: list
    trace_events: list
    execution_time_ms: float


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Executes full multi-agent collaborative RAG workflow for the query."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Run the (blocking) multi-agent graph in a worker thread so this
        # request doesn't stall the event loop / other concurrent requests.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_collaborative_rag, req.query, req.run_id)
    except Exception as e:
        logger.error(f"Chat execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat execution failed: {e}")

    ACTIVE_RUNS[result["run_id"]] = result

    return ChatResponse(
        run_id=result["run_id"],
        query=result["user_query"],
        answer=result.get("final_answer", ""),
        confidence=result.get("confidence", 0.0),
        citations=result.get("citations", []),
        evidence=result.get("evidence", []),
        trace_events=result.get("trace_events", []),
        execution_time_ms=result.get("execution_time_ms", 0.0),
    )


@router.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """Streams operational trace events and final synthesis via Server-Sent Events (SSE)."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    async def event_generator():
        # Yield start event
        run_id = req.run_id or f"run_{asyncio.get_event_loop().time()}"
        yield f"data: {json.dumps({'type': 'run_started', 'run_id': run_id, 'query': req.query})}\n\n"

        try:
            # Execute graph in worker
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_collaborative_rag, req.query, run_id)
        except Exception as e:
            logger.error(f"Chat stream execution failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'run_id': run_id, 'message': str(e)})}\n\n"
            return

        ACTIVE_RUNS[result["run_id"]] = result

        # Stream trace events sequentially
        for evt in result.get("trace_events", []):
            yield f"data: {json.dumps({'type': 'trace_event', 'event': evt})}\n\n"
            await asyncio.sleep(0.05)

        # Stream final result
        final_payload = {
            "type": "completed",
            "run_id": result["run_id"],
            "answer": result.get("final_answer", ""),
            "confidence": result.get("confidence", 0.0),
            "citations": result.get("citations", []),
            "evidence": result.get("evidence", []),
            "execution_time_ms": result.get("execution_time_ms", 0.0),
        }
        yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
