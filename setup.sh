#!/bin/bash
# SRRD-Builder MCP Server Setup Script for Unix/Linux/macOS

set -e

# Parse command line arguments
RUN_TESTS=false
if [[ "$1" == "--with-tests" ]]; then
    RUN_TESTS=true
fi

echo "🚀 SRRD-Builder MCP Server Setup"
echo "================================="

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    echo "⚠️  Unsupported platform. This script supports macOS and Linux."
    exit 1
fi

echo "📍 Detected platform: $PLATFORM"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist (Unix-style)
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "📦 Creating Unix virtual environment..."
    # Remove any existing Windows venv directory
    if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
        echo "🔄 Removing Windows virtual environment..."
        rm -rf venv
    fi
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Clean previous installation
echo "🧹 Cleaning previous SRRD-Builder installation..."
pip uninstall -y srrd-builder >/dev/null 2>&1 || true
echo "✅ Previous installation cleaned"

# Install Python dependencies
echo "📥 Installing Python dependencies..."
if pip install -r requirements.txt; then
    echo "✅ Python dependencies installed successfully"
else
    echo "⚠️  Full requirements failed. Trying minimal installation..."
    if pip install -r requirements-minimal.txt; then
        echo "✅ Minimal dependencies installed"
        echo "📝 Note: Some advanced features (semantic search, ML) may not be available"
    else
        echo "❌ Even minimal installation failed. Please check your Python environment."
        exit 1
    fi
fi

# Install SRRD CLI package
echo "🔧 Installing SRRD CLI package..."
if pip install -e .; then
    echo "✅ SRRD CLI package installed successfully"
else
    echo "❌ SRRD CLI installation failed"
    exit 1
fi

# Platform-specific installations
if [[ "$PLATFORM" == "macOS" ]]; then
    echo "🍺 Setting up macOS-specific configurations..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "⚠️  Homebrew not found. Install Homebrew for easier package management:"
        echo "    /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
    
    # Check for LaTeX installation
    if ! command -v pdflatex &> /dev/null; then
        echo "⚠️  LaTeX not found. Install MacTeX for document generation:"
        echo "    brew install --cask mactex"
        echo "📝 Document generation tools will show helpful error messages without LaTeX"
    else
        echo "✅ LaTeX found"
    fi
    
elif [[ "$PLATFORM" == "Linux" ]]; then
    echo "🐧 Setting up Linux-specific configurations..."
    
    # Check for LaTeX installation
    if ! command -v pdflatex &> /dev/null; then
        echo "⚠️  LaTeX not found. Install LaTeX for document generation:"
        if command -v apt-get &> /dev/null; then
            echo "    sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended"
        elif command -v yum &> /dev/null; then
            echo "    sudo yum install texlive-scheme-basic texlive-latex"
        else
            echo "    Please install LaTeX manually for your distribution"
        fi
        echo "📝 Document generation tools will show helpful error messages without LaTeX"
    else
        echo "✅ LaTeX found"
    fi
fi

# Download spaCy model (if spaCy is installed)
echo "🧠 Checking for spaCy..."
if python3 -c "import spacy" 2>/dev/null; then
    echo "📥 Downloading spaCy language model..."
    if python3 -m spacy download en_core_web_sm 2>/dev/null; then
        echo "✅ spaCy language model downloaded"
    else
        echo "⚠️  spaCy language model download failed"
    fi
else
    echo "⚠️  spaCy not installed - skipping language model download"
    echo "💡 To enable advanced NLP features, install spaCy: pip install spacy"
fi

# Download NLTK data (if NLTK is installed)
echo "📚 Checking for NLTK..."
if python3 -c "import nltk" 2>/dev/null; then
    echo "📥 Downloading NLTK data..."
    python3 -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print('✅ NLTK data downloaded')
except Exception as e:
    print(f'⚠️  NLTK download failed: {e}')
"
else
    echo "⚠️  NLTK not installed - skipping NLTK data download"
    echo "💡 To enable text processing features, install NLTK: pip install nltk"
fi

# Test basic functionality
echo "🧪 Testing basic functionality..."
if python -c "import srrd_builder; print('✅ Package import successful')"; then
    echo "Package import test passed"
else
    echo "❌ Package import failed"
    exit 1
fi

# Test CLI command
echo "Testing CLI command..."
if PYTHONWARNINGS="ignore" python -m srrd_builder.cli.main --version 2>/dev/null; then
    echo "CLI test passed"
else
    echo "❌ CLI test failed"
    exit 1
fi

# Test pytest
if python -m pytest --version &> /dev/null; then
    echo "✅ Pytest configured correctly"
else
    echo "❌ Pytest not working correctly"
    exit 1
fi

# Test installation
echo "🧪 Testing installation..."

# Test SRRD CLI
echo "Testing SRRD CLI..."

if command -v srrd &> /dev/null; then
    echo "✅ SRRD CLI available"
    
    # Test CLI status
    echo "Testing CLI status..."
    if srrd configure --status &> /dev/null; then
        echo "✅ CLI status command working"
    else
        echo "⚠️  CLI status command failed"
    fi
    
    # Test CLI help
    echo "Testing CLI help..."
    if srrd --help &> /dev/null; then
        echo "✅ CLI help command working"
    else
        echo "⚠️  CLI help command failed"
    fi
else
    echo "❌ SRRD CLI not available in PATH"
fi

# Test MCP server
echo "Testing MCP server..."
if [ -f "work/code/mcp/mcp_server.py" ]; then
    TEST_RESULT=$(echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 work/code/mcp/mcp_server.py 2>/dev/null)
    JSON_LINE=$(echo "$TEST_RESULT" | grep '^{')
    if [ -n "$JSON_LINE" ] && echo "$JSON_LINE" | grep -q '"tools"'; then
        TOOL_INFO=$(echo "$JSON_LINE" | python3 -c "import sys, json; data = json.load(sys.stdin); tools = data.get('result', {}).get('tools', []); print(len(tools)); print('\n'.join([t.get('name', '') for t in tools])) if tools else None")
        TOOL_COUNT=$(echo "$TOOL_INFO" | head -n1)
        TOOL_NAMES=$(echo "$TOOL_INFO" | tail -n +3 | tr '\n' ',' | sed 's/,$//')
        echo "✅ MCP server working ($TOOL_COUNT tools available)"
    else
        echo "❌ MCP server test failed"
        TOOL_NAMES=""
    fi
else
    echo "⚠️  MCP server file not found at work/code/mcp/mcp_server.py"
    TOOL_NAMES=""
fi

# Test LaTeX if available
if command -v pdflatex &> /dev/null; then
    echo "Testing LaTeX compilation..."
    cat > /tmp/srrd_test.tex << 'EOF'
\documentclass{article}
\begin{document}
Hello from SRRD-Builder!
\end{document}
EOF
    
    # Run the CLI command to generate the PDF. This is a finite process.
    echo "   - Compiling LaTeX to PDF via 'srrd generate pdf'..."
    python3 -m srrd_builder.cli.main generate pdf /tmp/srrd_test.tex
    
    # Check if the PDF was created
    if [ -f "/tmp/srrd_test.pdf" ]; then
        echo "   - ✅ SUCCESS: /tmp/srrd_test.pdf was generated."
        LATEX_SUCCESS=true
    else
        echo "   - ❌ FAILURE: PDF file was not created. Check LaTeX installation."
        LATEX_SUCCESS=false
    fi
else
    echo "⚠️  LaTeX not available - document generation tools will have limited functionality"
fi

# Generate Claude Desktop config
echo "⚙️  Generating Claude Desktop configuration..."
CURRENT_DIR=$(pwd)
CONFIG_CONTENT='{
  "mcpServers": {
    "srrd-builder": {
      "command": "python3",
      "args": ["'$CURRENT_DIR'/work/code/mcp/mcp_server.py"],
      "cwd": "'$CURRENT_DIR'/work/code/mcp",
      "env": {
        "PYTHONPATH": "'$CURRENT_DIR'/work/code/mcp"
      }
    }
  }
}'

echo "📋 Claude Desktop configuration:"
echo "$CONFIG_CONTENT"

if [[ "$PLATFORM" == "macOS" ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
    
    if [ -f "$CLAUDE_CONFIG_FILE" ]; then
        echo "⚠️  Claude Desktop config already exists at $CLAUDE_CONFIG_FILE"
        echo "💡 Please manually add the SRRD-Builder server configuration."
    else
        mkdir -p "$CLAUDE_CONFIG_DIR"
        echo "$CONFIG_CONTENT" > "$CLAUDE_CONFIG_FILE"
        echo "✅ Claude Desktop configuration created at $CLAUDE_CONFIG_FILE"
    fi
fi

# Optional test suite execution
if [[ "$RUN_TESTS" == "true" ]]; then
    echo ""
    echo "🧪 Running Professional Test Suite (158 tests)..."
    echo "================================================="
    
    if [ -f "run_tests.sh" ]; then
        if bash run_tests.sh; then
            echo "✅ All 158 tests passed successfully!"
        else
            echo "❌ Some tests failed. Check test output above."
            echo "💡 Installation is still functional - tests validate code quality."
        fi
    else
        echo "⚠️  Test runner not found. Skipping test execution."
    fi
else
    echo ""
    echo "💡 To run the professional test suite (158 tests):"
    echo "   bash run_tests.sh"
    echo "   or"
    echo "   ./setup.sh --with-tests"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Use 'srrd configure --status' to check configuration"
echo "2. Configure Claude Desktop: 'srrd configure --claude'"
echo "3. Restart Claude Desktop to use SRRD-Builder tools"
echo "4. Restart Claude Desktop if it's running"
echo "5. The SRRD-Builder tools should now be available in Claude Desktop"
echo "6. Check the INSTALLATION.md file for detailed documentation"
echo ""
echo "🧪 Quality Assurance:"
echo "   bash run_tests.sh    # Run 158 professional tests"
echo "   See work/docs/TEST_SUITE.md for testing guidelines"
echo ""
echo "🔧 To activate the environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "⚙️  CLI Commands:"
echo "   srrd configure --status      # Check configuration and server status"
echo "   srrd configure --claude      # Configure Claude Desktop"
echo "   srrd-server --with-frontend  # Start web demo"
echo ""
echo "📖 Available tools: $TOOL_NAMES"
echo ""
echo "🔄 Initializing global SRRD project context..."
python3 -c "import sys; sys.path.insert(0, '$(pwd)/srrd_builder/utils'); import launcher_config; launcher_config.reset_to_global_project()"
echo "✅ Global SRRD project context initialized (if not already present)"