# SRRD-Builder

**S**cientific **R**esearch **R**equirement **D**ocument Builder - An AI-powered toolkit for scientific research collaboration and document generation.

## ✅ 100% Test Success Achieved**: Test suite fully operational with complete pass rate

- 183/183 tests passing (100% success rate)
- Comprehensive coverage across unit, integration, and validation tests
- Full research lifecycle persistence implemented and validated
- Production-ready with robust error handling and quality assurance

## Overview

SRRD-Builder uses a **neurosymbolic approach**, combining traditional symbolic programming (rule-based systems, structured knowledge, logical reasoning) with neural networks/large language models to support the scientific research lifecycle from initial planning to publication-ready documents.

The system features an **MCP (Model Context Protocol) server** that integrates with Claude Desktop and VS Code, providing **44 research tools** for document generation, knowledge management, and research quality assurance. It specializes in novel theory development for fundamental physics research, ensuring rigorous development of alternative paradigms with equal treatment to mainstream approaches.

## ⚠️ Production Ready**: This project is production-ready with complete functionality and comprehensive testing. Core features are fully implemented with 100% test success rate

## Key Features

- **MCP Server Integration** with Claude Desktop (automatic stdio mode)
- **CLI Tool (`srrd`)** for project initialization and configuration
- **WebSocket Demo Server (`srrd-server`)** for testing and web interfaces
- **44 Research Tools** including document generation, semantic search, and quality gates
- **Research Lifecycle Persistence** with automatic tool logging and progress tracking
- **Workflow Intelligence** providing AI-powered progress analysis and recommendations
- **LaTeX Document Generation** with automatic bibliography integration
- **Vector Database Storage** for semantic search and knowledge management
- **Git-based Project Management** with session restoration
- **Socratic Questioning Engine** for progressive research refinement
- **Novel Theory Development Framework** for paradigm innovation in physics
- **Web Frontend Interface** for testing and demonstration
- **Local Storage Integration** (Git, SQLite, Vector DB)

## Quick Start

### 🚀 Automated Installation

Choose your platform for quick setup:

#### Windows

```powershell
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
setup.bat
```

#### WSL (Windows Subsystem for Linux)

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
dos2unix setup.sh  # Convert Windows line endings
bash setup.sh
```

#### macOS/Linux

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh

# Optional: Run with comprehensive testing (183 tests)
./setup.sh --with-tests
```

### What the setup scripts do:

- Install Python dependencies with fallback to minimal requirements
- Install the `srrd` and `srrd-server` CLI tools
- Configure platform-specific LaTeX installation
- Set up Claude Desktop configuration automatically  
- Test all components and verify installation
- **Optionally run complete test suite (183 tests)**

## Platform Support

SRRD-Builder supports all major platforms with optimized setup:

- **Windows**: Native PowerShell setup with Windows-specific paths
- **WSL**: Linux environment on Windows with automatic virtual environment handling
- **macOS**: Homebrew integration and MacTeX installation
- **Linux**: Package manager detection and LaTeX setup

For detailed platform-specific instructions, see [Installation Guide](INSTALLATION.md).

## AI Agents Guide

We maintain a central guide for configuring and using AI agents in VS Code. See [AI Agent Quick Start](AI_AGENT_GUIDE.md) for details, including recommended extensions, settings, tasks, and snippets.

### 📱 Server Access Methods

SRRD-Builder provides two different server modes:

#### 1. Claude Desktop Integration (MCP stdio)

For Claude Desktop, no manual server management needed - it's configured in Claude's settings:

```bash
# Setup once
srrd init                    # Initialize project  
srrd configure --claude      # Configure Claude Desktop

# Claude Desktop automatically runs: python3 mcp_server.py
# No manual server start/stop needed
```

#### 2. WebSocket Demo Server (`srrd-server`)

For web interfaces and testing only:

```bash
# Start WebSocket demo server
srrd-server --with-frontend

# Check server status
srrd-server status

# Stop the server
srrd-server stop
```

### 🔧 Requirements

- **Python 3.8+** (all platforms)
- **LaTeX distribution**: 
  - Windows: MiKTeX
  - macOS: MacTeX  
  - Linux: TeXLive
  - WSL: TeXLive via package manager
- **Claude Desktop** (uses MCP stdio automatically)
- **Git** (for project initialization)

## Usage

### With Claude Desktop

1. Install using platform-specific setup script
2. Initialize project: `cd /path/to/git/repo && srrd init`
3. Configure Claude: `srrd configure --claude`
4. Restart Claude Desktop
5. Use SRRD-Builder tools in your conversations (no manual server start needed)

### Web Interface Demo

1. Start the demo system: `srrd-server --with-frontend`
2. Open web interface: <http://localhost:8080>
3. Click "Connect to Server" to establish WebSocket connection
4. Test any of the 44 available tools using the categorized interface

### Available Tools

The MCP server provides **44 tools** organized by research workflow categories:

#### 🧪 Research Planning & Goal Setting (2 tools)

- Socratic questioning to clarify research objectives and requirements
- Methodology advisory for selecting appropriate research approaches

#### ✅ Quality Assurance & Review (2 tools)

- AI-powered peer review simulation mimicking expert feedback
- Quality gates with automated validation at each research phase

#### 🗄️ Storage & Project Management (6 tools)

- Git-based project initialization and version control
- Session save/restore for research continuity
- Backup and project archival systems

#### 📄 Document Generation & LaTeX (6 tools)

- LaTeX document generation with automatic formatting
- Bibliography management and citation integration
- Template-based research document creation

#### 🔍 Search & Discovery (6 tools)

- Semantic search across research documents and knowledge bases
- Key concept extraction and pattern discovery
- Document similarity analysis and knowledge graph building

#### ⚗️ Methodology & Validation (4 tools)

- Research methodology explanation and guidance
- Experimental design validation and ethics review
- Statistical analysis framework recommendations

#### 🚀 Novel Theory Development (8 tools)

- Alternative paradigm development for fundamental physics
- Foundational assumption analysis and paradigm comparison
- Equal treatment validation for alternative theories

#### 🔄 Research Lifecycle Persistence (6 tools)

- Automatic tool usage logging and progress tracking
- Research session management and milestone tracking
- AI-powered workflow recommendations and health monitoring

### Example Workflow

```text
# With Claude Desktop:
"Initialize a new research project on quantum computing"
"Generate a LaTeX document with bibliography from my vector database"
"Perform semantic search for related documents"
"Simulate peer review of my methodology section"

# With Web Interface Demo:
1. Run: srrd-server --with-frontend
2. Open http://localhost:8080 in browser
3. Click "Connect to Server"
4. Test tools by clicking category buttons
5. View real-time results in console
```

## Server Architecture

SRRD-Builder uses two different server modes:

### Claude Desktop Integration (MCP stdio)

- **Purpose**: Integration with Claude Desktop within research projects
- **Protocol**: stdio (standard input/output) - Claude manages the process
- **Context**: Project-specific data and configuration loaded automatically
- **Use Case**: Daily research work, manuscript writing, project management
- **Management**: No manual start/stop - Claude Desktop handles it automatically

### WebSocket Demo Server (`srrd-server`)

- **Purpose**: Demos, web interfaces, and external tool integration only
- **Protocol**: WebSocket on localhost:8765
- **Context**: Global tool access without project dependency
- **Use Case**: Testing, demonstrations, web application integration
- **Management**: Manual start/stop with `srrd-server` command

## Technical Architecture

SRRD-Builder implements a **neurosymbolic architecture** that combines:

### Symbolic Components

- Rule-based validation and quality control systems
- Structured templates for different research types
- Knowledge graphs for research methodology relationships
- Git-based project management and version control

### Neural Components

- Large language model integration for content generation
- Semantic search across research documents and knowledge bases
- AI-powered peer review simulation and quality assessment
- Natural language processing for research requirement extraction

### Integration Layer

- MCP server interface for Claude Desktop and VS Code integration
- WebSocket server for web interfaces and external tool access
- Vector database storage for semantic search capabilities
- LaTeX document generation with automatic bibliography management

## Use Cases

### Academic Researchers

- Generate research protocols and methodology frameworks
- Access interactive Socratic guidance for research planning
- Create structured literature reviews with semantic search

### Graduate Students & Early Career Researchers

- Learn research methodology through interactive questioning
- Develop thesis proposals with systematic guidance
- Practice peer review processes with AI simulation

### Fundamental Physics Research

- Develop alternative theories with equal treatment frameworks
- Challenge existing paradigms through rigorous investigation
- Create publication-ready documents for novel ontologies

### Research Institutions

- Standardize research planning processes across departments
- Implement consistent quality control for research projects
- Coordinate multi-institutional collaborative efforts

### AI Research Systems

- Provide structured requirements for autonomous research
- Generate comprehensive research requirement documents
- Integrate systematic research planning into AI workflows

## Documentation

### Getting Started

- [📖 Installation Guide](INSTALLATION.md) - Detailed platform-specific installation instructions and troubleshooting
- [📋 Project Status](work/PROJECT_STATUS.md) - Current implementation status and completion tracking

### Testing & Quality

- [🧪 Test Suite Status](work/docs/TEST_SUITE.md) - Comprehensive testing documentation and guidelines
- **Run Tests:** `bash run_tests.sh` - Execute 183 tests with 100% success rate
- **Test Coverage:** Complete coverage across unit, integration, and validation tests (183/183 passing)

### Usage Guides

- [⚙️ Technical Requirements](work/docs/TECHNICAL_REQUIREMENTS.md) - Software library requirements and test specifications
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

#### Cross-Platform Issues

1. **Claude Desktop not finding tools**: Check configuration with `srrd configure --status` and ensure `claude_desktop_config.json` is properly set
2. **WebSocket demo server connection failed**: Ensure `srrd-server` is running and check port 8765 availability
3. **Web interface can't connect**: Make sure WebSocket server is running with `srrd-server --with-frontend`
4. **MCP server errors in Claude**: Check Python environment and dependencies, view logs in `work/code/mcp/logs/`
5. **LaTeX compilation errors**: Verify LaTeX installation with `pdflatex --version`
6. **Import errors**: Ensure virtual environment is activated

#### Platform-Specific Issues

**Windows:**
- **"'srrd' is not recognized"**: Ensure virtual environment is activated with `venv\Scripts\activate.bat`
- **"Access denied" errors**: Run as Administrator or check antivirus software

**WSL:**
- **"$'\r': command not found"**: Run `dos2unix setup.sh` to fix line endings
- **"venv/bin/activate: No such file"**: Script will automatically detect and recreate Unix-style venv

**All Platforms:**
- **Virtual environment activation**: 
  - Windows: `venv\Scripts\activate.bat`
  - macOS/Linux/WSL: `source venv/bin/activate`

### Getting Help

1. **Run Test Suite**: `bash run_tests.sh` - Full validation (183/183 tests passing)
2. Check server status: `srrd configure --status`
3. View logs in `work/code/mcp/logs/`
4. Check the [Installation Guide](INSTALLATION.md) for platform-specific troubleshooting
5. Check the [Test Suite Documentation](work/docs/TEST_SUITE.md) for testing guidelines

## Project Status

✅ **Production Ready**: This project is production-ready with complete functionality and comprehensive testing.

**Fully Implemented Features:**

- MCP Server with 44 research tools (full functionality)
- CLI tool for server management (`srrd` and `srrd-server` commands)
- Vector database integration with semantic search
- LaTeX document generation with automatic bibliography
- Git-based project management and session restoration
- Claude Desktop integration (full functionality)
- Web interface for testing and demonstrations
- Research lifecycle persistence with comprehensive tool logging
- Workflow intelligence with AI-powered progress tracking
- **Complete test suite (183/183 tests passing - 100% success rate)**
- **Cross-platform support (Windows, WSL, macOS, Linux)**

🚀 **Future Enhancement Plans:**

- Frontend dashboard for research progress visualization
- Enhanced AI features and advanced workflow automation
- Publication workflow integration and submission tools
- VS Code extension development
- Advanced semantic search features
- Extended research templates
- Performance optimization

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
