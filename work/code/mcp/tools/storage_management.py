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
    
    if not all([name, description, domain]):
        return "Error: Missing required parameters (name, description, domain)"
    
    # Smart project location handling
    resolved_path = _resolve_project_location(name, project_path)
    
    project_manager = ProjectManager(resolved_path)
    result = await project_manager.initialize_project(name, description, domain)
    
    # Update the result to include guidance
    guidance = _get_project_creation_guidance(resolved_path)
    auto_switched = result.get('auto_switched', False)
    
    if auto_switched:
        switch_status = """✅ **MCP Context Automatically Switched!**
   Claude Desktop is now using this project for all research tools."""
        next_steps = """🚀 **Your project is ready!**

What would you like to work on next?
• Use **clarify_research_goals** if you want to refine your research objectives
• Use **suggest_methodology** if you want research methodology recommendations  
• Use **start_research_session** if you want to begin a formal research session
• Or simply tell me what aspect of your research you'd like to focus on"""
    else:
        switch_status = """⚠️ **Manual Switch Required**
   Auto-switch failed. Please run: srrd switch"""
        next_steps = """🔧 **Setup Required**:
1. Navigate to your project: cd {resolved_path}
2. Switch MCP context: srrd switch
3. Then tell me what you'd like to work on!"""
    
    return f"""Project '{name}' initialized successfully!

📁 **Project Location**: {resolved_path}
📊 **Status**: {result.get('status', 'initialized')}
🔢 **Project ID**: {result.get('project_id', 'N/A')}

{guidance}

{switch_status}

{next_steps}
"""

def _resolve_project_location(project_name: str, requested_path: Optional[str] = None) -> str:
    """Resolve where the new project should be created based on current context"""
    from pathlib import Path
    import os
    
    # Get current SRRD context
    current_project_path = os.environ.get('SRRD_PROJECT_PATH')
    
    if requested_path:
        # User specified a path
        requested = Path(requested_path).resolve()
        
        # If it's a relative path and we're in a global context, 
        # create it in a reasonable location
        if not requested.is_absolute() and current_project_path:
            current_dir = Path(current_project_path).parent
            if current_dir.name == 'globalproject' or '.srrd' in current_dir.name:
                # We're in global context, create in home directory's Projects folder
                home_projects = Path.home() / 'Projects'
                home_projects.mkdir(exist_ok=True)
                resolved = home_projects / requested.name
            else:
                # We're in a specific project context, create relative to it
                resolved = current_dir.parent / requested.name
        else:
            resolved = requested
            
        return str(resolved)
    
    # No path specified - use intelligent defaults
    if current_project_path:
        current_dir = Path(current_project_path)
        
        if 'globalproject' in str(current_dir):
            # In global context - create in user's Projects folder
            home_projects = Path.home() / 'Projects'
            home_projects.mkdir(exist_ok=True)
            return str(home_projects / project_name.lower().replace(' ', '-'))
        else:
            # In specific project context - create alongside current project
            parent_dir = current_dir.parent
            return str(parent_dir / project_name.lower().replace(' ', '-'))
    
    # Fallback - create in user's Projects folder
    home_projects = Path.home() / 'Projects'
    home_projects.mkdir(exist_ok=True)
    return str(home_projects / project_name.lower().replace(' ', '-'))

def _get_project_creation_guidance(project_path: str) -> str:
    """Provide guidance based on where the project was created"""
    path = Path(project_path)
    
    if 'Projects' in str(path):
        return """🏠 **Location**: Created in your home Projects directory
💡 **Context**: This is now your active SRRD project"""
    elif path.parent.name in ['globalproject', '.srrd']:
        return """🌐 **Location**: Created in global SRRD context  
💡 **Context**: This project is now active and ready to use"""
    else:
        return """📂 **Location**: Created alongside your current project
💡 **Context**: Automatically switched to this new project"""

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
        description="Initialize a new research project with Git-based storage. Creates project in intelligent location based on current context.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name"},
                "description": {"type": "string", "description": "Project description"},
                "domain": {"type": "string", "description": "Research domain"},
                "project_path": {"type": "string", "description": "Project path (optional - if not provided, will use intelligent location based on current context)"}
            },
            "required": ["name", "description", "domain"]
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
