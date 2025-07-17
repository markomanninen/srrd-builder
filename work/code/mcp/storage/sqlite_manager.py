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
            # Fallback: create basic schema
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
