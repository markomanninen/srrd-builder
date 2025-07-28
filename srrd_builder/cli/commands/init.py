"""
SRRD Init Command - Initialize SRRD project structure for scientific collaboration
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the work/code/mcp directory to Python path for SQLiteManager import
current_dir = Path(__file__).parent.parent.parent.parent  # Go up to srrd-builder root
mcp_path = current_dir / "work" / "code" / "mcp"
if str(mcp_path) not in sys.path:
    sys.path.insert(0, str(mcp_path))

from storage.sqlite_manager import SQLiteManager

from ...utils.git_utils import get_git_root, is_git_repository


def create_project_structure(
    project_root: Path, domain: str, template: str, force: bool = False
):
    """Create proper SRRD project structure"""

    # Check if .srrd already exists
    srrd_dir = project_root / ".srrd"
    if srrd_dir.exists() and not force:
        print(f"❌ SRRD already initialized in {project_root}")
        print("   Use --force to reinitialize")
        return False

    print(f"🔧 Creating SRRD project structure...")

    # Create main directories
    directories = [
        # SRRD configuration
        srrd_dir,
        srrd_dir / "data",
        srrd_dir / "logs",
        # Work area (development and drafts)
        project_root / "work",
        project_root / "work" / "drafts",
        project_root / "work" / "research",
        project_root / "work" / "data",
        # Publications (final outputs)
        project_root / "publications",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   📁 {directory.relative_to(project_root)}")

    # Create SRRD configuration
    config = {
        "version": "0.1.0",
        "project_name": project_root.name,
        "domain": domain,
        "template": template,
        "created_at": datetime.now().isoformat(),
        "mcp_server": {"enabled": True, "project_path": str(project_root)},
        "storage": {
            "git_enabled": True,
            "sqlite_db": SQLiteManager.get_sessions_db_path(str(project_root)),
            "vector_db": ".srrd/data/knowledge.db",
        },
        "latex": {"output_dir": "publications", "draft_dir": "work/drafts"},
    }

    config_file = srrd_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"   ⚙️  {config_file.relative_to(project_root)}")

    # Create comprehensive .gitignore
    gitignore_content = create_gitignore_content()
    gitignore_file = project_root / ".gitignore"

    if gitignore_file.exists():
        # Append to existing .gitignore
        with open(gitignore_file, "a") as f:
            f.write(f"\n# SRRD-Builder\n{gitignore_content}")
    else:
        # Create new .gitignore
        with open(gitignore_file, "w") as f:
            f.write(gitignore_content)
    print(f"   🚫 {gitignore_file.relative_to(project_root)}")

    # Create README.md
    readme_content = create_readme_content(project_root.name, domain)
    readme_file = project_root / "README.md"

    if not readme_file.exists():
        with open(readme_file, "w") as f:
            f.write(readme_content)
        print(f"   📖 {readme_file.relative_to(project_root)}")

    # Create work area README
    work_readme = project_root / "work" / "README.md"
    with open(work_readme, "w") as f:
        f.write(create_work_readme_content())
    print(f"   📖 {work_readme.relative_to(project_root)}")

    # Set current project pointer using current_project.py
    try:
        from utils.current_project import set_current_project

        if set_current_project(str(project_root)):
            print(f"   🚀 Current project pointer set to: {project_root}")
            print(f"      Claude Desktop and VS Code Chat will use: {project_root}")
        else:
            print(f"   ⚠️  Warning: Could not set current project pointer!")
            print(f"      MCP tools may not work until configured manually")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not set current project pointer: {e}")
        print(f"      MCP tools may not work until configured manually")
        print(f"      MCP tools may not work until configured manually")
    return True


def create_gitignore_content():
    """Create comprehensive .gitignore for scientific collaboration"""
    return """
# SRRD-Builder files
.srrd/data/sessions.db (use SQLiteManager.get_sessions_db_path(project_path) for canonical resolution)
.srrd/data/knowledge.db*
.srrd/logs/*.log

# LaTeX temporary files
*.aux
*.bbl
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
*.lof
*.lot

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
.vscode/settings.json

# Temporary files
*.tmp
*.temp
.env
"""


def create_readme_content(project_name: str, domain: str):
    """Create main project README"""
    return f"""# {project_name}

A scientific research project in **{domain}** using SRRD-Builder.

## Publications

*No publications yet. Drafts can be published using `srrd publish <draft-name>`*

## Project Structure

- `work/` - Development and draft materials
  - `work/drafts/` - Draft papers and manuscripts  
  - `work/research/` - Research notes and data
  - `work/data/` - Datasets and experimental data
- `publications/` - Finalized published papers
- `.srrd/` - SRRD-Builder configuration and data

## Getting Started

1. **Create a draft**: Use Claude Desktop with SRRD-Builder tools to generate research content
2. **Work on draft**: Edit files in `work/drafts/`
3. **Publish**: Run `srrd publish <draft-name>` to move to `publications/`

## Commands

```bash
# Configure Claude Desktop for MCP tools
srrd configure --claude

# Check project status  
srrd status

# Generate LaTeX template
srrd generate template paper --title "My Paper"

# Compile LaTeX to PDF
srrd generate pdf work/drafts/my-paper.tex

# Publish finalized draft
srrd publish my-paper --version v1.0
```

## MCP Tools Available

Use these tools in Claude Desktop:
- `initialize_project` - Set up research project structure
- `generate_latex_document` - Create LaTeX documents with AI assistance
- `semantic_search` - Search through research knowledge base
- `simulate_peer_review` - Get AI-powered peer review feedback
- And 20+ more research assistance tools

---
*Powered by [SRRD-Builder](https://github.com/markomanninen/srrd-builder)*
"""


def create_work_readme_content():
    """Create work directory README"""
    return """# Work Directory

This directory contains all development and draft materials.

## Structure

- `drafts/` - Draft papers and manuscripts
- `research/` - Research notes, literature reviews, methodology
- `data/` - Datasets, experimental data, analysis scripts

## Workflow

1. Use Claude Desktop with SRRD-Builder to generate content in `drafts/`
2. Iterate and refine using MCP tools
3. When ready, use `srrd publish <draft-name>` to move to `publications/`

## Guidelines

- Keep drafts separate from final publications
- Use meaningful filenames (e.g., `quantum-computing-review.tex`)
- Commit regularly to track research progress
- Use MCP tools for content generation and quality assurance
"""


def handle_init(args):
    """Handle 'srrd init' command"""
    current_dir = Path.cwd()

    # Always use current directory for SRRD initialization
    # Don't try to find Git root - initialize where the user is
    project_root = current_dir

    print(f"🚀 Initializing SRRD project in: {project_root}")
    print(f"   Domain: {args.domain}")
    print(f"   Template: {args.template}")

    # Kill any existing Claude Desktop and MCP server processes before initializing
    from ...utils.process_cleanup import cleanup_claude_and_mcp_processes

    print("\n🔧 Preparing environment...")
    cleanup_claude_and_mcp_processes()

    # Auto-initialize Git if not already a repository in THIS directory
    git_was_initialized = False
    git_dir = current_dir / ".git"
    if not git_dir.exists():
        print("🔧 No Git repository in current directory - initializing...")
        try:
            import subprocess

            subprocess.run(
                ["git", "init"], cwd=current_dir, check=True, capture_output=True
            )
            print("   ✅ Git repository initialized")
            git_was_initialized = True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to initialize Git: {e}")
            print("   Please install Git and try again")
            return 1
        except FileNotFoundError:
            print("   ❌ Git not found. Please install Git first.")
            return 1

    # Create project structure
    if create_project_structure(project_root, args.domain, args.template, args.force):
        
        # Initialize database and create project entry
        print("🔧 Setting up project database...")
        try:
            import asyncio
            
            async def setup_database():
                db_path = SQLiteManager.get_sessions_db_path(str(project_root))
                sqlite_manager = SQLiteManager(db_path)
                await sqlite_manager.initialize()
                
                # Create project entry in database
                project_id = await sqlite_manager.create_project(
                    name=project_root.name,
                    description=f"Scientific research project in {args.domain}",
                    domain=args.domain
                )
                await sqlite_manager.close()
                return project_id
            
            project_id = asyncio.run(setup_database())
            print(f"   ✅ Project database initialized (Project ID: {project_id})")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not initialize project database: {e}")
            print(f"   You may need to run the 'initialize_project' MCP tool manually")

        # Make initial Git commit for the new SRRD project
        if (project_root / ".git").exists():
            print("🔧 Making initial Git commit...")
            try:
                import subprocess

                # Add all files
                subprocess.run(
                    ["git", "add", "."],
                    cwd=current_dir,
                    check=True,
                    capture_output=True,
                )

                # Make initial commit
                commit_message = (
                    f"Initial SRRD-Builder project setup for {args.domain} research"
                )
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=current_dir,
                    check=True,
                    capture_output=True,
                )
                print("   ✅ Initial commit created")

            except subprocess.CalledProcessError as e:
                # Check if it's because there are no changes to commit
                if "nothing to commit" in str(e):
                    print("   ℹ️  No changes to commit (files may already be tracked)")
                else:
                    print(f"   ⚠️  Warning: Could not create initial commit: {e}")
                    print(
                        "   You can manually commit files later with: git add . && git commit -m 'Initial setup'"
                    )

        print("\n✅ SRRD-Builder project initialized successfully!")
        print(f"   Configuration: {project_root}/.srrd/config.json")
        print(f"   Global MCP launcher: Configured for THIS project")

        # Show configuration instructions using existing commands
        print("\n📋 Configuration:")
        print("   Use 'srrd configure --status' to see configuration blocks")
        print("   Use 'srrd configure --claude' to auto-configure Claude Desktop")
        print("   Use 'srrd configure --vscode' to auto-configure VS Code")

        print("\n🎯 Ready to use:")
        print("   1. Open Claude Desktop    # All SRRD tools ready")
        print("   2. Open VS Code Chat      # All SRRD tools ready")
        print("   3. srrd status           # Check project health")
        print("\n🔄 To switch to another project:")
        print("   1. cd /other/project && srrd switch")

        # Suggest restarting Claude Desktop for new project
        print(
            f"\n💡 Tip: Restart Claude Desktop to ensure it uses the new project configuration."
        )

        return 0
    else:
        return 1
