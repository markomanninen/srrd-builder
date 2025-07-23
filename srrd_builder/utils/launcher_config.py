"""
Shared launcher configuration utilities
Used by both CLI commands (init, switch, reset) and MCP tools (initialize_project)
"""
import sys
import json
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger("srrd_builder.launcher_config")

def reset_to_global_project() -> Tuple[bool, Optional[str], Optional[Path]]:
    """
    Reset the global MCP launcher to use home .srrd globalproject.
    
    Used by 'srrd reset' command.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str], project_path: Optional[Path])
    """
    try:
        # Get home directory and ensure global project directory exists
        home = Path.home()
        global_project_path = home / '.srrd' / 'globalproject'
        global_project_path.mkdir(parents=True, exist_ok=True)

        # Create global project .srrd directory
        srrd_dir = global_project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)

        # Create global project config
        config_data = {
            "project_name": "Global Home Project",
            "description": "Global SRRD project in home directory",
            "domain": "general",
            "is_global": True,
            "version": "0.1.0",
            "created_at": "auto-generated"
        }

        config_file = global_project_path / '.srrd' / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Set the current project pointer to the global project
        try:
            # Add the work/code/mcp directory to Python path so we can import current_project
            import os
            current_dir = Path(__file__).parent.parent.parent  # Go up to srrd-builder root
            mcp_path = current_dir / 'work' / 'code' / 'mcp'
            if str(mcp_path) not in sys.path:
                sys.path.insert(0, str(mcp_path))
            
            from utils.current_project import set_current_project
            set_current_project(str(global_project_path))
        except Exception as e:
            logger.warning(f"Failed to set current project pointer: {e}")
            # Don't fail the entire operation, just log the warning
            # The reset still succeeded in creating the global project

        return True, None, global_project_path

    except Exception as e:
        error_msg = f"Could not reset to global project: {e}"
        logger.error(error_msg)
        return False, error_msg, None
