# Import tool modules with error handling

# Fix import path issues for all tools
import sys
from pathlib import Path

current_dir = Path(__file__).parent.parent

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Also add utils directory directly
utils_dir = current_dir / 'utils'
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

available_modules = {}

try:
    from .research_planning import register_research_tools
    available_modules['research_planning'] = register_research_tools
except ImportError as e:
    print(f"Warning: Failed to import research_planning: {e}")

try:
    from .quality_assurance import register_quality_tools
    available_modules['quality_assurance'] = register_quality_tools
except ImportError as e:
    print(f"Warning: Failed to import quality_assurance: {e}")

try:
    from .storage_management import register_storage_tools
    available_modules['storage_management'] = register_storage_tools
except ImportError as e:
    print(f"Warning: Failed to import storage_management: {e}")

try:
    from .document_generation import register_document_tools
    available_modules['document_generation'] = register_document_tools
except ImportError as e:
    print(f"Warning: Failed to import document_generation: {e}")

try:
    from .search_discovery import register_search_tools
    available_modules['search_discovery'] = register_search_tools
except ImportError as e:
    print(f"Warning: Failed to import search_discovery: {e}")

try:
    from .methodology_advisory import register_methodology_tools
    available_modules['methodology_advisory'] = register_methodology_tools
except ImportError as e:
    print(f"Warning: Failed to import methodology_advisory: {e}")

try:
    from .novel_theory_development import register_novel_theory_tools
    available_modules['novel_theory_development'] = register_novel_theory_tools
except ImportError as e:
    print(f"Warning: Failed to import novel_theory_development: {e}")

try:
    from .research_continuity import register_research_continuity_tools
    available_modules['research_continuity'] = register_research_continuity_tools
except ImportError as e:
    print(f"Warning: Failed to import research_continuity: {e}")

def register_all_tools(server):
    """Register all tools with the MCP server"""
    total_tools = 0
    
    for module_name, register_func in available_modules.items():
        try:
            tools_before = len(server.tools)
            register_func(server)
            tools_added = len(server.tools) - tools_before
            total_tools += tools_added
            print(f"Registered {tools_added} tools from {module_name}")
        except Exception as e:
            print(f"Error registering tools from {module_name}: {e}")
    
    print(f"Total tools registered: {total_tools}")

__all__ = [
    "register_all_tools",
    "available_modules"
] + list(available_modules.keys())
