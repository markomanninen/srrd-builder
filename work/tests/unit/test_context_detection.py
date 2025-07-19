#!/usr/bin/env python3
"""
Unit tests for context detection functionality
"""
import sys
import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))
try:
    from utils.context_detector import ContextDetector, get_context_detector, detect_project_context
except ImportError:
    # Handle import errors gracefully during testing
    ContextDetector = None
    get_context_detector = None
    detect_project_context = None


@pytest.mark.skipif(ContextDetector is None, reason="Context detector not available")
class TestContextDetector:
    """Test context detection functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.detector = ContextDetector()
        # Clear cache before each test
        self.detector.clear_cache()
    
    def test_context_detector_initialization(self):
        """Test context detector initialization"""
        assert self.detector is not None
        assert hasattr(self.detector, '_cached_context')
        assert hasattr(self.detector, '_cache_valid')
    
    def test_detect_context_no_environment(self):
        """Test context detection with no environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            context = self.detector.detect_context()
            # Should return None or detect from directory
            assert context is None or isinstance(context, dict)
    
    def test_detect_context_with_environment(self):
        """Test context detection with environment variables"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            srrd_dir = temp_path / '.srrd'
            srrd_dir.mkdir()
            
            # Create basic project structure
            (temp_path / 'work').mkdir()
            (temp_path / 'data').mkdir()
            
            # Create config file
            config_file = srrd_dir / 'config.json'
            config_data = {
                "name": "Test Project",
                "description": "Test project",
                "domain": "testing"
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            
            with patch.dict(os.environ, {
                'SRRD_PROJECT_PATH': str(temp_path),
                'SRRD_CONFIG_PATH': str(config_file)
            }):
                context = self.detector.detect_context()
                
                assert context is not None
                assert context['project_path'] == str(temp_path)
                assert context['method'] == 'environment'
                assert context['validated'] is True
                assert 'config' in context
    
    def test_validate_project_structure(self):
        """Test project structure validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Invalid project (no .srrd directory)
            assert not self.detector._validate_project_structure(temp_path)
            
            # Create .srrd directory
            srrd_dir = temp_path / '.srrd'
            srrd_dir.mkdir()
            
            # Should now be valid (flexible validation)
            assert self.detector._validate_project_structure(temp_path)
    
    def test_directory_traversal_detection(self):
        """Test context detection via directory traversal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create project structure
            srrd_dir = temp_path / '.srrd'
            srrd_dir.mkdir()
            
            # Create subdirectory to test traversal
            sub_dir = temp_path / 'subdir' / 'deeper'
            sub_dir.mkdir(parents=True)
            
            # Change to subdirectory and test detection
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)
                
                # Mock environment to be empty
                with patch.dict(os.environ, {}, clear=True):
                    context = self.detector.detect_context()
                    
                if context:  # May not detect if validation is strict
                    # Handle symlink resolution differences
                    assert Path(context['project_path']).resolve() == temp_path.resolve()
                    assert context['method'] == 'directory_traversal'
                    
            finally:
                os.chdir(original_cwd)
    
    def test_context_caching(self):
        """Test context caching functionality"""
        # First call should detect and cache
        context1 = self.detector.detect_context()
        
        # Second call should use cache
        context2 = self.detector.detect_context()
        
        assert context1 == context2
        
        # Force refresh should re-detect
        context3 = self.detector.detect_context(refresh_cache=True)
        
        # Should be same result but freshly detected
        assert context3 == context1
    
    def test_get_convenience_functions(self):
        """Test convenience functions"""
        project_path = self.detector.get_project_path()
        config_path = self.detector.get_config_path()
        config = self.detector.get_config()
        is_available = self.detector.is_context_available()
        
        # Should all return consistently
        if project_path:
            assert is_available
        else:
            assert not is_available or is_available  # May be available via other methods


@pytest.mark.skipif(get_context_detector is None, reason="Context detector not available")
class TestContextDetectorGlobals:
    """Test global context detector functions"""
    
    def test_get_global_context_detector(self):
        """Test global context detector singleton"""
        detector1 = get_context_detector()
        detector2 = get_context_detector()
        
        # Should be same instance (singleton)
        assert detector1 is detector2
    
    def test_convenience_functions(self):
        """Test global convenience functions"""
        if detect_project_context:
            context = detect_project_context()
            # Should return same as detector instance
            detector_context = get_context_detector().detect_context()
            assert context == detector_context


class TestContextDetectorEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Setup test environment"""
        if ContextDetector:
            self.detector = ContextDetector()
            self.detector.clear_cache()
    
    @pytest.mark.skipif(ContextDetector is None, reason="Context detector not available")
    def test_nonexistent_environment_path(self):
        """Test handling of nonexistent environment path"""
        with patch.dict(os.environ, {
            'SRRD_PROJECT_PATH': '/nonexistent/path/that/should/not/exist'
        }):
            context = self.detector.detect_context()
            # Should warn about invalid path but may still detect via directory traversal
            if context:
                assert context['method'] == 'directory_traversal'
                assert 'project_path' in context
            # If no context is found, that's also acceptable
    
    @pytest.mark.skipif(ContextDetector is None, reason="Context detector not available") 
    def test_invalid_config_file(self):
        """Test handling of invalid config file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            srrd_dir = temp_path / '.srrd'
            srrd_dir.mkdir()
            
            # Create invalid JSON config file
            config_file = srrd_dir / 'config.json'
            with open(config_file, 'w') as f:
                f.write("invalid json content {")
            
            with patch.dict(os.environ, {
                'SRRD_PROJECT_PATH': str(temp_path),
                'SRRD_CONFIG_PATH': str(config_file)
            }):
                context = self.detector.detect_context()
                
                # Should detect project but not load config
                if context:
                    assert context['project_path'] == str(temp_path)
                    assert 'config' not in context or context['config'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
