"""
Typed state definition and evidence data schemas for LangGraph multi-agent orchestration.
"""
from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    evidence_id: str
    source_type: str  # "database", "document", "web"
    source_id: str  # e.g., table name, filename#page, URL
    content: str
    relevance_score: float = 0.8
    source_quality: float = 0.9
    timestamp: str = ""
    citation: str = ""
    agent: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    event_id: str
    step: str
    agent: str
    status: str  # "started", "completed", "retrying", "warning", "error"
    message: str
    timestamp: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AgentState(TypedDict):
    run_id: str
    user_query: str
    tasks: List[Dict[str, Any]]
    task_results: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    retrieval_strategy: Dict[str, Any]
    critique: Dict[str, Any]
    retry_count: int
    final_answer: str
    citations: List[Dict[str, Any]]
    confidence: float
    trace_events: List[Dict[str, Any]]
    current_step: str
    execution_time_ms: float
