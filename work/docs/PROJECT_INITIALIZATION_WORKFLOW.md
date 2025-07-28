# Project Initialization Workflow

## Installation

### Automated Installation

Choose your platform for quick setup:

#### Windows

```powershell
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.bat
```

#### macOS/Linux

```bash
git clone https://github.com/markomanninen/srrd-builder
cd srrd-builder
./setup.sh

# Optional: Install with vector database support
./setup.sh --with-vector-database

# Optional: Install with LaTeX support
./setup.sh --with-latex
```

### Manual Installation

See the [Installation Guide](INSTALLATION.md) for detailed instructions.

## Project Initialization

### Via CLI

```bash
# Navigate to your research directory
cd /path/to/my-research-area

# Initialize a new project
srrd init

# The CLI will automatically switch to the new project context
```

### Via MCP Tools (Claude Desktop)

```bash
# In Claude Desktop, use the `initialize_project` tool
initialize_project(
  name="Quantum NLP Research",
  description="Research on quantum computing in NLP",
  domain="computer_science"
)

# The MCP server will automatically switch to the new project context
```

## Switching Projects

```bash
# Switch to a different project directory
cd /path/to/another-project

# Switch the MCP context
srrd switch

# Reset to the global context
srrd reset
```

## Verifying the Context

```bash
# Check the current project context
srrd status
```

## Project Structure

When a project is initialized, the following structure is created:

```
/path/to/my-research-area
├── .srrd/
│   ├── config.yaml
│   └── db.sqlite
├── .gitignore
├── README.md
└── work/
    ├── documents/
    ├── logs/
    └── vector_db/
```

- **`.srrd/`**: Contains project-specific configuration and the SQLite database.
- **`.gitignore`**: Ignores the `.srrd/` directory and other temporary files.
- **`README.md`**: A template README file for the project.
- **`work/`**: The main directory for research artifacts.
  - **`documents/`**: For research papers, notes, and other documents.
  - **`logs/`**: Contains logs from the MCP server.
  - **`vector_db/`**: Stores the vector database for semantic search.

## Workflow Intelligence

SRRD-Builder includes a **Workflow Intelligence** feature that provides AI-powered analysis of your research progress. This feature is enabled by default.

### How it Works

- **Tool Logging**: All tool usage is logged to `work/logs/mcp_server.log`.
- **Progress Analysis**: The `srrd status` command analyzes the log file to provide insights and recommendations.
- **Contextual Awareness**: The analysis is aware of the current project and its goals.

### Usage

1. **Initialize a project** and start using the MCP tools.
2. Run `srrd status` to see your progress and get recommendations.

## Global Project Context

SRRD-Builder uses a global project context located at `~/.srrd/globalproject`. This allows you to use the MCP tools from any directory without initializing a project.

- **Default Context**: When no project is active, the global context is used.
- **Initialization**: The global context is automatically initialized on the first run.
- **Switching**: You can switch back to the global context with `srrd reset`.

## Troubleshooting

- **"No such file or directory"**: Make sure you are in the correct project directory.
- **"MCP context not switched"**: Run `srrd switch` manually to switch to the correct context.
- **"Error: Project not initialized"**: Run `srrd init` to initialize a new project.
