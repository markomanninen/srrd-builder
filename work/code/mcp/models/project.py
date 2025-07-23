from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Project:
    """Research project data model"""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    domain: str = ""
    methodology: str = ""
    novel_theory_mode: bool = False
    paradigm_focus: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "methodology": self.methodology,
            "novel_theory_mode": self.novel_theory_mode,
            "paradigm_focus": self.paradigm_focus,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create Project from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            domain=data.get("domain", ""),
            methodology=data.get("methodology", ""),
            novel_theory_mode=data.get("novel_theory_mode", False),
            paradigm_focus=data.get("paradigm_focus"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
        )
