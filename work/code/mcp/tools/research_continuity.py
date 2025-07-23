"""
Research Continuity Tools
Research lifecycle persistence and workflow guidance
"""

import json
import sys
from pathlib import Path

# Fix import path issues by adding utils directory to sys.path
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

# Add parent directory to path to access storage modules
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from storage.sqlite_manager import SQLiteManager
from utils.research_framework import ResearchFrameworkService
from utils.workflow_intelligence import WorkflowIntelligence

# Context-aware decorator imports
sys.path.insert(0, str(current_dir / "utils"))
from context_decorator import context_aware
from current_project import get_current_project


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
        return "Error: Project context not available. Please ensure you are in an SRRD project."

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

        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get project ID and stats from database
        async with sqlite_manager.connection.execute(
            "SELECT id, name, created_at FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return f"""# Research Progress Analysis

## Project Information
- **Name**: {project_name}
- **Directory**: {project_path}
- **Domain**: {project_domain}
- **Description**: {project_description}
- **Status**: Not initialized - No project found in database

Please initialize the project by running research tools first."""

        project_id = project_row[0]
        db_project_name = project_row[1]
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
            # Safely get act display name
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

        # Add recommendations
        if analysis["next_steps"]:
            response += "\n## Recommended Next Steps\n"
            for i, rec in enumerate(analysis["next_steps"][:3], 1):
                response += f"{i}. **{rec['tool']}** ({rec['priority']} priority): {rec['reason']}\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error analyzing research progress: {str(e)}"


@context_aware(require_context=True)
async def get_tool_usage_history_tool(**kwargs) -> str:
    """Get chronological tool usage history for session/project"""
    project_path = get_current_project()
    session_id = kwargs.get("session_id")  # Optional
    limit = kwargs.get("limit", 20)

    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project."

    try:
        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Initialize research framework
        research_framework = _get_research_framework()

        if session_id:
            # Get history for specific session
            history = await sqlite_manager.get_tool_usage_history(session_id)
        else:
            # Get recent history for project
            async with sqlite_manager.connection.execute(
                """SELECT tu.* FROM tool_usage tu 
                   JOIN sessions s ON tu.session_id = s.id 
                   WHERE s.project_id = (SELECT id FROM projects ORDER BY created_at DESC LIMIT 1)
                   ORDER BY tu.timestamp DESC LIMIT ?""",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()

            columns = [
                "id",
                "session_id",
                "tool_name",
                "research_act",
                "research_category",
                "arguments",
                "result_summary",
                "execution_time_ms",
                "success",
                "error_message",
                "timestamp",
            ]
            history = [dict(zip(columns, row)) for row in rows]

        if not history:
            return "No tool usage history found."

        # Format response
        response = f"# Tool Usage History\n\n"

        for entry in history:
            timestamp = entry["timestamp"]
            tool_name = entry["tool_name"]
            research_act = entry["research_act"]
            success = "PASS" if entry["success"] else "FAIL"

            # Safely get act name
            if (
                research_framework
                and hasattr(research_framework, "acts")
                and research_act in research_framework.acts
            ):
                act_name = research_framework.acts[research_act]["name"]
            else:
                act_name = (
                    research_act.replace("_", " ").title()
                    if research_act
                    else "Unknown"
                )

            response += f"## {timestamp}\n"
            response += f"- **Tool**: {tool_name} {success}\n"
            response += f"- **Research Act**: {act_name}\n"

            if entry["execution_time_ms"]:
                response += f"- **Duration**: {entry['execution_time_ms']}ms\n"

            if not entry["success"] and entry["error_message"]:
                response += f"- **Error**: {entry['error_message']}\n"

            if entry["result_summary"]:
                response += f"- **Result**: {entry['result_summary'][:100]}...\n"

            response += "\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error retrieving tool usage history: {str(e)}"


@context_aware(require_context=True)
async def get_workflow_recommendations_tool(**kwargs) -> str:
    """Get AI-generated recommendations for next research steps"""
    project_path = get_current_project()

    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project."

    try:
        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database."

        project_id = project_row[0]

        # Initialize workflow intelligence and research framework
        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        # Get or create session
        async with sqlite_manager.connection.execute(
            "SELECT id FROM sessions WHERE project_id = ? ORDER BY started_at DESC LIMIT 1",
            (project_id,),
        ) as cursor:
            session_row = await cursor.fetchone()
            if session_row:
                session_id = session_row[0]
            else:
                session_id = await sqlite_manager.create_session(
                    project_id, "research", "claude_user"
                )

        # Generate recommendations
        recommendations = await workflow_intelligence.generate_recommendations(
            project_id, session_id
        )

        if not recommendations:
            return "No specific recommendations available at this time."

        # Format response
        response = "# Workflow Recommendations\n\n"
        response += "*These are suggestions based on your current research progress. Please choose what interests you most or aligns with your current goals.*\n\n"

        for i, rec in enumerate(recommendations, 1):
            response += f"## {i}. {rec['tool']} ({rec['priority']} priority)\n"
            response += (
                f"- **Research Act**: {rec.get('act_name', rec['research_act'])}\n"
            )
            response += f"- **Category**: {rec.get('category_name', rec['category'])}\n"
            response += f"- **Reasoning**: {rec['enhanced_reasoning']}\n"
            response += f"- **Effort**: {rec['effort_estimate']}\n\n"

        response += "\n**Next Steps**: Please let me know which of these recommendations interests you, or if you'd prefer to work on something else entirely. I'm here to support your research direction.\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error generating workflow recommendations: {str(e)}"


@context_aware(require_context=True)
async def get_research_milestones_tool(**kwargs) -> str:
    """Get achieved research milestones and upcoming targets"""
    project_path = get_current_project()
    limit = kwargs.get("limit", 10)

    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project."

    try:
        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database."

        project_id = project_row[0]

        # Initialize workflow intelligence and research framework
        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        # Get milestones from database
        milestones = await sqlite_manager.get_research_milestones(project_id, limit)

        # Detect new milestones
        new_milestones = await workflow_intelligence.detect_milestones(project_id)

        # Format response
        response = "# Research Milestones\n\n"

        if milestones:
            response += "## Achieved Milestones\n"
            for milestone in milestones:
                impact_stars = "*" * milestone["impact_score"]
                response += f"- **{milestone['milestone_name']}** {impact_stars}\n"
                response += f"  - Type: {milestone['milestone_type']}\n"
                response += f"  - Achieved: {milestone['achieved_at']}\n"
                if milestone["description"]:
                    response += f"  - Description: {milestone['description']}\n"
                response += "\n"

        if new_milestones:
            response += "## Recently Detected Milestones\n"
            for milestone in new_milestones:
                impact_stars = "*" * milestone["impact_score"]
                response += f"- **{milestone['name']}** {impact_stars}\n"
                response += f"  - Type: {milestone['type']}\n"
                response += f"  - Description: {milestone['description']}\n"
                response += "\n"

        if not milestones and not new_milestones:
            response += "No milestones achieved yet. Keep using research tools to reach your first milestone!\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error retrieving research milestones: {str(e)}"


@context_aware(require_context=True)
async def start_research_session_tool(**kwargs) -> str:
    """Start a new research session with act-specific goals"""
    project_path = get_current_project()
    research_act = kwargs.get("research_act")  # Optional
    session_goals = kwargs.get("session_goals", [])  # Optional list of goals
    research_focus = kwargs.get("research_focus")  # Optional description

    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project."

    try:
        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return (
                    "No project found in database. Please initialize a project first."
                )

        project_id = project_row[0]

        # Create new session
        session_id = await sqlite_manager.create_session(
            project_id=project_id, session_type="research", user_id="claude_user"
        )

        # Update session with research context if provided
        if research_act or research_focus or session_goals:
            await sqlite_manager.update_session_research_context(
                session_id=session_id,
                current_research_act=research_act,
                research_focus=research_focus,
                session_goals=session_goals,
            )

        # Generate initial recommendations if WorkflowIntelligence is available
        recommendations = []
        if WorkflowIntelligence:
            try:
                research_framework = _get_research_framework()
                workflow_intelligence = WorkflowIntelligence(
                    sqlite_manager, research_framework
                )
                recommendations = await workflow_intelligence.generate_recommendations(
                    project_id, session_id
                )
            except Exception as e:
                # Continue even if recommendations fail
                pass

        # Format response
        response = f"# New Research Session Started\n\n"
        response += f"**Session ID**: {session_id}\n"

        if research_act:
            # Safely get act name
            research_framework = _get_research_framework()
            if (
                research_framework
                and hasattr(research_framework, "acts")
                and research_act in research_framework.acts
            ):
                act_name = research_framework.acts[research_act]["name"]
            else:
                act_name = research_act.replace("_", " ").title()
            response += f"**Research Act**: {act_name}\n"

        if research_focus:
            response += f"**Focus**: {research_focus}\n"

        if session_goals:
            response += f"**Goals**: {', '.join(session_goals)}\n"

        if recommendations:
            response += "\n## Recommended Starting Tools\n"
            for i, rec in enumerate(recommendations[:3], 1):
                response += f"{i}. **{rec['tool']}**: {rec['reason']}\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error starting research session: {str(e)}"


@context_aware(require_context=True)
async def get_session_summary_tool(**kwargs) -> str:
    """Get comprehensive summary of current session progress"""
    project_path = get_current_project()
    session_id = kwargs.get("session_id")  # Optional, uses latest if not provided

    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project."

    try:
        # Initialize database
        db_path = str(Path(project_path) / ".srrd" / "sessions.db")
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get session ID if not provided
        if not session_id:
            # Find session with most recent tool usage, fallback to latest session
            async with sqlite_manager.connection.execute(
                """SELECT s.id FROM sessions s 
                   JOIN projects p ON s.project_id = p.id 
                   LEFT JOIN tool_usage tu ON s.id = tu.session_id
                   GROUP BY s.id
                   ORDER BY MAX(tu.timestamp) DESC, s.started_at DESC 
                   LIMIT 1"""
            ) as cursor:
                session_row = await cursor.fetchone()
                if not session_row:
                    return "No active sessions found."
                session_id = session_row[0]

        # Initialize workflow intelligence and research framework
        research_framework = _get_research_framework()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)

        # Generate session summary
        summary = await workflow_intelligence.generate_session_summary(session_id)

        # Format response
        response = f"# Session Summary\n\n"
        response += f"**Session ID**: {summary['session_id']}\n"
        response += f"**Duration**: {summary['duration_minutes']} minutes\n"
        response += f"**Tools Used**: {len(summary['tools_used'])} unique tools\n"
        response += f"**Total Calls**: {summary['total_tool_calls']}\n"
        response += f"**Success Rate**: {summary['successful_calls']}/{summary['total_tool_calls']}\n"
        response += f"**Avg Execution Time**: {summary['avg_execution_time_ms']}ms\n"

        response += f"\n## Research Acts Involved\n"
        for act in summary["research_acts_involved"]:
            # Safely get act name
            if (
                research_framework
                and hasattr(research_framework, "acts")
                and act in research_framework.acts
            ):
                act_name = research_framework.acts[act]["name"]
            else:
                act_name = act.replace("_", " ").title() if act else "Unknown"
            response += f"- {act_name}\n"

        response += f"\n## Tools Used\n"
        for tool in summary["tools_used"]:
            response += f"- {tool}\n"

        response += f"\n## Summary\n{summary['summary']}\n"

        await sqlite_manager.close()
        return response

    except Exception as e:
        return f"Error generating session summary: {str(e)}"


def register_research_continuity_tools(server):
    """Register research continuity tools with the MCP server"""

    server.register_tool(
        name="get_research_progress",
        description="Get current research progress across all acts and categories",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                }
            },
            "required": [],
        },
        handler=get_research_progress_tool,
    )

    server.register_tool(
        name="get_tool_usage_history",
        description="Get chronological tool usage history for session/project",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                },
                "session_id": {
                    "type": "integer",
                    "description": "Specific session ID (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entries to return",
                    "default": 20,
                },
            },
            "required": [],
        },
        handler=get_tool_usage_history_tool,
    )

    server.register_tool(
        name="get_workflow_recommendations",
        description="Get AI-generated recommendations for next research steps",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                }
            },
            "required": [],
        },
        handler=get_workflow_recommendations_tool,
    )

    server.register_tool(
        name="get_research_milestones",
        description="Get achieved research milestones and upcoming targets",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of milestones to return",
                    "default": 10,
                },
            },
            "required": [],
        },
        handler=get_research_milestones_tool,
    )

    server.register_tool(
        name="start_research_session",
        description="Start a new research session with act-specific goals",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                },
                "research_act": {
                    "type": "string",
                    "description": "Target research act for this session",
                },
                "research_focus": {
                    "type": "string",
                    "description": "Description of research focus",
                },
                "session_goals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific goals for this session",
                },
            },
            "required": [],
        },
        handler=start_research_session_tool,
    )

    server.register_tool(
        name="get_session_summary",
        description="Get comprehensive summary of current session progress",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Project path (optional - auto-detected when in SRRD project)",
                },
                "session_id": {
                    "type": "integer",
                    "description": "Session ID (optional - uses latest if not provided)",
                },
            },
            "required": [],
        },
        handler=get_session_summary_tool,
    )
