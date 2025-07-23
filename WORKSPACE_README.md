# SRRD Builder - Quick Start

Welcome to the SRRD Builder development workspace!

## 📚 Essential Documentation

### For AI Agents
- **[Complete AI Agent Guide](work/docs/GUIDE_FOR_AI_AGENTS.md)** - Comprehensive guidelines, principles, and workflows
- **[VS Code Chat Guide](work/docs/VS_CODE_CHAT_GUIDE.md)** - Specific VS Code integration instructions
- **[Claude Research Guide](work/docs/CLAUDE_RESEARCH_GUIDE.md)** - Research-specific guidance

### For Developers
- **[VS Code Development Guide](.vscode/DEVELOPMENT_GUIDE.md)** - VS Code workspace setup and workflows
- **[Work Directory Guide](work/WORK_DIRECTORY_GUIDE.md)** - Project structure overview
- **[Technical Requirements](work/docs/TECHNICAL_REQUIREMENTS.md)** - System requirements and setup

## 🚀 Quick Actions

### Keyboard Shortcuts
- `Ctrl+Shift+G` - Open AI Agent Guide
- `Ctrl+Shift+H` - Open Development Guide
- `Ctrl+Shift+R` - Clean and restart MCP server
- `Ctrl+Shift+T` - Run all tests
- `Ctrl+Shift+K` - Kill all MCP servers
- `Ctrl+Shift+S` - Check MCP server status

### Essential Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- **SRRD: Clean and Restart MCP Server** - Use after code changes
- **SRRD: Run All Tests** - Complete test suite
- **SRRD: Open AI Agent Guide** - Quick access to documentation
- **SRRD: Check MCP Server Status** - Verify server health

## 🎯 Development Workflow

1. **Make Code Changes** - Edit files in `work/code/mcp/` or `srrd_builder/`
2. **Clean Restart MCP** - Use `Ctrl+Shift+R` or the task
3. **Run Tests** - Use `Ctrl+Shift+T` or specific test tasks
4. **Debug if Needed** - Use F5 with debug configurations

## 🔧 Project Structure

```
srrd-builder/
├── .vscode/                 # VS Code configuration
├── work/                    # Main development area
│   ├── code/mcp/           # MCP server implementation
│   ├── docs/               # Documentation
│   └── tests/              # Test suites
├── srrd_builder/           # CLI and server packages
└── scripts/                # Development scripts
```

## 🆘 Need Help?

- Check the **[AI Agent Guide](work/docs/GUIDE_FOR_AI_AGENTS.md)** for comprehensive instructions
- Use the **[Development Guide](.vscode/DEVELOPMENT_GUIDE.md)** for VS Code workflows
- Run tasks via `Ctrl+Shift+P` → "Tasks: Run Task"
- Use debug configurations with F5 for troubleshooting

---
*This workspace is optimized for SRRD Builder development with AI agents and human developers.*
