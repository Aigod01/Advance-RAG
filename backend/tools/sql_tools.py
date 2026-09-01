"""
Safe SQL execution and validation tools.
Enforces SELECT-only allow-lists, query execution limits, statement timeouts,
and provides schema inspection for SQL Agent.
"""
import logging
from typing import Dict, Any, List, Tuple
from backend.database.postgres import db_manager

logger = logging.getLogger(__name__)


def execute_safe_sql(query: str, max_rows: int = 50) -> Dict[str, Any]:
    """
    Executes a read-only SQL query safely.
    Returns structured results and execution metadata.
    """
    rows, status = db_manager.execute_read_query(query, max_rows=max_rows)
    if status != "SUCCESS":
        return {
            "success": False,
            "error": status,
            "query": query,
            "row_count": 0,
            "data": [],
        }

    return {
        "success": True,
        "query": query,
        "row_count": len(rows),
        "data": rows,
        "columns": list(rows[0].keys()) if rows else [],
    }


def get_db_schema() -> str:
    """Returns database schema definition."""
    return db_manager.get_schema_info()
