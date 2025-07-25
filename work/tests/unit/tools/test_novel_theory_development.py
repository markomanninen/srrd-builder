#!/usr/bin/env python3
"""
Test suite for Novel Theory Development tools.

Tests initiate_paradigm_challenge, develop_alternative_framework, compare_paradigms,
validate_novel_theory, cultivate_innovation, assess_foundational_assumptions,
generate_critical_questions, evaluate_paradigm_shift_potential
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from work.code.mcp.utils import current_project as current_project_module

# Import novel theory development tools with error handling
try:
    from work.code.mcp.tools.novel_theory_development import (
        assess_foundational_assumptions,
        compare_paradigms,
        cultivate_innovation,
        develop_alternative_framework,
        evaluate_paradigm_shift_potential,
        generate_critical_questions,
        initiate_paradigm_challenge,
        register_novel_theory_tools,
        validate_novel_theory,
    )

    NOVEL_THEORY_TOOLS_AVAILABLE = True
except ImportError:
    NOVEL_THEORY_TOOLS_AVAILABLE = False


@pytest.fixture
def active_project_context():
    """
    Creates a temporary project and sets it as the active context for the duration of a test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / ".srrd").mkdir()
        (project_path / ".srrd" / "config.json").write_text(
            '{"name": "test_novel_theory_project"}'
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
    not NOVEL_THEORY_TOOLS_AVAILABLE,
    reason="Novel Theory Development tools not available",
)
@pytest.mark.usefixtures("active_project_context")
class TestNovelTheoryDevelopmentTools:
    """Test novel theory development functionality"""

    @pytest.mark.asyncio
    async def test_initiate_paradigm_challenge_tool(self):
        """Test paradigm challenge initiation"""
        try:
            result = await initiate_paradigm_challenge(
                domain="theoretical_physics",
                current_paradigm="standard_model",
                challenge_area="quantum_mechanics",
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Paradigm challenge dependencies not available")

    @pytest.mark.asyncio
    async def test_develop_alternative_framework_tool(self):
        """Test alternative framework development"""
        try:
            result = await develop_alternative_framework(
                domain="theoretical_physics",
                core_principles=["Principle A", "Principle B"],
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Alternative framework dependencies not available")

    @pytest.mark.asyncio
    async def test_compare_paradigms_tool(self):
        """Test paradigm comparison"""
        try:
            result = await compare_paradigms(
                mainstream_paradigm="classical_mechanics",
                alternative_paradigm="quantum_mechanics",
                domain="theoretical_physics",
                comparison_criteria=["predictive_power", "explanatory_scope"],
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Paradigm comparison dependencies not available")

    @pytest.mark.asyncio
    async def test_validate_novel_theory_tool(self):
        """Test novel theory validation"""
        try:
            result = await validate_novel_theory(
                domain="theoretical_physics",
                theory_framework={
                    "name": "quantum_field_theory",
                    "core_principles": ["Fields are fundamental"],
                },
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Novel theory validation dependencies not available")

    @pytest.mark.asyncio
    async def test_cultivate_innovation_tool(self):
        """Test innovation cultivation"""
        try:
            result = await cultivate_innovation(
                domain="theoretical_physics",
                research_idea="A new approach to quantum gravity",
                innovation_goals=["Unify GR and QM"],
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Innovation cultivation dependencies not available")

    @pytest.mark.asyncio
    async def test_assess_foundational_assumptions_tool(self):
        """Test foundational assumptions assessment"""
        try:
            result = await assess_foundational_assumptions(
                domain="theoretical_physics", current_paradigm="standard_model"
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Foundational assumptions dependencies not available")

    @pytest.mark.asyncio
    async def test_generate_critical_questions_tool(self):
        """Test critical questions generation"""
        try:
            result = await generate_critical_questions(
                research_area="quantum_mechanics",
                paradigm_context="Copenhagen Interpretation",
                domain="theoretical_physics",
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Critical questions dependencies not available")

    @pytest.mark.asyncio
    async def test_evaluate_paradigm_shift_potential_tool(self):
        """Test paradigm shift potential evaluation"""
        try:
            result = await evaluate_paradigm_shift_potential(
                domain="theoretical_physics",
                theory_framework="A new theory of quantum_gravity",
            )

            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0

        except ImportError:
            pytest.skip("Paradigm shift evaluation dependencies not available")


@pytest.mark.skipif(
    not NOVEL_THEORY_TOOLS_AVAILABLE,
    reason="Novel Theory Development tools not available",
)
class TestNovelTheoryToolRegistration:
    """Test novel theory development tool registration"""

    def test_novel_theory_tools_registration(self):
        """Test that novel theory tools are properly registered"""
        try:
            mock_server = Mock()
            mock_server.register_tool = Mock()

            # Register tools
            register_novel_theory_tools(mock_server)

            # Verify tools were registered
            assert mock_server.register_tool.called

        except ImportError:
            pytest.skip("Novel theory tools not available")


@pytest.mark.skipif(
    not NOVEL_THEORY_TOOLS_AVAILABLE,
    reason="Novel Theory Development tools not available",
)
@pytest.mark.usefixtures("active_project_context")
class TestNovelTheoryWorkflows:
    """Test novel theory development workflows"""

    @pytest.mark.asyncio
    async def test_complete_theory_development_workflow(self):
        """Test complete novel theory development workflow"""
        try:
            # Workflow: challenge -> develop -> compare -> validate -> assess -> question -> evaluate

            # Step 1: Initiate paradigm challenge
            challenge_result = await initiate_paradigm_challenge(
                domain="test", current_paradigm="test", challenge_area="test"
            )
            assert challenge_result is not None

            # Step 2: Develop alternative framework
            framework_result = await develop_alternative_framework(
                domain="test", core_principles=["test"]
            )
            assert framework_result is not None

            # Step 3: Compare paradigms
            compare_result = await compare_paradigms(
                mainstream_paradigm="test",
                alternative_paradigm="test2",
                domain="test",
                comparison_criteria=["test"],
            )
            assert compare_result is not None

            # Step 4: Validate novel theory
            validate_result = await validate_novel_theory(
                theory_framework={"name": "test"}, domain="test"
            )
            assert validate_result is not None

            # Step 5: Assess foundational assumptions
            assess_result = await assess_foundational_assumptions(
                domain="test", current_paradigm="test"
            )
            assert assess_result is not None

            # Step 6: Generate critical questions
            questions_result = await generate_critical_questions(
                research_area="test", paradigm_context="test"
            )
            assert questions_result is not None

            # Step 7: Evaluate paradigm shift potential
            evaluate_result = await evaluate_paradigm_shift_potential(
                theory_framework="test", domain="test"
            )
            assert evaluate_result is not None

        except ImportError:
            pytest.skip("Novel theory tools not available")

    @pytest.mark.asyncio
    async def test_innovation_cultivation_workflow(self):
        """Test innovation cultivation workflow"""
        try:
            # Focus on innovation aspects

            # Cultivate innovation
            innovation_result = await cultivate_innovation(
                domain="test", research_idea="test", innovation_goals=["test"]
            )
            assert innovation_result is not None

            # Generate critical questions for innovation
            questions_result = await generate_critical_questions(
                research_area="test", paradigm_context="test"
            )
            assert questions_result is not None

            # Assess foundational assumptions that may limit innovation
            assess_result = await assess_foundational_assumptions(
                domain="test", current_paradigm="test"
            )
            assert assess_result is not None

        except ImportError:
            pytest.skip("Innovation tools not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
