# Enhanced Frontend Interface for SRRD-Builder MCP Server

This directory contains a modern, comprehensive web-based testing interface for the SRRD-Builder MCP Server with advanced parameter editing capabilities and academic-themed UI.

## 🎨 **New Enhanced Features**

### **🔧 Modular Architecture**
- **Separated Stylesheets**: `styles.css` with academic/scientific theme
- **Modular JavaScript**: `app.js` with comprehensive tool management
- **Clean HTML Structure**: `index.html` as the main entry point
- **Dynamic Tool Discovery**: Automatically loads all available MCP tools

### **⚙️ Advanced Parameter Editing**
- **Modal Parameter Editor**: Edit tool parameters with JSON validation
- **Parameter Templates**: Quick templates (minimal, full, empty) for each tool
- **Real-time Validation**: JSON syntax checking and error reporting
- **Category Filtering**: Tools organized by research categories

### **🎯 Academic UI Theme**
- **Professional Typography**: Inter font family optimized for research interfaces
- **Scientific Color Palette**: Blue-based academic color scheme
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern Interactions**: Smooth animations and intuitive controls

### **WebSocket Integration**
- **Real MCP Protocol**: Uses actual WebSocket connections to MCP server
- **JSON-RPC**: Proper MCP protocol implementation
- **Async Operations**: Non-blocking tool calls and responses
- **Connection Management**: Auto-reconnect and error handling

## 📁 Files

### **index.html**
Main testing interface with:
- Tool testing buttons organized by category
- Real-time output console
- Server status monitoring
- Custom tool parameter input
- Test result export functionality

### **mcp-client.js**
WebSocket client for MCP server communication:
- `MCPClient` class for server communication
- JSON-RPC protocol implementation
- Connection management and error handling
- Tool calling and response handling

### **test-suite.js**
Automated test runner:
- `TestSuiteRunner` class for automated testing
- Comprehensive test cases for all tool categories
- Performance monitoring and reporting
- Error validation and edge case testing

## 🚀 Quick Start

### Method 1: Using VS Code Tasks (Recommended)

1. **Open VS Code Command Palette**: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. **Type**: `Tasks: Run Task`
3. **Select**: `SRRD: Start Frontend Test Server`

This will:
- Start the frontend test server on localhost:8080
- Automatically serve the enhanced interface

### Method 2: Manual Setup

1. **Start the MCP Server**:
   ```bash
   cd work/code/mcp
   python3 web_server.py
   ```

2. **Start the Frontend Server**:
   ```bash
   cd work/code/mcp
   python3 -m http.server 8080 --directory frontend
   ```

3. **Open in Browser**:
   ```bash
   open http://localhost:8080
   ```

## 📁 **File Structure**

```
frontend/
├── index.html              # Enhanced main interface (NEW)
├── styles.css              # Academic theme stylesheet (NEW)
├── app.js                  # Main application logic (NEW)
├── mcp-client.js           # WebSocket MCP client
├── test-suite.js           # Automated test suite
├── index_dynamic.html      # Legacy dynamic interface
├── index_old_backup.html   # Backup of previous version
└── README.md               # This documentation
```

## 🛠️ **Enhanced Testing Features**

### **🎮 Interactive Tool Testing**
- **Dynamic Tool Discovery**: Automatically discovers all 46+ MCP tools
- **Category Organization**: Tools grouped by research function
- **One-Click Testing**: Run tools with default parameters instantly
- **Custom Parameter Editing**: Full JSON parameter editor with validation

### **🚀 Batch Execution System (NEW)**
- **Run All Tools**: Execute all available tools in dependency order with one click
- **Group Execution**: Run tools by research act (Conceptualization, Analysis, etc.)
- **Category Execution**: Run tools by category (Document Generation, Quality Control, etc.)
- **Smart Dependency Management**: Automatic tool ordering based on research workflow
- **Real-time Progress Tracking**: Visual progress bars and current tool indicators
- **Batch Results Summary**: Comprehensive success/failure reporting with detailed statistics

### **📝 Enhanced Parameter Editor**
- **Modal Interface**: Clean popup editor for tool parameters
- **Template System**: Pre-built parameter templates for each tool
- **JSON Validation**: Real-time syntax checking and error highlighting
- **Smart Defaults**: Intelligent default parameters based on tool requirements
- **Auto-retry Logic**: Automatic fallback parameters for failed tool executions

### **📊 Real-time Monitoring**
- **Connection Status**: Live WebSocket connection monitoring
- **Statistics Dashboard**: Success rates, error counts, tool counts
- **Console Logging**: Detailed logs with timestamps and categorization
- **Export Functionality**: Download results and logs as JSON

## 🎯 How to Test Different Scenarios

### **1. Basic Functionality Test**
```javascript
// In browser console
const client = new MCPClient();
await client.connect();
const tools = await client.listTools();
console.log('Available tools:', tools);
```

### **2. Individual Tool Testing**
Click any tool button in the interface or use custom parameters:
```json
{
  "research_area": "quantum computing",
  "experience_level": "graduate",
  "novel_theory_mode": true
}
```

### **3. Batch Execution Testing (NEW)**
**Run All Tools**:
- Click the "🚀 Run All Tools" button in the main toolbar
- Tools execute in proper dependency order automatically
- Real-time progress tracking with visual indicators

**Group Testing**:
- Navigate to Research Acts view
- Click "▶️ Run All Tools" on any research act card
- Or click "▶️ Run Category" on any category card

**Programmatic Batch Execution**:
```javascript
// Run all tools in dependency order
await app.runAllTools();

// Run tools for a specific research act
await app.runToolGroup('act', 'conceptualization');

// Run tools for a specific category
await app.runToolGroup('category', 'document_generation');
```

### **4. Automated Test Suite Integration**
Enhanced test suite with batch execution support:
```javascript
// Traditional test suite
const testRunner = new TestSuiteRunner(client);
testRunner.onProgress = (msg) => console.log(msg);
const results = await testRunner.runFullTestSuite();

// NEW: Group-based testing
const groupResults = await testRunner.runGroupTestSuite('act', 'analysis_synthesis');

// NEW: Dependency-ordered testing
const orderedResults = await testRunner.runDependencyOrderedTests();
```

### **5. Performance Testing & Monitoring**
**Real-time Monitoring**:
- Monitor the "Server Statistics" panel for response times, success rates, active connections, and error frequencies
- Watch batch execution progress with live updates
- Review comprehensive batch summary reports with success/failure statistics

**Batch Performance Analytics**:
- Track execution time for complete tool workflows
- Monitor dependency resolution efficiency  
- Analyze tool failure patterns and retry success rates
- Export batch results for performance analysis

## 🔍 Research Acts & Tool Categories

### **🎯 Conceptualization**
**Goal Setting**: `clarify_research_goals`
**Problem Identification**: `assess_foundational_assumptions`, `generate_critical_questions`
**Critical Thinking**: `compare_approaches`, `initiate_paradigm_challenge`

### **📋 Design & Planning**
**Methodology**: `explain_methodology`, `suggest_methodology`
**Experimental Design**: Planning and design tools
**Ethics Validation**: `ensure_ethics`

### **📚 Knowledge Acquisition**
**Literature Search**: `search_scholarly_articles`, `semantic_search_documents`
**Data Collection**: `find_similar_documents`, `extract_document_sections`
**Source Management**: Document and source organization tools

### **🔬 Analysis & Synthesis**
**Data Analysis**: `discover_patterns`, `build_knowledge_graph`
**Pattern Recognition**: `extract_key_concepts`, `synthesize_findings`
**Semantic Analysis**: Content analysis and interpretation tools
**Knowledge Building**: `generate_research_summary`

### **✅ Validation & Refinement**
**Peer Review**: `simulate_peer_review`
**Quality Control**: `check_quality_gates`
**Paradigm Validation**: `validate_novel_theory`, `evaluate_paradigm_shift_potential`, `cultivate_innovation`

### **📄 Communication & Dissemination**
**Document Generation**: `generate_latex_document`, `generate_document_with_database_bibliography`
**Formatting**: `compile_latex`, `format_research_content`, `generate_bibliography`
**Project Management**: `initialize_project`, `save_session`, `restore_session`, `version_control`
**Workflow Tracking**: `get_research_progress`, `get_workflow_recommendations`, `start_research_session`

## 📊 Expected Results

### **Successful Test Run**
- All tools should respond without errors
- Response times should be under 5 seconds
- Success rate should be 90%+ for basic functionality
- WebSocket connection should remain stable
- **NEW**: Batch execution should complete with proper dependency order
- **NEW**: Group testing should execute all tools in the selected category/act
- **NEW**: Progress tracking should show real-time updates during batch runs

### **Common Issues and Solutions**

**Connection Failed**:
- Ensure MCP server is running on port 8765
- Check for port conflicts
- Verify WebSocket support in browser

**Tool Errors**:
- Check tool parameters match expected schema
- Verify required dependencies are installed
- Review server logs for detailed error messages

**Timeout Issues**:
- Increase timeout values in test configuration
- Check server performance and resource usage
- Verify network connectivity

## 🛠️ Development and Debugging

### **Browser Developer Tools**
- **Console**: View detailed logs and error messages
- **Network**: Monitor WebSocket communication
- **Application**: Inspect local storage and session data

### **Server Logs**
Monitor MCP server output for:
- Tool execution details
- Error stack traces  
- Performance metrics
- Connection status

### **Test Customization**
Modify test parameters in `test-suite.js` to:
- Add new test cases
- Adjust timeout values
- Customize tool parameters
- Add performance benchmarks

## 🎉 Ready for Testing!

The frontend testing interface provides a comprehensive way to:
- ✅ **Validate all MCP tools** through an intuitive web interface
- ✅ **Monitor server performance** in real-time
- ✅ **Export test results** for documentation and reporting
- ✅ **Debug issues** with detailed logging and error handling
- ✅ **Automate testing** with comprehensive test suites

Perfect for development, QA testing, and demonstration purposes! 🚀
