# SRRD-Builder Global Package Specification

## Overview

The SRRD-Builder is designed as a globally installable Python package that can be used with any Git-based research project. It provides LaTeX-based publication generation with MCP server integration for interactive research guidance.

## Global Installation Architecture

### Package Structure
```
srrd-builder/
├── srrd_builder/                  # Main package directory
│   ├── __init__.py
│   ├── mcp_server/               # MCP server implementation
│   │   ├── __init__.py
│   │   ├── server.py            # Main MCP server
│   │   ├── tools/               # MCP tool implementations
│   │   │   ├── research_planning.py
│   │   │   ├── latex_generation.py
│   │   │   ├── quality_assurance.py
│   │   │   └── storage_management.py
│   │   └── storage/             # Storage management
│   │       ├── git_manager.py
│   │       ├── sqlite_manager.py
│   │       └── vector_manager.py
│   ├── templates/               # Global template library
│   │   ├── latex/              # LaTeX templates
│   │   │   ├── journals/       # Journal-specific templates
│   │   │   │   ├── nature.tex
│   │   │   │   ├── science.tex
│   │   │   │   ├── ieee.tex
│   │   │   │   └── acm.tex
│   │   │   ├── conferences/    # Conference templates
│   │   │   └── general/        # General academic templates
│   │   ├── proposal/           # Research proposal templates
│   │   └── methodology/        # Methodology templates
│   ├── knowledge_base/         # Global knowledge database
│   │   ├── methodologies.json
│   │   ├── best_practices.json
│   │   ├── journal_requirements.json
│   │   └── quality_standards.json
│   ├── cli/                    # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py            # Main CLI entry point
│   │   ├── commands/          # Individual commands
│   │   │   ├── init.py       # Project initialization
│   │   │   ├── generate.py   # Document generation
│   │   │   ├── serve.py      # MCP server management
│   │   │   ├── compile.py    # LaTeX compilation
│   │   │   └── template.py   # Template management
│   │   └── utils.py          # CLI utilities
│   ├── latex/                 # LaTeX processing engine
│   │   ├── __init__.py
│   │   ├── compiler.py       # LaTeX compilation
│   │   ├── validator.py      # LaTeX validation
│   │   ├── formatter.py      # Journal formatting
│   │   └── bibliography.py   # BibTeX management
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   ├── global_config.py
│   │   ├── project_config.py
│   │   └── defaults.json
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── git_utils.py
│       ├── file_utils.py
│       └── validation.py
├── setup.py                  # Package setup and installation
├── requirements.txt          # Dependencies
├── README.md                 # Package documentation
├── MANIFEST.in              # Package manifest
└── tests/                   # Test suite
    ├── test_cli.py
    ├── test_mcp_server.py
    ├── test_latex.py
    └── test_integration.py
```

## Installation and Usage

### Global Installation
```bash
# Install from PyPI
pip install srrd-builder

# Install from source
git clone https://github.com/your-org/srrd-builder.git
cd srrd-builder
pip install -e .

# Verify installation
srrd --version
srrd --help
```

### Usage in Any Git Repository

#### 1. Initialize SRRD in Existing Project
```bash
# Navigate to any Git repository
cd /path/to/your/research/project

# Initialize SRRD-Builder
srrd init

# This creates:
# .srrd/                    # SRRD metadata directory
# ├── config.json         # Project configuration
# ├── sessions.db         # SQLite database
# ├── knowledge.db        # Vector database
# └── templates/          # Local templates

# Start interactive MCP server
srrd serve --port 8080
```

#### 2. Generate Research Documents
```bash
# Generate research proposal
srrd generate proposal \
    --title "Machine Learning in Healthcare" \
    --methodology experimental \
    --domain "computer science" \
    --output documents/proposal/

# Generate manuscript for specific journal
srrd generate manuscript \
    --journal nature \
    --title "Novel AI Approach for Medical Diagnosis" \
    --sections all \
    --output documents/manuscripts/

# Compile LaTeX to PDF
srrd compile documents/manuscripts/main.tex --output main.pdf
```

#### 3. Interactive Research Guidance
```bash
# Start MCP server for interactive guidance
srrd serve --interactive

# Connect from MCP client
# The server provides Socratic questioning and methodology advice
```

## LaTeX Integration System

### Template Management

#### Journal-Specific Templates
```latex
% Nature Journal Template (templates/latex/journals/nature.tex)
\documentclass[fleqn,10pt]{wlscirep}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}

\title{{{TITLE}}}

\author[1,*]{ {{FIRST_AUTHOR}} }
\author[2]{ {{SECOND_AUTHOR}} }
\affil[1]{ {{FIRST_AFFILIATION}} }
\affil[2]{ {{SECOND_AFFILIATION}} }
\affil[*]{ {{CORRESPONDING_EMAIL}} }

\begin{document}
\maketitle

\begin{abstract}
{{ABSTRACT}}
\end{abstract}

\section{Introduction}
{{INTRODUCTION}}

\section{Methods}
{{METHODS}}

\section{Results}
{{RESULTS}}

\section{Discussion}
{{DISCUSSION}}

\bibliography{references}
\end{document}
```

#### Dynamic Content Generation
```python
# latex/compiler.py
class LaTeXCompiler:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.templates_path = self.project_path / '.srrd' / 'templates'
        
    def generate_document(self, template_name: str, content_data: dict) -> str:
        """Generate LaTeX document from template and research data"""
        template = self.load_template(template_name)
        return self.render_template(template, content_data)
        
    def compile_to_pdf(self, tex_file: str) -> dict:
        """Compile LaTeX document to PDF with error handling"""
        result = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory=' + str(self.project_path / 'documents'),
            tex_file
        ], capture_output=True, text=True)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr,
            'pdf_path': tex_file.replace('.tex', '.pdf')
        }
```

### Bibliography Management
```python
# latex/bibliography.py
class BibliographyManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.bib_file = self.project_path / 'documents' / 'references.bib'
        
    def add_reference(self, reference_data: dict) -> str:
        """Add reference to bibliography"""
        bib_entry = self.format_bibtex_entry(reference_data)
        with open(self.bib_file, 'a') as f:
            f.write(bib_entry + '\n')
        return bib_entry
        
    def validate_bibliography(self) -> dict:
        """Validate BibTeX syntax and completeness"""
        # Implementation for bibliography validation
```

## MCP Server Integration

### Auto-Detection and Setup
```python
# cli/commands/init.py
class ProjectInitializer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def detect_existing_project(self) -> dict:
        """Detect existing research project structure"""
        git_repo = git.Repo.search_parent_dirs(self.project_path)
        if not git_repo:
            raise ValueError("Not a Git repository")
            
        # Detect existing LaTeX files
        latex_files = list(self.project_path.rglob('*.tex'))
        
        # Detect research data directories
        data_dirs = [d for d in self.project_path.iterdir() 
                    if d.is_dir() and d.name in ['data', 'datasets', 'experiments']]
        
        # Detect existing papers/manuscripts
        paper_dirs = [d for d in self.project_path.iterdir()
                     if d.is_dir() and d.name in ['papers', 'manuscripts', 'documents']]
        
        return {
            'git_repo': git_repo,
            'latex_files': latex_files,
            'data_dirs': data_dirs,
            'paper_dirs': paper_dirs,
            'project_type': self.infer_project_type(latex_files, data_dirs)
        }
        
    def setup_srrd_structure(self) -> bool:
        """Set up SRRD structure in existing project"""
        # Create .srrd directory structure
        srrd_dir = self.project_path / '.srrd'
        srrd_dir.mkdir(exist_ok=True)
        
        # Initialize databases
        self.init_sqlite_database()
        self.init_vector_database()
        
        # Copy global templates
        self.setup_templates()
        
        # Create configuration
        self.create_project_config()
        
        return True
```

### Command-Line Interface
```python
# cli/main.py
import click
from .commands import init, generate, serve, compile_cmd, template

@click.group()
@click.version_option()
def main():
    """SRRD-Builder: Scientific Research Requirement Document Builder"""
    pass

@main.command()
@click.option('--template', default='general', help='Initial template type')
@click.option('--domain', help='Research domain')
@click.option('--methodology', help='Research methodology')
def init(template, domain, methodology):
    """Initialize SRRD-Builder in current Git repository"""
    from .commands.init import InitCommand
    InitCommand().execute(template, domain, methodology)

@main.command()
@click.argument('document_type')
@click.option('--journal', help='Target journal for formatting')
@click.option('--template', help='Template name')
@click.option('--output', help='Output directory')
def generate(document_type, journal, template, output):
    """Generate research documents"""
    from .commands.generate import GenerateCommand
    GenerateCommand().execute(document_type, journal, template, output)

@main.command()
@click.option('--port', default=8080, help='Server port')
@click.option('--host', default='localhost', help='Server host')
@click.option('--interactive', is_flag=True, help='Interactive mode')
def serve(port, host, interactive):
    """Start MCP server"""
    from .commands.serve import ServeCommand
    ServeCommand().execute(port, host, interactive)

if __name__ == '__main__':
    main()
```

## Configuration System

### Global Configuration
```json
// config/defaults.json
{
    "mcp_server": {
        "default_port": 8080,
        "timeout": 300,
        "max_connections": 10
    },
    "latex": {
        "compiler": "pdflatex",
        "bibtex_processor": "bibtex",
        "max_compilation_time": 60,
        "output_format": "pdf"
    },
    "templates": {
        "update_interval": 86400,
        "remote_repository": "https://github.com/srrd-templates/official",
        "local_cache": "~/.srrd_templates"
    },
    "knowledge_base": {
        "auto_update": true,
        "embedding_model": "all-MiniLM-L6-v2",
        "max_results": 10
    }
}
```

### Project-Specific Configuration
```json
// .srrd/config.json (created in each project)
{
    "project": {
        "name": "My Research Project",
        "domain": "computer science",
        "methodology": "experimental",
        "created_at": "2025-07-16T10:00:00Z"
    },
    "latex": {
        "main_document": "documents/manuscript/main.tex",
        "bibliography": "documents/references.bib",
        "figure_directory": "documents/figures/",
        "output_directory": "documents/output/"
    },
    "git": {
        "auto_commit": true,
        "commit_message_template": "[SRRD] {action}: {description}",
        "ignored_patterns": ["*.aux", "*.log", "*.bbl", "*.blg"]
    }
}
```

## Quality Assurance and Testing

### Automated Testing
```python
# tests/test_integration.py
class TestGlobalIntegration:
    def test_install_and_init(self, tmp_git_repo):
        """Test global installation and project initialization"""
        # Test CLI commands work after installation
        result = subprocess.run(['srrd', 'init'], 
                              cwd=tmp_git_repo, 
                              capture_output=True)
        assert result.returncode == 0
        assert (tmp_git_repo / '.srrd').exists()
        
    def test_latex_compilation(self, tmp_project):
        """Test LaTeX document generation and compilation"""
        # Generate document
        subprocess.run(['srrd', 'generate', 'manuscript', 
                       '--journal', 'nature'], cwd=tmp_project)
        
        # Compile to PDF
        result = subprocess.run(['srrd', 'compile', 
                               'documents/manuscript/main.tex'], 
                               cwd=tmp_project)
        assert result.returncode == 0
        assert (tmp_project / 'documents/manuscript/main.pdf').exists()
```

## Distribution and Packaging

### PyPI Package Setup
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="srrd-builder",
    version="1.0.0",
    author="SRRD-Builder Team",
    author_email="contact@srrd-builder.org",
    description="Scientific Research Requirement Document Builder with MCP integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/srrd-builder/srrd-builder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "gitpython>=3.1.0",
        "jinja2>=3.0.0",
        "pylatex>=1.4.0",
        "chromadb>=0.4.0",
        "sentence-transformers",
        "websockets>=10.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
    },
    entry_points={
        "console_scripts": [
            "srrd=srrd_builder.cli.main:main",
        ],
    },
    package_data={
        "srrd_builder": [
            "templates/**/*",
            "knowledge_base/**/*",
            "config/**/*",
        ],
    },
    include_package_data=True,
)
```

This global package design ensures that SRRD-Builder can be installed once and used across any Git-based research project, with comprehensive LaTeX support for publication-ready document generation.
