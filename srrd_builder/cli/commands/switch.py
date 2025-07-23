"""
SRRD Switch Command - Switch MCP context to current project
"""

import os
import json
from pathlib import Path
from datetime import datetime

def handle_switch(args):
    """Handle 'srrd switch' command to change MCP context to current project"""
    current_dir = Path.cwd()
    
    # Check if SRRD is initialized in current directory
    srrd_dir = current_dir / '.srrd'
    if not srrd_dir.exists():
        print("❌ SRRD not initialized in current directory")
        print("   Run 'srrd init' to initialize this project")
        return 1
    
    # Check if config exists
    config_file = srrd_dir / 'config.json'
    if not config_file.exists():
        print("❌ SRRD configuration not found")
        print(f"   Expected: {config_file}")
        return 1
    
    print(f"🔄 Switching MCP context to: {current_dir}")
    
    # Clean up any existing Claude/MCP processes before switch
    from ...utils.process_cleanup import cleanup_claude_and_mcp_processes
    cleanup_claude_and_mcp_processes()
    
    # Set current project pointer using current_project.py
    try:
        from ...utils.current_project import set_current_project
        if set_current_project(str(current_dir)):
            print("✅ MCP context switched successfully!")
            print(f"   Project: {current_dir}")
            print(f"   All MCP tools (Claude Desktop, VS Code Chat) now use THIS project's database")
            print("\n🎯 Ready to use:")
            print("   • Claude Desktop - All SRRD tools available")
            print("   • VS Code Chat - All SRRD tools available")
            return 0
        else:
            print(f"   ⚠️  Warning: Could not set current project pointer!")
            print(f"      MCP tools may not work until configured manually")
            return 1
    except Exception as e:
        print(f"   ⚠️  Warning: Could not set current project pointer: {e}")
        print(f"      MCP tools may not work until configured manually")
        return 1
