from .research_planning import register_research_tools
from .quality_assurance import register_quality_tools
from .storage_management import register_storage_tools
from .document_generation import register_document_tools
from .search_discovery import register_search_tools
from .methodology_advisory import register_methodology_tools
from .novel_theory_development import register_novel_theory_tools
from .research_continuity import register_research_continuity_tools

def register_all_tools(server):
    """Register all tools with the MCP server"""
    register_research_tools(server)
    register_quality_tools(server)
    register_storage_tools(server)
    register_document_tools(server)
    register_search_tools(server)
    register_methodology_tools(server)
    register_novel_theory_tools(server)
    register_research_continuity_tools(server)

__all__ = [
    "register_all_tools",
    "register_research_tools",
    "register_quality_tools", 
    "register_storage_tools",
    "register_document_tools",
    "register_search_tools",
    "register_methodology_tools",
    "register_novel_theory_tools",
    "register_research_continuity_tools"
]
