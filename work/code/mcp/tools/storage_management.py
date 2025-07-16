from typing import Dict, Any, Optional, List
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

from storage.project_manager import ProjectManager

async def initialize_project_tool(name: str, description: str, domain: str, project_path: str) -> str:
    """MCP tool to initialize Git-based project storage"""
    project_manager = ProjectManager(project_path)
    result = project_manager.initialize_project(name, description, domain)
    return f"Project initialized with status: {result}"

async def save_session_tool(session_data: dict, project_path: str) -> str:
    """MCP tool to save research session data"""
    project_manager = ProjectManager(project_path)
    # This is a placeholder until the session manager is implemented
    return "Session saved"

async def search_knowledge_tool(query: str, collection: str, project_path: str) -> str:
    """MCP tool for vector database search"""
    project_manager = ProjectManager(project_path)
    results = project_manager.vector_manager.search_knowledge(query, collection)
    return f"Search results: {results}"

async def version_control_tool(action: str, message: str, files: list, project_path: str) -> str:
    """MCP tool for Git operations"""
    project_manager = ProjectManager(project_path)
    if action == "commit":
        commit_hash = project_manager.git_manager.commit_changes(message, files)
        return f"Committed changes with hash: {commit_hash}"
    return "Unknown action"

async def backup_project_tool(project_path: str, backup_location: str = None) -> str:
    """MCP tool to backup project"""
    project_manager = ProjectManager(project_path)
    result = project_manager.backup_project(backup_location)
    return f"Project backed up with status: {result}"

async def restore_session_tool(session_id: int, project_path: str) -> str:
    """MCP tool to restore previous session"""
    project_manager = ProjectManager(project_path)
    # This is a placeholder until the session manager is implemented
    return "Session restored"

def register_storage_tools(server):
    """Register storage management tools with the MCP server"""
    server.tools["initialize_project"] = initialize_project_tool
    server.tools["save_session"] = save_session_tool
    server.tools["search_knowledge"] = search_knowledge_tool
    server.tools["version_control"] = version_control_tool
    server.tools["backup_project"] = backup_project_tool
    server.tools["restore_session"] = restore_session_tool
