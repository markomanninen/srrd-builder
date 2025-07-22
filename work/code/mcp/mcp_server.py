#!/usr/bin/env python3
"""
SRRD-Builder MCP Server for Claude Desktop
Model Context Protocol server providing 44 research assistance tools
"""
import asyncio
import json
import sys
import os
import signal
import time
from pathlib import Path
from typing import Optional

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from tools import register_all_tools

# Import database and workflow intelligence functionality
try:
    from storage.sqlite_manager import SQLiteManager
    from utils.research_framework import ResearchFrameworkService  
    from utils.workflow_intelligence import WorkflowIntelligence
except ImportError as e:
    # Log to stderr to avoid JSON parsing issues
    import sys
    print(f"Warning: Could not import database functionality: {e}", file=sys.stderr)
    SQLiteManager = None
    ResearchFrameworkService = None
    WorkflowIntelligence = None

class ClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        self.running = True
        self.current_session_id = None
        self.current_project_id = None
        
        # Initialize services if available
        self.research_framework = ResearchFrameworkService() if ResearchFrameworkService else None
        self.sqlite_manager = None
        self.workflow_intelligence = None
        
        self._register_tools()
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        # Skip signal handlers during test execution to prevent hanging
        import sys
        if 'pytest' in sys.modules:
            return
            
        def signal_handler(signum, frame):
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def _register_tools(self):
        """Register MCP tools using the standard registration system"""
        # Use the existing registration system from tools module
        register_all_tools(self)
        
        # Make server instance available globally for tools to access shared database
        sys.modules[__name__].global_server_instance = self
    
    def register_tool(self, name, description, parameters, handler):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            'description': description,
            'parameters': parameters,
            'handler': handler
        }

    async def _initialize_database_if_needed(self):
        """Initialize database connection if not already done"""
        if not self.sqlite_manager and SQLiteManager:
            # Try to get project path from environment
            project_path = os.environ.get('SRRD_PROJECT_PATH')
            if project_path:
                db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
                self.sqlite_manager = SQLiteManager(db_path)
                await self.sqlite_manager.initialize()
                
                # Initialize workflow intelligence
                if WorkflowIntelligence and self.research_framework:
                    self.workflow_intelligence = WorkflowIntelligence(
                        self.sqlite_manager, 
                        self.research_framework
                    )
                
                # Ensure a default project exists
                await self._ensure_default_project_exists()

    async def _ensure_default_project_exists(self):
        """Ensure a default project exists in the database"""
        if self.sqlite_manager:
            try:
                # Check if any projects exist
                async with self.sqlite_manager.connection.execute(
                    "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
                ) as cursor:
                    project_row = await cursor.fetchone()
                    
                if not project_row:
                    # Create a default project
                    project_path = os.environ.get('SRRD_PROJECT_PATH', '/tmp/default_project')
                    project_name = Path(project_path).name or 'Default Project'
                    
                    await self.sqlite_manager.connection.execute(
                        "INSERT INTO projects (name, description, domain, created_at) VALUES (?, ?, ?, ?)",
                        (project_name, "Auto-created default project", "general", "datetime('now')")
                    )
                    await self.sqlite_manager.connection.commit()
                    # Log to stderr to avoid JSON parsing issues
                    import sys
                    print(f"Created default project: {project_name}", file=sys.stderr)
                    
            except Exception as e:
                # Log to stderr to avoid JSON parsing issues
                import sys
                print(f"Warning: Could not ensure default project: {e}", file=sys.stderr)

    async def _get_or_create_session(self, project_id: int) -> int:
        """Get current session or create a new one"""
        if not self.current_session_id and self.sqlite_manager:
            # Create new session
            self.current_session_id = await self.sqlite_manager.create_session(
                project_id=project_id,
                session_type='research',
                user_id='claude_user'
            )
            self.current_project_id = project_id
        
        return self.current_session_id

    async def handle_request(self, request_data):
        """Handle MCP request from Claude Desktop"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            msg_id = request_data.get("id", 1)
            
            if method == "initialize":
                # Include project path in server info if available
                project_path = os.environ.get('SRRD_PROJECT_PATH')
                server_info = {
                    "name": "SRRD Builder MCP Server",
                    "version": "1.0.0"
                }
                
                # Add project path to server info if available
                if project_path:
                    server_info["projectPath"] = project_path
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {"tools": {}},
                        "serverInfo": server_info
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
                        # Enhanced tool execution with comprehensive logging
                        result = await self._execute_tool_with_logging(tool_name, tool_args)
                        
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
                        "message": f"Unknown method: {method}"
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

    async def _execute_tool_with_logging(self, tool_name: str, tool_args: dict):
        """Execute tool with comprehensive logging and research act tracking"""
        start_time = time.time()
        
        # Initialize database if needed
        await self._initialize_database_if_needed()
        
        # Get research context for tool
        research_context = self.research_framework.get_tool_research_context(tool_name) if self.research_framework else None
        
        try:
            # Execute the tool
            handler = self.tools[tool_name]['handler']
            result = await handler(**tool_args)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log tool usage if database is available
            if self.sqlite_manager and research_context:
                # Get or create project if project_path is in args
                project_id = await self._get_project_id_from_args(tool_args)
                
                if project_id:
                    # Get or create session
                    session_id = await self._get_or_create_session(project_id)
                    
                    # Log tool usage
                    await self.sqlite_manager.log_tool_usage(
                        session_id=session_id,
                        tool_name=tool_name,
                        research_act=research_context['act'],
                        research_category=research_context['category'],
                        arguments=tool_args,
                        result_summary=str(result)[:500],  # Truncate long results
                        execution_time_ms=execution_time_ms,
                        success=True
                    )
                    
                    # Update research progress
                    await self._update_research_progress(project_id, research_context, tool_name)
                    
                    # Check for milestones
                    if self.workflow_intelligence:
                        await self.workflow_intelligence.detect_milestones(project_id)
            
            return result
            
        except Exception as e:
            # Log error if database is available
            if self.sqlite_manager and research_context:
                project_id = await self._get_project_id_from_args(tool_args)
                if project_id:
                    session_id = await self._get_or_create_session(project_id)
                    
                    await self.sqlite_manager.log_tool_usage(
                        session_id=session_id,
                        tool_name=tool_name,
                        research_act=research_context['act'],
                        research_category=research_context['category'],
                        arguments=tool_args,
                        success=False,
                        error_message=str(e)
                    )
            
            raise e

    async def _get_project_id_from_args(self, tool_args: dict) -> Optional[int]:
        """Extract project ID from tool arguments or environment"""
        
        # First try to get from environment (set by global launcher)
        project_path = os.environ.get('SRRD_PROJECT_PATH')
        
        # If not in environment, try to get from tool args
        if not project_path:
            project_path = tool_args.get('project_path')
        
        if not project_path:
            return None
        
        # Try to get project ID from database
        try:
            # Check if project exists in database
            async with self.sqlite_manager.connection.execute(
                "SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
        except:
            pass
        
        return None

    async def _update_research_progress(self, project_id: int, research_context: dict, tool_name: str):
        """Update research progress based on tool usage"""
        
        # Get current tools used in this category
        tools_used = await self.sqlite_manager.get_tools_used_in_project(project_id)
        
        # Calculate category completion
        category_completion = self.research_framework.calculate_category_completion(
            tools_used, research_context['category']
        )
        
        # Determine status
        status = 'in_progress'
        if category_completion['completion_percentage'] >= 100:
            status = 'completed'
        elif category_completion['completion_percentage'] > 0:
            status = 'in_progress'
        else:
            status = 'not_started'
        
        # Update progress
        await self.sqlite_manager.update_research_progress(
            project_id=project_id,
            research_act=research_context['act'],
            research_category=research_context['category'],
            status=status,
            completion_percentage=int(category_completion['completion_percentage']),
            tools_used=category_completion['tools_used_list']
        )

    def list_tools_mcp(self):
        """Return list of available tools in MCP format"""
        tools_list = []
        
        # Use the dynamically registered tools
        for tool_name, tool_info in self.tools.items():
            tools_list.append({
                "name": tool_name,
                "description": tool_info['description'],
                "inputSchema": tool_info['parameters']
            })
        
        return {"tools": tools_list}

    async def run(self):
        """Run the MCP server using stdio for Claude Desktop"""
        try:
            while self.running:
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
                        response_json = json.dumps(response, ensure_ascii=False) + '\n'
                        sys.stdout.write(response_json)
                        sys.stdout.flush()
                    
                except EOFError:
                    break
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    response_json = json.dumps(error_response, ensure_ascii=False) + '\n'
                    sys.stdout.write(response_json)
                    sys.stdout.flush()
                except Exception as e:
                    # Log errors to stderr for debugging
                    print(f"MCP Server Error: {e}", file=sys.stderr)
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    response_json = json.dumps(error_response, ensure_ascii=False) + '\n'
                    sys.stdout.write(response_json)
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"MCP Server Fatal Error: {e}", file=sys.stderr)

    def start(self):
        """Start the MCP server"""
        # Log to stderr to avoid JSON parsing issues
        import sys
        print("Starting SRRD-Builder MCP Server...", file=sys.stderr)
        print(f"Registered {len(self.tools)} tools", file=sys.stderr)
        asyncio.run(self.run())

if __name__ == "__main__":
    server = ClaudeMCPServer()
    server.start()
