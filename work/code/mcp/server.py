#!/usr/bin/env python3
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
    def __init__(self, port=None, use_stdio=False):
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
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "SRRD Builder MCP Server",
                        "version": "1.0.0"
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
                    result = await self.tools[tool_name](**tool_args)
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
        
        async with websockets.serve(self.handle_mcp_message, config.server.host, self.port):
            print(f"SRRD Builder MCP Server running on ws://{config.server.host}:{self.port}")
            await asyncio.Future()  # run forever

    async def handle_mcp_message(self, websocket):
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
                                    "version": "1.0.0"
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
                                result = await self.tools[tool_name](**tool_args)
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

    async def list_tools_mcp(self):
        """Return list of available tools in MCP format"""
        tools_list = []
        
        # Define schema mappings for known tools
        tool_schemas = {
            "clarify_research_goals": {
                "description": "Clarify research objectives through Socratic questioning",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "research_area": {"type": "string"},
                        "initial_goals": {"type": "string"}, 
                        "experience_level": {"type": "string"},
                        "domain_specialization": {"type": "string"},
                        "novel_theory_mode": {"type": "boolean"}
                    },
                    "required": ["research_area", "initial_goals"]
                }
            },
            "suggest_methodology": {
                "description": "Recommend appropriate research methodologies",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "research_goals": {"type": "string"},
                        "domain": {"type": "string"},
                        "constraints": {"type": "object"},
                        "novel_theory_flag": {"type": "boolean"}
                    },
                    "required": ["research_goals", "domain"]
                }
            },
            "simulate_peer_review": {
                "description": "AI-powered peer review simulation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {"type": "object"},
                        "domain": {"type": "string"},
                        "review_type": {"type": "string"},
                        "novel_theory_mode": {"type": "boolean"}
                    },
                    "required": ["document_content", "domain"]
                }
            },
            "check_quality_gates": {
                "description": "Automated quality checks at each research phase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "research_content": {"type": "object"},
                        "phase": {"type": "string"},
                        "domain_standards": {"type": "object"},
                        "innovation_criteria": {"type": "object"}
                    },
                    "required": ["research_content", "phase", "domain_standards"]
                }
            },
            "semantic_search": {
                "description": "Perform semantic search across research documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "collection": {"type": "string"},
                        "limit": {"type": "integer"},
                        "similarity_threshold": {"type": "number"},
                        "project_path": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            "discover_patterns": {
                "description": "Discover patterns and themes in research content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "pattern_type": {"type": "string"},
                        "min_frequency": {"type": "integer"}
                    },
                    "required": ["content"]
                }
            },
            "build_knowledge_graph": {
                "description": "Build knowledge graph from research documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "documents": {"type": "array", "items": {"type": "string"}},
                        "relationship_types": {"type": "array", "items": {"type": "string"}},
                        "project_path": {"type": "string"}
                    },
                    "required": ["documents"]
                }
            },
            "find_similar_documents": {
                "description": "Find documents similar to the target document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_document": {"type": "string"},
                        "collection": {"type": "string"},
                        "similarity_threshold": {"type": "number"},
                        "max_results": {"type": "integer"},
                        "project_path": {"type": "string"}
                    },
                    "required": ["target_document"]
                }
            },
            "extract_key_concepts": {
                "description": "Extract key concepts from research text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "max_concepts": {"type": "integer"},
                        "concept_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["text"]
                }
            },
            "generate_research_summary": {
                "description": "Generate summary of research documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "documents": {"type": "array", "items": {"type": "string"}},
                        "summary_type": {"type": "string"},
                        "max_length": {"type": "integer"}
                    },
                    "required": ["documents"]
                }
            }
        }
        
        # Generate tool list from registered tools
        for tool_name in self.tools.keys():
            if tool_name in tool_schemas:
                tool_info = {
                    "name": tool_name,
                    "description": tool_schemas[tool_name]["description"],
                    "inputSchema": tool_schemas[tool_name]["inputSchema"]
                }
            else:
                # Fallback for tools without defined schemas
                tool_info = {
                    "name": tool_name,
                    "description": f"Tool: {tool_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            tools_list.append(tool_info)
        
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
                        "domain_standards": "object",
                        "innovation_criteria": "object (optional)"
                    }
                }
            ]
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SRRD Builder MCP Server')
    parser.add_argument('--stdio', action='store_true', help='Use stdio for Claude Desktop')
    parser.add_argument('--port', type=int, default=None, help='WebSocket port')
    
    args = parser.parse_args()
    
    server = MCPServer(port=args.port, use_stdio=args.stdio)
    asyncio.run(server.start_server())
