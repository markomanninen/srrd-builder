# Web Interface Dashboard and Project Management - Refined

## Overview

Enhance the existing web interface by building on the current testing framework at `work/code/mcp/frontend/` to create a comprehensive research management dashboard. This plan leverages the existing WebSocket infrastructure, tool categorization, and batch execution system while avoiding redundant implementations.

## Current System Analysis

### Existing Web Interface Infrastructure ✅

**Already Implemented:**
- Complete web server at `work/code/mcp/web_server.py` with Flask backend
- Frontend infrastructure in `work/code/mcp/frontend/` with:
  - `index.html` - Research interface with tool categorization and batch execution
  - `enhanced-app.js` - WebSocket connections and tool execution
  - `enhanced-styles.css` - Professional styling and responsive design
- Tool organization by research acts and categories
- Batch execution system with progress tracking and "Run All Tools" functionality
- WebSocket communication for real-time tool execution
- Professional UI with status indicators and tool count displays

**Current Capabilities:**
- Tool categorization by research acts (🎯), categories (📁), and all tools (🔧)
- Real-time WebSocket communication with MCP server
- Batch tool execution with progress tracking and error handling
- Status monitoring and connection management
- Tool result display and console output
- Professional styling with responsive design

### Existing Infrastructure to Build On:
- `WebSocketHandler` class for MCP protocol communication
- Tool registration and categorization system
- Batch execution with progress tracking and status updates
- Professional CSS styling with consistent design patterns

## Enhancement Strategy - Building on Existing

### 1. Research Analytics Dashboard

**Enhancement**: Add analytics and visualization to existing interface without replacing core functionality

#### Implementation Plan

**File**: `work/code/mcp/frontend/dashboard.html` (new, complementing existing)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder Research Dashboard</title>
    <link rel="stylesheet" href="enhanced-styles.css">
    <link rel="stylesheet" href="dashboard-styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <!-- Reuse existing header structure -->
        <div class="header">
            <h1>Research Analytics Dashboard</h1>
            <div class="view-switcher">
                <button class="btn btn-secondary" onclick="window.location.href='index.html'">
                    🔧 Tool Interface
                </button>
                <button class="btn btn-primary" onclick="refreshDashboard()">
                    🔄 Refresh Data
                </button>
            </div>
        </div>

        <!-- Reuse existing status bar structure -->
        <div class="status-bar">
            <div class="status-info">
                <span class="status-indicator" id="statusIndicator"></span>
                <span class="status-text" id="statusText">Loading Dashboard...</span>
                <span class="project-info" id="projectInfo"></span>
            </div>
        </div>

        <!-- Dashboard Grid using existing CSS classes -->
        <div class="dashboard-grid">
            <!-- Research Progress Card -->
            <div class="card">
                <div class="card-header">
                    <h2>🎯 Research Acts Progress</h2>
                </div>
                <div class="card-content">
                    <canvas id="researchActsChart"></canvas>
                    <div id="progressDetails" class="progress-details"></div>
                </div>
            </div>

            <!-- Tool Usage Analytics Card -->
            <div class="card">
                <div class="card-header">
                    <h2>🔧 Tool Usage Analytics</h2>
                </div>
                <div class="card-content">
                    <canvas id="toolUsageChart"></canvas>
                    <div id="toolStats" class="tool-stats"></div>
                </div>
            </div>

            <!-- Research Timeline Card -->
            <div class="card">
                <div class="card-header">
                    <h2>📅 Research Timeline</h2>
                </div>
                <div class="card-content">
                    <div id="timelineVisualization" class="timeline-viz"></div>
                </div>
            </div>

            <!-- Project Metadata Card -->
            <div class="card">
                <div class="card-header">
                    <h2>📋 Project Information</h2>
                    <button class="btn btn-secondary btn-sm" onclick="editProjectMetadata()">Edit</button>
                </div>
                <div class="card-content">
                    <div id="projectMetadata" class="project-metadata"></div>
                </div>
            </div>
        </div>

        <!-- Reuse existing console for progress messages -->
        <div class="console-container">
            <div class="console-header">
                <h3>Dashboard Activity</h3>
                <button class="btn btn-secondary btn-sm" onclick="clearConsole()">Clear</button>
            </div>
            <div class="console" id="console"></div>
        </div>
    </div>

    <!-- Project Metadata Edit Modal -->
    <div id="metadataModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Edit Project Metadata</h3>
                <span class="close" onclick="closeMetadataModal()">&times;</span>
            </div>
            <div class="modal-body">
                <form id="metadataForm">
                    <div class="form-group">
                        <label for="projectTitle">Project Title:</label>
                        <input type="text" id="projectTitle" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="projectDescription">Description:</label>
                        <textarea id="projectDescription" name="description" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="researchDomain">Research Domain:</label>
                        <select id="researchDomain" name="domain">
                            <option value="physics">Physics</option>
                            <option value="computer_science">Computer Science</option>
                            <option value="biology">Biology</option>
                            <option value="psychology">Psychology</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeMetadataModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Reuse existing enhanced-app.js for WebSocket communication -->
    <script src="enhanced-app.js"></script>
    <script src="dashboard.js"></script>
</body>
</html>
```

**File**: `work/code/mcp/frontend/dashboard.js` (building on existing WebSocket infrastructure)

```javascript
// Dashboard functionality building on existing enhanced-app.js
class ResearchDashboard {
    constructor() {
        // Reuse existing WebSocket connection from enhanced-app.js
        this.wsConnection = null;
        this.charts = {};
        this.initializeDashboard();
    }

    async initializeDashboard() {
        // Reuse existing connection logic from enhanced-app.js
        await this.connectToServer();
        await this.loadDashboardData();
        this.setupEventListeners();
    }

    async connectToServer() {
        // Leverage existing WebSocket connection setup
        if (typeof connectToMCPServer === 'function') {
            await connectToMCPServer();
            this.wsConnection = window.mcpConnection; // Use global connection
        }
    }

    async loadDashboardData() {
        try {
            this.updateStatus("Loading research progress...");
            
            // Use existing tool execution pattern from enhanced-app.js
            const progressData = await this.executeTool('get_research_progress_tool', {});
            const visualData = await this.executeTool('get_visual_progress_summary', {});
            
            this.updateResearchProgress(progressData);
            this.updateToolUsageAnalytics(progressData);
            this.updateProjectMetadata();
            
            this.updateStatus("Dashboard loaded successfully");
        } catch (error) {
            console.error('Dashboard loading failed:', error);
            this.updateStatus("Dashboard loading failed");
        }
    }

    async executeTool(toolName, parameters) {
        // Reuse existing tool execution pattern from enhanced-app.js
        if (typeof executeTool === 'function') {
            return await executeTool(toolName, parameters);
        } else {
            // Fallback to direct WebSocket communication
            return new Promise((resolve, reject) => {
                const message = {
                    jsonrpc: "2.0",
                    id: Date.now(),
                    method: "tools/call",
                    params: {
                        name: toolName,
                        arguments: parameters
                    }
                };
                
                this.wsConnection.send(JSON.stringify(message));
                
                // Handle response (simplified - production would need proper message handling)
                this.wsConnection.onmessage = (event) => {
                    const response = JSON.parse(event.data);
                    if (response.id === message.id) {
                        resolve(response.result);
                    }
                };
            });
        }
    }

    updateResearchProgress(progressData) {
        // Extract research acts progress from existing tool data
        const progressText = progressData.result || progressData;
        const actsProgress = this.parseResearchActsProgress(progressText);
        
        // Create chart using Chart.js
        const ctx = document.getElementById('researchActsChart').getContext('2d');
        
        if (this.charts.researchActs) {
            this.charts.researchActs.destroy();
        }
        
        this.charts.researchActs = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(actsProgress),
                datasets: [{
                    label: 'Completion %',
                    data: Object.values(actsProgress),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Update progress details
        const detailsDiv = document.getElementById('progressDetails');
        detailsDiv.innerHTML = Object.entries(actsProgress)
            .map(([act, progress]) => `
                <div class="progress-item">
                    <span class="act-name">${act.replace('_', ' ').toUpperCase()}</span>
                    <div class="progress-bar-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <span class="progress-value">${progress}%</span>
                    </div>
                </div>
            `).join('');
    }

    parseResearchActsProgress(progressText) {
        // Parse existing tool output to extract progress percentages
        const acts = {
            'conceptualization': 0,
            'design_planning': 0, 
            'implementation': 0,
            'analysis': 0,
            'synthesis': 0,
            'publication': 0
        };

        // Extract progress from existing text-based output
        // This builds on the existing get_research_progress_tool format
        const lines = progressText.split('\n');
        lines.forEach(line => {
            Object.keys(acts).forEach(act => {
                const actPattern = new RegExp(`${act}.*?([0-9]+\.?[0-9]*)%`, 'i');
                const match = line.match(actPattern);
                if (match) {
                    acts[act] = parseFloat(match[1]);
                }
            });
        });

        return acts;
    }

    updateToolUsageAnalytics(progressData) {
        // Extract tool usage patterns from existing progress data
        const toolUsage = this.parseToolUsageData(progressData.result || progressData);
        
        const ctx = document.getElementById('toolUsageChart').getContext('2d');
        
        if (this.charts.toolUsage) {
            this.charts.toolUsage.destroy();
        }
        
        const topTools = Object.entries(toolUsage)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10);
        
        this.charts.toolUsage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topTools.map(([tool]) => tool.replace('_', ' ')),
                datasets: [{
                    label: 'Usage Count',
                    data: topTools.map(([,count]) => count),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Update tool stats
        const statsDiv = document.getElementById('toolStats');
        const totalUsage = Object.values(toolUsage).reduce((a, b) => a + b, 0);
        const uniqueTools = Object.keys(toolUsage).length;
        
        statsDiv.innerHTML = `
            <div class="stat-item">
                <span class="stat-value">${totalUsage}</span>
                <span class="stat-label">Total Tool Uses</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${uniqueTools}</span>
                <span class="stat-label">Unique Tools Used</span>
            </div>
        `;
    }

    parseToolUsageData(progressText) {
        // Parse tool usage from existing progress output
        const toolUsage = {};
        
        // Look for tool usage patterns in the text
        const toolPattern = /(\w+_?\w+).*?(\d+)\s*(?:time|use)/gi;
        let match;
        
        while ((match = toolPattern.exec(progressText)) !== null) {
            const toolName = match[1];
            const count = parseInt(match[2]);
            toolUsage[toolName] = count;
        }
        
        return toolUsage;
    }

    updateStatus(message) {
        // Reuse existing status update pattern
        const statusText = document.getElementById('statusText');
        if (statusText) {
            statusText.textContent = message;
        }
        
        // Add to console like existing interface
        if (typeof addToConsole === 'function') {
            addToConsole(`[Dashboard] ${message}`);
        }
    }

    setupEventListeners() {
        // Setup refresh button
        window.refreshDashboard = () => {
            this.loadDashboardData();
        };
        
        // Setup metadata editing
        window.editProjectMetadata = () => {
            document.getElementById('metadataModal').style.display = 'block';
        };
        
        window.closeMetadataModal = () => {
            document.getElementById('metadataModal').style.display = 'none';
        };
        
        // Handle metadata form submission
        document.getElementById('metadataForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveProjectMetadata();
        });
    }

    async saveProjectMetadata() {
        const formData = new FormData(document.getElementById('metadataForm'));
        const metadata = Object.fromEntries(formData.entries());
        
        try {
            // Use existing tool execution pattern
            await this.executeTool('update_project_metadata', metadata);
            this.updateStatus('Project metadata updated successfully');
            closeMetadataModal();
        } catch (error) {
            console.error('Failed to update metadata:', error);
            this.updateStatus('Failed to update project metadata');
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ResearchDashboard();
});
```

### 2. Enhanced Backend API

**Enhancement**: Extend existing Flask web server with additional endpoints

#### Implementation Plan

**File**: `work/code/mcp/web_server.py` (extend existing)

```python
# Add to existing web_server.py

# Add new routes building on existing Flask app

@app.route('/dashboard')
def dashboard():
    """Serve dashboard interface"""
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/api/project/metadata', methods=['GET', 'POST'])
def project_metadata():
    """Handle project metadata operations"""
    try:
        if request.method == 'GET':
            # Get current project metadata
            current_project = get_current_project_info()
            return jsonify({
                'success': True,
                'metadata': current_project
            })
        
        elif request.method == 'POST':
            # Update project metadata
            metadata = request.json
            result = update_project_metadata(metadata)
            return jsonify({
                'success': True,
                'message': 'Metadata updated successfully'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/analytics/progress')
def get_progress_analytics():
    """Get enhanced progress analytics for dashboard"""
    try:
        # Use existing MCP tool execution
        progress_result = execute_mcp_tool('get_visual_progress_summary', {})
        
        # Parse and structure data for frontend
        analytics_data = parse_progress_data(progress_result)
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_current_project_info():
    """Get current project information using existing utilities"""
    # Leverage existing project detection logic
    from utils.current_project import get_current_project
    
    project_path = get_current_project()
    if not project_path:
        return {'name': 'No Active Project', 'path': None}
    
    # Load project config if available
    import json
    from pathlib import Path
    
    config_file = Path(project_path) / '.srrd' / 'config.json'
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            return {
                'name': config.get('project_name', Path(project_path).name),
                'path': project_path,
                'domain': config.get('domain', 'Unknown'),
                'description': config.get('description', '')
            }
    
    return {
        'name': Path(project_path).name,
        'path': project_path,
        'domain': 'Unknown',
        'description': ''
    }

def execute_mcp_tool(tool_name, parameters):
    """Execute MCP tool using existing infrastructure"""
    # Reuse existing tool execution logic from the web server
    # This builds on the existing WebSocket handler and tool registration
    pass

def parse_progress_data(progress_result):
    """Parse progress data for dashboard consumption"""
    # Extract structured data from existing text-based tool output
    # This builds on the existing get_research_progress_tool output format
    pass
```

### 3. File Management Integration

**Enhancement**: Add simple file browsing to existing interface

#### Implementation Plan

**File**: `work/code/mcp/frontend/files.html` (new page complementing existing interface)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder File Manager</title>
    <link rel="stylesheet" href="enhanced-styles.css">
</head>
<body>
    <div class="container">
        <!-- Reuse existing header structure -->
        <div class="header">
            <h1>Project File Manager</h1>
            <div class="view-switcher">
                <button class="btn btn-secondary" onclick="window.location.href='index.html'">
                    🔧 Tool Interface
                </button>
                <button class="btn btn-secondary" onclick="window.location.href='dashboard.html'">
                    📊 Dashboard
                </button>
            </div>
        </div>

        <!-- File browser using existing card structure -->
        <div class="card">
            <div class="card-header">
                <h2>📁 Project Files</h2>
                <div class="file-actions">
                    <button class="btn btn-secondary btn-sm" onclick="refreshFiles()">Refresh</button>
                    <input type="file" id="fileUpload" multiple style="display: none;" onchange="uploadFiles()">
                    <button class="btn btn-primary btn-sm" onclick="document.getElementById('fileUpload').click()">Upload</button>
                </div>
            </div>
            <div class="card-content">
                <div id="fileList" class="file-list"></div>
            </div>
        </div>

        <!-- File preview using existing console structure -->
        <div class="console-container">
            <div class="console-header">
                <h3>File Preview</h3>
                <button class="btn btn-secondary btn-sm" onclick="clearPreview()">Clear</button>
            </div>
            <div class="console" id="filePreview"></div>
        </div>
    </div>

    <script src="enhanced-app.js"></script>
    <script src="files.js"></script>
</body>
</html>
```

## Testing Strategy - Building on Existing Patterns

### Integration Tests Following Existing Structure

**File**: `work/tests/integration/test_web_dashboard_integration.py`

```python
#!/usr/bin/env python3
"""
Integration Tests for Web Dashboard
================================

Tests web dashboard integration with existing MCP server and tools.
"""
import pytest
import requests
import tempfile
import os
from pathlib import Path

class TestWebDashboardIntegration:
    """Test web dashboard integration"""

    @pytest.fixture
    def web_server_url(self):
        """Provide web server URL - assumes server is running"""
        return "http://localhost:8080"

    def test_dashboard_page_loads(self, web_server_url):
        """Test that dashboard page loads properly"""
        response = requests.get(f"{web_server_url}/dashboard")
        assert response.status_code == 200
        assert "Research Analytics Dashboard" in response.text

    def test_progress_analytics_api(self, web_server_url):
        """Test progress analytics API endpoint"""
        response = requests.get(f"{web_server_url}/api/analytics/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is not None
        
        if data['success']:
            assert 'data' in data

    def test_project_metadata_api(self, web_server_url):
        """Test project metadata API endpoints"""
        # Test GET metadata
        response = requests.get(f"{web_server_url}/api/project/metadata")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('success') is not None
        
        if data['success']:
            metadata = data['metadata']
            assert 'name' in metadata
            assert 'path' in metadata

    @pytest.mark.asyncio
    async def test_dashboard_with_real_project_data(self):
        """Test dashboard with actual project data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="computer_science", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Create some research activity
            from tools.research_planning import clarify_research_goals
            
            await clarify_research_goals(
                research_area="machine learning",
                initial_goals="Optimize neural networks"
            )
            
            # Test that dashboard can access this data
            # (Would require running web server in test environment)
            # This is a placeholder for integration testing
            assert True  # Placeholder assertion
```

## Implementation Phases

### Phase 1: Dashboard Enhancement (2 weeks)

- Create `dashboard.html` building on existing interface structure
- Implement `dashboard.js` using existing WebSocket infrastructure
- Add Chart.js integration for visualizations
- Extend existing Flask server with analytics endpoints

### Phase 2: Project Management Features (1 week)

- Add project metadata editing capabilities
- Implement file browsing using existing card structure
- Create project switching interface
- Build on existing status and console patterns

### Phase 3: Backend API Extensions (1 week)

- Extend existing `web_server.py` with new endpoints
- Add project metadata management
- Implement file system browsing API
- Leverage existing MCP tool execution infrastructure

### Phase 4: Testing and Integration (1 week)

- Create integration tests building on existing patterns
- Test dashboard with real project data
- Performance optimization
- Documentation updates

## Success Metrics

### Quantitative Metrics

- Dashboard loading performance (< 3 seconds)
- Chart rendering accuracy (matches existing tool data)
- API response times (< 500ms)
- Integration test coverage maintaining 100% pass rate

### Qualitative Metrics

- Visual appeal and consistency with existing interface
- User experience quality and navigation
- Data accuracy and usefulness of analytics
- Integration quality with existing tool ecosystem

## Building on Existing Strengths

### Leveraging Current Infrastructure

- **Web Server**: Build on existing Flask server and WebSocket infrastructure
- **Frontend Framework**: Use existing CSS styling and component patterns
- **Tool Integration**: Leverage existing tool execution and batch processing
- **Communication**: Use existing WebSocket protocol and message handling

### Avoiding Redundancy

- **Don't Recreate**: Extend existing web interface rather than replacing
- **Don't Replace**: Build on existing tool categorization and execution
- **Don't Duplicate**: Use existing styling patterns and component structure
- **Don't Over-Engineer**: Add features incrementally to proven interface

## Frontend Integration Implementation Notes

### Tool Integration Status

The dashboard enhancement will build upon the existing frontend framework that already includes:

**Existing Frontend Infrastructure:**

- ✅ **Tool Information Database** (`work/code/mcp/frontend/data/tool-info.js`) - 48 tools with comprehensive metadata
- ✅ **Research Framework** (`work/code/mcp/frontend/data/research-framework.js`) - 6 research acts, categorized tools
- ✅ **Validation System** - Automated tool mapping validation and console logging

**Dashboard Integration Requirements:**

When adding new dashboard features, maintain consistency with existing frontend patterns:

**Tool Visualization:**

- Use existing tool categorization from research framework
- Leverage existing tool metadata for descriptions and help text
- Build upon existing tool count validation (currently 48 tools)

**New Dashboard Tools Integration:**

- Add new dashboard-specific tools to `tool-info.js` with comprehensive metadata
- Map dashboard tools to appropriate research acts in `research-framework.js`
- Update tool count references and validation arrays
- Follow established integration process for frontend validation

**Recommended Process for Dashboard Tools:**

1. Add dashboard tool metadata to `tool-info.js`
2. Map to Communication & Dissemination act, project_management category
3. Update tool count in both frontend files
4. Add to expectedTools validation array
5. Test integration via console validation logs

This refined plan builds systematically on the existing robust web interface while adding dashboard capabilities that integrate seamlessly with the current tool ecosystem and visualization patterns.

This refined plan builds systematically on the existing robust web interface infrastructure while adding sophisticated dashboard and project management capabilities that integrate seamlessly with the current system architecture.
