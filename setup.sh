#!/bin/bash
# SRRD-Builder MCP Server Quick Setup Script

set -e

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

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -U pip

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
    echo "🍺 Installing macOS dependencies..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "📥 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install LaTeX
    if ! command -v pdflatex &> /dev/null; then
        echo "📄 Installing MacTeX..."
        brew install --cask mactex
        echo "⚠️  You may need to restart your terminal after MacTeX installation."
    else
        echo "✅ LaTeX already installed"
    fi
    
elif [[ "$PLATFORM" == "Linux" ]]; then
    echo "🐧 Installing Linux dependencies..."
    
    # Install LaTeX
    if ! command -v pdflatex &> /dev/null; then
        echo "📄 Installing LaTeX..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended
        elif command -v yum &> /dev/null; then
            sudo yum install -y texlive-scheme-basic texlive-latex
        else
            echo "⚠️  Please install LaTeX manually for your distribution"
        fi
    else
        echo "✅ LaTeX already installed"
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

# Test installation
echo "🧪 Testing installation..."

# Test SRRD CLI
echo "Testing SRRD CLI..."
cd ../../..  # Back to root directory for CLI testing

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

cd work/code/mcp

# Test MCP server
echo "Testing MCP server..."
TEST_RESULT=$(echo '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | python3 mcp_server.py 2>/dev/null)
if echo "$TEST_RESULT" | grep -q '"tools"'; then
    TOOL_COUNT=$(echo "$TEST_RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data.get('result', {}).get('tools', [])))
except:
    print('0')
")
    echo "✅ MCP server working ($TOOL_COUNT tools available)"
else
    echo "❌ MCP server test failed"
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
    
    TEST_LATEX=$(echo '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "compile_latex", "arguments": {"tex_file_path": "/tmp/srrd_test.tex", "output_format": "pdf"}}, "id": 2}' | python3 mcp_server.py 2>/dev/null)
    if echo "$TEST_LATEX" | grep -q "PDF compiled successfully"; then
        echo "✅ LaTeX compilation working"
        rm -f /tmp/srrd_test.*
    else
        echo "⚠️  LaTeX compilation test failed"
    fi
else
    echo "⚠️  LaTeX not available - document generation tools will have limited functionality"
fi

cd ../../..

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

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Use 'srrd configure --status' to check configuration"
echo "2. Use 'srrd serve start' to start the MCP server"
echo "3. Restart Claude Desktop if it's running"
echo "4. The SRRD-Builder tools should now be available in Claude Desktop"
echo "5. Check the INSTALLATION.md file for detailed documentation"
echo ""
echo "🔧 To activate the environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "⚙️  CLI Commands:"
echo "   srrd configure --status    # Check configuration and server status"
echo "   srrd serve start          # Start the MCP server"
echo "   srrd serve stop           # Stop the MCP server"
echo "   srrd serve restart        # Restart the MCP server"
echo ""
echo "📖 Available tools: research planning, document generation, semantic search, quality assurance, and storage management"
