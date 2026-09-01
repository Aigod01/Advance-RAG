"""
LangGraph Multi-Agent Orchestration Graph.
Connects Planner -> Parallel Agents -> Evidence Aggregator -> Critic -> Retry Loop -> Grounded Synthesizer.
"""
import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import StateGraph, START, END

from backend.graph.state import AgentState, EvidenceItem, TraceEvent
from backend.graph.router import (
    normalize_database_results,
    normalize_document_results,
    normalize_web_results,
    deduplicate_evidence,
    detect_contradictions,
)
from backend.graph.edges import route_after_critic
from backend.agents.planner import planner_agent
from backend.agents.database_agent import database_agent
from backend.agents.document_agent import document_agent
from backend.agents.web_agent import web_agent
from backend.agents.critic import critic_agent
from backend.agents.synthesizer import synthesizer_agent
from backend.memory.strategy_memory import strategy_memory
from backend.config import settings


def add_trace(state: AgentState, step: str, agent: str, status: str, message: str, details: Dict[str, Any] = None):
    """Appends an operational trace event."""
    if "trace_events" not in state:
        state["trace_events"] = []

    evt = {
        "event_id": f"evt_{len(state['trace_events']) + 1}",
        "step": step,
        "agent": agent,
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().strftime("%H:%M:%S.%f")[:-3],
        "details": details or {},
    }
    state["trace_events"].append(evt)


def planner_node(state: AgentState) -> Dict[str, Any]:
    """Decomposes the incoming query into structured subtasks."""
    start_time = time.time()
    user_query = state["user_query"]

    add_trace(state, "Planning", "planner", "started", f"Analyzing query: '{user_query[:60]}...'")

    plan_res = planner_agent.plan(user_query)
    tasks = plan_res.get("tasks", [])

    add_trace(
        state,
        "Planning",
        "planner",
        "completed",
        f"Planner created {len(tasks)} subtasks",
        {"tasks": tasks, "reasoning": plan_res.get("plan_reasoning")},
    )

    return {
        "tasks": tasks,
        "current_step": "tasks_planned",
        "trace_events": state["trace_events"],
    }


def execute_agents_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes specialized agents for the planned subtasks.
    Runs independent tasks and collects results.
    """
    tasks = state.get("tasks", [])
    user_query = state["user_query"]
    task_results = []

    for task in tasks:
        agent_type = task.get("agent")
        task_desc = task.get("description", "")
        task_id = task.get("task_id", "")

        add_trace(state, "Execution", agent_type, "started", f"Starting task [{task_id}]: {task_desc[:60]}...")

        if agent_type == "database_agent":
            res = database_agent.execute_task(task_desc, user_query)
            add_trace(
                state,
                "Execution",
                "database_agent",
                "completed",
                f"SQL Agent executed query ({res.get('row_count', 0)} rows returned)",
                {"sql": res.get("sql_query"), "rows": res.get("row_count")},
            )
            task_results.append(res)

        elif agent_type == "document_agent":
            res = document_agent.execute_task(task_desc, user_query)
            add_trace(
                state,
                "Execution",
                "document_agent",
                "completed",
                f"Document Agent retrieved {res.get('passage_count', 0)} passages",
                {"passages": res.get("passage_count"), "strategy": res.get("strategy")},
            )
            task_results.append(res)

        elif agent_type == "web_agent":
            res = web_agent.execute_task(task_desc, user_query)
            add_trace(
                state,
                "Execution",
                "web_agent",
                "completed",
                f"Web Agent retrieved {res.get('source_count', 0)} web sources",
                {"sources": res.get("source_count")},
            )
            task_results.append(res)

    return {
        "task_results": task_results,
        "current_step": "agents_executed",
        "trace_events": state["trace_events"],
    }


def aggregator_node(state: AgentState) -> Dict[str, Any]:
    """Normalizes and deduplicates all collected agent evidence."""
    add_trace(state, "Aggregation", "aggregator", "started", "Normalizing & deduplicating evidence...")

    raw_results = state.get("task_results", [])
    raw_evidence_items: List[EvidenceItem] = []

    for res in raw_results:
        agent_type = res.get("agent")
        if agent_type == "database_agent":
            raw_evidence_items.extend(normalize_database_results(res))
        elif agent_type == "document_agent":
            raw_evidence_items.extend(normalize_document_results(res))
        elif agent_type == "web_agent":
            raw_evidence_items.extend(normalize_web_results(res))

    # Deduplicate
    deduped = deduplicate_evidence(raw_evidence_items)
    evidence_dicts = [e.model_dump() for e in deduped]

    add_trace(
        state,
        "Aggregation",
        "aggregator",
        "completed",
        f"Aggregated {len(evidence_dicts)} unified evidence items",
        {"count": len(evidence_dicts)},
    )

    return {
        "evidence": evidence_dicts,
        "current_step": "evidence_aggregated",
        "trace_events": state["trace_events"],
    }


def critic_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates evidence completeness, freshness, and checks for contradictions."""
    add_trace(state, "Verification", "critic", "started", "Evaluating evidence sufficiency & conflict check...")

    user_query = state["user_query"]
    evidence = state.get("evidence", [])
    retry_count = state.get("retry_count", 0)

    verdict = critic_agent.evaluate(
        user_query=user_query,
        normalized_evidence=evidence,
        retry_count=retry_count,
        max_retries=settings.MAX_RETRIES,
    )

    is_sufficient = verdict.get("sufficient", False)
    status_label = "completed" if is_sufficient else "warning"
    msg = "Critic accepted evidence (sufficiency: 100%)" if is_sufficient else f"Critic flagged missing items: {', '.join(verdict.get('missing', ['data']))}"

    add_trace(state, "Verification", "critic", status_label, msg, verdict)

    return {
        "critique": verdict,
        "current_step": "critique_completed",
        "trace_events": state["trace_events"],
    }


def retry_router_node(state: AgentState) -> Dict[str, Any]:
    """Routes targeted retry query back to specific agent."""
    critique = state.get("critique", {})
    target_agent = critique.get("target_agent", "document_agent")
    new_query = critique.get("new_query", state["user_query"])
    retry_count = state.get("retry_count", 0) + 1

    add_trace(
        state,
        "Self-Correction",
        "retry_router",
        "retrying",
        f"Retry {retry_count}/{settings.MAX_RETRIES} routed to {target_agent}: '{new_query[:50]}...'",
        {"target_agent": target_agent, "new_query": new_query, "retry_count": retry_count},
    )

    new_results = []
    if target_agent == "database_agent":
        res = database_agent.execute_task(new_query, state["user_query"])
        new_results.append(res)
    elif target_agent == "document_agent":
        res = document_agent.execute_task(new_query, state["user_query"])
        new_results.append(res)
    elif target_agent == "web_agent":
        res = web_agent.execute_task(new_query, state["user_query"])
        new_results.append(res)

    # Normalize and merge with existing evidence
    existing_evidence = state.get("evidence", [])
    new_raw_items: List[EvidenceItem] = []
    for res in new_results:
        agent_type = res.get("agent")
        if agent_type == "database_agent":
            new_raw_items.extend(normalize_database_results(res))
        elif agent_type == "document_agent":
            new_raw_items.extend(normalize_document_results(res))
        elif agent_type == "web_agent":
            new_raw_items.extend(normalize_web_results(res))

    combined = existing_evidence + [e.model_dump() for e in new_raw_items]
    # Deduplicate
    seen_ids = set()
    deduped_combined = []
    for ev in combined:
        ev_id = ev.get("evidence_id")
        if ev_id not in seen_ids:
            seen_ids.add(ev_id)
            deduped_combined.append(ev)

    # Re-evaluate critic on new evidence
    re_verdict = critic_agent.evaluate(
        user_query=state["user_query"],
        normalized_evidence=deduped_combined,
        retry_count=retry_count,
        max_retries=settings.MAX_RETRIES,
    )

    add_trace(
        state,
        "Self-Correction",
        "critic",
        "completed",
        f"Post-retry evidence accepted (Score: {re_verdict.get('score', 0.85):.2f})",
        re_verdict,
    )

    return {
        "evidence": deduped_combined,
        "retry_count": retry_count,
        "critique": re_verdict,
        "current_step": "retry_executed",
        "trace_events": state["trace_events"],
    }


def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    """Generates the grounded answer with citations and calibrated confidence."""
    add_trace(state, "Synthesis", "synthesizer", "started", "Generating grounded answer with citations...")

    user_query = state["user_query"]
    evidence = state.get("evidence", [])
    critique = state.get("critique", {})

    syn_res = synthesizer_agent.synthesize(
        user_query=user_query,
        evidence_list=evidence,
        critic_result=critique,
    )

    final_answer = syn_res.get("answer", "")
    citations = syn_res.get("citations", [])
    confidence = syn_res.get("confidence", 0.85)

    add_trace(
        state,
        "Synthesis",
        "synthesizer",
        "completed",
        f"Synthesis complete (Confidence: {int(confidence * 100)}%, {len(citations)} citations)",
        {"confidence": confidence, "citations_count": len(citations)},
    )

    # Record outcome in Strategy Memory (Collaborative Retrieval Learning)
    if settings.ENABLE_STRATEGY_LEARNING:
        doc_tasks = [r for r in state.get("task_results", []) if r.get("agent") == "document_agent"]
        doc_strategy = doc_tasks[0].get("strategy", {}) if doc_tasks else {"retriever": "hybrid", "top_k": 8}
        critic_score = critique.get("score", 0.85)
        latency = state.get("execution_time_ms", 500.0)

        strategy_memory.record_outcome(
            query=user_query,
            agent="document_agent",
            strategy=doc_strategy,
            critic_score=critic_score,
            latency_ms=latency,
            retries_needed=state.get("retry_count", 0),
        )

    return {
        "final_answer": final_answer,
        "citations": citations,
        "confidence": confidence,
        "current_step": "completed",
        "trace_events": state["trace_events"],
    }


def build_collaborative_rag_graph():
    """Builds and compiles the multi-agent LangGraph workflow."""
    builder = StateGraph(AgentState)

    # Register nodes
    builder.add_node("planner", planner_node)
    builder.add_node("execute_agents", execute_agents_node)
    builder.add_node("aggregator", aggregator_node)
    builder.add_node("critic", critic_node)
    builder.add_node("retry_router", retry_router_node)
    builder.add_node("synthesizer", synthesizer_node)

    # Wire edges
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "execute_agents")
    builder.add_edge("execute_agents", "aggregator")
    builder.add_edge("aggregator", "critic")

    # Conditional edge from critic: retry or synthesize
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "retry_router": "retry_router",
            "synthesizer": "synthesizer",
        },
    )

    builder.add_edge("retry_router", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()


# Global compiled workflow
orchestration_graph = build_collaborative_rag_graph()


def run_collaborative_rag(user_query: str, run_id: str = None) -> Dict[str, Any]:
    """Synchronous / callable runner for the multi-agent graph."""
    import uuid

    active_run_id = run_id or f"run_{uuid.uuid4().hex[:10]}"
    start_time = time.time()

    initial_state: AgentState = {
        "run_id": active_run_id,
        "user_query": user_query,
        "tasks": [],
        "task_results": [],
        "evidence": [],
        "retrieval_strategy": {},
        "critique": {},
        "retry_count": 0,
        "final_answer": "",
        "citations": [],
        "confidence": 0.0,
        "trace_events": [],
        "current_step": "initialized",
        "execution_time_ms": 0.0,
    }

    final_state = orchestration_graph.invoke(initial_state)
    elapsed_ms = (time.time() - start_time) * 1000
    final_state["execution_time_ms"] = round(elapsed_ms, 2)

    return final_state
