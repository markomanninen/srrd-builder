# SRRD-Builder MCP Server

This directory contains the Model Context Protocol (MCP) server for SRRD-Builder with **context-aware functionality**.

## 🎯 Key Features

- **46 Context-Aware Tools** - All tools automatically detect project context
- **100% Enhancement Coverage** - Complete context-aware functionality
- **Backward Compatibility** - Existing tool calls work unchanged
- **Automatic Context Injection** - No manual project_path parameters needed
- **Graceful Fallback** - Works with or without project context
- **Project Context Management** - Switch between projects or reset to global context

## Production Files

- **`mcp_server.py`** - The main MCP server for Claude Desktop
- **`server.py`** - Alternative MCP server implementation
- **`tools/`** - Tool modules providing all 46 research assistance tools
- **`utils/`** - Context detection and decorator utilities
- **`storage/`** - Storage management backend

## Context-Aware Enhancement

All 38 tools are now enhanced with automatic context detection:

### Enhanced Tool Categories

- **Storage Management** (8/8) - Project initialization, session management, version control, context switching
- **Document Generation** (10/10) - LaTeX generation, compilation, formatting, templates
- **Search & Discovery** (6/6) - Semantic search, knowledge graphs, pattern discovery
- **Research Planning** (2/2) - Goal clarification, methodology suggestion  
- **Quality Assurance** (2/2) - Peer review simulation, quality gates
- **Methodology Advisory** (4/4) - Methodology explanation, design validation
- **Novel Theory Development** (8/8) - Paradigm challenge, framework development
- **Research Continuity** (6/6) - Progress tracking, session management, workflow intelligence

### New Project Context Management

**Switch Between Projects:**
```python
# Switch MCP context to a different project
result = await switch_project_context_tool(
    target_project_path="/path/to/my-research-project"
)
# All subsequent tool calls now use the target project's database
```

**Reset to Global Context:**
```python  
# Reset to global home project (neutral state)
result = await reset_project_context_tool()
# All tools now use the global ~/.srrd/globalproject context
```

### Usage Examples

**Traditional (still works):**

```python
# Explicit project_path parameter
result = await save_session_tool(
    session_data={'experiment': 'test'},
    project_path='/path/to/project'
)
```

**New Context-Aware:**

```python
# When configured with Claude Desktop - project_path is auto-detected
result = await save_session_tool(
    session_data={'experiment': 'test'}
    # project_path automatically injected from environment
)
```

## Configuration

The MCP server is configured in Claude Desktop's config file as:

```json
{
  "mcpServers": {
    "srrd-builder": {
      "command": "python3",
      "args": ["/path/to/srrd-builder/work/code/mcp/mcp_server.py"],
      "cwd": "/path/to/srrd-builder/work/code/mcp",
      "env": {
        "PYTHONPATH": "/path/to/srrd-builder/work/code/mcp",
        "SRRD_PROJECT_PATH": "/current/project/path",
        "SRRD_CONFIG_PATH": "/current/project/.srrd/config.json"
      }
    }
  }
}
```

**Context-Aware Environment Variables:**

- `SRRD_PROJECT_PATH` - Path to current SRRD project (set by Claude Desktop when configured)
- `SRRD_CONFIG_PATH` - Path to project config file (set by Claude Desktop when configured)

## Development

- Run `../../setup.sh` from the root directory to install dependencies and test the server
- The server uses stdio-based communication with Claude Desktop
- All 38 tools are enhanced with context-aware functionality

## Testing

Test the MCP server directly:

```bash
echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 mcp_server.py
```

Should return a list of 38 available tools.

**Run comprehensive tests:**

```bash
# Run the complete organized test suite (158 tests)
cd ../../../ && bash run_tests.sh

# The organized test suite covers all functionality:
# • 19 test files in work/tests/
# • Unit tests for all tools and components
# • Integration tests for workflows
# • Context-aware functionality validation
```

## Context-Aware Implementation

See [`CONTEXT_AWARE_IMPLEMENTATION.md`](CONTEXT_AWARE_IMPLEMENTATION.md) for detailed technical documentation on the context-aware enhancement system.

## Legacy Information (Archived)

A neurosymbolic Model Context Protocol (MCP) server for AI-driven scientific research requirement document generation, with specialized support for novel theory development in fundamental physics.

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python3 web_server.py
```

The server will start on `localhost:8083` with WebSocket endpoint `ws://localhost:8083`

### Test the Implementation

```bash
# All testing is now handled by the organized test suite
cd ../../../ && bash run_tests.sh

# 158 comprehensive tests covering all functionality
```

## 🧠 Neurosymbolic Architecture

This implementation combines:

- **Symbolic Programming**: Rule-based logic, structured knowledge representation
- **Neural Networks/LLMs**: Natural language processing, pattern recognition
- **MCP Protocol**: Standardized tool interface for AI interactions

## 🛠️ Available Tools (21 total)

### Research Planning

- `clarify_research_goals`: Socratic questioning for goal refinement
- `suggest_methodology`: Research methodology recommendations

### Quality Assurance  

- `simulate_peer_review`: AI-driven peer review simulation
- `check_quality_gates`: Research quality validation

### Document Generation

- `generate_latex_document`: LaTeX document with physics templates
- `format_research_content`: Content formatting and structure
- `generate_bibliography`: Bibliography and citation management

### Search & Discovery

- `semantic_search`: Intelligent content search
- `discover_patterns`: Research pattern identification  
- `extract_key_concepts`: Concept extraction and analysis

### Storage Management

- `initialize_project`: Project setup and configuration
- Additional Git, SQLite, and vector database tools

## 🔬 Novel Theory Development Features

### Equal Treatment Protocols

- Alternative theories receive equal computational resources
- Bias detection and mitigation in research evaluation
- Paradigm-agnostic methodology recommendations

### Foundational Analysis

- Assumption identification and examination
- Conceptual framework comparison
- Paradigm innovation support

### Socratic Questioning Engine

- Progressive question refinement
- Research goal clarification
- Methodology validation through inquiry

## 💾 Storage Systems

### Git Integration

- Project versioning and history
- Collaborative research support
- Backup and recovery systems

### SQLite Database

- Project metadata and sessions
- Interaction logging and tracking
- Structured data storage

### Vector Database (ChromaDB)

- Semantic search capabilities
- Research content indexing
- Pattern discovery and analysis

## 🧪 Test Results

The system passes **24/24 comprehensive tests** (100% success rate):

- ✅ **Storage Components**: 10/10 tests passed
- ✅ **Research Planning**: 2/2 tests passed  
- ✅ **Quality Assurance**: 2/2 tests passed
- ✅ **Document Generation**: 3/3 tests passed
- ✅ **Search & Discovery**: 3/3 tests passed
- ✅ **Storage Management**: 1/1 tests passed
- ✅ **System Tests**: 3/3 tests passed

## 📁 Directory Structure

```text
mcp/
├── server.py              # Main MCP server implementation
├── web_server.py          # Web GUI server startup script
├── requirements.txt       # Python dependencies
├── config/               # Configuration management
├── models/               # Data models (Project, Session, Interaction)
├── storage/              # Storage backends (Git, SQLite, Vector)
├── tools/                # MCP tools implementation
├── utils/                # Logging and utilities
└── tests/                # Test suites
```

## 🔧 Configuration

Default configuration in `config/default_config.json`:

- Server settings (host, port, logging)
- Database paths and settings
- Vector database collections
- LaTeX template configurations

## 🔌 MCP Protocol Compliance

Fully implements Model Context Protocol specification:

- Tool discovery and registration
- Structured input/output schemas
- Error handling and validation
- WebSocket communication interface

## 🎯 Research Focus Areas

- **Fundamental Physics**: Specialized templates and methodologies
- **Novel Theory Development**: Equal treatment and paradigm innovation
- **Quality Assurance**: Peer review simulation and validation
- **Document Generation**: LaTeX output with physics-specific formatting

## 🛡️ Error Handling

- Graceful fallbacks for missing dependencies
- Comprehensive error logging and reporting
- Resource cleanup and connection management
- Robust exception handling throughout

## 📊 Performance

- Clean startup and shutdown (no hanging)
- Efficient resource utilization
- Scalable storage backend support
- Asynchronous processing capabilities

---

**Development Status**: ✅ Core functionality working, test suite comprehensive (158 tests).
