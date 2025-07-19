#!/usr/bin/env python3
"""
Unit Tests for Context-Aware System
===================================

Tests the context detection and decorator system that enables
automatic project_path injection for all 38 MCP tools.
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
    from utils.context_detector import ContextDetector, get_context_detector
    from utils.context_decorator import context_aware, ContextAwareError
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Make sure MCP server modules are available")
    sys.exit(1)

class TestContextDetection:
    """Test context detection functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_test_project(self, name: str) -> Path:
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_test_{name}_")
        project_path = Path(temp_dir)
        self.temp_dirs.append(project_path)
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config file
        config = {
            "name": f"Test Project {name}",
            "description": f"Test project for context detection - {name}",
            "domain": "software_testing",
            "version": "1.0.0"
        }
        
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return project_path
    
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
    
    def test_environment_detection(self):
        """Test detection from environment variables"""
        print("  🔍 Testing environment variable detection...")
        
        # Create test project
        project_path = self.create_test_project("env_test")
        
        # Test with environment variable
        with patch.dict(os.environ, {'SRRD_PROJECT_PATH': str(project_path)}):
            detector = ContextDetector()
            context = detector.detect_context(refresh_cache=True)
            
            self.assert_test(
                context is not None, 
                "Environment detection returns context"
            )
            
            if context:
                self.assert_test(
                    context['project_path'] == str(project_path),
                    "Correct project path detected",
                    f"Expected {project_path}, got {context.get('project_path')}"
                )
                
                self.assert_test(
                    'config' in context,
                    "Config loaded from detected project"
                )
    
    def test_directory_traversal_detection(self):
        """Test detection by directory traversal"""
        print("  🔍 Testing directory traversal detection...")
        
        # Create test project
        project_path = self.create_test_project("traversal_test")
        
        # Create subdirectory and test from there
        sub_dir = project_path / "data" / "raw"
        sub_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock os.getcwd to return the subdirectory
        with patch('os.getcwd', return_value=str(sub_dir)):
            detector = ContextDetector()
            context = detector.detect_context(refresh_cache=True)
            
            self.assert_test(
                context is not None,
                "Directory traversal detection finds project"
            )
            
            if context:
                self.assert_test(
                    context['project_path'] == str(project_path),
                    "Correct parent project path found"
                )
    
    def test_no_context_available(self):
        """Test behavior when no context is available"""
        print("  🔍 Testing no context scenario...")
        
        # Clear environment and mock getcwd to non-SRRD directory
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.getcwd', return_value='/tmp'):
                detector = ContextDetector()
                context = detector.detect_context(refresh_cache=True)
                
                self.assert_test(
                    context is None,
                    "No context returned when not in SRRD project"
                )
    
    def test_context_caching(self):
        """Test context caching behavior"""
        print("  🔍 Testing context caching...")
        
        project_path = self.create_test_project("cache_test")
        
        with patch.dict(os.environ, {'SRRD_PROJECT_PATH': str(project_path)}):
            detector = ContextDetector()
            
            # First call
            context1 = detector.detect_context()
            # Second call (should use cache)
            context2 = detector.detect_context()
            
            self.assert_test(
                context1 == context2,
                "Cached context matches original"
            )
            
            # Force refresh
            context3 = detector.detect_context(refresh_cache=True)
            
            self.assert_test(
                context1 == context3,
                "Refreshed context matches original"
            )

class TestContextDecorator:
    """Test context-aware decorator functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_test_project(self, name: str) -> Path:
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_decorator_test_{name}_")
        project_path = Path(temp_dir)
        self.temp_dirs.append(project_path)
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config file
        config = {
            "name": f"Decorator Test Project {name}",
            "description": f"Test project for decorator testing - {name}",
            "domain": "software_testing"
        }
        
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return project_path
    
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
    async def test_automatic_injection(self):
        """Test automatic project_path injection"""
        print("  🎯 Testing automatic project_path injection...")
        
        project_path = self.create_test_project("injection_test")
        
        @context_aware()
        async def test_tool(**kwargs):
            return kwargs.get('project_path')
        
        # Test with context available
        with patch.dict(os.environ, {'SRRD_PROJECT_PATH': str(project_path)}):
            # Clear cache first
            detector = get_context_detector()
            detector._cache_valid = False
            
            result = await test_tool()
            
            self.assert_test(
                result == str(project_path),
                "Project path automatically injected",
                f"Expected {project_path}, got {result}"
            )
    
    @pytest.mark.asyncio
    async def test_explicit_parameter_priority(self):
        """Test that explicit parameters override auto-injection"""
        print("  🎯 Testing explicit parameter priority...")
        
        project_path1 = self.create_test_project("explicit_test1")
        project_path2 = self.create_test_project("explicit_test2")
        
        @context_aware()
        async def test_tool(**kwargs):
            return kwargs.get('project_path')
        
        # Test with context available but explicit parameter provided
        with patch.dict(os.environ, {'SRRD_PROJECT_PATH': str(project_path1)}):
            # Clear cache first
            detector = get_context_detector()
            detector._cache_valid = False
            
            result = await test_tool(project_path=str(project_path2))
            
            self.assert_test(
                result == str(project_path2),
                "Explicit parameter overrides auto-injection",
                f"Expected {project_path2}, got {result}"
            )
    
    @pytest.mark.asyncio
    async def test_optional_context(self):
        """Test optional context behavior"""
        print("  🎯 Testing optional context behavior...")
        
        @context_aware()
        async def test_tool(**kwargs):
            return kwargs.get('project_path', 'NO_PROJECT')
        
        # Test without context
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.getcwd', return_value='/tmp'):
                # Clear cache first
                detector = get_context_detector()
                detector._cache_valid = False
                
                result = await test_tool()
                
                self.assert_test(
                    result == 'NO_PROJECT',
                    "Tool runs without context (optional mode)"
                )
    
    @pytest.mark.asyncio
    async def test_required_context(self):
        """Test required context behavior"""
        print("  🎯 Testing required context behavior...")
        
        @context_aware(require_context=True)
        async def test_tool(**kwargs):
            return "SUCCESS"
        
        # Test without context - should raise error
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.getcwd', return_value='/tmp'):
                # Clear cache first
                detector = get_context_detector()
                detector._cache_valid = False
                
                try:
                    result = await test_tool()
                    self.assert_test(
                        False,
                        "Required context raises error when unavailable"
                    )
                except ContextAwareError:
                    self.assert_test(
                        True,
                        "Required context raises ContextAwareError when unavailable"
                    )
                except Exception as e:
                    self.assert_test(
                        False,
                        f"Required context raises wrong exception: {e}"
                    )

async def main():
    """Main test function"""
    print("🧪 CONTEXT-AWARE SYSTEM UNIT TESTS")
    print("=" * 50)
    
    # Test context detection
    print("📍 Context Detection Tests")
    detection_tests = TestContextDetection()
    
    try:
        detection_tests.test_environment_detection()
        detection_tests.test_directory_traversal_detection()
        detection_tests.test_no_context_available()
        detection_tests.test_context_caching()
    finally:
        detection_tests.cleanup()
    
    print()
    
    # Test context decorator
    print("🎯 Context Decorator Tests")
    decorator_tests = TestContextDecorator()
    
    try:
        await decorator_tests.test_automatic_injection()
        await decorator_tests.test_explicit_parameter_priority()
        await decorator_tests.test_optional_context()
        await decorator_tests.test_required_context()
    finally:
        decorator_tests.cleanup()
    
    # Summary
    total_passed = detection_tests.test_passed + decorator_tests.test_passed
    total_failed = detection_tests.test_failed + decorator_tests.test_failed
    total_tests = total_passed + total_failed
    
    print()
    print("=" * 50)
    print("📊 CONTEXT-AWARE TESTS SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    if total_failed > 0:
        print("\n⚠️  Some tests failed - check implementation")
        sys.exit(1)
    else:
        print("\n🎉 All context-aware system tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
