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

def configure_global_launcher(project_root: Path, srrd_dir: Path) -> Tuple[bool, Optional[str]]:
    """
    Configure the global MCP launcher for a project.
    
    This is shared code used by:
    - srrd init
    - srrd switch  
    - initialize_project MCP tool
    
    Args:
        project_root: Path to the project root directory
        srrd_dir: Path to the .srrd directory
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        # Find the global launcher script in the srrd_builder package
        launcher_file = Path(__file__).resolve()
        global_launcher_dir = launcher_file.parent.parent  # utils/launcher_config.py -> srrd_builder/
        global_launcher_script = global_launcher_dir / 'mcp_global_launcher.py'
        
        if not global_launcher_script.parent.exists():
            return False, f"Could not find srrd_builder package directory: {global_launcher_dir}"
        
        # Create launcher content with this project's path
        launcher_content = f'''#!/usr/bin/env python3
"""
SRRD MCP Launcher - Auto-configured Project Context
Project path was set by srrd init/switch or initialize_project tool.
"""

import sys
import os
from pathlib import Path

# Project context (auto-configured)
PROJECT_PATH = '{project_root}'
CONFIG_PATH = '{srrd_dir / "config.json"}'

def main():
    """Main launcher - uses the configured project"""
    # Set the project context
    os.environ['SRRD_PROJECT_PATH'] = PROJECT_PATH
    os.environ['SRRD_CONFIG_PATH'] = CONFIG_PATH
    
    # Dynamic MCP server path
    launcher_path = Path(__file__).resolve()
    mcp_server_path = launcher_path.parent.parent / 'work' / 'code' / 'mcp'
    sys.path.insert(0, str(mcp_server_path))
    
    # Import and run the MCP server
    try:
        from mcp_server import ClaudeMCPServer
        import asyncio
        server = ClaudeMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"Server error: {{e}}\\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
        
        with open(global_launcher_script, 'w') as f:
            f.write(launcher_content)
        
        logger.info(f"Global MCP launcher configured for project: {project_root}")
        return True, None
        
    except Exception as e:
        error_msg = f"Could not configure global launcher: {e}"
        logger.warning(error_msg)
        return False, error_msg

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
        
        # Configure launcher for global project
        success, error = configure_global_launcher(global_project_path, srrd_dir)
        
        if success:
            return True, None, global_project_path
        else:
            return False, error, None
        
    except Exception as e:
        error_msg = f"Could not reset to global project: {e}"
        logger.error(error_msg)
        return False, error_msg, None
