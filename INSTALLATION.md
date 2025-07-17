# SRRD-Builder MCP Server Installation Guide

This guide covers all the dependencies and components needed to use the SRRD-Builder MCP server with Claude Desktop.

## Prerequisites

- **Python 3.8+**: Required for running the MCP server
- **Claude Desktop**: Required for using the MCP server
- **Git**: Required for version control features

## Core Dependencies

### 1. Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv srrd-builder-env
source srrd-builder-env/bin/activate  # On macOS/Linux
# or
srrd-builder-env\Scripts\activate     # On Windows

# Install Python dependencies
pip install -r requirements.txt
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

1. **Locate Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add SRRD-Builder server configuration:**

```json
{
  "mcpServers": {
    "srrd-builder": {
      "command": "python3",
      "args": ["/path/to/srrd-builder/work/code/mcp/mcp_claude_ultra_clean.py"],
      "cwd": "/path/to/srrd-builder/work/code/mcp",
      "env": {
        "PYTHONPATH": "/path/to/srrd-builder/work/code/mcp"
      }
    }
  }
}
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

Test your installation by running:

```bash
# Test the MCP server
cd /path/to/srrd-builder/work/code/mcp
echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 mcp_claude_ultra_clean.py

# Test LaTeX compilation
echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "compile_latex", "arguments": {"tex_file_path": "/tmp/test.tex", "output_format": "pdf"}}, "id": 2}' | python3 mcp_claude_ultra_clean.py
```

## Troubleshooting

### Common Issues

1. **"pdflatex not found"**
   - Install LaTeX distribution (see above)
   - Ensure pdflatex is in your PATH: `which pdflatex`

2. **"ModuleNotFoundError"**
   - Install missing Python dependencies: `pip install [module_name]`
   - Check virtual environment activation

3. **"Config file not found"**
   - Ensure Claude Desktop config file exists and is properly formatted
   - Check file permissions

4. **"Tool execution error"**
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
2. Verify all dependencies are installed
3. Test individual components
4. Check Claude Desktop logs: `~/Library/Logs/Claude/` (macOS)

## Version Information

- **SRRD-Builder MCP Server**: v1.0.0
- **Supported Python**: 3.8+
- **Supported Claude Desktop**: Latest version
- **Last Updated**: January 17, 2025
