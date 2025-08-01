#!/usr/bin/env python3
"""
Integration Tests for Enhanced Progress System
===========================================

Tests complete enhanced progress system with real database integration.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

class TestEnhancedProgressIntegration:
    """Test enhanced progress system integration"""

    @pytest.mark.asyncio
    async def test_visual_progress_summary_with_real_data(self):
        """Test visual progress summary with real project and database"""
        # Use a more robust approach that doesn't change working directory
        original_cwd = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Mock get_current_project to return our temp directory
                with patch('utils.current_project.get_current_project', return_value=str(temp_path)):
                    # Initialize project using existing CLI
                    from srrd_builder.cli.commands.init import handle_init
                    from tests.conftest import MockArgs
                    
                    # Change to temp dir only for initialization
                    os.chdir(temp_dir)
                    args = MockArgs(domain="computer_science", template="basic")
                    result = handle_init(args)
                    assert result == 0
                    
                    # Restore original directory immediately
                    os.chdir(original_cwd)
                    
                    # Create some research activity with mocked project path
                    from tools.research_planning import clarify_research_goals, suggest_methodology
                    
                    await clarify_research_goals(
                        research_area="machine learning",
                        initial_goals="Optimize neural network training"
                    )
                    
                    await suggest_methodology(
                        research_goals="Neural network optimization", 
                        domain="computer_science"
                    )
                    
                    # Test enhanced visual progress summary
                    from tools.research_continuity import get_visual_progress_summary
                    
                    visual_summary = await get_visual_progress_summary()
                    
                    # Should contain visual elements
                    assert "Visual Research Progress Summary" in visual_summary
                    assert "Research Acts Progress" in visual_summary
                    assert "[" in visual_summary and "]" in visual_summary  # Progress bars
                    assert "█" in visual_summary or "░" in visual_summary  # Bar characters
                    
                    # Should contain tool usage frequency
                    assert "Tool Usage Frequency" in visual_summary
                    assert "clarify_research_goals" in visual_summary
                    assert "suggest_methodology" in visual_summary
                    
                    # Should include original detailed progress (building on existing)
                    assert "Project Information" in visual_summary  # From existing get_research_progress_tool
        
        finally:
            # Always restore original directory
            try:
                os.chdir(original_cwd)
            except (OSError, FileNotFoundError):
                # If original directory no longer exists, change to a safe directory
                os.chdir(os.path.expanduser("~"))

    @pytest.mark.asyncio
    async def test_milestone_detection_with_real_workflow(self):
        """Test milestone detection with actual research workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="physics", template="theoretical")
            result = handle_init(args)
            assert result == 0
            
            # Complete conceptualization phase tools
            from tools.research_planning import clarify_research_goals
            from tools.novel_theory_development import assess_foundational_assumptions
            
            await clarify_research_goals(
                research_area="quantum mechanics",
                initial_goals="Develop new quantum measurement theory"
            )
            
            await assess_foundational_assumptions(
                research_context="Quantum measurement theory development"
            )
            
            # Test milestone detection
            from tools.research_continuity import detect_and_celebrate_milestones
            
            milestones_result = await detect_and_celebrate_milestones()
            
            # Should detect progress-based milestones
            assert "Research Milestones Achieved" in milestones_result or "Keep up the great research work" in milestones_result
            
            # If milestones detected, should have proper formatting
            if "Research Milestones Achieved" in milestones_result:
                assert "🎉" in milestones_result  # Celebration emoji
                assert "Achievement" in milestones_result
                assert "Significance" in milestones_result

    @pytest.mark.asyncio
    async def test_enhanced_progress_system_complete_workflow(self):
        """Test complete enhanced progress system workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="biology", template="experimental")
            result = handle_init(args)
            assert result == 0
            
            # Simulate extended research workflow
            from tools.research_planning import clarify_research_goals, suggest_methodology
            from tools.search_discovery import semantic_search
            
            # Conceptualization phase
            await clarify_research_goals(
                research_area="genetics",
                initial_goals="Study gene expression patterns"
            )
            
            await semantic_search(
                search_query="gene expression analysis methods",
                search_type="academic"
            )
            
            # Design planning phase
            await suggest_methodology(
                research_goals="Gene expression pattern analysis",
                domain="biology"
            )
            
            # Test visual progress summary
            from tools.research_continuity import get_visual_progress_summary
            visual_summary = await get_visual_progress_summary()
            
            # Verify comprehensive visual elements
            assert "Visual Research Progress Summary" in visual_summary
            assert "Research Acts Progress" in visual_summary
            assert "Tool Usage Frequency" in visual_summary
            assert "Project Information" in visual_summary
            
            # Check for progress bars and charts
            assert "[" in visual_summary and "]" in visual_summary
            assert ("█" in visual_summary or "░" in visual_summary)
            
            # Test milestone detection
            from tools.research_continuity import detect_and_celebrate_milestones
            milestones = await detect_and_celebrate_milestones()
            
            # Should provide milestone feedback
            assert isinstance(milestones, str)
            assert len(milestones) > 0

    @pytest.mark.asyncio
    async def test_progress_metrics_accuracy(self):
        """Test accuracy of progress metrics with known tool usage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="chemistry", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Use specific tools to create known progress state
            from tools.research_planning import clarify_research_goals
            from tools.research_continuity import _extract_progress_metrics
            
            # Use conceptualization tools
            await clarify_research_goals(
                research_area="organic chemistry",
                initial_goals="Analyze reaction mechanisms"
            )
            
            # Extract metrics and verify accuracy
            current_dir = Path.cwd()
            metrics = await _extract_progress_metrics(str(current_dir))
            
            # Verify structure
            assert "research_acts" in metrics
            assert "tool_usage" in metrics
            assert "velocity_data" in metrics
            
            # Verify conceptualization progress
            conceptualization = metrics["research_acts"]["conceptualization"]
            assert conceptualization["completion_percentage"] > 0
            assert conceptualization["completed_tools"] > 0
            
            # Verify tool usage tracking
            assert "clarify_research_goals" in metrics["tool_usage"]
            assert metrics["tool_usage"]["clarify_research_goals"] >= 1

    @pytest.mark.asyncio
    async def test_milestone_celebration_formatting(self):
        """Test milestone celebration message formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="mathematics", template="theoretical")
            result = handle_init(args)
            assert result == 0
            
            # Create enough activity to trigger milestones
            from tools.research_planning import clarify_research_goals
            from tools.novel_theory_development import assess_foundational_assumptions
            from tools.search_discovery import semantic_search
            
            # Execute multiple tools to trigger various milestones
            for i in range(3):
                await clarify_research_goals(
                    research_area=f"topology_{i}",
                    initial_goals=f"Study topological invariants {i}"
                )
            
            await assess_foundational_assumptions(
                research_context="Topological analysis"
            )
            
            await semantic_search(
                search_query="topological methods",
                search_type="academic"
            )
            
            # Test milestone detection and formatting
            from tools.research_continuity import detect_and_celebrate_milestones
            celebration = await detect_and_celebrate_milestones()
            
            # Verify proper formatting if milestones are detected
            if "Research Milestones Achieved" in celebration:
                # Should have proper markdown structure
                assert celebration.startswith("# 🎉 Research Milestones Achieved! 🎉")
                assert "Achievement" in celebration
                assert "Significance" in celebration
                assert celebration.endswith("Keep up the excellent research progress! 🚀")

    @pytest.mark.asyncio
    async def test_progress_system_error_handling(self):
        """Test enhanced progress system error handling"""
        # Test with non-existent project path
        from tools.research_continuity import _extract_progress_metrics
        
        with pytest.raises(Exception):
            await _extract_progress_metrics("/nonexistent/path")
        
        # Test velocity chart with invalid data
        from tools.research_continuity import _create_velocity_chart
        
        empty_chart = _create_velocity_chart([])
        assert "Insufficient data" in empty_chart
        
        single_point_chart = _create_velocity_chart([{"date": "2024-01-01", "daily_velocity": 5}])
        assert "Insufficient data" in single_point_chart

    @pytest.mark.asyncio
    async def test_visual_elements_consistency(self):
        """Test consistency of visual elements across different scenarios"""
        from tools.research_continuity import _create_progress_bar, _create_velocity_chart
        
        # Test progress bar consistency
        bars = []
        for percentage in [0, 25, 50, 75, 100]:
            bar = _create_progress_bar(percentage, width=20)
            bars.append(bar)
            
            # All bars should have same format
            assert bar.startswith("[")
            assert bar.endswith("]")
            assert len(bar) == 22  # width + 2 brackets
        
        # Verify progression
        assert bars[0] == "[░░░░░░░░░░░░░░░░░░░░]"  # 0%
        assert bars[-1] == "[████████████████████]"  # 100%
        
        # Test velocity chart consistency
        test_data = [
            {"date": "2024-01-01", "daily_velocity": 1},
            {"date": "2024-01-02", "daily_velocity": 3},
            {"date": "2024-01-03", "daily_velocity": 2}
        ]
        
        chart = _create_velocity_chart(test_data)
        lines = chart.split("\n")
        
        # Each line should have consistent format
        for line in lines:
            assert ":" in line
            assert "[" in line and "]" in line
            assert "tools" in line