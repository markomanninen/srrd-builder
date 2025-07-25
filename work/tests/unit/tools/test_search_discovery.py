import sys
from pathlib import Path

# FILE: work/code/mcp/tools/search_discovery.py
project_root = Path(__file__).resolve().parent.parent.parent.parent
mcp_code_path = project_root / "work" / "code" / "mcp"
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(mcp_code_path) not in sys.path:
    sys.path.insert(0, str(mcp_code_path))

import tempfile
from unittest.mock import Mock

import pytest

try:
    import work.code.mcp.utils.current_project as current_project_module
    from work.code.mcp.storage.project_manager import ProjectManager
    from work.code.mcp.tools.search_discovery import (
        build_knowledge_graph_tool as build_knowledge_graph_tool_func,
    )
    from work.code.mcp.tools.search_discovery import (
        discover_patterns_tool as discover_patterns_tool_func,
    )
    from work.code.mcp.tools.search_discovery import (
        extract_key_concepts_tool as extract_key_concepts_tool_func,
    )
    from work.code.mcp.tools.search_discovery import (
        find_similar_documents_tool as find_similar_documents_tool_func,
    )
    from work.code.mcp.tools.search_discovery import (
        generate_research_summary_tool as generate_research_summary_tool_func,
    )
    from work.code.mcp.tools.search_discovery import register_search_tools
    from work.code.mcp.tools.search_discovery import (
        semantic_search_tool as semantic_search_tool_func,
    )

    SEARCH_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"FATAL: Import failed: {e}", file=sys.stderr)
    SEARCH_TOOLS_AVAILABLE = False


@pytest.fixture
async def initialized_project():
    """
    Provides a fully initialized SRRD project and sets it as the active context for the test.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        (project_path / ".srrd" / "data").mkdir(parents=True)
        (project_path / ".srrd" / "config.json").write_text('{"name": "test"}')
        (project_path / "work").mkdir()
        (project_path / "data").mkdir()

        pm = ProjectManager(str(project_path))
        await pm.sqlite_manager.initialize_database()
        await pm.vector_manager.initialize(enable_embedding_model=False)

        # Store original project to restore it later
        original_project = current_project_module.get_current_project()
        try:
            # Set the current project context for the duration of the test
            current_project_module.set_current_project(str(project_path))
            yield project_path
        finally:
            # Restore original context after the test
            if original_project:
                current_project_module.set_current_project(original_project)
            else:
                current_project_module.clear_current_project()


@pytest.mark.skipif(
    not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available"
)
@pytest.mark.usefixtures("initialized_project")
class TestSearchDiscoveryTools:
    """Test search and discovery functionality"""

    @pytest.mark.asyncio
    async def test_semantic_search_tool(self):
        kwargs = {
            "query": "machine learning algorithms",
            "collection": "research_literature",
        }
        result = await semantic_search_tool_func(**kwargs)
        assert "semantic search results" in result.lower()

    @pytest.mark.asyncio
    async def test_discover_patterns_tool(self):
        kwargs = {"content": "Machine learning algorithms include neural networks."}
        result = await discover_patterns_tool_func(**kwargs)
        assert "discovered patterns" in result.lower()

    @pytest.mark.asyncio
    async def test_build_knowledge_graph_tool(self):
        kwargs = {"documents": ["Neural networks are models."]}
        result = await build_knowledge_graph_tool_func(**kwargs)
        assert "knowledge graph built" in result.lower()

    @pytest.mark.asyncio
    async def test_find_similar_documents_tool(self):
        kwargs = {"target_document": "Machine learning is a subset of AI"}
        result = await find_similar_documents_tool_func(**kwargs)
        assert "similar documents found" in result.lower()

    @pytest.mark.asyncio
    async def test_extract_key_concepts_tool(self):
        kwargs = {
            "text": "Artificial intelligence and machine learning are transforming industries."
        }
        result = await extract_key_concepts_tool_func(**kwargs)
        assert "extracted key concepts" in result.lower()

    @pytest.mark.asyncio
    async def test_generate_research_summary_tool(self):
        kwargs = {"documents": ["Machine learning algorithms learn from data."]}
        result = await generate_research_summary_tool_func(**kwargs)
        assert "research summary" in result.lower()


@pytest.mark.skipif(
    not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available"
)
class TestSearchToolRegistration:
    """Test search and discovery tool registration"""

    def test_search_tools_registration(self):
        mock_server = Mock()
        mock_server.register_tool = Mock()
        register_search_tools(mock_server)
        assert mock_server.register_tool.called


@pytest.mark.skipif(
    not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available"
)
@pytest.mark.usefixtures("initialized_project")
class TestSearchToolParameters:
    """Test search and discovery tool parameter validation"""

    @pytest.mark.asyncio
    async def test_semantic_search_parameter_validation(self):
        result = await semantic_search_tool_func(query="test query")
        assert "semantic search results" in result.lower()
        with pytest.raises(TypeError):
            await semantic_search_tool_func()

    @pytest.mark.asyncio
    async def test_discover_patterns_parameter_validation(self):
        result = await discover_patterns_tool_func(content="test content")
        assert "discovered patterns" in result.lower()
        with pytest.raises(TypeError):
            await discover_patterns_tool_func()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
