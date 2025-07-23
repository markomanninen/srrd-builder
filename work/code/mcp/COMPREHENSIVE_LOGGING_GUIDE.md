# MCP Request/Response Logging System

## Overview

This document describes the comprehensive logging system implemented for the SRRD Builder MCP Server that captures detailed information about every MCP tool request, server context, and response with timestamped files.

## Features

### 1. **Comprehensive Request Tracking**

- **Incoming Requests**: Every MCP request is logged with full details
- **Server Context**: Current server state and project context
- **Tool Execution**: Detailed execution timing and parameters  
- **Outgoing Responses**: Complete response data and status
- **Request Summaries**: Links all related log files for a request

### 2. **Timestamped File Structure**

Each MCP request generates a unique timestamp ID in format: `YYYYMMDD_HHMMSS_microseconds`

Example: `20250723_143052_123456`

### 3. **Log File Types**

| File Type     | Purpose                          | Example Filename                        |
| ------------- | -------------------------------- | --------------------------------------- |
| **Request**   | Incoming MCP request data        | `request_20250723_143052_123456.json`   |
| **Context**   | Server context during processing | `context_20250723_143052_123456.json`   |
| **Execution** | Tool execution details & timing  | `execution_20250723_143052_123456.json` |
| **Response**  | Outgoing response data           | `response_20250723_143052_123456.json`  |
| **Summary**   | Links to all related files       | `summary_20250723_143052_123456.json`   |
| **General**   | Overall activity log             | `mcp_requests.log`                      |

## Log Storage Locations

### Project-Specific Logging

When working in a specific SRRD project:

```text
[PROJECT_PATH]/logs/mcp_requests/
```

### Global Logging  

When no project is active:

```text
~/.srrd/globalproject/logs/mcp_requests/
```

## Sample Log Files

### Request Log Example

```json
{
  "request_id": "20250723_143052_123456",
  "timestamp": "2025-07-23T14:30:52.123456",
  "client_info": "127.0.0.1:54321",
  "direction": "incoming",
  "request_data": {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "initialize_project",
      "arguments": {
        "name": "Example Project",
        "description": "Test project",
        "domain": "Computer Science"
      }
    }
  },
  "method": "tools/call",
  "message_id": 1,
  "parameters": {...}
}
```

### Context Log Example

```json
{
  "request_id": "20250723_143052_123456",
  "timestamp": "2025-07-23T14:30:52.123500", 
  "direction": "server_context",
  "context_data": {
    "project_path": "/Users/user/projects/example",
    "server_port": 8080,
    "tools_count": 25,
    "available_tools": ["initialize_project", "clarify_research_goals", ...],
    "stdio_mode": false
  }
}
```

### Execution Log Example

```json
{
  "request_id": "20250723_143052_123456",
  "timestamp": "2025-07-23T14:30:52.789012",
  "direction": "tool_execution", 
  "tool_name": "initialize_project",
  "tool_arguments": {...},
  "execution_start": "2025-07-23T14:30:52.234567",
  "execution_end": "2025-07-23T14:30:52.789012",
  "execution_time_seconds": 0.554445,
  "status": "success",
  "result": "Project initialized successfully...",
  "result_truncated": false
}
```

### Response Log Example

```json
{
  "request_id": "20250723_143052_123456",
  "timestamp": "2025-07-23T14:30:52.790000",
  "client_info": "127.0.0.1:54321",
  "direction": "outgoing",
  "response_data": {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
      "content": [
        {
          "type": "text",
          "text": "Project initialized successfully..."
        }
      ]
    }
  },
  "status": "success"
}
```

### Summary Log Example

```json
{
  "request_id": "20250723_143052_123456",
  "summary_timestamp": "2025-07-23T14:30:52.791000",
  "related_log_files": [
    "request_20250723_143052_123456.json",
    "context_20250723_143052_123456.json",
    "execution_20250723_143052_123456.json", 
    "response_20250723_143052_123456.json"
  ],
  "log_directory": "/Users/user/projects/example/logs/mcp_requests"
}
```

## Implementation Details

### MCPRequestLogger Class

Located in: `work/code/mcp/utils/request_logger.py`

Key methods:

- `log_incoming_request()` - Logs incoming MCP requests
- `log_server_context()` - Logs server state during processing
- `log_tool_execution()` - Logs tool execution with timing
- `log_outgoing_response()` - Logs outgoing responses
- `log_request_summary()` - Creates summary linking all files

### Integration with MCP Server

The logging is integrated into `work/code/mcp/server.py` in the `handle_mcp_message()` method:

1. **Request Arrival**: Immediate logging of incoming request
2. **Context Capture**: Server state logged before tool execution
3. **Execution Tracking**: Tool execution with start/end timing
4. **Response Logging**: Complete response data captured  
5. **Summary Creation**: Links all related files together

### Error Handling

- **Tool Execution Errors**: Full stack traces captured in execution logs
- **JSON Decode Errors**: Invalid JSON requests logged with error details
- **Connection Errors**: WebSocket connection issues logged appropriately

## Benefits

### For Debugging

- **Complete Request History**: Every interaction is preserved
- **Timing Information**: Identify performance bottlenecks
- **Error Analysis**: Full stack traces for failed tool calls
- **Context Awareness**: Understand server state during issues

### For Development

- **Tool Usage Patterns**: See which tools are used most frequently
- **Parameter Analysis**: Understand how tools are being called
- **Performance Monitoring**: Track execution times across tools
- **Client Behavior**: Analyze different client connection patterns

### For Research Continuity

- **Session Reconstruction**: Replay exactly what happened in a session
- **Research Trail**: Complete audit trail of research activities
- **Data Recovery**: Restore lost work from detailed logs
- **Process Analysis**: Understand research workflow patterns

## Usage Examples

### Finding All Logs for a Request

```python
from utils.request_logger import get_request_logger

logger = get_request_logger()
files = logger.get_request_files("20250723_143052_123456")
print(files)
# Output: {
#   'request': '/path/to/request_20250723_143052_123456.json',
#   'context': '/path/to/context_20250723_143052_123456.json',
#   'execution': '/path/to/execution_20250723_143052_123456.json', 
#   'response': '/path/to/response_20250723_143052_123456.json',
#   'summary': '/path/to/summary_20250723_143052_123456.json'
# }
```

### Cleaning Old Logs

```python
logger.cleanup_old_logs(days_to_keep=7)  # Keep only 7 days of logs
```

### Analyzing Request Patterns

You can analyze the log files using standard JSON tools:

```bash
# Find all tool calls
grep -l "tools/call" logs/mcp_requests/request_*.json

# Count tool usage
jq -r '.request_data.params.name' logs/mcp_requests/request_*.json | sort | uniq -c

# Find slow operations
jq 'select(.execution_time_seconds > 1.0)' logs/mcp_requests/execution_*.json
```

## Testing the Logging System

Run the test script to see the logging in action:

```bash
cd work/code/mcp
python test_logging.py
```

This will:

1. Connect to the MCP server
2. Send various types of requests
3. Generate comprehensive logs
4. Show you where to find the log files

## Practical Examples

### Starting the MCP Server with Logging

```bash
# Start the MCP server on port 8080 with logging enabled
cd /path/to/srrd-builder
python -m work.code.mcp.server --port 8080
```

Expected output:

```text
2025-07-23 17:17:02,500 - srrd_builder - INFO - MCP Server initialized on port 8080
2025-07-23 17:17:02,500 - srrd_builder - INFO - Registered 46 tools
2025-07-23 17:17:02,500 - srrd_builder - INFO - PROJECT_PATH: /Users/username/Desktop/example-srrd-project
2025-07-23 17:17:02,500 - srrd_builder - INFO - Using project-specific context: /Users/username/Desktop/example-srrd-project
2025-07-23 17:17:02,513 - srrd_builder - INFO - SRRD Builder MCP Server running on ws://localhost:8080
```

### Examining Generated Log Files

After running the test script, check the generated logs:

```bash
# List all generated log files
ls -la /Users/username/Desktop/example-srrd-project/logs/mcp_requests/

# Expected output:
# -rw-r--r-- context_20250723_171852_519058.json
# -rw-r--r-- execution_20250723_171853_540629.json
# -rw-r--r-- mcp_requests.log
# -rw-r--r-- request_20250723_171852_519058.json
# -rw-r--r-- response_20250723_171852_519058.json
# -rw-r--r-- summary_20250723_171852_519058.json
```

### Viewing the General Activity Log

```bash
# Show recent MCP activity
tail -10 /Users/username/Desktop/example-srrd-project/logs/mcp_requests/mcp_requests.log

# Expected output:
# 2025-07-23 17:18:52,519 - INFO - INCOMING REQUEST [20250723_171852_519058] - Method: initialize, ID: 1, Client: ('::1', 53866, 0, 0)
# 2025-07-23 17:18:53,024 - INFO - INCOMING REQUEST [20250723_171853_024130] - Method: tools/list, ID: 2, Client: ('::1', 53866, 0, 0)
# 2025-07-23 17:18:53,540 - INFO - INCOMING REQUEST [20250723_171853_540629] - Method: tools/call, ID: 3, Client: ('::1', 53866, 0, 0)
# 2025-07-23 17:18:54,321 - INFO - TOOL EXECUTION [20250723_171853_540629] - Tool: initialize_project, Status: success, Duration: 0.780s
```

### Examining a Specific Request

```bash
# View the incoming request details
cat /path/to/logs/mcp_requests/request_20250723_171853_540629.json
```

**Example Request File:**

```json
{
  "request_id": "20250723_171853_540629",
  "timestamp": "2025-07-23T17:18:53.540629",
  "client_info": "('::1', 53866, 0, 0)",
  "direction": "incoming",
  "request_data": {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "initialize_project",
      "arguments": {
        "name": "Test Logging Project",
        "description": "A test project to demonstrate logging",
        "domain": "Computer Science"
      }
    }
  },
  "method": "tools/call",
  "message_id": 3,
  "parameters": {
    "name": "initialize_project",
    "arguments": {
      "name": "Test Logging Project",
      "description": "A test project to demonstrate logging", 
      "domain": "Computer Science"
    }
  }
}
```

### Viewing Server Context

```bash
# Check what server context was captured
cat /path/to/logs/mcp_requests/context_20250723_171853_540629.json
```

**Example Context File:**

```json
{
  "request_id": "20250723_171853_540629",
  "timestamp": "2025-07-23T17:18:53.541011",
  "direction": "server_context",
  "context_data": {
    "project_path": "/Users/username/Desktop/example-srrd-project",
    "server_port": 8080,
    "tools_count": 46,
    "available_tools": [
      "clarify_research_goals",
      "suggest_methodology", 
      "initialize_project",
      "save_session",
      "... (42 more tools)"
    ],
    "stdio_mode": false
  }
}
```

### Analyzing Tool Execution Performance

```bash
# View detailed execution information
cat /path/to/logs/mcp_requests/execution_20250723_171853_540629.json
```

**Example Execution File:**

```json
{
  "request_id": "20250723_171853_540629",
  "timestamp": "2025-07-23T17:18:54.321561",
  "direction": "tool_execution",
  "tool_name": "initialize_project",
  "tool_arguments": {
    "name": "Test Logging Project",
    "description": "A test project to demonstrate logging",
    "domain": "Computer Science"
  },
  "execution_start": "2025-07-23T17:18:53.541247",
  "execution_end": "2025-07-23T17:18:54.321561", 
  "execution_time_seconds": 0.780314,
  "status": "success",
  "result": "Project 'Test Logging Project' initialized successfully!...",
  "result_truncated": false
}
```

### Using Summary Files for Correlation

```bash
# Find all related files for a specific request
cat /path/to/logs/mcp_requests/summary_20250723_171853_540629.json
```

**Example Summary File:**

```json
{
  "request_id": "20250723_171853_540629",
  "summary_timestamp": "2025-07-23T17:18:54.321938",
  "related_log_files": [
    "request_20250723_171853_540629.json",
    "context_20250723_171853_540629.json",
    "execution_20250723_171853_540629.json",
    "response_20250723_171853_540629.json"
  ],
  "log_directory": "/Users/username/Desktop/example-srrd-project/logs/mcp_requests"
}
```

### Debugging Workflow

When troubleshooting MCP tool issues:

1. **Find the problematic request** in the general log:

   ```bash
   grep -n "ERROR\|Tool execution error" mcp_requests.log
   ```

2. **Get the timestamp** from the log entry and examine the request:

   ```bash
   cat request_[TIMESTAMP].json
   ```

3. **Check server context** at the time:

   ```bash
   cat context_[TIMESTAMP].json
   ```

4. **Analyze execution details** for timing and errors:

   ```bash
   cat execution_[TIMESTAMP].json
   ```

5. **Verify the response** that was sent:

   ```bash
   cat response_[TIMESTAMP].json
   ```

### Common Log Analysis Commands

```bash
# Count requests by method
grep "INCOMING REQUEST" mcp_requests.log | cut -d'-' -f2 | cut -d',' -f1 | sort | uniq -c

# Find slow tool executions (>1 second)
grep "Duration:" mcp_requests.log | awk '$NF > 1.0'

# List all tool execution errors
grep "Status: error" mcp_requests.log

# Find most used tools
jq -r '.tool_name' execution_*.json | sort | uniq -c | sort -nr
```

## Configuration

The logging system is automatically enabled when the MCP server starts with logging enabled. It uses the project path to determine where to store logs:

- **In Project**: Logs go to `[PROJECT_PATH]/logs/mcp_requests/`
- **Global**: Logs go to `~/.srrd/globalproject/logs/mcp_requests/`

## Performance Considerations

- **Asynchronous Logging**: File I/O doesn't block request processing
- **Result Truncation**: Very long results are truncated but length is preserved
- **Automatic Cleanup**: Old logs can be automatically removed
- **Optional Detailed Logging**: Can be disabled if only console logging is needed

## Future Enhancements

Potential future improvements:

- **Log Compression**: Compress old log files to save space
- **Database Storage**: Store logs in SQLite for easier querying
- **Real-time Monitoring**: WebSocket endpoint for live log streaming
- **Log Analysis Dashboard**: Web interface for log analysis
- **Metrics Collection**: Aggregate statistics about tool usage and performance
