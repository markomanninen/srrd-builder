import aiosqlite
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize_database(self):
        """Create database with schema"""
        self.connection = await aiosqlite.connect(self.db_path)
        with open("work/code/mcp/config/database_schema.sql") as f:
            await self.connection.executescript(f.read())
        await self.connection.commit()

    async def create_project(self, name: str, description: str, domain: str) -> int:
        """Create new project record"""
        cursor = await self.connection.execute(
            "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
            (name, description, domain),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def create_session(self, project_id: int, session_type: str, user_id: str) -> int:
        """Create new research session"""
        cursor = await self.connection.execute(
            "INSERT INTO sessions (project_id, session_type, user_id) VALUES (?, ?, ?)",
            (project_id, session_type, user_id),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def log_interaction(self, session_id: int, interaction_type: str, content: str, metadata: Dict = None) -> int:
        """Log Socratic questioning interaction"""
        cursor = await self.connection.execute(
            "INSERT INTO interactions (session_id, interaction_type, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, interaction_type, content, json.dumps(metadata)),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def save_requirement(self, project_id: int, category: str, requirement_text: str, priority: int = 1) -> int:
        """Save research requirement"""
        cursor = await self.connection.execute(
            "INSERT INTO requirements (project_id, category, requirement_text, priority) VALUES (?, ?, ?, ?)",
            (project_id, category, requirement_text, priority),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def record_quality_check(self, project_id: int, check_type: str, component: str, result: str, comments: str = None) -> int:
        """Record quality assurance check"""
        cursor = await self.connection.execute(
            "INSERT INTO quality_checks (project_id, check_type, component, result, comments) VALUES (?, ?, ?, ?, ?)",
            (project_id, check_type, component, result, comments),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def get_project_data(self, project_id: int) -> Dict[str, Any]:
        """Get complete project data"""
        async with self.connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)) as cursor:
            project = await cursor.fetchone()
        async with self.connection.execute("SELECT * FROM sessions WHERE project_id = ?", (project_id,)) as cursor:
            sessions = await cursor.fetchall()
        async with self.connection.execute(
            "SELECT * FROM interactions WHERE session_id IN (SELECT id FROM sessions WHERE project_id = ?)",
            (project_id,),
        ) as cursor:
            interactions = await cursor.fetchall()
        return {"project": project, "sessions": sessions, "interactions": interactions}
