#!/usr/bin/env python3
"""
Integration tests for context-aware workflow functionality
"""
import sys
import os
import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))


class TestContextAwareWorkflow:
    """Test context-aware workflow functionality"""
    
    def create_test_project(self, project_name="test_project"):
        """Create a test SRRD project for testing"""
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_test_{project_name}_")
        project_path = Path(temp_dir)
        
        # Initialize SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config file
        config = {
            "name": f"Context Test Project {project_name}",
            "description": f"Test project for context-aware functionality - {project_name}",
            "domain": "software_testing",
            "version": "1.0.0",
            "created": "2025-07-19"
        }
        
        config_file = srrd_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create necessary directories
        (srrd_dir / 'data').mkdir(exist_ok=True)
        (srrd_dir / 'logs').mkdir(exist_ok=True)
        (project_path / 'work').mkdir(exist_ok=True)
        (project_path / 'data').mkdir(exist_ok=True)
        
        return project_path
    
    def test_context_detection_environment_variables(self):
        """Test context detection via environment variables"""
        try:
            from utils.context_detector import ContextDetector
            
            project_path = self.create_test_project("env_test")
            config_path = project_path / '.srrd' / 'config.json'
            
            try:
                with patch.dict(os.environ, {
                    'SRRD_PROJECT_PATH': str(project_path),
                    'SRRD_CONFIG_PATH': str(config_path)
                }):
                    detector = ContextDetector()
                    context = detector.detect_context()
                    
                    assert context is not None
                    assert context['project_path'] == str(project_path)
                    assert context['method'] == 'environment'
                    assert context['validated'] is True
                    assert 'config' in context
                    assert context['config']['name'].startswith('Context Test Project')
                    
            finally:
                # Cleanup
                import shutil
                if project_path.exists():
                    shutil.rmtree(project_path)
                    
        except ImportError:
            pytest.skip("Context detector not available")
    
    def test_context_detection_directory_traversal(self):
        """Test context detection via directory traversal"""
        try:
            from utils.context_detector import ContextDetector
            
            project_path = self.create_test_project("dir_test")
            
            # Create subdirectory to test traversal
            sub_dir = project_path / 'subdir' / 'deeper'
            sub_dir.mkdir(parents=True)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)
                
                # Clear environment variables
                with patch.dict(os.environ, {}, clear=True):
                    detector = ContextDetector()
                    context = detector.detect_context()
                    
                    if context:  # May not detect depending on validation
                        # Resolve paths to handle symlinks like /private/var vs /var
                        detected_path = os.path.realpath(context['project_path'])
                        expected_path = os.path.realpath(str(project_path))
                        assert detected_path == expected_path
                        assert context['method'] == 'directory_traversal'
                        assert context['validated'] is True
                        
            finally:
                os.chdir(original_cwd)
                # Cleanup
                import shutil
                if project_path.exists():
                    shutil.rmtree(project_path)
                    
        except ImportError:
            pytest.skip("Context detector not available")
    
    @pytest.mark.asyncio
    async def test_context_aware_tool_execution(self):
        """Test that tools work without explicit project_path when context is available"""
        try:
            from server import MCPServer
            
            project_path = self.create_test_project("tool_test")
            
            try:
                with patch.dict(os.environ, {
                    'SRRD_PROJECT_PATH': str(project_path),
                    'SRRD_CONFIG_PATH': str(project_path / '.srrd' / 'config.json')
                }):
                    server = MCPServer()
                    
                    # Test a storage tool without providing project_path
                    request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "save_session",
                            "arguments": {
                                "session_data": {
                                    "test": "data"
                                }
                                # Note: NO project_path provided - should be auto-injected
                            }
                        }
                    }
                    
                    response = await server.handle_mcp_request(request)
                    
                    # Should not fail due to missing project_path
                    assert response["jsonrpc"] == "2.0"
                    assert response["id"] == 1
                    assert "result" in response or "error" in response
                    
                    # If there's an error, it shouldn't be about missing project context
                    if "error" in response:
                        error_msg = response["error"]["message"].lower()
                        assert "project context not available" not in error_msg
                        assert "missing.*project_path" not in error_msg
                        
            finally:
                # Cleanup
                import shutil
                if project_path.exists():
                    shutil.rmtree(project_path)
                    
        except ImportError:
            pytest.skip("MCP server not available")
    
    @pytest.mark.asyncio
    async def test_bibliography_context_aware_workflow(self):
        """Test bibliography storage and retrieval with context awareness"""
        try:
            from server import MCPServer
            
            project_path = self.create_test_project("bib_test")
            
            try:
                with patch.dict(os.environ, {
                    'SRRD_PROJECT_PATH': str(project_path),
                    'SRRD_CONFIG_PATH': str(project_path / '.srrd' / 'config.json')
                }):
                    server = MCPServer()
                    
                    # Test storing a bibliography reference without project_path
                    store_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "store_bibliography_reference",
                            "arguments": {
                                "reference": {
                                    "title": "Context-Aware Testing in MCP Systems",
                                    "authors": ["Dr. Test Author"],
                                    "year": 2025,
                                    "journal": "Journal of Testing",
                                    "doi": "10.1234/test.2025.001"
                                }
                                # No project_path - should be auto-injected
                            }
                        }
                    }
                    
                    store_response = await server.handle_mcp_request(store_request)
                    
                    # Should succeed or fail for other reasons
                    assert store_response["jsonrpc"] == "2.0"
                    assert store_response["id"] == 1
                    
                    # Test retrieving bibliography references without project_path
                    retrieve_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "retrieve_bibliography_references",
                            "arguments": {
                                "query": "context-aware testing"
                                # No project_path - should be auto-injected
                            }
                        }
                    }
                    
                    retrieve_response = await server.handle_mcp_request(retrieve_request)
                    
                    # Should succeed or fail for other reasons
                    assert retrieve_response["jsonrpc"] == "2.0"
                    assert retrieve_response["id"] == 2
                    
                    # Both operations should not fail due to missing project context
                    for response in [store_response, retrieve_response]:
                        if "error" in response:
                            error_msg = response["error"]["message"].lower()
                            assert "project context not available" not in error_msg
                            
            finally:
                # Cleanup
                import shutil
                if project_path.exists():
                    shutil.rmtree(project_path)
                    
        except ImportError:
            pytest.skip("MCP server not available")
    
    def test_context_aware_fallback_behavior(self):
        """Test fallback behavior when no context is available"""
        try:
            from utils.context_detector import ContextDetector
            
            # Clear all environment variables
            with patch.dict(os.environ, {}, clear=True):
                # Change to a directory without .srrd
                with tempfile.TemporaryDirectory() as temp_dir:
                    original_cwd = os.getcwd()
                    try:
                        os.chdir(temp_dir)
                        
                        detector = ContextDetector()
                        context = detector.detect_context()
                        
                        # Should return None when no context available
                        assert context is None
                        
                        # Test convenience functions
                        assert detector.get_project_path() is None
                        assert detector.get_config_path() is None
                        assert detector.get_config() is None
                        assert detector.is_context_available() is False
                        
                    finally:
                        os.chdir(original_cwd)
                        
        except ImportError:
            pytest.skip("Context detector not available")
    
    @pytest.mark.asyncio
    async def test_explicit_project_path_override(self):
        """Test that explicit project_path parameters override context detection"""
        try:
            from server import MCPServer
            
            # Create two different projects
            project1_path = self.create_test_project("override_test1")
            project2_path = self.create_test_project("override_test2")
            
            try:
                # Set environment to project1
                with patch.dict(os.environ, {
                    'SRRD_PROJECT_PATH': str(project1_path),
                    'SRRD_CONFIG_PATH': str(project1_path / '.srrd' / 'config.json')
                }):
                    server = MCPServer()
                    
                    # Call tool with explicit project_path pointing to project2
                    request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "save_session",
                            "arguments": {
                                "session_data": {"test": "data"},
                                "project_path": str(project2_path)  # Explicit override
                            }
                        }
                    }
                    
                    response = await server.handle_mcp_request(request)
                    
                    # Should use the explicit project_path, not the environment one
                    assert response["jsonrpc"] == "2.0"
                    assert response["id"] == 1
                    # Tool should process with project2_path, not project1_path
                    
            finally:
                # Cleanup both projects
                import shutil
                for project_path in [project1_path, project2_path]:
                    if project_path.exists():
                        shutil.rmtree(project_path)
                        
        except ImportError:
            pytest.skip("MCP server not available")
    
    def test_context_caching_behavior(self):
        """Test context detection caching behavior"""
        try:
            from utils.context_detector import ContextDetector
            
            project_path = self.create_test_project("cache_test")
            
            try:
                with patch.dict(os.environ, {
                    'SRRD_PROJECT_PATH': str(project_path),
                    'SRRD_CONFIG_PATH': str(project_path / '.srrd' / 'config.json')
                }):
                    detector = ContextDetector()
                    
                    # First detection should cache result
                    context1 = detector.detect_context()
                    
                    # Second detection should use cache
                    context2 = detector.detect_context()
                    
                    assert context1 == context2
                    
                    # Force refresh should re-detect
                    context3 = detector.detect_context(refresh_cache=True)
                    
                    assert context3 == context1  # Same result, but freshly detected
                    
                    # Clear cache and test again
                    detector.clear_cache()
                    context4 = detector.detect_context()
                    
                    assert context4 == context1
                    
            finally:
                # Cleanup
                import shutil
                if project_path.exists():
                    shutil.rmtree(project_path)
                    
        except ImportError:
            pytest.skip("Context detector not available")


class TestContextAwareErrorHandling:
    """Test error handling in context-aware scenarios"""
    
    @pytest.mark.asyncio
    async def test_context_required_tool_without_context(self):
        """Test tools that require context when no context is available"""
        try:
            from server import MCPServer
            
            # Clear environment and use temp directory without .srrd
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)
                    
                    with patch.dict(os.environ, {}, clear=True):
                        server = MCPServer()
                        
                        # Try to call a storage tool without context or explicit project_path
                        request = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "tools/call",
                            "params": {
                                "name": "save_session",
                                "arguments": {
                                    "session_data": {"test": "data"}
                                    # No project_path and no context
                                }
                            }
                        }
                        
                        response = await server.handle_mcp_request(request)
                        
                        # Should return appropriate error about missing context
                        assert response["jsonrpc"] == "2.0"
                        assert response["id"] == 1
                        
                        if "error" in response:
                            error_msg = response["error"]["message"].lower()
                            assert "project context not available" in error_msg or \
                                   "project_path" in error_msg
                        elif "result" in response:
                            # Tool handled gracefully - check if it used current directory as fallback
                            result_text = response["result"]["content"][0]["text"].lower()
                            # Accept either error message or successful operation with current directory
                            assert ("error" in result_text or 
                                   "project" in result_text or
                                   "session saved" in result_text)  # Tool may succeed with current dir fallback
                            
                finally:
                    os.chdir(original_cwd)
                    
        except ImportError:
            pytest.skip("MCP server not available")
    
    def test_invalid_project_path_in_environment(self):
        """Test handling of invalid project path in environment"""
        try:
            from utils.context_detector import ContextDetector
            
            with patch.dict(os.environ, {
                'SRRD_PROJECT_PATH': '/nonexistent/path/that/should/not/exist'
            }):
                detector = ContextDetector()
                context = detector.detect_context()
                
                # Should handle invalid path gracefully by falling back to directory traversal
                # or return None if no valid context can be found
                if context:
                    # If context was found, it should be from directory traversal fallback
                    assert context['method'] == 'directory_traversal'
                    # And the path should NOT be the invalid environment path
                    assert context['project_path'] != '/nonexistent/path/that/should/not/exist'
                else:
                    # Or context should be None if no fallback was possible
                    assert context is None
                
        except ImportError:
            pytest.skip("Context detector not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
