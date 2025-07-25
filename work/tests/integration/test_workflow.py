#!/usr/bin/env python3
"""
Integration tests for context-aware workflow functionality
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from work.code.mcp.storage.project_manager import ProjectManager
from work.code.mcp.utils.current_project import (
    clear_current_project,
    set_current_project,
)


@pytest.fixture
def active_project_context():
    """
    Creates a temporary project, fully initializes its databases, and sets
    it as the active context for the duration of a test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        (project_path / ".srrd" / "data").mkdir(parents=True, exist_ok=True)
        (project_path / ".srrd" / "config.json").write_text('{"name": "test_project"}')
        (project_path / "work").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)

        async def init_databases():
            pm = ProjectManager(str(project_path))
            await pm.sqlite_manager.initialize_database()
            await pm.vector_manager.initialize()

        asyncio.run(init_databases())

        try:
            set_current_project(str(project_path))
            yield project_path
        finally:
            clear_current_project()
            import shutil

            shutil.rmtree(temp_dir)


class TestContextAwareWorkflow:
    """Test context-aware workflow functionality"""

    def create_test_project(self, project_name="test_project"):
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_test_{project_name}_")
        project_path = Path(temp_dir)
        srrd_dir = project_path / ".srrd"
        srrd_dir.mkdir(parents=True, exist_ok=True)
        config = {"name": f"Test Project {project_name}", "domain": "testing"}
        config_file = srrd_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        (project_path / "work").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        return project_path

    def test_context_detection_environment_variables(self, active_project_context):
        from work.code.mcp.utils.context_detector import ContextDetector

        detector = ContextDetector()
        context = detector.detect_context(refresh_cache=True)
        assert context is not None
        assert (
            Path(context["project_path"]).resolve() == active_project_context.resolve()
        )
        assert context["method"] == "environment"

    def test_context_detection_directory_traversal(self):
        from work.code.mcp.utils.context_detector import ContextDetector

        project_path = self.create_test_project("dir_test")
        sub_dir = project_path / "subdir"
        sub_dir.mkdir()
        original_cwd = os.getcwd()
        try:
            os.chdir(sub_dir)
            with patch(
                "work.code.mcp.utils.current_project.get_current_project",
                return_value=None,
            ):
                detector = ContextDetector()
                context = detector.detect_context(refresh_cache=True)
                assert context is not None
                assert Path(context["project_path"]).resolve() == project_path.resolve()
                assert context["method"] == "directory_traversal"
        finally:
            os.chdir(original_cwd)
            import shutil

            shutil.rmtree(project_path)

    @pytest.mark.asyncio
    async def test_context_aware_tool_execution(self, active_project_context):
        from work.code.mcp.server import MCPServer

        server = MCPServer()
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "save_session",
                "arguments": {"session_data": {"test": "data"}},
            },
        }
        response = await server.handle_mcp_request(request)
        assert "error" not in response
        assert (
            "session saved"
            in response.get("result", {})
            .get("content", [{}])[0]
            .get("text", "")
            .lower()
        )

    @pytest.mark.asyncio
    async def test_bibliography_context_aware_workflow(self, active_project_context):
        from work.code.mcp.server import MCPServer

        server = MCPServer()

        store_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "store_bibliography_reference",
                "arguments": {
                    "reference": {
                        "title": "A Test Paper",
                        "authors": "J. Doe",
                        "year": 2024,
                    }
                },
            },
        }
        store_response = await server.handle_mcp_request(store_req)
        assert "error" not in store_response, store_response.get("error", {}).get(
            "message"
        )

        retrieve_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "retrieve_bibliography_references",
                "arguments": {"query": "Test Paper"},
            },
        }
        retrieve_response = await server.handle_mcp_request(retrieve_req)
        assert "error" not in retrieve_response, retrieve_response.get("error", {}).get(
            "message"
        )

    def test_context_aware_fallback_behavior(self):
        from work.code.mcp.utils.context_detector import ContextDetector

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                clear_current_project()
                detector = ContextDetector()
                assert detector.is_context_available() is False
            finally:
                os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_explicit_project_path_override(self, active_project_context):
        from work.code.mcp.server import MCPServer

        project1_path = active_project_context
        project2_path = self.create_test_project("override_attempt_project")

        try:
            server = MCPServer()
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "save_session",
                    "arguments": {
                        "session_data": {"test": "data"},
                        "project_path": str(project2_path),
                    },
                },
            }
            response = await server.handle_mcp_request(request)
            result_text = (
                response.get("result", {}).get("content", [{}])[0].get("text", "")
            )

            assert str(project1_path) in result_text
            assert str(project2_path) not in result_text
        finally:
            import shutil

            shutil.rmtree(project2_path)

    def test_context_caching_behavior(self, monkeypatch):
        from work.code.mcp.utils.context_detector import ContextDetector

        detector = ContextDetector()
        mock_get_project = Mock(return_value=None)
        monkeypatch.setattr(
            "work.code.mcp.utils.context_detector.get_current_project", mock_get_project
        )
        detector.detect_context()
        detector.detect_context()
        mock_get_project.assert_called_once()
        detector.detect_context(refresh_cache=True)
        assert mock_get_project.call_count == 2


class TestContextAwareErrorHandling:
    """Test error handling in context-aware scenarios"""

    @pytest.mark.asyncio
    async def test_context_required_tool_without_context(self):
        from work.code.mcp.server import MCPServer

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                clear_current_project()
                server = MCPServer()
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "save_session",
                        "arguments": {"session_data": {}},
                    },
                }
                response = await server.handle_mcp_request(request)
                assert "error" in response
                assert (
                    "requires srrd project context"
                    in response["error"]["message"].lower()
                )
            finally:
                os.chdir(original_cwd)

    def test_invalid_project_path_in_environment(self):
        from work.code.mcp.utils.context_detector import ContextDetector

        home_dir = Path.home()
        srrd_home = home_dir / ".srrd"
        srrd_home.mkdir(exist_ok=True)
        (srrd_home / "current_project.txt").write_text(
            "/nonexistent/path/that/should/never/exist"
        )

        try:
            with patch.object(
                ContextDetector, "_detect_from_directory", return_value=None
            ):
                detector = ContextDetector()
                context = detector.detect_context(refresh_cache=True)
                assert context is None
        finally:
            clear_current_project()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
