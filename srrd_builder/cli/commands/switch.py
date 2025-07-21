"""
SRRD Switch Command - Switch MCP context to current project
"""

import os
import json
from pathlib import Path
from datetime import datetime

def configure_global_launcher(project_root: Path, srrd_dir: Path):
    """Configure the global MCP launcher for this project"""
    from ...utils.launcher_config import configure_global_launcher as config_launcher
    
    success, error = config_launcher(project_root, srrd_dir)
    return success

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
    
    # Kill any existing MCP server processes before switch
    from ...utils.process_utils import kill_mcp_processes, restart_message
    killed_count = kill_mcp_processes(verbose=True)
    
    if killed_count > 0:
        print(f"   ⚡ Stopped {killed_count} MCP server process(es)")
    
    # Configure global launcher for this project
    if configure_global_launcher(current_dir, srrd_dir):
        print("✅ MCP context switched successfully!")
        print(f"   Project: {current_dir}")
        print(f"   All MCP tools (Claude Desktop, VS Code Chat) now use THIS project's database")
        print("\n🎯 Ready to use:")
        print("   • Claude Desktop - All SRRD tools available")
        print("   • VS Code Chat - All SRRD tools available")
        
        # Show restart instructions
        restart_message(f"Context switched to {current_dir.name}.")
        
        return 0
    else:
        return 1
