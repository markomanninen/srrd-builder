#!/usr/bin/env python3
import asyncio
import json
import websockets
import sys
import os
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import PROJECT_PATH from the launcher module
try:
    sys.path.insert(0, str(current_dir.parent.parent.parent / 'srrd_builder'))
    from mcp_global_launcher import PROJECT_PATH
except ImportError:
    PROJECT_PATH = None

# Import tools and utilities with fallback error handling
try:
    from tools import register_all_tools
except ImportError:
    def register_all_tools(server):
        pass

try:
    from utils.logging_setup import setup_logging, MCPLoggerAdapter
except ImportError:
    # Fallback logging if utils.logging_setup is not available
    import logging
    def setup_logging(*args, **kwargs):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    class MCPLoggerAdapter:
        def __init__(self, logger, prefix):
            self.logger = logger
            self.prefix = prefix
        
        def log_tool_call(self, tool_name, args, result=None, error=None):
            if error:
                self.logger.error(f"{self.prefix}: {tool_name} failed - {error}")
            else:
                self.logger.info(f"{self.prefix}: {tool_name} called")

# ConfigManager will be initialized later in __init__ to allow environment variables to be set first
config = None

class MCPServer:
    def __init__(self, port=None, use_stdio=False):
        # Initialize ConfigManager here to allow environment variables to be set first
        global config
        if config is None:
            try:
                from config.config_manager import ConfigManager
                config = ConfigManager()
            except ImportError:
                # Fallback config if config_manager is not available
                class FallbackConfig:
                    def __init__(self):
                        self.server = type('ServerConfig', (), {
                            'port': 8765,
                            'host': 'localhost',
                            'enable_logging': True,
                            'log_level': 'INFO',
                            'log_file': None
                        })()
                    
                    def setup_directories(self):
                        pass
                    
                    def validate_config(self):
                        return []
                
                config = FallbackConfig()
        
        self.port = port or config.server.port
        self.use_stdio = use_stdio
        self.tools = {}
        self.storage_manager = None
        self.session_manager = None
        
        # Setup logging
        if config.server.enable_logging and not use_stdio:
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
            self.logger.info(f"PROJECT_PATH: {PROJECT_PATH}")

    async def start_stdio_server(self):
        """Start MCP server using stdio for Claude Desktop"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if not line:
                    break
                    
                data = json.loads(line)
                response = await self.handle_mcp_request(data)
                print(json.dumps(response), flush=True)
                
            except EOFError:
                break
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id") if 'data' in locals() else None,
                    "error": {
                        "code": -32000,
                        "message": f"Server error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

    async def handle_mcp_request(self, data):
        """Handle MCP request and return response"""
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "SRRD Builder MCP Server",
                        "version": "1.0.0",
                        "projectPath": PROJECT_PATH or os.getcwd()
                    }
                }
            }
            
        elif method == "tools/list":
            tools_info = await self.list_tools_mcp()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": tools_info
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name in self.tools:
                try:
                    # Call the handler function from the tool dict
                    handler = self.tools[tool_name]['handler']
                    result = await handler(**tool_args)
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32000,
                            "message": f"Tool execution error: {str(e)}"
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    async def start_server(self):
        if self.use_stdio:
            await self.start_stdio_server()
            return
            
        if self.logger:
            self.logger.info(f"Starting MCP server on {config.server.host}:{self.port}")
        
        # Create a proper handler function
        async def websocket_handler(websocket):
            return await self.handle_mcp_message(websocket, "/")
        
        async with websockets.serve(
            websocket_handler,
            config.server.host, 
            self.port
        ):
            self.logger.info(f"SRRD Builder MCP Server running on ws://{config.server.host}:{self.port}")
            await asyncio.Future()  # run forever

    async def handle_mcp_message(self, websocket, path):
        """Handle incoming WebSocket messages using MCP JSON-RPC protocol"""
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Handle JSON-RPC format
                if "method" in data:
                    method = data.get("method")
                    params = data.get("params", {})
                    msg_id = data.get("id")
                    
                    if method == "initialize":
                        if self.log_adapter:
                            self.log_adapter.log_tool_call("initialize", params, "Server initialized")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {
                                        "listChanged": False
                                    }
                                },
                                "serverInfo": {
                                    "name": "SRRD Builder MCP Server",
                                    "version": "1.0.0",
                                    "projectPath": PROJECT_PATH or os.getcwd()
                                }
                            }
                        }
                        
                        await websocket.send(json.dumps(response))
                        
                    elif method == "tools/list":
                        tools_info = await self.list_tools_mcp()
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": tools_info
                        }
                        await websocket.send(json.dumps(response))
                        
                    elif method == "tools/call":
                        tool_name = params.get("name")
                        tool_args = params.get("arguments", {})
                        
                        if self.log_adapter:
                            self.log_adapter.log_tool_call(tool_name, tool_args)
                        
                        if tool_name in self.tools:
                            try:
                                result = await self.tools[tool_name]['handler'](**tool_args)
                                if self.log_adapter:
                                    self.log_adapter.log_tool_call(tool_name, tool_args, result)
                                
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": msg_id,
                                    "result": {
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": str(result)
                                            }
                                        ]
                                    }
                                }
                                await websocket.send(json.dumps(response))
                            except Exception as e:
                                error_msg = f"Tool execution error: {str(e)}"
                                if self.log_adapter:
                                    self.log_adapter.log_tool_call(tool_name, tool_args, error=error_msg)
                                
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": msg_id,
                                    "error": {
                                        "code": -32000,
                                        "message": error_msg
                                    }
                                }
                                await websocket.send(json.dumps(response))
                        else:
                            error_msg = f"Tool '{tool_name}' not found"
                            response = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "error": {
                                    "code": -32601,
                                    "message": error_msg
                                }
                            }
                            await websocket.send(json.dumps(response))
                    else:
                        # Unknown method
                        response = {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                        await websocket.send(json.dumps(response))
                
                # Handle legacy format for backward compatibility
                else:
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

    def register_tool(self, name, description, parameters, handler):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            'description': description,
            'parameters': parameters,
            'handler': handler
        }
        if self.logger:
            self.logger.info(f"Registered tool: {name}")

    async def list_tools_mcp(self):
        """Return list of available tools in MCP format - USING REAL REGISTERED SCHEMAS"""
        tools_list = []
        
        # Generate tool list from ACTUALLY registered tools (no more hardcoded schemas!)
        for tool_name, tool_data in self.tools.items():
            tool_info = {
                "name": tool_name,
                "description": tool_data.get("description", f"Tool: {tool_name}"),
                "inputSchema": tool_data.get("parameters", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            }
            tools_list.append(tool_info)
        
        if self.logger:
            self.logger.info(f"✅ Listed {len(tools_list)} tools")
        
        return {"tools": tools_list}

    async def list_tools(self):
        """Return list of available tools (legacy format)"""
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
                        "domain_standards": "object (optional)",
                        "innovation_criteria": "object (optional)"
                    }
                }
            ]
        }

    async def _websocket_handler(self, websocket, path=None):
        """WebSocket handler wrapper - compatible with different websockets versions"""
        # Some websockets versions pass path, others don't
        return await self.handle_mcp_message(websocket, path or "/")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SRRD Builder MCP Server')
    parser.add_argument('--stdio', action='store_true', help='Use stdio for Claude Desktop')
    parser.add_argument('--port', type=int, default=None, help='WebSocket port')
    
    args = parser.parse_args()
    
    server = MCPServer(port=args.port, use_stdio=args.stdio)
    asyncio.run(server.start_server())
