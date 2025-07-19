#!/usr/bin/env python3
"""
SRRD MCP Launcher - Context Set by 'srrd init'
Project path was set when 'srrd init' was run.
"""

import sys
import os
from pathlib import Path

# Project context set by 'srrd init' (or last 'srrd switch')
PROJECT_PATH = '/private/var/folders/1t/xzhjq5g1027f9mtd62jc31xh0000gp/T/cli_test_pdf_fail_test_s0edkgs_'
CONFIG_PATH = '/private/var/folders/1t/xzhjq5g1027f9mtd62jc31xh0000gp/T/cli_test_pdf_fail_test_s0edkgs_/.srrd/config.json'

def main():
    """Main launcher - uses the project set by srrd init"""
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
        sys.stderr.write(f"Server error: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
