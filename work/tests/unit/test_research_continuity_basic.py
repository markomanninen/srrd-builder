"""
Simple test for research continuity tools - basic functionality validation
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))

from storage.sqlite_manager import SQLiteManager
from utils.research_framework import ResearchFrameworkService
from utils.workflow_intelligence import WorkflowIntelligence


@pytest.mark.asyncio
async def test_research_continuity_basic_functionality():
    """Test basic functionality of research continuity components"""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir) / 'test_project'
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create .srrd directory
    srrd_dir = project_path / '.srrd'
    srrd_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize database
        db_path = str(srrd_dir / 'sessions.db')
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        
        # Create test project
        project_id = await sqlite_manager.create_project(
            name="Test Research Project",
            description="A test project for continuity tools",
            domain="computer_science"
        )
        
        # Create test session
        session_id = await sqlite_manager.create_session(
            project_id=project_id,
            session_type='research',
            user_id='test_user'
        )
        
        # Test research framework
        research_framework = ResearchFrameworkService()
        assert len(research_framework.tool_mappings) > 0
        assert 'conceptualization' in research_framework.acts
        
        # Test workflow intelligence
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Add some test tool usage
        await sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name='clarify_research_goals',
            research_act='conceptualization',
            research_category='problem_definition',
            arguments={'research_area': 'AI'},
            result_summary='Goals clarified',
            execution_time_ms=150,
            success=True
        )
        
        # Test progress analysis
        progress_analysis = await workflow_intelligence.analyze_research_progress(project_id)
        assert 'overall_progress' in progress_analysis
        assert progress_analysis['overall_progress']['tools_used'] >= 1
        
        # Test session summary
        summary = await workflow_intelligence.generate_session_summary(session_id)
        assert summary['session_id'] == session_id
        assert summary['total_tool_calls'] >= 1
        
        # Test milestones detection
        milestones = await workflow_intelligence.detect_milestones(project_id)
        # Milestones might be empty for a single tool usage
        assert isinstance(milestones, list)
        
        # Cleanup
        await sqlite_manager.close()
        
        print("✅ All basic functionality tests passed!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_research_continuity_tools_import():
    """Test that research continuity tools can be imported and basic structure is correct"""
    
    try:
        from tools.research_continuity import (
            get_research_progress_tool,
            get_tool_usage_history_tool,
            get_workflow_recommendations_tool,
            get_research_milestones_tool,
            start_research_session_tool,
            get_session_summary_tool,
            register_research_continuity_tools
        )
        
        # Test that functions are callable
        assert callable(get_research_progress_tool)
        assert callable(get_tool_usage_history_tool)
        assert callable(get_workflow_recommendations_tool)
        assert callable(get_research_milestones_tool)
        assert callable(start_research_session_tool)
        assert callable(get_session_summary_tool)
        assert callable(register_research_continuity_tools)
        
        print("✅ All research continuity tools imported successfully!")
        
    except ImportError as e:
        pytest.fail(f"Failed to import research continuity tools: {e}")


@pytest.mark.asyncio
async def test_enhanced_mcp_server_basic():
    """Test basic functionality of enhanced MCP server"""
    
    try:
        from enhanced_mcp_server import EnhancedClaudeMCPServer
        
        # Create server instance
        server = EnhancedClaudeMCPServer()
        
        # Check that tools are registered
        assert len(server.tools) > 0
        
        # Check for specific continuity tools
        continuity_tools = [
            'get_research_progress',
            'get_tool_usage_history',
            'get_workflow_recommendations',
            'get_research_milestones',
            'start_research_session',
            'get_session_summary'
        ]
        
        for tool_name in continuity_tools:
            assert tool_name in server.tools, f"Tool {tool_name} not found in server"
        
        # Check that services are initialized
        assert server.research_framework is not None
        assert isinstance(server.research_framework, ResearchFrameworkService)
        
        print(f"✅ Enhanced MCP server initialized with {len(server.tools)} tools")
        
    except ImportError as e:
        pytest.fail(f"Failed to import enhanced MCP server: {e}")


if __name__ == "__main__":
    # Run basic tests
    import asyncio
    
    async def run_tests():
        print("Running basic research continuity tests...")
        
        try:
            await test_research_continuity_basic_functionality()
            await test_research_continuity_tools_import()
            await test_enhanced_mcp_server_basic()
            print("🎯 All tests passed successfully!")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_tests())
