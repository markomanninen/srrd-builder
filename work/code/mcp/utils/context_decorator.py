"""
Context-Aware Decorator for SRRD MCP Tools
Automatically injects project context and handles database logging
"""

import functools
import logging

# Import with absolute path to avoid import issues
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

sys.path.append(str(Path(__file__).parent))
from current_project import get_current_database_path, get_current_project

logger = logging.getLogger(__name__)


class ContextAwareError(Exception):
    """Exception raised when context-aware operation fails"""

    pass


async def log_tool_usage(
    tool_name: str, parameters: Dict[str, Any], project_path: Optional[str] = None
):
    """Log tool usage to the project database"""
    try:
        if not project_path:
            project_path = get_current_project()

        if not project_path:
            logger.debug(f"No project context for logging {tool_name}")
            return

        db_path = get_current_database_path()

        if not db_path:
            logger.debug(f"No database path for logging {tool_name}")
            return

        # Check if database file exists
        from pathlib import Path

        if not Path(db_path).exists():
            logger.debug(f"Database file does not exist: {db_path}")
            return

        # Import SQLiteManager here to avoid circular imports
        from storage.sqlite_manager import SQLiteManager

        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()

        # Get or create a session for logging
        session_id = (
            1  # Default session for now - TODO: implement proper session management
        )

        # Map tool names to research categories (using MCP tool names, not function names)
        research_category_map = {
            "explain_methodology": "methodology_advisory",
            "compare_approaches": "methodology_advisory",
            "validate_design": "methodology_advisory",
            "ensure_ethics": "methodology_advisory",
            "get_research_progress": "research_continuity",
            "get_tool_usage_history": "research_continuity",
            "get_workflow_recommendations": "research_continuity",
            "get_research_milestones": "research_continuity",
            "start_research_session": "research_continuity",
            "get_session_summary": "research_continuity",
            "initialize_project": "project_management",
            "initiate_paradigm_challenge": "problem_identification",
            "assess_foundational_assumptions": "critical_thinking",
            "generate_critical_questions": "critical_thinking",
            "develop_alternative_framework": "knowledge_building",
            "compare_paradigms": "knowledge_building",
            "validate_novel_theory": "paradigm_validation",
            "evaluate_paradigm_shift_potential": "paradigm_validation",
            "cultivate_innovation": "paradigm_validation",
            "switch_project_context": "project_management",
            "reset_project_context": "project_management",
            # LEGACY: Function names that need mapping to MCP tool names
            "get_research_progress_tool": "research_continuity",
            "get_tool_usage_history_tool": "research_continuity",
            "get_workflow_recommendations_tool": "research_continuity",
            "get_research_milestones_tool": "research_continuity",
            "start_research_session_tool": "research_continuity",
            "get_session_summary_tool": "research_continuity",
        }

        research_category = research_category_map.get(tool_name, "unknown")
        research_act = "planning"  # Default act - TODO: implement proper act detection

        # Map function names to MCP tool names for consistent logging
        function_to_mcp_tool_map = {
            "get_research_progress_tool": "get_research_progress",
            "get_tool_usage_history_tool": "get_tool_usage_history",
            "get_workflow_recommendations_tool": "get_workflow_recommendations",
            "get_research_milestones_tool": "get_research_milestones",
            "start_research_session_tool": "start_research_session",
            "get_session_summary_tool": "get_session_summary",
        }

        # Use MCP tool name for logging consistency
        mcp_tool_name = function_to_mcp_tool_map.get(tool_name, tool_name)

        # Log the tool usage with correct parameters
        await sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name=mcp_tool_name,  # Use MCP tool name, not function name
            research_act=research_act,
            research_category=research_category,
            arguments=parameters,
            result_summary=None,  # TODO: capture result summary
            execution_time_ms=None,  # TODO: measure execution time
            success=True,  # TODO: capture actual success status
            error_message=None,
        )

        await sqlite_manager.close()

        logger.debug(f"Successfully logged usage for {tool_name}")

    except Exception as e:
        logger.error(
            f"CONTEXT DECORATOR LOGGING FAILED for {tool_name}: {e}"
        )  # Changed to ERROR level
        # Don't let logging failures break the tool


def context_aware_tool(
    name: str,
    description: str,
    parameters: dict,
    require_context: bool = False,
    fallback_message: Optional[str] = None,
    disable_logging: bool = False,
    allow_explicit_project_path: bool = False,
) -> Callable:
    """
    Decorator that automatically injects project context into MCP tool functions
    and logs tool usage to the project database

    Args:
        require_context: If True, tool will fail if no context is available
        fallback_message: Custom message to show when operating without context
        disable_logging: If False, log tool usage to project database
        allow_explicit_project_path: If True, allows explicit project_path to be passed through to the tool (default False)

    Usage:
        @context_aware()
        def my_tool(**kwargs):
            # Current project context is automatically available
            # project_path parameter is no longer needed
            pass

        @context_aware(require_context=True)
        def project_only_tool(**kwargs):
            # Will fail with clear error if no project context
            pass

        @context_aware(allow_explicit_project_path=True)
        def tool_with_explicit_path(**kwargs):
            # project_path will be passed through if provided
            pass
    """

    def decorator(func: Callable) -> Callable:
        import asyncio
        import inspect

        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Attach metadata to the wrapper function
                async_wrapper.tool_name = name
                async_wrapper.description = description
                async_wrapper.parameters = parameters
                current_project = get_current_project()
                provided_project_path = kwargs.get("project_path")
                if not allow_explicit_project_path:
                    # Remove project_path from kwargs if present (deprecated)
                    provided_project_path = kwargs.pop("project_path", None)
                    if provided_project_path:
                        logger.debug(
                            f"project_path parameter is deprecated, using current project: {current_project}"
                        )
                # If allow_explicit_project_path is True, do not pop, just pass through
                # Check if context is required
                if require_context and not (
                    current_project or kwargs.get("project_path")
                ):
                    error_msg = (
                        f"Tool '{func.__name__}' requires SRRD project context but none is active.\n"
                        f"Please run 'srrd init' or 'srrd switch <project>' to set a current project."
                    )
                    raise ContextAwareError(error_msg)

                # Log tool usage if enabled and we have a project
                if not disable_logging and (
                    current_project or kwargs.get("project_path")
                ):
                    await log_tool_usage(
                        func.__name__,
                        kwargs,
                        kwargs.get("project_path") or current_project,
                    )

                # Call the function
                if (
                    not (current_project or kwargs.get("project_path"))
                    and fallback_message
                ):
                    logger.info(fallback_message)

                return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                current_project = get_current_project()
                provided_project_path = None
                if not allow_explicit_project_path:
                    provided_project_path = kwargs.pop("project_path", None)
                    if provided_project_path:
                        logger.debug(
                            f"project_path parameter is deprecated, using current project: {current_project}"
                        )
                # If allow_explicit_project_path is True, do not pop, just pass through

                if require_context and not (
                    current_project or kwargs.get("project_path")
                ):
                    error_msg = (
                        f"Tool '{func.__name__}' requires SRRD project context but none is active.\n"
                        f"Please run 'srrd init' or 'srrd switch <project>' to set a current project."
                    )
                    raise ContextAwareError(error_msg)

                if not disable_logging and (
                    current_project or kwargs.get("project_path")
                ):
                    try:
                        asyncio.create_task(
                            log_tool_usage(
                                func.__name__,
                                kwargs,
                                kwargs.get("project_path") or current_project,
                            )
                        )
                    except RuntimeError:
                        pass

                if (
                    not (current_project or kwargs.get("project_path"))
                    and fallback_message
                ):
                    logger.info(fallback_message)

                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


def project_required(
    fallback_message: Optional[str] = None, disable_logging: bool = False
) -> Callable:
    """
    Convenience decorator for tools that require project context
    Equivalent to @context_aware(require_context=True)
    """
    return context_aware(
        require_context=True,
        fallback_message=fallback_message,
        disable_logging=disable_logging,
    )


def context_optional(
    fallback_message: Optional[str] = None, disable_logging: bool = False
) -> Callable:
    """
    Convenience decorator for tools that can work with or without context
    Equivalent to @context_aware(require_context=False)
    """
    return context_aware(
        require_context=False,
        fallback_message=fallback_message,
        disable_logging=disable_logging,
    )


# Convenience functions for accessing current project (no parameters needed)
def get_current_project_path() -> Optional[str]:
    """Get the current project path - convenience function for tools"""
    return get_current_project()


def get_current_project_config() -> Optional[Dict[str, Any]]:
    """Get the current project config - convenience function for tools"""
    from current_project import get_current_config

    return get_current_config()


def require_current_project() -> str:
    """Get current project path or raise error if none - convenience function for tools"""
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError(
            "No active SRRD project. Please run 'srrd init' or 'srrd switch <project>' to set a current project."
        )
    return project_path


def get_enhanced_error_message(tool_name: str, original_error: Exception) -> str:
    """
    Generate enhanced error messages that guide users to provide context
    """
    if "project_path" in str(original_error).lower():
        return (
            f"Tool '{tool_name}' failed due to missing project context.\n"
            f"Original error: {original_error}\n\n"
            f"To fix this, either:\n"
            f"1. Configure Claude Desktop with 'srrd configure --claude'\n"
            f"2. Provide the 'project_path' parameter when calling this tool\n"
            f"3. Initialize an SRRD project with 'srrd init' if you haven't already"
        )

    return str(original_error)


def validate_context_injection(func: Callable) -> bool:
    """
    Validate that a function can receive context injection
    Checks if the function accepts project_path parameter
    """
    import inspect

    sig = inspect.signature(func)
    params = sig.parameters

    # Check if function accepts project_path parameter
    has_project_path = "project_path" in params

    # Check if function accepts **kwargs
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())

    return has_project_path or has_kwargs


# Alias for backward compatibility - many modules import this
def context_aware(
    name: str = None,
    description: str = None,
    parameters: dict = None,
    require_context: bool = False,
    fallback_message: Optional[str] = None,
    disable_logging: bool = False,
    allow_explicit_project_path: bool = False,
) -> Callable:
    """
    Alias for context_aware_tool for backward compatibility
    """
    return context_aware_tool(
        name=name or "",
        description=description or "",
        parameters=parameters or {},
        require_context=require_context,
        fallback_message=fallback_message,
        disable_logging=disable_logging,
        allow_explicit_project_path=allow_explicit_project_path,
    )
