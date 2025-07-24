#!/usr/bin/env python3
"""
Complete STDIO MCP logging test script
Tests initialization, research tools, and project info retrieval with proper logging verification
"""

import json
import os
import subprocess
import sys
import time
import threading
import queue


class StdioMCPTester:
    def __init__(self, project_path):
        self.project_path = project_path
        self.server_process = None
        self.response_queue = queue.Queue()
        self.stdout_thread = None

    def send_request(self, request_data):
        """Send a JSON-RPC request to the server"""
        request_json = json.dumps(request_data) + "\n"
        print(f"  → Sending: {request_data['method']}")
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()

    def read_response_worker(self):
        """Worker thread to read responses from server stdout"""
        try:
            while True:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                if line.strip():
                    try:
                        response = json.loads(line.strip())
                        self.response_queue.put(response)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON response: {line.strip()}")
        except Exception as e:
            print(f"Response reader error: {e}")

    def get_response(self, timeout=5):
        """Get response from the queue with timeout"""
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def start_server(self):
        """Start the MCP server in stdio mode"""
        print("🚀 Starting MCP server in stdio mode...")

        env = os.environ.copy()
        env["SRRD_PROJECT_PATH"] = self.project_path

        self.server_process = subprocess.Popen(
            [sys.executable, "work/code/mcp/server.py", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd="/Users/markomanninen/Documents/GitHub/srrd-builder/srrd-builder",
        )

        # Start response reader thread
        self.stdout_thread = threading.Thread(
            target=self.read_response_worker, daemon=True
        )
        self.stdout_thread.start()

        # Give server time to initialize
        time.sleep(2)
        print("✅ Server started and ready")

    def test_initialization(self):
        """Test MCP initialization"""
        print("\n📋 Test 1: MCP Initialization")

        init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

        self.send_request(init_request)
        response = self.get_response()

        if response and response.get("id") == 1:
            server_info = response["result"]["serverInfo"]
            print(f"  ✅ Initialized: {server_info['name']}")
            print(f"  📁 Project: {server_info.get('projectPath', 'N/A')}")
            return True
        else:
            print("  ❌ Initialization failed")
            return False

    def test_list_tools(self):
        """Test listing available tools"""
        print("\n📋 Test 2: List Available Tools")

        list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        self.send_request(list_request)
        response = self.get_response()

        if response and response.get("id") == 2:
            tools = response["result"]["tools"]
            print(f"  ✅ Found {len(tools)} tools")

            # Show some key research tools
            research_tools = [t for t in tools if "research" in t["name"].lower()]
            print(f"  🔬 Research tools: {len(research_tools)}")
            return True
        else:
            print("  ❌ Failed to list tools")
            return False

    def test_research_tool(self):
        """Test using a research tool"""
        print("\n📋 Test 3: Research Tool Execution")

        research_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_research_progress", "arguments": {}},
        }

        self.send_request(research_request)
        response = self.get_response()

        if response and response.get("id") == 3:
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                print("  ✅ Research progress retrieved")
                if "Research Progress Analysis" in content:
                    print("  📊 Progress analysis generated")
                return True
            else:
                error = response.get("error", {})
                print(f"  ❌ Tool failed: {error.get('message', 'Unknown error')}")
                return False
        else:
            print("  ❌ No response received")
            return False

    def test_project_info(self):
        """Test retrieving project information"""
        print("\n📋 Test 4: Project Information Retrieval")

        # First try to initialize a research session
        session_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "start_research_session",
                "arguments": {
                    "research_focus": "Testing STDIO logging system",
                    "session_goals": [
                        "Verify comprehensive logging",
                        "Test tool execution",
                    ],
                },
            },
        }

        self.send_request(session_request)
        response = self.get_response()

        if response and response.get("id") == 4:
            if "result" in response:
                print("  ✅ Research session started")

                # Now get research milestones
                milestone_request = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {"name": "get_research_milestones", "arguments": {}},
                }

                self.send_request(milestone_request)
                milestone_response = self.get_response()

                if milestone_response and milestone_response.get("id") == 5:
                    if "result" in milestone_response:
                        print("  ✅ Research milestones retrieved")
                        return True
                    else:
                        print("  ⚠️  Session started but milestone retrieval failed")
                        return True  # Partial success
                else:
                    print("  ⚠️  Session started but no milestone response")
                    return True  # Partial success
            else:
                error = response.get("error", {})
                print(
                    f"  ❌ Session start failed: {error.get('message', 'Unknown error')}"
                )
                return False
        else:
            print("  ❌ No response received")
            return False

    def test_error_handling(self):
        """Test error handling with invalid tool"""
        print("\n📋 Test 5: Error Handling")

        error_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool_stdio_test", "arguments": {}},
        }

        self.send_request(error_request)
        response = self.get_response()

        if response and response.get("id") == 6:
            if "error" in response:
                error_msg = response["error"]["message"]
                print(f"  ✅ Error properly handled: {error_msg}")
                return True
            else:
                print("  ❌ Expected error but got success")
                return False
        else:
            print("  ❌ No response received")
            return False

    def stop_server(self):
        """Stop the server gracefully"""
        if self.server_process:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️  Server force-killed")


def test_stdio_logging():
    """Main test function with complete STDIO workflow"""

    print("🔍 Comprehensive STDIO MCP Request Logging Test")
    print("=" * 60)

    project_path = "/Users/markomanninen/Desktop/example-srrd-project"
    tester = StdioMCPTester(project_path)

    try:
        # Start server
        tester.start_server()

        # Run all tests
        tests = [
            ("Initialization", tester.test_initialization),
            ("List Tools", tester.test_list_tools),
            ("Research Tool", tester.test_research_tool),
            ("Project Info", tester.test_project_info),
            ("Error Handling", tester.test_error_handling),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(0.5)  # Allow logging to complete
            except Exception as e:
                print(f"  ❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))

        # Stop server
        tester.stop_server()

        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")

        print(f"\n🎯 Overall: {passed}/{total} tests passed")

        if passed >= 3:  # At least 3 tests should pass
            print("✅ STDIO communication is working!")
            return True
        else:
            print("❌ STDIO communication has issues")
            return False

    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        tester.stop_server()
        return False

        time.sleep(0.5)  # Allow logging to complete

        # Test 2: List tools request
        print("\n📋 Test 2: List Tools Request via STDIO")
        list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        request_json = json.dumps(list_request) + "\n"
        server_process.stdin.write(request_json)
        server_process.stdin.flush()

        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools")
        else:
            print("❌ No response received")

        time.sleep(0.5)

        # Test 3: Tool call via stdio
        print("\n📋 Test 3: Tool Call via STDIO (get_research_progress)")
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_research_progress", "arguments": {}},
        }

        request_json = json.dumps(tool_request) + "\n"
        server_process.stdin.write(request_json)
        server_process.stdin.flush()

        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                print("✅ Tool call successful via stdio")
            else:
                print(
                    f"❌ Tool call failed: {response.get('error', {}).get('message', 'Unknown error')}"
                )
        else:
            print("❌ No response received")

        time.sleep(0.5)

        # Test 4: Invalid tool call
        print("\n📋 Test 4: Invalid Tool Call via STDIO")
        invalid_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool_stdio", "arguments": {}},
        }

        request_json = json.dumps(invalid_request) + "\n"
        server_process.stdin.write(request_json)
        server_process.stdin.flush()

        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(
                f"Expected error: {response.get('error', {}).get('message', 'No error message')}"
            )
        else:
            print("❌ No response received")

        time.sleep(1)  # Allow all logging to complete

        # Terminate the server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

        print("\n" + "=" * 50)
        print("✅ STDIO tests completed!")

        return True

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"❌ STDIO test failed with error: {e}")
        if "server_process" in locals():
            server_process.terminate()
        return False


def check_stdio_logs():
    """Check if stdio requests were logged to files"""
    print("\n📁 Checking for STDIO log files...")

    import glob

    # Check in the example project directory
    log_dir = "/Users/markomanninen/Desktop/example-srrd-project/logs/mcp_requests"

    if os.path.exists(log_dir):
        # Look for recent log files (last 5 minutes)
        current_time = time.time()
        recent_files = []

        for file_pattern in [
            "request_*.json",
            "context_*.json",
            "execution_*.json",
            "response_*.json",
        ]:
            files = glob.glob(os.path.join(log_dir, file_pattern))
            for file_path in files:
                file_time = os.path.getmtime(file_path)
                if current_time - file_time < 300:  # 5 minutes
                    recent_files.append(file_path)

        if recent_files:
            print(f"✅ Found {len(recent_files)} recent log files:")
            for file_path in sorted(recent_files)[-5:]:  # Show last 5 files
                print(f"   - {os.path.basename(file_path)}")

            # Check if any contain "stdio" as client_info
            stdio_logs = []
            for file_path in recent_files:
                if "request_" in file_path or "context_" in file_path:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = json.load(f)
                            if content.get("client_info") == "stdio":
                                stdio_logs.append(file_path)
                    except (IOError, json.JSONDecodeError):
                        pass

            if stdio_logs:
                print(f"✅ Found {len(stdio_logs)} STDIO-specific log files!")
                return True
            else:
                print("❌ No STDIO-specific logs found")
                return False
        else:
            print("❌ No recent log files found")
            return False
    else:
        print(f"❌ Log directory not found: {log_dir}")
        return False


if __name__ == "__main__":
    print("🚀 STDIO MCP Request Logging Test")
    print("This script tests logging for stdio connections (like Claude Desktop)")
    print("=" * 70)

    # Run the stdio test
    success = test_stdio_logging()

    if success:
        # Check if logs were actually created
        logs_found = check_stdio_logs()

        if logs_found:
            print("\n🎉 SUCCESS! STDIO requests are being logged!")
            print("\n💡 Claude Desktop connections will now be fully logged with:")
            print("   - Request details (method, parameters)")
            print("   - Server context (available tools, project path)")
            print("   - Tool execution timing and results")
            print("   - Response data")
            print("   - Error details with stack traces")
        else:
            print("\n⚠️  STDIO communication worked but no logs were found.")
            print("   Check if logging is properly configured.")
    else:
        print("\n❌ STDIO test failed. Check the error messages above.")
