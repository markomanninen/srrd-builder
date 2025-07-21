from pathlib import Path
from typing import Dict, Any, Optional
import logging
from .git_manager import GitManager
from .sqlite_manager import SQLiteManager
from .vector_manager import VectorManager

# Get logger for this module
logger = logging.getLogger("srrd_builder.project_manager")

class ProjectManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git_manager = GitManager(project_path)
        self.sqlite_manager = SQLiteManager(str(self.project_path / '.srrd' / 'data' / 'sessions.db'))
        self.vector_manager = VectorManager(str(self.project_path / '.srrd' / 'data' / 'knowledge.db'))

    async def initialize_project(self, name: str, description: str, domain: str) -> Dict[str, Any]:
        """Initialize complete project structure"""
        logger.info(f"Initializing project '{name}' in domain '{domain}'...")
        
        logger.debug("Creating directory structure...")
        self.create_directory_structure()
        
        logger.debug("Setting up configuration...")
        self.setup_configuration({
            'name': name,
            'description': description,
            'domain': domain
        })
        
        logger.debug("Initializing Git repository...")
        self.git_manager.initialize_repository()
        
        logger.debug("Setting up database...")
        await self.sqlite_manager.initialize_database()
        
        logger.debug("Initializing vector search capabilities...")
        await self.vector_manager.initialize(enable_embedding_model=False)
        
        logger.debug("Creating project record...")
        project_id = await self.sqlite_manager.create_project(name, description, domain)
        
        logger.debug("Automatically switching MCP context to new project...")
        switch_success, switch_error = self._configure_global_launcher()
        if not switch_success:
            logger.warning(f"Project created successfully, but MCP context switch failed: {switch_error}")
            logger.warning("You may need to run 'srrd switch' manually.")
        
        logger.info(f"Project '{name}' initialized successfully! (ID: {project_id})")
        if switch_success:
            logger.info(f"MCP context automatically switched to: {self.project_path}")
            
        return {
            "project_id": project_id, 
            "status": "initialized", 
            "project_path": str(self.project_path),
            "auto_switched": switch_success
        }

    def create_directory_structure(self) -> bool:
        """Create standard research project directories"""
        # Create project directory if it doesn't exist
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard SRRD directory structure
        directories = [
            self.project_path / '.srrd',
            self.project_path / '.srrd' / 'data',
            self.project_path / 'work',
            self.project_path / 'work' / 'research',
            self.project_path / 'work' / 'drafts',
            self.project_path / 'work' / 'data',
            self.project_path / 'docs',
            self.project_path / 'publications'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        return True

    def setup_configuration(self, config: Dict[str, Any]) -> bool:
        """Setup project-specific configuration"""
        import json
        from datetime import datetime
        
        # Create proper SRRD configuration
        full_config = {
            "version": "0.1.0",
            "project_name": config.get('name', self.project_path.name),
            "domain": config.get('domain', 'general'),
            "template": config.get('template', 'research'),
            "created_at": datetime.now().isoformat(),
            "mcp_server": {
                "enabled": True,
                "project_path": str(self.project_path)
            },
            "storage": {
                "git_enabled": True,
                "sqlite_db": ".srrd/data/sessions.db",
                "vector_db": ".srrd/data/knowledge.db"
            },
            "latex": {
                "output_dir": "publications",
                "draft_dir": "work/drafts"
            }
        }
        
        config_file = self.project_path / '.srrd' / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(full_config, f, indent=2)
        return True

    def _configure_global_launcher(self) -> tuple[bool, Optional[str]]:
        """Configure the global MCP launcher for this project using shared utility"""
        try:
            # Import the shared launcher configuration utility
            import sys
            import os
            
            # Find and add the srrd_builder package to path
            current_dir = Path(__file__).resolve().parent
            while current_dir != current_dir.parent:
                srrd_builder_dir = current_dir / 'srrd_builder'
                if srrd_builder_dir.exists() and (srrd_builder_dir / 'utils' / 'launcher_config.py').exists():
                    if str(current_dir) not in sys.path:
                        sys.path.insert(0, str(current_dir))
                    break
                current_dir = current_dir.parent
            
            from srrd_builder.utils.launcher_config import configure_global_launcher
            
            srrd_dir = self.project_path / '.srrd'
            success, error = configure_global_launcher(self.project_path, srrd_dir)
            return success, error
            
        except ImportError as e:
            error_msg = f"Could not import launcher configuration utility: {e}"
            logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error configuring launcher: {e}"
            logger.warning(error_msg)
            return False, error_msg

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
