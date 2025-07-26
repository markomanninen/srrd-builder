import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add MCP directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "code" / "mcp"))

# Mock the dependencies before importing the tools
sys.modules["chromadb"] = MagicMock()

from tools.document_generation import register_document_tools, compile_latex_tool
from tools.vector_database import (
    register_vector_database_tools,
    retrieve_bibliography_references_tool,
    store_bibliography_reference_tool,
)
from mcp_server import ClaudeMCPServer


@pytest.fixture
def mcp_server():
    # Reset the tools dictionary for each test
    server = ClaudeMCPServer()
    server.tools = {}
    return server


def test_latex_tool_registration(mcp_server):
    """Test that latex tools are registered only when the env var is set."""
    with patch.dict(os.environ, {"SRRD_LATEX_INSTALLED": "true"}):
        register_document_tools(mcp_server)
        assert "compile_latex" in mcp_server.tools

    mcp_server.tools = {}  # Reset tools
    with patch.dict(os.environ, {"SRRD_LATEX_INSTALLED": "false"}):
        register_document_tools(mcp_server)
        assert "compile_latex" not in mcp_server.tools


def test_vector_db_tool_registration(mcp_server):
    """Test that vector db tools are registered only when the env var is set."""
    with patch.dict(os.environ, {"SRRD_VECTOR_DB_INSTALLED": "true"}):
        register_vector_database_tools(mcp_server)
        assert "store_bibliography_reference" in mcp_server.tools
        assert "retrieve_bibliography_references" in mcp_server.tools

    mcp_server.tools = {}  # Reset tools
    with patch.dict(os.environ, {"SRRD_VECTOR_DB_INSTALLED": "false"}):
        register_vector_database_tools(mcp_server)
        assert "store_bibliography_reference" not in mcp_server.tools
        assert "retrieve_bibliography_references" not in mcp_server.tools


@pytest.mark.asyncio
async def test_latex_tool_without_env_var():
    """Test that the latex tool returns a message when the env var is not set."""
    with patch.dict(os.environ, {"SRRD_LATEX_INSTALLED": "false"}):
        result = await compile_latex_tool(tex_file_path="dummy.tex")
        assert "not installed" in result.lower()


@pytest.mark.asyncio
async def test_vector_db_tools_without_env_var():
    """Test that vector db tools return a message when the env var is not set."""
    with patch.dict(os.environ, {"SRRD_VECTOR_DB_INSTALLED": "false"}):
        with patch("tools.vector_database.VECTOR_DB_AVAILABLE", False):
            result = await store_bibliography_reference_tool(reference={})
            assert "not available" in result.lower()

            result = await retrieve_bibliography_references_tool(query="test")
            assert "not available" in result.lower()
