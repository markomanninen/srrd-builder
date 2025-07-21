"""
SRRD Reset Command - Reset project to global home directory context
"""

import os
import json
from pathlib import Path

def reset_global_launcher():
    """Reset the global MCP launcher to use home .srrd globalproject"""
    try:
        # Use the working path that actually works
        reset_file = Path(__file__).resolve()
        global_launcher_dir = reset_file.parent.parent.parent  # cli/commands/reset.py -> srrd_builder/
        global_launcher_script = global_launcher_dir / 'mcp_global_launcher.py'
        
        # Get home directory and ensure global project directory exists
        home = Path.home()
        global_project_path = home / '.srrd' / 'globalproject'
        global_project_path.mkdir(parents=True, exist_ok=True)
        
        # Create global project launcher content
        launcher_content = f'''#!/usr/bin/env python3
"""
SRRD MCP Launcher - Global Project Context
Using global project in ~/.srrd/globalproject
"""

import sys
import os
from pathlib import Path

# Global project context
PROJECT_PATH = "{global_project_path}"
CONFIG_PATH = "{global_project_path / 'config.json'}"

def get_project_path():
    """Get the current project path"""
    return Path(PROJECT_PATH)

def main():
    """Main launcher for global project context"""
    # Add the MCP server directory to Python path
    current_dir = Path(__file__).parent
    mcp_server_dir = current_dir / 'work' / 'code' / 'mcp'
    
    if not mcp_server_dir.exists():
        print("❌ MCP server directory not found")
        sys.exit(1)
    
    sys.path.insert(0, str(mcp_server_dir))
    
    # Start the MCP server
    from server import MCPServer
    import asyncio
    
    server = MCPServer(project_path=PROJECT_PATH)
    asyncio.run(server.run())

if __name__ == '__main__':
    main()
'''
        
        with open(global_launcher_script, 'w') as f:
            f.write(launcher_content)
        
        # Create global project config
        config_data = {
            "project_path": str(global_project_path),
            "project_name": "Global Home Project",
            "description": "Global SRRD project in home directory",
            "domain": "general",
            "is_global": True
        }
        
        config_file = global_project_path / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return True, str(global_project_path)
        
    except Exception as e:
        print(f"❌ Could not reset global launcher: {e}")
        return False, None

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
