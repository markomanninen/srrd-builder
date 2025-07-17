#!/usr/bin/env python3
"""
SRRD-Builder MCP Server for Claude Desktop
Model Context Protocol server providing 24 research assistance tools
Version: UPDATED_20250717_1834
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from tools import register_all_tools

class ClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        self._register_tools()
        
    def _register_tools(self):
        """Register MCP tools using the standard registration system"""
    def _register_tools(self):
        """Register MCP tools using the standard registration system"""
        # Use the existing registration system from tools module
        register_all_tools(self)
    
    def register_tool(self, name, description, parameters, handler):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            'description': description,
            'parameters': parameters,
            'handler': handler
        }

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
                tools_info = self.list_tools_mcp()
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
                                "content": [{"type": "text", "text": str(result)}]
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
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    def list_tools_mcp(self):
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
                        "document_content": {"type": "object", "description": "Document content to review"},
                        "domain": {"type": "string", "description": "Research domain"},
                        "review_type": {"type": "string", "description": "Type of review"},
                        "novel_theory_mode": {"type": "boolean", "description": "Novel theory mode flag"}
                    },
                    "required": ["document_content", "domain"]
                }
            },
            "check_quality_gates": {
                "description": "Check research quality gates and standards",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "research_content": {"type": "object", "description": "Research content to check"},
                        "phase": {"type": "string", "description": "Research phase (planning, execution, analysis, writing)"},
                        "domain_standards": {"type": "object", "description": "Domain-specific quality standards"},
                        "innovation_criteria": {"type": "object", "description": "Innovation criteria (optional)"}
                    },
                    "required": ["research_content", "phase"]
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
                        "title": {"type": "string", "description": "Document title"},
                        "author": {"type": "string", "description": "Author name"},
                        "abstract": {"type": "string", "description": "Abstract content"},
                        "introduction": {"type": "string", "description": "Introduction section"},
                        "methodology": {"type": "string", "description": "Methodology section"},
                        "results": {"type": "string", "description": "Results section"},
                        "discussion": {"type": "string", "description": "Discussion section"},
                        "conclusion": {"type": "string", "description": "Conclusion section"},
                        "bibliography": {"type": "string", "description": "Bibliography content"},
                        "project_path": {"type": "string", "description": "Project path for saving"}
                    },
                    "required": ["title"]
                }
            },
            "compile_latex": {
                "description": "Compile LaTeX document to PDF",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tex_file_path": {"type": "string", "description": "Path to .tex file"},
                        "output_format": {"type": "string", "description": "Output format (pdf)"}
                    },
                    "required": ["tex_file_path"]
                }
            },
            "format_research_content": {
                "description": "Format research content according to academic standards",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to format"},
                        "content_type": {"type": "string", "description": "Type of content (section, equation, citation)"},
                        "formatting_style": {"type": "string", "description": "Formatting style (academic)"}
                    },
                    "required": ["content"]
                }
            },
            "generate_bibliography": {
                "description": "Generate LaTeX bibliography from reference list",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "references": {"type": "array", "items": {"type": "object"}, "description": "List of references"}
                    },
                    "required": ["references"]
                }
            },
            "extract_document_sections": {
                "description": "Extract and identify sections from document content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {"type": "string", "description": "Document content to analyze"}
                    },
                    "required": ["document_content"]
                }
            },
            "discover_patterns": {
                "description": "Discover patterns and themes in research content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to analyze"},
                        "pattern_type": {"type": "string", "description": "Type of patterns to discover"},
                        "min_frequency": {"type": "integer", "description": "Minimum frequency threshold"}
                    },
                    "required": ["content"]
                }
            },
            "build_knowledge_graph": {
                "description": "Build knowledge graph from research documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "documents": {"type": "array", "items": {"type": "string"}, "description": "List of documents"},
                        "relationship_types": {"type": "array", "items": {"type": "string"}, "description": "Types of relationships"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["documents"]
                }
            },
            "find_similar_documents": {
                "description": "Find documents similar to target document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_document": {"type": "string", "description": "Target document content"},
                        "collection": {"type": "string", "description": "Collection to search"},
                        "similarity_threshold": {"type": "number", "description": "Similarity threshold"},
                        "max_results": {"type": "integer", "description": "Maximum results"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["target_document"]
                }
            },
            "extract_key_concepts": {
                "description": "Extract key concepts from research text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"},
                        "max_concepts": {"type": "integer", "description": "Maximum concepts to extract"},
                        "concept_types": {"type": "array", "items": {"type": "string"}, "description": "Types of concepts"}
                    },
                    "required": ["text"]
                }
            },
            "generate_research_summary": {
                "description": "Generate summary of research documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "documents": {"type": "array", "items": {"type": "string"}, "description": "Documents to summarize"},
                        "summary_type": {"type": "string", "description": "Type of summary"},
                        "max_length": {"type": "integer", "description": "Maximum summary length"}
                    },
                    "required": ["documents"]
                }
            },
            "initialize_project": {
                "description": "Initialize a new research project with Git-based storage",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"},
                        "description": {"type": "string", "description": "Project description"},
                        "domain": {"type": "string", "description": "Research domain"},
                        "project_path": {"type": "string", "description": "Path where project will be created"}
                    },
                    "required": ["name", "description", "domain", "project_path"]
                }
            },
            "save_session": {
                "description": "Save current research session data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_data": {"type": "object", "description": "Session data to save"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["session_data", "project_path"]
                }
            },
            "search_knowledge": {
                "description": "Search knowledge base using vector search",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "collection": {"type": "string", "description": "Collection to search"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["query", "project_path"]
                }
            },
            "version_control": {
                "description": "Perform Git version control operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Git action (commit, push, pull, etc.)"},
                        "message": {"type": "string", "description": "Commit message"},
                        "files": {"type": "array", "items": {"type": "string"}, "description": "Files to include"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["action", "message", "project_path"]
                }
            },
            "backup_project": {
                "description": "Backup project to specified location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Project path to backup"},
                        "backup_location": {"type": "string", "description": "Backup destination"}
                    },
                    "required": ["project_path"]
                }
            },
            "restore_session": {
                "description": "Restore a previous research session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "integer", "description": "Session ID to restore"},
                        "project_path": {"type": "string", "description": "Project path"}
                    },
                    "required": ["session_id", "project_path"]
                }
            },
            "store_bibliography_reference": {
                "description": "Store a bibliography reference in the vector database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "reference": {"type": "object", "description": "Reference data with title, authors, year, journal, etc."},
                        "project_path": {"type": "string", "description": "Project path for vector database"}
                    },
                    "required": ["reference"]
                }
            },
            "retrieve_bibliography_references": {
                "description": "Retrieve relevant bibliography references from vector database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for finding relevant references"},
                        "project_path": {"type": "string", "description": "Project path for vector database"},
                        "max_results": {"type": "integer", "description": "Maximum number of references to retrieve"}
                    },
                    "required": ["query"]
                }
            },
            "generate_document_with_database_bibliography": {
                "description": "Generate LaTeX document with bibliography retrieved from vector database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Document title"},
                        "author": {"type": "string", "description": "Author name"},
                        "abstract": {"type": "string", "description": "Abstract content"},
                        "introduction": {"type": "string", "description": "Introduction section"},
                        "methodology": {"type": "string", "description": "Methodology section"},
                        "results": {"type": "string", "description": "Results section"},
                        "discussion": {"type": "string", "description": "Discussion section"},
                        "conclusion": {"type": "string", "description": "Conclusion section"},
                        "project_path": {"type": "string", "description": "Project path for saving"},
                        "bibliography_query": {"type": "string", "description": "Query to retrieve relevant bibliography from database"}
                    },
                    "required": ["title", "bibliography_query"]
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
