#!/bin/bash
# SRRD Builder MCP Server Management Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MCP_SERVER="$SCRIPT_DIR/mcp_server.py"

case "$1" in
    "test")
        echo "Testing MCP server in stdio mode..."
        echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python3 "$MCP_SERVER" --stdio
        ;;
    "tools")
        echo "Listing available tools..."
        echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python3 "$MCP_SERVER" --stdio
        ;;
    "websocket")
        echo "Starting WebSocket server on port 8083..."
        python3 "$SCRIPT_DIR/server.py"
        ;;
    "stdio")
        echo "Starting MCP server in stdio mode (for VS Code)..."
        python3 "$MCP_SERVER" --stdio
        ;;
    *)
        echo "SRRD Builder MCP Server Management"
        echo "Usage: $0 {test|tools|websocket|stdio}"
        echo ""
        echo "Commands:"
        echo "  test      - Test MCP server initialization"
        echo "  tools     - List all available tools"
        echo "  websocket - Start WebSocket server for GUI"
        echo "  stdio     - Start stdio server for VS Code"
        ;;
esac
