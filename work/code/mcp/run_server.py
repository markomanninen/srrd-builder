#!/usr/bin/env python3
"""
SRRD-Builder MCP Server Runner
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import MCPServer
from config.config_manager import config

def main():
    """Main entry point for MCP server"""
    print("🚀 Starting SRRD-Builder MCP Server")
    print("=" * 50)
    
    # Use configuration values
    host = config.server.host
    port = config.server.port
    
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
