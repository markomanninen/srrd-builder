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
import subprocess
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
    
    # Auto-initialize if needed
    srrd_dir = current_dir / '.srrd'
    if not srrd_dir.exists():
        print("🔧 SRRD not initialized - auto-initializing...")
        
        # Check if git repository exists, if not initialize it
        from ...utils.git_utils import is_git_repository
        if not is_git_repository(current_dir):
            print("🔧 Initializing Git repository...")
            try:
                subprocess.run(['git', 'init'], 
                             cwd=current_dir, 
                             check=True, 
                             capture_output=True)
                print("   ✅ Git repository initialized")
                
                # Create initial .gitignore for SRRD
                gitignore_content = """# SRRD-Builder
.srrd/data/
.srrd/logs/
*.log
__pycache__/
*.pyc
*.pyo
.DS_Store
.vscode/
"""
                gitignore_file = current_dir / '.gitignore'
                with open(gitignore_file, 'w') as f:
                    f.write(gitignore_content)
                print("   ✅ Initial .gitignore created")
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to initialize Git: {e}")
                return 1
            except FileNotFoundError:
                print("   ❌ Git not found. Please install Git first.")
                return 1
        
        # Initialize SRRD project structure
        print("🔧 Initializing SRRD project structure...")
        from .init import create_project_structure
        
        domain = getattr(args, 'domain', 'general_research')
        template = getattr(args, 'template', 'basic')
        
        if create_project_structure(current_dir, domain, template, force=False):
            print("   ✅ SRRD project initialized")
        else:
            print("   ❌ Failed to initialize SRRD project")
            return 1
    
    # Add the existing MCP server to Python path
    mcp_server_path = Path(__file__).parent.parent.parent.parent / 'work' / 'code' / 'mcp'
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found at: {mcp_server_path}")
        print("   This may indicate the package structure needs adjustment")
        return 1
    
    try:
        print(f"🚀 Configuring SRRD MCP Server for THIS project")
        print(f"   Project: {current_dir}")
        
        # Create/update the GLOBAL launcher with THIS project's path
        global_launcher_dir = Path(__file__).parent.parent.parent.parent / 'srrd_builder'
        global_launcher_script = global_launcher_dir / 'mcp_global_launcher.py'
        
        launcher_content = f'''#!/usr/bin/env python3
"""
SRRD MCP Launcher - Context Set by 'srrd serve'
Project path was set when 'srrd serve start' was run.
"""

import sys
import os
from pathlib import Path

# Project context set by 'srrd serve start'
PROJECT_PATH = '{current_dir}'
CONFIG_PATH = '{srrd_dir / "config.json"}'

def main():
    """Main launcher - uses the project set by srrd serve"""
    # Set the project context from when 'srrd serve' was run
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
        
        # Make it executable
        global_launcher_script.chmod(0o755)
        
        print(f"✅ MCP Server configured for: {current_dir}")
        print(f"   Launcher: {global_launcher_script}")
        print(f"   All MCP tools will now use THIS project's database!")
        
        print("\n🎯 Claude Desktop Config (set once):")
        print(f"   {{")
        print(f"     \"mcpServers\": {{")
        print(f"       \"srrd-builder\": {{")
        print(f"         \"command\": \"python3\",")
        print(f"         \"args\": [\"{global_launcher_script}\"]")
        print(f"       }}")
        print(f"     }}")
        print(f"   }}")
        print("\n🚀 To switch projects:")
        print("1. cd /path/to/other/srrd/project")
        print("2. srrd serve start")
        print("3. All MCP tools now use the new project!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Server configuration error: {e}")
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
