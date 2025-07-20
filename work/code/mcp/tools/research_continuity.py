"""
Research Continuity Tools
MCP tools for research lifecycle persistence and workflow guidance
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path to access storage modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from storage.sqlite_manager import SQLiteManager
except ImportError as e:
    print(f"Warning: Could not import SQLiteManager: {e}")
    SQLiteManager = None

try:
    from utils.research_framework import ResearchFrameworkService
except ImportError as e:
    print(f"Warning: Could not import ResearchFrameworkService: {e}")
    ResearchFrameworkService = None

try:
    from utils.workflow_intelligence import WorkflowIntelligence
except ImportError as e:
    print(f"Warning: Could not import WorkflowIntelligence: {e}")
    WorkflowIntelligence = None

# Add context-aware decorator
sys.path.append(str(Path(__file__).parent.parent / 'utils'))
try:
    from context_decorator import context_aware, project_required
except ImportError as e:
    print(f"Warning: Could not import context decorators: {e}")
    # Fallback decorators
    def context_aware():
        def decorator(func):
            return func
        return decorator
    
    def project_required(func):
        return func

# Initialize services if available
research_framework = ResearchFrameworkService() if ResearchFrameworkService else None

@context_aware()
async def get_research_progress_tool(**kwargs) -> str:
    """Get current research progress across all acts and categories"""
    project_path = kwargs.get('project_path')
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        # Initialize workflow intelligence
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database. Please initialize a project first."
        
        project_id = project_row[0]
        
        # Analyze research progress
        analysis = await workflow_intelligence.analyze_research_progress(project_id)
        
        # Format response
        response = f"""# Research Progress Analysis

## Overall Progress
- **Completion**: {analysis['overall_progress']['completion_percentage']:.1f}%
- **Tools Used**: {analysis['overall_progress']['tools_used']}/{analysis['overall_progress']['total_tools']}

## Research Acts Progress
"""
        
        for act_name, progress in analysis['research_acts'].items():
            act_display_name = research_framework.acts[act_name]['name']
            response += f"- **{act_display_name}**: {progress['completion_percentage']:.1f}% ({progress['tools_used']}/{progress['total_tools']} tools)\n"
        
        response += "\n## Research Velocity\n"
        velocity = analysis['research_velocity']
        response += f"- **Tools per day**: {velocity['tools_per_day']}\n"
        response += f"- **Trend**: {velocity['velocity_trend']}\n"
        if velocity['estimated_completion_days']:
            response += f"- **Estimated completion**: {velocity['estimated_completion_days']} days\n"
        
        response += "\n## Workflow Health\n"
        health = analysis['workflow_health']
        response += f"- **Health Score**: {health['health_score']}/100 ({health['health_status']})\n"
        response += f"- **Balance Score**: {health['balance_score']}/100\n"
        
        if health['issues']:
            response += "- **Issues**: " + ", ".join(health['issues']) + "\n"
        
        # Add recommendations
        if analysis['next_steps']:
            response += "\n## Recommended Next Steps\n"
            for i, rec in enumerate(analysis['next_steps'][:3], 1):
                response += f"{i}. **{rec['tool']}** ({rec['priority']} priority): {rec['reason']}\n"
        
        await sqlite_manager.close()
        return response
        
    except Exception as e:
        return f"Error analyzing research progress: {str(e)}"

@context_aware()
async def get_tool_usage_history_tool(**kwargs) -> str:
    """Get chronological tool usage history for session/project"""
    project_path = kwargs.get('project_path')
    session_id = kwargs.get('session_id')  # Optional
    limit = kwargs.get('limit', 20)
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        if session_id:
            # Get history for specific session
            history = await sqlite_manager.get_tool_usage_history(session_id)
        else:
            # Get recent history for project
            async with sqlite_manager.connection.execute(
                """SELECT tu.* FROM tool_usage tu 
                   JOIN sessions s ON tu.session_id = s.id 
                   WHERE s.project_id = (SELECT id FROM projects ORDER BY created_at DESC LIMIT 1)
                   ORDER BY tu.timestamp DESC LIMIT ?""", (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
            
            columns = ['id', 'session_id', 'tool_name', 'research_act', 'research_category', 
                      'arguments', 'result_summary', 'execution_time_ms', 'success', 'error_message', 'timestamp']
            history = [dict(zip(columns, row)) for row in rows]
        
        if not history:
            return "No tool usage history found."
        
        # Format response
        response = f"# Tool Usage History\n\n"
        
        for entry in history:
            timestamp = entry['timestamp']
            tool_name = entry['tool_name']
            research_act = entry['research_act']
            success = "✅" if entry['success'] else "❌"
            
            act_name = research_framework.acts.get(research_act, {}).get('name', research_act)
            
            response += f"## {timestamp}\n"
            response += f"- **Tool**: {tool_name} {success}\n"
            response += f"- **Research Act**: {act_name}\n"
            
            if entry['execution_time_ms']:
                response += f"- **Duration**: {entry['execution_time_ms']}ms\n"
            
            if not entry['success'] and entry['error_message']:
                response += f"- **Error**: {entry['error_message']}\n"
            
            if entry['result_summary']:
                response += f"- **Result**: {entry['result_summary'][:100]}...\n"
            
            response += "\n"
        
        await sqlite_manager.close()
        return response
        
    except Exception as e:
        return f"Error retrieving tool usage history: {str(e)}"

@context_aware()
async def get_workflow_recommendations_tool(**kwargs) -> str:
    """Get AI-generated recommendations for next research steps"""
    project_path = kwargs.get('project_path')
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database and services
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Get project ID and session ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database."
        
        project_id = project_row[0]
        
        # Get or create session
        async with sqlite_manager.connection.execute(
            "SELECT id FROM sessions WHERE project_id = ? ORDER BY started_at DESC LIMIT 1",
            (project_id,)
        ) as cursor:
            session_row = await cursor.fetchone()
            if session_row:
                session_id = session_row[0]
            else:
                session_id = await sqlite_manager.create_session(project_id, 'research', 'claude_user')
        
        # Generate recommendations
        recommendations = await workflow_intelligence.generate_recommendations(project_id, session_id)
        
        if not recommendations:
            return "No specific recommendations available at this time."
        
        # Format response
        response = "# Workflow Recommendations\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            response += f"## {i}. {rec['tool']} ({rec['priority']} priority)\n"
            response += f"- **Research Act**: {rec.get('act_name', rec['research_act'])}\n"
            response += f"- **Category**: {rec.get('category_name', rec['category'])}\n"
            response += f"- **Reasoning**: {rec['enhanced_reasoning']}\n"
            response += f"- **Effort**: {rec['effort_estimate']}\n\n"
        
        await sqlite_manager.close()
        return response
        
    except Exception as e:
        return f"Error generating workflow recommendations: {str(e)}"

@context_aware()
async def get_research_milestones_tool(**kwargs) -> str:
    """Get achieved research milestones and upcoming targets"""
    project_path = kwargs.get('project_path')
    limit = kwargs.get('limit', 10)
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database."
        
        project_id = project_row[0]
        
        # Get milestones from database
        milestones = await sqlite_manager.get_research_milestones(project_id, limit)
        
        # Detect new milestones
        new_milestones = await workflow_intelligence.detect_milestones(project_id)
        
        # Format response
        response = "# Research Milestones\n\n"
        
        if milestones:
            response += "## Achieved Milestones\n"
            for milestone in milestones:
                impact_stars = "⭐" * milestone['impact_score']
                response += f"- **{milestone['milestone_name']}** {impact_stars}\n"
                response += f"  - Type: {milestone['milestone_type']}\n"
                response += f"  - Achieved: {milestone['achieved_at']}\n"
                if milestone['description']:
                    response += f"  - Description: {milestone['description']}\n"
                response += "\n"
        
        if new_milestones:
            response += "## Recently Detected Milestones\n"
            for milestone in new_milestones:
                impact_stars = "⭐" * milestone['impact_score']
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

@context_aware()
async def start_research_session_tool(**kwargs) -> str:
    """Start a new research session with act-specific goals"""
    project_path = kwargs.get('project_path')
    research_act = kwargs.get('research_act')  # Optional
    session_goals = kwargs.get('session_goals', [])  # Optional list of goals
    research_focus = kwargs.get('research_focus')  # Optional description
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        # Get project ID
        async with sqlite_manager.connection.execute(
            "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
        ) as cursor:
            project_row = await cursor.fetchone()
            if not project_row:
                return "No project found in database. Please initialize a project first."
        
        project_id = project_row[0]
        
        # Create new session
        session_id = await sqlite_manager.create_session(
            project_id=project_id,
            session_type='research',
            user_id='claude_user'
        )
        
        # Update session with research context if provided
        if research_act or research_focus or session_goals:
            await sqlite_manager.update_session_research_context(
                session_id=session_id,
                current_research_act=research_act,
                research_focus=research_focus,
                session_goals=session_goals
            )
        
        # Generate initial recommendations
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        recommendations = await workflow_intelligence.generate_recommendations(project_id, session_id)
        
        # Format response
        response = f"# New Research Session Started\n\n"
        response += f"**Session ID**: {session_id}\n"
        
        if research_act:
            act_name = research_framework.acts.get(research_act, {}).get('name', research_act)
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

@context_aware()
async def get_session_summary_tool(**kwargs) -> str:
    """Get comprehensive summary of current session progress"""
    project_path = kwargs.get('project_path')
    session_id = kwargs.get('session_id')  # Optional, uses latest if not provided
    
    if not project_path:
        return "Error: Project context not available. Please ensure you are in an SRRD project or provide project_path parameter."
    
    try:
        # Initialize database
        db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
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
        for act in summary['research_acts_involved']:
            act_name = research_framework.acts.get(act, {}).get('name', act)
            response += f"- {act_name}\n"
        
        response += f"\n## Tools Used\n"
        for tool in summary['tools_used']:
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
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"}
            },
            "required": []
        },
        handler=get_research_progress_tool
    )
    
    server.register_tool(
        name="get_tool_usage_history",
        description="Get chronological tool usage history for session/project",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "session_id": {"type": "integer", "description": "Specific session ID (optional)"},
                "limit": {"type": "integer", "description": "Maximum number of entries to return", "default": 20}
            },
            "required": []
        },
        handler=get_tool_usage_history_tool
    )
    
    server.register_tool(
        name="get_workflow_recommendations",
        description="Get AI-generated recommendations for next research steps",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"}
            },
            "required": []
        },
        handler=get_workflow_recommendations_tool
    )
    
    server.register_tool(
        name="get_research_milestones",
        description="Get achieved research milestones and upcoming targets",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "limit": {"type": "integer", "description": "Maximum number of milestones to return", "default": 10}
            },
            "required": []
        },
        handler=get_research_milestones_tool
    )
    
    server.register_tool(
        name="start_research_session",
        description="Start a new research session with act-specific goals",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "research_act": {"type": "string", "description": "Target research act for this session"},
                "research_focus": {"type": "string", "description": "Description of research focus"},
                "session_goals": {"type": "array", "items": {"type": "string"}, "description": "List of specific goals for this session"}
            },
            "required": []
        },
        handler=start_research_session_tool
    )
    
    server.register_tool(
        name="get_session_summary",
        description="Get comprehensive summary of current session progress",
        parameters={
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Project path (optional - auto-detected when in SRRD project)"},
                "session_id": {"type": "integer", "description": "Session ID (optional - uses latest if not provided)"}
            },
            "required": []
        },
        handler=get_session_summary_tool
    )
