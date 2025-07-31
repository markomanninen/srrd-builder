#!/usr/bin/env python3
"""
Unit Tests for Enhanced Workflow Guidance
=======================================

Tests enhanced research workflow guidance functionality:
- Research act guidance generation
- Smart contextual recommendations  
- Tool progression logic
"""
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

# NOTE: All sys.path manipulations have been removed.
# Pytest's conftest.py handles path setup automatically.

try:
    from tools.research_continuity import (
        get_research_act_guidance,
        _get_enhanced_act_guidance,
        _get_act_specific_progress, 
        _get_smart_next_tools
    )
    from storage.sqlite_manager import SQLiteManager
    from utils.research_framework import ResearchFrameworkService
    from utils.workflow_intelligence import WorkflowIntelligence
    from utils.current_project import set_current_project, clear_current_project
except ImportError as e:
    pytest.skip(f"MCP server modules not available: {e}", allow_module_level=True)


class TestEnhancedWorkflowGuidance:
    """Test enhanced workflow guidance functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        clear_current_project()

    def create_temp_dir(self, name: str) -> Path:
        """Create temporary directory for testing"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix=f"test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path

    @pytest.mark.asyncio
    async def test_research_act_guidance_generation(self):
        """Test research act guidance generation functionality"""
        # Test using real function (not mocked) following test suite guidelines
        temp_dir = self.create_temp_dir("act_guidance")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        research_framework = ResearchFrameworkService()
        
        # Test conceptualization act guidance
        guidance = await _get_enhanced_act_guidance(
            "conceptualization",
            "intermediate", 
            True,
            sqlite_manager,
            research_framework
        )
        
        assert "Conceptualization Research Act Guidance" in guidance
        assert "Purpose" in guidance
        assert "Key Activities" in guidance
        assert "Success Criteria" in guidance
        assert "clarify_research_goals" in guidance
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_act_specific_progress_calculation(self):
        """Test act-specific progress calculation using real database"""
        # Create temporary database with some tool usage data
        temp_dir = self.create_temp_dir("progress_calc")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Insert some test tool usage data
        await sqlite_manager.connection.execute(
            "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "clarify_research_goals", "2024-01-01 10:00:00", "Research goals clarified", "conceptualization", "goal_setting")
        )
        await sqlite_manager.connection.execute(
            "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
            (1, "semantic_search", "2024-01-01 11:00:00", "Literature search completed", "conceptualization", "literature_search")
        )
        await sqlite_manager.connection.commit()
        
        # Test progress calculation
        progress = await _get_act_specific_progress("conceptualization", sqlite_manager)
        
        assert "completion_percentage" in progress
        assert progress["completion_percentage"] > 0
        assert "completed_tools" in progress
        assert "clarify_research_goals" in progress["completed_tools"]
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_smart_next_tools_recommendation(self):
        """Test smart next tool recommendations based on progress"""
        temp_dir = self.create_temp_dir("next_tools")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Test with partial progress
        progress = {
            "completion_percentage": 33.3,
            "completed_tools": ["clarify_research_goals"],
            "total_tools": 3
        }
        
        recommendations = await _get_smart_next_tools("conceptualization", progress, sqlite_manager)
        
        assert len(recommendations) > 0
        assert all("name" in rec and "rationale" in rec for rec in recommendations)
        # Should not recommend already completed tools
        tool_names = [rec["name"] for rec in recommendations]
        assert "clarify_research_goals" not in tool_names
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_get_research_act_guidance_with_context(self):
        """Test get_research_act_guidance tool with proper context"""
        # Create a temporary project directory
        temp_dir = self.create_temp_dir("guidance_context")
        project_dir = temp_dir / ".srrd"
        project_dir.mkdir(parents=True)
        
        # Create minimal config
        config_file = project_dir / "config.json"
        config_file.write_text(json.dumps({
            "project_name": "Test Project",
            "domain": "computer_science"
        }))
        
        # Set current project
        set_current_project(str(temp_dir))
        
        # Initialize database
        db_path = project_dir / "data" / "sessions.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Test the tool function
        result = await get_research_act_guidance(
            target_act="conceptualization",
            user_experience="intermediate",
            detailed_guidance=True
        )
        
        assert isinstance(result, str)
        assert "Conceptualization Research Act Guidance" in result
        assert "Purpose" in result

    @pytest.mark.asyncio 
    async def test_all_research_acts_have_guidance(self):
        """Test that all research acts have proper guidance definitions"""
        temp_dir = self.create_temp_dir("all_acts")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        research_framework = ResearchFrameworkService()
        
        # Test all research acts
        research_acts = ["conceptualization", "design_planning", "implementation", "analysis", "synthesis", "publication"]
        
        for act in research_acts:
            guidance = await _get_enhanced_act_guidance(
                act,
                "intermediate",
                True,
                sqlite_manager,
                research_framework
            )
            
            assert f"{act.title().replace('_', ' ')} Research Act Guidance" in guidance
            assert "Purpose" in guidance
            assert "Key Activities" in guidance
            assert "Success Criteria" in guidance
            assert "Common Challenges" in guidance
            assert "Recommended Next Steps" in guidance
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_user_experience_levels(self):
        """Test guidance adaptation for different user experience levels"""
        temp_dir = self.create_temp_dir("experience_levels")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        research_framework = ResearchFrameworkService()
        
        experience_levels = ["beginner", "intermediate", "expert"]
        
        for level in experience_levels:
            guidance = await _get_enhanced_act_guidance(
                "conceptualization",
                level,
                True,
                sqlite_manager,
                research_framework
            )
            
            # Should contain level-specific guidance
            assert isinstance(guidance, str)
            assert len(guidance) > 100  # Should be substantial
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_workflow_intelligence_contextual_recommendations(self):
        """Test enhanced contextual recommendations in WorkflowIntelligence"""
        temp_dir = self.create_temp_dir("contextual_recs")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Create a test project in database
        await sqlite_manager.connection.execute(
            "INSERT INTO projects (name, description, domain) VALUES (?, ?, ?)",
            ("Test Project", "Test Description", "computer_science")
        )
        await sqlite_manager.connection.commit()
        project_id = 1
        
        research_framework = ResearchFrameworkService()
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        
        # Test contextual recommendations
        recommendations = await workflow_intelligence.get_contextual_recommendations(
            project_id=project_id,
            last_tool_used="clarify_research_goals",
            recommendation_depth=3
        )
        
        assert "current_context" in recommendations
        assert "recent_activity_pattern" in recommendations
        assert "prioritized_recommendations" in recommendations
        assert "rationale" in recommendations
        assert "alternative_paths" in recommendations
        
        await sqlite_manager.close()

    def test_tool_pattern_analysis(self):
        """Test tool pattern analysis functionality"""
        workflow_intelligence = WorkflowIntelligence(None, None)
        
        # Test repetitive pattern
        repetitive_tools = [
            {"tool_name": "semantic_search", "timestamp": "2024-01-01 10:00:00"},
            {"tool_name": "semantic_search", "timestamp": "2024-01-01 11:00:00"},
        ]
        
        pattern = workflow_intelligence._analyze_tool_patterns(repetitive_tools)
        assert pattern["pattern_type"] == "repetitive"
        assert pattern["repeated_tool"] == "semantic_search"
        
        # Test logical progression
        logical_tools = [
            {"tool_name": "suggest_methodology", "timestamp": "2024-01-01 11:00:00"},
            {"tool_name": "clarify_research_goals", "timestamp": "2024-01-01 10:00:00"},
        ]
        
        pattern = workflow_intelligence._analyze_tool_patterns(logical_tools)
        assert pattern["pattern_type"] == "logical_progression"
        
        # Test exploratory pattern
        exploratory_tools = [
            {"tool_name": "tool1", "timestamp": "2024-01-01 10:00:00"},
            {"tool_name": "tool2", "timestamp": "2024-01-01 11:00:00"},
            {"tool_name": "tool3", "timestamp": "2024-01-01 12:00:00"},
        ]
        
        pattern = workflow_intelligence._analyze_tool_patterns(exploratory_tools)
        assert pattern["pattern_type"] == "exploratory"
        assert pattern["diversity"] == 1.0

    def test_sequence_matching(self):
        """Test logical sequence matching functionality"""
        workflow_intelligence = WorkflowIntelligence(None, None)
        
        # Test positive match
        tool_names = ["suggest_methodology", "clarify_research_goals"]
        sequence = ["clarify_research_goals", "suggest_methodology"]
        
        assert workflow_intelligence._check_sequence_match(tool_names, sequence) == True
        
        # Test negative match
        tool_names = ["tool1", "tool2"]
        sequence = ["clarify_research_goals", "suggest_methodology"]
        
        assert workflow_intelligence._check_sequence_match(tool_names, sequence) == False