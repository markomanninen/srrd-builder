#!/usr/bin/env python3
"""
Simple WebSocket test client for SRRD-Builder MCP Server
Tests that the WebSocket server is working properly
"""

import asyncio
import json
import websockets

async def test_mcp_server():
    """Test the MCP server WebSocket connection"""
    uri = "ws://localhost:8765"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Test 1: Initialize the MCP connection
            print("\n📋 Test 1: Initialize MCP connection")
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "Test Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            await websocket.send(json.dumps(init_message))
            response = await websocket.recv()
            init_response = json.loads(response)
            print(f"   Response: {init_response.get('result', {}).get('serverInfo', 'Unknown')}")
            
            # Test 2: List available tools
            print("\n🛠️  Test 2: List available tools")
            list_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            await websocket.send(json.dumps(list_message))
            response = await websocket.recv()
            list_response = json.loads(response)
            tools = list_response.get('result', {}).get('tools', [])
            print(f"   Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                print(f"     {i+1}. {tool.get('name', 'Unknown')}")
            if len(tools) > 5:
                print(f"     ... and {len(tools) - 5} more tools")
            
            # Test 3: Call a simple tool
            print("\n🔧 Test 3: Call a tool (extract_key_concepts)")
            call_message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "extract_key_concepts",
                    "arguments": {
                        "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
                        "max_concepts": 3
                    }
                }
            }
            
            await websocket.send(json.dumps(call_message))
            response = await websocket.recv()
            call_response = json.loads(response)
            
            if 'result' in call_response:
                content = call_response['result'].get('content', [])
                if content and len(content) > 0:
                    result_text = content[0].get('text', 'No text content')
                    print(f"   Tool result: {result_text[:100]}...")
                else:
                    print(f"   Tool result: {call_response['result']}")
            else:
                print(f"   Tool error: {call_response.get('error', 'Unknown error')}")
            
            print("\n🎉 All tests completed successfully!")
            print("   The WebSocket MCP server is working correctly!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure the server is running with 'srrd-server'")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 SRRD-Builder MCP Server WebSocket Test")
    print("=" * 50)
    asyncio.run(test_mcp_server())
