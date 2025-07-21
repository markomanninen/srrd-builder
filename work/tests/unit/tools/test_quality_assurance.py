#!/usr/bin/env python3
"""
Test suite for Quality Assurance tools.

Tests simulate_peer_review, check_quality_gates
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import quality assurance tools with error handling
try:
    from work.code.mcp.tools.quality_assurance import (
        QualityAssuranceTool,
        register_quality_tools
    )
    QUALITY_TOOLS_AVAILABLE = True
except ImportError:
    QUALITY_TOOLS_AVAILABLE = False


@pytest.mark.skipif(not QUALITY_TOOLS_AVAILABLE, reason="Quality Assurance tools not available")
class TestQualityAssuranceTools:
    """Test quality assurance functionality"""
    
    def create_test_project(self, name="test_project"):
        """Create a test project directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_test_{name}_")
        project_path = Path(temp_dir)
        
        # Create basic SRRD structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir()
        
        return project_path
    
    @pytest.mark.asyncio
    async def test_simulate_peer_review(self):
        """Test peer review simulation functionality"""
        try:
            tool = QualityAssuranceTool()
            
            test_document = {
                "title": "Test Research Paper",
                "abstract": "This is a test abstract for peer review simulation",
                "content": "Research content for testing peer review functionality"
            }
            
            result = await tool.simulate_peer_review(
                document_content=test_document,
                domain="computer_science",
                review_type="comprehensive",
                novel_theory_mode=False
            )
            
            assert result is not None
            assert isinstance(result, dict)
            assert "overall_score" in result
            assert "detailed_assessment" in result
            
            # Check if review contains expected elements
            assert result["overall_score"] > 0
            assert len(result["areas_for_improvement"]) > 0
            
        except ImportError:
            pytest.skip("Peer review simulation dependencies not available")
    
    @pytest.mark.asyncio
    async def test_check_quality_gates(self):
        """Test quality gates checking functionality"""
        try:
            tool = QualityAssuranceTool()
            
            test_research_content = {
                "methodology": "Experimental design with control groups",
                "data_analysis": "Statistical analysis using ANOVA",
                "conclusions": "Significant results found with p < 0.05",
                "literature_review": "Comprehensive review of 50+ papers"
            }
            
            result = await tool.check_quality_gates(
                research_content=test_research_content,
                phase="analysis",
                domain_standards={"statistical_significance": 0.05},
                innovation_criteria={"novelty_score": 0.7}
            )
            
            assert result is not None
            assert isinstance(result, dict)
            assert "gate_results" in result or "overall_score" in result
            assert "gate_results" in result
            assert len(result["gate_results"]) > 0
            
            # Check if quality gates assessment is provided
            assert result["overall_pass_rate"] >= 0.0
            
        except ImportError:
            pytest.skip("Quality gates dependencies not available")
    
    @pytest.mark.asyncio
    async def test_peer_review_with_novel_theory_mode(self):
        """Test peer review simulation with novel theory mode"""
        try:
            tool = QualityAssuranceTool()
            
            test_document = {
                "title": "Novel Theory in Quantum Computing",
                "abstract": "Proposing a new theoretical framework for quantum algorithms",
                "content": "Revolutionary approach to quantum state manipulation"
            }
            
            result = await tool.simulate_peer_review(
                document_content=test_document,
                domain="physics",
                review_type="novel_theory",
                novel_theory_mode=True
            )
            
            assert result is not None
            assert isinstance(result, dict)
            assert "overall_score" in result
            
            # Novel theory mode should provide different type of review
            assert "novel_theory_evaluation" in result
            assert result["overall_score"] >= 0.0
            
        except ImportError:
            pytest.skip("Novel theory peer review dependencies not available")
    
    @pytest.mark.asyncio
    async def test_quality_gates_different_phases(self):
        """Test quality gates for different research phases"""
        try:
            tool = QualityAssuranceTool()
            
            test_content = {
                "research_question": "How does X affect Y?",
                "hypothesis": "X positively correlates with Y",
                "methodology": "Controlled experimental design"
            }
            
            phases = ["planning", "execution", "analysis", "writing"]
            
            for phase in phases:
                result = await tool.check_quality_gates(
                    research_content=test_content,
                    phase=phase
                )
                
                assert result is not None
                assert isinstance(result, dict)
                assert "gate_results" in result or "overall_score" in result
                
        except ImportError:
            pytest.skip("Quality gates phase testing dependencies not available")


@pytest.mark.skipif(not QUALITY_TOOLS_AVAILABLE, reason="Quality Assurance tools not available")
class TestQualityToolRegistration:
    """Test quality assurance tool registration"""
    
    def test_quality_tools_registration(self):
        """Test that quality tools are properly registered"""
        try:
            mock_server = Mock()
            mock_server.register_tool = Mock()
            
            # Register tools
            register_quality_tools(mock_server)
            
            # Verify tools were registered
            assert mock_server.register_tool.called
            
        except ImportError:
            pytest.skip("Quality tools not available")


@pytest.mark.skipif(not QUALITY_TOOLS_AVAILABLE, reason="Quality Assurance tools not available") 
class TestQualityToolParameters:
    """Test quality assurance tool parameter validation"""
    
    @pytest.mark.asyncio
    async def test_peer_review_parameter_validation(self):
        """Test peer review parameter validation"""
        try:
            tool = QualityAssuranceTool()
            
            # Test missing required parameters
            with pytest.raises((TypeError, ValueError)):
                await tool.simulate_peer_review()  # Missing required parameters
            
            # Test with minimal required parameters
            test_doc = {"title": "Test", "content": "Test content"}
            result = await tool.simulate_peer_review(
                document_content=test_doc,
                domain="general"
            )
            assert result is not None
            
        except ImportError:
            pytest.skip("Peer review parameter validation not available")
    
    @pytest.mark.asyncio
    async def test_quality_gates_parameter_validation(self):
        """Test quality gates parameter validation"""
        try:
            tool = QualityAssuranceTool()
            
            # Test missing required parameters
            with pytest.raises((TypeError, ValueError)):
                await tool.check_quality_gates()  # Missing required parameters
            
            # Test with minimal required parameters
            test_content = {"methodology": "Test methodology"}
            result = await tool.check_quality_gates(
                research_content=test_content,
                phase="planning"
            )
            assert result is not None
            
        except ImportError:
            pytest.skip("Quality gates parameter validation not available")


@pytest.mark.skipif(not QUALITY_TOOLS_AVAILABLE, reason="Quality Assurance tools not available")
class TestQualityAssuranceWorkflow:
    """Test quality assurance workflow integration"""
    
    @pytest.mark.asyncio
    async def test_complete_quality_workflow(self):
        """Test complete quality assurance workflow"""
        try:
            tool = QualityAssuranceTool()
            
            # Step 1: Check quality gates during planning
            planning_content = {
                "research_question": "How does machine learning impact productivity?",
                "methodology": "Mixed methods approach with surveys and experiments"
            }
            
            planning_result = await tool.check_quality_gates(
                research_content=planning_content,
                phase="planning"
            )
            assert planning_result is not None
            
            # Step 2: Simulate peer review of completed research
            research_document = {
                "title": "Machine Learning Impact on Productivity",
                "abstract": "Study of ML tools on workplace productivity",
                "methodology": planning_content["methodology"],
                "results": "Significant productivity improvements observed",
                "conclusions": "ML tools increase productivity by 25%"
            }
            
            peer_review_result = await tool.simulate_peer_review(
                document_content=research_document,
                domain="computer_science",
                review_type="comprehensive"
            )
            assert peer_review_result is not None
            
            # Step 3: Final quality gates check
            final_content = {**planning_content, **research_document}
            final_result = await tool.check_quality_gates(
                research_content=final_content,
                phase="writing"
            )
            assert final_result is not None
            
        except ImportError:
            pytest.skip("Quality workflow dependencies not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
