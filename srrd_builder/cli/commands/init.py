"""
SRRD Init Command - Initialize SRRD project structure for scientific collaboration
"""

import os
import json
from pathlib import Path
from datetime import datetime
from ...utils.git_utils import is_git_repository, get_git_root

def create_project_structure(project_root: Path, domain: str, template: str, force: bool = False):
    """Create proper SRRD project structure"""
    
    # Check if .srrd already exists
    srrd_dir = project_root / '.srrd'
    if srrd_dir.exists() and not force:
        print(f"❌ SRRD already initialized in {project_root}")
        print("   Use --force to reinitialize")
        return False
    
    print(f"🔧 Creating SRRD project structure...")
    
    # Create main directories
    directories = [
        # SRRD configuration
        srrd_dir,
        srrd_dir / 'data',
        srrd_dir / 'logs',
        
        # Work area (development and drafts)
        project_root / 'work',
        project_root / 'work' / 'drafts',
        project_root / 'work' / 'research', 
        project_root / 'work' / 'data',
        
        # Publications (final outputs)
        project_root / 'publications'
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
        "mcp_server": {
            "enabled": True,
            "project_path": str(project_root)
        },
        "storage": {
            "git_enabled": True,
            "sqlite_db": ".srrd/data/sessions.db",
            "vector_db": ".srrd/data/knowledge.db"
        },
        "latex": {
            "output_dir": "publications",
            "draft_dir": "work/drafts"
        }
    }
    
    config_file = srrd_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"   ⚙️  {config_file.relative_to(project_root)}")
    
    # Create comprehensive .gitignore
    gitignore_content = create_gitignore_content()
    gitignore_file = project_root / '.gitignore'
    
    if gitignore_file.exists():
        # Append to existing .gitignore
        with open(gitignore_file, 'a') as f:
            f.write(f"\n# SRRD-Builder\n{gitignore_content}")
    else:
        # Create new .gitignore
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
    print(f"   🚫 {gitignore_file.relative_to(project_root)}")
    
    # Create README.md
    readme_content = create_readme_content(project_root.name, domain)
    readme_file = project_root / 'README.md'
    
    if not readme_file.exists():
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print(f"   📖 {readme_file.relative_to(project_root)}")
    
    # Create work area README
    work_readme = project_root / 'work' / 'README.md'
    with open(work_readme, 'w') as f:
        f.write(create_work_readme_content())
    print(f"   📖 {work_readme.relative_to(project_root)}")
    
    # Configure global MCP launcher for this project
    from ...utils.launcher_config import configure_global_launcher
    success, error = configure_global_launcher(project_root, srrd_dir)
    if success:
        print(f"   🚀 Global MCP launcher configured for this project")
        print(f"      Claude Desktop and VS Code Chat will use: {project_root}")
    else:
        print(f"   ⚠️  Warning: Could not configure global launcher: {error}")
        print(f"      MCP tools may not work until configured manually")
    
    return True

def create_gitignore_content():
    """Create comprehensive .gitignore for scientific collaboration"""
    return """
# SRRD-Builder files
.srrd/data/sessions.db*
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
    
    # Auto-initialize Git if not already a repository
    if not is_git_repository(current_dir):
        print("🔧 Not in a Git repository - auto-initializing...")
        try:
            import subprocess
            subprocess.run(['git', 'init'], 
                         cwd=current_dir, 
                         check=True, 
                         capture_output=True)
            print("   ✅ Git repository initialized")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to initialize Git: {e}")
            print("   Please install Git and try again")
            return 1
        except FileNotFoundError:
            print("   ❌ Git not found. Please install Git first.")
            return 1
    
    # Get Git repository root
    git_root = get_git_root(current_dir)
    if not git_root:
        git_root = current_dir  # Use current directory if can't determine git root
    
    print(f"🚀 Initializing SRRD project in: {git_root}")
    print(f"   Domain: {args.domain}")
    print(f"   Template: {args.template}")
    
    # Kill any existing MCP server processes before initializing new project
    from ...utils.process_utils import kill_mcp_processes, restart_message
    killed_count = kill_mcp_processes(verbose=True)
    
    if killed_count > 0:
        print(f"   ⚡ Stopped {killed_count} MCP server process(es)")
    
    # Create project structure
    if create_project_structure(git_root, args.domain, args.template, args.force):
        print("\n✅ SRRD-Builder project initialized successfully!")
        print(f"   Configuration: {git_root}/.srrd/config.json")
        print(f"   Global MCP launcher: Configured for THIS project")
        print("\n🎯 Ready to use:")
        print("   1. Open Claude Desktop    # All SRRD tools ready")
        print("   2. Open VS Code Chat      # All SRRD tools ready") 
        print("   3. srrd status           # Check project health")
        print("\n🔄 To switch to another project:")
        print("   1. cd /other/project && srrd switch")
        
        # Show restart instructions
        restart_message(f"New project {git_root.name} initialized.")
        
        return 0
    else:
        return 1
