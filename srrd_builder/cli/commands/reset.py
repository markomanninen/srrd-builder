"""
SRRD Reset Command - Reset project to global home directory context
"""

import os
import json
from pathlib import Path

def reset_global_launcher():
    """Reset the global MCP launcher to use home .srrd globalproject"""
    from ...utils.launcher_config import reset_to_global_project
    
    success, error, project_path = reset_to_global_project()
    return success, str(project_path) if project_path else None

def handle_reset(args):
    """Handle 'srrd reset' command to reset to global home project"""
    print("🔄 Resetting SRRD to global home project...")
    
    result = reset_global_launcher()
    if result[0]:  # Check if successful
        project_path = result[1]
        print("✅ SRRD reset to global home project successfully!")
        print(f"   📁 Global project: {project_path}")
        print(f"   📍 Config: ~/.srrd/globalproject/config.json")
        print("   • Use 'srrd init' in specific directories for local projects") 
        print("   • Use 'srrd switch' to change between projects")
        return 0
    else:
        return 1
