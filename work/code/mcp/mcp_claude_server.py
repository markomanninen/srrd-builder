#!/usr/bin/env python3
"""
SRRD-Builder MCP Server for Claude Desktop
Provides stdio-based communication for Claude Desktop integration
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from tools import register_all_tools
from config.config_manager import config

class ClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        
        # Suppress all stdout output during initialization
        try:
            # Redirect stdout temporarily during setup
            original_stdout = sys.stdout
            sys.stdout = sys.stderr
            
            # Setup directories and validate config silently
            config.setup_directories()
            issues = config.validate_config()
            
            # Register tools
            self._register_tools()
            
            # Restore stdout
            sys.stdout = original_stdout
            
        except Exception as e:
            sys.stderr.write(f"MCP Server initialization error: {str(e)}\n")
            sys.stderr.flush()
            # Restore stdout in case of error
            sys.stdout = original_stdout
        
    def _register_tools(self):
        """Register MCP tools"""
        self.tools = {}
        
        # Temporarily redirect stdout to stderr during tool registration
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        
        try:
            register_all_tools(self)
        except Exception as e:
            sys.stderr.write(f"Tool registration error: {str(e)}\n")
            sys.stderr.flush()
        finally:
            # Always restore stdout
            sys.stdout = original_stdout

    async def handle_request(self, request_data):
        """Handle MCP request from Claude Desktop"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            msg_id = request_data.get("id")
            
            # Ensure id is always present and valid
            if msg_id is None:
                msg_id = 1
                
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "SRRD Builder MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif method == "notifications/initialized":
                # This is a notification, no response needed
                return None
                
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
                        # Redirect stdout during tool execution
                        original_stdout = sys.stdout
                        sys.stdout = sys.stderr
                        
                        result = await self.tools[tool_name](**tool_args)
                        
                        # Restore stdout
                        sys.stdout = original_stdout
                        
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
                        # Restore stdout in case of error
                        sys.stdout = original_stdout
                        
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
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

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
            "generate_latex_document": {
                "description": "Generate LaTeX research document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_type": {"type": "string"},
                        "content_data": {"type": "object"},
                        "template": {"type": "string"},
                        "output_path": {"type": "string"}
                    },
                    "required": ["document_type", "content_data"]
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
                    "description": f"Research tool: {tool_name.replace('_', ' ').title()}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            tools_list.append(tool_info)
        
        return {"tools": tools_list}

    async def run(self):
        """Run the MCP server using stdio for Claude Desktop"""
        # Send initial greeting to stderr for debugging
        sys.stderr.write("SRRD-Builder MCP Server starting for Claude Desktop...\n")
        sys.stderr.flush()
        
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                request_data = json.loads(line)
                response = await self.handle_request(request_data)
                
                # Only send response if not None (for notifications)
                if response is not None:
                    response_json = json.dumps(response)
                    # Send ONLY the JSON response to stdout - use sys.stdout.write to avoid any print overrides
                    sys.stdout.write(response_json + '\n')
                    sys.stdout.flush()
                
            except EOFError:
                break
            except json.JSONDecodeError as e:
                # Send error response for malformed JSON
                error_response = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
                sys.stderr.write(f"JSON Parse error: {str(e)}\n")
                sys.stderr.flush()
            except Exception as e:
                # Send error response for other exceptions
                error_response = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
                sys.stderr.write(f"Server error: {str(e)}\n")
                sys.stderr.flush()

if __name__ == "__main__":
    server = ClaudeMCPServer()
    asyncio.run(server.run())
