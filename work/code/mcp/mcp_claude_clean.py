#!/usr/bin/env python3
"""
SRRD-Builder MCP Server for Claude Desktop - Clean Version
Minimal version with no debug output to avoid JSON parsing issues
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Suppress all warnings and debug output
import warnings
warnings.filterwarnings('ignore')

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import with output suppression
class NullWriter:
    def write(self, txt): pass
    def flush(self): pass

original_stderr = sys.stderr
sys.stderr = NullWriter()

try:
    from tools import register_all_tools
    from config.config_manager import config
finally:
    sys.stderr = original_stderr

class ClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        
        # Silent initialization
        original_stderr = sys.stderr
        original_stdout = sys.stdout
        sys.stderr = NullWriter()
        sys.stdout = NullWriter()
        
        try:
            config.setup_directories()
            config.validate_config()
            self._register_tools()
        except:
            pass
        finally:
            sys.stderr = original_stderr
            sys.stdout = original_stdout
        
    def _register_tools(self):
        """Register MCP tools"""
        self.tools = {}
        register_all_tools(self)

    async def handle_request(self, request_data):
        """Handle MCP request from Claude Desktop"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            msg_id = request_data.get("id", 1)
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "SRRD Builder MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif method == "notifications/initialized":
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
                        # Suppress tool output
                        original_stderr = sys.stderr
                        original_stdout = sys.stdout
                        sys.stderr = NullWriter()
                        sys.stdout = NullWriter()
                        
                        result = await self.tools[tool_name](**tool_args)
                        
                        sys.stderr = original_stderr
                        sys.stdout = original_stdout
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "content": [{"type": "text", "text": str(result)}]
                            }
                        }
                    except Exception as e:
                        sys.stderr = original_stderr
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
        
        for tool_name in self.tools.keys():
            if tool_name in tool_schemas:
                tool_info = {
                    "name": tool_name,
                    "description": tool_schemas[tool_name]["description"],
                    "inputSchema": tool_schemas[tool_name]["inputSchema"]
                }
            else:
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
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                request_data = json.loads(line)
                response = await self.handle_request(request_data)
                
                if response is not None:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()
                
            except EOFError:
                break
            except:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32603,
                        "message": "Internal server error"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()

if __name__ == "__main__":
    server = ClaudeMCPServer()
    asyncio.run(server.run())
