"""
SRRD Reset Command - Reset project to global home directory context
"""

import json
import os
from pathlib import Path


def reset_global_launcher():
    """Reset the global MCP launcher to use home Projects default project"""
    from ...utils.launcher_config import reset_to_global_project

    success, error, project_path = reset_to_global_project()
    return success, error, project_path


def handle_reset(args):
    """Handle 'srrd reset' command to reset to global home project"""
    print("🔄 Resetting SRRD to global home project...")

    # Clean up any existing Claude/MCP processes before reset
    from ...utils.process_cleanup import cleanup_claude_and_mcp_processes

    cleanup_claude_and_mcp_processes()

    success, error, project_path = reset_global_launcher()
    if success:
        print("✅ SRRD reset to global home project successfully!")
        print(f"   📁 Global project: {project_path}")
        print(f"   📍 Config: ~/Projects/default/config.json")
        print("   • Use 'srrd init' in specific directories for local projects")
        print("   • Use 'srrd switch' to change between projects")
        return 0
    else:
        print(f"❌ Failed to reset SRRD: {error}")
        return 1
