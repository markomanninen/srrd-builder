# SRRD-Builder MCP Server Installation Guide

This guide covers all the dependencies and components needed to use the SRRD-Builder MCP server with Claude Desktop on Windows, WSL, macOS, and Linux.

## System Requirements

### **Essential Prerequisites:**

- **Python 3.8+** - Core runtime environment with pip package manager
- **Git** - Version control system for project management
- **Claude Desktop** - Required for MCP server integration and AI tools
- **2GB+ free disk space** - For LaTeX distributions, ML models, and dependencies
- **4GB+ RAM** - For running machine learning models and vector databases
- **Internet connection** - For downloading dependencies, models, and packages

### **Optional but Recommended:**

- **LaTeX Distribution** - For PDF document generation
  - Windows: MiKTeX (1-3GB) or TeX Live
  - macOS: MacTeX (4-5GB) via Homebrew
  - Linux: TeXLive (1-4GB depending on package selection)
- **VS Code with MCP Extension** - Alternative interface to Claude Desktop
- **Additional RAM** - 8GB+ recommended for large document processing

## Quick Installation (Recommended)

The fastest way to get started is using the automated setup script:

### Wi## MCP Configuration

Configure your MCP client to use the SRRD-Builder MCP server.

### VS Code Configuration

For VS Code with MCP extension, create or edit your MCP configuration file:

- **Windows**: `%APPDATA%\Code\User\mcp.json`
- **macOS**: `~/Library/Application Support/Code/User/mcp.json`
- **Linux**: `~/.config/Code/User/mcp.json`

**Configuration Format:**

```json
{
  "servers": {
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

### Claude Desktop Configuration

For Claude Desktop users, add to your configuration file:

- **Windows**: `%APPDATA%\Claude\config.json`
- **macOS**: `~/Library/Application Support/Claude/config.json`
- **Linux**: `~/.config/Claude/config.json`

**Configuration Format:**

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
```wershell
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
setup.bat
```

### WSL (Windows Subsystem for Linux)

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
dos2unix setup.sh  # Convert line endings from Windows format
bash setup.sh
```

### macOS/Linux

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh

# Optional: Install with vector database support
./setup.sh --with-vector-database

# Optional: Install with LaTeX support
./setup.sh --with-latex
```

These scripts will:

- Install Python dependencies with fallback to minimal requirements
- Install the `srrd` CLI tool
- Set up LaTeX (platform-specific instructions)
- Configure Claude Desktop
- Test all components

After installation, use the CLI:

```bash
# Initialize and configure project
srrd init                       # Initialize a new research project in current directory
srrd switch                     # Switch MCP context to this project
srrd configure --status         # Check configuration and status

# Claude Desktop Integration (automatic - no manual server management)
srrd configure --claude         # Configure Claude Desktop to use MCP server

# VS Code Integration (automatic with MCP extension)
srrd configure --vscode         # Configure VS Code to use MCP server

# WebSocket Demo Server (for testing and web interfaces only)
srrd-server --with-frontend     # Start demo server with web interface
srrd-server status              # Check demo server status
srrd-server stop                # Stop demo server
```

## Platform-Specific Installation

### Windows Installation

#### Windows Prerequisites

- **Python 3.8+**: Download from [python.org](https://python.org)
- **Claude Desktop**: Required for using the MCP server
- **Git**: Download from [git-scm.com](https://git-scm.com/)

#### Automated Setup (Recommended)

```powershell
# Clone the repository
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder

# Run the Windows setup script
setup.bat
```

The Windows setup script will:

- Check Python installation
- Create a virtual environment
- Install Python dependencies
- Install the SRRD CLI package
- Test all components
- Provide next steps

#### Manual Windows Installation

```powershell
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install SRRD CLI package
pip install -e .

# Test installation
srrd --version
```

#### Windows LaTeX Installation

```powershell
# Install MiKTeX using winget
winget install MiKTeX.MiKTeX

# Or download manually from: https://miktex.org/download
```

### WSL (Windows Subsystem for Linux) Installation

WSL provides a Linux environment on Windows. This is useful for users who prefer Unix-style tools.

#### Prerequisites

1. **Enable WSL**: Follow [Microsoft's WSL installation guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. **Install Ubuntu or preferred Linux distribution**
3. **Install Python 3.8+** in WSL

#### WSL Setup

```bash
# Clone the repository (in WSL)
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder

# Convert Windows line endings to Unix format
dos2unix setup.sh

# Run the Unix setup script
bash setup.sh
```

**Important WSL Notes:**

- The script will automatically detect and remove any Windows-style virtual environments
- Creates a new Unix-style virtual environment with proper activation scripts
- Installs all dependencies in the WSL environment
- Provides Linux package manager commands for LaTeX installation

#### WSL LaTeX Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# Or full installation
sudo apt-get install texlive-full
```

### macOS Installation

#### macOS Prerequisites

- **Python 3.8+**: Pre-installed or via Homebrew
- **Claude Desktop**: Required for using the MCP server
- **Git**: Pre-installed or via Xcode Command Line Tools

#### Automated macOS Setup

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh
```

The macOS setup script will:

- Install or check for Homebrew
- Install LaTeX (MacTeX) if not present
- Download spaCy and NLTK language models
- Configure Claude Desktop automatically

#### macOS LaTeX Installation

```bash
# Install MacTeX (recommended - full distribution)
brew install --cask mactex

# Alternative: BasicTeX (minimal distribution)
brew install --cask basictex
```

### Linux Installation

#### Linux Prerequisites

- **Python 3.8+**: Usually pre-installed or available via package manager
- **Claude Desktop**: Required for using the MCP server
- **Git**: Usually pre-installed or available via package manager

#### Automated Setup

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh
```

#### Linux LaTeX Installation

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# CentOS/RHEL/Fedora
sudo yum install texlive-scheme-basic texlive-latex
# or
sudo dnf install texlive-scheme-basic texlive-latex

# Arch Linux
sudo pacman -S texlive-most texlive-lang
```

## Manual Installation

If you prefer manual installation or encounter issues with the automated setup:

### Core Dependencies

#### 1. Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux/WSL
# or
venv\Scripts\activate     # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Install SRRD CLI package
pip install -e .
```

#### 2. Vector Database (Optional - for semantic search)

The semantic search tools can work with various vector databases:

```bash
# ChromaDB (Default)
pip install chromadb

# Alternative: Pinecone
pip install pinecone-client
```

#### 3. Machine Learning Libraries (Optional - for advanced features)

```bash
# Sentence transformers for embeddings
pip install sentence-transformers

# Scientific computing
pip install numpy scipy scikit-learn

# Natural language processing
pip install nltk spacy
python -m spacy download en_core_web_sm
```

## Configuring Claude Desktop

### Automatic Configuration (Recommended)

The setup scripts automatically configure Claude Desktop. To check or manually configure:

```bash
# Check current configuration status
srrd configure --status

# Automatically configure Claude Desktop
srrd configure --claude

# The CLI will show if Claude Desktop is properly configured
```

### Manual Configuration

1. **Locate Claude Desktop config file:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

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

**Windows Path Example:**

```json
{
  "mcpServers": {
    "srrd-builder": {
      "command": "python",
      "args": ["C:\\Users\\YourName\\Documents\\GitHub\\srrd-builder\\work\\code\\mcp\\mcp_server.py"],
      "cwd": "C:\\Users\\YourName\\Documents\\GitHub\\srrd-builder\\work\\code\\mcp",
      "env": {
        "PYTHONPATH": "C:\\Users\\YourName\\Documents\\GitHub\\srrd-builder\\work\\code\\mcp"
      }
    }
  }
}
```

## Server Management

### VS Code MCP (Automatic)

VS Code with MCP extension automatically manages the server:

```bash
# Configure once
srrd configure --vscode

# Check configuration status
srrd configure --status

# VS Code automatically runs: python3 mcp_server.py
```

### Claude Desktop (Automatic)

Claude Desktop automatically manages the MCP server. No manual start/stop needed:

```bash
# Configure once
srrd configure --claude

# Check configuration status
srrd configure --status

# Claude Desktop automatically runs: python3 mcp_server.py
```

### WebSocket Demo Server (Manual)

Use the WebSocket server launcher for demos and web interfaces only:

```bash
# Start demo server with web frontend
srrd-server --with-frontend

# Check server status
srrd-server status

# Stop the server
srrd-server stop

# Get help
srrd-server --help
```

## Feature-Specific Requirements

### Document Generation Tools

- **Required**: LaTeX distribution (see platform-specific installation above)
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

The setup scripts include automated testing, but you can also test manually:

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

1. Configure Claude: `srrd configure --claude`
2. Restart Claude Desktop
3. In Claude, try: "List the available SRRD-Builder tools"
4. Check status anytime with: `srrd configure --status`

## Troubleshooting

### Common Issues

#### Windows-Specific Issues

1. **"'srrd' is not recognized as an internal or external command"**
   - Ensure virtual environment is activated: `venv\Scripts\activate.bat`
   - Reinstall CLI package: `pip install -e .`
   - Check if Python Scripts directory is in PATH

2. **"setup.bat fails with 'may was unexpected at this time'"**
   - This was a known issue that has been fixed in the current version
   - Use the updated setup.bat script provided

3. **"Access denied" errors during installation**
   - Run PowerShell or Command Prompt as Administrator
   - Check antivirus software isn't blocking the installation

#### WSL-Specific Issues

1. **"setup.sh: line X: $'\r': command not found"**
   - Convert line endings: `dos2unix setup.sh`
   - This happens when the script has Windows line endings

2. **"venv/bin/activate: No such file or directory"**
   - The script will automatically detect and fix this
   - Remove Windows venv: `rm -rf venv` and run setup again

3. **"Python3 not found in WSL"**

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

#### Cross-Platform Issues

1. **"MCP tools not found in VS Code"**
   - Check VS Code MCP extension is installed and enabled
   - Verify mcp.json configuration: `srrd configure --status`
   - Restart VS Code after configuration changes
   - Check path separators (Windows uses `\`, Unix uses `/`)

2. **"Claude Desktop not finding tools"**
   - Check configuration: `srrd configure --status`
   - Ensure Claude Desktop config is properly set
   - Restart Claude Desktop after configuration changes
   - Check path separators (Windows uses `\`, Unix uses `/`)

3. **"MCP server not starting"**
   - Check status: `srrd configure --status`
   - View logs: Check files in `work/code/mcp/logs/`
   - Restart: `srrd-server restart`

4. **"pdflatex not found"**
   - Install LaTeX distribution (see platform-specific instructions above)
   - Ensure pdflatex is in your PATH: `which pdflatex` (Unix) or `where pdflatex` (Windows)

5. **"ModuleNotFoundError"**
   - Install missing Python dependencies: `pip install [module_name]`
   - Check virtual environment activation

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

## Platform-Specific Full Installation Scripts

### Windows PowerShell Script

```powershell
# Full SRRD-Builder installation script for Windows

# Install Python dependencies
pip install chromadb sentence-transformers nltk spacy numpy scipy scikit-learn

# Download language models
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Install MiKTeX (requires manual download)
Write-Host "Please install MiKTeX from: https://miktex.org/download"
Write-Host "SRRD-Builder Python components installation complete!"
```

### macOS/Linux Script

```bash
#!/bin/bash
# Full SRRD-Builder installation script for macOS/Linux

# Install system dependencies (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install --cask mactex
fi

# Install system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
    fi
fi

# Install Python dependencies
pip install chromadb sentence-transformers nltk spacy numpy scipy scikit-learn
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo "SRRD-Builder installation complete!"
```

## Support

If you encounter issues:

1. Check this installation guide for your specific platform
2. Run `srrd configure --status` for current system status
3. Check logs in `work/code/mcp/logs/`
4. Run the comprehensive test suite: `bash run_tests.sh` (158 tests)
5. Verify all dependencies are installed
6. Check MCP client logs:
   - **VS Code**: Open Developer Tools → Console for MCP extension logs
   - **Claude Desktop**: Check logs in:
     - Windows: `%APPDATA%\Claude\logs\`
     - macOS: `~/Library/Logs/Claude/`
     - Linux: `~/.config/Claude/logs/`

## Version Information

- **SRRD-Builder MCP Server**: v1.0.0
- **Supported Python**: 3.8+
- **Supported Platforms**: Windows, WSL, macOS, Linux
- **Supported Claude Desktop**: Latest version with MCP support
- **CLI Tool**: Included (`srrd` command)
- **Last Updated**: January 17, 2025
