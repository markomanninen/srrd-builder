"""
Test suite for research continuity tools
Tests workflow tracking, progress analysis, and session management
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# NOTE: All sys.path manipulations have been removed.
# Pytest's conftest.py handles path setup automatically.

try:
    from tools.research_continuity import (
        get_research_milestones_tool,
        get_research_progress_tool,
        get_session_summary_tool,
        get_tool_usage_history_tool,
        get_workflow_recommendations_tool,
        start_research_session_tool,
    )
    from utils.context_decorator import ContextAwareError
    from utils.current_project import (
        clear_current_project,
        get_current_project,
        set_current_project,
    )
    from utils.research_framework import ResearchFrameworkService
    from utils.workflow_intelligence import WorkflowIntelligence

    from work.code.mcp.storage.sqlite_manager import SQLiteManager
except ImportError as e:
    pytest.skip(f"MCP server modules not available: {e}", allow_module_level=True)


class TestResearchContinuityTools:
    """Test class for research continuity MCP tools"""

    @pytest.fixture
    def setup_test_environment(self):
        """Setup a complete, initialized test project with pre-populated data."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "test_project"

        original_current_project = get_current_project()

        async def async_setup():
            project_path.mkdir(parents=True, exist_ok=True)
            srrd_dir = project_path / ".srrd"
            srrd_dir.mkdir(exist_ok=True)
            config_data = {
                "project_name": "Test Research Project",
                "domain": "computer_science",
            }
            with open(srrd_dir / "config.json", "w") as f:
                json.dump(config_data, f)

            set_current_project(str(project_path))

            db_path = SQLiteManager.get_sessions_db_path(str(project_path))
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()

            project_id = await sqlite_manager.create_project(
                name="Test Research Project",
                description="A test project for continuity tools",
                domain="computer_science",
            )
            session_id = await sqlite_manager.create_session(
                project_id=project_id, session_type="research", user_id="test_user"
            )

            await sqlite_manager.log_tool_usage(
                session_id=session_id,
                tool_name="clarify_research_goals",
                research_act="conceptualization",
                research_category="problem_definition",
                success=True,
            )

            return {
                "project_path": str(project_path),
                "project_id": project_id,
                "session_id": session_id,
                "sqlite_manager": sqlite_manager,
            }

        test_env = asyncio.run(async_setup())
        yield test_env

        async def async_teardown():
            await test_env["sqlite_manager"].close()

        asyncio.run(async_teardown())

        if original_current_project:
            set_current_project(original_current_project)
        else:
            clear_current_project()

        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_get_research_progress_tool(self, setup_test_environment):
        result = await get_research_progress_tool()
        assert "Research Progress Analysis" in result

    @pytest.mark.asyncio
    async def test_get_tool_usage_history_tool(self, setup_test_environment):
        result = await get_tool_usage_history_tool()
        assert "Tool Usage History" in result

    @pytest.mark.asyncio
    async def test_get_workflow_recommendations_tool(self, setup_test_environment):
        result = await get_workflow_recommendations_tool()
        assert (
            "Workflow Recommendations" in result
            or "No specific recommendations" in result
        )

    @pytest.mark.asyncio
    async def test_get_research_milestones_tool(self, setup_test_environment):
        result = await get_research_milestones_tool()
        assert "Research Milestones" in result

    @pytest.mark.asyncio
    async def test_start_research_session_tool(self, setup_test_environment):
        result = await start_research_session_tool(research_act="conceptualization")
        assert "New Research Session Started" in result

    @pytest.mark.asyncio
    async def test_get_session_summary_tool(self, setup_test_environment):
        test_env = setup_test_environment
        result = await get_session_summary_tool(session_id=test_env["session_id"])
        assert "Session Summary" in result

    @pytest.mark.asyncio
    async def test_tools_with_invalid_project(self):
        """Test tools require project context and raise ContextAwareError."""
        original_current_project = get_current_project()
        try:
            clear_current_project()
            assert (
                get_current_project() is None
            ), "Context should be cleared for this test"
            with pytest.raises(ContextAwareError):
                await get_research_progress_tool()
        finally:
            if original_current_project:
                set_current_project(original_current_project)

    @pytest.mark.asyncio
    async def test_workflow_intelligence_integration(self, setup_test_environment):
        test_env = setup_test_environment
        workflow_intelligence = WorkflowIntelligence(
            test_env["sqlite_manager"], ResearchFrameworkService()
        )
        analysis = await workflow_intelligence.analyze_research_progress(
            test_env["project_id"]
        )
        assert "overall_progress" in analysis

    @pytest.mark.asyncio
    async def test_research_framework_integration(self):
        research_framework = ResearchFrameworkService()
        assert "clarify_research_goals" in research_framework.tool_mappings


class TestResearchContinuityIntegration:
    """Integration tests for research continuity with complete workflow"""

    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test complete research workflow tracking, ensuring DB is initialized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "integration_test"
            project_path.mkdir(parents=True, exist_ok=True)
            srrd_dir = project_path / ".srrd"
            srrd_dir.mkdir(exist_ok=True)

            original_current_project = get_current_project()
            try:
                (srrd_dir / "config.json").write_text('{"name": "Integration Test"}')
                set_current_project(str(project_path))

                db_path = SQLiteManager.get_sessions_db_path(str(project_path))
                sqlite_manager = SQLiteManager(db_path)
                await sqlite_manager.initialize()
                await sqlite_manager.create_project(
                    name="Integration", description="", domain=""
                )
                await sqlite_manager.close()

                result = await start_research_session_tool(
                    research_act="conceptualization"
                )
                assert "New Research Session Started" in result

                progress = await get_research_progress_tool()
                assert "Research Progress Analysis" in progress

            finally:
                if original_current_project:
                    set_current_project(original_current_project)
                else:
                    clear_current_project()

    @pytest.mark.asyncio
    async def test_tool_context_awareness(self):
        """Test tools raise errors without context and work with it."""
        original_current_project = get_current_project()
        try:
            clear_current_project()
            with pytest.raises(ContextAwareError):
                await get_research_progress_tool()
        finally:
            if original_current_project:
                set_current_project(original_current_project)

        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "context_test"
            project_path.mkdir(parents=True, exist_ok=True)
            srrd_dir = project_path / ".srrd"
            srrd_dir.mkdir(exist_ok=True)

            try:
                (srrd_dir / "config.json").write_text('{"name": "Context Test"}')
                set_current_project(str(project_path))

                db_path = SQLiteManager.get_sessions_db_path(str(project_path))
                sqlite_manager = SQLiteManager(db_path)
                await sqlite_manager.initialize()
                await sqlite_manager.create_project(
                    name="Context", description="", domain=""
                )
                await sqlite_manager.close()

                result = await start_research_session_tool()
                assert "New Research Session Started" in result
            finally:
                clear_current_project()
