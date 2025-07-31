"""
Research Continuity Tools
Research lifecycle persistence and workflow guidance

Enhanced with structured research act guidance and contextual recommendations:
- get_research_act_guidance: Experience-tailored guidance for specific research acts
- get_contextual_recommendations: AI-powered tool recommendations based on usage patterns
- Pattern analysis and workflow intelligence for optimized research progression
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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


@context_aware(require_context=True)
async def get_research_act_guidance(**kwargs) -> str:
    """
    Get structured guidance for current or specified research act
    
    Builds on existing ResearchFrameworkService and WorkflowIntelligence
    """
    # Get parameters
    target_act = kwargs.get('target_act', None)
    user_experience = kwargs.get('user_experience', 'intermediate')
    detailed_guidance = kwargs.get('detailed_guidance', True)
    
    # Use existing research framework service
    research_framework = _get_research_framework()
    if not research_framework:
        return "Research framework service not available."
    
    project_path = get_current_project()
    # Note: @context_aware(require_context=True) already ensures project_path exists
    
    try:
        # Get current progress using existing functionality
        db_path = SQLiteManager.get_sessions_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        # Determine current act if not specified
        if not target_act:
            # Default to conceptualization for initial guidance
            # TODO: Implement intelligent act detection based on tool usage patterns
            target_act = 'conceptualization'
        
        # Get enhanced guidance for the target act
        act_guidance = await _get_enhanced_act_guidance(
            target_act, user_experience, detailed_guidance, sqlite_manager, research_framework
        )
        
        await sqlite_manager.close()
        return act_guidance
        
    except Exception as e:
        return f"Error generating research act guidance: {str(e)}"


async def _get_enhanced_act_guidance(
    act_name: str, 
    experience: str, 
    detailed: bool, 
    sqlite_manager: SQLiteManager,
    research_framework: ResearchFrameworkService
) -> str:
    """Generate enhanced guidance for specific research act"""
    
    # Extended act definitions building on existing framework
    act_definitions = {
        "conceptualization": {
            "purpose": "Defining research problems, questions, and objectives",
            "key_activities": [
                "clarify_research_goals",
                "assess_foundational_assumptions", 
                "generate_critical_questions",
                "semantic_search"
            ],
            "success_criteria": [
                "Clear, specific research question formulated",
                "Key assumptions identified and examined", 
                "Research scope properly defined",
                "Initial literature review completed"
            ],
            "common_challenges": [
                "Research question too broad or vague",
                "Unexamined assumptions",
                "Insufficient background research",
                "Unclear success metrics"
            ]
        },
        "design_planning": {
            "purpose": "Planning methodology and research approach",
            "key_activities": [
                "suggest_methodology",
                "design_experimental_framework",
                "plan_data_collection",
                "assess_resource_requirements"
            ],
            "success_criteria": [
                "Appropriate methodology selected and justified",
                "Research design is feasible and rigorous",
                "Data collection plan is detailed and realistic",
                "Resource requirements identified"
            ],
            "common_challenges": [
                "Methodology doesn't match research question",
                "Unrealistic scope or timeline",
                "Missing ethical considerations",
                "Inadequate resource planning"
            ]
        },
        "implementation": {
            "purpose": "Executing research plan and collecting data",
            "key_activities": [
                "execute_data_collection",
                "monitor_progress",
                "document_procedures",
                "quality_assurance"
            ],
            "success_criteria": [
                "Data collection executed according to plan",
                "Quality standards maintained",
                "Procedures properly documented",
                "Progress regularly monitored"
            ],
            "common_challenges": [
                "Deviation from planned methodology",
                "Data quality issues",
                "Timeline pressures",
                "Resource constraints"
            ]
        },
        "analysis": {
            "purpose": "Analyzing collected data and identifying patterns",
            "key_activities": [
                "analyze_data_patterns",
                "validate_findings",
                "statistical_analysis",
                "interpret_results"
            ],
            "success_criteria": [
                "Data properly analyzed using appropriate methods",
                "Findings validated and reliable",
                "Results clearly interpreted",
                "Limitations identified"
            ],
            "common_challenges": [
                "Inappropriate analysis methods",
                "Overinterpretation of results",
                "Missing confounding factors",
                "Statistical errors"
            ]
        },
        "synthesis": {
            "purpose": "Synthesizing findings and developing conclusions",
            "key_activities": [
                "synthesize_findings",
                "develop_conclusions",
                "identify_implications",
                "assess_contribution"
            ],
            "success_criteria": [
                "Findings synthesized coherently",
                "Conclusions well-supported by data",
                "Implications clearly identified",
                "Contribution to field assessed"
            ],
            "common_challenges": [
                "Inconsistent synthesis",
                "Unsupported conclusions",
                "Missing broader implications",
                "Overstated contributions"
            ]
        },
        "publication": {
            "purpose": "Communicating research findings and disseminating results",
            "key_activities": [
                "prepare_manuscript",
                "peer_review_process",
                "present_findings",
                "disseminate_results"
            ],
            "success_criteria": [
                "Research clearly communicated",
                "Appropriate venues selected",
                "Feedback incorporated",
                "Results widely disseminated"
            ],
            "common_challenges": [
                "Poor communication of findings",
                "Inappropriate publication venues",
                "Ignoring peer feedback",
                "Limited dissemination"
            ]
        }
    }
    
    act_info = act_definitions.get(act_name, {})
    if not act_info:
        return f"Unknown research act: {act_name}"
    
    # Check current progress in this act using existing database
    act_progress = await _get_act_specific_progress(act_name, sqlite_manager)
    
    # Generate guidance based on progress and experience level
    guidance_sections = []
    
    # Act overview - properly format act name
    formatted_act_name = act_name.replace('_', ' ').title()
    guidance_sections.append(f"# {formatted_act_name} Research Act Guidance")
    guidance_sections.append(f"\n**Purpose**: {act_info['purpose']}")
    
    # Current progress
    if act_progress:
        completion_pct = act_progress.get('completion_percentage', 0)
        guidance_sections.append(f"\n**Current Progress**: {completion_pct:.1f}% complete")
        
        if completion_pct > 0:
            completed_tools = act_progress.get('completed_tools', [])
            guidance_sections.append(f"**Completed Tools**: {', '.join(completed_tools)}")
    
    # Key activities and tools
    guidance_sections.append(f"\n## Key Activities for {formatted_act_name}")
    for i, activity in enumerate(act_info.get('key_activities', []), 1):
        guidance_sections.append(f"{i}. **{activity}**")
        if detailed:
            tool_guidance = _get_tool_specific_guidance(activity, experience)
            if tool_guidance:
                guidance_sections.append(f"   - {tool_guidance}")
    
    # Success criteria
    guidance_sections.append(f"\n## Success Criteria")
    for criterion in act_info.get('success_criteria', []):
        guidance_sections.append(f"- {criterion}")
    
    # Common challenges and how to avoid them
    guidance_sections.append(f"\n## Common Challenges to Avoid")
    for challenge in act_info.get('common_challenges', []):
        guidance_sections.append(f"- {challenge}")
    
    # Next steps based on current progress
    guidance_sections.append(f"\n## Recommended Next Steps")
    next_tools = await _get_smart_next_tools(act_name, act_progress, sqlite_manager)
    for tool in next_tools:
        guidance_sections.append(f"- Use **{tool['name']}**: {tool['rationale']}")
    
    return "\n".join(guidance_sections)


async def _get_act_specific_progress(act_name: str, sqlite_manager: SQLiteManager) -> Dict[str, Any]:
    """Get progress specific to a research act using existing database"""
    # Query existing tool_usage table to determine act progress
    act_tools_map = {
        "conceptualization": ["clarify_research_goals", "assess_foundational_assumptions", "generate_critical_questions", "semantic_search"],
        "design_planning": ["suggest_methodology", "design_experimental_framework", "plan_data_collection"],
        "implementation": ["execute_data_collection", "monitor_progress", "document_procedures"],
        "analysis": ["analyze_data_patterns", "validate_findings", "statistical_analysis"],
        "synthesis": ["synthesize_findings", "develop_conclusions", "identify_implications"],
        "publication": ["prepare_manuscript", "peer_review_process", "present_findings"]
    }
    
    relevant_tools = act_tools_map.get(act_name, [])
    if not relevant_tools:
        return {}
    
    # Query database for tools used in this act
    placeholders = ','.join(['?' for _ in relevant_tools])
    query = f"""
        SELECT tool_name, COUNT(*) as usage_count, MAX(timestamp) as last_used
        FROM tool_usage 
        WHERE tool_name IN ({placeholders})
        GROUP BY tool_name
        ORDER BY last_used DESC
    """
    
    try:
        async with sqlite_manager.connection.execute(query, relevant_tools) as cursor:
            tool_usage = await cursor.fetchall()
        
        completed_tools = [row[0] for row in tool_usage]
        completion_pct = (len(completed_tools) / len(relevant_tools)) * 100
        
        return {
            "completion_percentage": completion_pct,
            "completed_tools": completed_tools,
            "total_tools": len(relevant_tools),
            "last_activity": tool_usage[0][2] if tool_usage else None
        }
    except Exception:
        return {"completion_percentage": 0, "completed_tools": [], "total_tools": len(relevant_tools)}


async def _get_smart_next_tools(act_name: str, progress: Dict, sqlite_manager: SQLiteManager) -> List[Dict[str, str]]:
    """Get smart next tool recommendations based on act progress"""
    completed_tools = progress.get('completed_tools', [])
    
    # Act-specific tool progressions
    tool_progressions = {
        "conceptualization": [
            {"name": "clarify_research_goals", "rationale": "Start by clarifying your research objectives"},
            {"name": "semantic_search", "rationale": "Search existing literature for background"},
            {"name": "assess_foundational_assumptions", "rationale": "Examine underlying assumptions"},
            {"name": "generate_critical_questions", "rationale": "Develop critical thinking questions"}
        ],
        "design_planning": [
            {"name": "suggest_methodology", "rationale": "Get methodology recommendations"},
            {"name": "design_experimental_framework", "rationale": "Design your research approach"},
            {"name": "assess_resource_requirements", "rationale": "Plan required resources"}
        ],
        "implementation": [
            {"name": "execute_data_collection", "rationale": "Begin systematic data collection"},
            {"name": "monitor_progress", "rationale": "Track implementation progress"},
            {"name": "document_procedures", "rationale": "Document your methodology"}
        ],
        "analysis": [
            {"name": "analyze_data_patterns", "rationale": "Identify patterns in your data"},
            {"name": "validate_findings", "rationale": "Ensure findings are robust"},
            {"name": "statistical_analysis", "rationale": "Apply appropriate statistical methods"}
        ],
        "synthesis": [
            {"name": "synthesize_findings", "rationale": "Combine findings coherently"},
            {"name": "develop_conclusions", "rationale": "Draw well-supported conclusions"},
            {"name": "identify_implications", "rationale": "Assess broader implications"}
        ],
        "publication": [
            {"name": "prepare_manuscript", "rationale": "Draft your research manuscript"},
            {"name": "peer_review_process", "rationale": "Engage with peer review"},
            {"name": "present_findings", "rationale": "Present to relevant audiences"}
        ]
    }
    
    progression = tool_progressions.get(act_name, [])
    next_tools = []
    
    for tool in progression:
        if tool["name"] not in completed_tools:
            next_tools.append(tool)
            if len(next_tools) >= 3:  # Limit to top 3 recommendations
                break
    
    return next_tools


def _get_tool_specific_guidance(tool_name: str, experience: str) -> str:
    """Get guidance for using specific tools"""
    tool_guidance = {
        "clarify_research_goals": {
            "beginner": "Take time to really think through your research interests",
            "intermediate": "Focus on making your goals specific and measurable", 
            "expert": "Consider novel angles and paradigm implications"
        },
        "suggest_methodology": {
            "beginner": "Ask for detailed explanations of recommended methodologies",
            "intermediate": "Consider multiple methodologies and their trade-offs",
            "expert": "Evaluate methodology appropriateness for novel approaches"
        },
        "semantic_search": {
            "beginner": "Start with broad search terms, then narrow down",
            "intermediate": "Use varied search strategies and sources",
            "expert": "Focus on gaps and contradictions in literature"
        },
        "assess_foundational_assumptions": {
            "beginner": "Question basic premises of your field",
            "intermediate": "Examine hidden assumptions in methodology",
            "expert": "Challenge paradigmatic assumptions"
        }
    }
    
    return tool_guidance.get(tool_name, {}).get(experience, "")


@context_aware(require_context=True)
async def get_contextual_recommendations(**kwargs) -> str:
    """
    Get enhanced contextual recommendations based on recent tool usage patterns
    
    Provides intelligent recommendations using tool pattern analysis and research context
    """
    # Get parameters
    last_tool_used = kwargs.get('last_tool_used', None)
    recommendation_depth = kwargs.get('recommendation_depth', 3)
    
    project_path = get_current_project()
    # Note: @context_aware(require_context=True) already ensures project_path exists
    
    try:
        # Initialize services
        research_framework = _get_research_framework()
        if not research_framework:
            return "Research framework service not available."
        
        db_path = SQLiteManager.get_sessions_db_path(project_path)
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        # Get project ID (assume first project for simplicity)
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            project_id = project_row[0] if project_row else 1
        
        # Use enhanced WorkflowIntelligence
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Get contextual recommendations
        recommendations = await workflow_intelligence.get_contextual_recommendations(
            project_id=project_id,
            last_tool_used=last_tool_used,
            recommendation_depth=recommendation_depth
        )
        
        await sqlite_manager.close()
        
        # Format response as markdown
        response_sections = []
        
        # Current context summary
        current_context = recommendations.get("current_context", {})
        if current_context:
            response_sections.append("# Current Research Context")
            overall_progress = current_context.get("overall_progress", {})
            if overall_progress:
                completion = overall_progress.get("completion_percentage", 0)
                response_sections.append(f"**Overall Progress**: {completion:.1f}% complete")
        
        # Recent activity pattern
        pattern = recommendations.get("recent_activity_pattern", {})
        if pattern:
            response_sections.append(f"\n# Recent Activity Pattern")
            pattern_type = pattern.get("pattern_type", "unknown")
            confidence = pattern.get("confidence", 0)
            response_sections.append(f"**Pattern**: {pattern_type.title()} (confidence: {confidence:.1f})")
            
            if pattern.get("suggestion"):
                response_sections.append(f"**Suggestion**: {pattern['suggestion']}")
        
        # Prioritized recommendations
        recs = recommendations.get("prioritized_recommendations", [])
        if recs:
            response_sections.append(f"\n# Recommended Next Tools")
            for i, rec in enumerate(recs, 1):
                tool_name = rec.get("tool_name", "unknown")
                priority = rec.get("priority", "medium")
                confidence = rec.get("confidence", 0)
                pattern_context = rec.get("pattern_context", "")
                
                response_sections.append(f"{i}. **{tool_name}** ({priority} priority, {confidence:.1f} confidence)")
                if pattern_context:
                    response_sections.append(f"   - {pattern_context}")
        
        # Rationale
        rationale = recommendations.get("rationale", "")
        if rationale:
            response_sections.append(f"\n# Rationale")
            response_sections.append(rationale)
        
        # Alternative paths
        alternatives = recommendations.get("alternative_paths", [])
        if alternatives:
            response_sections.append(f"\n# Alternative Approaches")
            for alt in alternatives:
                response_sections.append(f"- {alt}")
        
        return "\n".join(response_sections) if response_sections else "No recommendations available at this time."
        
    except Exception as e:
        return f"Error generating contextual recommendations: {str(e)}"


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

    server.register_tool(
        name="get_research_act_guidance",
        description="Get structured guidance for current or specified research act",
        parameters={
            "type": "object",
            "properties": {
                "target_act": {
                    "type": "string",
                    "enum": ["conceptualization", "design_planning", "implementation", "analysis", "synthesis", "publication"],
                    "description": "Specific research act to get guidance for (defaults to current act)"
                },
                "user_experience": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "expert"],
                    "default": "intermediate",
                    "description": "User experience level for tailored guidance"
                },
                "detailed_guidance": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include detailed tool-specific guidance"
                }
            }
        },
        handler=get_research_act_guidance,
    )

    server.register_tool(
        name="get_contextual_recommendations",
        description="Get enhanced contextual recommendations based on recent tool usage patterns",
        parameters={
            "type": "object",
            "properties": {
                "last_tool_used": {
                    "type": "string",
                    "description": "Name of the last tool used (for enhanced context)"
                },
                "recommendation_depth": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of recommendations to generate"
                }
            }
        },
        handler=get_contextual_recommendations,
    )
