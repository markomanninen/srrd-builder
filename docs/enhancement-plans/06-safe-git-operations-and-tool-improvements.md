# Enhancement Plan 06: Safe Git Operations, Current Tool Improvements, and User Guidance

## Overview
This enhancement plan focuses on implementing a safe git MCP tool for basic file version control, improving existing tools, and providing better user guidance with tighter integration for scientific research activities within the SRRD Builder system.

## Core Components

### 1. Basic Git MCP Tool
A simple, safe git tool focused on file version control without complex branch operations or destructive commands.

#### Safe Operations Only
```typescript
interface BasicGitOperations {
  // Read operations
  status(): GitStatus;
  diff(file?: string): string;
  log(limit?: number): GitCommit[];
  
  // Safe file operations
  add(files: string[]): Promise<void>;
  commit(message: string): Promise<void>;
  
  // File history
  fileHistory(file: string): GitCommit[];
  showFile(file: string, commit?: string): string;
}
```

#### What's Included
- Check file status and changes
- View file differences
- Add files to staging area
- Commit changes with messages
- View commit history
- View file content at specific commits

#### What's Excluded (Too Risky/Complex)
- Branch operations (create, switch, merge, delete)
- Remote operations (push, pull, fetch, clone)
- Destructive operations (reset, revert, force operations)
- Repository initialization or configuration changes

### 2. Current Tool Improvements

#### Research Data Management Tools
- **Enhanced Data Validation**: Improve data integrity checks with scientific validation rules
- **Metadata Preservation**: Better handling of research metadata during file operations
- **Version Control Integration**: Seamless integration with the basic git tool
- **Format-Specific Handlers**: Specialized handling for scientific file formats (CSV, JSON, XML)

#### Analysis Tools
- **Statistical Validation**: Built-in statistical checks for research data
- **Data Lineage Tracking**: Track data transformations using git history
- **Research Reproducibility**: Ensure analysis steps are documented in commits
- **Cross-Reference Validation**: Validate relationships between versioned datasets

#### Documentation Tools
- **Auto-Documentation**: Generate documentation and commit automatically
- **Research Journal Integration**: Link documentation with git commit history
- **Methodology Documentation**: Template-driven docs with version tracking

### 3. Enhanced User Guidance

#### Contextual Help System
- **Research Phase Awareness**: Provide guidance based on current research phase
- **Tool Recommendations**: Suggest appropriate tools based on research context
- **Version Control Guidance**: Help users understand when and what to commit
- **Best Practice Prompts**: Proactive suggestions for research best practices

#### Interactive Tutorials
- **Basic Git Workflows**: Simple tutorials for research file versioning
- **Tool-Specific Guidance**: In-context help for each research tool
- **Data Management Training**: Best practices for scientific data versioning
- **Commit Message Guidelines**: Help writing meaningful research commit messages

### 4. Scientific Research Integration

#### Research Activity Recognition
- **Context Detection**: Automatically detect research activities and suggest commits
- **Phase-Specific Versioning**: Recommend versioning strategies by research phase
- **Progress Indicators**: Visual indicators using git history
- **Milestone Tracking**: Use commits to track research milestones

#### File-Focused Collaboration
- **File Change Tracking**: Track who changed what files when
- **Research File Tagging**: Tag commits by research activity type
- **Data Provenance**: Use git history for data provenance tracking

## Advanced Operations Guidance

### CLI Documentation and External Resources
The basic git tool will provide guidance for users who need advanced operations through:

#### Command Line Guidance
```python
def provide_advanced_git_guidance(operation_type: str) -> str:
    """Provide guidance for advanced git operations via CLI"""
    guidance = {
        "branching": {
            "description": "For branch operations, use git CLI directly",
            "commands": [
                "git branch -b feature/my-feature  # Create new branch",
                "git checkout main              # Switch to main branch", 
                "git merge feature/my-feature   # Merge branch"
            ],
            "documentation": "https://git-scm.com/docs/git-branch"
        },
        "remote_operations": {
            "description": "For remote operations, use git CLI directly",
            "commands": [
                "git push origin main           # Push to remote",
                "git pull origin main           # Pull from remote",
                "git fetch --all               # Fetch all remotes"
            ],
            "documentation": "https://git-scm.com/docs/git-push"
        },
        "advanced_history": {
            "description": "For complex history operations, use git CLI with caution",
            "commands": [
                "git rebase -i HEAD~3          # Interactive rebase (CAUTION)",
                "git reset --soft HEAD~1       # Soft reset (safer option)",
                "git reflog                    # View reference log"
            ],
            "documentation": "https://git-scm.com/docs/git-rebase",
            "warning": "⚠️  These operations can be destructive. Always backup your work first."
        }
    }
    return guidance.get(operation_type, {"description": "Refer to official git documentation"})
```

#### Documentation Links Integration
- Link to official Git documentation for each advanced operation
- Provide specific command examples with safety warnings
- Include links to Git best practices for research workflows
- Reference GitLab/GitHub documentation for collaborative features

## Testing Strategy - Following TEST SUITE Guidelines

### Unit Tests - Real Implementation Pattern

**File**: `work/tests/unit/tools/test_basic_git_tool.py`

```python
#!/usr/bin/env python3
"""
Unit Tests for Basic Git Tool
============================

Tests safe git operations following pytest best practices.
Avoids over-mocking and tests real git functionality.
"""
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestBasicGitTool:
    """Test basic git tool functionality with real git operations"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def create_temp_git_repo(self, name: str) -> Path:
        """Create temporary git repository for testing"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix=f"test_git_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        
        # Initialize real git repo
        subprocess.run(["git", "init"], cwd=temp_path, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_path)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_path)
        
        return temp_path

    def test_git_status_with_real_repo(self):
        """Test git status with real repository"""
        from tools.basic_git import BasicGitTool
        
        repo_path = self.create_temp_git_repo("status_test")
        tool = BasicGitTool(repo_path)
        
        # Create test file
        test_file = repo_path / "test.txt"
        test_file.write_text("Initial content")
        
        status = tool.git_status()
        
        assert status["untracked_files"]
        assert "test.txt" in status["untracked_files"]
        assert not status["staged_files"]
        assert not status["modified_files"]

    def test_git_add_and_commit_workflow(self):
        """Test complete add and commit workflow"""
        from tools.basic_git import BasicGitTool
        
        repo_path = self.create_temp_git_repo("add_commit_test")
        tool = BasicGitTool(repo_path)
        
        # Create and add file
        test_file = repo_path / "research_data.csv"
        test_file.write_text("experiment,result\n1,success\n2,failure")
        
        # Test add operation
        result = tool.git_add(["research_data.csv"])
        assert result["success"] is True
        assert "research_data.csv" in result["added_files"]
        
        # Test commit operation
        commit_result = tool.git_commit("Add initial research data")
        assert commit_result["success"] is True
        assert "commit_hash" in commit_result
        assert len(commit_result["commit_hash"]) > 6

    def test_file_history_tracking(self):
        """Test file history functionality with multiple commits"""
        from tools.basic_git import BasicGitTool
        
        repo_path = self.create_temp_git_repo("history_test")
        tool = BasicGitTool(repo_path)
        
        # Create file and make multiple commits
        test_file = repo_path / "analysis.py"
        
        # First commit
        test_file.write_text("# Initial analysis script\nprint('hello')")
        tool.git_add(["analysis.py"])
        tool.git_commit("Initial analysis script")
        
        # Second commit
        test_file.write_text("# Enhanced analysis script\nimport pandas as pd\nprint('enhanced')")
        tool.git_add(["analysis.py"])
        tool.git_commit("Enhanced analysis with pandas")
        
        # Test file history
        history = tool.file_history("analysis.py")
        
        assert len(history) == 2
        assert "Initial analysis script" in [commit["message"] for commit in history]
        assert "Enhanced analysis with pandas" in [commit["message"] for commit in history]

    def test_safety_validations(self):
        """Test safety validations prevent dangerous operations"""
        from tools.basic_git import BasicGitTool
        
        repo_path = self.create_temp_git_repo("safety_test")
        tool = BasicGitTool(repo_path)
        
        # Test file path validation
        with pytest.raises(ValueError, match="Invalid file path"):
            tool.git_add(["../../../etc/passwd"])
        
        # Test repository boundary validation
        with pytest.raises(ValueError, match="File outside repository"):
            tool.show_file("/etc/passwd")
        
        # Test commit message validation
        with pytest.raises(ValueError, match="Empty commit message"):
            tool.git_commit("")
```

### Integration Tests - Real Database and MCP Server Pattern

**File**: `work/tests/integration/test_git_tool_mcp_integration.py`

```python
#!/usr/bin/env python3
"""
Integration Tests for Git Tool MCP Server Integration
===================================================

Tests complete workflow with real MCP server and database.
Follows proven pattern of using temporary directories and real databases.
"""
import pytest
import tempfile
import os
import asyncio
from pathlib import Path

class TestGitToolMCPIntegration:
    """Test git tool integration with MCP server"""

    @pytest.mark.asyncio
    async def test_git_tool_mcp_server_integration(self):
        """Test git tool through MCP server with real database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="computer_science", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Initialize git repository
            import subprocess
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
            
            # Test MCP server git tool integration
            from mcp.server import create_mcp_server
            from tools.basic_git import register_git_tools
            
            server = create_mcp_server()
            register_git_tools(server)
            
            # Test git status through MCP
            status_result = await server.call_tool("git_status", {})
            assert "untracked_files" in status_result
            
            # Create research file and test add/commit workflow
            research_file = Path("research_hypothesis.md")
            research_file.write_text("# Research Hypothesis\n\nQuantum effects influence neural computation.")
            
            # Test add operation through MCP
            add_result = await server.call_tool("git_add", {"files": ["research_hypothesis.md"]})
            assert add_result["success"] is True
            
            # Test commit operation through MCP
            commit_result = await server.call_tool("git_commit", {
                "message": "Add initial research hypothesis"
            })
            assert commit_result["success"] is True
            assert "commit_hash" in commit_result

    @pytest.mark.asyncio
    async def test_git_tool_with_research_workflow(self):
        """Test git tool integration with complete research workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize research project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="biology", template="experimental")
            result = handle_init(args)
            assert result == 0
            
            # Initialize git
            import subprocess
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.name", "Test Researcher"], check=True)
            subprocess.run(["git", "config", "user.email", "researcher@university.edu"], check=True)
            
            # Test research data versioning workflow
            from mcp.server import create_mcp_server
            from tools.basic_git import register_git_tools
            
            server = create_mcp_server()
            register_git_tools(server)
            
            # Create research data files
            data_dir = Path("data")
            data_dir.mkdir()
            
            experimental_data = data_dir / "experiment_001.csv"
            experimental_data.write_text("sample_id,treatment,response\n1,A,0.75\n2,B,0.82")
            
            analysis_script = Path("analysis.py")
            analysis_script.write_text("import pandas as pd\ndf = pd.read_csv('data/experiment_001.csv')")
            
            # Test versioning workflow
            add_result = await server.call_tool("git_add", {
                "files": ["data/experiment_001.csv", "analysis.py"]
            })
            assert add_result["success"] is True
            
            commit_result = await server.call_tool("git_commit", {
                "message": "Add experiment 001 data and analysis script"
            })
            assert commit_result["success"] is True
            
            # Test file history tracking
            history_result = await server.call_tool("file_history", {
                "file": "data/experiment_001.csv"
            })
            assert len(history_result) == 1
            assert "experiment 001" in history_result[0]["message"]
```

## Implementation Strategy

### Phase 1: Basic Git Tool Implementation (Weeks 1-2)
1. **Core Tool Development**
   - Implement safe git operations interface with input validation
   - Create file-focused git workflows with safety checks
   - Add comprehensive error handling and logging
   - Test with real git repositories using pytest patterns

2. **MCP Server Integration**
   - Register git tools with MCP server
   - Implement tool parameter validation
   - Add proper error responses and status codes
   - Test server integration with real database

### Phase 2: CLI and Script Integration (Weeks 3-4)
1. **CLI Commands Enhancement**
   - Update `work/code/cli/commands/` with git tool commands
   - Add `git-status`, `git-add`, `git-commit` CLI interfaces
   - Include help documentation and usage examples
   - Provide guidance links to advanced git operations

2. **Script Updates**
   - Update `scripts/all_mcp_tools_commands.sh` with git tool tests
   - Add comprehensive test scenarios for all git operations
   - Include error case testing and validation scenarios
   - Add performance testing for large file operations

### Phase 3: Frontend Integration (Weeks 5-6)
1. **Tool Database Updates**
   - Add git tools to `work/code/mcp/frontend/data/tool-info.js`
   - Update tool count from 48 to 54 (6 new git tools)
   - Provide comprehensive metadata and usage examples

2. **Research Framework Mapping**
   - Map git tools to appropriate categories in `research-framework.js`
   - Add to **Documentation** and **Data Management** categories
   - Update validation arrays and tool count references

3. **Frontend Parameter Defaults** ⚠️ **CRITICAL**
   - Add parameter defaults to `enhanced-app.js` → `getToolParameterDefaults()`
   - Provide meaningful defaults for all git tool parameters
   - Ensure exact parameter name matching with MCP tool registration

### Phase 4: Advanced Guidance System (Weeks 7-8)
1. **Documentation Integration**
   - Implement guidance system linking to official Git docs
   - Add command examples with safety warnings
   - Create research-specific git workflow documentation
   - Include links to collaborative research practices

2. **Research Workflow Integration**
   - Implement research activity recognition for commit suggestions
   - Add research-specific commit message templates
   - Create data validation with version tracking
   - Build milestone tracking via commits

## Technical Specifications

### Git Tool Interface
```typescript
interface GitTool {
  name: "basic_git";
  description: "Safe git operations for file version control";
  tools: {
    git_status: () => GitStatus;
    git_diff: (file?: string) => string;
    git_log: (limit?: number) => GitCommit[];
    git_add: (files: string[]) => Promise<void>;
    git_commit: (message: string) => Promise<void>;
    file_history: (file: string) => GitCommit[];
    show_file: (file: string, commit?: string) => string;
  };
}
```

### Research Integration
```typescript
interface ResearchGitIntegration {
  autoCommitSuggestions: boolean;
  researchPhaseDetection: boolean;
  commitTemplates: CommitTemplate[];
  fileTypeHandlers: FileTypeHandler[];
}

interface CommitTemplate {
  phase: ResearchPhase;
  template: string;
  requiredFields: string[];
}
```

## Security and Safety

### File-Level Safety
- Only operate on files within the current repository
- Validate file paths before operations
- No operations outside the working directory
- Read-only operations by default

### Input Validation
- Sanitize all file paths and commit messages
- Validate file existence before operations
- Check for binary files before diff operations
- Limit log output to prevent memory issues

### Error Handling
- Graceful handling of git errors
- Clear error messages for users
- No exposure of system-level git errors
- Automatic recovery from common issues

## User Experience

### Simple Interface
- Clear, descriptive operation names
- Minimal required parameters
- Helpful error messages
- Progress indicators for operations

### Research-Focused Workflows
- Commit suggestions based on file changes
- Research phase-aware templates
- Data file-specific handling
- Automatic documentation updates

## Success Metrics

### Safety Metrics
- Zero destructive operations executed
- No repository corruption incidents
- 100% operation success rate within scope
- Clear error reporting for edge cases

### Usability Metrics
- Increased research file versioning adoption
- Reduced git-related user errors
- Improved commit message quality
- Higher user satisfaction with version control

### Integration Metrics
- Seamless tool interoperability
- Consistent research workflow support
- Effective data provenance tracking
- Improved research reproducibility

## Future Considerations

### Potential Extensions
- Integration with research data repositories
- Export to research publication formats
- Advanced file diff for scientific data
- Collaboration features within file scope

### Platform Integration
- Support for discipline-specific file types
- Integration with research metadata standards
- Custom validation rules for different research domains

## CLI and Script Integration Details

### CLI Command Updates

**File**: `work/code/cli/commands/git_commands.py`

```python
#!/usr/bin/env python3
"""
CLI Commands for Basic Git Operations
====================================

Safe git operations with guidance for advanced features.
"""
import click
from srrd_builder.core.git_tool import BasicGitTool

@click.group()
def git():
    """Basic git operations for research file version control"""
    pass

@git.command()
@click.option('--show-help', is_flag=True, help='Show guidance for advanced git operations')
def status(show_help):
    """Show git repository status"""
    tool = BasicGitTool()
    result = tool.git_status()
    
    # Display status
    click.echo(f"Untracked files: {result['untracked_files']}")
    click.echo(f"Modified files: {result['modified_files']}")
    click.echo(f"Staged files: {result['staged_files']}")
    
    if show_help:
        click.echo("\n📖 For advanced git operations:")
        click.echo("• Branch operations: git branch, git checkout, git merge")
        click.echo("• Remote operations: git push, git pull, git fetch")
        click.echo("• Documentation: https://git-scm.com/docs")
```

### Script Integration Updates

**File**: `scripts/all_mcp_tools_commands.sh` (additions)

```bash
#!/bin/bash
# Git Tool Testing Commands - Added to existing script

echo "=== Testing Basic Git Tools ==="

# Git Status Tests
echo "Testing git_status..."
curl -X POST http://localhost:8000/mcp/tools/git_status \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

# Git Add Tests  
echo "Testing git_add with research file..."
curl -X POST http://localhost:8000/mcp/tools/git_add \
  -H "Content-Type: application/json" \
  -d '{"files": ["research_data.csv", "analysis.py"]}' | jq .
```

## Frontend Integration - Complete Implementation

### Tool Information Database Updates

**File**: `work/code/mcp/frontend/data/tool-info.js` (additions)

```javascript
// Add to TOOL_INFO object - update count from 48 to 54 tools

'git_status': {
    title: 'Git Status',
    purpose: 'Check repository status and file changes',
    context: 'Use when you need to see what files have been modified, added, or are untracked in your research project',
    usage: 'Run without parameters to see current repository status',
    examples: [
        'Check current file changes before committing research updates',
        'Verify which experimental data files need to be tracked'
    ],
    tags: ['git', 'version-control', 'file-management', 'research-workflow']
},

'git_add': {
    title: 'Git Add Files',
    purpose: 'Add files to git staging area for commit',
    context: 'Use when you want to stage research files for version control',
    usage: 'Provide array of file paths to add to staging area',
    examples: [
        'Stage experimental data: ["data/experiment_001.csv"]',
        'Stage analysis scripts: ["analysis.py", "visualization.py"]'
    ],
    tags: ['git', 'version-control', 'staging', 'research-data']
}
```

### Frontend Parameter Defaults - CRITICAL

**File**: `work/code/mcp/frontend/enhanced-app.js` (additions to `getToolParameterDefaults()`)

```javascript
// Add to toolParameters object in getToolParameterDefaults function:

'git_status': {
    // No parameters required - empty object
},

'git_add': {
    files: ['research_data.csv', 'analysis.py']
},

'git_commit': {
    message: 'Add experimental data and initial analysis for machine learning study'
}
```

## Success Metrics and Validation

### Quantitative Metrics

- **Safety**: Zero destructive operations executed through tool
- **Coverage**: 100% of basic git operations (status, add, commit, history, show, diff)
- **Integration**: All 6 git tools properly integrated in frontend (54 total tools)
- **Testing**: 100% test coverage for git tool functionality

### Qualitative Metrics

- **User Safety**: Clear guidance for advanced operations
- **Research Integration**: Seamless workflow with research activities
- **Documentation Quality**: Comprehensive help and examples
- **CLI Integration**: Smooth command-line interface experience

### Validation Checklist

- ✅ Git tools registered in MCP server
- ✅ Frontend tool database updated (48 → 54 tools)
- ✅ Research framework categories updated
- ✅ Parameter defaults added to enhanced-app.js
- ✅ CLI commands implemented with help
- ✅ Script testing commands added
- ✅ Unit tests with real git repositories
- ✅ Integration tests with MCP server
- ✅ Documentation with safety guidance
- ✅ Research workflow templates

## Future Considerations

### Advanced Features

- Research-specific commit templates with metadata
- Integration with research data repositories
- Automated backup before git operations
- Data provenance tracking through git history

### Platform Extensions

- Integration with GitLab/GitHub for collaborative research
- Support for large file handling (Git LFS)
- Research paper collaboration workflows
- Citation and reference tracking

## Conclusion

This comprehensive approach provides safe, essential git functionality for research file version control while maintaining safety through restricted operations. The plan includes complete testing coverage, frontend integration, CLI commands, and clear guidance for advanced operations through official documentation. The emphasis on research workflows ensures the tool meets scientific needs without introducing dangerous capabilities.