"""
Test suite for research continuity tools
Tests workflow tracking, progress analysis, and session management
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp' / 'tools'))
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp' / 'utils'))

from storage.sqlite_manager import SQLiteManager
from utils.research_framework import ResearchFrameworkService
from utils.workflow_intelligence import WorkflowIntelligence
from tools.research_continuity import (
    get_research_progress_tool,
    get_tool_usage_history_tool,
    get_workflow_recommendations_tool,
    get_research_milestones_tool,
    start_research_session_tool,
    get_session_summary_tool
)

class TestResearchContinuityTools:
    """Test class for research continuity MCP tools"""
    
    @pytest.fixture
    def setup_test_environment(self):
        """Setup test database and project for testing"""
        import asyncio
        
        async def async_setup():
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            project_path = Path(temp_dir) / 'test_project'
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create .srrd directory
            srrd_dir = project_path / '.srrd'
            srrd_dir.mkdir(exist_ok=True)
            
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
            
            # Add some test tool usage data
            await sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name='clarify_research_goals',
                research_act='conceptualization',
                research_category='problem_definition',
                arguments={'research_area': 'AI', 'initial_goals': 'Test goals'},
                result_summary='Research goals clarified',
                execution_time_ms=150,
                success=True
            )
            
            await sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name='suggest_methodology',
                research_act='design_planning',
                research_category='methodology_selection',
                arguments={'research_goals': 'Test goals', 'domain': 'AI'},
                result_summary='Methodology suggested',
                execution_time_ms=200,
                success=True
            )
            
            # Add failed tool usage
            await sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name='semantic_search',
                research_act='knowledge_acquisition',
                research_category='literature_review',
                arguments={'query': 'test query'},
                result_summary=None,
                execution_time_ms=50,
                success=False,
                error_message='Search failed'
            )
            
            return {
                'project_path': str(project_path),
                'project_id': project_id,
                'session_id': session_id,
                'sqlite_manager': sqlite_manager,
                'temp_dir': temp_dir
            }
        
        # Run setup and return result
        test_env = asyncio.run(async_setup())
        
        yield test_env
        
        # Cleanup
        async def async_cleanup():
            await test_env['sqlite_manager'].close()
        
        asyncio.run(async_cleanup())
        import shutil
        shutil.rmtree(test_env['temp_dir'])
    
    @pytest.mark.asyncio
    async def test_get_research_progress_tool(self):
        """Test research progress analysis tool"""
        # Create self-contained test environment
        import tempfile
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'test_project'
        project_path.mkdir(parents=True, exist_ok=True)
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        try:
            # Initialize database
            db_path = str(srrd_dir / 'sessions.db')
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create test project and session
            project_id = await sqlite_manager.create_project(
                name="Test Research Project",
                description="A test project for continuity tools",
                domain="computer_science"
            )
            
            session_id = await sqlite_manager.create_session(
                project_id=project_id,
                session_type='research',
                user_id='test_user'
            )
            
            # Add test tool usage data
            await sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name='clarify_research_goals',
                research_act='conceptualization',
                research_category='problem_definition',
                arguments={'research_area': 'AI', 'initial_goals': 'Test goals'},
                result_summary='Research goals clarified',
                execution_time_ms=150,
                success=True
            )
            
            # Test with project path
            result = await get_research_progress_tool(project_path=str(project_path))
            
            assert "Research Progress Analysis" in result
            assert "Overall Progress" in result
            assert "Research Acts Progress" in result
            assert "Research Velocity" in result
            assert "Workflow Health" in result
            assert "%" in result
            
            # Test without project path in clean environment
            import os
            import tempfile
            original_path = os.environ.get('SRRD_PROJECT_PATH')
            if 'SRRD_PROJECT_PATH' in os.environ:
                del os.environ['SRRD_PROJECT_PATH']
            
            # Change to temp directory that's not an SRRD project
            original_cwd = os.getcwd()
            clean_temp_dir = tempfile.mkdtemp()
            os.chdir(clean_temp_dir)
            
            try:
                result_no_path = await get_research_progress_tool()
                # Should get error about project context not being available
                assert ("Error: Project context not available" in result_no_path or 
                        "No project found in database" in result_no_path)
            finally:
                os.chdir(original_cwd)
                import shutil
                shutil.rmtree(clean_temp_dir)
                if original_path:
                    os.environ['SRRD_PROJECT_PATH'] = original_path
            
            await sqlite_manager.close()
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_get_tool_usage_history_tool(self, setup_test_environment):
        """Test tool usage history retrieval"""
        test_env = setup_test_environment
        
        # Test with project path
        result = await get_tool_usage_history_tool(project_path=test_env['project_path'])
        
        assert "Tool Usage History" in result
        assert "clarify_research_goals" in result
        assert "suggest_methodology" in result
        assert "semantic_search" in result
        assert "✅" in result  # Success indicator
        assert "❌" in result  # Failure indicator
        
        # Test with session ID
        result_session = await get_tool_usage_history_tool(
            project_path=test_env['project_path'],
            session_id=test_env['session_id']
        )
        assert "Tool Usage History" in result_session
        
        # Test with limit
        result_limited = await get_tool_usage_history_tool(
            project_path=test_env['project_path'],
            limit=1
        )
        # Should contain fewer entries
        assert result_limited.count("##") <= 2  # Title + 1 entry
    
    @pytest.mark.asyncio
    async def test_get_workflow_recommendations_tool(self, setup_test_environment):
        """Test workflow recommendations generation"""
        test_env = setup_test_environment
        
        result = await get_workflow_recommendations_tool(project_path=test_env['project_path'])
        
        # Should either provide recommendations or indicate none available
        assert ("Workflow Recommendations" in result or 
                "No specific recommendations available" in result)
        
        if "Workflow Recommendations" in result:
            # If recommendations are provided, check structure
            assert "priority" in result.lower()
    
    @pytest.mark.asyncio
    async def test_get_research_milestones_tool(self, setup_test_environment):
        """Test research milestones retrieval"""
        test_env = setup_test_environment
        
        result = await get_research_milestones_tool(project_path=test_env['project_path'])
        
        assert "Research Milestones" in result
        # For new project, should indicate no milestones yet
        assert ("No milestones achieved yet" in result or 
                "Achieved Milestones" in result or
                "Recently Detected Milestones" in result)
    
    @pytest.mark.asyncio
    async def test_start_research_session_tool(self, setup_test_environment):
        """Test starting a new research session"""
        test_env = setup_test_environment
        
        # Test basic session start
        result = await start_research_session_tool(project_path=test_env['project_path'])
        
        assert "New Research Session Started" in result
        assert "Session ID" in result
        
        # Test with research act
        result_with_act = await start_research_session_tool(
            project_path=test_env['project_path'],
            research_act='conceptualization',
            research_focus='Testing session creation',
            session_goals=['Test goal 1', 'Test goal 2']
        )
        
        assert "New Research Session Started" in result_with_act
        assert "Research Act" in result_with_act
        assert "Focus" in result_with_act
        assert "Goals" in result_with_act
    
    @pytest.mark.asyncio
    async def test_get_session_summary_tool(self, setup_test_environment):
        """Test session summary generation"""
        test_env = setup_test_environment
        
        # Test with project path (should use latest session)
        result = await get_session_summary_tool(project_path=test_env['project_path'])
        
        assert "Session Summary" in result
        assert "Session ID" in result
        assert "Duration" in result
        assert "Tools Used" in result
        assert "Success Rate" in result
        
        # Test with specific session ID
        result_specific = await get_session_summary_tool(
            project_path=test_env['project_path'],
            session_id=test_env['session_id']
        )
        
        assert "Session Summary" in result_specific
        assert str(test_env['session_id']) in result_specific
    
    @pytest.mark.asyncio
    async def test_tools_with_invalid_project(self):
        """Test all tools with invalid project path"""
        invalid_path = '/nonexistent/path'
        
        tools_to_test = [
            get_research_progress_tool,
            get_tool_usage_history_tool,
            get_workflow_recommendations_tool,
            get_research_milestones_tool,
            start_research_session_tool,
            get_session_summary_tool
        ]
        
        for tool in tools_to_test:
            result = await tool(project_path=invalid_path)
            # Should handle error gracefully
            assert "Error" in result or "No project found" in result
    
    @pytest.mark.asyncio
    async def test_workflow_intelligence_integration(self, setup_test_environment):
        """Test integration with workflow intelligence"""
        test_env = setup_test_environment
        
        # Initialize workflow intelligence
        workflow_intelligence = WorkflowIntelligence(
            test_env['sqlite_manager'], 
            ResearchFrameworkService()
        )
        
        # Test progress analysis
        analysis = await workflow_intelligence.analyze_research_progress(test_env['project_id'])
        
        assert 'overall_progress' in analysis
        assert 'research_acts' in analysis
        assert 'research_velocity' in analysis
        assert 'workflow_health' in analysis
        
        # Should reflect the test data we inserted
        assert analysis['overall_progress']['tools_used'] >= 2  # 2 successful + 1 failed
    
    @pytest.mark.asyncio
    async def test_research_framework_integration(self):
        """Test integration with research framework"""
        # Initialize research framework
        research_framework = ResearchFrameworkService()
        
        # Test tool categorization
        assert 'clarify_research_goals' in research_framework.tool_mappings
        assert 'suggest_methodology' in research_framework.tool_mappings
        
        # Test research act structure
        assert 'conceptualization' in research_framework.acts
        assert 'design_planning' in research_framework.acts
        
        # Test category mappings
        conceptualization_categories = research_framework.acts['conceptualization']['categories']
        assert 'goal_setting' in conceptualization_categories  # Fixed: actual category name


class TestResearchContinuityIntegration:
    """Integration tests for research continuity with complete workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test complete research workflow tracking"""
        # Create temporary project
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'integration_test'
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create .srrd directory and initialize database structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        try:
            # Pre-initialize the database to avoid "unable to open database file" errors
            db_path = str(srrd_dir / 'sessions.db')
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create a basic project so tools don't fail
            project_id = await sqlite_manager.create_project(
                name="Integration Test Project",
                description="Test project for complete workflow",
                domain="computer_science"
            )
            
            await sqlite_manager.close()
            
            # Start new session
            result = await start_research_session_tool(
                project_path=str(project_path),
                research_act='conceptualization',
                research_focus='Integration testing',
                session_goals=['Test workflow', 'Validate tools']
            )
            
            assert "New Research Session Started" in result
            
            # Check initial progress
            progress = await get_research_progress_tool(project_path=str(project_path))
            assert "Research Progress Analysis" in progress
            
            # Get recommendations
            recommendations = await get_workflow_recommendations_tool(project_path=str(project_path))
            assert ("Workflow Recommendations" in recommendations or 
                    "No specific recommendations" in recommendations)
            
            # Check milestones
            milestones = await get_research_milestones_tool(project_path=str(project_path))
            assert "Research Milestones" in milestones
            
            # Get session summary
            summary = await get_session_summary_tool(project_path=str(project_path))
            assert "Session Summary" in summary
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_tool_context_awareness(self):
        """Test that tools work with and without explicit project context"""
        import os
        
        # Save original state
        original_path = os.environ.get('SRRD_PROJECT_PATH')
        original_cwd = os.getcwd()
        
        # Ensure clean environment for no-context test
        if 'SRRD_PROJECT_PATH' in os.environ:
            del os.environ['SRRD_PROJECT_PATH']
        
        # Change to a clean temporary directory that's not an SRRD project
        clean_temp_dir = tempfile.mkdtemp()
        os.chdir(clean_temp_dir)
        
        try:
            # Test without project context
            result = await get_research_progress_tool()
            # Should get error about project context not being available
            assert ("Error: Project context not available" in result or 
                    "No project found in database" in result)
            
        finally:
            # Restore original state
            os.chdir(original_cwd)
            import shutil
            shutil.rmtree(clean_temp_dir)
            if original_path:
                os.environ['SRRD_PROJECT_PATH'] = original_path
        
        # Create temporary project
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'context_test'
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create .srrd directory and initialize database structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        try:
            # Pre-initialize the database to avoid "unable to open database file" errors
            db_path = str(srrd_dir / 'sessions.db')
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create a basic project so tools don't fail
            project_id = await sqlite_manager.create_project(
                name="Context Test Project",
                description="Test project for context awareness",
                domain="computer_science"
            )
            
            await sqlite_manager.close()
            
            # Test with explicit project path
            result = await start_research_session_tool(project_path=str(project_path))
            assert "New Research Session Started" in result
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)


# Run tests if called directly
if __name__ == "__main__":
    # Simple test runner for development
    import asyncio
    
    async def run_basic_test():
        """Run a basic test to verify functionality"""
        print("Testing research continuity tools...")
        
        # Create temporary project
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'basic_test'
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Using temporary project: {project_path}")
            
            # Test session start
            result = await start_research_session_tool(
                project_path=str(project_path),
                research_focus='Basic functionality test'
            )
            print("✅ Session start:", "SUCCESS" if "Session Started" in result else "FAILED")
            
            # Test progress
            result = await get_research_progress_tool(project_path=str(project_path))
            print("✅ Progress check:", "SUCCESS" if "Research Progress" in result else "FAILED")
            
            print("Basic tests completed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
    
    asyncio.run(run_basic_test())
