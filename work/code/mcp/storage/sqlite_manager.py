import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite


class SQLiteManager:
    @staticmethod
    def get_sessions_db_path(project_path: str) -> str:
        """Return the canonical sessions.db path for a project"""
        return str(Path(project_path) / ".srrd" / "data" / "sessions.db")

    @staticmethod
    def get_db_path(project_path: str) -> str:
        """Centralized getter for sessions.db path under .srrd/data"""
        return str(Path(project_path) / ".srrd" / "data" / "sessions.db")

    def __init__(self, db_path: str = None, project_path: str = None):
        if db_path:
            self.db_path = db_path
        elif project_path:
            self.db_path = self.get_db_path(project_path)
        else:
            self.db_path = None
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """Initialize the database connection and schema"""
        return await self.initialize_database()

    async def initialize_database(self):
        """Create database with schema, using a robust path to the schema file."""
        if not self.db_path:
            raise ValueError("Database path is not set for SQLiteManager.")

        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.db_path)

        try:
            base_dir = Path(__file__).resolve().parent.parent
            schema_file_path = base_dir / "config" / "database_schema.sql"

            if not schema_file_path.is_file():
                raise FileNotFoundError(
                    f"Database schema not found at the expected location: {schema_file_path}"
                )

            with open(schema_file_path, "r", encoding="utf-8") as f:
                schema_content = f.read()

            await self.connection.executescript(schema_content)
            await self.connection.commit()
        except Exception as e:
            await self.close()
            raise RuntimeError(
                f"FATAL: Could not initialize database from schema file. Error: {e}"
            )

    async def create_project(self, name: str, description: str, domain: str) -> int:
        """Create new project record"""
        cursor = await self.connection.execute(
            "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
            (name, description, domain),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def create_session(
        self, project_id: int, session_type: str, user_id: str
    ) -> int:
        """Create new research session"""
        cursor = await self.connection.execute(
            "INSERT INTO sessions (project_id, session_type, user_id) VALUES (?, ?, ?)",
            (project_id, session_type, user_id),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def log_interaction(
        self,
        session_id: int,
        interaction_type: str,
        content: str,
        metadata: Dict = None,
    ) -> int:
        """Log Socratic questioning interaction"""
        cursor = await self.connection.execute(
            "INSERT INTO interactions (session_id, interaction_type, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, interaction_type, content, json.dumps(metadata)),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def save_requirement(
        self, project_id: int, category: str, requirement_text: str, priority: int = 1
    ) -> int:
        """Save research requirement"""
        cursor = await self.connection.execute(
            "INSERT INTO requirements (project_id, category, requirement_text, priority) VALUES (?, ?, ?, ?)",
            (project_id, category, requirement_text, priority),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def record_quality_check(
        self,
        project_id: int,
        check_type: str,
        component: str,
        result: str,
        comments: str = None,
    ) -> int:
        """Record quality assurance check"""
        cursor = await self.connection.execute(
            "INSERT INTO quality_checks (project_id, check_type, component, result, comments) VALUES (?, ?, ?, ?, ?)",
            (project_id, check_type, component, result, comments),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def get_project_data(self, project_id: int) -> Dict[str, Any]:
        """Get complete project data"""
        async with self.connection.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ) as cursor:
            project = await cursor.fetchone()
        async with self.connection.execute(
            "SELECT * FROM sessions WHERE project_id = ?", (project_id,)
        ) as cursor:
            sessions = await cursor.fetchall()
        async with self.connection.execute(
            "SELECT * FROM interactions WHERE session_id IN (SELECT id FROM sessions WHERE project_id = ?)",
            (project_id,),
        ) as cursor:
            interactions = await cursor.fetchall()
        return {"project": project, "sessions": sessions, "interactions": interactions}

    async def log_tool_usage(
        self,
        session_id: int,
        tool_name: str,
        research_act: str,
        research_category: str,
        arguments: Dict = None,
        result_summary: str = None,
        execution_time_ms: int = None,
        success: bool = True,
        error_message: str = None,
    ) -> int:
        """Log tool usage with research act context"""
        cursor = await self.connection.execute(
            """INSERT INTO tool_usage 
               (session_id, tool_name, research_act, research_category, arguments, 
                result_summary, execution_time_ms, success, error_message) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                tool_name,
                research_act,
                research_category,
                json.dumps(arguments) if arguments else None,
                result_summary,
                execution_time_ms,
                success,
                error_message,
            ),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def update_research_progress(
        self,
        project_id: int,
        research_act: str,
        research_category: str,
        status: str,
        completion_percentage: int,
        tools_used: List[str] = None,
        notes: str = None,
    ) -> int:
        """Update or create research progress entry"""
        async with self.connection.execute(
            "SELECT id FROM research_progress WHERE project_id = ? AND research_act = ? AND research_category = ?",
            (project_id, research_act, research_category),
        ) as cursor:
            existing = await cursor.fetchone()

        if existing:
            await self.connection.execute(
                """UPDATE research_progress 
                   SET status = ?, completion_percentage = ?, tools_used = ?, notes = ?, 
                       last_activity = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (
                    status,
                    completion_percentage,
                    json.dumps(tools_used) if tools_used else None,
                    notes,
                    existing[0],
                ),
            )
            await self.connection.commit()
            return existing[0]
        else:
            cursor = await self.connection.execute(
                """INSERT INTO research_progress 
                   (project_id, research_act, research_category, status, completion_percentage, 
                    tools_used, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    project_id,
                    research_act,
                    research_category,
                    status,
                    completion_percentage,
                    json.dumps(tools_used) if tools_used else None,
                    notes,
                ),
            )
            await self.connection.commit()
            return cursor.lastrowid

    async def create_workflow_recommendation(
        self,
        project_id: int,
        session_id: int,
        current_research_act: str,
        recommended_next_act: str = None,
        recommended_tools: List[str] = None,
        reasoning: str = None,
        priority: int = 1,
    ) -> int:
        """Create workflow recommendation"""
        cursor = await self.connection.execute(
            """INSERT INTO workflow_recommendations 
               (project_id, session_id, current_research_act, recommended_next_act, 
                recommended_tools, reasoning, priority) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                session_id,
                current_research_act,
                recommended_next_act,
                json.dumps(recommended_tools) if recommended_tools else None,
                reasoning,
                priority,
            ),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def record_research_milestone(
        self,
        project_id: int,
        milestone_type: str,
        milestone_name: str,
        description: str = None,
        research_act: str = None,
        research_category: str = None,
        completion_criteria: Dict = None,
        tools_involved: List[str] = None,
        impact_score: int = 1,
    ) -> int:
        """Record research milestone achievement"""
        cursor = await self.connection.execute(
            """INSERT INTO research_milestones 
               (project_id, milestone_type, milestone_name, description, research_act, 
                research_category, completion_criteria, tools_involved, impact_score) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                milestone_type,
                milestone_name,
                description,
                research_act,
                research_category,
                json.dumps(completion_criteria) if completion_criteria else None,
                json.dumps(tools_involved) if tools_involved else None,
                impact_score,
            ),
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def get_research_progress_summary(self, project_id: int) -> Dict[str, Any]:
        """Get comprehensive research progress summary"""
        async with self.connection.execute(
            "SELECT * FROM research_progress WHERE project_id = ?", (project_id,)
        ) as cursor:
            progress_rows = await cursor.fetchall()
        async with self.connection.execute(
            """SELECT tu.* FROM tool_usage tu JOIN sessions s ON tu.session_id = s.id WHERE s.project_id = ? ORDER BY tu.timestamp""",
            (project_id,),
        ) as cursor:
            tool_usage_rows = await cursor.fetchall()
        async with self.connection.execute(
            "SELECT * FROM research_milestones WHERE project_id = ? ORDER BY achieved_at DESC",
            (project_id,),
        ) as cursor:
            milestone_rows = await cursor.fetchall()
        return {
            "progress_entries": progress_rows,
            "tool_usage": tool_usage_rows,
            "milestones": milestone_rows,
        }

    async def get_tool_usage_history(self, session_id: int) -> List[Dict[str, Any]]:
        """Get tool usage history for a session. Returns empty list if session does not exist."""
        async with self.connection.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ) as cursor:
            if not await cursor.fetchone():
                return []
        async with self.connection.execute(
            "SELECT * FROM tool_usage WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            columns = (
                [description[0] for description in cursor.description] if rows else []
            )
            return [dict(zip(columns, row)) for row in rows]

    async def get_workflow_recommendations(
        self, project_id: int, status: str = "pending"
    ) -> List[Dict[str, Any]]:
        """Get workflow recommendations for a project"""
        query = "SELECT * FROM workflow_recommendations WHERE project_id = ? AND status = ? ORDER BY priority, created_at DESC"
        async with self.connection.execute(query, (project_id, status)) as cursor:
            rows = await cursor.fetchall()
            columns = (
                [description[0] for description in cursor.description] if rows else []
            )
            return [dict(zip(columns, row)) for row in rows]

    async def get_research_milestones(
        self, project_id: int, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get research milestones for a project"""
        query = "SELECT * FROM research_milestones WHERE project_id = ? ORDER BY achieved_at DESC"
        params = [project_id]
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = (
                [description[0] for description in cursor.description] if rows else []
            )
            return [dict(zip(columns, row)) for row in rows]

    async def update_session_research_context(
        self,
        session_id: int,
        current_research_act: str = None,
        research_focus: str = None,
        session_goals: Dict = None,
        completion_status: str = None,
    ) -> bool:
        """Update session with research context"""
        updates, params = [], []
        if current_research_act:
            updates.append("current_research_act = ?")
            params.append(current_research_act)
        if research_focus:
            updates.append("research_focus = ?")
            params.append(research_focus)
        if session_goals:
            updates.append("session_goals = ?")
            params.append(json.dumps(session_goals))
        if not updates:
            return False
        params.append(session_id)
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        await self.connection.execute(query, params)
        await self.connection.commit()
        return True

    async def get_tools_used_in_project(self, project_id: int) -> List[str]:
        """Get list of all tools used in a project"""
        query = "SELECT DISTINCT tu.tool_name FROM tool_usage tu JOIN sessions s ON tu.session_id = s.id WHERE s.project_id = ? AND tu.success = 1"
        async with self.connection.execute(query, (project_id,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_research_act_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics about research act usage"""
        query = """SELECT research_act, COUNT(*) as tool_count, 
                      COUNT(DISTINCT tool_name) as unique_tools,
                      AVG(execution_time_ms) as avg_execution_time
               FROM tool_usage tu JOIN sessions s ON tu.session_id = s.id 
               WHERE s.project_id = ? AND tu.success = 1
               GROUP BY research_act"""
        async with self.connection.execute(query, (project_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = (
                [description[0] for description in cursor.description] if rows else []
            )
            return [dict(zip(columns, row)) for row in rows]

    async def close(self):
        """Close the database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def __aenter__(self):
        """Async context manager entry"""
        if not self.connection:
            await self.initialize_database()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
