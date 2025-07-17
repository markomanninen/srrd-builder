#!/usr/bin/env python3
"""
SRRD-Builder MCP Server Global Launcher
Provides global access to the MCP server functionality
"""

import sys
import os
import asyncio
import argparse
import threading
import webbrowser
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

def find_frontend_dir(mcp_dir):
    """Find the frontend directory"""
    frontend_dir = mcp_dir / "frontend"
    if frontend_dir.exists():
        return frontend_dir
    return None

def start_frontend_server(frontend_dir, port):
    """Start the HTTP frontend server in a separate thread"""
    class FrontendHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(frontend_dir), **kwargs)
        
        def log_message(self, format, *args):
            # Suppress default logging to reduce noise
            pass
    
    try:
        with socketserver.TCPServer(("", port), FrontendHandler) as httpd:
            print(f"🌐 Frontend server running on http://localhost:{port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def find_mcp_server():
    """Find the MCP server module in the installed package"""
    try:
        # Try to import from installed package
        import srrd_builder
        package_path = Path(srrd_builder.__file__).parent
        mcp_server_path = package_path / "work" / "code" / "mcp" / "server.py"
        
        if mcp_server_path.exists():
            return mcp_server_path
        
        # Alternative path structure
        mcp_server_path = package_path / "mcp" / "server.py"
        if mcp_server_path.exists():
            return mcp_server_path
            
    except ImportError:
        pass
    
    # Fallback: look in current directory structure
    current_dir = Path(__file__).parent
    possible_paths = [
        current_dir / ".." / "work" / "code" / "mcp" / "server.py",
        current_dir / "mcp" / "server.py",
        current_dir / ".." / ".." / "work" / "code" / "mcp" / "server.py"
    ]
    
    for path in possible_paths:
        if path.exists():
            return path.resolve()
    
    return None

def main():
    """Main entry point for the global MCP server launcher"""
    parser = argparse.ArgumentParser(
        description="SRRD-Builder MCP Server Global Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    srrd-server                    # Start WebSocket server with default settings
    srrd-server --port 8080        # Start WebSocket server on specific port
    srrd-server --with-frontend    # Start both WebSocket server and web interface
    srrd-server --config ~/my.conf # Use custom configuration file
    
Note: For Claude Desktop/VS Code integration, use 'srrd serve' instead.
For more information, visit: https://github.com/markomanninen/srrd-builder
        """
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="WebSocket server port (default: 8765)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="WebSocket server host (default: localhost)"
    )
    

    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--with-frontend",
        action="store_true",
        help="Also start the web frontend server (default: port 8080)"
    )
    
    parser.add_argument(
        "--frontend-port",
        type=int,
        default=8080,
        help="Port for the frontend server (default: 8080)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="SRRD-Builder MCP Server 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Find the MCP server module
    server_path = find_mcp_server()
    if not server_path:
        print("Error: Cannot find MCP server module. Please reinstall srrd-builder.", file=sys.stderr)
        sys.exit(1)

    # Add the MCP server directory to Python path
    mcp_dir = server_path.parent
    sys.path.insert(0, str(mcp_dir))
    
    print(f"Starting SRRD-Builder MCP Server...")
    print(f"Mode: WebSocket server on {args.host}:{args.port}")
        
    # Start frontend server if requested
    frontend_thread = None
    if args.with_frontend:
        frontend_dir = find_frontend_dir(mcp_dir)
        if frontend_dir:
            print(f"🎨 Starting frontend server on port {args.frontend_port}...")
            frontend_thread = threading.Thread(
                target=start_frontend_server, 
                args=(frontend_dir, args.frontend_port),
                daemon=True
            )
            frontend_thread.start()
            
            # Give frontend a moment to start
            time.sleep(1)
            print(f"🌟 Complete SRRD demo running!")
            print(f"   • WebSocket API: ws://{args.host}:{args.port}")
            print(f"   • Web Interface: http://localhost:{args.frontend_port}")
            print(f"💡 Tip: Open http://localhost:{args.frontend_port} in your browser")
        else:
            print("⚠️  Frontend directory not found, skipping frontend server")

    try:
        # Import and start the server
        from server import MCPServer
        
        server = MCPServer(port=args.port)
        
        # Run in WebSocket mode
        asyncio.run(server.start_server())
            
    except KeyboardInterrupt:
        print("\nServer shutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
