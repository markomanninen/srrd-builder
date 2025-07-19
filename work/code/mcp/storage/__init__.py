"""
Storage module utilities for SRRD Builder
"""

from pathlib import Path

# Import storage managers
try:
    from .git_manager import GitManager
except ImportError:
    GitManager = None

try:
    from .sqlite_manager import SQLiteManager
except ImportError:
    SQLiteManager = None

try:
    from .vector_manager import VectorManager
except ImportError:
    VectorManager = None

# Import project manager
try:
    from .project_manager import ProjectManager
except ImportError:
    ProjectManager = None

def get_project_root():
    """
    Get the absolute path to the project root directory.
    This works regardless of current working directory.
    
    Returns the path to: /Users/markomanninen/Documents/GitHub/srrd-builder/srrd-builder
    """
    # Start from this file's directory and navigate up to project root
    current_file = Path(__file__)  # storage/__init__.py
    mcp_dir = current_file.parent.parent  # work/code/mcp
    work_dir = mcp_dir.parent.parent  # work
    project_root = work_dir.parent  # srrd-builder
    
    return project_root.resolve()

def get_srrd_db_path():
    """Get the absolute path to the project's .srrd/knowledge.db"""
    return get_project_root() / ".srrd" / "knowledge.db"

def get_config_path():
    """Get the absolute path to the vector collections config"""
    return get_project_root() / "work" / "code" / "mcp" / "config" / "vector_collections.yaml"