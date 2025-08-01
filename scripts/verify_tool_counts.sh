#!/bin/bash

# SRRD-Builder Tool Count Verification Script
# ==========================================
# 
# Comprehensive verification that all 52 research tools are properly
# registered and available across all system components.
#
# This script verifies:
# 1. Python MCP server tool registration
# 2. Frontend JavaScript tool definitions
# 3. Tool distribution across modules
# 4. Specific enhanced progress tracking tools
#
# For detailed documentation, see: work/docs/TEST_SUITE.md
#
# Usage: bash scripts/verify_tool_counts.sh
# Expected: All verifications should show 52 tools

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔢 SRRD-Builder Tool Count Verification"
echo "========================================"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if required directories exist
if [[ ! -d "work/code/mcp" ]]; then
    echo "❌ Error: work/code/mcp directory not found"
    echo "   Make sure you're running this from the project root"
    exit 1
fi

if [[ ! -d "work/code/mcp/frontend/data" ]]; then
    echo "❌ Error: Frontend data directory not found"
    exit 1
fi

echo "1. 🐍 Python MCP Server Tool Registration"
echo "----------------------------------------"

cd work/code/mcp

python3 -c "
import sys
from pathlib import Path

# Add MCP directory to Python path
mcp_dir = Path('.')
sys.path.insert(0, str(mcp_dir))
sys.path.insert(0, str(mcp_dir / 'utils'))

# Mock server to count tool registrations
class MockServer:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name, description, parameters, handler):
        self.tools[name] = {
            'name': name,
            'description': description,
            'parameters': parameters,
            'handler': handler
        }

# Create mock server and register all tools
server = MockServer()

try:
    from tools import register_all_tools
    register_all_tools(server)
    
    print(f'✅ Python MCP Server: {len(server.tools)} tools registered')
    
    # Verify expected count
    if len(server.tools) == 52:
        print('✅ Tool count matches expected: 52 tools')
    else:
        print(f'❌ Tool count mismatch: expected 52, got {len(server.tools)}')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Error registering tools: {e}')
    sys.exit(1)
" 2>&1 | grep -v "Registered.*tools from" | grep -v "Total tools registered"

echo ""
echo "2. 🌐 Frontend JavaScript Tool Definitions"
echo "------------------------------------------"

# Check tool-info.js
if [[ -f "frontend/data/tool-info.js" ]]; then
    TOOL_INFO_COUNT=$(grep -c "': {$" frontend/data/tool-info.js)
    echo "✅ tool-info.js: $TOOL_INFO_COUNT tools"
    
    if [[ $TOOL_INFO_COUNT -eq 52 ]]; then
        echo "✅ tool-info.js count matches expected: 52 tools"
    else
        echo "❌ tool-info.js count mismatch: expected 52, got $TOOL_INFO_COUNT"
        exit 1
    fi
else
    echo "❌ Error: frontend/data/tool-info.js not found"
    exit 1
fi

# Check research-framework.js
if [[ -f "frontend/data/research-framework.js" ]]; then
    FRAMEWORK_COUNT=$(grep -A 1000 "const expectedTools = \[" frontend/data/research-framework.js | grep -B 1000 "^];" | grep -c "'")
    echo "✅ research-framework.js expectedTools: $FRAMEWORK_COUNT tools"
    
    if [[ $FRAMEWORK_COUNT -eq 52 ]]; then
        echo "✅ research-framework.js count matches expected: 52 tools"
    else
        echo "❌ research-framework.js count mismatch: expected 52, got $FRAMEWORK_COUNT"
        exit 1
    fi
else
    echo "❌ Error: frontend/data/research-framework.js not found"
    exit 1
fi

echo ""
echo "3. 📊 Tool Distribution by Module"
echo "---------------------------------"

python3 -c "
import sys
from pathlib import Path
import inspect

# Add MCP directory to Python path
mcp_dir = Path('.')
sys.path.insert(0, str(mcp_dir))
sys.path.insert(0, str(mcp_dir / 'utils'))

# Import all tool registration functions
try:
    from tools.research_continuity import register_research_continuity_tools
    from tools.research_planning import register_research_tools
    from tools.methodology_advisory import register_methodology_tools
    from tools.novel_theory_development import register_novel_theory_tools
    from tools.quality_assurance import register_quality_tools
    from tools.document_generation import register_document_tools
    from tools.search_discovery import register_search_tools
    from tools.storage_management import register_storage_tools
    from tools.vector_database import register_vector_database_tools
    
    modules = {
        'Research Continuity': register_research_continuity_tools,
        'Research Planning': register_research_tools,
        'Methodology Advisory': register_methodology_tools,
        'Novel Theory Development': register_novel_theory_tools,
        'Quality Assurance': register_quality_tools,
        'Document Generation': register_document_tools,
        'Search Discovery': register_search_tools,
        'Storage Management': register_storage_tools,
        'Vector Database': register_vector_database_tools
    }
    
    total = 0
    expected_distribution = {
        'Research Continuity': 10,
        'Research Planning': 3,
        'Methodology Advisory': 4,
        'Novel Theory Development': 9,
        'Quality Assurance': 2,
        'Document Generation': 8,
        'Search Discovery': 6,
        'Storage Management': 8,
        'Vector Database': 2
    }
    
    all_good = True
    
    for name, func in modules.items():
        source = inspect.getsource(func)
        count = source.count('server.register_tool')
        total += count
        expected = expected_distribution[name]
        
        if count == expected:
            print(f'✅ {name}: {count} tools')
        else:
            print(f'❌ {name}: {count} tools (expected {expected})')
            all_good = False
    
    print(f'')
    if total == 52 and all_good:
        print(f'✅ Total distribution: {total} tools (matches expected)')
    else:
        print(f'❌ Total distribution: {total} tools (expected 52)')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Error checking tool distribution: {e}')
    sys.exit(1)
"

echo ""
echo "4. 🎯 Enhanced Progress Tracking Tools"
echo "-------------------------------------"

python3 -c "
import sys
from pathlib import Path

# Add MCP directory to Python path
mcp_dir = Path('.')
sys.path.insert(0, str(mcp_dir))
sys.path.insert(0, str(mcp_dir / 'utils'))

# Mock server to check specific tools
class MockServer:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name, description, parameters, handler):
        self.tools[name] = True

server = MockServer()

try:
    from tools import register_all_tools
    register_all_tools(server)
    
    # Check for new enhanced progress tracking tools
    new_tools = ['get_visual_progress_summary', 'detect_and_celebrate_milestones']
    all_found = True
    
    for tool in new_tools:
        if tool in server.tools:
            print(f'✅ {tool}: Found')
        else:
            print(f'❌ {tool}: Missing')
            all_found = False
    
    if all_found:
        print('✅ All enhanced progress tracking tools are registered')
    else:
        print('❌ Some enhanced progress tracking tools are missing')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Error checking enhanced progress tracking tools: {e}')
    sys.exit(1)
" 2>&1 | grep -v "Registered.*tools from" | grep -v "Total tools registered"

echo ""
echo "5. 🧪 Test Coverage Verification"
echo "--------------------------------"

cd "$PROJECT_ROOT"

# Check if test files exist
if [[ -f "work/tests/unit/tools/test_enhanced_progress_tracking.py" ]]; then
    echo "✅ Unit tests found: test_enhanced_progress_tracking.py"
else
    echo "❌ Unit tests missing: test_enhanced_progress_tracking.py"
    exit 1
fi

if [[ -f "work/tests/integration/test_enhanced_progress_integration.py" ]]; then
    echo "✅ Integration tests found: test_enhanced_progress_integration.py"
else
    echo "❌ Integration tests missing: test_enhanced_progress_integration.py"
    exit 1
fi

echo ""
echo "6. 📝 Documentation Verification"
echo "--------------------------------"

# Check if documentation has been updated
if grep -q "52 research tools" README.md; then
    echo "✅ Main README.md updated with correct tool count"
else
    echo "❌ Main README.md not updated with correct tool count"
    exit 1
fi

if grep -q "52 Context-Aware Tools" work/code/mcp/README.md; then
    echo "✅ MCP README.md updated with correct tool count"
else
    echo "❌ MCP README.md not updated with correct tool count"
    exit 1
fi

if grep -q "52 research tools" work/docs/TEST_SUITE.md; then
    echo "✅ TEST_SUITE.md updated with verification scripts"
else
    echo "❌ TEST_SUITE.md not updated with verification scripts"
    exit 1
fi

echo ""
echo "🎉 VERIFICATION COMPLETE"
echo "======================="
echo "✅ All 52 research tools are properly registered and available"
echo "✅ Frontend integration is complete and consistent"
echo "✅ Tool distribution matches expected values"
echo "✅ Enhanced progress tracking tools are integrated"
echo "✅ Test coverage is in place"
echo "✅ Documentation is updated"
echo ""
echo "System is ready for production use with all 52 tools verified!"