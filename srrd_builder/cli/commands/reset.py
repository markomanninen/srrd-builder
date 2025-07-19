"""
SRRD Reset Command - Reset/Clear global MCP launcher
"""

import os
from pathlib import Path

def reset_global_launcher():
    """Reset the global MCP launcher to a default state"""
    try:
        # Use the working path that actually works
        reset_file = Path(__file__).resolve()
        global_launcher_dir = reset_file.parent.parent.parent  # cli/commands/reset.py -> srrd_builder/
        global_launcher_script = global_launcher_dir / 'mcp_global_launcher.py'
        
        # Create default launcher content with no project
        launcher_content = '''#!/usr/bin/env python3
"""
SRRD MCP Launcher - NO PROJECT CONFIGURED
Run 'srrd init' or 'srrd switch' to configure a project.
"""

import sys
import os
from pathlib import Path

# No project context configured
PROJECT_PATH = None
CONFIG_PATH = None

def main():
    """Main launcher - no project configured"""
    print("❌ SRRD MCP Server: No project configured")
    print("   Run one of these commands first:")
    print("   • cd /your/project && srrd init")
    print("   • cd /existing/project && srrd switch")
    print("   • srrd reset  # to clear this configuration")
    sys.exit(1)

if __name__ == '__main__':
    main()
'''
        
        with open(global_launcher_script, 'w') as f:
            f.write(launcher_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Could not reset global launcher: {e}")
        return False

def handle_reset(args):
    """Handle 'srrd reset' command to clear global MCP launcher"""
    print("🔄 Resetting global MCP launcher...")
    
    if reset_global_launcher():
        print("✅ Global MCP launcher reset successfully!")
        print("   All MCP tools are now disabled until you:")
        print("   1. cd /your/project && srrd init      # Initialize new project")
        print("   2. cd /existing/project && srrd switch # Switch to existing project")
        return 0
    else:
        return 1
