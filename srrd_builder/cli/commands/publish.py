"""
SRRD Publish Command - Move finalized drafts to publications
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def handle_publish(args):
    """Handle 'srrd publish' command"""
    current_dir = Path.cwd()
    
    # Check if SRRD is initialized
    if not (current_dir / '.srrd').exists():
        print("❌ SRRD not initialized in current directory")
        print("   Run 'srrd init' first")
        return 1
    
    # Check if we're in a Git repository
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Not in a Git repository")
        print("   SRRD publish requires Git for version control")
        return 1
    
    # Define paths
    drafts_dir = current_dir / 'work' / 'drafts'
    publications_dir = current_dir / 'publications'
    draft_file = drafts_dir / f"{args.draft_name}.tex"
    
    # Check if draft exists
    if not draft_file.exists():
        print(f"❌ Draft not found: {draft_file}")
        print(f"   Available drafts in {drafts_dir}:")
        if drafts_dir.exists():
            for tex_file in drafts_dir.glob("*.tex"):
                print(f"   • {tex_file.stem}")
        return 1
    
    # Create publications directory if it doesn't exist
    publications_dir.mkdir(exist_ok=True)
    
    # Define publication paths
    pub_dir = publications_dir / args.draft_name
    pub_tex = pub_dir / f"{args.draft_name}.tex"
    
    # Check if publication already exists
    if pub_dir.exists() and not args.force:
        print(f"❌ Publication already exists: {pub_dir}")
        print("   Use --force to overwrite")
        return 1
    
    print(f"📝 Publishing: {args.draft_name}")
    print(f"   From: {draft_file}")
    print(f"   To: {pub_dir}")
    
    try:
        # Create publication directory
        pub_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy LaTeX source
        shutil.copy2(draft_file, pub_tex)
        
        # Copy any associated files (.bib, images, etc.)
        for ext in ['.bib', '.png', '.jpg', '.pdf']:
            associated_files = drafts_dir.glob(f"{args.draft_name}*{ext}")
            for file in associated_files:
                shutil.copy2(file, pub_dir / file.name)
        
        # Try to compile PDF
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', f"{args.draft_name}.tex"],
                cwd=pub_dir,
                capture_output=True,
                text=True
            )
            
            # Run bibtex if .bib file exists
            if (pub_dir / f"{args.draft_name}.bib").exists():
                subprocess.run(['bibtex', args.draft_name], cwd=pub_dir, capture_output=True)
                # Run pdflatex twice more for bibliography
                subprocess.run(['pdflatex', '-interaction=nonstopmode', f"{args.draft_name}.tex"], cwd=pub_dir, capture_output=True)
                subprocess.run(['pdflatex', '-interaction=nonstopmode', f"{args.draft_name}.tex"], cwd=pub_dir, capture_output=True)
            
            pdf_file = pub_dir / f"{args.draft_name}.pdf"
            if pdf_file.exists():
                print(f"✅ PDF compiled: {pdf_file}")
            else:
                print("⚠️  PDF compilation failed, but source published")
                
        except FileNotFoundError:
            print("⚠️  pdflatex not found - source published without PDF")
        
        # Update root README
        update_root_readme(current_dir, args.draft_name, args.version, pub_dir)
        
        # Create Git tag
        create_git_tag(args.draft_name, args.version)
        
        print(f"✅ Publication complete!")
        print(f"   Version: {args.version}")
        print(f"   Location: {pub_dir}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Publication failed: {str(e)}")
        return 1

def update_root_readme(project_dir: Path, draft_name: str, version: str, pub_dir: Path):
    """Update root README.md with publication info"""
    readme_file = project_dir / 'README.md'
    
    # Publication entry
    publication_line = f"- **{draft_name}** ({version}) - [PDF](publications/{draft_name}/{draft_name}.pdf) | [LaTeX](publications/{draft_name}/{draft_name}.tex)\n"
    
    if readme_file.exists():
        content = readme_file.read_text()
        
        # Look for Publications section
        if "## Publications" in content:
            # Add to existing section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("## Publications"):
                    # Insert after the Publications header
                    lines.insert(i + 2, publication_line.rstrip())
                    break
            content = '\n'.join(lines)
        else:
            # Add Publications section
            content += f"\n## Publications\n\n{publication_line}"
        
        readme_file.write_text(content)
    else:
        # Create new README
        readme_content = f"""# {project_dir.name}

## Publications

{publication_line}

## Overview

This is an SRRD-Builder research project.

## Structure

- `work/` - Development and draft materials
- `publications/` - Finalized published papers
"""
        readme_file.write_text(readme_content)

def create_git_tag(draft_name: str, version: str):
    """Create Git tag for the publication"""
    tag_name = f"{draft_name}-{version}"
    commit_message = f"Publish {draft_name} {version}"
    
    try:
        # Add and commit the publication
        subprocess.run(['git', 'add', 'publications/', 'README.md'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Create tag
        subprocess.run(['git', 'tag', '-a', tag_name, '-m', commit_message], check=True)
        
        print(f"📌 Git tag created: {tag_name}")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operations failed: {e}")
