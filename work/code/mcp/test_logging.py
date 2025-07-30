#!/usr/bin/env python3
"""
Test script to demonstrate the new comprehensive MCP request logging system
"""

import asyncio
import json
import time
from datetime import datetime

import websockets


async def test_mcp_logging():
    """Test the comprehensive logging by sending various MCP requests"""

    print("🔍 Testing MCP Request Logging System")
    print("=" * 50)

    # Connect to the MCP server
    try:
        uri = "ws://localhost:8080"
        print(f"Connecting to {uri}...")

        # Connect with MCP subprotocol as required by the server
        async with websockets.connect(uri, subprotocols=["mcp"]) as websocket:
            print("✅ Connected to MCP server")

            # Test 1: Initialize request
            print("\n📋 Test 1: Initialize Request")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            }

            await websocket.send(json.dumps(init_request))
            response = await websocket.recv()
            print(f"Response: {json.loads(response)['result']['serverInfo']['name']}")

            # Wait a moment for logging to complete
            await asyncio.sleep(0.5)

            # Test 2: List tools request
            print("\n📋 Test 2: List Tools Request")
            list_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }

            await websocket.send(json.dumps(list_request))
            response = await websocket.recv()
            tools = json.loads(response)["result"]["tools"]
            print(f"Found {len(tools)} tools")

            await asyncio.sleep(0.5)

            # Test 3: Valid tool call
            print("\n📋 Test 3: Valid Tool Call (initialize_project)")
            tool_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "initialize_project",
                    "arguments": {
                        "name": "Test Logging Project",
                        "description": "A test project to demonstrate logging",
                        "domain": "Computer Science",
                    },
                },
            }

            await websocket.send(json.dumps(tool_request))
            response = await websocket.recv()
            result = json.loads(response)
            if "result" in result:
                print("✅ Tool call successful")
            else:
                print(
                    f"❌ Tool call failed: {result.get('error', {}).get('message', 'Unknown error')}"
                )

            await asyncio.sleep(0.5)

            # Test 4: Invalid tool call
            print("\n📋 Test 4: Invalid Tool Call")
            invalid_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "nonexistent_tool", "arguments": {}},
            }

            await websocket.send(json.dumps(invalid_request))
            response = await websocket.recv()
            result = json.loads(response)
            print(
                f"Expected error: {result.get('error', {}).get('message', 'No error message')}"
            )

            await asyncio.sleep(0.5)

            # Test 5: Tool call with error
            print("\n📋 Test 5: Tool Call with Missing Parameters")
            error_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "initialize_project",
                    "arguments": {
                        # Missing required parameters to trigger an error
                    },
                },
            }

            await websocket.send(json.dumps(error_request))
            response = await websocket.recv()
            result = json.loads(response)
            if "error" in result:
                print(f"Expected error: {result['error']['message']}")
            else:
                print("Unexpected success")

            await asyncio.sleep(0.5)

    except ConnectionRefusedError:
        print(
            "❌ Could not connect to MCP server. Make sure it's running on localhost:8080"
        )
        print("   Run: python -m work.code.mcp.server")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📁 Check the logs directory for detailed request logs:")
    print("   - Request files: request_TIMESTAMP.json")
    print("   - Context files: context_TIMESTAMP.json")
    print("   - Execution files: execution_TIMESTAMP.json")
    print("   - Response files: response_TIMESTAMP.json")
    print("   - Summary files: summary_TIMESTAMP.json")
    return True


def show_log_directory_info():
    """Show information about where to find the logs"""
    print("\n📂 Log File Locations:")
    print("=" * 30)
    print("🔍 Logs are stored in project-specific directories:")
    print("   ~/Projects/default/logs/mcp_requests/  (when no project is active)")
    print("   [PROJECT_PATH]/logs/mcp_requests/         (when in a specific project)")
    print("\n📋 Log File Types:")
    print("   • mcp_requests.log          - General activity log")
    print("   • request_[TIMESTAMP].json  - Incoming request details")
    print("   • context_[TIMESTAMP].json  - Server context during processing")
    print("   • execution_[TIMESTAMP].json - Tool execution details")
    print("   • response_[TIMESTAMP].json  - Outgoing response details")
    print("   • summary_[TIMESTAMP].json   - Summary linking all related files")
    print("\n🕒 Timestamp format: YYYYMMDD_HHMMSS_microseconds")
    print("💡 Each MCP request gets a unique timestamp for easy tracking")


if __name__ == "__main__":
    print("🚀 MCP Request Logging Test")
    print("This script tests the comprehensive logging system")
    print("Make sure the MCP server is running before starting the test\n")

    show_log_directory_info()

    # Ask user if they want to proceed
    try:
        input("\nPress Enter to start the test, or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
        exit(0)

    # Run the test
    success = asyncio.run(test_mcp_logging())

    if success:
        print("\n💡 Tip: You can now examine the generated log files to see")
        print("   detailed information about each MCP request and response!")
    else:
        print("\n❌ Test failed. Check the error messages above.")
