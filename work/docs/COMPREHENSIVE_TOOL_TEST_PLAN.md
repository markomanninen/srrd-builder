# Comprehensive Tool Test Plan

**SRRD Builder MCP Tools - Testing Project Path Usage and Database Logging**

*Created: July 22, 2025*

## Executive Summary

This document outlines a comprehensive test plan to verify that all SRRD Builder MCP tools handle project path parameters correctly and perform database logging as required. We'll start with methodology advisory tools as the prototype, then extend to all tool categories.

## Test Objectives

### Primary Goals
1. **Verify project path handling** - Test tools with and without project_path parameter
2. **Confirm database logging** - Ensure all tool calls are logged to SQLite database
3. **Validate response quality** - Check that tools provide appropriate responses
4. **Test context-aware behavior** - Verify `@context_aware()` decorator functionality

### Secondary Goals
1. **Performance testing** - Measure tool execution times
2. **Error handling** - Test edge cases and invalid inputs
3. **Integration testing** - Verify tool interactions with storage systems

## Tool Categories Analysis

### 1. Methodology Advisory Tools (PROTOTYPE - START HERE)

**Location**: `work/code/mcp/tools/methodology_advisory.py`
**Test File**: `work/tests/unit/tools/test_methodology_advisory.py`

**Tools to Test**:
- `explain_methodology(**kwargs)`
- `compare_approaches(**kwargs)` 
- `validate_design(**kwargs)`
- `ensure_ethics(**kwargs)`

**Current Implementation Analysis**:
```python
# All tools use @context_aware() decorator
@context_aware()
async def explain_methodology(**kwargs) -> str:
    # Tools filter out project_path - they don't use it
    research_question = kwargs.get("research_question")
    domain = kwargs.get("domain")
    # No project_path usage - these are "advisory" tools
```

**Expected Behavior**:
- **With project_path**: Should work and log usage to database
- **Without project_path**: Should work but may not log to database (needs verification)
- **Invalid inputs**: Should return proper error messages
- **Response format**: Should return JSON with structured guidance

### 2. Research Planning Tools

**Location**: `work/code/mcp/tools/research_planning.py`
**Test File**: `work/tests/unit/tools/test_research_planning.py` ✅ (exists)

**Tools to Test**:
- `clarify_research_goals(**kwargs)`
- `suggest_methodology(**kwargs)`

### 3. Quality Assurance Tools  

**Location**: `work/code/mcp/tools/quality_assurance.py`
**Test File**: `work/tests/unit/tools/test_quality_assurance.py` ✅ (exists)

**Tools to Test**:
- `simulate_peer_review(**kwargs)`
- `check_quality_gates(**kwargs)`

### 4. Novel Theory Development Tools

**Location**: `work/code/mcp/tools/novel_theory_development.py`
**Test File**: `work/tests/unit/tools/test_novel_theory_development.py` ✅ (exists)

**Tools to Test**: (Multiple tools - need to enumerate)

### 5. Search Discovery Tools

**Location**: `work/code/mcp/tools/search_discovery.py`
**Test File**: `work/tests/unit/tools/test_search_discovery.py` ✅ (exists)

**Tools to Test**:
- `semantic_search_tool(**kwargs)`
- Other search tools

### 6. Document Generation Tools

**Location**: `work/code/mcp/tools/document_generation.py`
**Test File**: `work/tests/unit/tools/test_document_generation.py` ❌ (MISSING)

**Expected Behavior**: Should use project_path when available, work without it

### 7. Research Continuity Tools

**Location**: `work/code/mcp/tools/research_continuity.py`
**Test File**: `work/tests/unit/tools/test_research_continuity.py` ❌ (MISSING)

**Expected Behavior**: REQUIRE project_path (these manage research state)

### 8. Storage Management Tools

**Location**: `work/code/mcp/tools/storage_management.py`
**Test File**: `work/tests/unit/tools/test_storage_management.py` ❌ (MISSING)

**Expected Behavior**: Special handling (init/switch/reset have unique requirements)

## Detailed Test Plan for Methodology Advisory Tools

### Test Structure

```python
# Test file: work/tests/unit/tools/test_methodology_advisory.py

class TestMethodologyAdvisoryProjectPath:
    """Test project path handling for methodology advisory tools"""
    
    @pytest.mark.asyncio
    async def test_explain_methodology_with_project_path(self):
        """Test explain_methodology with project_path provided"""
        
    @pytest.mark.asyncio  
    async def test_explain_methodology_without_project_path(self):
        """Test explain_methodology without project_path"""
        
    @pytest.mark.asyncio
    async def test_explain_methodology_database_logging(self):
        """Verify database logging occurs when project_path available"""

class TestMethodologyAdvisoryFunctionality:
    """Test core functionality of methodology advisory tools"""
    
    @pytest.mark.asyncio
    async def test_explain_methodology_valid_inputs(self):
        """Test with valid research question and domain"""
        
    @pytest.mark.asyncio
    async def test_explain_methodology_invalid_inputs(self):
        """Test error handling with missing parameters"""
```

### Required Test Infrastructure

**1. Database Logging Verification**:
```python
async def verify_tool_logging(tool_func, tool_name, **kwargs):
    """Helper to verify tool usage is logged to database"""
    # Setup test database
    # Call tool
    # Verify log entry exists with correct tool_name
    # Return log entry for further verification
```

**2. Project Path Context Setup**:
```python
@pytest.fixture
async def test_project_context():
    """Create test project with proper .srrd structure"""
    # Create temp directory with .srrd/data/sessions.db
    # Initialize SQLiteManager
    # Yield project_path and db manager
    # Cleanup
```

**3. Mock Context Detector**:
```python
@pytest.fixture
def mock_context_detector():
    """Mock context detector for testing different scenarios"""
    # Mock successful context detection
    # Mock failed context detection
    # Return configurable mock
```

### Test Cases for Each Tool

#### 1. explain_methodology Tests

**Required Parameters**: `research_question`, `domain`
**Optional Parameters**: `methodology_type`

```python
TEST_CASES = [
    # Valid cases
    {
        "research_question": "How does exercise affect memory?",
        "domain": "psychology", 
        "expected_status": "success"
    },
    {
        "research_question": "What causes climate change?",
        "domain": "environmental_science",
        "methodology_type": "observational",
        "expected_status": "success"
    },
    
    # Error cases
    {
        "domain": "psychology",  # missing research_question
        "expected_status": "error",
        "expected_error": "Missing required parameters"
    },
    {
        "research_question": "How does exercise affect memory?",
        # missing domain
        "expected_status": "error",
        "expected_error": "Missing required parameters"
    }
]
```

#### 2. compare_approaches Tests

**Required Parameters**: `approach_a`, `approach_b`, `research_context`

#### 3. validate_design Tests

**Required Parameters**: `research_design`, `domain`
**Optional Parameters**: `constraints`

#### 4. ensure_ethics Tests

**Required Parameters**: `research_proposal`, `domain`
**Optional Parameters**: `participant_type`

### Database Logging Test Specification

**For each tool, verify**:
1. **Tool usage logged** when project_path available
2. **Session ID creation/reuse** in database
3. **Research act/category tracking** (if applicable)
4. **Success/failure status** logged correctly
5. **Execution time** recorded
6. **Tool arguments** stored (sanitized)

### Response Quality Tests

**For each tool, verify**:
1. **JSON format** response (where applicable)
2. **Required fields** present in response
3. **User interaction guidance** provided
4. **Next step options** included
5. **Error messages** are clear and actionable

## Implementation Phase Plan

### Phase 1: Methodology Advisory Tools (Week 1)
1. ✅ **Enhance existing test file** with comprehensive project path tests
2. ✅ **Add database logging verification** infrastructure
3. ✅ **Implement response quality validation** tests
4. ✅ **Create reusable test utilities** for other tool categories

### Phase 2: Advisory Tool Categories (Week 2)
1. 🔧 **Research Planning Tools** - Apply same test pattern
2. 🔧 **Quality Assurance Tools** - Apply same test pattern  
3. 🔧 **Novel Theory Development Tools** - Apply same test pattern

### Phase 3: Storage-Dependent Tools (Week 3)
1. 📝 **Document Generation Tools** - Test project_path usage patterns
2. 📝 **Search Discovery Tools** - Test database and vector storage integration
3. 📝 **Research Continuity Tools** - Test REQUIRED project_path behavior
4. 📝 **Storage Management Tools** - Test special init/switch/reset behaviors

### Phase 4: Integration and Performance (Week 4)
1. 🚀 **Cross-tool workflow tests** - Test tool interactions
2. 🚀 **Performance benchmarking** - Measure execution times
3. 🚀 **Error handling edge cases** - Comprehensive error testing
4. 🚀 **Documentation updates** - Update tool documentation based on findings

## Success Criteria

### Tool-Level Success Criteria
- ✅ **100% test coverage** for project path handling
- ✅ **Database logging verification** for all applicable tools
- ✅ **Response quality validation** passes
- ✅ **Error handling** works correctly

### System-Level Success Criteria  
- ✅ **Consistent behavior** across all tool categories
- ✅ **PROJECT_PATH as single source of truth** verified
- ✅ **Research lifecycle tracking** complete
- ✅ **No custom fallback logic** in advisory tools

## Test Execution Strategy

### **NEW: Enhanced Frontend Batch Testing**

**🚀 Batch Execution Testing**:
```bash
# Frontend batch execution testing
cd work/code/mcp/frontend
python3 -m http.server 8080

# Navigate to http://localhost:8080
# Use new batch execution features:
```

**Batch Testing Workflow**:
1. **Full Workflow Testing**: Click "🚀 Run All Tools" - tests all 44 tools in dependency order
2. **Research Act Testing**: Click "▶️ Run All Tools" on each research act card
3. **Category Testing**: Click "▶️ Run Category" on each category card
4. **Progress Monitoring**: Watch real-time progress bars and success/failure tracking
5. **Results Analysis**: Review comprehensive batch summary reports

**Group Testing Categories**:
- **Conceptualization Tools**: Goal setting, problem identification, critical thinking
- **Design & Planning Tools**: Methodology, experimental design, ethics validation
- **Knowledge Acquisition Tools**: Literature search, data collection, source management
- **Analysis & Synthesis Tools**: Data analysis, pattern recognition, knowledge building
- **Validation & Refinement Tools**: Peer review, quality control, paradigm validation
- **Communication Tools**: Document generation, formatting, project management

### Automated Testing
```bash
# Run all methodology advisory tests
pytest work/tests/unit/tools/test_methodology_advisory.py -v

# Run project path specific tests
pytest work/tests/unit/tools/ -k "project_path" -v

# Run database logging tests
pytest work/tests/unit/tools/ -k "database_logging" -v

# Run all tool tests with coverage
pytest work/tests/unit/tools/ --cov=work/code/mcp/tools --cov-report=html

# NEW: Frontend batch execution integration tests
cd work/code/mcp/frontend
python3 test_batch_execution.py  # Run automated batch tests
```

### Manual Verification
1. **MCP server integration testing** - Test with actual Claude Desktop
2. **Global launcher PROJECT_PATH testing** - Verify environment variable usage
3. **Project switching workflow** - Test init/switch/reset sequence
4. **Cross-platform testing** - Verify on macOS/Windows/Linux
5. **NEW: Batch execution verification** - Test complete research workflows through frontend
6. **NEW: Dependency order validation** - Verify tools run in proper sequence
7. **NEW: Error handling testing** - Verify smart fallbacks and retry logic

## Risk Mitigation

### Testing Risks
- **Database setup complexity** - Use temporary databases for tests
- **Context detector mocking** - Isolate context-aware behavior testing
- **Tool dependency issues** - Handle import failures gracefully
- **NEW: Batch execution timing** - Tools may timeout or interfere with each other
- **NEW: Frontend integration complexity** - WebSocket connections and state management

### Implementation Risks
- **Breaking existing functionality** - Run regression tests
- **Performance degradation** - Benchmark before/after changes
- **Cross-tool compatibility** - Test tool interaction workflows
- **NEW: Batch execution resource usage** - Monitor memory and CPU during large batches
- **NEW: Dependency order failures** - Ensure proper error handling when prerequisites fail

## Deliverables

### Test Infrastructure
1. **Enhanced test files** for all tool categories
2. **Reusable test utilities** for project path and logging verification
3. **Mock infrastructure** for context detection and database testing
4. **Performance benchmarking** framework
5. **NEW: Batch execution test framework** for frontend integration testing
6. **NEW: Dependency order validation utilities** for workflow testing
7. **NEW: Progress tracking test infrastructure** for UI verification

### Documentation Updates
1. **Updated PROJECT_PATH_USAGE_ANALYSIS.md** with test findings
2. **NEW: Frontend batch execution user guide** with testing procedures
3. **NEW: Dependency management documentation** for tool workflow ordering
4. **NEW: Performance benchmarking results** for batch execution capabilities
2. **Tool behavior documentation** with verified patterns
3. **Testing guidelines** for future tool development
4. **Integration testing procedures** for MCP server

### Code Changes
1. **Fixed project path handling** where inconsistencies found
2. **Enhanced error messages** based on test findings
3. **Improved logging coverage** for research lifecycle tracking
4. **Standardized tool response formats** where needed

---

**Next Action**: Start with implementing enhanced tests for methodology advisory tools as the prototype for all other tool categories.
