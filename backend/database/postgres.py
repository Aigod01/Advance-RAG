"""
Database connection, session management, and schema inspection engine.
Supports PostgreSQL and SQLite (in-memory/file) transparently.
"""
import re
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from backend.config import settings
from backend.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connection, safe query execution, and schema reflection."""

    def __init__(self, db_url: str = settings.DATABASE_URL):
        self.db_url = db_url
        connect_args = {}
        if self.db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            self.db_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            echo=False,
        )
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        self._cached_schema: str = ""

    def init_db(self):
        """Create tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        self._cached_schema = self.get_schema_info()

    def get_session(self):
        """Provide transactional session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def get_schema_info(self, refresh: bool = False) -> str:
        """Returns structured DDL / Schema text for LLM SQL Agent."""
        if self._cached_schema and not refresh:
            return self._cached_schema

        inspector = inspect(self.engine)
        schema_lines = []
        table_names = inspector.get_table_names()

        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            col_strs = []
            for col in columns:
                col_type = str(col["type"])
                nullable = "" if col.get("nullable", True) else " NOT NULL"
                pk = " PRIMARY KEY" if col.get("primary_key", False) else ""
                col_strs.append(f"  {col['name']} {col_type}{nullable}{pk}")

            # Foreign keys
            fks = inspector.get_foreign_keys(table_name)
            fk_strs = []
            for fk in fks:
                for c, r_c in zip(fk["constrained_columns"], fk["referred_columns"]):
                    fk_strs.append(f"  FOREIGN KEY ({c}) REFERENCES {fk['referred_table']}({r_c})")

            body = ",\n".join(col_strs + fk_strs)
            schema_lines.append(f"CREATE TABLE {table_name} (\n{body}\n);")

        self._cached_schema = "\n\n".join(schema_lines)
        return self._cached_schema

    def execute_read_query(
        self, query: str, max_rows: int = settings.DB_MAX_ROWS
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Executes a SELECT query safely with timeout and row limits.
        Returns: (results_as_list_of_dicts, status_or_error_msg)
        """
        # Clean query
        query = query.strip()
        if query.endswith(";"):
            query = query[:-1]

        # Enforce safety check
        is_safe, reason = self.is_safe_query(query)
        if not is_safe:
            return [], f"Safety Violation: {reason}"

        # If query has no LIMIT clause and is a SELECT, add LIMIT
        if "limit" not in query.lower():
            query = f"{query} LIMIT {max_rows}"

        with self.engine.connect() as conn:
            try:
                # Set execution timeout if PostgreSQL
                if not self.db_url.startswith("sqlite"):
                    conn.execute(
                        text(f"SET statement_timeout = {settings.DB_TIMEOUT_SECONDS * 1000}")
                    )

                result = conn.execute(text(query))
                keys = list(result.keys())
                rows = result.fetchmany(max_rows)
                dict_rows = [dict(zip(keys, row)) for row in rows]
                return dict_rows, "SUCCESS"
            except SQLAlchemyError as e:
                err_msg = str(e.orig) if hasattr(e, "orig") else str(e)
                logger.warning(f"SQL execution error: {err_msg}")
                return [], f"Database Error: {err_msg}"
            except Exception as e:
                logger.error(f"Unexpected DB execution error: {e}")
                return [], f"Execution Error: {str(e)}"

    @staticmethod
    def is_safe_query(query: str) -> Tuple[bool, str]:
        """Validates that query is strictly a read-only SELECT statement."""
        normalized = query.strip().upper()
        # Remove comments
        normalized = re.sub(r"--.*?$", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL).strip()

        if not normalized.startswith("SELECT") and not normalized.startswith("WITH"):
            return False, "Only SELECT or WITH queries are permitted."

        forbidden_keywords = [
            r"\bDELETE\b",
            r"\bUPDATE\b",
            r"\bINSERT\b",
            r"\bDROP\b",
            r"\bALTER\b",
            r"\bTRUNCATE\b",
            r"\bCREATE\b",
            r"\bREPLACE\b",
            r"\bGRANT\b",
            r"\bREVOKE\b",
            r"\bEXEC\b",
            r"\bEXECUTE\b",
            r"\bATTACH\b",
            r"\bDETACH\b",
            r"\bPRAGMA\b",
            r"\bVACUUM\b",
        ]
        for pattern in forbidden_keywords:
            if re.search(pattern, normalized, re.IGNORECASE):
                return False, f"Forbidden keyword detected matching pattern: {pattern}"

        return True, "Valid SELECT query"


db_manager = DatabaseManager()
