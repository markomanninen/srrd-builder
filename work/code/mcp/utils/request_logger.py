"""
Enhanced MCP Request/Response Logger
Provides detailed timestamped logging for all MCP tool requests, server context, and responses
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class MCPRequestLogger:
    """
    Comprehensive logger for MCP tool requests with timestamped files
    """

    def __init__(self, log_dir: str = None, enable_detailed_logging: bool = True):
        """
        Initialize the MCP request logger

        Args:
            log_dir: Directory for log files (defaults to ./logs/mcp_requests/)
            enable_detailed_logging: Whether to enable detailed timestamped logging
        """
        self.enable_detailed_logging = enable_detailed_logging

        if log_dir is None:
            # Default to logs/mcp_requests in the current working directory
            log_dir = os.path.join(os.getcwd(), "logs", "mcp_requests")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup standard logger
        self.logger = logging.getLogger("mcp_request_logger")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                "%(asctime)s - MCP_REQUEST - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # File handler for general MCP request log
            general_log_file = self.log_dir / "mcp_requests.log"
            file_handler = logging.FileHandler(general_log_file)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log_incoming_request(
        self, request_data: Dict[str, Any], client_info: str = "unknown"
    ) -> str:
        """
        Log an incoming MCP request with timestamp

        Args:
            request_data: The incoming request data
            client_info: Information about the client making the request

        Returns:
            request_id: Unique identifier for this request
        """
        timestamp = datetime.now()
        request_id = f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"

        # Extract basic info
        method = request_data.get("method", "unknown")
        msg_id = request_data.get("id", "no-id")
        params = request_data.get("params", {})

        # Log to console/general log
        self.logger.info(
            "INCOMING REQUEST [%s] - Method: %s, ID: %s, Client: %s",
            request_id,
            method,
            msg_id,
            client_info,
        )

        if self.enable_detailed_logging:
            # Create timestamped file for this request
            request_file = self.log_dir / f"request_{request_id}.json"

            detailed_log = {
                "request_id": request_id,
                "timestamp": timestamp.isoformat(),
                "client_info": client_info,
                "direction": "incoming",
                "request_data": request_data,
                "method": method,
                "message_id": msg_id,
                "parameters": params,
            }

            try:
                with open(request_file, "w", encoding="utf-8") as f:
                    json.dump(
                        detailed_log, f, indent=2, ensure_ascii=False, default=str
                    )

                self.logger.debug("Detailed request logged to: %s", request_file)
            except (IOError, OSError, ValueError) as e:
                self.logger.error("Failed to write detailed request log: %s", e)

        return request_id

    def log_server_context(self, request_id: str, context_data: Dict[str, Any]):
        """
        Log server context during request processing

        Args:
            request_id: The request ID from log_incoming_request
            context_data: Server context information
        """
        timestamp = datetime.now()

        self.logger.info("SERVER CONTEXT [%s] - Processing with context", request_id)

        if self.enable_detailed_logging:
            context_file = self.log_dir / f"context_{request_id}.json"

            context_log = {
                "request_id": request_id,
                "timestamp": timestamp.isoformat(),
                "direction": "server_context",
                "context_data": context_data,
            }

            try:
                with open(context_file, "w", encoding="utf-8") as f:
                    json.dump(context_log, f, indent=2, ensure_ascii=False, default=str)

                self.logger.debug("Server context logged to: %s", context_file)
            except (IOError, OSError, ValueError) as e:
                self.logger.error("Failed to write server context log: %s", e)

    def log_tool_execution(
        self,
        request_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        execution_start: datetime,
        execution_end: datetime = None,
        result: Any = None,
        error: str = None,
        traceback_info: str = None,
    ):
        """
        Log tool execution details

        Args:
            request_id: The request ID from log_incoming_request
            tool_name: Name of the tool being executed
            tool_args: Arguments passed to the tool
            execution_start: When tool execution started
            execution_end: When tool execution ended (optional if still running)
            result: Tool execution result (if successful)
            error: Error message (if failed)
            traceback_info: Full traceback information (if error occurred)
        """
        if execution_end is None:
            execution_end = datetime.now()

        execution_time = (execution_end - execution_start).total_seconds()

        status = "success" if error is None else "error"
        self.logger.info(
            "TOOL EXECUTION [%s] - Tool: %s, Status: %s, Duration: %.3fs",
            request_id,
            tool_name,
            status,
            execution_time,
        )

        if self.enable_detailed_logging:
            execution_file = self.log_dir / f"execution_{request_id}.json"

            execution_log = {
                "request_id": request_id,
                "timestamp": execution_end.isoformat(),
                "direction": "tool_execution",
                "tool_name": tool_name,
                "tool_arguments": tool_args,
                "execution_start": execution_start.isoformat(),
                "execution_end": execution_end.isoformat(),
                "execution_time_seconds": execution_time,
                "status": status,
            }

            if result is not None:
                # Truncate very long results but preserve structure
                result_str = str(result)
                if len(result_str) > 10000:
                    execution_log["result"] = (
                        result_str[:10000]
                        + f"... (truncated, full length: {len(result_str)})"
                    )
                    execution_log["result_truncated"] = True
                else:
                    execution_log["result"] = result
                    execution_log["result_truncated"] = False

            if error:
                execution_log["error"] = error

            if traceback_info:
                execution_log["traceback"] = traceback_info

            try:
                with open(execution_file, "w", encoding="utf-8") as f:
                    json.dump(
                        execution_log, f, indent=2, ensure_ascii=False, default=str
                    )

                self.logger.debug("Tool execution logged to: %s", execution_file)
            except (IOError, OSError, ValueError) as e:
                self.logger.error("Failed to write tool execution log: %s", e)

    def log_outgoing_response(
        self,
        request_id: str,
        response_data: Dict[str, Any],
        client_info: str = "unknown",
    ):
        """
        Log an outgoing MCP response

        Args:
            request_id: The request ID from log_incoming_request
            response_data: The response data being sent
            client_info: Information about the client receiving the response
        """
        timestamp = datetime.now()

        # Extract basic info
        error = response_data.get("error")
        status = "success" if error is None else "error"

        self.logger.info(
            "OUTGOING RESPONSE [%s] - Status: %s, Client: %s",
            request_id,
            status,
            client_info,
        )

        if self.enable_detailed_logging:
            response_file = self.log_dir / f"response_{request_id}.json"

            response_log = {
                "request_id": request_id,
                "timestamp": timestamp.isoformat(),
                "client_info": client_info,
                "direction": "outgoing",
                "response_data": response_data,
                "status": status,
            }

            try:
                with open(response_file, "w", encoding="utf-8") as f:
                    json.dump(
                        response_log, f, indent=2, ensure_ascii=False, default=str
                    )

                self.logger.debug("Outgoing response logged to: %s", response_file)
            except (IOError, OSError, ValueError) as e:
                self.logger.error("Failed to write outgoing response log: %s", e)

    def log_request_summary(self, request_id: str):
        """
        Create a summary file linking all related log files for a request

        Args:
            request_id: The request ID to summarize
        """
        if not self.enable_detailed_logging:
            return

        summary_file = self.log_dir / f"summary_{request_id}.json"

        # Find all related files
        related_files = []
        for file_pattern in [
            f"request_{request_id}.json",
            f"context_{request_id}.json",
            f"execution_{request_id}.json",
            f"response_{request_id}.json",
        ]:
            file_path = self.log_dir / file_pattern
            if file_path.exists():
                related_files.append(file_pattern)

        summary = {
            "request_id": request_id,
            "summary_timestamp": datetime.now().isoformat(),
            "related_log_files": related_files,
            "log_directory": str(self.log_dir),
        }

        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.logger.info("Request summary created: %s", summary_file)
        except (IOError, OSError, ValueError) as e:
            self.logger.error("Failed to write request summary: %s", e)

    def get_request_files(self, request_id: str) -> Dict[str, str]:
        """
        Get all log files associated with a request ID

        Args:
            request_id: The request ID to find files for

        Returns:
            Dictionary mapping file types to file paths
        """
        files = {}

        file_mappings = {
            "request": f"request_{request_id}.json",
            "context": f"context_{request_id}.json",
            "execution": f"execution_{request_id}.json",
            "response": f"response_{request_id}.json",
            "summary": f"summary_{request_id}.json",
        }

        for file_type, filename in file_mappings.items():
            file_path = self.log_dir / filename
            if file_path.exists():
                files[file_type] = str(file_path)

        return files

    def cleanup_old_logs(self, days_to_keep: int = 7):
        """
        Clean up log files older than specified days

        Args:
            days_to_keep: Number of days to keep log files
        """
        try:
            import time

            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

            removed_count = 0
            for log_file in self.log_dir.glob("*.json"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    removed_count += 1

            if removed_count > 0:
                self.logger.info("Cleaned up %d old log files", removed_count)

        except (OSError, IOError) as e:
            self.logger.error("Failed to cleanup old logs: %s", e)


# Module-level instance for easy access
_request_logger_instance: Optional[MCPRequestLogger] = None


def get_request_logger() -> MCPRequestLogger:
    """Get the module-level request logger instance"""
    if _request_logger_instance is None:
        return initialize_request_logger()
    return _request_logger_instance


def initialize_request_logger(
    log_dir: str = None, enable_detailed_logging: bool = True
) -> MCPRequestLogger:
    """Initialize the module-level request logger with custom settings"""
    # pylint: disable=global-statement
    global _request_logger_instance
    _request_logger_instance = MCPRequestLogger(log_dir, enable_detailed_logging)
    return _request_logger_instance
