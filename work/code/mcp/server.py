import asyncio
import json
import websockets

class MCPServer:
    def __init__(self, port=8080):
        self.port = port
        self.tools = {}
        self.storage_manager = None
        self.session_manager = None

    async def start_server(self):
        async with websockets.serve(self.handle_mcp_message, "localhost", self.port):
            await asyncio.Future()  # run forever

    async def handle_mcp_message(self, websocket, path):
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")
                payload = data.get("payload")

                if command == "initialize":
                    await websocket.send(json.dumps({"status": "initialized"}))
                elif command == "list_tools":
                    await websocket.send(json.dumps({"tools": list(self.tools.keys())}))
                elif command == "call_tool":
                    tool_name = payload.get("tool_name")
                    tool_args = payload.get("tool_args")
                    if tool_name in self.tools:
                        result = await self.tools[tool_name](**tool_args)
                        await websocket.send(json.dumps({"result": result}))
                    else:
                        await websocket.send(json.dumps({"error": "Tool not found"}))
                else:
                    await websocket.send(json.dumps({"error": "Unknown command"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.start_server())
