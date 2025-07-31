#!/usr/bin/env python3
"""
Integration Tests for Enhanced Workflow System
===========================================

Tests complete enhanced workflow system with real database integration.
Follows proven pattern of using temporary directories and real databases.
"""
import pytest
import tempfile
import os
from pathlib import Path

# NOTE: All sys.path manipulations have been removed.
# Pytest's conftest.py handles path setup automatically.

try:
    from tools.research_continuity import get_research_act_guidance
    from utils.workflow_intelligence import WorkflowIntelligence
    from storage.sqlite_manager import SQLiteManager
    from utils.research_framework import ResearchFrameworkService
    from utils.current_project import set_current_project, clear_current_project
except ImportError as e:
    pytest.skip(f"MCP server modules not available: {e}", allow_module_level=True)


class TestEnhancedWorkflowIntegration:
    """Test enhanced workflow system integration"""

    def teardown_method(self):
        """Clean up after each test"""
        clear_current_project()

    @pytest.mark.asyncio
    async def test_complete_workflow_guidance_cycle(self):
        """Test complete workflow guidance cycle with real database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_dir = Path(temp_dir)
            srrd_dir = project_dir / ".srrd"
            srrd_dir.mkdir()
            data_dir = srrd_dir / "data"
            data_dir.mkdir()
            
            # Create config file
            config_file = srrd_dir / "config.json"
            config_file.write_text('{"project_name": "Test Project", "domain": "computer_science"}')
            
            # Set current project
            set_current_project(str(project_dir))
            
            # Test enhanced workflow guidance
            guidance_result = await get_research_act_guidance(
                target_act="conceptualization",
                user_experience="intermediate",
                detailed_guidance=True
            )
            
            assert "Conceptualization Research Act Guidance" in guidance_result
            assert "Key Activities" in guidance_result
            assert "Recommended Next Steps" in guidance_result

    @pytest.mark.asyncio 
    async def test_contextual_recommendations_with_tool_history(self):
        """Test contextual recommendations based on actual tool usage history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_dir = Path(temp_dir)
            srrd_dir = project_dir / ".srrd"
            srrd_dir.mkdir()
            data_dir = srrd_dir / "data"
            data_dir.mkdir()
            
            # Create config file
            config_file = srrd_dir / "config.json"
            config_file.write_text('{"project_name": "Physics Project", "domain": "physics"}')
            
            # Set current project
            set_current_project(str(project_dir))
            
            # Initialize database with tool usage history
            db_path = SQLiteManager.get_sessions_db_path(str(project_dir))
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create a test project in database
            await sqlite_manager.connection.execute(
                "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
                ("Physics Project", "Quantum mechanics research", "physics")
            )
            await sqlite_manager.connection.commit()
            project_id = 1
            
            # Create session for the project
            await sqlite_manager.connection.execute(
                "INSERT INTO sessions (project_id, session_type, research_focus) VALUES (?, ?, ?)",
                (project_id, "execution", "Quantum mechanics research session")
            )
            await sqlite_manager.connection.commit()
            session_id = 1
            
            # Add tool usage history
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, "clarify_research_goals", "2024-01-01 10:00:00", "Goals clarified", "conceptualization", "goal_setting")
            )
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, "suggest_methodology", "2024-01-01 11:00:00", "Methodology suggested", "design_planning", "methodology")
            )
            await sqlite_manager.connection.commit()
            
            # Test contextual recommendations
            research_framework = ResearchFrameworkService()
            workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
            
            recommendations = await workflow_intelligence.get_contextual_recommendations(
                project_id=project_id,
                last_tool_used="suggest_methodology",
                recommendation_depth=3
            )
            
            assert "prioritized_recommendations" in recommendations
            assert "rationale" in recommendations
            assert "recent_activity_pattern" in recommendations
            
            # Verify recommendations are contextually appropriate
            assert isinstance(recommendations["prioritized_recommendations"], list)
            assert isinstance(recommendations["rationale"], str)
            
            await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_workflow_progression_tracking(self):
        """Test that workflow progression is properly tracked across multiple tool uses"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_dir = Path(temp_dir)
            srrd_dir = project_dir / ".srrd"
            srrd_dir.mkdir()
            data_dir = srrd_dir / "data"
            data_dir.mkdir()
            
            # Create config file
            config_file = srrd_dir / "config.json"
            config_file.write_text('{"project_name": "Progression Test", "domain": "biology"}')
            
            # Set current project
            set_current_project(str(project_dir))
            
            # Test initial guidance
            initial_guidance = await get_research_act_guidance(
                target_act="conceptualization",
                user_experience="intermediate"
            )
            
            assert "0.0% complete" in initial_guidance or "Current Progress" not in initial_guidance
            
            # Simulate tool usage by directly adding to database
            db_path = SQLiteManager.get_sessions_db_path(str(project_dir))
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create project and session
            await sqlite_manager.connection.execute(
                "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
                ("Progression Test", "Workflow progression test", "biology")
            )
            await sqlite_manager.connection.execute(
                "INSERT INTO sessions (project_id, session_type, research_focus) VALUES (?, ?, ?)",
                (1, "execution", "Progression test session")
            )
            await sqlite_manager.connection.commit()
            
            # Add some tool usage
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (1, "clarify_research_goals", "2024-01-01 10:00:00", "Goals clarified", "conceptualization", "goal_setting")
            )
            await sqlite_manager.connection.commit()
            
            # Get updated guidance
            updated_guidance = await get_research_act_guidance(
                target_act="conceptualization",
                user_experience="intermediate"
            )
            
            # Should show progress has been made
            assert "Current Progress" in updated_guidance
            assert "clarify_research_goals" in updated_guidance
            
            await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_pattern_detection_integration(self):
        """Test that tool usage patterns are properly detected and influence recommendations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_dir = Path(temp_dir)
            srrd_dir = project_dir / ".srrd"
            srrd_dir.mkdir()
            data_dir = srrd_dir / "data"
            data_dir.mkdir()
            
            # Create config file
            config_file = srrd_dir / "config.json"
            config_file.write_text('{"project_name": "Pattern Test", "domain": "chemistry"}')
            
            # Initialize database
            db_path = SQLiteManager.get_sessions_db_path(str(project_dir))
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Create project in database
            await sqlite_manager.connection.execute(
                "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
                ("Pattern Test", "Pattern detection test", "chemistry")
            )
            await sqlite_manager.connection.commit()
            project_id = 1
            
            # Create session for the project
            await sqlite_manager.connection.execute(
                "INSERT INTO sessions (project_id, session_type, research_focus) VALUES (?, ?, ?)",
                (project_id, "execution", "Pattern detection test session")
            )
            await sqlite_manager.connection.commit()
            session_id = 1
            
            # Create repetitive pattern
            tools = ["semantic_search", "semantic_search", "semantic_search"]
            for i, tool in enumerate(tools):
                await sqlite_manager.connection.execute(
                    "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, tool, f"2024-01-01 1{i}:00:00", f"Result {i}", "conceptualization", "literature_search")
                )
            await sqlite_manager.connection.commit()
            
            # Test pattern detection
            research_framework = ResearchFrameworkService()
            workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
            
            recent_tools = await workflow_intelligence._get_recent_tool_sequence(project_id, 3)
            pattern = workflow_intelligence._analyze_tool_patterns(recent_tools)
            
            assert pattern["pattern_type"] == "repetitive"
            assert pattern["repeated_tool"] == "semantic_search"
            assert "diversifying" in pattern["suggestion"]
            
            await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_all_research_acts_integration(self):
        """Test that guidance works for all research acts in integration context"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project structure
            project_dir = Path(temp_dir)
            srrd_dir = project_dir / ".srrd"
            srrd_dir.mkdir()
            data_dir = srrd_dir / "data"
            data_dir.mkdir()
            
            # Create config file
            config_file = srrd_dir / "config.json"
            config_file.write_text('{"project_name": "All Acts Test", "domain": "mathematics"}')
            
            # Set current project
            set_current_project(str(project_dir))
            
            # Test all research acts
            research_acts = ["conceptualization", "design_planning", "implementation", "analysis", "synthesis", "publication"]
            
            for act in research_acts:
                guidance = await get_research_act_guidance(
                    target_act=act,
                    user_experience="intermediate",
                    detailed_guidance=True
                )
                
                assert isinstance(guidance, str)
                assert len(guidance) > 200  # Should be substantial
                assert "Purpose" in guidance
                assert "Key Activities" in guidance
                assert "Success Criteria" in guidance