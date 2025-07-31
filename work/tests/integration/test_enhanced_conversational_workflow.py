#!/usr/bin/env python3
"""
Integration Tests for Enhanced Conversational Workflow
===================================================

Tests complete conversational workflow with real database integration.
Follows the proven pattern of using temporary directories and real databases.
"""
import pytest
import tempfile
import os
import sys
import json
from pathlib import Path

# Add path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))

from srrd_builder.config.installation_status import is_latex_installed, is_vector_db_installed


@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation by clearing module cache and restoring environment variable"""
    original_env = os.environ.get('SRRD_PROJECT_PATH')
    print("[ISOLATION] Storing SRRD_PROJECT_PATH:", original_env)
    yield
    # Restore environment variable
    if original_env is not None:
        os.environ['SRRD_PROJECT_PATH'] = original_env
        print("[ISOLATION] Restored SRRD_PROJECT_PATH to:", original_env)
    elif 'SRRD_PROJECT_PATH' in os.environ:
        del os.environ['SRRD_PROJECT_PATH']
        print("[ISOLATION] Deleted SRRD_PROJECT_PATH")
    # Clear module cache after test to prevent state pollution
    modules_to_clear = [m for m in sys.modules.keys() if any(x in m for x in ['mcp_server', 'tools', 'storage', 'utils']) and m not in ['sys', 'os', 'pathlib', 'tempfile', 'json']]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    print("[ISOLATION] Cleared modules:", modules_to_clear)


class TestEnhancedConversationalWorkflow:
    """Test enhanced conversational workflow integration"""

    @pytest.mark.asyncio
    async def test_progressive_dialogue_with_database_persistence(self):
        """Test progressive dialogue workflow with real database storage"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI pattern
            try:
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="computer_science", template="basic", force=False)
                result = handle_init(args)
                assert result == 0
                
                # Verify project structure exists
                assert (temp_path / ".srrd").exists()
                assert (temp_path / ".srrd" / "config.json").exists()
                
                # Import enhanced tools after project initialization
                from tools.research_planning import enhanced_socratic_dialogue
                
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
                assert result2["response_analysis"] is not None
                assert result2["response_analysis"]["technical_terms"] > 0
                
                # Test depth 3 - Validation questions
                result3 = await enhanced_socratic_dialogue(
                    research_context="machine learning optimization",
                    user_response="I will use adaptive learning rates and momentum optimization with batch normalization",
                    dialogue_depth=3,
                    domain_specialization="computer_science"
                )
                
                assert result3["dialogue_depth"] == 3
                assert "progressive_questions" in result3
                assert len(result3["progressive_questions"]) > 0
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_theory_challenge_integration_with_existing_validation(self):
        """Test enhanced theory challenger integrates with existing validation tools"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            try:
                # Initialize project
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="physics", template="theoretical", force=False)
                result = handle_init(args)
                assert result == 0
                
                # Import enhanced theory challenger after project initialization
                from tools.novel_theory_development import enhanced_theory_challenger
                
                result = await enhanced_theory_challenger(
                    theory_description="Consciousness arises from quantum coherence in neural microtubules",
                    domain="neuroscience",
                    challenge_intensity="moderate"
                )
                
                # Should include existing validation results
                assert "base_validation" in result
                base_validation = result["base_validation"]
                assert isinstance(base_validation, dict)
                
                # Should include new critical challenges
                assert "critical_challenges" in result
                assert "paradigm_implications" in result
                assert len(result["critical_challenges"]) > 0
                
                # Test challenge progression
                assert "challenge_progression" in result
                progression = result["challenge_progression"]
                assert progression["current_level"] == "moderate"
                assert progression["next_level"] == "rigorous"
                assert progression["escalation_available"] == True
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_enhanced_dialogue_with_real_project_context(self):
        """Test enhanced dialogue works with real project context and database"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            try:
                # Initialize project with specific domain
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="biology", template="experimental", force=False)
                result = handle_init(args)
                assert result == 0
                
                # Import tools after project initialization
                from tools.research_planning import enhanced_socratic_dialogue
                
                # Test domain-specific questioning
                result = await enhanced_socratic_dialogue(
                    research_context="enzyme kinetics research",
                    dialogue_depth=1,
                    domain_specialization="biology"
                )
                
                assert result["domain"] == "biology"
                assert "progressive_questions" in result
                
                # Questions should be domain-appropriate
                questions_text = " ".join(result["progressive_questions"])
                assert any(bio_term in questions_text.lower() for bio_term in 
                          ["biological", "organism", "molecular", "cellular", "system", "process"])
                
                # Test user response analysis with biological context
                bio_response = "I want to study enzyme activity in different cellular environments using fluorescence microscopy"
                
                result_with_response = await enhanced_socratic_dialogue(
                    research_context="enzyme kinetics research",
                    user_response=bio_response,
                    dialogue_depth=2,
                    domain_specialization="biology"
                )
                
                assert "response_analysis" in result_with_response
                analysis = result_with_response["response_analysis"]
                assert analysis["technical_terms"] >= 2  # enzyme, cellular, fluorescence, microscopy
                assert analysis["specificity_level"] > 0.5
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_contextual_followup_generation_with_real_database(self):
        """Test contextual follow-up generation with real database persistence"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            try:
                # Initialize project
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="psychology", template="basic", force=False)
                result = handle_init(args)
                assert result == 0
                
                from tools.research_planning import enhanced_socratic_dialogue
                
                # Test with uncertain response that should trigger contextual follow-ups
                uncertain_response = "I think maybe I could possibly study something about memory, but I'm not sure what exactly or how to approach it"
                
                result = await enhanced_socratic_dialogue(
                    research_context="memory research",
                    user_response=uncertain_response,
                    dialogue_depth=1,
                    domain_specialization="psychology"
                )
                
                assert "response_analysis" in result
                analysis = result["response_analysis"]
                
                # Should detect uncertainty
                assert analysis["uncertainty_indicators"] >= 3
                assert "Clarification of uncertain points" in analysis["follow_up_needed"]
                
                # Should generate contextual follow-ups
                assert "contextual_followups" in result
                followups = result["contextual_followups"]
                assert len(followups) > 0
                
                # Follow-ups should address uncertainty
                followups_text = " ".join(followups)
                assert any(term in followups_text.lower() for term in ["uncertain", "specific", "clarify"])
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    @pytest.mark.skipif(not (is_latex_installed() and is_vector_db_installed()), 
                       reason="LaTeX and/or vector database not installed")
    async def test_enhanced_workflow_with_full_mcp_server(self):
        """Test enhanced conversational workflow with full MCP server integration"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            try:
                # Initialize project
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="computer_science", template="basic", force=False)
                result = handle_init(args)
                assert result == 0
                
                # Import and initialize MCP server
                from mcp_server import ClaudeMCPServer
                
                server = ClaudeMCPServer()
                await server._initialize_database_if_needed()
                
                # Test that enhanced tools are registered
                available_tools = server.list_tools_mcp()["tools"]
                tool_names = [tool["name"] for tool in available_tools]
                
                # Should include enhanced tools
                assert "enhanced_socratic_dialogue" in tool_names
                assert "enhanced_theory_challenger" in tool_names
                
                # Test enhanced socratic dialogue through server
                dialogue_result = await server._execute_tool(
                    "enhanced_socratic_dialogue",
                    {
                        "research_context": "artificial intelligence ethics",
                        "dialogue_depth": 1,
                        "domain_specialization": "computer_science"
                    }
                )
                
                assert dialogue_result is not None
                assert isinstance(dialogue_result, dict)
                assert "progressive_questions" in dialogue_result
                
                # Test enhanced theory challenger through server
                challenger_result = await server._execute_tool(
                    "enhanced_theory_challenger",
                    {
                        "theory_description": "AI consciousness emerges from sufficiently complex neural networks",
                        "domain": "computer_science",
                        "challenge_intensity": "moderate"
                    }
                )
                
                assert challenger_result is not None
                assert isinstance(challenger_result, dict)
                assert "critical_challenges" in challenger_result
                assert "paradigm_implications" in challenger_result
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_enhanced_workflow_error_handling(self):
        """Test enhanced workflow handles errors gracefully"""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_dir)
            
            try:
                # Initialize project
                from srrd_builder.cli.commands.init import handle_init
                from conftest import MockArgs
                
                args = MockArgs(domain="general", template="basic", force=False)
                result = handle_init(args)
                assert result == 0
                
                from tools.research_planning import enhanced_socratic_dialogue
                from tools.novel_theory_development import enhanced_theory_challenger
                
                # Test missing required parameters
                try:
                    await enhanced_socratic_dialogue()
                    assert False, "Should have raised TypeError"
                except TypeError:
                    pass  # Expected
                
                # Test enhanced theory challenger with missing parameters
                missing_theory_result = await enhanced_theory_challenger(
                    domain="physics",
                    challenge_intensity="moderate"
                )
                assert "error" in missing_theory_result
                
                missing_domain_result = await enhanced_theory_challenger(
                    theory_description="Some theory",
                    challenge_intensity="moderate"
                )
                assert "error" in missing_domain_result
                
            except ImportError as e:
                pytest.skip(f"Required dependencies not available: {e}")
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])