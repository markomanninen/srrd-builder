# Project Initialization Workflow

## Automatic Context Switching

As of the latest update, **no manual switching is required** when creating new projects through MCP tools. The system automatically handles MCP context switching.

## How It Works

### 1. Via MCP Tools (Claude Desktop/VS Code Chat)

```bash
# User in Claude Desktop:
initialize_project(
  name="Quantum NLP Research",
  description="Research on quantum computing in NLP", 
  domain="computer_science"
)

# Result: 
✅ MCP Context Automatically Switched!
   Claude Desktop is now using this project for all research tools.
```

**What happens automatically:**
- Project directory structure created
- Git repository initialized
- SQLite and vector databases set up
- MCP global launcher reconfigured
- **Context automatically switched** - no manual action needed

### 2. Via CLI Commands

```bash
# Navigate to any directory
cd /path/to/my-research-area

# Initialize SRRD project
srrd init

# Result: MCP context automatically set to this project
# Start using Claude Desktop with MCP tools immediately
```

### 3. Switching Between Projects

```bash
# To switch to an existing project:
cd /path/to/another-project
srrd switch

# Or reset to global context:
srrd reset
```

## Benefits

- **Zero Manual Steps**: Create and immediately use new projects
- **Consistent Experience**: CLI and MCP tools behave identically  
- **Clear Feedback**: Users know when auto-switch succeeds or fails
- **Graceful Fallback**: If auto-switch fails, clear instructions provided

## Implementation Details

The automatic switching is implemented using shared utilities:
- `srrd_builder/utils/launcher_config.py` - Shared launcher configuration
- Used by CLI commands (`init`, `switch`, `reset`) and MCP tools
- Eliminates code duplication and ensures consistent behavior
