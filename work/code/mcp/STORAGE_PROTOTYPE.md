# MCP Server Storage Implementation Prototype

## File Structure
```
work/code/mcp/
├── server.py                 # Main MCP server implementation
├── storage/                  # Storage management modules
│   ├── __init__.py
│   ├── git_manager.py       # Git repository management
│   ├── sqlite_manager.py    # SQLite database operations
│   ├── vector_manager.py    # Vector database operations
│   └── project_manager.py   # Project initialization and management
├── tools/                    # MCP tool implementations
│   ├── __init__.py
│   ├── research_planning.py
│   ├── methodology_advisory.py
│   ├── quality_assurance.py
│   ├── document_generation.py
│   └── storage_management.py
├── models/                   # Data models and schemas
│   ├── __init__.py
│   ├── project.py
│   ├── session.py
│   └── interaction.py
└── config/                   # Configuration files
    ├── database_schema.sql
    ├── default_config.json
    └── vector_collections.yaml
```

## Key Implementation Files

### 1. Git Manager (git_manager.py)
```python
import git
from pathlib import Path
from typing import Optional, List

class GitManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.repo: Optional[git.Repo] = None
    
    def initialize_repository(self) -> bool:
        """Initialize Git repository in project directory"""
        
    def commit_changes(self, message: str, files: List[str] = None) -> str:
        """Commit changes with message, return commit hash"""
        
    def create_branch(self, branch_name: str) -> bool:
        """Create new branch for research phase"""
        
    def get_commit_history(self, max_count: int = 50) -> List[dict]:
        """Get commit history with metadata"""
        
    def backup_to_remote(self, remote_url: str) -> bool:
        """Backup repository to remote Git server"""
```

### 2. SQLite Manager (sqlite_manager.py)
```python
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def initialize_database(self) -> bool:
        """Create database with schema"""
        
    def create_project(self, name: str, description: str, domain: str) -> int:
        """Create new project record"""
        
    def create_session(self, project_id: int, session_type: str, user_id: str) -> int:
        """Create new research session"""
        
    def log_interaction(self, session_id: int, interaction_type: str, content: str, metadata: Dict = None) -> int:
        """Log Socratic questioning interaction"""
        
    def save_requirement(self, project_id: int, category: str, requirement_text: str, priority: int = 1) -> int:
        """Save research requirement"""
        
    def record_quality_check(self, project_id: int, check_type: str, component: str, result: str, comments: str = None) -> int:
        """Record quality assurance check"""
        
    def get_project_data(self, project_id: int) -> Dict[str, Any]:
        """Get complete project data"""
```

### 3. Vector Manager (vector_manager.py)
```python
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

class VectorManager:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(path=db_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def initialize_collections(self) -> bool:
        """Initialize vector database collections"""
        
    def add_research_literature(self, title: str, content: str, metadata: Dict) -> str:
        """Add research literature with embeddings"""
        
    def add_methodology(self, name: str, description: str, metadata: Dict) -> str:
        """Add research methodology with embeddings"""
        
    def add_interaction(self, session_id: int, content: str, interaction_type: str) -> str:
        """Add interaction with embeddings for context retrieval"""
        
    def search_knowledge(self, query: str, collection: str, n_results: int = 5) -> List[Dict]:
        """Semantic search in knowledge base"""
        
    def find_similar_interactions(self, query: str, session_id: int = None, n_results: int = 3) -> List[Dict]:
        """Find similar previous interactions"""
        
    def get_relevant_methodologies(self, research_description: str, domain: str = None) -> List[Dict]:
        """Get relevant research methodologies"""
```

### 4. Project Manager (project_manager.py)
```python
from pathlib import Path
from typing import Dict, Any, Optional
from .git_manager import GitManager
from .sqlite_manager import SQLiteManager
from .vector_manager import VectorManager

class ProjectManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git_manager = GitManager(project_path)
        self.sqlite_manager = SQLiteManager(str(self.project_path / '.srrd' / 'sessions.db'))
        self.vector_manager = VectorManager(str(self.project_path / '.srrd' / 'knowledge.db'))
        
    def initialize_project(self, name: str, description: str, domain: str) -> Dict[str, Any]:
        """Initialize complete project structure"""
        
    def create_directory_structure(self) -> bool:
        """Create standard research project directories"""
        
    def setup_configuration(self, config: Dict[str, Any]) -> bool:
        """Setup project-specific configuration"""
        
    def backup_project(self, backup_location: Optional[str] = None) -> bool:
        """Create complete project backup"""
        
    def restore_project(self, backup_location: str) -> bool:
        """Restore project from backup"""
        
    def get_project_status(self) -> Dict[str, Any]:
        """Get comprehensive project status"""
```

### 5. Storage Management Tools (storage_management.py)
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
from .storage.project_manager import ProjectManager

# MCP Tools for storage management
async def initialize_project_tool(name: str, description: str, domain: str, project_path: str) -> str:
    """MCP tool to initialize Git-based project storage"""
    
async def save_session_tool(session_data: dict, project_path: str) -> str:
    """MCP tool to save research session data"""
    
async def search_knowledge_tool(query: str, collection: str, project_path: str) -> str:
    """MCP tool for vector database search"""
    
async def version_control_tool(action: str, message: str, files: list, project_path: str) -> str:
    """MCP tool for Git operations"""
    
async def backup_project_tool(project_path: str, backup_location: str = None) -> str:
    """MCP tool to backup project"""
    
async def restore_session_tool(session_id: int, project_path: str) -> str:
    """MCP tool to restore previous session"""
```

## Database Schema (database_schema.sql)
```sql
-- Core project tables
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT,
    methodology TEXT,
    project_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    session_type TEXT NOT NULL, -- planning, execution, analysis, publication
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    user_id TEXT,
    status TEXT DEFAULT 'active',
    metadata JSON
);

-- Socratic questioning interactions
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    interaction_type TEXT NOT NULL, -- question, answer, guidance, suggestion
    content TEXT NOT NULL,
    metadata JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vector_id TEXT -- Reference to vector database
);

-- Research requirements
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    category TEXT NOT NULL, -- objective, methodology, timeline, resources
    requirement_text TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality assurance records
CREATE TABLE IF NOT EXISTS quality_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    check_type TEXT NOT NULL, -- peer_review, validation, verification
    component TEXT NOT NULL, -- proposal, methodology, data, manuscript
    result TEXT NOT NULL, -- passed, failed, needs_review
    comments TEXT,
    performed_by TEXT, -- user_id or 'system'
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document management
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    document_type TEXT NOT NULL, -- proposal, protocol, manuscript
    file_path TEXT NOT NULL,
    version TEXT,
    git_commit_hash TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research methodology knowledge base
CREATE TABLE IF NOT EXISTS methodologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    requirements TEXT,
    best_practices TEXT,
    examples TEXT,
    domain TEXT,
    complexity_level INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_interactions_session_id ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_requirements_project_id ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_quality_checks_project_id ON quality_checks(project_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_methodologies_domain ON methodologies(domain);
```

## Configuration (default_config.json)
```json
{
    "storage": {
        "sqlite": {
            "database_name": "sessions.db",
            "backup_interval": 3600,
            "auto_vacuum": true
        },
        "vector_db": {
            "type": "chromadb",
            "embedding_model": "all-MiniLM-L6-v2",
            "collections": {
                "research_literature": {"distance": "cosine"},
                "methodologies": {"distance": "cosine"},
                "interactions": {"distance": "cosine"},
                "templates": {"distance": "cosine"}
            }
        },
        "git": {
            "auto_commit": true,
            "commit_message_template": "[SRRD] {action}: {description}",
            "backup_remotes": [],
            "ignore_patterns": ["*.tmp", "*.log", "__pycache__/"]
        }
    },
    "project": {
        "directory_structure": {
            "data": ["raw", "processed", "analysis"],
            "documents": ["proposal", "protocols", "reports", "manuscripts"],
            "methodology": [],
            "logs": ["sessions", "guidance", "quality_checks"]
        }
    }
}
```

This prototype provides a solid foundation for implementing the local storage system with Git, SQLite, and vector database integration.
