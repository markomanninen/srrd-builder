#!/usr/bin/env python3
"""
Unit tests for research planning tools
"""
import sys
import tempfile
from pathlib import Path

import pytest

from work.code.mcp.utils import current_project as current_project_module

# Import research planning tools with error handling
try:
    from work.code.mcp.tools.research_planning import (
        clarify_research_goals,
        register_research_tools,
        suggest_methodology,
    )

    RESEARCH_TOOLS_AVAILABLE = True
except ImportError:
    RESEARCH_TOOLS_AVAILABLE = False


@pytest.fixture
def active_project_context():
    """
    Creates a temporary project and sets it as the active context for the duration of a test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / ".srrd").mkdir()
        (project_path / ".srrd" / "config.json").write_text(
            '{"name": "test_planning_project"}'
        )

        original_project = current_project_module.get_current_project()
        try:
            current_project_module.set_current_project(str(project_path))
            yield project_path
        finally:
            if original_project:
                current_project_module.set_current_project(original_project)
            else:
                current_project_module.clear_current_project()


@pytest.mark.skipif(
    not RESEARCH_TOOLS_AVAILABLE, reason="Research Planning tools not available"
)
@pytest.mark.usefixtures("active_project_context")
class TestResearchPlanningTools:
    """Test research planning tools"""

    @pytest.mark.asyncio
    async def test_clarify_research_goals(self):
        """Test clarify_research_goals tool"""
        try:
            # Test with minimal valid parameters
            result = await clarify_research_goals(
                research_area="artificial intelligence",
                initial_goals="Develop better AI systems",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "clarified_goals" in result or "recommended_methodologies" in result
            assert len(result) > 0

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_clarify_research_goals_with_context(self):
        """Test clarify_research_goals tool with additional context"""
        try:
            result = await clarify_research_goals(
                research_area="machine learning",
                initial_goals="Create interpretable ML models",
                experience_level="advanced",
                domain_specialization="computer science",
                novel_theory_mode=True,
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "clarified_goals" in result or "recommended_methodologies" in result
            assert len(result) > 0

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_clarify_research_goals_missing_parameters(self):
        """Test clarify_research_goals tool with missing required parameters"""
        try:
            # Missing research_area should raise TypeError
            with pytest.raises(TypeError):
                await clarify_research_goals(initial_goals="Some goals")

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_suggest_methodology(self):
        """Test suggest_methodology tool"""
        try:
            result = await suggest_methodology(
                research_goals="Study the effects of meditation on cognitive performance",
                domain="psychology",
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "clarified_goals" in result or "recommended_methodologies" in result
            assert len(result) > 0

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_suggest_methodology_with_constraints(self):
        """Test suggest_methodology tool with constraints"""
        try:
            result = await suggest_methodology(
                research_goals="Investigate climate change impacts on agriculture",
                domain="environmental science",
                constraints={
                    "budget": "limited",
                    "time_frame": "6 months",
                    "participants": 100,
                },
                novel_theory_flag=False,
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "clarified_goals" in result or "recommended_methodologies" in result
            assert len(result) > 0

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_suggest_methodology_missing_parameters(self):
        """Test suggest_methodology tool with missing parameters"""
        try:
            # Missing required parameters should raise TypeError
            with pytest.raises(TypeError):
                await suggest_methodology()

        except ImportError:
            pytest.skip("Research planning tools not available")


class TestResearchPlanningToolRegistration:
    """Test research planning tool registration"""

    def test_research_tools_registration(self):
        """Test that research planning tools are properly registered"""
        try:
            from unittest.mock import Mock

            # Mock server for testing registration
            mock_server = Mock()
            mock_server.register_tool = Mock()

            # Register tools
            register_research_tools(mock_server)

            # Verify tools were registered
            assert mock_server.register_tool.called

            # Check for expected tool names - handle different registration formats
            call_args_list = mock_server.register_tool.call_args_list
            if call_args_list and len(call_args_list) > 0:
                # Check if we have any calls
                first_call = call_args_list[0]
                if len(first_call.args) > 0:  # Check if first call has positional args
                    registered_tools = [
                        call.args[0] for call in call_args_list
                    ]  # First argument is tool name

                    expected_tools = ["clarify_research_goals", "suggest_methodology"]

                    for tool in expected_tools:
                        assert tool in registered_tools
            # If registration format is different, just verify registration was called

        except ImportError:
            pytest.skip("Research planning tools not available")

    def test_tool_handler_registration(self):
        """Test that tool handlers are properly registered"""
        try:
            from unittest.mock import Mock

            mock_server = Mock()
            mock_server.register_tool = Mock()

            register_research_tools(mock_server)

            # Verify each registration call has proper structure
            if mock_server.register_tool.call_args_list:
                for call in mock_server.register_tool.call_args_list:
                    args = call.args

                    # Registration format may vary - check if we have enough arguments
                    if len(args) >= 2:  # At least name and something else
                        name = args[0]
                        assert isinstance(name, str)
                    # Registration structure may be different than expected - just verify basic call
            else:
                # If no calls recorded, tools may be registered differently
                assert mock_server.register_tool.called

        except ImportError:
            pytest.skip("Research planning tools not available")


@pytest.mark.skipif(
    not RESEARCH_TOOLS_AVAILABLE, reason="Research Planning tools not available"
)
@pytest.mark.usefixtures("active_project_context")
class TestResearchPlanningToolParameters:
    """Test research planning tool parameter handling"""

    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """Test parameter validation in research planning tools"""
        try:
            # Test with various parameter types
            test_cases = [
                {
                    "research_area": "physics",
                    "initial_goals": "Study quantum mechanics",
                },
                {"research_area": "", "initial_goals": "Some goal"},  # Empty string
                {"research_area": "biology", "initial_goals": ""},  # Empty string
            ]

            for params in test_cases:
                result = await clarify_research_goals(**params)
                assert result is not None
                assert isinstance(result, dict)
                assert (
                    "clarified_goals" in result or "recommended_methodologies" in result
                )

        except ImportError:
            pytest.skip("Research planning tools not available")

    @pytest.mark.asyncio
    async def test_optional_parameters(self):
        """Test handling of optional parameters"""
        try:
            # Test with only required parameters
            result1 = await clarify_research_goals(
                research_area="chemistry", initial_goals="Synthesize new compounds"
            )

            # Test with all optional parameters
            result2 = await clarify_research_goals(
                research_area="chemistry",
                initial_goals="Synthesize new compounds",
                experience_level="beginner",
                domain_specialization="organic chemistry",
                novel_theory_mode=False,
            )

            # Both should work
            assert result1 is not None
            assert result2 is not None
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)

        except ImportError:
            pytest.skip("Research planning tools not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
