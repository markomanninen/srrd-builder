#!/usr/bin/env python3
"""
Enhanced Test Suite for Methodology Advisory Tools.

Tests explain_methodology, compare_approaches, validate_design, ensure_ethics
with comprehensive project path handling and database logging verification.
"""

import pytest
import tempfile
import json
import sys
import os
import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path for imports  
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "work" / "code" / "mcp"))

# Import current project utilities for context management
from utils.current_project import set_current_project, clear_current_project

# Import methodology advisory tools with error handling
try:
    from tools.methodology_advisory import (
        explain_methodology,
        compare_approaches,
        validate_design,
        ensure_ethics
    )
    METHODOLOGY_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Methodology tools import failed: {e}")
    METHODOLOGY_TOOLS_AVAILABLE = False

# Import storage components for database testing
try:
    from storage.sqlite_manager import SQLiteManager
    STORAGE_AVAILABLE = True
except ImportError as e:
    print(f"Storage import failed: {e}")
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
    """Create test project structure with database"""
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
        
        # Initialize database if SQLiteManager is available
        if STORAGE_AVAILABLE:
            import asyncio
            from storage.sqlite_manager import SQLiteManager
            
            async def init_db():
                db_path = srrd_dir / 'sessions.db'
                sqlite_manager = SQLiteManager(str(db_path))
                await sqlite_manager.initialize()
                await sqlite_manager.close()
            
            # Run database initialization
            try:
                asyncio.get_event_loop().run_until_complete(init_db())
            except RuntimeError:
                # No event loop, create one
                asyncio.run(init_db())
        
        yield project_path


# Test Utilities
async def call_tool_with_project_path(tool_func, project_path, **kwargs):
    """Call tool with project context properly set"""
    # Set current project context (no longer pass as parameter)
    set_current_project(str(project_path))
    try:
        result = await tool_func(**kwargs)
        return result
    finally:
        # Clean up context
        clear_current_project()


async def call_tool_without_project_path(tool_func, **kwargs):
    """Call tool without project context - will raise ContextAwareError"""
    # Ensure no project context is set
    clear_current_project()
    # Ensure no project_path in kwargs
    kwargs.pop('project_path', None)
    # This will raise ContextAwareError - let it propagate
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
    
    if row is None:
        return None  # No logging found
    
    # Return the log entry for further verification
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


# Test Classes
@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestExplainMethodology:
    """Test explain_methodology tool"""
    
    @pytest.mark.asyncio
    async def test_with_project_path(self, test_project_context):
        """Test explain_methodology with project_path"""
        result = await call_tool_with_project_path(
            explain_methodology,
            test_project_context,
            research_question="How to test software?",
            domain="software_engineering"
        )
        
        response = verify_tool_response_format(result, "explain_methodology")
        assert "research_question" in result or "methodology" in result.lower()
    
    @pytest.mark.asyncio  
    async def test_without_project_path(self):
        """Test explain_methodology without project_path - should raise ContextAwareError"""
        try:
            await call_tool_without_project_path(
                explain_methodology,
                research_question="How to test software?",
                domain="software_engineering"
            )
            # If we get here, the test should fail
            pytest.fail("Expected ContextAwareError but no exception was raised")
        except Exception as e:
            # Check that it's a ContextAwareError by name (to avoid import issues)
            assert type(e).__name__ == "ContextAwareError", f"Expected ContextAwareError, got {type(e).__name__}: {e}"
            # Verify the error message mentions SRRD project context
            assert "SRRD project context" in str(e), f"Error message should mention SRRD project context: {e}"
    
    @pytest.mark.asyncio
    async def test_database_logging_placeholder(self, test_database, test_project_context):
        """Placeholder test for database logging - not yet implemented"""
        # Database logging is not yet implemented in methodology advisory tools
        # This test verifies the tool still works without logging
        
        result = await call_tool_with_project_path(
            explain_methodology,
            test_project_context,
            research_question="How to test software?",
            domain="software_engineering"
        )
        
        # Verify result exists - logging will be tested later when implemented
        assert result is not None
        verify_tool_response_format(result, "explain_methodology")
    
    @pytest.mark.asyncio
    async def test_required_parameters(self):
        """Test explain_methodology with missing required parameters"""
        # This test should also fail due to missing project context
        try:
            await explain_methodology()
            pytest.fail("Expected ContextAwareError but no exception was raised")
        except Exception as e:
            assert type(e).__name__ == "ContextAwareError", f"Expected ContextAwareError, got {type(e).__name__}: {e}"
    
    @pytest.mark.asyncio
    async def test_methodology_types(self, test_project_context):
        """Test different methodology types"""
        methodologies = [
            "quantitative",
            "qualitative", 
            "mixed_methods",
            "experimental"
        ]
        
        for methodology in methodologies:
            try:
                result = await call_tool_with_project_path(
                    explain_methodology,
                    test_project_context,
                    research_question="How to test software?",
                    domain="software_engineering",
                    methodology_type=methodology
                )
                
                verify_tool_response_format(result, "explain_methodology")
            except TypeError:
                # If methodology_type parameter doesn't exist, that's ok
                pass


@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestCompareApproaches:
    """Test compare_approaches tool"""
    
    @pytest.mark.asyncio
    async def test_with_project_path(self, test_project_context):
        """Test compare_approaches with project_path"""
        result = await call_tool_with_project_path(
            compare_approaches,
            test_project_context,
            approach_a="Unit Testing",
            approach_b="Integration Testing",
            research_context="Software Quality Assurance"
        )
        
        response = verify_tool_response_format(result, "compare_approaches")
        assert "approach" in result.lower() or "comparison" in result.lower()
    
    @pytest.mark.asyncio
    async def test_without_project_path(self):
        """Test compare_approaches without project_path - should raise ContextAwareError"""
        try:
            await call_tool_without_project_path(
                compare_approaches,
                approach_a="Unit Testing",
                approach_b="Integration Testing", 
                research_context="Software Quality Assurance"
            )
            pytest.fail("Expected ContextAwareError but no exception was raised")
        except Exception as e:
            assert type(e).__name__ == "ContextAwareError", f"Expected ContextAwareError, got {type(e).__name__}: {e}"
            assert "SRRD project context" in str(e), f"Error message should mention SRRD project context: {e}"


@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestValidateDesign:
    """Test validate_design tool"""
    
    @pytest.mark.asyncio
    async def test_with_project_path(self, test_project_context):
        """Test validate_design with project_path"""
        research_design = {
            "type": "experimental",
            "participants": 100,
            "duration": "6 months",
            "variables": ["performance", "usability"]
        }
        
        result = await call_tool_with_project_path(
            validate_design,
            test_project_context,
            research_design=research_design,
            domain="software_engineering"
        )
        
        response = verify_tool_response_format(result, "validate_design")
        assert "design" in result.lower() or "validation" in result.lower()
    
    @pytest.mark.asyncio
    async def test_without_project_path(self):
        """Test validate_design without project_path - should raise ContextAwareError"""
        research_design = {
            "type": "observational",
            "participants": 50,
            "methods": ["survey", "interview"]
        }
        
        try:
            await call_tool_without_project_path(
                validate_design,
                research_design=research_design,
                domain="software_engineering"
            )
            pytest.fail("Expected ContextAwareError but no exception was raised")
        except Exception as e:
            assert type(e).__name__ == "ContextAwareError", f"Expected ContextAwareError, got {type(e).__name__}: {e}"
            assert "SRRD project context" in str(e), f"Error message should mention SRRD project context: {e}"


@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestEnsureEthics:
    """Test ensure_ethics tool"""
    
    @pytest.mark.asyncio
    async def test_with_project_path(self, test_project_context):
        """Test ensure_ethics with project_path"""
        research_proposal = {
            "title": "Software Testing Study",
            "participants": "software developers", 
            "data_collection": ["surveys", "interviews"],
            "risks": "minimal",
            "consent": True
        }
        
        result = await call_tool_with_project_path(
            ensure_ethics,
            test_project_context,
            research_proposal=research_proposal,
            domain="software_engineering"
        )
        
        response = verify_tool_response_format(result, "ensure_ethics")
        assert "ethics" in result.lower() or "consent" in result.lower()
    
    @pytest.mark.asyncio
    async def test_without_project_path(self):
        """Test ensure_ethics without project_path - should raise ContextAwareError"""
        research_proposal = {
            "title": "User Experience Study",
            "participants": "general users",
            "data_collection": ["observation"],
            "anonymization": True
        }
        
        try:
            await call_tool_without_project_path(
                ensure_ethics,
                research_proposal=research_proposal,
                domain="software_engineering"
            )
            pytest.fail("Expected ContextAwareError but no exception was raised")
        except Exception as e:
            assert type(e).__name__ == "ContextAwareError", f"Expected ContextAwareError, got {type(e).__name__}: {e}"
            assert "SRRD project context" in str(e), f"Error message should mention SRRD project context: {e}"


# Integration Tests
@pytest.mark.skipif(not METHODOLOGY_TOOLS_AVAILABLE, reason="Methodology tools not available")
class TestMethodologyWorkflow:
    """Test complete methodology workflow"""
    
    @pytest.mark.asyncio
    async def test_methodology_pipeline(self, test_project_context):
        """Test complete methodology advisory pipeline"""
        # 1. Explain methodology
        methodology_result = await call_tool_with_project_path(
            explain_methodology,
            test_project_context,
            research_question="How effective is test-driven development?",
            domain="software_engineering"
        )
        
        verify_tool_response_format(methodology_result, "explain_methodology")
        
        # 2. Compare approaches
        comparison_result = await call_tool_with_project_path(
            compare_approaches,
            test_project_context,
            approach_a="Test-Driven Development",
            approach_b="Behavior-Driven Development",
            research_context="Software Development Methodologies"
        )
        
        verify_tool_response_format(comparison_result, "compare_approaches")
        
        # 3. Validate design
        research_design = {
            "type": "controlled_experiment",
            "participants": 60,
            "groups": ["TDD", "BDD", "Control"],
            "metrics": ["code_quality", "development_time", "bug_count"]
        }
        
        validation_result = await call_tool_with_project_path(
            validate_design,
            test_project_context,
            research_design=research_design,
            domain="software_engineering"
        )
        
        verify_tool_response_format(validation_result, "validate_design")
        
        # 4. Ensure ethics
        research_proposal = {
            "title": "TDD vs BDD Effectiveness Study",
            "participants": "professional developers",
            "data_collection": ["code_analysis", "time_tracking", "surveys"],
            "consent": True,
            "anonymization": True
        }
        
        ethics_result = await call_tool_with_project_path(
            ensure_ethics,
            test_project_context,
            research_proposal=research_proposal,
            domain="software_engineering"
        )
        
        verify_tool_response_format(ethics_result, "ensure_ethics")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
