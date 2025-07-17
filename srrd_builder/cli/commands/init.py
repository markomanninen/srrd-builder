"""
SRRD Init Command - Initialize SRRD in any Git repository
"""

import os
import json
from pathlib import Path
from ...utils.git_utils import is_git_repository, get_git_root

def create_srrd_structure(project_root: Path, force: bool = False):
    """Create .srrd directory structure in project"""
    srrd_dir = project_root / '.srrd'
    
    if srrd_dir.exists() and not force:
        print(f"❌ SRRD already initialized in {project_root}")
        print("   Use --force to reinitialize")
        return False
    
    # Create directory structure
    directories = [
        srrd_dir,
        srrd_dir / 'data',
        srrd_dir / 'documents', 
        srrd_dir / 'templates',
        srrd_dir / 'logs'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create config.json
    config = {
        "version": "0.1.0",
        "project_name": project_root.name,
        "created_at": "",
        "mcp_server": {
            "port": 8080,
            "host": "localhost"
        },
        "storage": {
            "git_enabled": True,
            "sqlite_enabled": True,
            "vector_db_enabled": True
        },
        "latex": {
            "default_template": "general",
            "auto_compile": True
        }
    }
    
    config_file = srrd_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create .gitignore for .srrd directory
    gitignore_content = """# SRRD-Builder files
*.log
*.tmp
sessions.db
knowledge.db*
"""
    
    gitignore_file = srrd_dir / '.gitignore'
    with open(gitignore_file, 'w') as f:
        f.write(gitignore_content)
    
    return True

def handle_init(args):
    """Handle 'srrd init' command"""
    current_dir = Path.cwd()
    
    # Check if we're in a Git repository
    if not is_git_repository(current_dir):
        print("❌ Not in a Git repository")
        print("   SRRD-Builder requires a Git repository to track research progress")
        print("   Initialize Git first: git init")
        return 1
    
    # Get Git repository root
    git_root = get_git_root(current_dir)
    if not git_root:
        print("❌ Could not determine Git repository root")
        return 1
    
    print(f"🔍 Initializing SRRD in: {git_root}")
    
    # Create SRRD structure
    if create_srrd_structure(git_root, args.force):
        print("✅ SRRD-Builder initialized successfully!")
        print(f"   Configuration: {git_root}/.srrd/config.json")
        print("   Start MCP server: srrd serve")
        return 0
    else:
        return 1
