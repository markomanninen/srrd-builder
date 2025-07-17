"""
SRRD Serve Command - Start/Stop/Restart MCP Server
"""

import sys
import os
import socket
import json
import signal
import time
import asyncio
from pathlib import Path

def check_port_in_use(host, port):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0  # True if port is in use
    except socket.error:
        return False

def check_existing_server(current_dir, host, port):
    """Check for existing SRRD server instances"""
    srrd_dir = current_dir / '.srrd'
    pid_file = srrd_dir / 'server.pid'
    
    # Check if we have a tracked server process
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid_data = json.load(f)
                
            pid = pid_data.get('pid')
            if pid:
                try:
                    # Check if process is still running
                    os.kill(pid, 0)  # This doesn't kill, just checks if process exists
                    
                    print(f"⚠️  SRRD server is already running")
                    print(f"   PID: {pid}")
                    print(f"   Started: {pid_data.get('started', 'unknown')}")
                    print(f"   Project: {pid_data.get('project_path', current_dir)}")
                    
                    response = input("   Stop existing server and start new one? (y/N): ")
                    if response.lower() in ['y', 'yes']:
                        # Stop the existing server
                        try:
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(2)
                            try:
                                os.kill(pid, 0)  # Check if still running
                                os.kill(pid, signal.SIGKILL)  # Force kill
                            except ProcessLookupError:
                                pass
                        except ProcessLookupError:
                            pass
                        
                        # Clean up PID file
                        pid_file.unlink()
                        print("   Stopped existing server")
                        return False  # Proceed with starting
                    else:
                        return True  # Don't start
                        
                except ProcessLookupError:
                    # Process doesn't exist anymore, clean up stale PID file
                    pid_file.unlink()
                    print("   Cleaned up stale server tracking file")
                    
        except (json.JSONDecodeError, FileNotFoundError):
            # PID file is corrupted or missing
            if pid_file.exists():
                pid_file.unlink()
                print("   Cleaned up corrupted server tracking file")
    
    return False  # No server running, proceed

def create_server_tracking(current_dir, host, port):
    """Create server tracking file"""
    import time
    import os
    
    srrd_dir = current_dir / '.srrd'
    pid_file = srrd_dir / 'server.pid'
    
    pid_data = {
        'pid': os.getpid(),
        'host': host,
        'port': port,
        'started': time.strftime('%Y-%m-%d %H:%M:%S'),
        'project_path': str(current_dir)
    }
    
    with open(pid_file, 'w') as f:
        json.dump(pid_data, f, indent=2)

def cleanup_server_tracking(current_dir):
    """Clean up server tracking file"""
    srrd_dir = current_dir / '.srrd'
    pid_file = srrd_dir / 'server.pid'
    
    if pid_file.exists():
        pid_file.unlink()

def stop_server(current_dir):
    """Stop running SRRD server"""
    srrd_dir = current_dir / '.srrd'
    pid_file = srrd_dir / 'server.pid'
    
    if not pid_file.exists():
        print("❌ No server tracking file found")
        print("   Server may not be running or was started outside SRRD CLI")
        return False
    
    try:
        with open(pid_file, 'r') as f:
            pid_data = json.load(f)
        
        pid = pid_data.get('pid')
        if not pid:
            print("❌ Invalid server tracking file")
            pid_file.unlink()
            return False
        
        print(f"🛑 Stopping SRRD server (PID: {pid})")
        
        try:
            # Try to terminate the process gracefully
            os.kill(pid, signal.SIGTERM)
            
            # Wait a bit for graceful shutdown
            time.sleep(2)
            
            # Check if process is still running
            try:
                os.kill(pid, 0)  # This checks if process exists
                print("   Forcing server shutdown...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            except ProcessLookupError:
                pass  # Process already terminated
                
        except ProcessLookupError:
            print("   Server process was already stopped")
        except PermissionError:
            print("❌ Permission denied - cannot stop server")
            return False
        
        # Clean up tracking file
        pid_file.unlink()
        print("✅ Server stopped successfully")
        return True
        
    except (json.JSONDecodeError, FileNotFoundError):
        print("❌ Corrupted server tracking file")
        pid_file.unlink() if pid_file.exists() else None
        return False
    except Exception as e:
        print(f"❌ Error stopping server: {e}")
        return False

def restart_server(args):
    """Restart SRRD server"""
    current_dir = Path.cwd()
    
    print("🔄 Restarting SRRD server...")
    
    # Stop existing server
    if stop_server(current_dir):
        print("   Waiting for clean shutdown...")
        time.sleep(1)
    
    # Start new server
    print("   Starting new server...")
    return handle_serve_start(args)

def handle_serve_start(args):
    """Handle starting the server"""
    current_dir = Path.cwd()
    
    # Check if SRRD is initialized
    srrd_dir = current_dir / '.srrd'
    if not srrd_dir.exists():
        print("❌ SRRD not initialized in current directory")
        print("   Run 'srrd init' first")
        return 1
    
    # Check for existing servers
    if check_existing_server(current_dir, args.host, args.port):
        print("❌ Cannot start server - address already in use")
        return 1
    
    # Add the existing MCP server to Python path
    mcp_server_path = Path(__file__).parent.parent.parent.parent / 'work' / 'code' / 'mcp'
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found at: {mcp_server_path}")
        print("   This may indicate the package structure needs adjustment")
        return 1
    
    # Add to Python path
    sys.path.insert(0, str(mcp_server_path))
    
    try:
        # Import and start the MCP server
        from mcp_server import ClaudeMCPServer
        
        print(f"🚀 Starting SRRD MCP Server")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port}")
        print(f"   Project: {current_dir}")
        print("   Press Ctrl+C to stop")
        
        # Create server tracking
        create_server_tracking(current_dir, args.host, args.port)
        
        # Set environment variables for MCP server
        os.environ['SRRD_PROJECT_PATH'] = str(current_dir)
        os.environ['SRRD_CONFIG_PATH'] = str(srrd_dir / 'config.json')
        
        # Start the MCP server
        server = ClaudeMCPServer()
        result = asyncio.run(server.run())
        
        # Clean up on exit
        cleanup_server_tracking(current_dir)
        return result or 0
        
    except ImportError as e:
        print(f"❌ Could not import MCP server: {e}")
        print("   The MCP server components may not be properly installed")
        cleanup_server_tracking(current_dir)
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        cleanup_server_tracking(current_dir)
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        cleanup_server_tracking(current_dir)
        return 1

def handle_serve(args):
    """Handle 'srrd serve' command with subcommands"""
    if not hasattr(args, 'serve_action') or args.serve_action is None:
        # Default to start if no subcommand specified
        return handle_serve_start(args)
    
    current_dir = Path.cwd()
    
    if args.serve_action == 'start':
        return handle_serve_start(args)
    elif args.serve_action == 'stop':
        success = stop_server(current_dir)
        return 0 if success else 1
    elif args.serve_action == 'restart':
        return restart_server(args)
    else:
        print(f"Unknown serve action: {args.serve_action}")
        return 1
