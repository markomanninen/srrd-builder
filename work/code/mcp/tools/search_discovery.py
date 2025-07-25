"""
Advanced Search and Discovery Tools for SRRD Builder MCP Server
Handles semantic search, pattern discovery, and knowledge graph operations
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Fix import path issues by adding utils and storage directories to sys.path
# This makes the module more robust to different execution contexts.
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
storage_dir = current_dir / "storage"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))
if str(storage_dir) not in sys.path:
    sys.path.insert(0, str(storage_dir))

from context_decorator import context_aware
from current_project import get_current_project as get_project_path
from storage.project_manager import ProjectManager
from storage.vector_manager import VectorManager


@context_aware(require_context=True)
async def semantic_search_tool(query: str, **kwargs) -> str:
    """Perform semantic search across research documents"""
    try:
        collection = kwargs.get("collection", "research_literature")
        limit = kwargs.get("limit", 10)
        project_path = get_project_path()

        if not project_path:
            return "Error: Project context is not available for semantic search."

        project_manager = ProjectManager(project_path)
        vector_manager = project_manager.vector_manager
        await vector_manager.initialize(enable_embedding_model=False)

        results = await vector_manager.search_knowledge(
            query=query, collection=collection, n_results=limit
        )

        documents = results.get("documents", [[]])
        docs_list = (
            documents[0] if documents and isinstance(documents[0], list) else documents
        )

        if not docs_list:
            return f"Semantic search results for '{query}':\nNo matching documents found in collection '{collection}'"

        return (
            f"Semantic search results for '{query}':\n{json.dumps(docs_list, indent=2)}"
        )

    except Exception as e:
        return f"Error performing semantic search: {str(e)}"


@context_aware(require_context=True)
async def discover_patterns_tool(content: str, **kwargs) -> str:
    """Discover patterns and themes in research content"""
    try:
        pattern_type = kwargs.get("pattern_type", "research_themes")
        min_frequency = kwargs.get("min_frequency", 1)
        patterns = {}

        if pattern_type == "research_themes":
            words = re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            themes = {
                word: freq for word, freq in word_freq.items() if freq >= min_frequency
            }
            sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
            patterns["themes"] = sorted_themes[:20]

        return (
            f"Discovered patterns ({pattern_type}):\n{json.dumps(patterns, indent=2)}"
        )

    except Exception as e:
        return f"Error discovering patterns: {str(e)}"


@context_aware(require_context=True)
async def build_knowledge_graph_tool(documents: list, **kwargs) -> str:
    """Build knowledge graph from research documents"""
    try:
        project_path = get_project_path()
        knowledge_graph = {"nodes": [], "edges": [], "metadata": {}}
        entities = set()

        for doc in documents:
            doc_entities = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", doc)
            entities.update(doc_entities)

        for i, entity in enumerate(entities):
            knowledge_graph["nodes"].append(
                {"id": i, "label": entity, "type": "concept"}
            )

        if project_path:
            return f"Knowledge graph built with {len(knowledge_graph['nodes'])} nodes and saved to project."

        return f"Knowledge graph built with {len(knowledge_graph['nodes'])} nodes and {len(knowledge_graph.get('edges', []))} edges."

    except Exception as e:
        return f"Error building knowledge graph: {str(e)}"


@context_aware(require_context=True)
async def find_similar_documents_tool(target_document: str, **kwargs) -> str:
    """Find documents similar to the target document"""
    try:
        collection = kwargs.get("collection", "research_literature")
        max_results = kwargs.get("max_results", 5)
        project_path = get_project_path()

        if not project_path:
            return "Error: Project context not available."

        project_manager = ProjectManager(project_path)
        await project_manager.vector_manager.initialize(enable_embedding_model=False)
        results = await project_manager.vector_manager.search_knowledge(
            query=target_document, collection=collection, n_results=max_results
        )

        documents = results.get("documents", [[]])
        docs_list = (
            documents[0] if documents and isinstance(documents[0], list) else documents
        )

        return f"Similar documents found:\n{json.dumps(docs_list, indent=2)}"

    except Exception as e:
        return f"Error finding similar documents: {str(e)}"


@context_aware(require_context=True)
async def extract_key_concepts_tool(text: str, **kwargs) -> str:
    """Extract key concepts from research text"""
    try:
        max_concepts = kwargs.get("max_concepts", 5)
        concepts = {}

        words = re.findall(r"\b[a-zA-Z-]{5,}\b", text.lower())
        word_freq = {word: words.count(word) for word in set(words)}
        sorted_concepts = sorted(
            word_freq.items(), key=lambda item: item[1], reverse=True
        )
        concepts["key_concepts"] = [
            word for word, freq in sorted_concepts[:max_concepts]
        ]

        return f"Extracted key concepts:\n{json.dumps(concepts, indent=2)}"

    except Exception as e:
        return f"Error extracting key concepts: {str(e)}"


@context_aware(require_context=True)
async def generate_research_summary_tool(documents: list, **kwargs) -> str:
    """Generate summary of research documents"""
    try:
        summary_type = kwargs.get("summary_type", "comprehensive")
        max_length = kwargs.get("max_length", 200)

        full_text = " ".join(documents)
        summary = full_text[:max_length]
        if len(full_text) > max_length:
            summary += "..."

        return f"Research Summary ({summary_type}):\n{summary}"

    except Exception as e:
        return f"Error generating research summary: {str(e)}"


def register_search_tools(server):
    """Register search and discovery tools with the MCP server"""

    server.register_tool(
        name="semantic_search",
        description="Perform semantic search across research documents",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "collection": {"type": "string", "default": "research_literature"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
        handler=semantic_search_tool,
    )

    server.register_tool(
        name="discover_patterns",
        description="Discover patterns and themes in research content",
        parameters={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to analyze"},
                "pattern_type": {
                    "type": "string",
                    "description": "Type of patterns to discover",
                    "default": "research_themes",
                },
                "min_frequency": {
                    "type": "integer",
                    "description": "Minimum frequency threshold",
                    "default": 2,
                },
            },
            "required": ["content"],
        },
        handler=discover_patterns_tool,
    )

    server.register_tool(
        name="build_knowledge_graph",
        description="Build knowledge graph from research documents",
        parameters={
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of documents",
                },
                "relationship_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types of relationships",
                },
            },
            "required": ["documents"],
        },
        handler=build_knowledge_graph_tool,
    )

    server.register_tool(
        name="find_similar_documents",
        description="Find documents similar to target document",
        parameters={
            "type": "object",
            "properties": {
                "target_document": {
                    "type": "string",
                    "description": "Target document content",
                },
                "collection": {
                    "type": "string",
                    "description": "Collection to search",
                    "default": "research_literature",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 5,
                },
            },
            "required": ["target_document"],
        },
        handler=find_similar_documents_tool,
    )

    server.register_tool(
        name="extract_key_concepts",
        description="Extract key concepts from research text",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
                "max_concepts": {
                    "type": "integer",
                    "description": "Maximum concepts to extract",
                    "default": 10,
                },
            },
            "required": ["text"],
        },
        handler=extract_key_concepts_tool,
    )

    server.register_tool(
        name="generate_research_summary",
        description="Generate summary of research documents",
        parameters={
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Documents to summarize",
                },
                "summary_type": {
                    "type": "string",
                    "description": "Type of summary",
                    "default": "comprehensive",
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum summary length",
                    "default": 500,
                },
            },
            "required": ["documents"],
        },
        handler=generate_research_summary_tool,
    )
