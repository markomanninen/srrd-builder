# SRRD-Builder

**S**cientific **R**esearch **R**equirement **D**ocument Builder - A neurosymbolic (symbolic + LLM) tool for generating scientific research requirement documents with AI-driven research guidance.

## Overview

SRRD-Builder is designed to support the full scientific research lifecycle, from initial planning to publication-ready documents. It features special capabilities for novel theory development in fundamental physics, ensuring equal treatment and rigorous development of alternative paradigms.

The project provides a **Model Context Protocol (MCP) server** that integrates with Claude Desktop and VS Code, offering 30+ research tools for document generation, knowledge management, and research quality assurance.

## Key Features

- **MCP (Model Context Protocol) Server** for interactive research guidance
- **CLI Tool (`srrd`)** for server management and configuration
- **30+ Research Tools** including document generation, semantic search, and quality gates
- **LaTeX Document Generation** with automatic bibliography integration
- **Vector Database Storage** for semantic search and knowledge management
- **Git-based Project Management** with session restoration
- **Socratic Questioning Engine** for progressive research refinement
- **Novel Theory Development Framework** for paradigm innovation in physics
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
- Install the `srrd` CLI tool
- Configure LaTeX (if needed)
- Set up Claude Desktop configuration
- Test all components

### 📱 CLI Usage

After installation, use the `srrd` command-line tool:

```bash
# Check configuration and server status
srrd configure --status

# Start the MCP server
srrd serve start

# Stop the MCP server  
srrd serve stop

# Restart the MCP server
srrd serve restart

# Get help
srrd --help
```

### 🔧 Requirements
- Python 3.8+
- LaTeX distribution (MacTeX on macOS, TeXLive on Linux)
- Claude Desktop or VS Code with MCP support
- Git

## Usage

### With Claude Desktop

1. Install using `./setup.sh`
2. Check status: `srrd configure --status`
3. Start server: `srrd serve start`
4. Restart Claude Desktop
5. Use SRRD-Builder tools in your conversations

### Available Tools

The MCP server provides 30+ tools organized by category:

- **Project Management**: Initialize projects, save/restore sessions
- **Research Planning**: Clarify goals, suggest methodologies, quality gates
- **Document Generation**: LaTeX compilation, bibliography management
- **Knowledge Management**: Semantic search, concept extraction, pattern discovery
- **Storage**: Vector database operations, document similarity
- **Quality Assurance**: Peer review simulation, research validation

### Example Workflow

```
# In Claude Desktop:
"Initialize a new research project on quantum computing"
"Generate a LaTeX document with bibliography from my vector database"
"Perform semantic search for related documents"
"Simulate peer review of my methodology section"
```

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

1. **MCP Server not responding**: Check status with `srrd configure --status` and restart with `srrd serve restart`
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
