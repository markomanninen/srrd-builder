from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Session:
    """Research session data model"""
    id: Optional[int] = None
    project_id: int = 0
    session_type: str = ""  # planning, execution, analysis, publication, novel_theory
    paradigm_innovation_session: bool = False
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    user_id: str = ""
    status: str = "active"  # active, completed, paused
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "session_type": self.session_type,
            "paradigm_innovation_session": self.paradigm_innovation_session,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "user_id": self.user_id,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary"""
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id", 0),
            session_type=data.get("session_type", ""),
            paradigm_innovation_session=data.get("paradigm_innovation_session", False),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            user_id=data.get("user_id", ""),
            status=data.get("status", "active")
        )
