#!/usr/bin/env python3
"""
Simple MCP client for testing the SRRD-Builder MCP server
"""

import asyncio
import json
import websockets
import sys

class MCPTestClient:
    def __init__(self, server_url="ws://localhost:8080"):
        self.server_url = server_url
        self.websocket = None
    
    async def connect(self):
        """Connect to MCP server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"✅ Connected to MCP server at {self.server_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def send_command(self, command, payload=None):
        """Send command to MCP server"""
        if not self.websocket:
            print("❌ Not connected to server")
            return None
        
        message = {
            "command": command,
            "payload": payload or {}
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return None
    
    async def test_initialization(self):
        """Test server initialization"""
        print("\n🧪 Testing server initialization...")
        response = await self.send_command("initialize")
        if response and response.get("status") == "initialized":
            print("✅ Server initialized successfully")
            print(f"   Capabilities: {response.get('capabilities', [])}")
            return True
        else:
            print(f"❌ Initialization failed: {response}")
            return False
    
    async def test_list_tools(self):
        """Test tool listing"""
        print("\n🧪 Testing tool listing...")
        response = await self.send_command("list_tools")
        if response and "tools" in response:
            print("✅ Tools listed successfully:")
            for tool in response["tools"]:
                print(f"   - {tool['name']}: {tool['description']}")
            return True
        else:
            print(f"❌ Tool listing failed: {response}")
            return False
    
    async def test_research_planning_tool(self):
        """Test research planning tool"""
        print("\n🧪 Testing research planning tool...")
        
        payload = {
            "tool_name": "clarify_research_goals",
            "tool_args": {
                "research_area": "theoretical_physics",
                "initial_goals": "Develop alternative quantum gravity theory",
                "experience_level": "expert",
                "domain_specialization": "theoretical_physics",
                "novel_theory_mode": True
            }
        }
        
        response = await self.send_command("call_tool", payload)
        if response and "result" in response:
            result = response["result"]
            print("✅ Research planning tool executed successfully:")
            print(f"   Questions: {len(result.get('follow_up_questions', []))}")
            print(f"   Methodologies: {len(result.get('methodology_suggestions', []))}")
            print(f"   Novel theory guidance: {'Yes' if result.get('novel_theory_guidance') else 'No'}")
            return True
        else:
            print(f"❌ Research planning tool failed: {response}")
            return False
    
    async def test_quality_assurance_tool(self):
        """Test quality assurance tool"""
        print("\n🧪 Testing quality assurance tool...")
        
        payload = {
            "tool_name": "simulate_peer_review",
            "tool_args": {
                "document_content": {
                    "title": "Novel Quantum Gravity Approach",
                    "abstract": "This paper presents an alternative framework...",
                    "methodology": "Theoretical analysis with mathematical modeling"
                },
                "domain": "theoretical_physics",
                "novel_theory_mode": True
            }
        }
        
        response = await self.send_command("call_tool", payload)
        if response and "result" in response:
            result = response["result"]
            print("✅ Quality assurance tool executed successfully:")
            print(f"   Overall score: {result.get('overall_score', 0):.2f}")
            print(f"   Recommendations: {len(result.get('recommendations', []))}")
            print(f"   Novel theory evaluation: {'Yes' if result.get('novel_theory_evaluation') else 'No'}")
            return True
        else:
            print(f"❌ Quality assurance tool failed: {response}")
            return False
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from server")

async def run_tests(server_url="ws://localhost:8080"):
    """Run all MCP server tests"""
    client = MCPTestClient(server_url)
    
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)
    
    # Connect to server
    if not await client.connect():
        print("❌ Cannot proceed without server connection")
        return False
    
    try:
        # Run tests
        tests = [
            client.test_initialization(),
            client.test_list_tools(),
            client.test_research_planning_tool(),
            client.test_quality_assurance_tool()
        ]
        
        results = []
        for test in tests:
            result = await test
            results.append(result)
        
        # Summary
        passed = sum(results)
        total = len(results)
        print("\n" + "=" * 50)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! MCP server is functional.")
            return True
        else:
            print("⚠️  Some tests failed. Check implementation.")
            return False
            
    finally:
        await client.disconnect()

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("MCP Test Client")
        print("Usage: python test_client.py [server_url]")
        print("Default server URL: ws://localhost:8080")
        return
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8080"
    
    # Run tests
    success = asyncio.run(run_tests(server_url))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
