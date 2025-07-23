"""
Process Management Utilities for SRRD MCP Servers
"""

import os
import json
import subprocess
import signal
from pathlib import Path
from typing import List, Tuple

def find_mcp_processes() -> List[Tuple[str, str]]:
    """Find all running MCP server processes
    
    Returns:
        List of tuples (process_id, command_info)
    """
    processes = []
    
    try:
        import platform
        if platform.system() == "Windows":
            # Use tasklist on Windows
            cmd = ["tasklist", "/FO", "CSV", "/V"]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if ('python' in line.lower() and 
                        ('mcp_server' in line or 'srrd_builder.server.launcher' in line)):
                        # Parse CSV format
                        parts = line.split('","')
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            command = line
                            processes.append((pid, command))
        else:
            # Use ps on Unix-like systems
            cmd = ["ps", "aux"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ('python' in line and 
                        ('mcp_server' in line or 'srrd_builder.server.launcher' in line)):
                        # Extract PID (second column in ps aux output)
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            command = ' '.join(parts[10:])  # Command starts from 11th column
                            processes.append((pid, command))
    except Exception as e:
        # Silently handle on Windows - this is expected behavior
        import platform
        if platform.system() != "Windows":
            print(f"Warning: Could not list processes: {e}")
    
    return processes

def kill_mcp_processes(verbose: bool = True) -> int:
    """Kill all running MCP server processes
    
    Args:
        verbose: Print detailed information about killed processes
        
    Returns:
        Number of processes killed
    """
    home = Path.home()
    killed_count = 0
    
    # First, try to kill processes from PID file
    global_pid_file = home / '.srrd' / 'server.pid'
    if global_pid_file.exists():
        try:
            with open(global_pid_file, 'r') as f:
                server_info = json.load(f)
            
            pids_to_kill = []
            if 'pid' in server_info:
                pids_to_kill.append(('MCP Server', server_info['pid']))
            if 'frontend_pid' in server_info:
                pids_to_kill.append(('Web GUI Server', server_info['frontend_pid']))
            
            for name, pid in pids_to_kill:
                try:
                    os.kill(pid, signal.SIGTERM)
                    if verbose:
                        print(f"   🔄 Killed {name} (PID {pid})")
                    killed_count += 1
                except ProcessLookupError:
                    if verbose:
                        print(f"   ℹ️  {name} (PID {pid}) already stopped")
                except PermissionError:
                    if verbose:
                        print(f"   ❌ No permission to kill {name} (PID {pid})")
            
            # Remove the PID file
            global_pid_file.unlink()
            if verbose and killed_count > 0:
                print(f"   🗑️  Removed server tracking file")
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            if verbose:
                print(f"   ⚠️  Could not read server PID file: {e}")
    
    # Find and kill any remaining MCP processes
    remaining_processes = find_mcp_processes()
    
    for pid, command in remaining_processes:
        try:
            os.kill(int(pid), signal.SIGTERM)
            if verbose:
                print(f"   🔄 Killed remaining MCP process (PID {pid})")
                print(f"      Command: {command[:80]}...")
            killed_count += 1
        except (ProcessLookupError, ValueError):
            if verbose:
                print(f"   ℹ️  Process {pid} already stopped")
        except PermissionError:
            if verbose:
                print(f"   ❌ No permission to kill process {pid}")
    
    return killed_count

def restart_message(context: str = ""):
    """Print restart instructions for different MCP clients"""
    print()
    print("🔄 MCP Server processes killed successfully!")
    print()
    print("📱 Next Steps:")
    if context:
        print(f"   {context}")
    print("   • Claude Desktop: Restart Claude Desktop to connect to fresh server")
    print("   • VS Code Chat: MCP tools will auto-reconnect on next use")
    print("   • Browser Demo: Refresh the frontend demo page")
    print()
