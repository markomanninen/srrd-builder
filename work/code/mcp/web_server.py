#!/usr/bin/env python3
"""
SRRD-Builder We    print("🌐 Starting SRRD-Builder Web GUI Server")
    print("=" * 50)
    print(f"🎯 Project: {project_path}")
    print(f"🌐 Web Interface: http://{host}:{port}/frontend/")
    print(f"📡 WebSocket API: ws://{host}:{port}")
    print("")
    print("💡 This server provides:")
    print("   - Web-based tool testing interface") 
    print("   - Demo and development environment")
    print("   - External WebSocket API access")
    print("")
    print("📝 NOTE: This is NOT needed for Claude Desktop integration!")
    print("   Claude Desktop uses the stdio MCP server directly.")
    print("="*50)UI Server
===========================

WebSocket server for the web-based testing interface and demos.
This server is NOT needed for Claude Desktop integration.

Usage:
  python3 web_server.py --port 8080
  
Then open: http://localhost:8080/frontend/
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

def main():
    """Main entry point for Web GUI server"""
    # Parse command line arguments to get the correct project path
    parser = argparse.ArgumentParser(description='SRRD-Builder Web GUI Server')
    parser.add_argument('--project-path', type=str, default=None, 
                       help='Path to the SRRD project directory')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Port to run the web server on')
    args = parser.parse_args()
    
    # Determine the project path
    if args.project_path:
        project_path = Path(args.project_path).resolve()
    else:
        # Try to detect from environment variable first
        env_path = os.environ.get('SRRD_PROJECT_PATH')
        if env_path:
            project_path = Path(env_path).resolve()
        else:
            # Fall back to current working directory
            project_path = Path.cwd().resolve()
    
    print("� Starting SRRD-Builder MCP Server")
    print("=" * 50)
    print(f"� Project: {project_path}")
    
    # Validate that this is an SRRD project
    srrd_dir = project_path / ".srrd"
    if not srrd_dir.exists():
        print(f"❌ Error: {project_path} is not a valid SRRD project")
        print(f"   Missing .srrd directory")
        sys.exit(1)
    
    # Set environment variables for context-aware tools
    os.environ['SRRD_PROJECT_PATH'] = str(project_path)
    config_path = srrd_dir / "config.json"
    if config_path.exists():
        os.environ['SRRD_CONFIG_PATH'] = str(config_path)
    
    print(f"✅ Environment SRRD_PROJECT_PATH: {os.environ.get('SRRD_PROJECT_PATH')}")
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from server import MCPServer
    from config.config_manager import config
    
    # Use configuration values
    host = config.server.host
    port = args.port or config.server.port
    
    print(f"🌐 Server will run on {host}:{port}")
    print(f"📡 WebSocket endpoint: ws://{host}:{port}")
    print("🛠️  Available tools:")
    print("   - clarify_research_goals")
    print("   - suggest_methodology")
    print("   - simulate_peer_review")
    print("   - check_quality_gates")
    print("\n✨ Special features:")
    print("   - Novel theory development support")
    print("   - Socratic questioning engine")
    print("   - Equal treatment validation")
    print("   - Paradigm innovation tools")
    print("\n🔧 Use test_client.py to test functionality")
    print("=" * 50)
    
    try:
        # Create and start server  
        server = MCPServer(port=port)
        print(f"✅ MCP Server initialized")
        print(f"🎯 Listening for connections...")
        
        # Run server
        asyncio.run(server.start_server())
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
