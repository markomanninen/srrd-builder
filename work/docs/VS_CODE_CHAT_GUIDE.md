# VS Code Chat Guide: Using SRRD-Builder MCP Tools

## 🎯 Overview

This guide demonstrates how to use all 38 context-aware SRRD-Builder MCP tools through VS Code Chat. The tools automatically detect your project context and work without requiring explicit `project_path` parameters.

## 🚀 Setup Complete

- **Project**: `/tmp/vscode-chat-demo`
- **Domain**: Computer Science
- **MCP Server**: Ready to start
- **Context-Aware**: All tools detect project automatically

## 📋 How to Use This Guide

### Step 1: Configure Claude Desktop

Configure Claude Desktop to use the MCP server:

```bash
# In terminal (from this directory):
srrd configure --claude
```

Then restart Claude Desktop.

### Step 2: Open VS Code Chat

- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Chat: Open Chat"
- Or use the chat icon in the sidebar

### Step 3: Use MCP Tools in Chat

Now you can use any of the 38 SRRD-Builder tools directly in VS Code Chat!

## 🛠️ Available MCP Tools (All Context-Aware)

### 📚 Bibliography Management

Use these tools to manage research literature:

**Store a bibliography reference:**

```txt
@mcp_srrd-builder_store_bibliography_reference
```

- **What it does**: Stores a research paper reference in your project's database
- **Context-aware**: Automatically uses `/tmp/vscode-chat-demo` as project path
- **Example**: Store papers about machine learning, software engineering, etc.

**Retrieve bibliography references:**

```txt
@mcp_srrd-builder_retrieve_bibliography_references
```

- **What it does**: Searches and retrieves stored references
- **Context-aware**: Searches only in your current project's database
- **Example**: Query for "machine learning" to find related papers

**Generate bibliography:**

```txt
@mcp_srrd-builder_generate_bibliography
```

- **What it does**: Creates formatted bibliography from your stored references
- **Context-aware**: Uses references from current project only

### 🔬 Research Planning

Plan and organize your research:

**Clarify research objectives:**

```txt
@mcp_srrd-builder_clarify_research_goals
```

- **What it does**: Helps define and refine research objectives through Socratic questioning
- **Context-aware**: Considers your project's domain (cs)

**Suggest research methodology:**

```txt
@mcp_srrd-builder_suggest_methodology
```

- **What it does**: Recommends appropriate research methods for your goals
- **Context-aware**: Tailored to your project's domain and context

### 📊 Data Management

Organize and analyze research data:

**Extract key concepts:**

```txt
@mcp_srrd-builder_extract_key_concepts
```

- **What it does**: Identifies important concepts from research text
- **Context-aware**: Saves concepts to your project's knowledge base

**Discover patterns:**

```txt
@mcp_srrd-builder_discover_patterns
```

- **What it does**: Finds themes and patterns in research content
- **Context-aware**: Analyzes data within your project scope

**Build knowledge graph:**

```txt
@mcp_srrd-builder_build_knowledge_graph
```

- **What it does**: Creates visual connections between research concepts
- **Context-aware**: Uses your project's stored documents and data

### 📝 Document Generation

Create professional research documents:

**Generate LaTeX document:**

```txt
@mcp_srrd-builder_generate_latex_document
```

- **What it does**: Creates professional LaTeX research papers
- **Context-aware**: Uses your project's bibliography and data

**Generate with database bibliography:**

```txt
@mcp_srrd-builder_generate_document_with_database_bibliography
```

- **What it does**: Creates document with automatically retrieved bibliography
- **Context-aware**: Pulls bibliography from your project's database

**Compile LaTeX to PDF:**

```txt
@mcp_srrd-builder_compile_latex
```

- **What it does**: Converts LaTeX documents to PDF
- **Context-aware**: Outputs to your project's publications folder

### 🔍 Search & Discovery

Find and explore research content:

**Semantic search:**

```txt
@mcp_srrd-builder_semantic_search
```

- **What it does**: Intelligent search across your research documents
- **Context-aware**: Searches only within your project's knowledge base

**Search knowledge base:**

```txt
@mcp_srrd-builder_search_knowledge
```

- **What it does**: Vector-based search through stored research content
- **Context-aware**: Limited to your project's scope

**Find similar documents:**

```txt
@mcp_srrd-builder_find_similar_documents
```

- **What it does**: Finds documents similar to a target document
- **Context-aware**: Searches within your project's document collection

### 🎯 Quality Assurance

Ensure research quality and standards:

**Check quality gates:**

```txt
@mcp_srrd-builder_check_quality_gates
```

- **What it does**: Validates research against quality standards
- **Context-aware**: Uses your project's domain-specific criteria

**Simulate peer review:**

```txt
@mcp_srrd-builder_simulate_peer_review
```

- **What it does**: AI-powered peer review simulation
- **Context-aware**: Considers your project's domain and standards

### 🔄 Version Control

Track and manage research versions:

**Version control operations:**

```txt
@mcp_srrd-builder_version_control
```

- **What it does**: Git operations for research project management
- **Context-aware**: Works with your project's Git repository

**Backup project:**

```txt
@mcp_srrd-builder_backup_project
```

- **What it does**: Creates project backups
- **Context-aware**: Backs up your current project automatically

### 📈 Session Management

Manage research sessions:

**Save research session:**

```txt
@mcp_srrd-builder_save_session
```

- **What it does**: Saves current research session state
- **Context-aware**: Saves to your project's session database

**Restore research session:**

```txt
@mcp_srrd-builder_restore_session
```

- **What it does**: Restores a previous research session
- **Context-aware**: Restores from your project's session history

## 💡 Example VS Code Chat Conversations

### Example 1: Starting a Research Project

```txt
You: I want to start researching machine learning algorithms for recommendation systems.

Response: I'll help you start your research project on ML algorithms for recommendation systems. Let me clarify your research objectives and suggest a methodology.

@mcp_srrd-builder_clarify_research_goals
Research Area: "Machine Learning Algorithms for Recommendation Systems"
Initial Goals: "Investigate current approaches and develop improved algorithms"

@mcp_srrd-builder_suggest_methodology
Research Goals: "Develop improved ML algorithms for recommendation systems"
Domain: "cs"
```

### Example 2: Managing Bibliography

```txt
You: I need to store some research papers about neural networks and then find them later.

Response: I'll help you store and organize your neural network research papers.

@mcp_srrd-builder_store_bibliography_reference
Reference: {
  "title": "Attention Is All You Need",
  "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
  "year": 2017,
  "journal": "NeurIPS",
  "abstract": "The dominant sequence transduction models..."
}

@mcp_srrd-builder_retrieve_bibliography_references
Query: "neural networks attention"
```

### Example 3: Creating Documents

```txt
You: Generate a research paper draft about my findings on recommendation systems.

Response: I'll create a LaTeX research document using your project's bibliography and data.

@mcp_srrd-builder_generate_document_with_database_bibliography
Title: "Advanced Machine Learning Approaches for Recommendation Systems"
Bibliography Query: "recommendation systems machine learning"
Introduction: "This paper presents novel approaches to..."
```

## 🔧 Key Features of Context-Aware Tools

### 1. **Automatic Project Detection**

- Tools automatically detect you're in `/tmp/vscode-chat-demo`
- No need to specify `project_path` parameter
- Environment variables set automatically

### 2. **Database Isolation**

- Each project has its own separate databases
- Your research data stays organized by project
- No cross-contamination between projects

### 3. **Intelligent Defaults**

- Tools use your project's domain (`cs`) for context
- Appropriate templates and standards applied
- Domain-specific recommendations

### 4. **Seamless Integration**

- Works directly in VS Code Chat
- No external tools needed
- Real-time interaction with your research data

## 🎯 Try It Now

1. **Configure Claude Desktop** (if not already done):

   ```bash
   srrd configure --claude
   ```

2. **Restart Claude Desktop** and try this:

   ```txt
   @mcp_srrd-builder_clarify_research_goals
   ```

3. **Follow the prompts** and see how the tool automatically:
   - Detects your project context
   - Uses your project's domain (cs)
   - Saves data to your project's database

## 📊 Tool Categories Summary

| Category                | Tools   | Purpose                        |
| ----------------------- | ------- | ------------------------------ |
| **Bibliography**        | 3 tools | Manage research literature     |
| **Research Planning**   | 8 tools | Plan and organize research     |
| **Data Management**     | 6 tools | Organize and analyze data      |
| **Document Generation** | 6 tools | Create professional documents  |
| **Search & Discovery**  | 4 tools | Find and explore content       |
| **Quality Assurance**   | 4 tools | Ensure research quality        |
| **Version Control**     | 2 tools | Track and manage versions      |
| **Session Management**  | 2 tools | Manage research sessions       |
| **Project Management**  | 3 tools | Initialize and manage projects |

## Total: 38 Context-Aware MCP Tools

## 🚀 Next Steps

1. Try different tools in VS Code Chat
2. Build up your research database
3. Generate professional documents
4. Use the search tools to find connections
5. Maintain quality with review tools

All tools work automatically with your project context - no manual configuration needed!

----

echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "initialize_project", "arguments": {"name": "Database Test Project 2", "description": "Testing database population", "domain": "Computer Science", "project_path": ""}}}' | python3 work/code/mcp/server.py --stdio

echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_research_progress", "arguments": {}}}' | python3 work/code/mcp/mcp_server.py --stdio

echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_research_milestones", "arguments": {"jsonrpc": "2.0", "id": 2,"method": "tools/call","params": {"name": "get_research_milestones","arguments": {}}}}}' | python3 work/code/mcp/mcp_server.py --stdio

echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "switch_project_context", "arguments": {"target_project_path": "/Users/markomanninen/Desktop/test_git_init"}}}' | python3 work/code/mcp/mcp_server.py --stdio
