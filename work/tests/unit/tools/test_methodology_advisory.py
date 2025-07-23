#!/usr/bin/env python3
"""
Test Methodology Advisory Tools with REAL Database Logging
No mocks - testing the actual implementation
"""

import pytest
import asyncio
import tempfile
import json
import sqlite3
from pathlib import Path
import sys

# Add MCP code to path
project_root = Path(__file__).parent.parent.parent
mcp_path = project_root / 'work' / 'code' / 'mcp'
sys.path.insert(0, str(mcp_path))

from utils.current_project import set_current_project, clear_current_project
from storage.sqlite_manager import SQLiteManager
from tools.methodology_advisory import explain_methodology, compare_approaches, validate_design, ensure_ethics

class TestMethodologyAdvisoryWithLogging:
    """Test methodology advisory tools with real database logging"""
    
    @pytest.fixture
    async def test_project_with_db(self):
        """Create test project with initialized database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / 'test_project'
            project_path.mkdir()
            srrd_dir = project_path / '.srrd'
            srrd_dir.mkdir()
            
            # Create config
            config = {
                'project_name': 'Database Logging Test Project',
                'domain': 'software_engineering',
                'version': '0.1.0'
            }
            
            with open(srrd_dir / 'config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            # Initialize database with proper schema
            db_path = srrd_dir / 'sessions.db'
            sqlite_manager = SQLiteManager(str(db_path))
            await sqlite_manager.initialize()
            await sqlite_manager.close()
            
            # Set as current project
            set_current_project(str(project_path))
            
            yield project_path, str(db_path)
            
            # Cleanup
            clear_current_project()
    
    def count_tool_usage_entries(self, db_path: str, tool_name: str = None) -> int:
        """Count entries in tool_usage table"""
        conn = sqlite3.connect(db_path)
        if tool_name:
            cursor = conn.execute("SELECT COUNT(*) FROM tool_usage WHERE tool_name = ?", (tool_name,))
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM tool_usage")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_latest_tool_entry(self, db_path: str):
        """Get the latest tool usage entry"""
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("""
            SELECT tool_name, research_category, arguments, success, timestamp 
            FROM tool_usage 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        entry = cursor.fetchone()
        conn.close()
        return entry
    
    @pytest.mark.asyncio
    async def test_explain_methodology_with_logging(self, test_project_with_db):
        """Test explain_methodology tool logs to database"""
        project_path, db_path = test_project_with_db
        
        # Check initial state
        initial_count = self.count_tool_usage_entries(db_path)
        
        # Call the tool
        result = await explain_methodology(
            research_question="How to measure software quality effectively?",
            domain="software_engineering"
        )
        
        # Verify tool executed successfully
        assert result is not None
        assert len(result) > 0
        assert "research_question" in result
        
        # Verify database logging
        final_count = self.count_tool_usage_entries(db_path)
        assert final_count == initial_count + 1, f"Expected 1 new entry, got {final_count - initial_count}"
        
        # Verify entry details
        latest_entry = self.get_latest_tool_entry(db_path)
        assert latest_entry is not None
        tool_name, category, arguments, success, timestamp = latest_entry
        
        assert tool_name == "explain_methodology"
        assert category == "methodology_advisory"
        assert success == 1  # True
        assert arguments is not None
        
        # Parse and verify arguments
        parsed_args = json.loads(arguments)
        assert "research_question" in parsed_args
        assert "domain" in parsed_args
        assert parsed_args["research_question"] == "How to measure software quality effectively?"
        assert parsed_args["domain"] == "software_engineering"
    
    @pytest.mark.asyncio
    async def test_compare_approaches_with_logging(self, test_project_with_db):
        """Test compare_approaches tool logs to database"""
        project_path, db_path = test_project_with_db
        
        initial_count = self.count_tool_usage_entries(db_path, "compare_approaches")
        
        result = await compare_approaches(
            approach_a="Unit Testing",
            approach_b="Integration Testing",
            research_context="Software Quality Assurance"
        )
        
        assert result is not None
        assert "approach" in result.lower() or "comparison" in result.lower()
        
        final_count = self.count_tool_usage_entries(db_path, "compare_approaches")
        assert final_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_validate_design_with_logging(self, test_project_with_db):
        """Test validate_design tool logs to database"""
        project_path, db_path = test_project_with_db
        
        initial_count = self.count_tool_usage_entries(db_path, "validate_design")
        
        result = await validate_design(
            research_design={
                "type": "experimental",
                "participants": 100,
                "variables": ["performance", "usability"]
            },
            domain="software_engineering"
        )
        
        assert result is not None
        assert "design" in result.lower() or "validation" in result.lower()
        
        final_count = self.count_tool_usage_entries(db_path, "validate_design")
        assert final_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_ensure_ethics_with_logging(self, test_project_with_db):
        """Test ensure_ethics tool logs to database"""
        project_path, db_path = test_project_with_db
        
        initial_count = self.count_tool_usage_entries(db_path, "ensure_ethics")
        
        result = await ensure_ethics(
            research_proposal={
                "title": "Software Testing Study",
                "participants": "software developers",
                "data_collection": ["surveys", "interviews"]
            },
            domain="software_engineering"
        )
        
        assert result is not None
        assert "ethics" in result.lower() or "consent" in result.lower()
        
        final_count = self.count_tool_usage_entries(db_path, "ensure_ethics")
        assert final_count == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_all_methodology_tools_workflow_with_logging(self, test_project_with_db):
        """Test complete methodology workflow with database logging"""
        project_path, db_path = test_project_with_db
        
        initial_count = self.count_tool_usage_entries(db_path)
        
        # Run complete methodology workflow
        tools_results = []
        
        # 1. Explain methodology
        result1 = await explain_methodology(
            research_question="How effective is test-driven development?",
            domain="software_engineering"
        )
        tools_results.append(("explain_methodology", result1))
        
        # 2. Compare approaches
        result2 = await compare_approaches(
            approach_a="Test-Driven Development",
            approach_b="Behavior-Driven Development",
            research_context="Software Development Methodologies"
        )
        tools_results.append(("compare_approaches", result2))
        
        # 3. Validate design
        result3 = await validate_design(
            research_design={
                "type": "controlled_experiment",
                "participants": 60,
                "groups": ["TDD", "BDD", "Control"]
            },
            domain="software_engineering"
        )
        tools_results.append(("validate_design", result3))
        
        # 4. Ensure ethics
        result4 = await ensure_ethics(
            research_proposal={
                "title": "TDD vs BDD Effectiveness Study",
                "participants": "professional developers",
                "data_collection": ["code_analysis", "surveys"]
            },
            domain="software_engineering"
        )
        tools_results.append(("ensure_ethics", result4))
        
        # Verify all tools executed successfully
        for tool_name, result in tools_results:
            assert result is not None, f"{tool_name} returned None"
            assert len(result) > 0, f"{tool_name} returned empty result"
        
        # Verify database logging for all tools
        final_count = self.count_tool_usage_entries(db_path)
        expected_new_entries = 4
        actual_new_entries = final_count - initial_count
        
        assert actual_new_entries == expected_new_entries, \
            f"Expected {expected_new_entries} new entries, got {actual_new_entries}"
        
        # Verify each tool was logged
        for tool_name, _ in tools_results:
            tool_count = self.count_tool_usage_entries(db_path, tool_name)
            assert tool_count >= 1, f"No database entry found for {tool_name}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
