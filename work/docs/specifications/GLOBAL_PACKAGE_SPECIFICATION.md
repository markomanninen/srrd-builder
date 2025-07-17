# SRRD-Builder Package Specification

## Overview

The SRRD-Builder is a Python package that provides LaTeX-based scientific document generation with MCP server integration for interactive AI-guided research assistance. It's designed to work within Git-based research projects.

## Installation and Architecture

### Simple Installation
```bash
# Clone and setup (makes CLI globally available)
git clone <repository>
cd srrd-builder  
./setup.sh

# Verify global CLI availability
srrd --version                    # ✅ Works from any directory
srrd-server --version            # ✅ Global WebSocket server for demos/external access
```

**Note**: `./setup.sh` automatically runs `pip install -e .` which makes both `srrd` and `srrd-server` commands globally available. Use `srrd serve` for project-aware server management, and `srrd-server` for standalone WebSocket demos.

### Package Structure

```
srrd-builder/
├── srrd_builder/                 # Main package directory  
│   ├── cli/                     # ✅ Command-line interface
│   │   ├── main.py             # Main CLI entry point
│   │   └── commands/           # Individual commands (init, generate, serve, etc.)
│   ├── config/                 # ✅ Configuration management  
│   │   └── defaults.json       # Package defaults
│   └── server/                 # ✅ Global server launcher
│       └── launcher.py         # Global MCP server launcher
├── work/code/mcp/              # ✅ MCP server implementation
│   ├── server.py              # Main MCP server
│   ├── tools/                 # 40+ MCP tools (research, latex, quality, etc.)
│   ├── config/                # Server configuration
│   │   └── default_config.json # Local MCP server config
│   └── storage/               # Storage management (Git, SQLite, Vector DB)
├── setup.py                   # ✅ Package setup with global entry points
├── requirements.txt           # ✅ Dependencies
└── README.md                  # ✅ Documentation
```

### Key Features
- ✅ **Global CLI Access**: `srrd` commands work from any directory after setup
- ✅ **Local MCP Server**: Each project runs its own MCP server instance
- ✅ **In-Memory Templates**: LaTeX templates built into the system (no external files needed)
- ✅ **Environment Config**: Use `SRRD_*` environment variables for configuration
- ✅ **Project-Specific**: Each project has its own `.srrd/` configuration and data

## MCP Server Access Methods

### Project-Aware Server Management (`srrd serve`)
```bash
# Within an SRRD project directory (has .srrd/ folder)
cd /path/to/your/research/project
srrd init                        # Creates .srrd/ project structure
srrd serve start                 # Start project-contextualized MCP server
srrd serve stop                  # Stop the server
srrd serve restart               # Restart the server
srrd serve status                # Check server status
```
**Use case**: Research workflow within a specific project with project-specific databases, config, and context.

### Global WebSocket Server (`srrd-server`)
```bash
# Can run from anywhere - no project context needed
srrd-server                      # Start WebSocket server on default port 8765
srrd-server --port 8080          # Start on custom port
srrd-server --stdio              # Start in stdio mode for Claude Desktop
```
**Use case**: Web GUI demos, external tool access, testing, or Claude Desktop integration.

## Usage Workflow

### 1. Project Initialization
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

### 2. Generate Research Documents
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

### 3. Interactive Research Guidance
```bash
# Start MCP server for interactive guidance
srrd serve --interactive

# Connect from MCP client
# The server provides Socratic questioning and methodology advice
```

## Configuration System

### Global Configuration
The package includes default configuration in `srrd_builder/config/defaults.json` with settings for:
- MCP server defaults (port, timeout, connections)
- LaTeX compilation settings
- Template management
- Knowledge base configuration

### Project-Specific Configuration  
Each project gets a `.srrd/config.json` file with:
- Project metadata (name, domain, methodology)
- LaTeX document structure
- Git integration settings

### Environment Variables
Configuration can be overridden using `SRRD_*` environment variables:
- `SRRD_MCP_PORT`: Override default MCP server port
- `SRRD_LATEX_COMPILER`: Override LaTeX compiler
- `SRRD_OUTPUT_DIR`: Override output directory

## Package Distribution

### Entry Points
The package provides these global commands via `setup.py`:
- `srrd`: Main CLI interface (includes `serve` command for project-aware MCP server management)
- `srrd-server`: Global MCP server launcher for WebSocket demos and external access

### Dependencies
Core dependencies include:
- `click`: CLI framework
- `gitpython`: Git integration
- `jinja2`: Template rendering
- `websockets`: MCP server communication
- `chromadb`: Vector database
- `sentence-transformers`: Text embedding

### Installation Requirements
- Python 3.8+
- Git repository (for project initialization)
- LaTeX distribution (for PDF compilation)
- Optional: spaCy, NLTK for advanced text processing

This specification defines a globally installable package that provides both CLI tools and MCP server functionality for scientific document generation and research assistance.
