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
    
    # Check if SRRD is initialized
    srrd_dir = current_dir / '.srrd'
    if not srrd_dir.exists():
        print("❌ SRRD not initialized in current directory")
        print("   Run 'srrd init' first")
        return 1
    
    print(f"📋 SRRD Status for: {current_dir}")
    print("=" * 50)
    
    # Check initialization
    print(f"✅ SRRD initialized: {srrd_dir.exists()}")
    
    # Check server status
    pid_file = srrd_dir / 'server.pid'
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid_data = json.load(f)
            
            host = pid_data.get('host', 'localhost')
            port = pid_data.get('port', 8080)
            
            if check_port_in_use(host, port):
                print(f"🟢 Server running")
                print(f"   PID: {pid_data.get('pid', 'unknown')}")
                print(f"   Started: {pid_data.get('started', 'unknown')}")
                print(f"   Host: {host}")
                print(f"   Port: {port}")
            else:
                print(f"🟡 Server tracking file exists but port {port} not in use")
                print(f"   (Server may have stopped unexpectedly)")
                
        except (json.JSONDecodeError, FileNotFoundError):
            print("🟡 Server tracking file corrupted")
    else:
        print("🔴 Server not running")
    
    # Check configuration
    config_file = srrd_dir / 'config.json'
    print(f"📄 Config file: {'✅' if config_file.exists() else '❌'}")
    
    # Check databases
    db_file = srrd_dir / 'srrd.db'
    print(f"🗄️  SQLite database: {'✅' if db_file.exists() else '❌'}")
    
    vector_db_dir = srrd_dir / 'vector_db'
    print(f"🔍 Vector database: {'✅' if vector_db_dir.exists() else '❌'}")
    
    # Check Git repository
    git_dir = current_dir / '.git'
    print(f"📁 Git repository: {'✅' if git_dir.exists() else '❌'}")
    
    return 0
