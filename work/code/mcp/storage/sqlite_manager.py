import aiosqlite
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        """Initialize the database connection and schema"""
        return await self.initialize_database()
    
    async def initialize_database(self):
        """Create database with schema"""
        self.connection = await aiosqlite.connect(self.db_path)
        
        # Try to find schema file in multiple locations
        schema_paths = [
            "config/database_schema.sql",
            "work/code/mcp/config/database_schema.sql",
            str(Path(__file__).parent.parent / "config" / "database_schema.sql")
        ]
        
        schema_content = None
        for schema_path in schema_paths:
            try:
                with open(schema_path, 'r') as f:
                    schema_content = f.read()
                    break
            except FileNotFoundError:
                continue
        
        if schema_content:
            await self.connection.executescript(schema_content)
            await self.connection.commit()
        else:
            # Fallback: create basic schema with tool_usage table
            basic_schema = """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                domain TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                session_type TEXT,
                user_id TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                tool_name TEXT NOT NULL,
                research_act TEXT NOT NULL,
                research_category TEXT NOT NULL,
                arguments TEXT,
                result_summary TEXT,
                execution_time_ms INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            );
            
            CREATE TABLE IF NOT EXISTS research_progress (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                research_act TEXT NOT NULL,
                research_category TEXT NOT NULL,
                status TEXT DEFAULT 'not_started',
                completion_percentage INTEGER DEFAULT 0,
                tools_used TEXT,
                notes TEXT,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY,
                session_id INTEGER,
                interaction_type TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            );
            
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                category TEXT,
                requirement_text TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            
            CREATE TABLE IF NOT EXISTS quality_checks (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                check_type TEXT,
                component TEXT,
                result TEXT,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            
            CREATE TABLE IF NOT EXISTS research_milestones (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                milestone_type TEXT NOT NULL,
                milestone_name TEXT NOT NULL,
                description TEXT,
                research_act TEXT,
                research_category TEXT,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                impact_score INTEGER DEFAULT 1,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            """
            await self.connection.executescript(basic_schema)
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
    
    # Enhanced methods for research lifecycle persistence
    
    async def log_tool_usage(self, session_id: int, tool_name: str, research_act: str, 
                            research_category: str, arguments: Dict = None, 
                            result_summary: str = None, execution_time_ms: int = None, 
                            success: bool = True, error_message: str = None) -> int:
        """Log tool usage with research act context"""
        cursor = await self.connection.execute(
            """INSERT INTO tool_usage 
               (session_id, tool_name, research_act, research_category, arguments, 
                result_summary, execution_time_ms, success, error_message) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, tool_name, research_act, research_category, 
             json.dumps(arguments) if arguments else None,
             result_summary, execution_time_ms, success, error_message)
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def update_research_progress(self, project_id: int, research_act: str, 
                                     research_category: str, status: str, 
                                     completion_percentage: int, tools_used: List[str] = None, 
                                     notes: str = None) -> int:
        """Update or create research progress entry"""
        # Check if progress entry exists
        async with self.connection.execute(
            "SELECT id FROM research_progress WHERE project_id = ? AND research_act = ? AND research_category = ?",
            (project_id, research_act, research_category)
        ) as cursor:
            existing = await cursor.fetchone()
        
        if existing:
            # Update existing entry
            await self.connection.execute(
                """UPDATE research_progress 
                   SET status = ?, completion_percentage = ?, tools_used = ?, notes = ?, 
                       last_activity = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (status, completion_percentage, json.dumps(tools_used) if tools_used else None, 
                 notes, existing[0])
            )
            await self.connection.commit()
            return existing[0]
        else:
            # Create new entry
            cursor = await self.connection.execute(
                """INSERT INTO research_progress 
                   (project_id, research_act, research_category, status, completion_percentage, 
                    tools_used, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (project_id, research_act, research_category, status, completion_percentage,
                 json.dumps(tools_used) if tools_used else None, notes)
            )
            await self.connection.commit()
            return cursor.lastrowid

    async def create_workflow_recommendation(self, project_id: int, session_id: int, 
                                           current_research_act: str, recommended_next_act: str = None,
                                           recommended_tools: List[str] = None, reasoning: str = None,
                                           priority: int = 1) -> int:
        """Create workflow recommendation"""
        cursor = await self.connection.execute(
            """INSERT INTO workflow_recommendations 
               (project_id, session_id, current_research_act, recommended_next_act, 
                recommended_tools, reasoning, priority) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, session_id, current_research_act, recommended_next_act,
             json.dumps(recommended_tools) if recommended_tools else None, reasoning, priority)
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def record_research_milestone(self, project_id: int, milestone_type: str, 
                                      milestone_name: str, description: str = None,
                                      research_act: str = None, research_category: str = None,
                                      completion_criteria: Dict = None, tools_involved: List[str] = None,
                                      impact_score: int = 1) -> int:
        """Record research milestone achievement"""
        cursor = await self.connection.execute(
            """INSERT INTO research_milestones 
               (project_id, milestone_type, milestone_name, description, research_act, 
                research_category, completion_criteria, tools_involved, impact_score) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, milestone_type, milestone_name, description, research_act, research_category,
             json.dumps(completion_criteria) if completion_criteria else None,
             json.dumps(tools_involved) if tools_involved else None, impact_score)
        )
        await self.connection.commit()
        return cursor.lastrowid

    async def get_research_progress_summary(self, project_id: int) -> Dict[str, Any]:
        """Get comprehensive research progress summary"""
        # Get all progress entries
        async with self.connection.execute(
            "SELECT * FROM research_progress WHERE project_id = ?", (project_id,)
        ) as cursor:
            progress_rows = await cursor.fetchall()
        
        # Get tool usage for the project
        async with self.connection.execute(
            """SELECT tu.* FROM tool_usage tu 
               JOIN sessions s ON tu.session_id = s.id 
               WHERE s.project_id = ? 
               ORDER BY tu.timestamp""", (project_id,)
        ) as cursor:
            tool_usage_rows = await cursor.fetchall()
        
        # Get milestones
        async with self.connection.execute(
            "SELECT * FROM research_milestones WHERE project_id = ? ORDER BY achieved_at DESC", 
            (project_id,)
        ) as cursor:
            milestone_rows = await cursor.fetchall()
        
        return {
            "progress_entries": progress_rows,
            "tool_usage": tool_usage_rows,
            "milestones": milestone_rows
        }

    async def get_tool_usage_history(self, session_id: int) -> List[Dict[str, Any]]:
        """Get tool usage history for a session"""
        async with self.connection.execute(
            "SELECT * FROM tool_usage WHERE session_id = ? ORDER BY timestamp", (session_id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        # Convert to list of dicts
        columns = [description[0] for description in cursor.description] if rows else []
        return [dict(zip(columns, row)) for row in rows]

    async def get_workflow_recommendations(self, project_id: int, status: str = 'pending') -> List[Dict[str, Any]]:
        """Get workflow recommendations for a project"""
        async with self.connection.execute(
            "SELECT * FROM workflow_recommendations WHERE project_id = ? AND status = ? ORDER BY priority, created_at DESC",
            (project_id, status)
        ) as cursor:
            rows = await cursor.fetchall()
        
        columns = [description[0] for description in cursor.description] if rows else []
        return [dict(zip(columns, row)) for row in rows]

    async def get_research_milestones(self, project_id: int, limit: int = None) -> List[Dict[str, Any]]:
        """Get research milestones for a project"""
        query = "SELECT * FROM research_milestones WHERE project_id = ? ORDER BY achieved_at DESC"
        params = [project_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        
        columns = [description[0] for description in cursor.description] if rows else []
        return [dict(zip(columns, row)) for row in rows]

    async def update_session_research_context(self, session_id: int, current_research_act: str = None,
                                            research_focus: str = None, session_goals: Dict = None,
                                            completion_status: str = None) -> bool:
        """Update session with research context"""
        updates = []
        params = []
        
        if current_research_act:
            updates.append("current_research_act = ?")
            params.append(current_research_act)
        
        if research_focus:
            updates.append("research_focus = ?")
            params.append(research_focus)
        
        if session_goals:
            updates.append("session_goals = ?")
            params.append(json.dumps(session_goals))
        
        if completion_status:
            updates.append("completion_status = ?")
            params.append(completion_status)
        
        if not updates:
            return False
        
        # Add session_id for WHERE clause
        params.append(session_id)
        
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        
        try:
            await self.connection.execute(query, params)
            await self.connection.commit()
            return True
        except Exception:
            return False

    async def get_tools_used_in_project(self, project_id: int) -> List[str]:
        """Get list of all tools used in a project"""
        async with self.connection.execute(
            """SELECT DISTINCT tu.tool_name FROM tool_usage tu 
               JOIN sessions s ON tu.session_id = s.id 
               WHERE s.project_id = ? AND tu.success = 1""", (project_id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        return [row[0] for row in rows]

    async def get_research_act_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics about research act usage"""
        async with self.connection.execute(
            """SELECT research_act, COUNT(*) as tool_count, 
                      COUNT(DISTINCT tool_name) as unique_tools,
                      AVG(execution_time_ms) as avg_execution_time
               FROM tool_usage tu 
               JOIN sessions s ON tu.session_id = s.id 
               WHERE s.project_id = ? AND tu.success = 1
               GROUP BY research_act""", (project_id,)
        ) as cursor:
            rows = await cursor.fetchall()
        
        columns = [description[0] for description in cursor.description] if rows else []
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
