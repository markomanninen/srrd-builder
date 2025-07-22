"""
Process cleanup utilities for SRRD-Builder
Handles cleanup of Claude Desktop and MCP server processes
"""
import os
import subprocess
import sys
import time
from typing import List, Optional


def get_running_processes(process_names: List[str]) -> List[dict]:
    """Get list of running processes by name"""
    processes = []
    
    if sys.platform == "win32":
        try:
            # PowerShell command to get processes
            cmd = ['powershell', '-Command', 
                   f'Get-Process | Where-Object {{$_.ProcessName -match "({"|".join(process_names)})"}} | Select-Object ProcessName, Id, Path | ConvertTo-Json']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                # Handle single process vs array
                if isinstance(data, dict):
                    processes = [data]
                else:
                    processes = data
        except Exception as e:
            print(f"Warning: Could not get process list: {e}", file=sys.stderr)
    else:
        # Unix/Linux process cleanup
        try:
            for name in process_names:
                result = subprocess.run(['pgrep', '-f', name], capture_output=True, text=True)
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            processes.append({'ProcessName': name, 'Id': int(pid)})
        except Exception as e:
            print(f"Warning: Could not get process list: {e}", file=sys.stderr)
    
    return processes


def kill_processes(process_names: List[str], force: bool = True) -> bool:
    """Kill processes by name"""
    success = True
    
    if sys.platform == "win32":
        try:
            # Kill processes using PowerShell
            for name in process_names:
                cmd = ['powershell', '-Command', f'Stop-Process -Name "{name}" -Force -ErrorAction SilentlyContinue']
                result = subprocess.run(cmd, timeout=10, capture_output=True, text=True)
                # PowerShell returns 0 even if no processes were found, so this is expected
            
            # Also kill any SRRD MCP server processes specifically
            cmd = ['powershell', '-Command', 
                   'Get-Process | Where-Object {$_.Path -like "*srrd-builder*"} | Stop-Process -Force -ErrorAction SilentlyContinue']
            result = subprocess.run(cmd, timeout=10, capture_output=True, text=True)
            
        except Exception as e:
            print(f"Warning: Could not kill processes: {e}", file=sys.stderr)
            success = False
    else:
        # Unix/Linux process cleanup
        try:
            for name in process_names:
                subprocess.run(['pkill', '-f' if force else '-TERM', name], timeout=10)
        except Exception as e:
            print(f"Warning: Could not kill processes: {e}", file=sys.stderr)
            success = False
    
    return success


def cleanup_claude_and_mcp_processes() -> bool:
    """Clean up Claude Desktop and MCP server processes"""
    print("🔄 Cleaning up Claude Desktop and MCP server processes...")
    
    # Process names to clean up
    process_names = ['claude', 'Claude']
    
    # Get running processes first
    running = get_running_processes(process_names)
    if running:
        print(f"   Found {len(running)} Claude/MCP processes to clean up")
        
        # Kill the processes
        if kill_processes(process_names, force=True):
            # Wait longer for processes to terminate
            time.sleep(3)
            
            # Verify cleanup - retry if needed
            remaining = get_running_processes(process_names)
            if remaining:
                print(f"   {len(remaining)} processes still running, retrying cleanup...")
                kill_processes(process_names, force=True)
                time.sleep(2)
                remaining = get_running_processes(process_names)
            
            if not remaining:
                print("✅ Process cleanup completed successfully")
                return True
            else:
                print(f"⚠️  {len(remaining)} processes still running after cleanup")
                return False
        else:
            print("❌ Failed to clean up processes")
            return False
    else:
        print("✅ No processes to clean up")
        return True


def restart_claude_desktop() -> bool:
    """Restart Claude Desktop after cleanup"""
    print("🚀 Starting Claude Desktop...")
    
    try:
        if sys.platform == "win32":
            # Find Claude Desktop executable
            claude_paths = [
                r"C:\Users\{}\AppData\Local\AnthropicClaude\Claude.exe".format(os.environ.get('USERNAME', '')),
                r"C:\Program Files\Claude\Claude.exe",
                r"C:\Program Files (x86)\Claude\Claude.exe"
            ]
            
            claude_exe = None
            for path in claude_paths:
                if os.path.exists(path):
                    claude_exe = path
                    break
            
            if claude_exe:
                subprocess.Popen([claude_exe], 
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
                
                # Wait and check for multiple processes (Claude Desktop Windows issue)
                print("⏳ Waiting for Claude Desktop to start...")
                time.sleep(5)
                
                claude_processes = get_running_processes(['claude', 'Claude'])
                if len(claude_processes) > 5:
                    print(f"⚠️  Claude Desktop started {len(claude_processes)} processes (Windows multi-process issue)")
                    print("💡 This is a known issue with Claude Desktop 0.12.28 on Windows")
                    print("   MCP connections may be unreliable with multiple processes")
                elif len(claude_processes) > 0:
                    print(f"✅ Claude Desktop started successfully ({len(claude_processes)} processes)")
                else:
                    print("⚠️  Claude Desktop may not have started properly")
                
                return True
            else:
                print("❌ Could not find Claude Desktop executable")
                return False
        else:
            # Unix/Linux - try common application launch methods
            try:
                subprocess.Popen(['claude'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅ Claude Desktop started successfully")
                return True
            except FileNotFoundError:
                print("❌ Could not find Claude Desktop executable")
                return False
                
    except Exception as e:
        print(f"❌ Failed to start Claude Desktop: {e}")
        return False


def full_mcp_reset() -> bool:
    """Perform a full MCP reset: cleanup processes and restart Claude"""
    print("\n🔧 Performing MCP server reset...")
    
    # Step 1: Cleanup processes
    if not cleanup_claude_and_mcp_processes():
        print("⚠️  Process cleanup had issues, but continuing...")
    
    # Step 2: Wait a moment
    print("⏳ Waiting for processes to fully terminate...")
    time.sleep(3)
    
    # Step 3: Restart Claude Desktop
    if restart_claude_desktop():
        print("✅ MCP reset completed successfully")
        print("💡 Please wait a few seconds for Claude Desktop to fully load the MCP configuration")
        return True
    else:
        print("⚠️  MCP reset completed, but you may need to manually start Claude Desktop")
        return False
