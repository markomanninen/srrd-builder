#!/usr/bin/env python3
"""
Unit Tests for Storage Management Tools
=======================================

Tests all 5 storage management MCP tools:
- initialize_project
- save_session  
- search_knowledge
- version_control
- backup_project
"""

import asyncio
import os
import sys
import tempfile
import shutil
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add MCP directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "code" / "mcp"))

try:
    from tools.storage_management import (
        initialize_project_tool,
        save_session_tool,
        search_knowledge_tool,
        version_control_tool,
        backup_project_tool
    )
    from storage.project_manager import ProjectManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Make sure MCP server modules are available")
    sys.exit(1)

class TestStorageTools:
    """Test storage management tools functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_temp_dir(self, name: str) -> Path:
        """Create a temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"storage_test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    @pytest.mark.asyncio
    async def test_initialize_project_tool(self):
        """Test project initialization tool"""
        print("  🏗️  Testing initialize_project_tool...")
        
        project_path = self.create_temp_dir("init_project")
        
        try:
            result = await initialize_project_tool(
                name="Test Storage Project",
                description="Testing storage management initialization",
                domain="theoretical_physics",
                project_path=str(project_path)
            )
            
            self.assert_test(
                "status" in str(result).lower(),
                "Initialize project returns status message"
            )
            
            # Check if .srrd directory was created
            srrd_dir = project_path / '.srrd'
            self.assert_test(
                srrd_dir.exists(),
                ".srrd directory created"
            )
            
            # Check if config was created
            config_file = srrd_dir / 'config.json'
            if config_file.exists():
                self.assert_test(True, "Config file created")
                
                with open(config_file) as f:
                    config = json.load(f)
                    self.assert_test(
                        config.get('name') == "Test Storage Project",
                        "Config contains correct project name"
                    )
            else:
                self.assert_test(False, "Config file not created")
                
        except Exception as e:
            self.assert_test(False, "Initialize project tool execution", str(e))
    
    @pytest.mark.asyncio
    async def test_save_session_tool(self):
        """Test session saving tool"""
        print("  💾 Testing save_session_tool...")
        
        project_path = self.create_temp_dir("save_session")
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            "session_id": "test_session_001",
            "user_id": "test_user",
            "research_phase": "planning",
            "interactions": []
        }
        
        try:
            result = await save_session_tool(
                session_data=session_data,
                project_path=str(project_path)
            )
            
            # Should succeed with valid project path and session data
            self.assert_test(
                "saved" in str(result).lower() or "success" in str(result).lower(),
                "Save session with valid data"
            )
            
        except Exception as e:
            self.assert_test(False, "Save session tool execution", str(e))
        
        # Test with missing session data
        try:
            result = await save_session_tool(project_path=str(project_path))
            
            self.assert_test(
                "error" in str(result).lower() and "session_data" in str(result),
                "Save session rejects missing session_data"
            )
            
        except Exception as e:
            self.assert_test(False, "Save session validation", str(e))
    
    @pytest.mark.asyncio
    async def test_search_knowledge_tool(self):
        """Test knowledge search tool"""
        print("  🔍 Testing search_knowledge_tool...")
        
        project_path = self.create_temp_dir("search_knowledge")
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            result = await search_knowledge_tool(
                query="test research methodology",
                project_path=str(project_path),
                collection="default"
            )
            
            self.assert_test(
                "results" in str(result).lower() or "search" in str(result).lower(),
                "Search knowledge returns results"
            )
            
        except Exception as e:
            self.assert_test(False, "Search knowledge tool execution", str(e))
        
        # Test with missing query
        try:
            result = await search_knowledge_tool(project_path=str(project_path))
            
            self.assert_test(
                "error" in str(result).lower() and "query" in str(result),
                "Search knowledge rejects missing query"
            )
            
        except Exception as e:
            self.assert_test(False, "Search knowledge validation", str(e))
    
    @pytest.mark.asyncio
    async def test_version_control_tool(self):
        """Test version control tool"""
        print("  📝 Testing version_control_tool...")
        
        project_path = self.create_temp_dir("version_control")
        
        # Initialize as git repository
        try:
            import git
            git.Repo.init(project_path)
            
            # Create SRRD project structure
            srrd_dir = project_path / '.srrd'
            srrd_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a test file
            test_file = project_path / "test.md"
            test_file.write_text("Test content for version control")
            
            result = await version_control_tool(
                action="commit",
                message="Test commit from unit test",
                project_path=str(project_path),
                files=[str(test_file)]
            )
            
            self.assert_test(
                "committed" in str(result).lower() or "hash" in str(result).lower(),
                "Version control commit successful"
            )
            
        except ImportError:
            self.assert_test(False, "Version control tool requires gitpython", "GitPython not available")
        except Exception as e:
            self.assert_test(False, "Version control tool execution", str(e))
        
        # Test with missing required parameters
        try:
            result = await version_control_tool(project_path=str(project_path))
            
            self.assert_test(
                "error" in str(result).lower() and ("action" in str(result) or "message" in str(result)),
                "Version control rejects missing parameters"
            )
            
        except Exception as e:
            self.assert_test(False, "Version control validation", str(e))
    
    @pytest.mark.asyncio
    async def test_backup_project_tool(self):
        """Test project backup tool"""
        print("  📦 Testing backup_project_tool...")
        
        project_path = self.create_temp_dir("backup_project")
        backup_path = self.create_temp_dir("backup_destination")
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create some project content
        (project_path / "data").mkdir()
        (project_path / "data" / "test.txt").write_text("Test data")
        
        try:
            result = await backup_project_tool(
                project_path=str(project_path),
                backup_location=str(backup_path)
            )
            
            self.assert_test(
                "backed up" in str(result).lower() or "backup" in str(result).lower(),
                "Project backup tool execution"
            )
            
        except Exception as e:
            self.assert_test(False, "Backup project tool execution", str(e))

class TestStorageComponents:
    """Test core storage components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_temp_dir(self, name: str) -> Path:
        """Create a temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"storage_comp_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    def test_project_manager_initialization(self):
        """Test ProjectManager initialization"""
        print("  🏗️  Testing ProjectManager initialization...")
        
        project_path = self.create_temp_dir("project_manager")
        
        try:
            project_manager = ProjectManager(str(project_path))
            
            self.assert_test(
                hasattr(project_manager, 'project_path'),
                "ProjectManager has project_path attribute"
            )
            
            self.assert_test(
                hasattr(project_manager, 'git_manager'),
                "ProjectManager has git_manager"
            )
            
            self.assert_test(
                hasattr(project_manager, 'sqlite_manager'),
                "ProjectManager has sqlite_manager"
            )
            
            self.assert_test(
                hasattr(project_manager, 'vector_manager'),
                "ProjectManager has vector_manager"
            )
            
        except Exception as e:
            self.assert_test(False, "ProjectManager initialization", str(e))

async def main():
    """Main test function"""
    print("🧪 STORAGE MANAGEMENT UNIT TESTS")
    print("=" * 50)
    
    # Test storage tools
    print("🛠️  Storage Tools Tests")
    tools_tests = TestStorageTools()
    
    try:
        await tools_tests.test_initialize_project_tool()
        await tools_tests.test_save_session_tool()
        await tools_tests.test_search_knowledge_tool()
        await tools_tests.test_version_control_tool()
        await tools_tests.test_backup_project_tool()
    finally:
        tools_tests.cleanup()
    
    print()
    
    # Test storage components
    print("🔧 Storage Components Tests")
    components_tests = TestStorageComponents()
    
    try:
        components_tests.test_project_manager_initialization()
    finally:
        components_tests.cleanup()
    
    # Summary
    total_passed = tools_tests.test_passed + components_tests.test_passed
    total_failed = tools_tests.test_failed + components_tests.test_failed
    total_tests = total_passed + total_failed
    
    print()
    print("=" * 50)
    print("📊 STORAGE MANAGEMENT TESTS SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    if total_failed > 0:
        print("\n⚠️  Some tests failed - check implementation")
        sys.exit(1)
    else:
        print("\n🎉 All storage management tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
