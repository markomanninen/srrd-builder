"""
SRRD Switch Command - Switch MCP context to current project
"""

import os
import json
from pathlib import Path
from datetime import datetime

def configure_global_launcher(project_root: Path, srrd_dir: Path):
    """Configure the global MCP launcher for this project"""
    try:
        # REVERT TO WORKING APPROACH: Update the global launcher in srrd_builder package
        switch_file = Path(__file__).resolve()
        global_launcher_dir = switch_file.parent.parent.parent  # cli/commands/switch.py -> srrd_builder/
        global_launcher_script = global_launcher_dir / 'mcp_global_launcher.py'
        
        # Create launcher content with this project's path
        launcher_content = f'''#!/usr/bin/env python3
"""
SRRD MCP Launcher - Context Set by 'srrd switch'
Project path was set when 'srrd switch' was run.
"""

import sys
import os
from pathlib import Path

# Project context set by 'srrd switch' (or 'srrd init')
PROJECT_PATH = '{project_root}'
CONFIG_PATH = '{srrd_dir / "config.json"}'

def main():
    """Main launcher - uses the project set by srrd switch"""
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
        
        return True
        
    except Exception as e:
        print(f"❌ Could not configure global launcher: {e}")
        return False

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
    
    # Configure global launcher for this project
    if configure_global_launcher(current_dir, srrd_dir):
        print("✅ MCP context switched successfully!")
        print(f"   Project: {current_dir}")
        print(f"   All MCP tools (Claude Desktop, VS Code Chat) now use THIS project's database")
        print("\n🎯 Ready to use:")
        print("   • Claude Desktop - All SRRD tools available")
        print("   • VS Code Chat - All SRRD tools available")
        return 0
    else:
        return 1
