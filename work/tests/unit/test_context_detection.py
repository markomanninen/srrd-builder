#!/usr/bin/env python3
"""
Unit tests for context detection functionality
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code" / "mcp"))
try:
    # Use a patchable path for get_current_project
    from utils import context_detector
    from utils.context_detector import (
        ContextDetector,
        detect_project_context,
        get_context_detector,
    )
except ImportError:
    # Handle import errors gracefully during testing
    context_detector = None
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
        assert hasattr(self.detector, "_cached_context")
        assert hasattr(self.detector, "_cache_valid")

    @patch("utils.context_detector.get_current_project", return_value=None)
    def test_detect_context_no_environment(self, mock_get_project):
        """Test context detection with no environment variables"""
        # Also patch cwd to a directory without a project
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("os.getcwd", return_value=temp_dir):
                context = self.detector.detect_context()
                assert context is None

    @patch("utils.context_detector.get_current_project")
    def test_detect_context_with_environment(self, mock_get_project):
        """Test context detection with environment variables"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            srrd_dir = temp_path / ".srrd"
            srrd_dir.mkdir()

            # Create basic project structure to pass validation
            (temp_path / "work").mkdir()
            (temp_path / "data").mkdir()

            # Create config file
            config_file = srrd_dir / "config.json"
            config_data = {
                "name": "Test Project",
                "description": "Test project",
                "domain": "testing",
            }
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # Mock get_current_project to return our test path
            mock_get_project.return_value = str(temp_path)

            # Also mock the env var for config path as it's read separately
            with patch.dict(os.environ, {"SRRD_CONFIG_PATH": str(config_file)}):
                context = self.detector.detect_context()

                assert context is not None
                assert context["project_path"] == str(temp_path)
                assert context["method"] == "environment"
                assert context["validated"] is True
                assert "config" in context

    def test_validate_project_structure(self):
        """Test project structure validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Invalid project (no .srrd directory)
            assert not self.detector._validate_project_structure(temp_path)

            # Create .srrd directory but missing work/data
            srrd_dir = temp_path / ".srrd"
            srrd_dir.mkdir()
            # The validation logic is now more flexible and doesn't strictly require these.
            # It just logs a debug message. So this should pass.
            assert self.detector._validate_project_structure(temp_path)

            # Create the rest of the structure
            (temp_path / "work").mkdir()
            (temp_path / "data").mkdir()
            assert self.detector._validate_project_structure(temp_path)

    @patch("utils.context_detector.get_current_project", return_value=None)
    def test_directory_traversal_detection(self, mock_get_project):
        """Test context detection via directory traversal"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create project structure that passes validation
            srrd_dir = temp_path / ".srrd"
            srrd_dir.mkdir()
            (temp_path / "work").mkdir()
            (temp_path / "data").mkdir()

            # Create subdirectory to test traversal
            sub_dir = temp_path / "subdir" / "deeper"
            sub_dir.mkdir(parents=True)

            # Change to subdirectory and test detection
            original_cwd = os.getcwd()
            try:
                os.chdir(sub_dir)

                # Mock environment to be empty (already done by patch)
                context = self.detector.detect_context()

                assert context is not None
                # Handle symlink resolution differences
                assert Path(context["project_path"]).resolve() == temp_path.resolve()
                assert context["method"] == "directory_traversal"

            finally:
                os.chdir(original_cwd)

    def test_context_caching(self):
        """Test context caching functionality"""
        # First call should detect and cache
        with patch(
            "utils.context_detector.ContextDetector._detect_from_directory"
        ) as mock_detect:
            mock_detect.return_value = {
                "project_path": "/fake/path",
                "method": "directory_traversal",
            }

            context1 = self.detector.detect_context()
            assert mock_detect.call_count == 1

            # Second call should use cache
            context2 = self.detector.detect_context()
            assert mock_detect.call_count == 1
            assert context1 == context2

            # Force refresh should re-detect
            context3 = self.detector.detect_context(refresh_cache=True)
            assert mock_detect.call_count == 2
            # Should be same result but freshly detected
            assert context3 == context1

    def test_get_convenience_functions(self):
        """Test convenience functions"""
        with patch.object(
            self.detector,
            "detect_context",
            return_value={
                "project_path": "/fake/path",
                "config_path": "/fake/path/config.json",
                "config": {"name": "fake"},
            },
        ):
            project_path = self.detector.get_project_path()
            config_path = self.detector.get_config_path()
            config = self.detector.get_config()
            is_available = self.detector.is_context_available()

            assert project_path == "/fake/path"
            assert config_path == "/fake/path/config.json"
            assert config["name"] == "fake"
            assert is_available is True


@pytest.mark.skipif(
    get_context_detector is None, reason="Context detector not available"
)
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
            with patch("utils.context_detector.get_context_detector") as mock_get:
                mock_detector = Mock()
                mock_get.return_value = mock_detector
                mock_detector.detect_context.return_value = {
                    "project_path": "/fake/path"
                }

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

    @pytest.mark.skipif(
        ContextDetector is None, reason="Context detector not available"
    )
    @patch(
        "utils.context_detector.get_current_project",
        return_value="/nonexistent/path/that/should/not/exist",
    )
    def test_nonexistent_environment_path(self, mock_get_project):
        """Test handling of nonexistent environment path"""
        # With an invalid configured path and no fallback project in cwd,
        # context detection should fail and return None.
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("os.getcwd", return_value=temp_dir):
                context = self.detector.detect_context()
                assert context is None

    @pytest.mark.skipif(
        ContextDetector is None, reason="Context detector not available"
    )
    @patch("utils.context_detector.get_current_project")
    def test_invalid_config_file(self, mock_get_project):
        """Test handling of invalid config file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            srrd_dir = temp_path / ".srrd"
            srrd_dir.mkdir()
            (temp_path / "work").mkdir()  # for validation
            (temp_path / "data").mkdir()  # for validation

            # Create invalid JSON config file
            config_file = srrd_dir / "config.json"
            with open(config_file, "w") as f:
                f.write("invalid json content {")

            # Mock get_current_project to return this path
            mock_get_project.return_value = str(temp_path)

            with patch.dict(os.environ, {"SRRD_CONFIG_PATH": str(config_file)}):
                context = self.detector.detect_context()

                # Should detect project but not load config
                assert context is not None
                assert context["project_path"] == str(temp_path)
                assert "config" not in context or context["config"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
