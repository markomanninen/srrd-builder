#!/bin/bash

# SRRD MCP Server Clean Restart Script
# This script safely stops all MCP server processes and cleans up resources

echo "🔄 SRRD MCP Server Clean Restart"
echo "================================="

# Function to check if any MCP processes are running
check_mcp_processes() {
    local processes=$(ps aux | grep "srrd_builder.server.launcher" | grep -v grep)
    if [ -n "$processes" ]; then
        echo "Found running MCP processes:"
        echo "$processes"
        return 0
    else
        echo "No MCP processes found."
        return 1
    fi
}

# Function to kill MCP processes gracefully
kill_mcp_processes() {
    echo "🛑 Stopping MCP server processes..."
    
    # First try graceful shutdown with SIGTERM
    local pids=$(pgrep -f "srrd_builder.server.launcher")
    if [ -n "$pids" ]; then
        echo "Sending SIGTERM to PIDs: $pids"
        kill -TERM $pids
        sleep 3
        
        # Check if processes are still running
        local remaining_pids=$(pgrep -f "srrd_builder.server.launcher")
        if [ -n "$remaining_pids" ]; then
            echo "Some processes still running, sending SIGKILL to PIDs: $remaining_pids"
            kill -KILL $remaining_pids
            sleep 1
        fi
    fi
    
    # Verify all processes are stopped
    if check_mcp_processes > /dev/null 2>&1; then
        echo "❌ Warning: Some MCP processes may still be running"
        return 1
    else
        echo "✅ All MCP processes stopped successfully"
        return 0
    fi
}

# Function to clean Python cache
clean_python_cache() {
    echo "🧹 Cleaning Python cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    echo "✅ Python cache cleaned"
}

# Function to clean log files (optional)
clean_logs() {
    echo "📋 Cleaning old log files..."
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        echo "✅ Old log files cleaned"
    fi
}

# Function to restart MCP server
restart_mcp_server() {
    echo "🚀 Starting MCP server..."
    python3 -m srrd_builder.server.launcher &
    local server_pid=$!
    echo "Started MCP server with PID: $server_pid"
    
    # Wait a moment and check if server started successfully
    sleep 2
    if kill -0 $server_pid 2>/dev/null; then
        echo "✅ MCP server started successfully"
        return 0
    else
        echo "❌ MCP server failed to start"
        return 1
    fi
}

# Main execution
main() {
    echo "Checking current MCP processes..."
    check_mcp_processes
    
    echo ""
    kill_mcp_processes
    
    echo ""
    clean_python_cache
    
    echo ""
    clean_logs
    
    echo ""
    if [ "$1" != "--no-restart" ]; then
        restart_mcp_server
        echo ""
        echo "🎯 Clean restart completed!"
        echo "Use 'ps aux | grep srrd_builder.server.launcher' to verify server status"
    else
        echo "🎯 Cleanup completed (no restart requested)"
    fi
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [--no-restart] [--help]"
        echo ""
        echo "Options:"
        echo "  --no-restart    Clean up processes but don't restart server"
        echo "  --help, -h      Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
