"""
SRRD Configure Command - Configure MCP server with IDEs and clients
"""

import json
import os
import platform
import socket
from pathlib import Path

def load_json_with_comments(file_path):
    """Load JSON file that may contain comments (VS Code settings.json)"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Simple approach: try to load as-is first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Remove single-line comments
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Find // that's not inside a string
            if '//' in line:
                in_string = False
                escaped = False
                comment_start = None
                for i, char in enumerate(line):
                    if escaped:
                        escaped = False
                        continue
                    if char == '\\':
                        escaped = True
                        continue
                    if char == '"' and not escaped:
                        in_string = not in_string
                    elif not in_string and char == '/' and i < len(line) - 1 and line[i + 1] == '/':
                        comment_start = i
                        break
                
                if comment_start is not None:
                    line = line[:comment_start].rstrip()
            
            cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Handle trailing commas by trying a simple regex replacement
        import re
        cleaned_content = re.sub(r',(\s*[}\]])', r'\1', cleaned_content)
        
        return json.loads(cleaned_content)
    
    except Exception:
        # Fallback to standard JSON parsing
        with open(file_path, 'r') as f:
            return json.load(f)

def get_claude_config_path():
    """Get Claude Desktop configuration path based on OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        return None

def get_vscode_config_path():
    """Get VS Code mcp.json path based on OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Code" / "User" / "mcp.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Code" / "User" / "mcp.json"
    else:
        return None

def get_srrd_mcp_config():
    """Get SRRD MCP server configuration"""
    import platform
    
    # Get the path to the MCP server
    package_root = Path(__file__).parent.parent.parent.parent
    mcp_server_path = package_root / 'work' / 'code' / 'mcp' / 'mcp_server.py'
    
    # Use the full path to the virtual environment's Python on Windows
    if platform.system() == "Windows":
        venv_python = package_root / 'venv' / 'Scripts' / 'python.exe'
        if venv_python.exists():
            python_cmd = str(venv_python)
        else:
            python_cmd = "python"
    else:
        python_cmd = "python3"
    
    return {
        "command": python_cmd,
        "args": [str(mcp_server_path)],
        "env": {},
        "type": "stdio"
    }

def configure_claude(force=False):
    """Configure SRRD MCP server for Claude Desktop"""
    config_path = get_claude_config_path()
    if not config_path:
        print("❌ Unsupported operating system for Claude Desktop configuration")
        return False
    
    print(f"📁 Claude config path: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing Claude config is invalid JSON, creating new one")
            config = {}
    else:
        config = {}
    
    # Ensure mcpServers section exists (Claude Desktop format)
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if SRRD is already configured
    if "srrd-builder" in config["mcpServers"] and not force:
        print("✅ SRRD-Builder already configured in Claude Desktop")
        print("   Use --force to overwrite existing configuration")
        return True
    
    # Add SRRD MCP server configuration
    config["mcpServers"]["srrd-builder"] = get_srrd_mcp_config()
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ SRRD-Builder MCP server configured for Claude Desktop")
        print("   Restart Claude Desktop to use the new configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to write Claude config: {e}")
        return False

def configure_vscode(force=False):
    """Configure SRRD MCP server for VS Code"""
    config_path = get_vscode_config_path()
    if not config_path:
        print("❌ Unsupported operating system for VS Code configuration")
        return False
    
    print(f"📁 VS Code MCP config path: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing VS Code MCP config is invalid JSON, creating new one")
            config = {}
    else:
        config = {}
    
    # Ensure servers section exists
    if "servers" not in config:
        config["servers"] = {}
    if "inputs" not in config:
        config["inputs"] = []
    
    # Check if SRRD is already configured
    if "srrd-builder" in config["servers"] and not force:
        print("✅ SRRD-Builder already configured in VS Code")
        print("   Use --force to overwrite existing configuration")
        return True
    
    # Add SRRD MCP server configuration
    config["servers"]["srrd-builder"] = get_srrd_mcp_config()
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ SRRD-Builder MCP server configured for VS Code")
        print("   Restart VS Code to use the new configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to write VS Code MCP config: {e}")
        return False

def show_config_status():
    """Show current MCP configuration status"""
    print("🔧 MCP Configuration Status")
    print("=" * 40)
    
    # Check if server is currently running
    current_dir = Path.cwd()
    home = Path.home()
    pid_file = home / '.srrd' / 'server.pid'  # Global server PID file in home directory
    
    server_running = False
    server_info = None
    
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
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
                print(f"🟢 SRRD Servers: {len(servers_running)} Running")
                for server in servers_running:
                    print(f"   📡 {server['name']}")
                    print(f"      PID: {server['pid']}")
                    print(f"      Address: {host}:{server['port']}")
                    print(f"      Type: {server['type']}")
                print(f"   Started: {server_info.get('started', 'unknown')}")
                print(f"   Project: {server_info.get('project_path', current_dir)}")
                
                # Show connection info for clients
                print(f"🔗 Connection Info:")
                mcp_running = any(s['name'] == 'MCP Server' for s in servers_running)
                web_running = any(s['name'] == 'Web GUI Server' for s in servers_running)
                
                if mcp_running:
                    print(f"   Claude Desktop: Ready (restart Claude to connect)")
                    print(f"   VS Code: Ready (reload window to connect)")
                if web_running:
                    print(f"   Browser: http://{host}:{frontend_port}")
            else:
                print(f"🟡 Servers: Process files exist but servers not responding")
                print(f"   Main PID {pid}, Frontend PID {frontend_pid}")
                # Clean up stale PID file
                pid_file.unlink()
                
        except (json.JSONDecodeError, FileNotFoundError):
            print("🟡 Local Server: Corrupted tracking file")
            if pid_file.exists():
                pid_file.unlink()
    
    if not server_running:
        print("🔴 Local Server: Not running")
        print("   Use 'srrd configure --claude' to configure Claude Desktop")
        print("   Then restart Claude Desktop to use MCP tools")
    
    print()  # Separator
    
    # Check Claude Desktop
    claude_path = get_claude_config_path()
    if claude_path and claude_path.exists():
        try:
            with open(claude_path, 'r') as f:
                claude_config = json.load(f)
            
            if "mcpServers" in claude_config and "srrd-builder" in claude_config["mcpServers"]:
                print("✅ Claude Desktop: SRRD-Builder configured")
                srrd_config = claude_config["mcpServers"]["srrd-builder"]
                print(f"   Command: {srrd_config.get('command', 'unknown')}")
                print(f"   Server Path: {' '.join(srrd_config.get('args', []))}")
                if server_running:
                    print("   💡 Tip: Restart Claude Desktop to use the running server")
            else:
                print("❌ Claude Desktop: SRRD-Builder not configured")
                print("   Use 'srrd configure --claude' to configure")
        except:
            print("⚠️  Claude Desktop: Config file exists but unreadable")
    else:
        print("❌ Claude Desktop: Config file not found")
        print("   Use 'srrd configure --claude' to configure")
    
    # Check VS Code
    vscode_path = get_vscode_config_path()
    if vscode_path and vscode_path.exists():
        try:
            with open(vscode_path, 'r') as f:
                vscode_config = json.load(f)
            
            if "servers" in vscode_config and "srrd-builder" in vscode_config["servers"]:
                print("✅ VS Code: SRRD-Builder configured")
                srrd_config = vscode_config["servers"]["srrd-builder"]
                print(f"   Command: {srrd_config.get('command', 'unknown')}")
                print(f"   Server Path: {' '.join(srrd_config.get('args', []))}")
                if server_running:
                    print("   💡 Tip: Reload VS Code window to use the running server")
            else:
                print("❌ VS Code: SRRD-Builder not configured")
                print("   Use 'srrd configure --vscode' to configure")
        except Exception as e:
            print(f"⚠️  VS Code: MCP config file exists but unreadable - {e}")
    else:
        print("❌ VS Code: MCP config file not found")
        print("   Use 'srrd configure --vscode' to configure")
    
    # Show MCP server components
    print("📍 MCP Server Components:")
    srrd_config = get_srrd_mcp_config()
    launcher_path = Path(srrd_config["args"][0])
    print(f"   Launcher: {launcher_path}")
    print(f"   Launcher exists: {'✅' if launcher_path.exists() else '❌'}")
    
    # Check actual MCP server files
    package_root = launcher_path.parent.parent
    actual_server_path = package_root / 'work' / 'code' / 'mcp' / 'server.py'
    print(f"   MCP Server: {actual_server_path}")
    print(f"   Server exists: {'✅' if actual_server_path.exists() else '❌'}")
    
    # Check MCP tools
    tools_path = package_root / 'work' / 'code' / 'mcp' / 'tools'
    print(f"   Tools directory: {'✅' if tools_path.exists() else '❌'}")
    
    # Show usage tips
    if server_running:
        print()
        print("💡 Server Management:")
        print("   Demo:    srrd-server --with-frontend")
        print("   Status:  srrd-server status")
        print("   Stop:    srrd-server stop")
    else:
        print()
        print("💡 Quick Start:")
        print("   1. srrd configure --claude  # Configure Claude Desktop")
        print("   2. Restart Claude Desktop") 
        print("   3. Use SRRD-Builder tools in Claude!")

def check_port_in_use(host, port):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0  # True if port is in use
    except socket.error:
        return False

def handle_configure(args):
    """Handle 'srrd configure' command"""
    if args.show_status:
        show_config_status()
        return 0
    
    success = True
    
    if args.claude or args.all:
        print("🔧 Configuring Claude Desktop...")
        if not configure_claude(args.force):
            success = False
        print()
    
    if args.vscode or args.all:
        print("🔧 Configuring VS Code...")
        if not configure_vscode(args.force):
            success = False
        print()
    
    if not (args.claude or args.vscode or args.all):
        print("❌ Please specify --claude, --vscode, or --all")
        print("   Or use --status to show current configuration")
        return 1
    
    if success:
        print("✅ Configuration completed successfully")
        print("   Restart your IDE(s) to use the new MCP server configuration")
    else:
        print("❌ Some configurations failed")
    
    return 0 if success else 1
