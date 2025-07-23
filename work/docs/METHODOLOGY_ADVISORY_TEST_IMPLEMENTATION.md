# Methodology Advisory Tools Test Implementation Plan

**Immediate Implementation Steps for Testing Project Path Usage and Database Logging**

*Created: July 22, 2025*

## Current State Analysis

### Existing Test File Status
- **File**: `work/tests/unit/tools/test_methodology_advisory.py`
- **Current Tests**: Basic functionality tests without project path verification
- **Missing**: Database logging verification, project path handling, comprehensive error testing

### Tools to Test
1. `explain_methodology(**kwargs)`
2. `compare_approaches(**kwargs)`
3. `validate_design(**kwargs)`
4. `ensure_ethics(**kwargs)`

## Required Test Infrastructure Changes

### 1. Database Testing Setup

**Add to test file**:
```python
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import storage components
try:
    from storage.sqlite_manager import SQLiteManager
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False

@pytest.fixture
async def test_database():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    if STORAGE_AVAILABLE:
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        yield sqlite_manager, db_path
        await sqlite_manager.close()
    else:
        yield None, db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def test_project_context():
    """Create test project structure"""
    with tempfile.TemporaryDirectory(prefix="srrd_test_") as temp_dir:
        project_path = Path(temp_dir)
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir()
        
        # Create config
        config = {
            "project_name": "Test Project",
            "domain": "test",
            "version": "0.1.0"
        }
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f)
        
        yield project_path
```

### 2. Project Path Testing Utilities

**Add helper functions**:
```python
async def call_tool_with_project_path(tool_func, project_path, **kwargs):
    """Call tool with project_path and verify behavior"""
    kwargs['project_path'] = str(project_path)
    result = await tool_func(**kwargs)
    return result

async def call_tool_without_project_path(tool_func, **kwargs):
    """Call tool without project_path and verify behavior"""
    # Ensure no project_path in kwargs
    kwargs.pop('project_path', None)
    result = await tool_func(**kwargs)
    return result

def verify_tool_response_format(response, tool_name):
    """Verify tool response has expected format"""
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Try to parse as JSON for structured responses
    try:
        parsed = json.loads(response)
        assert isinstance(parsed, dict)
        return parsed
    except json.JSONDecodeError:
        # Text response is also valid
        return {"raw_response": response}

async def verify_database_logging(sqlite_manager, tool_name, session_id=None):
    """Verify tool usage was logged to database"""
    if not sqlite_manager:
        pytest.skip("Database not available")
    
    # Query tool usage
    async with sqlite_manager.connection.execute(
        "SELECT * FROM tool_usage WHERE tool_name = ? ORDER BY timestamp DESC LIMIT 1",
        (tool_name,)
    ) as cursor:
        row = await cursor.fetchone()
    
    assert row is not None, f"No database entry found for tool: {tool_name}"
    
    # Return the log entry for further verification
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))
```

## Specific Test Cases to Implement

### Test Class 1: Project Path Handling

```python
@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestMethodologyAdvisoryProjectPath:
    """Test project path handling for methodology advisory tools"""
    
    @pytest.mark.asyncio
    async def test_explain_methodology_with_project_path(self, test_project_context):
        """Test explain_methodology with project_path provided"""
        result = await call_tool_with_project_path(
            explain_methodology,
            test_project_context,
            research_question="How does exercise affect memory?",
            domain="psychology"
        )
        
        response = verify_tool_response_format(result, "explain_methodology")
        assert "research_question" in response
        assert "methodology_analysis" in response
        
    @pytest.mark.asyncio
    async def test_explain_methodology_without_project_path(self):
        """Test explain_methodology without project_path"""
        result = await call_tool_without_project_path(
            explain_methodology,
            research_question="How does exercise affect memory?",
            domain="psychology"
        )
        
        # Should still work (advisory tools don't require project context)
        response = verify_tool_response_format(result, "explain_methodology")
        assert "research_question" in response
        
    @pytest.mark.asyncio
    async def test_compare_approaches_with_project_path(self, test_project_context):
        """Test compare_approaches with project_path provided"""
        result = await call_tool_with_project_path(
            compare_approaches,
            test_project_context,
            approach_a="experimental",
            approach_b="observational", 
            research_context="memory research"
        )
        
        response = verify_tool_response_format(result, "compare_approaches")
        assert "comparison" in response
        
    @pytest.mark.asyncio
    async def test_validate_design_with_project_path(self, test_project_context):
        """Test validate_design with project_path provided"""
        research_design = {
            "research_question": "Test question",
            "methodology": "experimental",
            "sample": {"size": 100, "representative": True}
        }
        
        result = await call_tool_with_project_path(
            validate_design,
            test_project_context,
            research_design=research_design,
            domain="psychology"
        )
        
        response = verify_tool_response_format(result, "validate_design")
        assert "validation_results" in response
        
    @pytest.mark.asyncio
    async def test_ensure_ethics_with_project_path(self, test_project_context):
        """Test ensure_ethics with project_path provided"""
        research_proposal = {
            "title": "Test Study",
            "participants": "adults",
            "risk_assessment": "minimal",
            "informed_consent": True
        }
        
        result = await call_tool_with_project_path(
            ensure_ethics,
            test_project_context,
            research_proposal=research_proposal,
            domain="psychology"
        )
        
        response = verify_tool_response_format(result, "ensure_ethics")
        assert "ethical_framework_analysis" in response
```

### Test Class 2: Database Logging Verification

```python
@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE or not STORAGE_AVAILABLE, 
                    reason="Methodology tools or storage not available")
class TestMethodologyAdvisoryDatabaseLogging:
    """Test database logging for methodology advisory tools"""
    
    @pytest.mark.asyncio
    async def test_explain_methodology_logging(self, test_database, test_project_context):
        """Verify explain_methodology usage is logged to database"""
        sqlite_manager, db_path = test_database
        if not sqlite_manager:
            pytest.skip("Database not available")
        
        # Create project and session
        project_id = await sqlite_manager.create_project(
            name="Test Project",
            description="Test project for logging verification",
            domain="psychology"
        )
        
        session_id = await sqlite_manager.create_session(
            project_id=project_id,
            session_type="test",
            user_id="test_user"
        )
        
        # Mock the MCP server's logging mechanism
        with patch('work.code.mcp.mcp_server.ClaudeMCPServer') as mock_server:
            mock_server.return_value.sqlite_manager = sqlite_manager
            
            result = await call_tool_with_project_path(
                explain_methodology,
                test_project_context,
                research_question="How does exercise affect memory?",
                domain="psychology"
            )
        
        # Verify tool was called successfully
        assert result is not None
        
        # Verify database logging (if integrated with MCP server)
        # Note: This requires integration with the MCP server's logging mechanism
        
    @pytest.mark.asyncio 
    async def test_all_methodology_tools_logging(self, test_database, test_project_context):
        """Test that all methodology advisory tools can be logged"""
        sqlite_manager, db_path = test_database
        if not sqlite_manager:
            pytest.skip("Database not available")
        
        # Test data for each tool
        tool_test_data = {
            "explain_methodology": {
                "research_question": "How does exercise affect memory?",
                "domain": "psychology"
            },
            "compare_approaches": {
                "approach_a": "experimental",
                "approach_b": "observational",
                "research_context": "memory research"
            },
            "validate_design": {
                "research_design": {"methodology": "experimental"},
                "domain": "psychology"
            },
            "ensure_ethics": {
                "research_proposal": {"title": "Test Study"},
                "domain": "psychology"
            }
        }
        
        # Test each tool
        for tool_name, test_args in tool_test_data.items():
            if tool_name == "explain_methodology":
                result = await call_tool_with_project_path(
                    explain_methodology, test_project_context, **test_args
                )
            elif tool_name == "compare_approaches":
                result = await call_tool_with_project_path(
                    compare_approaches, test_project_context, **test_args
                )
            elif tool_name == "validate_design":
                result = await call_tool_with_project_path(
                    validate_design, test_project_context, **test_args
                )
            elif tool_name == "ensure_ethics":
                result = await call_tool_with_project_path(
                    ensure_ethics, test_project_context, **test_args
                )
            
            # Verify tool executed successfully
            assert result is not None
            verify_tool_response_format(result, tool_name)
```

### Test Class 3: Error Handling and Edge Cases

```python
@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestMethodologyAdvisoryErrorHandling:
    """Test error handling for methodology advisory tools"""
    
    @pytest.mark.asyncio
    async def test_explain_methodology_missing_required_params(self):
        """Test explain_methodology with missing required parameters"""
        # Missing research_question
        result = await explain_methodology(domain="psychology")
        assert "Error: Missing required parameters" in result
        
        # Missing domain
        result = await explain_methodology(research_question="Test question")
        assert "Error: Missing required parameters" in result
        
        # Missing both
        result = await explain_methodology()
        assert "Error: Missing required parameters" in result
        
    @pytest.mark.asyncio
    async def test_compare_approaches_missing_required_params(self):
        """Test compare_approaches with missing required parameters"""
        # Missing approach_b
        result = await compare_approaches(
            approach_a="experimental",
            research_context="test"
        )
        assert "Error: Missing required parameters" in result
        
    @pytest.mark.asyncio
    async def test_validate_design_missing_required_params(self):
        """Test validate_design with missing required parameters"""
        # Missing research_design
        result = await validate_design(domain="psychology")
        assert "Error: Missing required parameters" in result
        
    @pytest.mark.asyncio
    async def test_ensure_ethics_missing_required_params(self):
        """Test ensure_ethics with missing required parameters"""
        # Missing research_proposal
        result = await ensure_ethics(domain="psychology")
        assert "Error: Missing required parameters" in result
```

## Implementation Steps

### Step 1: Update Test File Structure
1. **Backup existing test file**
2. **Add required imports** for database and project testing
3. **Add test fixtures** for database and project context setup
4. **Add utility functions** for project path testing

### Step 2: Implement Project Path Tests
1. **Add TestMethodologyAdvisoryProjectPath class** with all 4 tools
2. **Test with project_path** - verify tools work and get project context
3. **Test without project_path** - verify tools still work (advisory nature)
4. **Compare behavior** - document any differences

### Step 3: Implement Database Logging Tests
1. **Add TestMethodologyAdvisoryDatabaseLogging class**
2. **Mock MCP server logging** mechanism for integration testing
3. **Verify database entries** when project context available
4. **Test logging metadata** (tool name, arguments, execution time)

### Step 4: Implement Error Handling Tests
1. **Add TestMethodologyAdvisoryErrorHandling class**
2. **Test missing required parameters** for each tool
3. **Test invalid parameter types** where applicable
4. **Verify error message quality** and user guidance

### Step 5: Verification and Documentation
1. **Run all tests** and verify 100% pass rate
2. **Measure test coverage** for methodology advisory tools
3. **Document findings** regarding project path usage
4. **Update tool documentation** if behavior clarifications needed

## Expected Outcomes

### Test Results Documentation
- **Project path handling**: All tools should work with/without project_path
- **Database logging**: Integration point identified for MCP server logging
- **Error handling**: Comprehensive error message testing completed
- **Response format**: JSON structure validation for all tools

### Tool Behavior Verification
- **Advisory tools independence**: Confirm tools don't require specific project context
- **Response consistency**: Verify all tools provide user interaction guidance
- **Error message quality**: Ensure clear, actionable error messages

### Integration Points Identified
- **MCP server logging**: How advisory tools integrate with research lifecycle tracking
- **Context detector usage**: How `@context_aware()` decorator functions with advisory tools
- **Database requirements**: Whether advisory tools need database connectivity

## Next Steps After Methodology Advisory

1. **Apply same pattern** to research planning tools
2. **Extend to quality assurance** tools
3. **Test novel theory development** tools
4. **Create reusable test utilities** for all tool categories
5. **Document standardized testing approach** for future tool development

---

**Ready to implement**: Enhanced `test_methodology_advisory.py` with comprehensive project path and database logging verification.
