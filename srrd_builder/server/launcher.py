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
import signal
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

def get_pid_file_path():
    """Get the path to the PID file"""
    home = Path.home()
    pid_file = home / ".srrd" / "server.pid"
    pid_file.parent.mkdir(exist_ok=True)
    return pid_file

def save_server_pid(pid, port, host, frontend_pid=None, frontend_port=None):
    """Save server PID to file"""
    pid_file = get_pid_file_path()
    pid_data = {
        'pid': pid,
        'port': port,
        'host': host,
        'started': time.strftime('%Y-%m-%d %H:%M:%S'),
        'frontend_pid': frontend_pid,
        'frontend_port': frontend_port
    }
    with open(pid_file, 'w') as f:
        json.dump(pid_data, f, indent=2)

def load_server_pid():
    """Load server PID from file"""
    pid_file = get_pid_file_path()
    if not pid_file.exists():
        return None
    
    try:
        with open(pid_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def cleanup_pid_file():
    """Remove PID file"""
    pid_file = get_pid_file_path()
    if pid_file.exists():
        pid_file.unlink()

def is_server_running():
    """Check if server is running"""
    pid_data = load_server_pid()
    
    # First check PID file if it exists
    if pid_data:
        pid = pid_data.get('pid')
        if pid:
            try:
                # Check if process exists (doesn't kill it)
                os.kill(pid, 0)
                return True
            except OSError:
                pass
    
    # Fallback: Check if ports are in use
    import subprocess
    try:
        # Check if port 8765 is in use (WebSocket server)
        result = subprocess.run(['lsof', '-i', ':8765'], capture_output=True, text=True)
        if result.stdout.strip():
            return True
        
        # Also check for SRRD-related processes
        result = subprocess.run(['pgrep', '-f', 'srrd_builder'], capture_output=True)
        if result.returncode == 0:
            return True
            
        result = subprocess.run(['pgrep', '-f', 'mcp_server'], capture_output=True)
        if result.returncode == 0:
            return True
            
    except Exception:
        pass
    
    return False

def stop_server():
    """Stop the running server"""
    pid_data = load_server_pid()
    success = True
    
    # First try to stop using PID file if it exists
    if pid_data:
        main_pid = pid_data.get('pid')
        frontend_pid = pid_data.get('frontend_pid')
        
        if main_pid:
            try:
                print(f"🛑 Stopping main server (PID: {main_pid})...")
                os.kill(main_pid, signal.SIGTERM)
                time.sleep(2)
                
                # Force kill if still running
                try:
                    os.kill(main_pid, 0)
                    print("⚠️  Main server didn't stop gracefully, force killing...")
                    os.kill(main_pid, signal.SIGKILL)
                    time.sleep(0.5)
                except OSError:
                    pass
                    
            except OSError:
                print("ℹ️  Main server was not running")
        
        # Stop frontend server if it exists
        if frontend_pid:
            try:
                print(f"🛑 Stopping frontend server (PID: {frontend_pid})...")
                os.kill(frontend_pid, signal.SIGTERM)
                time.sleep(1)
                
                # Force kill if still running
                try:
                    os.kill(frontend_pid, 0)
                    print("⚠️  Frontend server didn't stop gracefully, force killing...")
                    os.kill(frontend_pid, signal.SIGKILL)
                    time.sleep(0.5)
                except OSError:
                    pass
                    
            except OSError:
                print("ℹ️  Frontend server was not running")
    else:
        print("ℹ️  No PID file found, searching for running processes...")
    
    # Always kill any processes by name as fallback (more aggressive)
    print("🧹 Cleaning up any remaining SRRD processes...")
    import subprocess
    try:
        # Kill processes using ports
        print("🔌 Killing processes using ports 8765 and 8080...")
        subprocess.run(['bash', '-c', 'lsof -ti:8765 | xargs -r kill -TERM'], capture_output=True)
        subprocess.run(['bash', '-c', 'lsof -ti:8080 | xargs -r kill -TERM'], capture_output=True)
        time.sleep(2)
        
        # Force kill if still there
        subprocess.run(['bash', '-c', 'lsof -ti:8765 | xargs -r kill -KILL'], capture_output=True)
        subprocess.run(['bash', '-c', 'lsof -ti:8080 | xargs -r kill -KILL'], capture_output=True)
        
        # Kill SRRD-related processes
        subprocess.run(['pkill', '-f', 'srrd_builder'], capture_output=True)
        subprocess.run(['pkill', '-f', 'mcp_server'], capture_output=True)
        subprocess.run(['pkill', '-f', 'run_server.py'], capture_output=True)
        subprocess.run(['pkill', '-f', 'SimpleHTTPRequestHandler'], capture_output=True)
        subprocess.run(['pkill', '-f', 'frontend.*8080'], capture_output=True)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")
    
    cleanup_pid_file()
    print("✅ Server stopped successfully")
    return success

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

def start_frontend_process(frontend_dir, port):
    """Start the frontend server in a separate process and return PID"""
    import subprocess
    import sys
    
    # Convert Path object to string and escape backslashes for Windows
    frontend_dir_str = str(frontend_dir).replace('\\', '\\\\')
    
    # Create a simple HTTP server script
    script_content = f"""
import socketserver
from http.server import SimpleHTTPRequestHandler
import os
import sys

class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='{frontend_dir_str}', **kwargs)
    
    def log_message(self, format, *args):
        pass

try:
    with socketserver.TCPServer(("", {port}), FrontendHandler) as httpd:
        print(f"🌐 Frontend server running on http://localhost:{port}")
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Frontend server error: {{e}}")
    sys.exit(1)
"""
    
    # Start the process
    try:
        process = subprocess.Popen([sys.executable, '-c', script_content])
        return process.pid
    except Exception as e:
        print(f"❌ Failed to start frontend process: {e}")
        return None

def find_mcp_server():
    """Find the MCP server module in the installed package"""
    try:
        # Try to import from installed package
        import srrd_builder
        package_path = Path(srrd_builder.__file__).parent
        mcp_server_path = package_path / "work" / "code" / "mcp" / "server.py"
        
        if (mcp_server_path.exists()):
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
    srrd-server stop               # Stop the running server
    srrd-server restart            # Restart the server
    
Note: For Claude Desktop/VS Code integration, configure Claude with 'srrd configure --claude' instead.
For more information, visit: https://github.com/markomanninen/srrd-builder
        """
    )
    
    parser.add_argument(
        "action",
        nargs="?",
        choices=["start", "stop", "restart", "status"],
        default="start",
        help="Action to perform (default: start)"
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
    
    # Handle non-start actions first
    if args.action == "stop":
        if stop_server():
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.action == "status":
        pid_data = load_server_pid()
        if pid_data:
            pid = pid_data.get('pid')
            frontend_pid = pid_data.get('frontend_pid')
            host = pid_data.get('host', 'localhost')
            port = pid_data.get('port', 8080)
            frontend_port = pid_data.get('frontend_port', 8765)
            
            servers_running = []
            
            # Check MCP server
            if pid:
                try:
                    os.kill(pid, 0)
                    # Check if port is in use
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        if sock.connect_ex((host, port)) == 0:
                            servers_running.append({
                                'name': 'MCP Server',
                                'pid': pid,
                                'port': port,
                                'type': 'MCP (Claude Desktop)'
                            })
                except (ProcessLookupError, socket.error):
                    pass
            
            # Check Web GUI server
            if frontend_pid:
                try:
                    os.kill(frontend_pid, 0)
                    # Check if port is in use
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        if sock.connect_ex((host, frontend_port)) == 0:
                            servers_running.append({
                                'name': 'Web GUI Server',
                                'pid': frontend_pid,
                                'port': frontend_port,
                                'type': 'WebSocket (Browser)'
                            })
                except (ProcessLookupError, socket.error):
                    pass
            
            if servers_running:
                print(f"✅ SRRD Servers are running ({len(servers_running)} servers)")
                for server in servers_running:
                    print(f"   📡 {server['name']} (PID: {server['pid']}) - {host}:{server['port']}")
                print(f"   Started: {pid_data.get('started', 'unknown')}")
                sys.exit(0)
            else:
                print("❌ Server processes exist but not responding")
                # Clean up stale PID file
                get_pid_file_path().unlink(missing_ok=True)
                sys.exit(1)
        else:
            print("❌ Server is not running")
            sys.exit(1)
    
    elif args.action == "restart":
        print("🔄 Restarting server...")
        if is_server_running():
            if not stop_server():
                print("❌ Failed to stop existing server")
                sys.exit(1)
            print("⏳ Waiting for ports to be released...")
            time.sleep(3)  # Wait longer for ports to be released
        # Continue to start the server
    
    # Check if server is already running for start action
    elif args.action == "start":
        if is_server_running():
            pid_data = load_server_pid()
            pid = pid_data.get('pid')
            frontend_pid = pid_data.get('frontend_pid')
            host = pid_data.get('host', 'localhost')
            port = pid_data.get('port', 8080)
            frontend_port = pid_data.get('frontend_port', 8765)
            
            servers_running = []
            
            # Check MCP server
            if pid:
                try:
                    os.kill(pid, 0)
                    servers_running.append({
                        'name': 'MCP Server',
                        'pid': pid,
                        'port': port,
                        'type': 'Claude Desktop'
                    })
                except OSError:
                    pass
            
            # Check Web GUI server
            if frontend_pid:
                try:
                    os.kill(frontend_pid, 0)
                    servers_running.append({
                        'name': 'Web GUI Server', 
                        'pid': frontend_pid,
                        'port': frontend_port,
                        'type': 'Browser WebSocket'
                    })
                except OSError:
                    pass
            
            if servers_running:
                print(f"⚠️  SRRD Servers are already running ({len(servers_running)} servers)")
                for server in servers_running:
                    print(f"   📡 {server['name']} (PID: {server['pid']}) - {host}:{server['port']}")
                print(f"   Started: {pid_data.get('started')}")
                print("   Use 'srrd-server stop' to stop them or 'srrd-server restart' to restart")
            else:
                print(f"⚠️  Server process file exists but servers not responding")
                print(f"   You may need to clean up with 'srrd-server stop'")
            sys.exit(1)
    
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
    frontend_pid = None
    if args.with_frontend:
        frontend_dir = find_frontend_dir(mcp_dir)
        if frontend_dir:
            print(f"🎨 Starting frontend server on port {args.frontend_port}...")
            frontend_pid = start_frontend_process(frontend_dir, args.frontend_port)
            if frontend_pid:
                time.sleep(1)  # Give frontend a moment to start
                print(f"🌟 Complete SRRD demo running!")
                print(f"   • WebSocket API: ws://{args.host}:{args.port}")
                print(f"   • Web Interface: http://localhost:{args.frontend_port}")
                print(f"💡 Tip: Open http://localhost:{args.frontend_port} in your browser")
            else:
                print("❌ Failed to start frontend server")
        else:
            print("⚠️  Frontend directory not found, skipping frontend server")

    try:
        # Import and start the server
        from server import MCPServer
        
        server = MCPServer(port=args.port)
        
        # Save PID before starting (including frontend PID if started)
        save_server_pid(os.getpid(), args.port, args.host, frontend_pid, args.frontend_port if args.with_frontend else None)
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}, shutting down...")
            cleanup_pid_file()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run in WebSocket mode
        asyncio.run(server.start_server())
            
    except KeyboardInterrupt:
        print("\nServer shutdown by user")
        cleanup_pid_file()
        cleanup_pid_file()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        cleanup_pid_file()
        sys.exit(1)

if __name__ == "__main__":
    main()
