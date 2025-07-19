# SRRD-Builder MCP Server Installation Guide

This guide covers all the dependencies and components needed to use the SRRD-Builder MCP server with Claude Desktop.

## Quick Installation (Recommended)

The fastest way to get started is using the automated setup script:

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh
```

This script will:
- Install Python dependencies with fallback to minimal requirements
- Install the `srrd` CLI tool
- Set up LaTeX (macOS/Linux)
- Configure Claude Desktop
- Test all components

After installation, use the CLI:

```bash
# Check configuration and status
srrd configure --status

# Start the MCP server
srrd serve start

# Stop the MCP server
srrd serve stop

# Restart the MCP server
srrd serve restart
```

## Manual Installation

If you prefer manual installation or encounter issues with the automated setup:

## Prerequisites

- **Python 3.8+**: Required for running the MCP server
- **Claude Desktop**: Required for using the MCP server
- **Git**: Required for version control features

## Core Dependencies

### 1. Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Install SRRD CLI package
pip install -e .
```

### 2. LaTeX Distribution (Required for Document Generation)

LaTeX is required for the document generation tools (`generate_latex_document`, `compile_latex`).

#### macOS:
```bash
# Install MacTeX (recommended - full distribution)
brew install --cask mactex

# Alternative: BasicTeX (minimal distribution)
brew install --cask basictex
sudo tlmgr update --self
sudo tlmgr install collection-latex collection-latexrecommended
```

#### Ubuntu/Debian:
```bash
# Full LaTeX distribution
sudo apt-get update
sudo apt-get install texlive-full

# Minimal installation
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

#### Windows:
```bash
# Install MiKTeX
winget install MiKTeX.MiKTeX

# Or download from: https://miktex.org/download
```

### 3. Vector Database (Optional - for semantic search)

The semantic search tools can work with various vector databases:

#### ChromaDB (Default):
```bash
pip install chromadb
```

#### Alternative: Pinecone
```bash
pip install pinecone-client
```

### 4. Machine Learning Libraries (Optional - for advanced features)

For enhanced semantic search and pattern discovery:

```bash
# Sentence transformers for embeddings
pip install sentence-transformers

# Scientific computing
pip install numpy scipy scikit-learn

# Natural language processing
pip install nltk spacy
python -m spacy download en_core_web_sm
```

## Claude Desktop Configuration

### Automatic Configuration (Recommended)

The setup script automatically configures Claude Desktop. To check or manually configure:

```bash
# Check current configuration status
srrd configure --status

# The CLI will show if Claude Desktop is properly configured
```

### Manual Configuration

1. **Locate Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add SRRD-Builder server configuration:**

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

## Server Management

Use the `srrd` CLI tool to manage the MCP server:

```bash
# Start the server
srrd serve start

# Check server status
srrd configure --status

# Stop the server
srrd serve stop

# Restart the server
srrd serve restart

# Get help
srrd serve --help
```

## Feature-Specific Requirements

### Document Generation Tools
- **Required**: LaTeX distribution (see above)
- **Tools affected**: `generate_latex_document`, `compile_latex`, `format_research_content`

### Semantic Search Tools
- **Required**: Vector database (ChromaDB recommended)
- **Optional**: Sentence transformers for better embeddings
- **Tools affected**: `semantic_search`, `find_similar_documents`, `build_knowledge_graph`

### Quality Assurance Tools
- **Required**: None (uses built-in Python libraries)
- **Tools affected**: `simulate_peer_review`, `check_quality_gates`

### Storage Management Tools
- **Required**: Git (for version control)
- **Optional**: Cloud storage backends
- **Tools affected**: `initialize_project`, `version_control`, `backup_project`

### Research Planning Tools
- **Required**: None (uses built-in Python libraries)
- **Tools affected**: `clarify_research_goals`, `suggest_methodology`

## Verification

### Automated Testing

The setup script includes automated testing, but you can also test manually:

```bash
# Test SRRD CLI
srrd --help
srrd configure --status

# Test MCP server directly
cd work/code/mcp
echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 mcp_server.py

# Test LaTeX compilation (if LaTeX is installed)
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "compile_latex", "arguments": {"tex_file_path": "/tmp/test.tex", "output_format": "pdf"}}, "id": 2}' | python3 mcp_server.py
```

### Testing with Claude Desktop

1. Start the server: `srrd serve start`
2. Restart Claude Desktop
3. In Claude, try: "List the available SRRD-Builder tools"
4. Check status anytime with: `srrd configure --status`

## Troubleshooting

### Common Issues

1. **"srrd command not found"**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Reinstall CLI package: `pip install -e .`

2. **"MCP server not starting"**
   - Check status: `srrd configure --status`
   - View logs: Check files in `work/code/mcp/logs/`
   - Restart: `srrd serve restart`

3. **"pdflatex not found"**
   - Install LaTeX distribution (see above)
   - Ensure pdflatex is in your PATH: `which pdflatex`

4. **"ModuleNotFoundError"**
   - Install missing Python dependencies: `pip install [module_name]`
   - Check virtual environment activation

5. **"Claude Desktop not finding tools"**
   - Ensure server is running: `srrd serve start`
   - Check configuration: `srrd configure --status`
   - Restart Claude Desktop after starting the server

6. **"Config file not found"**
   - Run setup script again: `./setup.sh`
   - Check Claude Desktop config manually

7. **"Tool execution error"**
   - Check tool-specific requirements above
   - Verify file paths are correct
   - Check Python environment and dependencies

### Performance Optimization

1. **For large document processing:**
   ```bash
   # Install faster JSON processing
   pip install orjson
   
   # Install parallel processing support
   pip install joblib
   ```

2. **For enhanced semantic search:**
   ```bash
   # Install GPU-accelerated libraries (if CUDA available)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Minimal Installation

For basic functionality without document generation:

```bash
# Python dependencies only
pip install chromadb sentence-transformers nltk

# Skip LaTeX installation
# Document generation tools will show helpful error messages
```

## Full Installation Script

```bash
#!/bin/bash
# Full SRRD-Builder installation script for macOS

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install LaTeX
brew install --cask mactex

# Install Python dependencies
pip install chromadb sentence-transformers nltk spacy numpy scipy scikit-learn
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo "SRRD-Builder installation complete!"
echo "Don't forget to configure Claude Desktop with the MCP server settings."
```

## Support

If you encounter issues:

1. Check this installation guide
2. Run `srrd configure --status` for current system status
3. Check logs in `work/code/mcp/logs/`
4. Run the comprehensive test suite: `bash run_tests.sh` (158 tests)
5. Verify all dependencies are installed
6. Check Claude Desktop logs: `~/Library/Logs/Claude/` (macOS)

## Version Information

- **SRRD-Builder MCP Server**: v1.0.0
- **Supported Python**: 3.8+
- **Supported Claude Desktop**: Latest version with MCP support
- **CLI Tool**: Included (`srrd` command)
- **Last Updated**: January 17, 2025
