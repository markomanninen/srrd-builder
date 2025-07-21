from typing import Dict, Any, Optional, List
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

from storage.project_manager import ProjectManager

# Import context-aware decorator
import sys
from pathlib import Path

# Fix import path issues by adding utils directory to sys.path
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

from context_decorator import context_aware, project_required

@context_aware()
async def initialize_project_tool(**kwargs) -> str:
    """MCP tool to initialize Git-based project storage"""
    name = kwargs.get('name')
    description = kwargs.get('description') 
    domain = kwargs.get('domain')
    project_path = kwargs.get('project_path')
    
    if not all([name, description, domain, project_path]):
        return "Error: Missing required parameters (name, description, domain, project_path)"
    
    project_manager = ProjectManager(project_path)
    result = await project_manager.initialize_project(name, description, domain)
    return f"Project initialized with status: {result}"

@context_aware()
async def save_session_tool(**kwargs) -> str:
    """MCP tool to save research session data"""
    session_data = kwargs.get('session_data')
    project_path = kwargs.get('project_path')
    
    if not session_data:
        return "Error: Missing session_data parameter"
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    project_manager = ProjectManager(project_path)
    # This is a placeholder until the session manager is implemented
    return "Session saved"

@context_aware()
async def search_knowledge_tool(**kwargs) -> str:
    """MCP tool for vector database search"""
    query = kwargs.get('query')
    collection = kwargs.get('collection', 'default')
    project_path = kwargs.get('project_path')
    
    if not query:
        return "Error: Missing required parameter (query)"
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    project_manager = ProjectManager(project_path)
    results = await project_manager.vector_manager.search_knowledge(query, collection)
    return f"Search results: {results}"

@context_aware()
async def version_control_tool(**kwargs) -> str:
    """MCP tool for Git operations"""
    action = kwargs.get('action')
    message = kwargs.get('message')
    files = kwargs.get('files', [])
    project_path = kwargs.get('project_path')
    
    if not all([action, message]):
        return "Error: Missing required parameters (action, message)"
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    project_manager = ProjectManager(project_path)
    if action == "commit":
        commit_hash = project_manager.git_manager.commit_changes(message, files)
        return f"Committed changes with hash: {commit_hash}"
    return "Unknown action"

@context_aware()
async def backup_project_tool(**kwargs) -> str:
    """MCP tool to backup project"""
    project_path = kwargs.get('project_path')
    backup_location = kwargs.get('backup_location')
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    project_manager = ProjectManager(project_path)
    result = project_manager.backup_project(backup_location)
    return f"Project backed up with status: {result}"

@context_aware()
async def restore_session_tool(**kwargs) -> str:
    """MCP tool to restore previous session"""
    session_id = kwargs.get('session_id')
    project_path = kwargs.get('project_path')
    
    if not session_id:
        return "Error: Missing required parameter (session_id)"
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    project_manager = ProjectManager(project_path)
    # This is a placeholder until the session manager is implemented
    return "Session restored"

def register_storage_tools(server):
    """Register storage management tools with the MCP server"""
    
    server.register_tool(
        name="initialize_project",
        description="Initialize a new research project with Git-based storage",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name"},
                "description": {"type": "string", "description": "Project description"},
                "domain": {"type": "string", "description": "Research domain"},
                "project_path": {"type": "string", "description": "Path where project will be created"}
            },
            "required": ["name", "description", "domain", "project_path"]
        },
        handler=initialize_project_tool
    )
    
    server.register_tool(
        name="save_session",
        description="Save current research session data",
        parameters={
            "type": "object",
            "properties": {
                "session_data": {"type": "object", "description": "Session data to save"},
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"}
            },
            "required": ["session_data"]
        },
        handler=save_session_tool
    )
    
    server.register_tool(
        name="search_knowledge",
        description="Search knowledge base using vector search",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "collection": {"type": "string", "description": "Collection to search"}
            },
            "required": ["query"]
        },
        handler=search_knowledge_tool
    )
    
    server.register_tool(
        name="version_control",
        description="Perform Git version control operations",
        parameters={
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Git action (commit, push, pull, etc.)"},
                "message": {"type": "string", "description": "Commit message"},
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files to include"}
            },
            "required": ["action", "message"]
        },
        handler=version_control_tool
    )
    
    server.register_tool(
        name="backup_project",
        description="Backup project to specified location",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path to backup (optional - auto-detected when in SRRD project)"},
                "backup_location": {"type": "string", "description": "Backup destination"}
            },
            "required": []
        },
        handler=backup_project_tool
    )
    
    server.register_tool(
        name="restore_session",
        description="Restore a previous research session",
        parameters={
            "type": "object",
            "properties": {
                "session_id": {"type": "integer", "description": "Session ID to restore"},
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"}
            },
            "required": ["session_id"]
        },
        handler=restore_session_tool
    )
