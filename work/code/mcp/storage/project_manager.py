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

    async def initialize_project(self, name: str, description: str, domain: str) -> Dict[str, Any]:
        """Initialize complete project structure"""
        print(f"🚀 Initializing project '{name}' in domain '{domain}'...")
        
        print("📁 Creating directory structure...")
        self.create_directory_structure()
        
        print("🔧 Initializing Git repository...")
        self.git_manager.initialize_repository()
        
        print("🗄️  Setting up database...")
        await self.sqlite_manager.initialize_database()
        
        print("🔍 Initializing vector search capabilities...")
        await self.vector_manager.initialize(enable_embedding_model=False)
        
        print("💾 Creating project record...")
        project_id = await self.sqlite_manager.create_project(name, description, domain)
        
        print(f"✅ Project '{name}' initialized successfully! (ID: {project_id})")
        return {"project_id": project_id, "status": "initialized"}

    def create_directory_structure(self) -> bool:
        """Create standard research project directories"""
        (self.project_path / '.srrd').mkdir(exist_ok=True)
        return True

    def setup_configuration(self, config: Dict[str, Any]) -> bool:
        """Setup project-specific configuration"""
        with open(self.project_path / '.srrd' / 'config.json', 'w') as f:
            f.write(str(config))
        return True

    def backup_project(self, backup_location: Optional[str] = None) -> bool:
        """Create complete project backup"""
        # This is a placeholder
        return True

    def restore_project(self, backup_location: str) -> bool:
        """Restore project from backup"""
        # This is a placeholder
        return True

    def get_project_status(self) -> Dict[str, Any]:
        """Get comprehensive project status"""
        # This is a placeholder
        return {}
