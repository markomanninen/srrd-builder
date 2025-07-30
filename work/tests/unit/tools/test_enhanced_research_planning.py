#!/usr/bin/env python3
"""
Unit Tests for Enhanced Research Planning Tools
============================================

Tests enhanced conversational guidance functionality:
- Progressive Socratic questioning
- User response analysis
- Contextual follow-up generation
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from work.code.mcp.utils import current_project as current_project_module

# Import enhanced research planning tools with error handling
try:
    from work.code.mcp.tools.research_planning import (
        ResearchPlanningTool,
        enhanced_socratic_dialogue,
        clarify_research_goals,
        suggest_methodology,
        register_research_tools,
    )
    ENHANCED_RESEARCH_TOOLS_AVAILABLE = True
except ImportError:
    ENHANCED_RESEARCH_TOOLS_AVAILABLE = False


@pytest.fixture
def active_project_context():
    """
    Creates a temporary project and sets it as the active context for the duration of a test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / ".srrd").mkdir()
        (project_path / ".srrd" / "config.json").write_text(
            '{"name": "test_enhanced_planning_project"}'
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
    not ENHANCED_RESEARCH_TOOLS_AVAILABLE, reason="Enhanced Research Planning tools not available"
)
class TestEnhancedResearchPlanning:
    """Test enhanced research planning functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def create_temp_dir(self, name: str) -> Path:
        """Create temporary directory for testing"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix=f"test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path

    @pytest.mark.asyncio
    async def test_enhanced_socratic_dialogue_progression(self):
        """Test progressive Socratic dialogue functionality"""
        tool = ResearchPlanningTool()
        
        # Test depth 1 (clarification questions)
        result_depth1 = await tool.enhanced_socratic_dialogue(
            research_context="quantum computing research",
            dialogue_depth=1,
            focus_area="clarification",
            domain_specialization="computer_science"
        )
        
        assert "progressive_questions" in result_depth1
        assert len(result_depth1["progressive_questions"]) <= 2
        assert result_depth1["dialogue_depth"] == 1
        assert result_depth1["suggested_next_depth"] == 2
        assert result_depth1["domain"] == "computer_science"
        assert result_depth1["focus_area"] == "clarification"
        
        # Test depth 2 (assumption questions)
        result_depth2 = await tool.enhanced_socratic_dialogue(
            research_context="quantum computing research",
            user_response="I want to develop quantum algorithms for optimization",
            dialogue_depth=2,
            focus_area="assumption",
            domain_specialization="computer_science"
        )
        
        assert result_depth2["dialogue_depth"] == 2
        assert "response_analysis" in result_depth2
        assert result_depth2["response_analysis"] is not None

    def test_user_response_analysis(self):
        """Test user response analysis functionality"""        
        tool = ResearchPlanningTool()
        
        # Test sophisticated response
        sophisticated_response = "I am developing lattice-based post-quantum cryptographic algorithms using ring learning with errors problems to ensure security against quantum adversaries"
        
        analysis = tool._analyze_user_response(sophisticated_response, "clarification")
        
        assert analysis["technical_terms"] >= 3
        assert analysis["specificity_level"] > 0.7
        assert len(analysis["follow_up_needed"]) <= 1

        # Test simple response
        simple_response = "I think I want to do something with computers maybe"
        
        simple_analysis = tool._analyze_user_response(simple_response, "clarification")
        
        assert simple_analysis["technical_terms"] < 2
        assert simple_analysis["uncertainty_indicators"] >= 2
        assert "More specific details needed" in simple_analysis["follow_up_needed"]

    def test_contextual_followup_generation(self):
        """Test contextual follow-up question generation"""        
        tool = ResearchPlanningTool()
        
        # Test analysis that needs more specificity
        analysis = {
            "response_length": 5,
            "technical_terms": 0,
            "uncertainty_indicators": 1,
            "specificity_level": 0.3,
            "follow_up_needed": ["More specific details needed"]
        }
        
        followups = tool._generate_contextual_followups(analysis, "computer_science", 1)
        
        assert len(followups) > 0
        assert any("specific" in q.lower() for q in followups)

        # Test analysis with uncertainty
        uncertain_analysis = {
            "response_length": 15,
            "technical_terms": 1,
            "uncertainty_indicators": 3,
            "specificity_level": 0.6,
            "follow_up_needed": ["Clarification of uncertain points"]
        }
        
        uncertain_followups = tool._generate_contextual_followups(uncertain_analysis, "biology", 2)
        
        assert len(uncertain_followups) > 0
        assert any("uncertain" in q.lower() for q in uncertain_followups)

    def test_domain_specific_question_banks(self):
        """Test that enhanced question banks include new domains"""        
        tool = ResearchPlanningTool()
        
        # Test computer science domain
        assert "computer_science" in tool.socratic_questions
        assert "clarification" in tool.socratic_questions["computer_science"]
        assert "assumption" in tool.socratic_questions["computer_science"]
        assert "validation" in tool.socratic_questions["computer_science"]
        
        # Test biology domain
        assert "biology" in tool.socratic_questions
        assert "methodology" in tool.socratic_questions["biology"]
        assert "validation" in tool.socratic_questions["biology"]
        
        # Test psychology domain
        assert "psychology" in tool.socratic_questions
        assert "clarification" in tool.socratic_questions["psychology"]
        assert "methodology" in tool.socratic_questions["psychology"]

    def test_technical_terms_counting(self):
        """Test technical terms counting functionality"""        
        tool = ResearchPlanningTool()
        
        # Test text with many technical terms
        technical_text = "Using machine learning algorithms and neural networks for data analysis and statistical validation of experimental hypotheses"
        technical_count = tool._count_technical_terms(technical_text)
        assert technical_count >= 5
        
        # Test text with few technical terms
        simple_text = "I want to study how people learn new things"
        simple_count = tool._count_technical_terms(simple_text)
        assert simple_count <= 2

    def test_uncertainty_detection(self):
        """Test uncertainty indicators detection"""        
        tool = ResearchPlanningTool()
        
        # Test text with uncertainty
        uncertain_text = "I think maybe I could possibly study something, but I'm not sure"
        uncertain_count = tool._detect_uncertainty(uncertain_text)
        assert uncertain_count >= 3
        
        # Test confident text
        confident_text = "I will develop a new algorithm that solves this specific problem"
        confident_count = tool._detect_uncertainty(confident_text)
        assert confident_count <= 1

    def test_specificity_assessment(self):
        """Test specificity level assessment"""        
        tool = ResearchPlanningTool()
        
        # Test specific text
        specific_text = "I will precisely measure and quantify the specific effects of temperature on enzyme activity"
        specific_score = tool._assess_specificity(specific_text)
        assert specific_score > 0.6
        
        # Test general text
        general_text = "I want to generally study some things about biology"
        general_score = tool._assess_specificity(general_text)
        assert general_score < 0.5


@pytest.mark.skipif(
    not ENHANCED_RESEARCH_TOOLS_AVAILABLE, reason="Enhanced Research Planning tools not available"
)
@pytest.mark.usefixtures("active_project_context")
class TestEnhancedConversationalWorkflow:
    """Test enhanced conversational workflow integration"""

    @pytest.mark.asyncio
    async def test_progressive_dialogue_with_context_awareness(self):
        """Test progressive dialogue workflow maintains context"""
        # Test depth 1 - Initial clarification
        result1 = await enhanced_socratic_dialogue(
            research_context="machine learning optimization",
            dialogue_depth=1,
            domain_specialization="computer_science"
        )
        
        assert result1["dialogue_depth"] == 1
        assert len(result1["progressive_questions"]) > 0
        assert result1["domain"] == "computer_science"
        assert result1["research_context"] == "machine learning optimization"
        
        # Test depth 2 - With user response
        result2 = await enhanced_socratic_dialogue(
            research_context="machine learning optimization", 
            user_response="I want to optimize neural network training using novel gradient descent variants",
            dialogue_depth=2,
            domain_specialization="computer_science"
        )
        
        assert result2["dialogue_depth"] == 2
        assert "response_analysis" in result2
        assert result2["response_analysis"]["technical_terms"] > 0

    @pytest.mark.asyncio
    async def test_enhanced_dialogue_integration_with_existing_tools(self):
        """Test enhanced dialogue integrates with existing clarify_research_goals"""
        # Test existing tool still works
        existing_result = await clarify_research_goals(
            research_area="artificial intelligence",
            initial_goals="Develop better AI systems"
        )
        
        assert existing_result is not None
        assert isinstance(existing_result, dict)
        
        # Test enhanced tool works independently
        enhanced_result = await enhanced_socratic_dialogue(
            research_context="artificial intelligence development",
            dialogue_depth=1,
            domain_specialization="computer_science"
        )
        
        assert enhanced_result is not None
        assert isinstance(enhanced_result, dict)
        assert "progressive_questions" in enhanced_result

    @pytest.mark.asyncio
    async def test_enhanced_dialogue_missing_parameters(self):
        """Test enhanced dialogue handles missing parameters gracefully"""
        # Missing research_context should raise TypeError
        with pytest.raises(TypeError):
            await enhanced_socratic_dialogue(
                dialogue_depth=1,
                domain_specialization="computer_science"
            )

    @pytest.mark.asyncio
    async def test_enhanced_dialogue_parameter_defaults(self):
        """Test enhanced dialogue uses appropriate defaults"""
        result = await enhanced_socratic_dialogue(
            research_context="quantum computing research"
        )
        
        # Check defaults are applied
        assert result["dialogue_depth"] == 1  # default
        assert result["focus_area"] == "clarification"  # default
        assert result["domain"] == "general"  # default


class TestEnhancedResearchPlanningToolRegistration:
    """Test enhanced research planning tool registration"""

    def test_enhanced_research_tools_registration(self):
        """Test that enhanced research planning tools are properly registered"""
        try:
            from unittest.mock import Mock

            # Mock server for testing registration
            mock_server = Mock()
            mock_server.register_tool = Mock()

            # Register tools
            register_research_tools(mock_server)

            # Verify tools were registered
            assert mock_server.register_tool.called

            # Check for expected tool names including enhanced_socratic_dialogue
            call_args_list = mock_server.register_tool.call_args_list
            if call_args_list and len(call_args_list) > 0:
                # Get registered tool names
                registered_tools = []
                for call in call_args_list:
                    if hasattr(call, 'kwargs') and 'name' in call.kwargs:
                        registered_tools.append(call.kwargs['name'])
                    elif len(call.args) > 0:
                        registered_tools.append(call.args[0])

                expected_tools = ["clarify_research_goals", "suggest_methodology", "enhanced_socratic_dialogue"]

                for tool in expected_tools:
                    assert tool in registered_tools or any(tool in str(reg_tool) for reg_tool in registered_tools)

        except ImportError:
            pytest.skip("Enhanced Research Planning tools not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])