import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

from storage.project_manager import ProjectManager

# Fix import path issues by adding utils directory to sys.path
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

from context_decorator import context_aware
from current_project import get_current_project as get_project_path


@context_aware(allow_explicit_project_path=True)
async def initialize_project_tool(**kwargs) -> str:
    """MCP tool to initialize Git-based project storage"""
    project_manager = None
    try:
        name = kwargs.get("name")
        description = kwargs.get("description")
        domain = kwargs.get("domain")
        project_path = kwargs.get("project_path")

        if not all([name, description, domain]):
            return "Error: Missing required parameters (name, description, domain)"

        try:
            resolved_path, error = _resolve_project_location(name, project_path)
            if error:
                return error
        except Exception as e:
            return f"Error: {str(e)}"

        if os.path.exists(resolved_path):
            return f"Error: Project already exists at {resolved_path}"

        project_manager = ProjectManager(resolved_path)
        result = await project_manager.initialize_project(name, description, domain)

        guidance = _get_project_creation_guidance(resolved_path)
        auto_switched = result.get("auto_switched", False)

        if auto_switched:
            switch_status = """**MCP Context Automatically Switched!**
Claude Desktop is now using this project for all research tools."""
            next_steps = """**Your project is ready!**

What would you like to work on next?
- Use **clarify_research_goals** if you want to refine your research objectives
- Use **suggest_methodology** if you want research methodology recommendations  
- Use **start_research_session** if you want to begin a formal research session
- Or simply tell me what aspect of your research you'd like to focus on"""
        else:
            switch_status = """**Manual Switch Required**
Auto-switch failed. Please run: srrd switch"""
            next_steps = f"""**Setup Required**:
1. Navigate to your project: cd {resolved_path}
2. Switch MCP context: srrd switch
3. Then tell me what you'd like to work on!"""

        return f"""Project '{name}' initialized successfully!

**Project Location**: {resolved_path}
**Status**: {result.get('status', 'initialized')}
**Project ID**: {result.get('project_id', 'N/A')}

{guidance}

{switch_status}

{next_steps}
"""
    finally:
        if project_manager:
            await project_manager.close()


def _resolve_project_location(
    project_name: str, requested_path: Optional[str] = None
) -> (str, Optional[str]):
    """Resolve where the new project should be created based on current context, with strict validation.
    Returns (resolved_path, error_message)"""

    from pathlib import Path

    home_projects = Path.home() / "Projects"

    if not requested_path:
        if not home_projects.exists():
            try:
                home_projects.mkdir(exist_ok=True)
            except Exception as e:
                return "", f"Error: Could not create ~/Projects directory: {str(e)}"
        resolved = home_projects / project_name.lower().replace(" ", "-")
        return str(resolved), None

    requested = Path(requested_path)
    if requested.is_absolute():
        if not requested.parent.exists():
            return (
                "",
                f"Error: Parent directory of specified absolute path does not exist: {requested.parent}",
            )
        return str(requested), None

    if not home_projects.exists():
        try:
            home_projects.mkdir(exist_ok=True)
        except Exception as e:
            return "", f"Error: Could not create ~/Projects directory: {str(e)}"
    resolved = home_projects / requested_path
    return str(resolved), None


def _get_project_creation_guidance(project_path: str) -> str:
    """Provide guidance based on where the project was created"""
    path = Path(project_path)
    if "Projects" in str(path):
        return """**Location**: Created in your home Projects directory
**Context**: This is now your active SRRD project"""
    else:
        return """**Location**: Created alongside your current project
**Context**: Automatically switched to this new project"""


@context_aware(require_context=True)
async def save_session_tool(**kwargs) -> str:
    """MCP tool to save research session data"""
    project_manager = None
    try:
        session_data = kwargs.get("session_data")
        project_path = get_project_path()

        if not session_data:
            return "Error: Missing session_data parameter"

        project_manager = ProjectManager(project_path)
        return f"Session saved to project: {project_path}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def search_knowledge_tool(**kwargs) -> str:
    """MCP tool for vector database search"""
    project_manager = None
    try:
        query = kwargs.get("query")
        collection = kwargs.get("collection", "default")
        project_path = get_project_path()

        if not query:
            return "Error: Missing required parameter (query)"

        project_manager = ProjectManager(project_path)
        results = await project_manager.vector_manager.search_knowledge(
            query, collection
        )
        return f"Search results: {results}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def version_control_tool(**kwargs) -> str:
    """MCP tool for Git operations"""
    project_manager = None
    try:
        action = kwargs.get("action")
        message = kwargs.get("message")
        files = kwargs.get("files", [])
        project_path = get_project_path()

        if not all([action, message]):
            return "Error: Missing required parameters (action, message)"

        project_manager = ProjectManager(project_path)
        if action == "commit":
            commit_hash = project_manager.git_manager.commit_changes(message, files)
            return f"Committed changes with hash: {commit_hash}"
        return "Unknown action"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def backup_project_tool(**kwargs) -> str:
    """MCP tool to backup project"""
    project_manager = None
    try:
        project_path = get_project_path()
        backup_location = kwargs.get("backup_location")

        project_manager = ProjectManager(project_path)
        result = project_manager.backup_project(backup_location)
        return f"Project backed up with status: {result}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def restore_session_tool(**kwargs) -> str:
    """MCP tool to restore previous session"""
    session_id = kwargs.get("session_id")
    project_path = get_project_path()

    if not session_id:
        return "Error: Missing required parameter (session_id)"

    return "Session restored"


@context_aware(require_context=False)
async def switch_project_context_tool(**kwargs) -> str:
    """MCP tool to switch MCP context to a different project"""
    target_project_path = kwargs.get("target_project_path")

    if not target_project_path:
        return """Error: Missing required parameter (target_project_path)"""

    from pathlib import Path

    from current_project import set_current_project

    target_path = Path(target_project_path).resolve()
    if not (target_path.exists() and (target_path / ".srrd").exists()):
        return f"Error: Target directory is not a valid SRRD project: {target_path}"

    try:
        set_current_project(str(target_path))
        return f"**MCP Context Switched Successfully!**\n\n**Active Project**: {target_path.name}"
    except Exception as e:
        return f"**Error switching MCP context**: {str(e)}"


@context_aware(require_context=False)
async def reset_project_context_tool(**kwargs) -> str:
    """MCP tool to reset MCP context to global home project"""
    try:
        import importlib.util
        from pathlib import Path

        launcher_config_path = (
            Path(__file__).resolve().parent.parent.parent.parent.parent
            / "srrd_builder"
            / "utils"
            / "launcher_config.py"
        )
        spec = importlib.util.spec_from_file_location(
            "launcher_config", launcher_config_path
        )
        launcher_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher_config)
        reset_to_global_project = launcher_config.reset_to_global_project
        success, error, global_project_path = reset_to_global_project()
        if success:
            return f"**MCP Context Reset to Global Home Project!**\n\n**Global Project Path**: {global_project_path}"
        else:
            return f"**Failed to reset to global project**: {error}"
    except Exception as e:
        return f"**Error resetting to global project**: {str(e)}"


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
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional)",
                },
            },
            "required": ["name", "description", "domain"],
        },
        handler=initialize_project_tool,
    )

    server.register_tool(
        name="save_session",
        description="Save current research session data",
        parameters={
            "type": "object",
            "properties": {
                "session_data": {
                    "type": "object",
                    "description": "Session data to save",
                },
            },
            "required": ["session_data"],
        },
        handler=save_session_tool,
    )

    server.register_tool(
        name="search_knowledge",
        description="Search knowledge base using vector search",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "collection": {"type": "string", "description": "Collection to search"},
            },
            "required": ["query"],
        },
        handler=search_knowledge_tool,
    )

    server.register_tool(
        name="version_control",
        description="Perform Git version control operations",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Git action (e.g., commit)",
                },
                "message": {"type": "string", "description": "Commit message"},
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files to include",
                },
            },
            "required": ["action", "message"],
        },
        handler=version_control_tool,
    )

    server.register_tool(
        name="backup_project",
        description="Backup project to specified location",
        parameters={
            "type": "object",
            "properties": {
                "backup_location": {
                    "type": "string",
                    "description": "Backup destination",
                },
            },
            "required": [],
        },
        handler=backup_project_tool,
    )

    server.register_tool(
        name="restore_session",
        description="Restore a previous research session",
        parameters={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "integer",
                    "description": "Session ID to restore",
                },
            },
            "required": ["session_id"],
        },
        handler=restore_session_tool,
    )

    server.register_tool(
        name="switch_project_context",
        description="Switch MCP context to a different SRRD project.",
        parameters={
            "type": "object",
            "properties": {
                "target_project_path": {
                    "type": "string",
                    "description": "Absolute path to the target SRRD project directory",
                }
            },
            "required": ["target_project_path"],
        },
        handler=switch_project_context_tool,
    )

    server.register_tool(
        name="reset_project_context",
        description="Reset MCP context to global home project.",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=reset_project_context_tool,
    )
