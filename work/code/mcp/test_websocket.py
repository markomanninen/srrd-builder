#!/usr/bin/env python3
"""
WebSocket Test Client for MCP Server
Tests the WebSocket connection from the command line
"""

import asyncio
import websockets
import json
import sys

async def test_mcp_connection():
    """Test WebSocket connection to MCP server"""
    uri = "ws://localhost:8083"
    
    try:
        print("🔌 Connecting to MCP server...")
        
        # Connect with proper WebSocket protocol
        async with websockets.connect(uri, subprotocols=['mcp']) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send MCP initialization
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {
                        "name": "WebSocket Test Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("📤 Sending initialization message...")
            await websocket.send(json.dumps(init_message))
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print("📥 Received response:")
            print(json.dumps(response_data, indent=2))
            
            # Test tool listing
            list_tools_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            print("\n📤 Requesting tool list...")
            await websocket.send(json.dumps(list_tools_message))
            
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print("📥 Available tools:")
            if 'result' in response_data and 'tools' in response_data['result']:
                tools = response_data['result']['tools']
                for i, tool in enumerate(tools, 1):
                    print(f"  {i}. {tool.get('name', 'Unknown')}")
                print(f"\n✅ Found {len(tools)} tools")
            else:
                print("❌ No tools found in response")
                print(json.dumps(response_data, indent=2))
            
            print("\n🎉 WebSocket connection test completed successfully!")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except websockets.exceptions.InvalidHandshake as e:
        print(f"❌ Invalid handshake: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🧪 MCP Server WebSocket Connection Test")
    print("=" * 50)
    
    success = await test_mcp_connection()
    
    if success:
        print("\n✅ All tests passed! WebSocket connection is working correctly.")
        print("🌐 Frontend interface should now be able to connect successfully.")
        sys.exit(0)
    else:
        print("\n❌ Connection test failed!")
        print("💡 Make sure the MCP server is running: python3 run_server.py")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
