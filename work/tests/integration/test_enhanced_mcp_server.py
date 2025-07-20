"""
Integration tests for Enhanced MCP Server with research lifecycle persistence
Tests the complete workflow tracking and intelligent guidance system
"""

import pytest
import asyncio
import tempfile
import json
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))

from enhanced_mcp_server import EnhancedClaudeMCPServer
from storage.sqlite_manager import SQLiteManager
from utils.research_framework import ResearchFrameworkService

class TestEnhancedMCPServerIntegration:
    """Integration tests for enhanced MCP server with full workflow tracking"""
    
    @pytest.fixture
    async def setup_server_environment(self):
        """Setup test environment with temporary project and server"""
        # Create temporary directory and project
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'test_project'
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create .srrd directory
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        # Set environment variable for project path
        import os
        original_path = os.environ.get('SRRD_PROJECT_PATH')
        os.environ['SRRD_PROJECT_PATH'] = str(project_path)
        
        # Initialize enhanced server
        server = EnhancedClaudeMCPServer()
        
        # Initialize database manually for testing
        db_path = str(srrd_dir / 'sessions.db')
        server.sqlite_manager = SQLiteManager(db_path)
        await server.sqlite_manager.initialize()
        
        # Create test project
        project_id = await server.sqlite_manager.create_project(
            name="Integration Test Project",
            description="Test project for enhanced MCP server",
            domain="computer_science"
        )
        
        # Initialize workflow intelligence
        from utils.workflow_intelligence import WorkflowIntelligence
        server.workflow_intelligence = WorkflowIntelligence(
            server.sqlite_manager, 
            server.research_framework
        )
        
        yield {
            'server': server,
            'project_path': str(project_path),
            'project_id': project_id,
            'temp_dir': temp_dir,
            'db_path': db_path
        }
        
        # Cleanup
        if server.sqlite_manager:
            await server.sqlite_manager.close()
        
        # Restore environment
        if original_path:
            os.environ['SRRD_PROJECT_PATH'] = original_path
        elif 'SRRD_PROJECT_PATH' in os.environ:
            del os.environ['SRRD_PROJECT_PATH']
        
        import shutil
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, setup_server_environment):
        """Test enhanced MCP server initialization"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Check services are initialized
        assert server.research_framework is not None
        assert server.sqlite_manager is not None
        assert server.workflow_intelligence is not None
        
        # Check tools are registered
        assert len(server.tools) > 0
        
        # Check for specific research continuity tools
        continuity_tools = [
            'get_research_progress',
            'get_tool_usage_history', 
            'get_workflow_recommendations',
            'get_research_milestones',
            'start_research_session',
            'get_session_summary'
        ]
        
        for tool_name in continuity_tools:
            assert tool_name in server.tools, f"Tool {tool_name} not registered"
    
    @pytest.mark.asyncio
    async def test_tool_execution_with_logging(self, setup_server_environment):
        """Test that tool execution includes automatic logging"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Start a session first
        session_id = await server._get_or_create_session(test_env['project_id'])
        
        # Mock tool execution (simulate clarify_research_goals)
        tool_name = 'clarify_research_goals'
        arguments = {
            'research_area': 'AI',
            'initial_goals': 'Test research goals',
            'project_path': test_env['project_path']  # Add project_path for logging
        }
        
        # Execute tool with logging
        result = await server._execute_tool_with_logging(
            tool_name=tool_name,
            tool_args=arguments
        )
        
        # Check that logging occurred
        tool_history = await server.sqlite_manager.get_tool_usage_history(session_id)
        assert len(tool_history) >= 1
        
        # Check logged data
        logged_entry = tool_history[-1]  # Get the most recent entry
        assert logged_entry['tool_name'] == tool_name
        assert logged_entry['research_act'] == 'conceptualization'
        assert logged_entry['research_category'] == 'goal_setting'  # Fixed: actual category from framework
    
    @pytest.mark.asyncio
    async def test_research_progress_tracking(self, setup_server_environment):
        """Test research progress tracking through multiple tool uses"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Start session
        session_id = await server._get_or_create_session(test_env['project_id'])
        
        # Simulate multiple tool uses across different research acts
        tools_to_simulate = [
            ('clarify_research_goals', 'conceptualization', 'problem_definition'),
            ('suggest_methodology', 'design_planning', 'methodology_selection'),
            ('search_knowledge', 'knowledge_acquisition', 'literature_review'),
            ('discover_patterns', 'analysis_synthesis', 'pattern_analysis')
        ]
        
        for tool_name, research_act, research_category in tools_to_simulate:
            await server.sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name=tool_name,
                research_act=research_act,
                research_category=research_category,
                arguments={'test': 'data'},
                result_summary=f'Successfully executed {tool_name}',
                execution_time_ms=100,
                success=True
            )
        
        # Check research progress
        progress_analysis = await server.workflow_intelligence.analyze_research_progress(test_env['project_id'])
        
        assert progress_analysis['overall_progress']['tools_used'] == 4
        assert len(progress_analysis['research_acts']) >= 4  # At least 4 different acts touched
        
        # Check that different acts show progress
        act_names = list(progress_analysis['research_acts'].keys())
        assert 'conceptualization' in act_names
        assert 'design_planning' in act_names
        assert 'knowledge_acquisition' in act_names
        assert 'analysis_synthesis' in act_names
    
    @pytest.mark.asyncio
    async def test_workflow_recommendations_generation(self, setup_server_environment):
        """Test workflow recommendations based on usage history"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Start session and log some initial tools
        session_id = await server._get_or_create_session(test_env['project_id'])
        
        # Log early-stage research tools
        await server.sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name='clarify_research_goals',
            research_act='conceptualization',
            research_category='problem_definition',
            arguments={'research_area': 'AI'},
            result_summary='Goals clarified',
            execution_time_ms=150,
            success=True
        )
        
        # Generate recommendations
        recommendations = await server.workflow_intelligence.generate_recommendations(
            test_env['project_id'], 
            session_id
        )
        
        # Should provide recommendations for next logical steps
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert 'tool' in rec
            assert 'research_act' in rec
            assert 'priority' in rec
            assert 'reason' in rec
    
    @pytest.mark.asyncio
    async def test_milestone_detection(self, setup_server_environment):
        """Test automatic milestone detection"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Start session
        session_id = await server._get_or_create_session(test_env['project_id'])
        
        # Simulate achieving a milestone (completing conceptualization)
        conceptualization_tools = [
            'clarify_research_goals',
            'assess_foundational_assumptions',
            'generate_critical_questions'
        ]
        
        for tool in conceptualization_tools:
            await server.sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name=tool,
                research_act='conceptualization',
                research_category='problem_definition',
                arguments={'test': 'data'},
                result_summary=f'Successfully completed {tool}',
                execution_time_ms=100,
                success=True
            )
        
        # Detect milestones
        milestones = await server.workflow_intelligence.detect_milestones(test_env['project_id'])
        
        # Should detect conceptualization milestone
        milestone_names = [m['name'] for m in milestones]
        assert any('conceptualization' in name.lower() for name in milestone_names)
    
    @pytest.mark.asyncio
    async def test_session_management(self, setup_server_environment):
        """Test session management and context tracking"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Test session creation
        session_id = await server._get_or_create_session(test_env['project_id'])
        assert session_id is not None
        assert server.current_session_id == session_id
        assert server.current_project_id == test_env['project_id']
        
        # Test session context updates
        await server.sqlite_manager.update_session_research_context(
            session_id=session_id,
            current_research_act='conceptualization',
            research_focus='Testing session management',
            session_goals=['Goal 1', 'Goal 2']
        )
        
        # Generate session summary
        summary = await server.workflow_intelligence.generate_session_summary(session_id)
        
        assert summary['session_id'] == session_id
        assert 'duration_minutes' in summary
        assert 'tools_used' in summary
        assert 'research_acts_involved' in summary
    
    @pytest.mark.asyncio
    async def test_research_continuity_tools_via_server(self, setup_server_environment):
        """Test research continuity tools through the server"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Mock request to start research session
        request_data = {
            "method": "tools/call",
            "params": {
                "name": "start_research_session",
                "arguments": {
                    "project_path": test_env['project_path'],
                    "research_act": "conceptualization",
                    "research_focus": "Testing continuity tools"
                }
            },
            "id": 1
        }
        
        # Note: The server.handle_request method would need to be implemented
        # For now, test direct tool access
        tool_handler = server.tools['start_research_session']['handler']
        result = await tool_handler(
            project_path=test_env['project_path'],
            research_act='conceptualization',
            research_focus='Testing continuity tools'
        )
        
        assert "New Research Session Started" in result
        
        # Test progress tool
        progress_tool = server.tools['get_research_progress']['handler']
        progress_result = await progress_tool(project_path=test_env['project_path'])
        
        assert "Research Progress Analysis" in progress_result
    
    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(self, setup_server_environment):
        """Test error handling in enhanced server"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Test with invalid project path
        invalid_tools = [
            'get_research_progress',
            'get_tool_usage_history',
            'get_workflow_recommendations'
        ]
        
        for tool_name in invalid_tools:
            tool_handler = server.tools[tool_name]['handler']
            result = await tool_handler(project_path='/invalid/path')
            assert "Error" in result or "No project found" in result
    
    @pytest.mark.asyncio
    async def test_complete_research_lifecycle(self, setup_server_environment):
        """Test complete research lifecycle tracking"""
        test_env = await setup_server_environment.__anext__()
        server = test_env['server']
        
        # Start new research session
        start_tool = server.tools['start_research_session']['handler']
        start_result = await start_tool(
            project_path=test_env['project_path'],
            research_act='conceptualization',
            research_focus='Complete lifecycle test'
        )
        
        assert "New Research Session Started" in start_result
        
        # Simulate research progression through multiple acts
        session_id = await server._get_or_create_session(test_env['project_id'])
        
        # Conceptualization phase
        await server.sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name='clarify_research_goals',
            research_act='conceptualization',
            research_category='problem_definition',
            arguments={'test': 'data'},
            result_summary='Research goals clarified',
            execution_time_ms=150,
            success=True
        )
        
        # Planning phase
        await server.sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name='suggest_methodology',
            research_act='design_planning',
            research_category='methodology_selection',
            arguments={'test': 'data'},
            result_summary='Methodology selected',
            execution_time_ms=200,
            success=True
        )
        
        # Knowledge acquisition
        await server.sqlite_manager.log_tool_usage(
            session_id=session_id,
            tool_name='search_knowledge',
            research_act='knowledge_acquisition',
            research_category='literature_review',
            arguments={'test': 'data'},
            result_summary='Literature searched',
            execution_time_ms=300,
            success=True
        )
        
        # Check final progress
        progress_tool = server.tools['get_research_progress']['handler']
        final_progress = await progress_tool(project_path=test_env['project_path'])
        
        assert "Research Progress Analysis" in final_progress
        assert "Research Acts Progress" in final_progress
        assert "Research Velocity" in final_progress
        
        # Get final session summary
        summary_tool = server.tools['get_session_summary']['handler']
        final_summary = await summary_tool(project_path=test_env['project_path'])
        
        assert "Session Summary" in final_summary
        assert "Tools Used: 3" in final_summary or "3 unique tools" in final_summary


# Performance and load testing
class TestEnhancedMCPServerPerformance:
    """Performance tests for enhanced MCP server"""
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent tool execution and logging"""
        # Create temporary environment
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'perf_test'
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create .srrd directory
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        try:
            # Initialize server
            import os
            os.environ['SRRD_PROJECT_PATH'] = str(project_path)
            
            server = EnhancedClaudeMCPServer()
            
            # Initialize database
            db_path = str(srrd_dir / 'sessions.db')
            server.sqlite_manager = SQLiteManager(db_path)
            await server.sqlite_manager.initialize()
            
            # Create project
            project_id = await server.sqlite_manager.create_project(
                name="Performance Test Project",
                description="Test concurrent execution",
                domain="performance"
            )
            
            session_id = await server._get_or_create_session(project_id)
            
            # Test concurrent tool executions
            tasks = []
            for i in range(10):
                task = server.sqlite_manager.log_tool_usage(
                    session_id=session_id,
                    tool_name=f'test_tool_{i}',
                    research_act='conceptualization',
                    research_category='problem_definition',
                    arguments={'test': f'concurrent_{i}'},
                    result_summary=f'Concurrent execution {i}',
                    execution_time_ms=50,
                    success=True
                )
                tasks.append(task)
            
            # Execute concurrently
            await asyncio.gather(*tasks)
            
            # Verify all logged
            history = await server.sqlite_manager.get_tool_usage_history(session_id)
            assert len(history) == 10
            
            await server.sqlite_manager.close()
            
        finally:
            # Cleanup
            if 'SRRD_PROJECT_PATH' in os.environ:
                del os.environ['SRRD_PROJECT_PATH']
            import shutil
            shutil.rmtree(temp_dir)


# Run tests if called directly
if __name__ == "__main__":
    # Simple test runner for development
    import asyncio
    
    async def run_basic_integration_test():
        """Run basic integration test"""
        print("Testing Enhanced MCP Server Integration...")
        
        # Create temporary project
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / 'integration_test'
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Set environment
            import os
            os.environ['SRRD_PROJECT_PATH'] = str(project_path)
            
            # Initialize server
            server = EnhancedClaudeMCPServer()
            print(f"✅ Server initialized with {len(server.tools)} tools")
            
            # Check for continuity tools
            continuity_tools = [
                'get_research_progress',
                'start_research_session'
            ]
            
            for tool in continuity_tools:
                if tool in server.tools:
                    print(f"✅ {tool}: REGISTERED")
                else:
                    print(f"❌ {tool}: MISSING")
            
            print("Basic integration test completed!")
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
        finally:
            # Cleanup
            if 'SRRD_PROJECT_PATH' in os.environ:
                del os.environ['SRRD_PROJECT_PATH']
            import shutil
            shutil.rmtree(temp_dir)
    
    asyncio.run(run_basic_integration_test())
