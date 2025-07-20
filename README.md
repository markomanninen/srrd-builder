# SRRD-Builder### Testing & Quality

- [🧪 Test Suite Status](work/docs/TEST_SUITE.md) - Testing documentation and guidelines
- **Run Tests:** `bash run_tests.sh` - Execute test suite (183/183 tests passing)
- **Production Status:** Production-ready with 100% test success rateS**cientific **R**esearch **R**equirement **D**ocument Builder - An AI-powered toolkit for scientific research collaboration and document generation.

## Testing Status

**✅ 100% Test Success Achieved**: Test suite fully operational with complete pass rate:

- 183/183 tests passing (100% success rate)
- Comprehensive coverage across unit, integration, and validation tests
- Full research lifecycle persistence implemented and validated
- Production-ready with robust error handling and quality assurance


## Testing & Quality
- [🧪 Test Suite Status](work/docs/TEST_SUITE.md) - Testing documentation and guidelines
- **Run Tests:** `bash run_tests.sh` - Execute test suite (working toward 100% pass rate)
- **Development Status:** Test suite in development, working toward comprehensive coverage

## Overview

SRRD-Builder uses a **neurosymbolic approach**, combining traditional symbolic programming (rule-based systems, structured knowledge, logical reasoning) with neural networks/large language models to support the scientific research lifecycle from initial planning to publication-ready documents. 

The system features an **MCP (Model Context Protocol) server** that integrates with Claude Desktop and VS Code, providing **44 research tools** for document generation, knowledge management, and research quality assurance. It specializes in novel theory development for fundamental physics research, ensuring rigorous development of alternative paradigms with equal treatment to mainstream approaches.

**⚠️ Production Ready**: This project is production-ready with complete functionality and comprehensive testing. Core features are fully implemented with 100% test success rate.

## Key Features

- **Dual MCP Server Architecture** for both project-aware and global access
- **CLI Tool (`srrd`)** for project-aware server management and configuration
- **Global WebSocket Server (`srrd-server`)** for demos and web interfaces
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
```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh

# Optional: Run with comprehensive testing (158 tests)
./setup.sh --with-tests
```

This will:
- Install Python dependencies
- Install the `srrd` and `srrd-server` CLI tools
- Configure LaTeX (if needed)
- Set up Claude Desktop configuration
- Test all components
- **Optionally run test suite (158 tests in development)**
  
## AI Agents Guide
We maintain a central guide for configuring and using AI agents in VS Code. See [AI Agent Quick Start](AI_AGENT_GUIDE.md) for details, including recommended extensions, settings, tasks, and snippets.

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

1. Start the demo system: `srrd-server --with-frontend`
2. Open web interface: http://localhost:8080
3. Click "Connect to Server" to establish WebSocket connection
4. Test any of the 38 available tools using the categorized interface

### Available Tools

The MCP server provides **44 tools** organized by research workflow categories:

**🧪 Research Planning & Goal Setting (2 tools)**

- Socratic questioning to clarify research objectives and requirements
- Methodology advisory for selecting appropriate research approaches

**✅ Quality Assurance & Review (2 tools)**

- AI-powered peer review simulation mimicking expert feedback
- Quality gates with automated validation at each research phase

**🗄️ Storage & Project Management (6 tools)**

- Git-based project initialization and version control
- Session save/restore for research continuity
- Backup and project archival systems

**📄 Document Generation & LaTeX (6 tools)**

- LaTeX document generation with automatic formatting
- Bibliography management and citation integration
- Template-based research document creation

**🔍 Search & Discovery (6 tools)**

- Semantic search across research documents and knowledge bases
- Key concept extraction and pattern discovery
- Document similarity analysis and knowledge graph building

**⚗️ Methodology & Validation (4 tools)**

- Research methodology explanation and guidance
- Experimental design validation and ethics review
- Statistical analysis framework recommendations

**🚀 Novel Theory Development (8 tools)**

- Alternative paradigm development for fundamental physics
- Foundational assumption analysis and paradigm comparison
- Equal treatment validation for alternative theories

**🔄 Research Lifecycle Persistence (6 tools)**

- Automatic tool usage logging and progress tracking
- Research session management and milestone tracking
- AI-powered workflow recommendations and health monitoring

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

SRRD-Builder uses a **dual server architecture** to support different use cases:

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

## Technical Architecture

SRRD-Builder implements a **neurosymbolic architecture** that combines:

**Symbolic Components**
- Rule-based validation and quality control systems
- Structured templates for different research types  
- Knowledge graphs for research methodology relationships
- Git-based project management and version control

**Neural Components**
- Large language model integration for content generation
- Semantic search across research documents and knowledge bases
- AI-powered peer review simulation and quality assessment
- Natural language processing for research requirement extraction

**Integration Layer**
- MCP server interface for Claude Desktop and VS Code integration
- WebSocket server for web interfaces and external tool access
- Vector database storage for semantic search capabilities
- LaTeX document generation with automatic bibliography management

## Use Cases

**Academic Researchers**
- Generate research protocols and methodology frameworks
- Access interactive Socratic guidance for research planning
- Create structured literature reviews with semantic search

**Graduate Students & Early Career Researchers**
- Learn research methodology through interactive questioning
- Develop thesis proposals with systematic guidance
- Practice peer review processes with AI simulation

**Fundamental Physics Research**
- Develop alternative theories with equal treatment frameworks
- Challenge existing paradigms through rigorous investigation
- Create publication-ready documents for novel ontologies

**Research Institutions**
- Standardize research planning processes across departments
- Implement consistent quality control for research projects
- Coordinate multi-institutional collaborative efforts

**AI Research Systems**
- Provide structured requirements for autonomous research
- Generate comprehensive research requirement documents
- Integrate systematic research planning into AI workflows

## Documentation

### Getting Started
- [📖 Installation Guide](INSTALLATION.md) - Detailed installation instructions and troubleshooting  
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

1. **Project-aware server not responding**: Check status with `srrd configure --status` and restart with `srrd serve restart`
2. **Global server connection failed**: Ensure `srrd-server` is running and check port 8765 availability
3. **Web interface can't connect**: Make sure WebSocket server is running with `srrd-server`
2. **Claude Desktop not finding tools**: Ensure server is running (`srrd serve start`) and restart Claude Desktop
3. **LaTeX compilation errors**: Verify LaTeX installation with `pdflatex --version`
4. **Import errors**: Ensure virtual environment is activated: `source venv/bin/activate`

### Getting Help

1. **Run Test Suite**: `bash run_tests.sh` - Test validation (development in progress)
2. Check server status: `srrd configure --status`
3. View logs in `work/code/mcp/logs/`
4. Check the [Test Suite Documentation](work/docs/TEST_SUITE.md) for testing guidelines
5. Check the [Installation Guide](INSTALLATION.md) for detailed troubleshooting

## Project Status

🚧 **Development Status**: This project is in active development with core functionality working.

✅ **Production Ready Features:**

- MCP Server with 44 research tools (full functionality)
- CLI tool for server management  
- Vector database integration
- LaTeX document generation
- Git-based project management
- Claude Desktop integration (full functionality)
- Web interface for testing and demos
- Research lifecycle persistence with tool logging
- Workflow intelligence and progress tracking
- **Complete test suite (183/183 tests passing - 100% success rate)**

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

~/Library/Application Support/Code/User/mcp.json

## Contributing

Please refer to the [Technical Requirements](work/docs/TECHNICAL_REQUIREMENTS.md) and [Implementation Roadmap](work/docs/IMPLEMENTATION_ROADMAP.md) for development guidelines and current priorities.

## License

See [LICENSE](LICENSE) file for details.
