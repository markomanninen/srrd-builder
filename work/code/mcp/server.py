import asyncio
import json
import websockets
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from tools import register_all_tools
from config.config_manager import config
from utils.logging_setup import setup_logging, MCPLoggerAdapter

class MCPServer:
    def __init__(self, port=None):
        self.port = port or config.server.port
        self.tools = {}
        self.storage_manager = None
        self.session_manager = None
        
        # Setup logging
        if config.server.enable_logging:
            self.logger = setup_logging(
                log_level=config.server.log_level,
                log_file=config.server.log_file,
                enable_console=True
            )
            self.log_adapter = MCPLoggerAdapter(self.logger, "mcp_server")
        else:
            self.logger = None
            self.log_adapter = None
        
        # Setup directories and validate config
        config.setup_directories()
        issues = config.validate_config()
        if issues and self.logger:
            for issue in issues:
                self.logger.warning(f"Configuration issue: {issue}")
        
        self._register_tools()
        
        if self.logger:
            self.logger.info(f"MCP Server initialized on port {self.port}")
            self.logger.info(f"Registered {len(self.tools)} tools")

    async def start_server(self):
        if self.logger:
            self.logger.info(f"Starting MCP server on {config.server.host}:{self.port}")
        
        async with websockets.serve(self.handle_mcp_message, config.server.host, self.port):
            print(f"SRRD Builder MCP Server running on ws://{config.server.host}:{self.port}")
            await asyncio.Future()  # run forever

    async def handle_mcp_message(self, websocket):
        """Handle incoming WebSocket messages"""
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")
                payload = data.get("payload")

                if command == "initialize":
                    if self.log_adapter:
                        self.log_adapter.log_tool_call("initialize", {}, "Server initialized")
                    await websocket.send(json.dumps({
                        "status": "initialized", 
                        "capabilities": ["tools", "resources"],
                        "server_info": {
                            "name": "SRRD Builder MCP Server",
                            "version": "1.0.0",
                            "tools_count": len(self.tools)
                        }
                    }))
                elif command == "list_tools":
                    tools_info = await self.list_tools()
                    await websocket.send(json.dumps(tools_info))
                elif command == "call_tool":
                    tool_name = payload.get("tool_name")
                    tool_args = payload.get("tool_args", {})
                    
                    if self.log_adapter:
                        self.log_adapter.log_tool_call(tool_name, tool_args)
                    
                    if tool_name in self.tools:
                        try:
                            result = await self.tools[tool_name](**tool_args)
                            if self.log_adapter:
                                self.log_adapter.log_tool_call(tool_name, tool_args, result)
                            await websocket.send(json.dumps({"result": result}))
                        except Exception as e:
                            error_msg = f"Tool execution error: {str(e)}"
                            if self.log_adapter:
                                self.log_adapter.log_tool_call(tool_name, tool_args, error=error_msg)
                            await websocket.send(json.dumps({"error": error_msg}))
                    else:
                        error_msg = f"Tool '{tool_name}' not found"
                        if self.log_adapter:
                            self.log_adapter.log_tool_call(tool_name, tool_args, error=error_msg)
                        await websocket.send(json.dumps({"error": error_msg}))
                else:
                    await websocket.send(json.dumps({"error": "Unknown command"}))
            except Exception as e:
                error_msg = f"Message handling error: {str(e)}"
                if self.logger:
                    self.logger.error(error_msg)
                await websocket.send(json.dumps({"error": error_msg}))

    def _register_tools(self):
        """Register MCP tools"""
        self.tools = {}
        register_all_tools(self)

    async def list_tools(self):
        """Return list of available tools"""
        return {
            "tools": [
                {
                    "name": "clarify_research_goals",
                    "description": "Clarify research objectives through Socratic questioning",
                    "parameters": {
                        "research_area": "string",
                        "initial_goals": "string", 
                        "experience_level": "string (optional)",
                        "domain_specialization": "string (optional)",
                        "novel_theory_mode": "boolean (optional)"
                    }
                },
                {
                    "name": "suggest_methodology",
                    "description": "Recommend appropriate research methodologies",
                    "parameters": {
                        "research_goals": "string",
                        "domain": "string",
                        "constraints": "object (optional)",
                        "novel_theory_flag": "boolean (optional)"
                    }
                },
                {
                    "name": "simulate_peer_review", 
                    "description": "AI-powered peer review simulation",
                    "parameters": {
                        "document_content": "object",
                        "domain": "string",
                        "review_type": "string (optional)",
                        "novel_theory_mode": "boolean (optional)"
                    }
                },
                {
                    "name": "check_quality_gates",
                    "description": "Automated quality checks at each research phase",
                    "parameters": {
                        "research_content": "object",
                        "phase": "string",
                        "domain_standards": "object",
                        "innovation_criteria": "object (optional)"
                    }
                }
            ]
        }

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.start_server())
