# SRRD-Builder MCP Server

This directory contains the Model Context Protocol (MCP) server for SRRD-Builder.

## Production Files

- **`mcp_server.py`** - The main MCP server for Claude Desktop
- **`tools/`** - Tool modules providing all 21 research assistance tools
- **`storage/`** - Storage management backend

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
        "PYTHONPATH": "/path/to/srrd-builder/work/code/mcp"
      }
    }
  }
}
```

## Development

- Run `../../setup.sh` from the root directory to install dependencies and test the server
- The server uses stdio-based communication with Claude Desktop

## Testing

Test the MCP server directly:

```bash
echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 mcp_server.py
```

Should return a list of 21 available tools.

## Legacy Information (Archived)

A neurosymbolic Model Context Protocol (MCP) server for AI-driven scientific research requirement document generation, with specialized support for novel theory development in fundamental physics.

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
python3 run_server.py
```
The server will start on `localhost:8083` with WebSocket endpoint `ws://localhost:8083`

### Test the Implementation
```bash
# Run comprehensive test suite (24 tests)
python3 test_comprehensive_tools_storage.py

# Run basic functionality tests
python3 test_basic.py

# Test with interactive client
python3 test_client.py
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

```
mcp/
├── server.py              # Main MCP server implementation
├── run_server.py          # Server startup script
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

**Ready for production use** ✅ All systems tested and validated.
