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
   python3 run_server.py
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
- **Dynamic Tool Discovery**: Automatically discovers all 38+ MCP tools
- **Category Organization**: Tools grouped by research function
- **One-Click Testing**: Run tools with default parameters instantly
- **Custom Parameter Editing**: Full JSON parameter editor with validation

### **📝 Parameter Editor**
- **Modal Interface**: Clean popup editor for tool parameters
- **Template System**: Pre-built parameter templates for each tool
- **JSON Validation**: Real-time syntax checking and error highlighting
- **Smart Defaults**: Intelligent default parameters based on tool requirements

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

### **3. Automated Test Suite**
Click "Run Full Test Suite" or use:
```javascript
// In browser console
const testRunner = new TestSuiteRunner(client);
testRunner.onProgress = (msg) => console.log(msg);
const results = await testRunner.runFullTestSuite();
```

### **4. Performance Testing**
Monitor the "Server Statistics" panel for:
- Response times
- Success rates
- Active connections
- Error frequencies

## 🔍 Test Categories

### **Research Planning Tools**
- `clarify_research_goals`: Socratic questioning for research clarification
- `suggest_methodology`: Research methodology recommendations

### **Quality Assurance Tools**
- `simulate_peer_review`: AI-driven peer review simulation
- `check_quality_gates`: Research quality validation

### **Document Generation Tools**
- `generate_latex_document`: LaTeX document generation
- `format_research_content`: Academic content formatting
- `generate_bibliography`: Citation and bibliography management

### **Search & Discovery Tools**
- `semantic_search`: Intelligent content search
- `discover_patterns`: Research pattern identification
- `extract_key_concepts`: Key concept extraction

### **Storage Management Tools**
- `initialize_project`: Project setup and initialization
- Additional storage and versioning tools

## 📊 Expected Results

### **Successful Test Run**
- All tools should respond without errors
- Response times should be under 5 seconds
- Success rate should be 90%+ for basic functionality
- WebSocket connection should remain stable

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
