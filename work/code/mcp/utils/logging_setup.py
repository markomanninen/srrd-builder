"""
Logging setup for SRRD Builder MCP Server
Provides structured logging with configurable levels and outputs
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logging for the MCP server
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to log to console
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        format_string: Custom log format string
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("srrd_builder")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "srrd_builder") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

class MCPLoggerAdapter:
    """Logger adapter for MCP operations with structured logging"""
    
    def __init__(self, logger: logging.Logger, tool_name: str = ""):
        self.logger = logger
        self.tool_name = tool_name
    
    def log_tool_call(self, tool_name: str, tool_args: dict, result: any = None, error: str = None):
        """Log tool call with structured information"""
        log_data = {
            "event": "tool_call",
            "tool": tool_name,
            "tool_arguments": tool_args,
            "timestamp": datetime.now().isoformat()
        }
        
        if result is not None:
            log_data["result"] = str(result)[:1000]  # Truncate long results
            self.logger.info(f"Tool call successful: {tool_name}", extra=log_data)
        elif error:
            log_data["error"] = error
            self.logger.error(f"Tool call failed: {tool_name} - {error}", extra=log_data)
        else:
            self.logger.info(f"Tool call initiated: {tool_name}", extra=log_data)
    
    def log_research_event(self, event_type: str, data: dict):
        """Log research-related events"""
        log_data = {
            "event": "research_event",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Research event: {event_type}", extra=log_data)
    
    def log_storage_operation(self, operation: str, path: str, status: str, details: dict = None):
        """Log storage operations (Git, SQLite, Vector DB)"""
        log_data = {
            "event": "storage_operation",
            "operation": operation,
            "path": path,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            log_data["details"] = details
        
        if status == "success":
            self.logger.info(f"Storage operation successful: {operation} on {path}", extra=log_data)
        else:
            self.logger.warning(f"Storage operation failed: {operation} on {path}", extra=log_data)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics"""
        log_data = {
            "event": "performance_metric",
            "metric": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Performance metric: {metric_name} = {value} {unit}", extra=log_data)

def create_session_logger(session_id: str, project_path: str = "") -> MCPLoggerAdapter:
    """Create a logger for a specific research session"""
    base_logger = get_logger()
    
    # Add session-specific file handler if project path provided
    if project_path:
        session_log_file = os.path.join(project_path, "logs", f"session_{session_id}.log")
        os.makedirs(os.path.dirname(session_log_file), exist_ok=True)
        
        session_handler = logging.FileHandler(session_log_file)
        session_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        session_handler.setFormatter(formatter)
        
        # Create session-specific logger
        session_logger = logging.getLogger(f"srrd_builder.session.{session_id}")
        session_logger.addHandler(session_handler)
        session_logger.setLevel(logging.INFO)
        
        return MCPLoggerAdapter(session_logger)
    
    return MCPLoggerAdapter(base_logger)
