"""
Supervisor / Planner Agent: Decomposes complex cross-domain queries into structured subtask graphs.
Validates output against Pydantic schema with dependency tracking and parallelization flags.
"""
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.llm.provider import llm_provider

logger = logging.getLogger(__name__)


class TaskDefinition(BaseModel):
    task_id: str
    description: str
    agent: str  # "database_agent", "document_agent", "web_agent"
    priority: int = 1
    depends_on: List[str] = Field(default_factory=list)
    expected_output: str


class PlanOutput(BaseModel):
    plan_reasoning: str
    tasks: List[TaskDefinition]


PLANNER_SYSTEM_PROMPT = """You are the Supervisor/Planner Agent for an advanced Multi-Agent Collaborative RAG system.
Your job is to decompose user queries into structured subtasks for three specialized agents:
1. 'database_agent': Handles structured SQL queries for exact numbers, financial aggregates, revenue, product sales, transactions, customers, dates.
2. 'document_agent': Handles internal corporate documents (PDFs, reports, memos, policies, root causes, operational audits, SLAs).
3. 'web_agent': Handles current external research, global market trends, competitor intelligence, industry statistics, news.

Rules:
- Split independent subtasks so they can run concurrently.
- Identify dependencies in 'depends_on' if one task requires the output of another.
- Attach specific expected_output descriptions.
- Bypass unnecessary agents when a query only targets one source.
- Output strictly valid JSON matching the schema.
"""


class PlannerAgent:
    """Decomposes queries into parallelizable and dependent subtasks."""

    def __init__(self, llm=llm_provider):
        self.llm = llm

    def plan(self, user_query: str) -> Dict[str, Any]:
        """Generates structured task breakdown for query."""
        prompt = f"""Decompose the following user query into structured subtasks:
Query: "{user_query}"

Provide JSON with:
- "plan_reasoning": string explanation of decomposition
- "tasks": list of task objects:
  - "task_id": "t1", "t2", ...
  - "description": specific actionable instruction for the agent
  - "agent": "database_agent" | "document_agent" | "web_agent"
  - "priority": integer (1 = high)
  - "depends_on": list of prerequisite task_ids
  - "expected_output": expected evidence type and content
"""
        try:
            result = self.llm.generate_json(prompt, system_prompt=PLANNER_SYSTEM_PROMPT)
            if "tasks" in result and isinstance(result["tasks"], list) and len(result["tasks"]) > 0:
                validated_tasks = []
                for t in result["tasks"]:
                    validated_tasks.append(TaskDefinition(**t).model_dump())
                return {
                    "plan_reasoning": result.get("plan_reasoning", "Plan generated successfully."),
                    "tasks": validated_tasks,
                }
        except Exception as e:
            logger.warning(f"Planner LLM generation error: {e}. Using deterministic decomposition.")

        # Robust deterministic fallback decomposition
        tasks = []
        q_lower = user_query.lower()
        if any(w in q_lower for w in ["sales", "revenue", "fell", "cost", "how much", "q2", "q3", "sql", "highest", "database"]):
            tasks.append({
                "task_id": "t1",
                "description": f"Query database for numerical figures regarding: {user_query}",
                "agent": "database_agent",
                "priority": 1,
                "depends_on": [],
                "expected_output": "Aggregated sales and revenue figures",
            })
        if any(w in q_lower for w in ["reason", "report", "why", "internal", "document", "audit", "policy", "memo"]):
            tasks.append({
                "task_id": "t2",
                "description": f"Search internal corporate reports for context and causes: {user_query}",
                "agent": "document_agent",
                "priority": 1,
                "depends_on": [],
                "expected_output": "Internal report explanations and findings",
            })
        if any(w in q_lower for w in ["industry", "market", "trend", "external", "competitor", "global", "sector", "company-specific"]):
            tasks.append({
                "task_id": "t3",
                "description": f"Research external industry and market trends: {user_query}",
                "agent": "web_agent",
                "priority": 1,
                "depends_on": [],
                "expected_output": "External market growth or contraction benchmarks",
            })

        if not tasks:
            tasks.append({
                "task_id": "t1",
                "description": user_query,
                "agent": "document_agent",
                "priority": 1,
                "depends_on": [],
                "expected_output": "Relevant factual answers",
            })

        return {
            "plan_reasoning": "Determined target data sources based on query semantics.",
            "tasks": tasks,
        }


planner_agent = PlannerAgent()
