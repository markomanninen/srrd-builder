#!/usr/bin/env python3
"""
SRRD-Builder Enhanced MCP Server for Claude Desktop
Model Context Protocol server providing 38+ research assistance tools with lifecycle persistence
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
from storage.sqlite_manager import SQLiteManager
from utils.research_framework import ResearchFrameworkService
from utils.workflow_intelligence import WorkflowIntelligence

class EnhancedClaudeMCPServer:
    def __init__(self):
        self.tools = {}
        self.running = True
        self.current_session_id = None
        self.current_project_id = None
        
        # Initialize services
        self.research_framework = ResearchFrameworkService()
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
    
    def register_tool(self, name, description, parameters, handler):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            'description': description,
            'parameters': parameters,
            'handler': handler
        }

    async def _initialize_database_if_needed(self):
        """Initialize database connection if not already done"""
        if not self.sqlite_manager:
            # Try to get project path from environment
            project_path = os.environ.get('SRRD_PROJECT_PATH')
            if project_path:
                db_path = str(Path(project_path) / '.srrd' / 'sessions.db')
                self.sqlite_manager = SQLiteManager(db_path)
                await self.sqlite_manager.initialize()
                
                # Initialize workflow intelligence
                self.workflow_intelligence = WorkflowIntelligence(
                    self.sqlite_manager, 
                    self.research_framework
                )

    async def _get_or_create_session(self, project_id: int) -> int:
        """Get current session or create a new one"""
        if not self.current_session_id:
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
                await self._initialize_database_if_needed()
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "SRRD Builder Enhanced MCP Server",
                            "version": "2.0.0"
                        }
                    }
                }
                
            elif method == "notifications/initialized":
                return None
                
            elif method == "tools/list":
                tools_info = await self.list_tools_mcp_enhanced()
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
                        # Enhanced tool execution with logging
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
                "id": msg_id,
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
        research_context = self.research_framework.get_tool_research_context(tool_name)
        
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

    async def list_tools_mcp_enhanced(self):
        """Return enhanced list of available tools with research act categorization"""
        tools_list = []
        
        # Group tools by research act for better organization
        tools_by_act = {}
        
        for tool_name, tool_data in self.tools.items():
            # Get research context
            research_context = self.research_framework.get_tool_research_context(tool_name)
            
            tool_info = {
                "name": tool_name,
                "description": tool_data['description'],
                "inputSchema": tool_data['parameters']
            }
            
            # Add research act metadata if available
            if research_context:
                tool_info["metadata"] = {
                    "research_act": research_context['act'],
                    "research_category": research_context['category'],
                    "act_name": research_context['act_name'],
                    "category_name": research_context['category_name']
                }
                
                # Group by research act
                act = research_context['act']
                if act not in tools_by_act:
                    tools_by_act[act] = []
                tools_by_act[act].append(tool_info)
            else:
                # Uncategorized tools
                if 'uncategorized' not in tools_by_act:
                    tools_by_act['uncategorized'] = []
                tools_by_act['uncategorized'].append(tool_info)
            
            tools_list.append(tool_info)
        
        return {
            "tools": tools_list,
            "research_framework": {
                "acts": self.research_framework.acts,
                "categories": self.research_framework.categories,
                "tools_by_act": tools_by_act
            }
        }

    async def run(self):
        """Run the MCP server"""
        while self.running:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    if response:
                        print(json.dumps(response), flush=True)
                        
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
        
        # Cleanup
        if self.sqlite_manager:
            await self.sqlite_manager.close()

# For backward compatibility, keep the original class name as alias
ClaudeMCPServer = EnhancedClaudeMCPServer

def main():
    """Main entry point"""
    server = EnhancedClaudeMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
