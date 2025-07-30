# FILE: ./work/code/mcp/server.py

#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from pathlib import Path

import websockets
import websockets.exceptions

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

utils_path = current_dir / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# Also add the parent mcp directory to path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import project path using current_project.py utilities
try:
    # Use the MCP directory's current_project module which has the correct implementation
    from utils.current_project import get_current_project

    current_project_path = get_current_project()
except Exception as e:
    # Fallback: try the srrd_builder package version
    try:
        import importlib.util

        srrd_builder_utils = current_dir.parent.parent.parent / "srrd_builder" / "utils"
        current_project_path_file = srrd_builder_utils / "current_project.py"
        spec = importlib.util.spec_from_file_location(
            "current_project", current_project_path_file
        )
        current_project = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(current_project)
        get_current_project = current_project.get_current_project
        current_project_path = get_current_project()
    except Exception:
        current_project_path = None

# If no current project is set, use the global project directory
if current_project_path:
    PROJECT_PATH = current_project_path
else:
    # Use ~/Projects/default as default for both Windows and Unix
    home = Path.home()
    default_project_path = home / "Projects" / "default"

    # Ensure the directory exists
    try:
        default_project_path.mkdir(parents=True, exist_ok=True)

        # Create a basic README if it doesn't exist
        readme_path = default_project_path / "README.md"
        if not readme_path.exists():
            readme_content = """# SRRD Global Project Directory

This is the default global project directory for SRRD-Builder when no specific project is configured.

To configure a specific project:
- Run `srrd init` in your project directory
- Or run `srrd switch` in an existing project directory

This directory will store:
- Research sessions and data
- Generated documents and outputs
- Tool usage history and context
"""
            readme_path.write_text(readme_content)

    except Exception as e:
        # Fallback to current working directory if we can't create the default
        default_project_path = Path(os.getcwd())

    PROJECT_PATH = str(default_project_path)

# Import tools and utilities with fallback error handling
try:
    from tools import register_all_tools
except ImportError:

    def register_all_tools(server):
        pass


try:
    from utils.logging_setup import MCPLoggerAdapter, setup_logging
    from utils.request_logger import get_request_logger, initialize_request_logger
except ImportError:
    # Fallback logging if utils.logging_setup is not available
    import logging

    def setup_logging(*args, **kwargs):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    def initialize_request_logger(*args, **kwargs):
        pass

    def get_request_logger():
        return None

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
                        self.server = type(
                            "ServerConfig",
                            (),
                            {
                                "port": 8765,
                                "host": "localhost",
                                "disable_logging": False,
                                "log_level": "INFO",
                                "log_file": None,
                            },
                        )()

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

        # Setup logging (enable for both WebSocket and stdio)
        if not config.server.disable_logging:
            # For stdio mode, disable console logging to avoid interfering with stdio communication
            enable_console_logging = not use_stdio

            self.logger = setup_logging(
                log_level=config.server.log_level,
                log_file=config.server.log_file,
                enable_console=enable_console_logging,
            )
            self.log_adapter = MCPLoggerAdapter(self.logger, "mcp_server")

            # Initialize request logger with project-specific directory
            request_log_dir = os.path.join(PROJECT_PATH, "logs", "mcp_requests")
            self.request_logger = initialize_request_logger(request_log_dir, True)
        else:
            self.logger = None
            self.log_adapter = None
            self.request_logger = None

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
            if current_project_path:
                self.logger.info(
                    f"Using project-specific context: {current_project_path}"
                )
            else:
                self.logger.info(f"Using global project context: {PROJECT_PATH}")

    async def start_stdio_server(self):
        """Start MCP server using stdio for Claude Desktop with comprehensive logging"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if not line:
                    break

                data = json.loads(line)

                # Use the same comprehensive logging as WebSocket connections
                request_id = None
                client_info = "stdio"

                # Log incoming request
                if self.request_logger:
                    request_id = self.request_logger.log_incoming_request(
                        data, client_info
                    )

                    # Log server context
                    server_context = {
                        "project_path": PROJECT_PATH,
                        "server_port": self.port,
                        "tools_count": len(self.tools),
                        "available_tools": list(self.tools.keys()),
                        "stdio_mode": True,
                    }
                    self.request_logger.log_server_context(request_id, server_context)

                # Process the request with full logging
                response = await self._handle_mcp_request_with_logging(
                    data, request_id, client_info
                )

                # Log outgoing response
                if self.request_logger and request_id:
                    self.request_logger.log_outgoing_response(
                        request_id, response, client_info
                    )
                    self.request_logger.log_request_summary(request_id)

                print(json.dumps(response), flush=True)

            except EOFError:
                break
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {str(e)}"
                if self.logger:
                    self.logger.error("JSON decode error in stdio: %s", error_msg)

                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": error_msg},
                }

                # Log error response if possible
                if self.request_logger and request_id:
                    self.request_logger.log_outgoing_response(
                        request_id, error_response, client_info
                    )
                    self.request_logger.log_request_summary(request_id)

                print(json.dumps(error_response), flush=True)

            except Exception as e:
                error_msg = f"Server error: {str(e)}"
                if self.logger:
                    self.logger.error("Server error in stdio: %s", error_msg)

                error_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id") if "data" in locals() else None,
                    "error": {"code": -32000, "message": error_msg},
                }

                # Log error response if possible
                if self.request_logger and request_id:
                    self.request_logger.log_outgoing_response(
                        request_id, error_response, client_info
                    )
                    self.request_logger.log_request_summary(request_id)

                print(json.dumps(error_response), flush=True)

    async def _handle_mcp_request_with_logging(self, data, request_id, client_info):
        """Handle MCP request with comprehensive logging support"""
        method = data.get("method")
        params = data.get("params", {})
        msg_id = data.get("id")

        if method == "initialize":
            if self.log_adapter:
                self.log_adapter.log_tool_call(
                    "initialize", params, "Server initialized"
                )

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "SRRD Builder MCP Server",
                        "version": "1.0.0",
                        "projectPath": PROJECT_PATH,
                    },
                },
            }

        elif method == "tools/list":
            tools_info = await self.list_tools_mcp()
            return {"jsonrpc": "2.0", "id": msg_id, "result": tools_info}

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            # Log tool execution start
            from datetime import datetime

            execution_start = datetime.now()

            if self.log_adapter:
                self.log_adapter.log_tool_call(tool_name, tool_args)

            if tool_name in self.tools:
                try:
                    # Call the handler function from the tool dict
                    handler = self.tools[tool_name]["handler"]
                    result = await handler(**tool_args)
                    execution_end = datetime.now()

                    if self.log_adapter:
                        self.log_adapter.log_tool_call(tool_name, tool_args, result)

                    # Log tool execution success
                    if self.request_logger and request_id:
                        self.request_logger.log_tool_execution(
                            request_id,
                            tool_name,
                            tool_args,
                            execution_start,
                            execution_end,
                            result=result,
                        )

                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": str(result)}]},
                    }

                except Exception as e:
                    execution_end = datetime.now()
                    error_msg = f"Tool execution error: {str(e)}"

                    # Get traceback for detailed logging
                    import traceback

                    traceback_info = traceback.format_exc()

                    if self.log_adapter:
                        self.log_adapter.log_tool_call(
                            tool_name, tool_args, error=error_msg
                        )

                    # Log tool execution error
                    if self.request_logger and request_id:
                        self.request_logger.log_tool_execution(
                            request_id,
                            tool_name,
                            tool_args,
                            execution_start,
                            execution_end,
                            error=error_msg,
                            traceback_info=traceback_info,
                        )

                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32000,
                            "message": error_msg,
                        },
                    }
            else:
                error_msg = f"Tool '{tool_name}' not found"
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": error_msg,
                    },
                }
        else:
            # Unknown method
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

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
                        "projectPath": PROJECT_PATH,
                    },
                },
            }

        elif method == "tools/list":
            tools_info = await self.list_tools_mcp()
            return {"jsonrpc": "2.0", "id": msg_id, "result": tools_info}

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name in self.tools:
                try:
                    # Call the handler function from the tool dict
                    handler = self.tools[tool_name]["handler"]
                    result = await handler(**tool_args)
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {"content": [{"type": "text", "text": str(result)}]},
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32000,
                            "message": f"Tool execution error: {str(e)}",
                        },
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found",
                    },
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    async def start_server(self):
        if self.use_stdio:
            await self.start_stdio_server()
            return

        if self.logger:
            self.logger.info(f"Starting MCP server on {config.server.host}:{self.port}")

        async def websocket_handler(websocket, path=None):
            # Handle WebSocket subprotocol selection for browser compatibility
            client_info = f"{websocket.remote_address}"

            if hasattr(websocket, "subprotocol") and websocket.subprotocol:
                if self.logger:
                    self.logger.info(
                        f"WebSocket using subprotocol: {websocket.subprotocol} from {client_info}"
                    )
            else:
                if self.logger:
                    self.logger.info(
                        f"WebSocket connection without subprotocol from {client_info}"
                    )

            # Log request headers for debugging browser differences
            if hasattr(websocket, "request_headers") and self.logger:
                user_agent = websocket.request_headers.get("User-Agent", "Unknown")
                origin = websocket.request_headers.get("Origin", "None")
                self.logger.info(f"Client User-Agent: {user_agent}")
                self.logger.info(f"Client Origin: {origin}")

            if self.logger:
                self.logger.info(f"New WebSocket connection from {client_info}")
            try:
                return await self.handle_mcp_message(websocket, path or "/")
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"WebSocket handler error from {client_info}: {str(e)}"
                    )
            finally:
                if self.logger:
                    self.logger.info(f"WebSocket connection closed for {client_info}")

        # Create WebSocket server with browser compatibility options
        async with websockets.serve(
            websocket_handler,
            config.server.host,
            self.port,
            subprotocols=["mcp"],  # Support MCP subprotocol for browser clients
            ping_interval=20,  # Send ping every 20 seconds
            ping_timeout=10,  # Wait 10 seconds for pong
            close_timeout=10,  # Wait 10 seconds for close handshake
            origins=None,  # Allow all origins (for CORS)
        ):
            if self.logger:
                self.logger.info(
                    f"SRRD Builder MCP Server running on ws://{config.server.host}:{self.port}"
                )
            await asyncio.Future()  # run forever

    async def handle_mcp_message(self, websocket, path):
        """Handle incoming WebSocket messages using MCP JSON-RPC protocol with comprehensive logging"""
        try:
            async for message in websocket:
                request_id = None
                client_info = (
                    f"{websocket.remote_address}"
                    if hasattr(websocket, "remote_address")
                    else "unknown"
                )

                try:
                    data = json.loads(message)

                    # Log incoming request
                    if self.request_logger:
                        request_id = self.request_logger.log_incoming_request(
                            data, client_info
                        )

                        # Log server context
                        server_context = {
                            "project_path": PROJECT_PATH,
                            "server_port": self.port,
                            "tools_count": len(self.tools),
                            "available_tools": list(self.tools.keys()),
                            "stdio_mode": self.use_stdio,
                        }
                        self.request_logger.log_server_context(
                            request_id, server_context
                        )

                    # Handle JSON-RPC format
                    if "method" in data:
                        method = data.get("method")
                        params = data.get("params", {})
                        msg_id = data.get("id")

                        if method == "initialize":
                            if self.log_adapter:
                                self.log_adapter.log_tool_call(
                                    "initialize", params, "Server initialized"
                                )

                            response = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "result": {
                                    "protocolVersion": "2024-11-05",
                                    "capabilities": {"tools": {"listChanged": False}},
                                    "serverInfo": {
                                        "name": "SRRD Builder MCP Server",
                                        "version": "1.0.0",
                                        "projectPath": PROJECT_PATH,
                                    },
                                },
                            }

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, response, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(response))

                        elif method == "tools/list":
                            tools_info = await self.list_tools_mcp()
                            response = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "result": tools_info,
                            }

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, response, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(response))

                        elif method == "tools/call":
                            tool_name = params.get("name")
                            tool_args = params.get("arguments", {})

                            # Log tool execution start
                            from datetime import datetime

                            execution_start = datetime.now()

                            if self.log_adapter:
                                self.log_adapter.log_tool_call(tool_name, tool_args)

                            if tool_name in self.tools:
                                try:
                                    result = await self.tools[tool_name]["handler"](
                                        **tool_args
                                    )
                                    execution_end = datetime.now()

                                    if self.log_adapter:
                                        self.log_adapter.log_tool_call(
                                            tool_name, tool_args, result
                                        )

                                    # Log tool execution success
                                    if self.request_logger and request_id:
                                        self.request_logger.log_tool_execution(
                                            request_id,
                                            tool_name,
                                            tool_args,
                                            execution_start,
                                            execution_end,
                                            result=result,
                                        )

                                    response = {
                                        "jsonrpc": "2.0",
                                        "id": msg_id,
                                        "result": {
                                            "content": [
                                                {"type": "text", "text": str(result)}
                                            ]
                                        },
                                    }

                                    # Log outgoing response
                                    if self.request_logger and request_id:
                                        self.request_logger.log_outgoing_response(
                                            request_id, response, client_info
                                        )
                                        self.request_logger.log_request_summary(
                                            request_id
                                        )

                                    await websocket.send(json.dumps(response))

                                except Exception as e:
                                    execution_end = datetime.now()
                                    error_msg = f"Tool execution error: {str(e)}"

                                    # Get traceback for detailed logging
                                    import traceback

                                    traceback_info = traceback.format_exc()

                                    if self.log_adapter:
                                        self.log_adapter.log_tool_call(
                                            tool_name, tool_args, error=error_msg
                                        )

                                    # Log tool execution error
                                    if self.request_logger and request_id:
                                        self.request_logger.log_tool_execution(
                                            request_id,
                                            tool_name,
                                            tool_args,
                                            execution_start,
                                            execution_end,
                                            error=error_msg,
                                            traceback_info=traceback_info,
                                        )

                                    response = {
                                        "jsonrpc": "2.0",
                                        "id": msg_id,
                                        "error": {"code": -32000, "message": error_msg},
                                    }

                                    # Log outgoing response
                                    if self.request_logger and request_id:
                                        self.request_logger.log_outgoing_response(
                                            request_id, response, client_info
                                        )
                                        self.request_logger.log_request_summary(
                                            request_id
                                        )

                                    await websocket.send(json.dumps(response))
                            else:
                                error_msg = f"Tool '{tool_name}' not found"
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": msg_id,
                                    "error": {"code": -32601, "message": error_msg},
                                }

                                # Log outgoing response
                                if self.request_logger and request_id:
                                    self.request_logger.log_outgoing_response(
                                        request_id, response, client_info
                                    )
                                    self.request_logger.log_request_summary(request_id)

                                await websocket.send(json.dumps(response))
                        else:
                            # Unknown method
                            response = {
                                "jsonrpc": "2.0",
                                "id": msg_id,
                                "error": {
                                    "code": -32601,
                                    "message": f"Method not found: {method}",
                                },
                            }

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, response, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(response))

                    # Handle legacy format for backward compatibility
                    else:
                        command = data.get("command")
                        payload = data.get("payload")

                        if command == "initialize":
                            if self.log_adapter:
                                self.log_adapter.log_tool_call(
                                    "initialize", {}, "Server initialized"
                                )

                            response = {
                                "status": "initialized",
                                "capabilities": ["tools", "resources"],
                                "server_info": {
                                    "name": "SRRD Builder MCP Server",
                                    "version": "1.0.0",
                                    "tools_count": len(self.tools),
                                },
                            }

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, response, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(response))

                        elif command == "list_tools":
                            tools_info = await self.list_tools()

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, tools_info, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(tools_info))

                        elif command == "call_tool":
                            tool_name = payload.get("tool_name") if payload else None
                            tool_args = payload.get("tool_args", {}) if payload else {}

                            # Log tool execution start
                            from datetime import datetime

                            execution_start = datetime.now()

                            if self.log_adapter:
                                self.log_adapter.log_tool_call(tool_name, tool_args)

                            if tool_name and tool_name in self.tools:
                                try:
                                    result = await self.tools[tool_name]["handler"](
                                        **tool_args
                                    )
                                    execution_end = datetime.now()

                                    if self.log_adapter:
                                        self.log_adapter.log_tool_call(
                                            tool_name, tool_args, result
                                        )

                                    # Log tool execution success
                                    if self.request_logger and request_id:
                                        self.request_logger.log_tool_execution(
                                            request_id,
                                            tool_name,
                                            tool_args,
                                            execution_start,
                                            execution_end,
                                            result=result,
                                        )

                                    response = {
                                        "status": "success",
                                        "result": str(result),
                                    }

                                    # Log outgoing response
                                    if self.request_logger and request_id:
                                        self.request_logger.log_outgoing_response(
                                            request_id, response, client_info
                                        )
                                        self.request_logger.log_request_summary(
                                            request_id
                                        )

                                    await websocket.send(json.dumps(response))

                                except Exception as e:
                                    execution_end = datetime.now()
                                    error_msg = f"Tool execution error: {str(e)}"

                                    # Get traceback for detailed logging
                                    import traceback

                                    traceback_info = traceback.format_exc()

                                    if self.log_adapter:
                                        self.log_adapter.log_tool_call(
                                            tool_name, tool_args, error=error_msg
                                        )

                                    # Log tool execution error
                                    if self.request_logger and request_id:
                                        self.request_logger.log_tool_execution(
                                            request_id,
                                            tool_name,
                                            tool_args,
                                            execution_start,
                                            execution_end,
                                            error=error_msg,
                                            traceback_info=traceback_info,
                                        )

                                    response = {"status": "error", "error": error_msg}

                                    # Log outgoing response
                                    if self.request_logger and request_id:
                                        self.request_logger.log_outgoing_response(
                                            request_id, response, client_info
                                        )
                                        self.request_logger.log_request_summary(
                                            request_id
                                        )

                                    await websocket.send(json.dumps(response))
                            else:
                                error_msg = (
                                    f"Tool '{tool_name}' not found"
                                    if tool_name
                                    else "No tool name provided"
                                )
                                response = {"status": "error", "error": error_msg}

                                # Log outgoing response
                                if self.request_logger and request_id:
                                    self.request_logger.log_outgoing_response(
                                        request_id, response, client_info
                                    )
                                    self.request_logger.log_request_summary(request_id)

                                await websocket.send(json.dumps(response))
                        else:
                            error_msg = f"Unknown command: {command}"
                            response = {"status": "error", "error": error_msg}

                            # Log outgoing response
                            if self.request_logger and request_id:
                                self.request_logger.log_outgoing_response(
                                    request_id, response, client_info
                                )
                                self.request_logger.log_request_summary(request_id)

                            await websocket.send(json.dumps(response))

                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON: {str(e)}"
                    if self.logger:
                        self.logger.error("JSON decode error: %s", error_msg)

                    response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": error_msg},
                    }

                    # Log outgoing response
                    if self.request_logger and request_id:
                        self.request_logger.log_outgoing_response(
                            request_id, response, client_info
                        )
                        self.request_logger.log_request_summary(request_id)

                    await websocket.send(json.dumps(response))

                except Exception as e:
                    error_msg = f"Message handling error: {str(e)}"
                    if self.logger:
                        self.logger.error("Message handling error: %s", error_msg)

                    response = {
                        "jsonrpc": "2.0",
                        "id": data.get("id") if "data" in locals() else None,
                        "error": {"code": -32603, "message": error_msg},
                    }

                    # Log outgoing response
                    if self.request_logger and request_id:
                        self.request_logger.log_outgoing_response(
                            request_id, response, client_info
                        )
                        self.request_logger.log_request_summary(request_id)

                    await websocket.send(json.dumps(response))

        except websockets.exceptions.ConnectionClosedError:
            if self.logger:
                self.logger.info("WebSocket connection closed by client")
        except websockets.exceptions.ConnectionClosedOK:
            if self.logger:
                self.logger.info("WebSocket connection closed normally")
        except Exception as e:
            if self.logger:
                self.logger.error("WebSocket error: %s", str(e))

    def _register_tools(self):
        """Register MCP tools"""
        self.tools = {}
        register_all_tools(self)

    def register_tool(self, name, description, parameters, handler):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    async def list_tools_mcp(self):
        """Return list of available tools in MCP format - USING REAL REGISTERED SCHEMAS"""
        tools_list = []

        # Generate tool list from ACTUALLY registered tools (no more hardcoded schemas!)
        for tool_name, tool_data in self.tools.items():
            tool_info = {
                "name": tool_name,
                "description": tool_data.get("description", f"Tool: {tool_name}"),
                "inputSchema": tool_data.get(
                    "parameters", {"type": "object", "properties": {}, "required": []}
                ),
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
                        "novel_theory_mode": "boolean (optional)",
                    },
                },
                {
                    "name": "suggest_methodology",
                    "description": "Recommend appropriate research methodologies",
                    "parameters": {
                        "research_goals": "string",
                        "domain": "string",
                        "constraints": "object (optional)",
                        "novel_theory_flag": "boolean (optional)",
                    },
                },
                {
                    "name": "simulate_peer_review",
                    "description": "AI-powered peer review simulation",
                    "parameters": {
                        "document_content": "object",
                        "domain": "string",
                        "review_type": "string (optional)",
                        "novel_theory_mode": "boolean (optional)",
                    },
                },
                {
                    "name": "check_quality_gates",
                    "description": "Automated quality checks at each research phase",
                    "parameters": {
                        "research_content": "object",
                        "phase": "string",
                        "domain_standards": "object (optional)",
                        "innovation_criteria": "object (optional)",
                    },
                },
            ]
        }

    async def _websocket_handler(self, websocket, path=None):
        """WebSocket handler wrapper - compatible with different websockets versions"""
        # Some websockets versions pass path, others don't
        return await self.handle_mcp_message(websocket, path or "/")


if __name__ == "__main__":
    setup_logging()
    import argparse

    parser = argparse.ArgumentParser(description="SRRD Builder MCP Server")
    parser.add_argument(
        "--stdio", action="store_true", help="Use stdio for Claude Desktop"
    )
    parser.add_argument("--port", type=int, default=None, help="WebSocket port")

    args = parser.parse_args()

    server = MCPServer(port=args.port, use_stdio=args.stdio)
    asyncio.run(server.start_server())
