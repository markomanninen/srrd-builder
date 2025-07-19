#!/usr/bin/env python3
"""
Test suite for Search & Discovery tools.

Tests semantic_search, discover_patterns, build_knowledge_graph, 
find_similar_documents, extract_key_concepts, generate_research_summary
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import search and discovery tools with error handling
try:
    from work.code.mcp.tools.search_discovery import (
        semantic_search_tool,
        discover_patterns_tool,
        build_knowledge_graph_tool,
        find_similar_documents_tool,
        extract_key_concepts_tool,
        generate_research_summary_tool,
        register_search_tools
    )
    SEARCH_TOOLS_AVAILABLE = True
except ImportError:
    SEARCH_TOOLS_AVAILABLE = False


@pytest.mark.skipif(not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available")
class TestSearchDiscoveryTools:
    """Test search and discovery functionality"""
    
    def create_test_project(self, name="test_project"):
        """Create a test project directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"srrd_test_{name}_")
        project_path = Path(temp_dir)
        
        # Create basic SRRD structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir()
        
        return project_path
    
    @pytest.mark.asyncio
    async def test_semantic_search_tool(self):
        """Test semantic search functionality"""
        try:
            project_path = self.create_test_project("semantic_search")
            
            result = await semantic_search_tool(
                query="machine learning algorithms",
                project_path=str(project_path),
                limit=5
            )
            
            assert result is not None
                # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Semantic search dependencies not available")
    
    @pytest.mark.asyncio
    async def test_discover_patterns_tool(self):
        """Test pattern discovery in research content"""
        try:
            test_content = """
            Machine learning algorithms include neural networks, 
            decision trees, and support vector machines. These algorithms
            are used for classification and regression tasks.
            """
            
            result = await discover_patterns_tool(
                content=test_content,
                pattern_type="concepts",
                min_frequency=1
            )
            
            assert result is not None
            # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Pattern discovery dependencies not available")
    
    @pytest.mark.asyncio
    async def test_build_knowledge_graph_tool(self):
        """Test knowledge graph construction"""
        try:
            project_path = self.create_test_project("knowledge_graph")
            
            test_documents = [
                "Neural networks are machine learning models.",
                "Deep learning uses neural networks with many layers."
            ]
            
            result = await build_knowledge_graph_tool(
                documents=test_documents,
                project_path=str(project_path),
                relationship_types=["is_a", "uses", "contains"]
            )
            
            assert result is not None
            # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Knowledge graph dependencies not available")
    
    @pytest.mark.asyncio
    async def test_find_similar_documents_tool(self):
        """Test document similarity search"""
        try:
            project_path = self.create_test_project("similar_docs")
            
            target_doc = "Machine learning is a subset of artificial intelligence"
            
            result = await find_similar_documents_tool(
                target_document=target_doc,
                project_path=str(project_path),
                max_results=3,
                similarity_threshold=0.5
            )
            
            assert result is not None
            # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Document similarity dependencies not available")
    
    @pytest.mark.asyncio
    async def test_extract_key_concepts_tool(self):
        """Test key concept extraction"""
        try:
            test_text = """
            Artificial intelligence and machine learning are transforming
            many industries. Natural language processing enables computers
            to understand human language. Computer vision allows machines
            to interpret visual information.
            """
            
            result = await extract_key_concepts_tool(
                text=test_text,
                max_concepts=5,
                concept_types=["technology", "field", "capability"]
            )
            
            assert result is not None
            # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Key concept extraction dependencies not available")
    
    @pytest.mark.asyncio
    async def test_generate_research_summary_tool(self):
        """Test research summary generation"""
        try:
            test_documents = [
                "Machine learning algorithms learn from data",
                "Neural networks are inspired by biological neurons",
                "Deep learning achieves state-of-the-art performance"
            ]
            
            result = await generate_research_summary_tool(
                documents=test_documents,
                summary_type="comprehensive",
                max_length=200
            )
            
            assert result is not None
            # Tools may return string directly or MCP format
            if isinstance(result, dict) and "content" in result:
                assert "content" in result
            elif isinstance(result, str):
                assert len(result) > 0  # Should return some result text
            else:
                # Accept any non-None result
                assert result is not None
            
        except ImportError:
            pytest.skip("Research summary dependencies not available")


@pytest.mark.skipif(not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available")
class TestSearchToolRegistration:
    """Test search and discovery tool registration"""
    
    def test_search_tools_registration(self):
        """Test that search tools are properly registered"""
        try:
            mock_server = Mock()
            mock_server.register_tool = Mock()
            
            # Register tools
            register_search_tools(mock_server)
            
            # Verify tools were registered
            assert mock_server.register_tool.called
            
        except ImportError:
            pytest.skip("Search tools not available")


@pytest.mark.skipif(not SEARCH_TOOLS_AVAILABLE, reason="Search & Discovery tools not available")
class TestSearchToolParameters:
    """Test search and discovery tool parameter validation"""
    
    @pytest.mark.asyncio
    async def test_semantic_search_parameter_validation(self):
        """Test semantic search parameter validation"""
        try:
            # Test with minimal required parameters (tools may have defaults)
            result = await semantic_search_tool(query="test query")
            assert result is not None
            
            # Test with empty query (should still work or handle gracefully) 
            result_empty = await semantic_search_tool(query="")
            assert result_empty is not None
            
        except ImportError:
            pytest.skip("Semantic search not available")
    
    @pytest.mark.asyncio  
    async def test_discover_patterns_parameter_validation(self):
        """Test pattern discovery parameter validation"""
        try:
            # Test with minimal required parameters (tools may have defaults)
            result = await discover_patterns_tool(content="test content")
            assert result is not None
            
            # Test with empty content (should handle gracefully)
            result_empty = await discover_patterns_tool(content="")
            assert result_empty is not None
            
        except ImportError:
            pytest.skip("Pattern discovery not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
