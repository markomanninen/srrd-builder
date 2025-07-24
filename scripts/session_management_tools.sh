#!/bin/bash
# SESSION MANAGEMENT TOOL TEST SCRIPT
# This script creates a temp project and tests session management tools in natural order.
# All output is logged and printed for debugging.

LOG_FILE="$(dirname "$0")/session_management_tools.log"
trap 'exit 130' INT
run_cmd() {
  local label="$1"
  local cmd="$2"
  echo "" | tee -a "$LOG_FILE"
  echo "Running command: $label " | tee -a "$LOG_FILE"
  (echo "$cmd" | timeout 10s python3 work/code/mcp/server.py --stdio 2>/dev/null | grep -Eo '\{.*\}' || true) | tee -a "$LOG_FILE"
}

# 1. Initialize temp project
SESSION_PROJECT_NAME="Session Test Project $(date +%Y%m%d%H%M%S)"
SESSION_PROJECT_PATH="/tmp/session_test_project_$(date +%Y%m%d%H%M%S)"
run_cmd "1. initialize_project" '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "initialize_project", "arguments": {"name": "'"${SESSION_PROJECT_NAME}"'", "description": "Session test project", "domain": "Test", "project_path": "'"${SESSION_PROJECT_PATH}"'"}}}'

# 2. Start a research session
run_cmd "2. start_research_session" '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "start_research_session", "arguments": {"research_act": "planning", "research_focus": "Session tool test"}}}'

# 3. Save session
run_cmd "3. save_session" '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "save_session", "arguments": {"session_data": {"note": "Session save test", "phase": "planning"}}}}'

# 4. Get session summary
run_cmd "4. get_session_summary" '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_session_summary", "arguments": {}}}'

# 5. Get research milestones
run_cmd "5. get_research_milestones" '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_research_milestones", "arguments": {}}}'

# 6. Get research progress
run_cmd "6. get_research_progress" '{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "get_research_progress", "arguments": {}}}'

# 7. Get tool usage history
run_cmd "7. get_tool_usage_history" '{"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "get_tool_usage_history", "arguments": {}}}'

# 8. Get tool usage history with session ID
run_cmd "8. get_tool_usage_history" '{"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "get_tool_usage_history", "arguments": {"session_id": 1}}}'

# 8. Restore session (using session_id=1 for demo; adjust as needed)
run_cmd "9. restore_session" '{"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "restore_session", "arguments": {"session_id": 1}}}'

# 9. Reset project context
run_cmd "10. reset_project_context" '{"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "reset_project_context", "arguments": {}}}'

exit 0
