from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Interaction:
    """User interaction data model for Socratic questioning and guidance"""

    id: Optional[int] = None
    session_id: int = 0
    interaction_type: str = (
        ""  # socratic_question, methodology_advice, paradigm_challenge
    )
    content: str = ""
    domain_context: Optional[str] = None
    novel_theory_context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "interaction_type": self.interaction_type,
            "content": self.content,
            "domain_context": self.domain_context,
            "novel_theory_context": self.novel_theory_context,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Interaction":
        """Create Interaction from dictionary"""
        return cls(
            id=data.get("id"),
            session_id=data.get("session_id", 0),
            interaction_type=data.get("interaction_type", ""),
            content=data.get("content", ""),
            domain_context=data.get("domain_context"),
            novel_theory_context=data.get("novel_theory_context"),
            metadata=data.get("metadata"),
            timestamp=(
                datetime.fromisoformat(data["timestamp"])
                if data.get("timestamp")
                else None
            ),
        )
