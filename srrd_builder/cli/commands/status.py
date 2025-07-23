"""
SRRD Status Command - Check server status
"""

import json
import socket
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

def handle_status(args):
    """Handle 'srrd status' command"""
    current_dir = Path.cwd()
    home = Path.home()
    
    print(f"📋 SRRD Status")
    print("=" * 50)
    
    # Check current project pointer
    try:
        # Add the work/code/mcp directory to Python path so we can import current_project
        import sys
        # Try to find the srrd-builder root directory
        possible_roots = [
            Path(__file__).parent.parent.parent.parent,  # From CLI commands
            Path.cwd(),  # Current directory
            Path.cwd().parent,  # Parent directory
            home / 'Documents' / 'GitHub' / 'srrd-builder' / 'srrd-builder'  # Common development location
        ]
        
        current_project_path = None
        for root in possible_roots:
            mcp_path = root / 'work' / 'code' / 'mcp'
            if mcp_path.exists():
                if str(mcp_path) not in sys.path:
                    sys.path.insert(0, str(mcp_path))
                try:
                    from utils.current_project import get_current_project
                    current_project_path = get_current_project()
                    break
                except ImportError:
                    continue
        
        if current_project_path:
            # Load project config if available
            project_name = Path(current_project_path).name
            config_file = Path(current_project_path) / '.srrd' / 'config.json'
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    project_name = config.get('project_name', project_name)
                    domain = config.get('domain', 'Unknown')
                    print(f"🎯 Current Project: {project_name}")
                    print(f"   📁 Path: {current_project_path}")
                    print(f"   🏷️  Domain: {domain}")
                    if current_project_path == str(current_dir):
                        print(f"   📍 Status: Active (you are here)")
                    else:
                        print(f"   � Status: Set globally (use 'cd {current_project_path}' to navigate)")
                except Exception:
                    print(f"🎯 Current Project: {current_project_path}")
                    print(f"   ⚠️  Config file exists but couldn't be read")
            else:
                print(f"🎯 Current Project: {current_project_path}")
                print(f"   ⚠️  No config file found")
        else:
            print("🎯 Current Project: None set")
            print("   💡 Use 'srrd init' to create a project or 'srrd switch <path>' to set one")
    except Exception as e:
        print(f"🎯 Current Project: Could not determine ({e})")
    
    print()
    print(f"📂 Current Directory: {current_dir}")
    
    # Check if SRRD is initialized in current directory
    srrd_dir = current_dir / '.srrd'
    local_initialized = srrd_dir.exists()
    
    print(f"   ✅ Local SRRD initialized: {local_initialized}")
    
    # Check global server status (new global server system)
    global_pid_file = home / '.srrd' / 'server.pid'
    server_running = False
    server_info = None
    
    print()
    print("🌐 Global SRRD Servers:")
    
    if global_pid_file.exists():
        try:
            with open(global_pid_file, 'r') as f:
                server_info = json.load(f)
            
            pid = server_info.get('pid')
            frontend_pid = server_info.get('frontend_pid')
            host = server_info.get('host', 'localhost')
            port = server_info.get('port', 8080)
            frontend_port = server_info.get('frontend_port', 8765)
            
            servers_running = []
            
            # Check MCP server
            if pid:
                try:
                    import os
                    os.kill(pid, 0)
                    if check_port_in_use(host, port):
                        servers_running.append({
                            'name': 'MCP Server',
                            'pid': pid,
                            'port': port,
                            'type': 'MCP (Claude Desktop)'
                        })
                except ProcessLookupError:
                    pass
            
            # Check Web GUI server
            if frontend_pid:
                try:
                    import os
                    os.kill(frontend_pid, 0)
                    if check_port_in_use(host, frontend_port):
                        servers_running.append({
                            'name': 'Web GUI Server',
                            'pid': frontend_pid,
                            'port': frontend_port,
                            'type': 'WebSocket (Browser)'
                        })
                except ProcessLookupError:
                    pass
            
            if servers_running:
                server_running = True
                print(f"🟢 Global SRRD Servers: {len(servers_running)} Running")
                for server in servers_running:
                    print(f"   📡 {server['name']}")
                    print(f"      PID: {server['pid']}, Port: {server['port']}")
                    print(f"      Type: {server['type']}")
                print(f"   Started: {server_info.get('started', 'unknown')}")
                print(f"   Project: {server_info.get('project_path', 'global')}")
            else:
                print(f"🟡 Global server tracking file exists but servers not responding")
                
        except (json.JSONDecodeError, FileNotFoundError):
            print("🟡 Global server tracking file corrupted")
    
    if not server_running:
        print("🔴 Global SRRD servers not running")
        print("   Use 'srrd-server' to start the global server")
        print("   Or 'srrd configure --claude' + restart Claude to use MCP tools")
    
    # Check local project files (if locally initialized)
    if local_initialized:
        print()
        print("📁 Local Project Files:")
        config_file = srrd_dir / 'config.json'
        print(f"   📄 Config file: {'✅' if config_file.exists() else '❌'}")
        
        db_file = srrd_dir / 'srrd.db'
        print(f"   🗄️  SQLite database: {'✅' if db_file.exists() else '❌'}")
        
        vector_db_dir = srrd_dir / 'vector_db'
        print(f"   🔍 Vector database: {'✅' if vector_db_dir.exists() else '❌'}")
    else:
        print()
        print("💡 Tip: This directory is not initialized as an SRRD project")
        print("   Run 'srrd init' to initialize a local research project")
    
    # Check Git repository
    git_dir = current_dir / '.git'
    print(f"📁 Git repository: {'✅' if git_dir.exists() else '❌'}")
    
    return 0
