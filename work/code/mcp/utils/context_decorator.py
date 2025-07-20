"""
Context-Aware Decorator for SRRD MCP Tools
Automatically injects project context into tool functions
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional

# Import with absolute path to avoid import issues
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from context_detector import get_context_detector

logger = logging.getLogger(__name__)

class ContextAwareError(Exception):
    """Exception raised when context-aware operation fails"""
    pass

def context_aware(
    require_context: bool = False,
    fallback_message: Optional[str] = None
) -> Callable:
    """
    Decorator that automatically injects project context into MCP tool functions
    
    Args:
        require_context: If True, tool will fail if no context is available
        fallback_message: Custom message to show when operating without context
        
    Usage:
        @context_aware()
        def my_tool(project_path=None, **kwargs):
            # project_path will be automatically injected if available
            pass
            
        @context_aware(require_context=True)
        def project_only_tool(project_path=None, **kwargs):
            # Will fail with clear error if no project context
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
                # Get context detector
                detector = get_context_detector()
                
                # Check if project_path is already provided
                if kwargs.get('project_path'):
                    # Use provided project_path
                    logger.debug(f"Using provided project_path for {func.__name__}")
                    return await func(*args, **kwargs)
                
                # Try to detect context
                context = detector.detect_context()
                
                if context:
                    # Inject project context
                    kwargs['project_path'] = context['project_path']
                    if context.get('config_path'):
                        kwargs['config_path'] = context['config_path']
                    if context.get('config'):
                        kwargs['config'] = context['config']
                    
                    logger.debug(f"Auto-injected context for {func.__name__}: {context['project_path']}")
                    return await func(*args, **kwargs)
                
                # No context available
                if require_context:
                    error_msg = (
                        f"Tool '{func.__name__}' requires SRRD project context but none was found.\n"
                        f"Please ensure you are either:\n"
                        f"1. Using Claude Desktop with proper MCP configuration, or\n"
                        f"2. Providing the 'project_path' parameter explicitly"
                    )
                    raise ContextAwareError(error_msg)
                
                # Proceed without context (stateless mode)
                if fallback_message:
                    logger.info(fallback_message)
                else:
                    logger.debug(f"Running {func.__name__} in stateless mode (no project context)")
                
                return await func(*args, **kwargs)
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Get context detector
                detector = get_context_detector()
                
                # Check if project_path is already provided
                if kwargs.get('project_path'):
                    # Use provided project_path
                    logger.debug(f"Using provided project_path for {func.__name__}")
                    return func(*args, **kwargs)
                
                # Try to detect context
                context = detector.detect_context()
                
                if context:
                    # Inject project context
                    kwargs['project_path'] = context['project_path']
                    if context.get('config_path'):
                        kwargs['config_path'] = context['config_path']
                    if context.get('config'):
                        kwargs['config'] = context['config']
                    
                    logger.debug(f"Auto-injected context for {func.__name__}: {context['project_path']}")
                    return func(*args, **kwargs)
                
                # No context available
                if require_context:
                    error_msg = (
                        f"Tool '{func.__name__}' requires SRRD project context but none was found.\n"
                        f"Please ensure you are either:\n"
                        f"1. Using Claude Desktop with proper MCP configuration, or\n"
                        f"2. Providing the 'project_path' parameter explicitly"
                    )
                    raise ContextAwareError(error_msg)
                
                # Proceed without context (stateless mode)
                if fallback_message:
                    logger.info(fallback_message)
                else:
                    logger.debug(f"Running {func.__name__} in stateless mode (no project context)")
                
                return func(*args, **kwargs)
            
            return sync_wrapper
        
        # Add metadata to indicate this is a context-aware function
        wrapper = async_wrapper if is_async else sync_wrapper
        wrapper._context_aware = True
        wrapper._require_context = require_context
        wrapper._fallback_message = fallback_message
        
        return wrapper
    
    return decorator

def project_required(fallback_message: Optional[str] = None) -> Callable:
    """
    Convenience decorator for tools that require project context
    Equivalent to @context_aware(require_context=True)
    """
    return context_aware(require_context=True, fallback_message=fallback_message)

def context_optional(fallback_message: Optional[str] = None) -> Callable:
    """
    Convenience decorator for tools that can work with or without context
    Equivalent to @context_aware(require_context=False)
    """
    return context_aware(require_context=False, fallback_message=fallback_message)

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
    has_project_path = 'project_path' in params
    
    # Check if function accepts **kwargs
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    
    return has_project_path or has_kwargs

def is_context_aware(func: Callable) -> bool:
    """Check if a function has been decorated with context_aware"""
    return hasattr(func, '_context_aware') and func._context_aware

def get_context_requirements(func: Callable) -> Dict[str, Any]:
    """Get context requirements for a function"""
    if not is_context_aware(func):
        return {'context_aware': False}
    
    return {
        'context_aware': True,
        'require_context': getattr(func, '_require_context', False),
        'fallback_message': getattr(func, '_fallback_message', None)
    }
