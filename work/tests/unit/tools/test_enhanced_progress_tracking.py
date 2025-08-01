#!/usr/bin/env python3
"""
Unit Tests for Enhanced Progress Tracking
======================================

Tests enhanced progress tracking and visualization functionality:
- Visual progress summary generation
- Milestone detection and celebration
- ASCII chart creation
"""
import pytest
import tempfile
from pathlib import Path

class TestEnhancedProgressTracking:
    """Test enhanced progress tracking functionality"""

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

    def test_progress_bar_creation(self):
        """Test ASCII progress bar creation"""
        from tools.research_continuity import _create_progress_bar
        
        # Test 0% progress
        bar_0 = _create_progress_bar(0, width=10)
        assert bar_0 == "[░░░░░░░░░░]"
        
        # Test 50% progress
        bar_50 = _create_progress_bar(50, width=10)
        assert bar_50 == "[█████░░░░░]"
        
        # Test 100% progress
        bar_100 = _create_progress_bar(100, width=10)
        assert bar_100 == "[██████████]"

    @pytest.mark.asyncio
    async def test_progress_metrics_extraction(self):
        """Test progress metrics extraction from real database"""
        from tools.research_continuity import _extract_progress_metrics
        from storage.sqlite_manager import SQLiteManager
        
        # Create temporary database with test data using the correct path structure
        temp_dir = self.create_temp_dir("metrics")
        # Create the .srrd/data directory structure that _extract_progress_metrics expects
        srrd_data_dir = temp_dir / ".srrd" / "data"
        srrd_data_dir.mkdir(parents=True, exist_ok=True)
        db_path = srrd_data_dir / "sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Insert test tool usage data
        test_tools = [
            ("clarify_research_goals", "2024-01-01 10:00:00"),
            ("suggest_methodology", "2024-01-01 11:00:00"),
            ("semantic_search", "2024-01-02 09:00:00"),
            ("clarify_research_goals", "2024-01-02 10:00:00")  # Duplicate for frequency
        ]
        
        # First create a project and session
        await sqlite_manager.connection.execute(
            "INSERT INTO projects (name, domain) VALUES (?, ?)",
            ("test_project", "test_domain")
        )
        project_id = 1
        
        await sqlite_manager.connection.execute(
            "INSERT INTO sessions (project_id, current_research_act, research_focus) VALUES (?, ?, ?)",
            (project_id, "conceptualization", "test research")
        )
        session_id = 1
        
        for tool_name, timestamp in test_tools:
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, tool_name, timestamp, f"{tool_name} completed", "conceptualization", "planning")
            )
        await sqlite_manager.connection.commit()
        await sqlite_manager.close()
        
        # Test metrics extraction
        metrics = await _extract_progress_metrics(str(temp_dir))
        
        assert "research_acts" in metrics
        assert "tool_usage" in metrics
        assert "velocity_data" in metrics
        
        # Check research acts progress
        assert "conceptualization" in metrics["research_acts"]
        conceptualization = metrics["research_acts"]["conceptualization"]
        
        # Should have 2/3 conceptualization tools completed (clarify_research_goals, suggest_methodology)
        # semantic_search is not in the conceptualization tool list
        assert conceptualization["completion_percentage"] > 0
        assert conceptualization["completed_tools"] >= 1
        
        # Check tool usage frequency
        assert "clarify_research_goals" in metrics["tool_usage"]
        assert metrics["tool_usage"]["clarify_research_goals"] == 2  # Used twice

    @pytest.mark.asyncio
    async def test_milestone_detection(self):
        """Test milestone detection functionality"""
        from tools.research_continuity import _detect_act_completion_milestones
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("milestones")
        # Create the .srrd/data directory structure
        srrd_data_dir = temp_dir / ".srrd" / "data"
        srrd_data_dir.mkdir(parents=True, exist_ok=True)
        db_path = srrd_data_dir / "sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # First create a project and session
        await sqlite_manager.connection.execute(
            "INSERT INTO projects (name, domain) VALUES (?, ?)",
            ("test_project", "test_domain")
        )
        project_id = 1
        
        await sqlite_manager.connection.execute(
            "INSERT INTO sessions (project_id, current_research_act, research_focus) VALUES (?, ?, ?)",
            (project_id, "conceptualization", "test research")
        )
        session_id = 1
        
        # Insert tools to complete conceptualization act (80%+ completion)
        conceptualization_tools = ["clarify_research_goals", "assess_foundational_assumptions", "generate_critical_questions"]
        
        for tool_name in conceptualization_tools:
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, tool_name, "2024-01-01 10:00:00", f"{tool_name} completed", "conceptualization", "planning")
            )
        await sqlite_manager.connection.commit()
        
        # Test milestone detection
        milestones = await _detect_act_completion_milestones(sqlite_manager)
        
        # Should detect conceptualization completion milestone
        assert len(milestones) > 0
        conceptualization_milestone = next(
            (m for m in milestones if "Conceptualization" in m["title"]), 
            None
        )
        assert conceptualization_milestone is not None
        assert conceptualization_milestone["icon"] == "🎯"
        assert "foundation established" in conceptualization_milestone["significance"]
        
        await sqlite_manager.close()

    def test_velocity_chart_creation(self):
        """Test velocity trend chart creation"""
        from tools.research_continuity import _create_velocity_chart
        
        # Test with sample velocity data
        velocity_data = [
            {"date": "2024-01-01", "daily_velocity": 2},
            {"date": "2024-01-02", "daily_velocity": 5},
            {"date": "2024-01-03", "daily_velocity": 3},
            {"date": "2024-01-04", "daily_velocity": 1}
        ]
        
        chart = _create_velocity_chart(velocity_data)
        
        assert "2024-01-01" in chart
        assert "2024-01-02" in chart
        assert "▓" in chart  # Should contain chart bars
        assert "░" in chart  # Should contain empty spaces
        
        # Test with empty data
        empty_chart = _create_velocity_chart([])
        assert "Insufficient data" in empty_chart

    @pytest.mark.asyncio
    async def test_usage_pattern_milestone_detection(self):
        """Test usage pattern milestone detection"""
        from tools.research_continuity import _detect_usage_pattern_milestones
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("usage_patterns")
        # Create the .srrd/data directory structure
        srrd_data_dir = temp_dir / ".srrd" / "data"
        srrd_data_dir.mkdir(parents=True, exist_ok=True)
        db_path = srrd_data_dir / "sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # First create a project and session
        await sqlite_manager.connection.execute(
            "INSERT INTO projects (name, domain) VALUES (?, ?)",
            ("test_project", "test_domain")
        )
        project_id = 1
        
        await sqlite_manager.connection.execute(
            "INSERT INTO sessions (project_id, current_research_act, research_focus) VALUES (?, ?, ?)",
            (project_id, "conceptualization", "test research")
        )
        session_id = 1
        
        # Insert 15 tool usage records to trigger usage milestone
        for i in range(15):
            await sqlite_manager.connection.execute(
                "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, f"test_tool_{i % 3}", "2024-01-01 10:00:00", "completed", "conceptualization", "planning")
            )
        await sqlite_manager.connection.commit()
        
        milestones = await _detect_usage_pattern_milestones(sqlite_manager)
        
        # Should detect 10 tools used milestone
        usage_milestone = next(
            (m for m in milestones if "Tools Used Milestone" in m["title"]), 
            None
        )
        assert usage_milestone is not None
        assert usage_milestone["icon"] == "🔧"
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_velocity_milestone_detection(self):
        """Test velocity milestone detection"""
        from tools.research_continuity import _detect_velocity_milestones
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("velocity")
        # Create the .srrd/data directory structure
        srrd_data_dir = temp_dir / ".srrd" / "data"
        srrd_data_dir.mkdir(parents=True, exist_ok=True)
        db_path = srrd_data_dir / "sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # First create a project and session
        await sqlite_manager.connection.execute(
            "INSERT INTO projects (name, domain) VALUES (?, ?)",
            ("test_project", "test_domain")
        )
        project_id = 1
        
        await sqlite_manager.connection.execute(
            "INSERT INTO sessions (project_id, current_research_act, research_focus) VALUES (?, ?, ?)",
            (project_id, "conceptualization", "test research")
        )
        session_id = 1
        
        # Insert data for 6 days with 3+ tools per day to trigger velocity milestone
        from datetime import datetime, timedelta
        base_date = datetime.now()
        
        for day_offset in range(6):
            date = base_date - timedelta(days=day_offset)
            for tool_num in range(4):  # 4 tools per day
                await sqlite_manager.connection.execute(
                    "INSERT INTO tool_usage (session_id, tool_name, timestamp, result_summary, research_act, research_category) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, f"tool_{tool_num}", date.strftime("%Y-%m-%d %H:%M:%S"), "completed", "conceptualization", "planning")
                )
        await sqlite_manager.connection.commit()
        
        milestones = await _detect_velocity_milestones(sqlite_manager)
        
        # Should detect consistent momentum milestone (5+ active days)
        velocity_milestone = next(
            (m for m in milestones if "Consistent Research Momentum" in m["title"]), 
            None
        )
        assert velocity_milestone is not None
        assert velocity_milestone["icon"] == "⚡"
        
        await sqlite_manager.close()

    def test_progress_bar_edge_cases(self):
        """Test progress bar creation with edge cases"""
        from tools.research_continuity import _create_progress_bar
        
        # Test very small percentage
        bar_small = _create_progress_bar(0.1, width=10)
        assert "[░░░░░░░░░░]" == bar_small  # Should round down to 0
        
        # Test percentage over 100
        bar_over = _create_progress_bar(150, width=10)
        assert "[██████████]" == bar_over  # Should cap at 100%
        
        # Test very small width
        bar_tiny = _create_progress_bar(50, width=2)
        assert "[█░]" == bar_tiny