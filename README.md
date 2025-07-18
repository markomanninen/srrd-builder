# SRRD-Builder

**S**cientific **R**esearch **R**equirement **D**ocument Builder - A comprehensive AI-powered toolkit for scientific research collaboration and document generation.

## Overview

SRRD-Builder is designed to support the full scientific research lifecycle, from initial planning to publication-ready documents. It features special capabilities for novel theory development in fundamental physics, ensuring equal treatment and rigorous development of alternative paradigms.

The project provides a **Model Context Protocol (MCP) server** that integrates with Claude Desktop and VS Code, offering 38+ research tools for document generation, knowledge management, and research quality assurance.

## Key Features

- **Dual MCP Server Architecture** for both project-aware and global access
- **CLI Tool (`srrd`)** for project-aware server management and configuration
- **Global WebSocket Server (`srrd-server`)** for demos and web interfaces
- **38+ Research Tools** including document generation, semantic search, and quality gates
- **LaTeX Document Generation** with automatic bibliography integration
- **Vector Database Storage** for semantic search and knowledge management
- **Git-based Project Management** with session restoration
- **Socratic Questioning Engine** for progressive research refinement
- **Novel Theory Development Framework** for paradigm innovation in physics
- **Web Frontend Interface** for testing and demonstration
- **Local Storage Integration** (Git, SQLite, Vector DB)

## Quick Start

### 🚀 Automated Installation
```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh
```

This will:
- Install Python dependencies
- Install the `srrd` and `srrd-server` CLI tools
- Configure LaTeX (if needed)
- Set up Claude Desktop configuration
- Test all components

### 📱 Server Access Methods

SRRD-Builder provides two ways to access the MCP server:

#### 1. Project-Aware Server (`srrd serve`)
For use within SRRD projects with Claude Desktop/VS Code integration:

```bash
# Initialize a new research project
cd /path/to/your/git/repo
srrd init

# Start project-aware MCP server
srrd serve start

# Check configuration and server status
srrd configure --status

# Stop the MCP server  
srrd serve stop  
```

#### 2. Global WebSocket Server (`srrd-server`)
For demos, web interfaces, and external access:

```bash
# Start global WebSocket server only
srrd-server

# Start with web frontend interface
srrd-server --with-frontend

# Use custom ports
srrd-server --port 9000 --frontend-port 8080

# Get help
srrd-server --help
```

### 🔧 Requirements
- Python 3.8+
- LaTeX distribution (MacTeX on macOS, TeXLive on Linux)
- Claude Desktop or VS Code with MCP support (for project-aware mode)
- Git (for project initialization)

## Usage

### Method 1: With Claude Desktop (Project-Aware)

1. Install using `./setup.sh`
2. Initialize project: `cd /path/to/git/repo && srrd init`
3. Check status: `srrd configure --status`
4. Start server: `srrd serve start`
5. Restart Claude Desktop
6. Use SRRD-Builder tools in your conversations

### Method 2: Web Interface Demo (Global)

1. Start the complete demo system: `srrd-server --with-frontend`
2. Open web interface: http://localhost:8080
3. Click "Connect to Server"
4. Test any of the 38 available tools

### Available Tools

The MCP server provides 38+ tools organized by category:

- **🧪 Research Planning & Goal Setting** (2 tools): Clarify goals, suggest methodologies
- **✅ Quality Assurance & Review** (2 tools): Peer review simulation, quality gates
- **🗄️ Storage & Project Management** (6 tools): Initialize projects, save/restore sessions
- **📄 Document Generation & LaTeX** (6 tools): LaTeX compilation, bibliography management
- **🔍 Search & Discovery** (6 tools): Semantic search, concept extraction, pattern discovery
- **⚗️ Methodology & Validation** (4 tools): Methodology explanation, design validation
- **🚀 Novel Theory Development** (8 tools): Paradigm innovation, equal treatment validation

### Example Workflow

```
# Method 1: In Claude Desktop (project-aware):
"Initialize a new research project on quantum computing"
"Generate a LaTeX document with bibliography from my vector database"
"Perform semantic search for related documents"
"Simulate peer review of my methodology section"

# Method 2: In Web Interface (global demo):
1. Open http://localhost:8080 in browser
2. Click "Connect to Server"
3. Test tools by clicking category buttons
4. View real-time results in console
```

## Server Architecture

SRRD-Builder uses a dual server architecture to support different use cases:

### Project-Aware Server (`srrd serve`)
- **Purpose**: Integration with Claude Desktop/VS Code within research projects
- **Protocol**: stdio (standard input/output)
- **Context**: Project-specific data and configuration
- **Use Case**: Daily research work, manuscript writing, project management

### Global WebSocket Server (`srrd-server`)
- **Purpose**: Demos, web interfaces, and external tool integration
- **Protocol**: WebSocket on localhost:8765
- **Context**: Global tool access without project dependency
- **Use Case**: Testing, demonstrations, web application integration

## Documentation

### Getting Started
- [📖 Installation Guide](INSTALLATION.md) - Detailed installation instructions and troubleshooting
- [📋 Project Status](work/PROJECT_STATUS.md) - Current implementation status and completion tracking

### Usage Guides
- [⚙️ Technical Requirements](work/docs/TECHNICAL_REQUIREMENTS.md) - Complete software library requirements and test specifications
- [🤖 Guide for AI Agents](work/docs/GUIDE_FOR_AI_AGENTS.md) - Instructions for AI-assisted development

### Development Documentation
- [🗺️ Implementation Roadmap](work/docs/IMPLEMENTATION_ROADMAP.md) - Phase-by-phase development plan
- [📁 Work Directory Guide](work/WORK_DIRECTORY_GUIDE.md) - Overview of project structure
- [🌐 MCP Server Specification](work/docs/specifications/MCP_SERVER_SPECIFICATION.md) - Model Context Protocol server requirements
- [📦 Global Package Specification](work/docs/specifications/GLOBAL_PACKAGE_SPECIFICATION.md) - CLI and global installation requirements

### Research Support
- [📝 Research Templates](work/docs/templates/RESEARCH_TEMPLATES.md) - Domain-specific templates including theoretical physics
- [📖 Main README Draft](work/docs/README_DRAFT.md) - Comprehensive project overview and objectives

## Troubleshooting

### Common Issues

1. **Project-aware server not responding**: Check status with `srrd configure --status` and restart with `srrd serve restart`
2. **Global server connection failed**: Ensure `srrd-server` is running and check port 8765 availability
3. **Web interface can't connect**: Make sure WebSocket server is running with `srrd-server`
2. **Claude Desktop not finding tools**: Ensure server is running (`srrd serve start`) and restart Claude Desktop
3. **LaTeX compilation errors**: Verify LaTeX installation with `pdflatex --version`
4. **Import errors**: Ensure virtual environment is activated: `source venv/bin/activate`

### Getting Help

1. Check server status: `srrd configure --status`
2. View logs in `work/code/mcp/logs/`
3. Run comprehensive tests: `python3 work/code/mcp/test_comprehensive_tools_storage.py`
4. Check the [Installation Guide](INSTALLATION.md) for detailed troubleshooting

## Project Status

✅ **Completed Features:**
- MCP Server with 30+ research tools
- CLI tool for server management
- Vector database integration
- LaTeX document generation
- Git-based project management
- Claude Desktop integration
- Comprehensive test suite

🚧 **In Development:**
- Advanced semantic search features
- Extended research templates
- VS Code extension integration

## Special Focus: Novel Theory Development

This project emphasizes equal treatment and rigorous development of alternative theories in fundamental physics, providing:

- Paradigm challenge methodologies
- Alternative framework development tools
- Equal treatment validation protocols
- Specialized Socratic questioning for novel theories
- Publication-ready output for alternative paradigms

## Contributing

Please refer to the [Technical Requirements](work/docs/TECHNICAL_REQUIREMENTS.md) and [Implementation Roadmap](work/docs/IMPLEMENTATION_ROADMAP.md) for development guidelines and current priorities.

## License

See [LICENSE](LICENSE) file for details.
