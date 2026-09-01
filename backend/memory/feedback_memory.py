"""
Feedback Memory and Evaluation Tracking.
Stores explicit user ratings, qualitative comments, and audit trails.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.config import settings

logger = logging.getLogger(__name__)


class FeedbackMemory:
    """Stores user evaluations (+1 / -1), correction notes, and metadata."""

    def __init__(self, storage_path: str = None):
        self.storage_file = storage_path or os.path.join(
            settings.STORAGE_PATH, "feedback_memory.json"
        )
        self.feedback_entries: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    self.feedback_entries = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load feedback memory: {e}")

    def _save(self):
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self.feedback_entries, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback memory: {e}")

    def record_feedback(
        self,
        run_id: str,
        rating: int,  # +1 or -1
        comments: Optional[str] = None,
        query: Optional[str] = None,
        final_answer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records user feedback and persists to storage."""
        entry = {
            "feedback_id": f"fb_{int(datetime.utcnow().timestamp() * 1000)}",
            "run_id": run_id,
            "rating": rating,
            "comments": comments or "",
            "query": query or "",
            "final_answer": final_answer or "",
            "created_at": datetime.utcnow().isoformat(),
        }
        self.feedback_entries.append(entry)
        self._save()
        return entry

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Calculates positive / negative ratio and review counts."""
        if not self.feedback_entries:
            return {"total": 0, "positive": 0, "negative": 0, "positive_ratio": 0.0}

        total = len(self.feedback_entries)
        positive = sum(1 for f in self.feedback_entries if f.get("rating", 0) > 0)
        negative = sum(1 for f in self.feedback_entries if f.get("rating", 0) < 0)

        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "positive_ratio": round(positive / total, 3) if total > 0 else 0.0,
            "recent": self.feedback_entries[-10:],
        }


feedback_memory = FeedbackMemory()
