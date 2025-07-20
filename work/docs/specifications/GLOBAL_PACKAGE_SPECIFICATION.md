# SRRD-Builder Package Specification

## Overview

The SRRD-Builder is a Python package that provides LaTeX-based scientific document generation with dual MCP server architecture for both project-aware research assistance and global demo/external access.

## Installation and Architecture

### Simple Installation

```bash
# Clone and setup (makes CLI globally available)
git clone <repository>
cd srrd-builder
./setup.sh

# Verify global CLI availability
srrd --version                    # ✅ Project-aware CLI (stdio MCP for Claude/VS Code)
srrd-server --version            # ✅ Global WebSocket server (demos/web interfaces)
```

**Note**: `./setup.sh` automatically runs `pip install -e .` which makes both `srrd` and `srrd-server` commands globally available. The dual architecture supports both integrated research workflows and standalone demonstrations.

### Dual Server Architecture

#### 1. Claude Desktop Integration (MCP stdio)

- **Purpose**: Integration with Claude Desktop within research projects
- **Protocol**: stdio (standard input/output) - Claude manages automatically
- **Context**: Project-specific data and configuration
- **Entry Point**: Direct `mcp_server.py` execution by Claude Desktop
- **Use Case**: Daily research work, manuscript writing, project management

#### 2. Global WebSocket Server (`srrd-server`)

- **Purpose**: Demos, web interfaces, and external tool integration
- **Protocol**: WebSocket on localhost:8765
- **Context**: Global tool access without project dependency
- **Entry Point**: `srrd_builder.server.launcher:main`
- **Use Case**: Testing, demonstrations, web application integration

### Package Structure

```text
srrd-builder/
├── srrd_builder/                 # Main package directory
│   ├── cli/                     # ✅ Project-aware CLI interface
│   │   ├── main.py             # Main CLI entry point (stdio MCP)
│   │   └── commands/           # Individual commands (init, generate, serve, etc.)
│   ├── config/                 # ✅ Configuration management
│   │   └── defaults.json       # Package defaults
│   └── server/                 # ✅ Global WebSocket server launcher
│       └── launcher.py         # Global MCP server launcher (WebSocket)
├── work/code/mcp/              # ✅ MCP server implementation (shared by both)
│   ├── server.py              # Main MCP server (38+ tools)
│   ├── tools/                 # Research, LaTeX, quality, novel theory tools
│   ├── config/                # Server configuration
│   │   └── default_config.json # MCP server config
│   ├── frontend/              # ✅ Web interface for global server
│   │   ├── index_dynamic.html # Dynamic tool discovery interface
│   │   └── mcp-client.js      # WebSocket MCP client
│   └── storage/               # Storage management (Git, SQLite, Vector DB)
├── setup.py                   # ✅ Package setup with dual entry points
├── requirements.txt           # ✅ Dependencies
└── README.md                  # ✅ Documentation
```

### Key Features

- ✅ **Dual CLI Access**: Both `srrd` and `srrd-server` commands work globally after setup
- ✅ **Project-Aware MCP**: Each project runs its own MCP server instance with context
- ✅ **Global WebSocket Demo**: Standalone server for testing and external integration
- ✅ **Web Frontend**: Dynamic interface for testing all 38 tools
- ✅ **In-Memory Templates**: LaTeX templates built into the system
- ✅ **Environment Config**: Use `SRRD_*` environment variables for configuration
- ✅ **Project-Specific**: Each project has its own `.srrd/` configuration and data

## MCP Server Access Methods

### 1. Claude Desktop Integration (Automatic)

```bash
# Within an SRRD project directory (has .srrd/ folder)
cd /path/to/your/research/project
srrd init                        # Creates .srrd/ project structure
srrd configure --claude          # Configure Claude Desktop once
# Claude Desktop automatically runs: python3 mcp_server.py
# No manual start/stop/restart needed
```

**Use case**: Research workflow within a specific project with project-specific databases, configuration, and context. Integrates with Claude Desktop via stdio protocol automatically.

### 2. Global WebSocket Server (`srrd-server`)

```bash
# Can run from anywhere - no project context needed
srrd-server                      # Start WebSocket server on default port 8765
srrd-server --port 8080          # Start on custom port
srrd-server --with-frontend      # Start with web interface on port 8080
srrd-server --frontend-port 9000 # Custom frontend port
```

**Use case**: Web GUI demos, external tool access, testing, and standalone demonstrations. Provides WebSocket API for custom applications.

### 3. Web Interface Testing

```bash
# Start complete demo system
srrd-server --with-frontend --frontend-port 8080

# Open browser to http://localhost:8080
# Features:
# - Dynamic discovery of all 38 tools
# - Real-time WebSocket connection status
# - Test interface for every tool
# - Categorized tool organization
# - Live console output
```

## Usage Workflow

### 1. Project Initialization (for project-aware usage)

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
# work/                   # Research work area
# publications/           # Final outputs

# Start Claude Desktop integration
srrd configure --claude
```

### 2. Global Demo Usage (no project needed)

```bash
# Start complete demo system
srrd-server --with-frontend

# Open http://localhost:8080 in browser
# Connect to server and test all tools
```

### 3. Generate Research Documents

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
# Use Claude Desktop for interactive guidance
srrd configure --claude

# Connect from Claude Desktop
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
