import os
import sys
from pathlib import Path

# Add utility functions for decorators
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

from context_decorator import context_aware
from current_project import get_current_project as get_project_path

import srrd_builder.config.installation_status

# Conditionally import vector database dependencies
try:
    from storage.project_manager import ProjectManager

    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False


@context_aware(require_context=True)
async def store_bibliography_reference_tool(**kwargs) -> str:
    """Store a bibliography reference in the vector database for future retrieval"""
    if not VECTOR_DB_AVAILABLE or not srrd_builder.config.installation_status.is_vector_db_installed():
        return "Vector database functionality is not available. Please install with --with-vector-database."

    project_manager = None
    try:
        reference = kwargs.get("reference", {})
        project_path = get_project_path()

        if not reference or not project_path:
            return "Error: Missing required parameters or project context."

        project_manager = ProjectManager(project_path)
        vector_manager = project_manager.vector_manager
        await vector_manager.initialize()

        if "research_literature" not in vector_manager.collections:
            return (
                "Error: 'research_literature' collection not found in vector database."
            )

        reference_text = f"Title: {reference.get('title', '')}\nAuthors: {reference.get('authors', '')}"
        doc_id = f"ref_{reference.get('title', 'unknown').replace(' ', '_').lower()}"

        await vector_manager.add_document(
            collection_name="research_literature",
            document=reference_text,
            doc_id=doc_id,
            metadata={"type": "bibliography_reference", **reference},
        )

        return f"Bibliography reference stored successfully: {reference.get('title', 'Unknown Title')}"

    except Exception as e:
        return f"Error storing bibliography reference: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


@context_aware(require_context=True)
async def retrieve_bibliography_references_tool(**kwargs) -> str:
    """Retrieve relevant bibliography references from the vector database based on search query"""
    if not VECTOR_DB_AVAILABLE or not srrd_builder.config.installation_status.is_vector_db_installed():
        return "Vector database functionality is not available. Please install with --with-vector-database."

    project_manager = None
    try:
        query = kwargs.get("query", "")
        project_path = get_project_path()

        if not query or not project_path:
            return "Error: Missing required parameters or project context."

        project_manager = ProjectManager(project_path)
        vector_manager = project_manager.vector_manager
        await vector_manager.initialize()

        if "research_literature" not in vector_manager.collections:
            return "Error: 'research_literature' collection not available in vector database."

        results = await vector_manager.search_knowledge(
            query=query,
            collection="research_literature",
            n_results=kwargs.get("max_results", 5),
        )

        metadatas = results.get("metadatas", [[]])[0]
        if not metadatas:
            return f"No bibliography references found for query: {query}"

        bib_entries = []
        for meta in metadatas:
            bib_entries.append(
                f"\\bibitem{{{meta.get('title', 'ref').replace(' ', '_')}}} {meta.get('authors', '')}. {meta.get('title', '')}. {meta.get('year', '')}."
            )

        return f"Retrieved {len(bib_entries)} references:\n\n" + "\n".join(bib_entries)

    except Exception as e:
        return f"Error retrieving bibliography references: {str(e)}"
    finally:
        if project_manager:
            await project_manager.close()


def register_vector_database_tools(server):
    """Register vector database tools with the MCP server"""
    if srrd_builder.config.installation_status.is_vector_db_installed():
        server.register_tool(
            name="store_bibliography_reference",
            description="Store a bibliography reference in the vector database",
            parameters={
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "object",
                        "description": "Reference data with title, authors, year, journal, etc.",
                    },
                },
                "required": ["reference"],
            },
            handler=store_bibliography_reference_tool,
        )

        server.register_tool(
            name="retrieve_bibliography_references",
            description="Retrieve relevant bibliography references from vector database",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for finding relevant references",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of references to retrieve",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            handler=retrieve_bibliography_references_tool,
        )
