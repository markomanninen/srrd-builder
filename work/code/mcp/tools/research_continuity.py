"""
Research Continuity Tools
Research lifecycle persistence and workflow guidance
"""

import json
import sys
from pathlib import Path

from storage.sqlite_manager import SQLiteManager
from utils.context_decorator import ContextAwareError, context_aware
from utils.current_project import get_current_project
from utils.research_framework import ResearchFrameworkService
from utils.workflow_intelligence import WorkflowIntelligence

# NOTE: All sys.path manipulations have been removed.
# The execution environment (e.g., conftest.py, application entry point)
# is responsible for ensuring work/code/mcp is on the PYTHONPATH.


# Function to safely initialize services when needed
def _get_research_framework():
    """Get research framework service, initializing if needed"""
    if ResearchFrameworkService:
        return ResearchFrameworkService()
    return None


@context_aware(require_context=True)
async def get_research_progress_tool(**kwargs) -> str:
    """Get current research progress across all acts and categories"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    try:
        # Get project information
        project_dir = Path(project_path)
        config_file = project_dir / ".srrd" / "config.json"

        # Load project config
        project_config = {}
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    project_config = json.load(f)
            except Exception:
                project_config = {}

        project_name = project_config.get("project_name", project_dir.name)
        project_domain = project_config.get("domain", "Unknown")
        project_description = project_config.get(
            "description", "No description available"
        )

        # Always use canonical getter for sessions.db
        db_path = SQLiteManager.get_sessions_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        sql_query = (
            "SELECT id, name, created_at FROM projects ORDER BY created_at DESC LIMIT 1"
        )

        # Get project ID and stats from database
        async with sqlite_manager.connection.execute(sql_query) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                await sqlite_manager.close()
                return f"""# Research Progress Analysis

## Project Information
- **Name**: {project_name}
- **Directory**: {project_path}
- **Domain**: {project_domain}
- **Description**: {project_description}
- **Status**: Not initialized - No project found in database

Please initialize the project by running research tools first."""

        project_id = project_row[0]
        created_at = project_row[2]

        # Check for recent activity
        async with sqlite_manager.connection.execute(
            """SELECT COUNT(*) FROM tool_usage tu 
               JOIN sessions s ON tu.session_id = s.id 
               WHERE s.project_id = ? AND tu.timestamp > datetime('now', '-7 days')""",
            (project_id,),
        ) as cursor:
            recent_activity = await cursor.fetchone()
            recent_count = recent_activity[0] if recent_activity else 0

        # Determine project status
        if recent_count > 0:
            status = f"Active ({recent_count} tools used in last 7 days)"
        else:
            status = "Inactive (no recent activity)"

        # Initialize workflow intelligence and research framework
        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        # Analyze research progress
        analysis = await workflow_intelligence.analyze_research_progress(project_id)

        # Format response with project information
        response = f"""# Research Progress Analysis

## Project Information
- **Name**: {project_name}
- **Directory**: {project_path}
- **Domain**: {project_domain}
- **Description**: {project_description}
- **Status**: {status}
- **Created**: {created_at}

## Overall Progress
- **Completion**: {analysis['overall_progress']['completion_percentage']:.1f}%
- **Tools Used**: {analysis['overall_progress']['tools_used']}/{analysis['overall_progress']['total_tools']}

## Research Acts Progress
"""

        for act_name, progress in analysis["research_acts"].items():
            if (
                research_framework
                and hasattr(research_framework, "acts")
                and act_name in research_framework.acts
            ):
                act_display_name = research_framework.acts[act_name]["name"]
            else:
                act_display_name = act_name.replace("_", " ").title()
            response += f"- **{act_display_name}**: {progress['completion_percentage']:.1f}% ({progress['tools_used']}/{progress['total_tools']} tools)\n"

        response += "\n## Research Velocity\n"
        velocity = analysis["research_velocity"]
        response += f"- **Tools per day**: {velocity['tools_per_day']}\n"
        response += f"- **Trend**: {velocity['velocity_trend']}\n"
        if velocity["estimated_completion_days"]:
            response += f"- **Estimated completion**: {velocity['estimated_completion_days']} days\n"

        response += "\n## Workflow Health\n"
        health = analysis["workflow_health"]
        response += f"- **Health Score**: {health['health_score']}/100 ({health['health_status']})\n"
        response += f"- **Balance Score**: {health['balance_score']}/100\n"

        if health["issues"]:
            response += "- **Issues**: " + ", ".join(health["issues"]) + "\n"

        if analysis["next_steps"]:
            response += "\n## Recommended Next Steps\n"
            for i, rec in enumerate(analysis["next_steps"][:3], 1):
                response += f"{i}. **{rec['tool']}** ({rec['priority']} priority): {rec['reason']}\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if isinstance(e, ContextAwareError):
            raise
        return f"Error analyzing research progress: {str(e)}"


@context_aware(require_context=True)
async def get_tool_usage_history_tool(**kwargs) -> str:
    """Get chronological tool usage history for session/project"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    session_id = kwargs.get("session_id")
    limit = kwargs.get("limit", 20)

    try:
        db_path = SQLiteManager.get_sessions_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        research_framework = _get_research_framework()

        if session_id:
            history = await sqlite_manager.get_tool_usage_history(session_id)
        else:
            async with sqlite_manager.connection.execute(
                """SELECT tu.* FROM tool_usage tu 
                   JOIN sessions s ON tu.session_id = s.id 
                   WHERE s.project_id = (SELECT id FROM projects ORDER BY created_at DESC LIMIT 1)
                   ORDER BY tu.timestamp DESC LIMIT ?""",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            history = [dict(zip(columns, row)) for row in rows]

        if not history:
            await sqlite_manager.close()
            return "No tool usage history found."

        response = "# Tool Usage History\n\n"
        for entry in history:
            act_name = (
                research_framework.acts[entry["research_act"]]["name"]
                if research_framework
                and entry["research_act"] in research_framework.acts
                else entry["research_act"].replace("_", " ").title()
            )
            response += f"## {entry['timestamp']}\n"
            response += f"- **Tool**: {entry['tool_name']} {'PASS' if entry['success'] else 'FAIL'}\n"
            response += f"- **Research Act**: {act_name}\n\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if isinstance(e, ContextAwareError):
            raise
        return f"Error retrieving tool usage history: {str(e)}"


@context_aware(require_context=True)
async def get_workflow_recommendations_tool(**kwargs) -> str:
    """Get AI-generated recommendations for next research steps"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")

    try:
        db_path = SQLiteManager.get_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                await sqlite_manager.close()
                return "No project found in database."
        project_id = project_row[0]

        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        async with sqlite_manager.connection.execute(
            "SELECT id FROM sessions WHERE project_id = ? ORDER BY started_at DESC LIMIT 1",
            (project_id,),
        ) as cursor:
            session_row = await cursor.fetchone()
        session_id = session_row[0] if session_row else 1

        recommendations = await workflow_intelligence.generate_recommendations(
            project_id, session_id
        )

        if not recommendations:
            await sqlite_manager.close()
            return "No specific recommendations available at this time."

        response = "# Workflow Recommendations\n\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"## {i}. {rec['tool']} ({rec['priority']} priority)\n"
            response += f"- **Reasoning**: {rec['enhanced_reasoning']}\n\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if isinstance(e, ContextAwareError):
            raise
        return f"Error generating workflow recommendations: {str(e)}"


@context_aware(require_context=True)
async def get_research_milestones_tool(**kwargs) -> str:
    """Get achieved research milestones and upcoming targets"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    limit = kwargs.get("limit", 10)

    try:
        db_path = SQLiteManager.get_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                await sqlite_manager.close()
                return "No project found in database."
        project_id = project_row[0]

        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        milestones = await workflow_intelligence.detect_milestones(project_id)

        if not milestones:
            await sqlite_manager.close()
            return "# Research Milestones\n\nNo milestones achieved yet."

        response = "# Research Milestones\n\n"
        for milestone in milestones:
            response += f"- **{milestone['name']}**\n  {milestone['description']}\n\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if isinstance(e, ContextAwareError):
            raise
        return f"Error retrieving research milestones: {str(e)}"


@context_aware(require_context=True)
async def start_research_session_tool(**kwargs) -> str:
    """Start a new research session with act-specific goals"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    research_act = kwargs.get("research_act")
    session_goals = kwargs.get("session_goals", [])
    research_focus = kwargs.get("research_focus")

    sqlite_manager = None
    try:
        db_path = SQLiteManager.get_db_path(project_path)
        
        # Check if database file exists first
        from pathlib import Path
        if not Path(db_path).exists():
            return f"Error: Project database not found at {db_path}. Run 'initialize_project' tool first to create the project."
        
        sqlite_manager = SQLiteManager(db_path)
        
        # Try to initialize database connection
        try:
            await sqlite_manager.initialize()
        except Exception as init_error:
            if "no such table" in str(init_error).lower():
                return f"Error: Database schema is incomplete at {db_path}. Run 'initialize_project' tool to fix the database schema."
            elif "database is locked" in str(init_error).lower():
                return f"Error: Database is locked by another process. Wait a moment and try again."
            return f"Error: Cannot connect to database at {db_path}: {str(init_error)}"

        # Check if any projects exist
        try:
            async with sqlite_manager.connection.execute(
                "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
            ) as cursor:
                project_row = await cursor.fetchone()
                if not project_row:
                    await sqlite_manager.close()
                    return "Error: No projects found in database. Run 'initialize_project' tool first with parameters: name, description, domain, and project_path."
        except Exception as query_error:
            await sqlite_manager.close()
            return f"Error: Cannot query projects table. Database may be corrupted: {str(query_error)}"
        
        project_id = project_row[0]

        # Try to create the session
        try:
            session_id = await sqlite_manager.create_session(
                project_id=project_id, session_type="research", user_id="claude_user"
            )
            await sqlite_manager.update_session_research_context(
                session_id=session_id,
                current_research_act=research_act,
                research_focus=research_focus,
                session_goals=session_goals,
            )
        except Exception as session_error:
            await sqlite_manager.close()
            return f"Error: Failed to create research session in database: {str(session_error)}"

        response = f"# New Research Session Started\n\n**Session ID**: {session_id}\n"
        if research_act:
            response += f"**Research Act**: {research_act}\n"
        if research_focus:
            response += f"**Focus**: {research_focus}\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if sqlite_manager:
            try:
                await sqlite_manager.close()
            except:
                pass  # Ignore cleanup errors
        if isinstance(e, ContextAwareError):
            raise
        return f"Error: Unexpected failure in start_research_session - {str(e)}"


@context_aware(require_context=True)
async def get_session_summary_tool(**kwargs) -> str:
    """Get comprehensive summary of current session progress"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    session_id = kwargs.get("session_id")

    # Validate session_id parameter if provided
    if session_id is not None and not isinstance(session_id, int):
        return "Error: session_id parameter must be an integer"

    sqlite_manager = None
    try:
        db_path = SQLiteManager.get_db_path(project_path)
        
        # Check if database file exists first
        from pathlib import Path
        if not Path(db_path).exists():
            return f"Error: Project database not found at {db_path}. Run 'initialize_project' tool first to create the project."
        
        sqlite_manager = SQLiteManager(db_path)
        
        # Try to initialize database connection
        try:
            await sqlite_manager.initialize()
        except Exception as init_error:
            if "no such table" in str(init_error).lower():
                return f"Error: Database schema is incomplete at {db_path}. Run 'initialize_project' tool to fix the database schema."
            elif "database is locked" in str(init_error).lower():
                return f"Error: Database is locked by another process. Wait a moment and try again."
            return f"Error: Cannot connect to database at {db_path}: {str(init_error)}"

        # Find session to summarize
        try:
            if not session_id:
                async with sqlite_manager.connection.execute(
                    "SELECT id FROM sessions ORDER BY started_at DESC LIMIT 1"
                ) as cursor:
                    session_row = await cursor.fetchone()
                    if not session_row:
                        await sqlite_manager.close()
                        return "Error: No sessions found in database. Run 'start_research_session' tool first to create a session."
                    session_id = session_row[0]
            else:
                # Validate that the provided session_id exists
                async with sqlite_manager.connection.execute(
                    "SELECT id FROM sessions WHERE id = ?", (session_id,)
                ) as cursor:
                    session_row = await cursor.fetchone()
                    if not session_row:
                        await sqlite_manager.close()
                        return f"Error: Session ID {session_id} not found in database. Use 'get_tool_usage_history' to see available sessions, or omit session_id to use the latest session."
        except Exception as query_error:
            await sqlite_manager.close()
            return f"Error: Cannot query sessions table. Database may be corrupted: {str(query_error)}"

        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        try:
            summary = await workflow_intelligence.generate_session_summary(session_id)
        except Exception as e:
            await sqlite_manager.close()
            error_msg = str(e)
            if "Connection closed" in error_msg:
                return f"Error: Database connection was closed while generating summary for session {session_id}. The session may contain invalid data or the database is corrupted."
            elif "no such table" in error_msg.lower():
                return f"Error: Missing database tables required for session summary. Run 'initialize_project' tool to fix the database schema."
            elif "database is locked" in error_msg.lower():
                return f"Error: Database is locked by another process. Wait a moment and try again."
            return f"Error: Failed to generate session summary for session {session_id}. Workflow intelligence error: {error_msg}"

        if not summary or not isinstance(summary, dict):
            await sqlite_manager.close()
            return f"Error: No summary data returned for session {session_id}. The session may be empty or corrupted."

        # Validate summary structure
        required_keys = ['session_id', 'duration_minutes', 'tools_used', 'summary']
        missing_keys = [key for key in required_keys if key not in summary]
        if missing_keys:
            await sqlite_manager.close()
            return f"Error: Invalid summary data structure for session {session_id} - missing keys: {', '.join(missing_keys)}. Database may be corrupted."

        response = f"# Session Summary\n\n"
        response += f"**Session ID**: {summary['session_id']}\n"
        response += f"**Duration**: {summary['duration_minutes']} minutes\n"
        response += f"**Tools Used**: {len(summary['tools_used'])} unique tools\n"
        response += f"\n## Summary\n{summary['summary']}\n"

        await sqlite_manager.close()
        return response
    except Exception as e:
        if sqlite_manager:
            try:
                await sqlite_manager.close()
            except:
                pass  # Ignore cleanup errors
        if isinstance(e, ContextAwareError):
            raise
        error_msg = str(e)
        if "Connection closed" in error_msg:
            return f"Error: Database connection failed unexpectedly. Check if another process is using the database at {project_path}/.srrd/data/sessions.db"
        return f"Error: Unexpected failure in get_session_summary - {error_msg}"


def register_research_continuity_tools(server):
    """Register research continuity tools with the MCP server"""

    server.register_tool(
        name="get_research_progress",
        description="Get current research progress across all acts and categories",
        parameters={"type": "object", "properties": {}},
        handler=get_research_progress_tool,
    )

    server.register_tool(
        name="get_tool_usage_history",
        description="Get chronological tool usage history for session/project",
        parameters={
            "type": "object",
            "properties": {
                "session_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 20},
            },
        },
        handler=get_tool_usage_history_tool,
    )

    server.register_tool(
        name="get_workflow_recommendations",
        description="Get AI-generated recommendations for next research steps",
        parameters={"type": "object", "properties": {}},
        handler=get_workflow_recommendations_tool,
    )

    server.register_tool(
        name="get_research_milestones",
        description="Get achieved research milestones and upcoming targets",
        parameters={
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 10}},
        },
        handler=get_research_milestones_tool,
    )

    server.register_tool(
        name="start_research_session",
        description="Start a new research session with act-specific goals",
        parameters={
            "type": "object",
            "properties": {
                "research_act": {"type": "string"},
                "research_focus": {"type": "string"},
                "session_goals": {"type": "array", "items": {"type": "string"}},
            },
        },
        handler=start_research_session_tool,
    )

    server.register_tool(
        name="get_session_summary",
        description="Get comprehensive summary of current session progress",
        parameters={
            "type": "object",
            "properties": {"session_id": {"type": "integer"}},
        },
        handler=get_session_summary_tool,
    )
