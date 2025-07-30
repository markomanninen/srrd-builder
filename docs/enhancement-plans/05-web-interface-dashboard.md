# Web Interface Dashboard and Project Management

## Overview

Create a comprehensive web interface dashboard for the SRRD-Builder system that provides rich visualizations, analytics, project management, and file handling capabilities. This interface extends beyond the current testing web server to become a full-featured research project management platform with cross-platform support.

## Goals

- Provide comprehensive visual analytics and progress tracking dashboards
- Enable full project management with metadata editing and project switching
- Create integrated file explorer with document handling capabilities
- Support text editing and LaTeX generation within the web interface
- Offer database exploration and analytics tools for power users
- Ensure cross-platform compatibility (Windows/macOS/Linux)

## Current State Analysis

### Existing Web Infrastructure

**Current web server** (`work/code/mcp/web_server.py` and `work/code/mcp/frontend/`):
- Basic tool testing interface with categorized tool buttons
- Simple WebSocket connection for MCP tool execution
- Static HTML/CSS/JS implementation for demonstration
- Limited to tool testing and basic result display

**Existing frontend assets**:
- `index.html` - Basic tool testing interface
- `enhanced-app.js` - Tool execution and WebSocket handling
- `enhanced-styles.css` - Basic styling
- `test-suite.js` - Automated tool testing capabilities

### Enhancement Opportunities

**What's Missing**:
- Visual analytics and progress tracking dashboards
- Project management and metadata editing capabilities
- File system integration and document handling
- Database exploration and analytics tools
- Text editing and LaTeX generation interfaces
- Multi-project support with project switching
- Responsive design for different screen sizes

## Features

### 1. Research Analytics Dashboard

**Purpose**: Provide comprehensive visual analytics of research progress and patterns

#### Implementation Plan

**File**: `work/code/mcp/frontend/dashboard/`

```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder Research Dashboard</title>
    <link rel="stylesheet" href="../enhanced-styles.css">
    <link rel="stylesheet" href="dashboard-styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
</head>
<body>
    <div class="dashboard-container">
        <!-- Project Header -->
        <header class="project-header">
            <div class="project-info">
                <h1 id="project-title">Research Project Dashboard</h1>
                <div class="project-metadata">
                    <span id="project-path"></span>
                    <button id="switch-project-btn" class="btn-secondary">Switch Project</button>
                </div>
            </div>
            <div class="dashboard-controls">
                <select id="time-range-selector">
                    <option value="7">Last 7 days</option>
                    <option value="30">Last 30 days</option>
                    <option value="90">Last 90 days</option>
                    <option value="all">All time</option>
                </select>
                <button id="refresh-dashboard" class="btn-primary">Refresh</button>
            </div>
        </header>

        <!-- Main Dashboard Grid -->
        <main class="dashboard-grid">
            <!-- Research Acts Progress -->
            <section class="dashboard-card research-acts-card">
                <h2>Research Acts Progress</h2>
                <div class="progress-visualization">
                    <canvas id="research-acts-chart"></canvas>
                </div>
                <div class="progress-details" id="acts-progress-details"></div>
            </section>

            <!-- Activity Timeline -->
            <section class="dashboard-card timeline-card">
                <h2>Research Activity Timeline</h2>
                <div class="timeline-container">
                    <canvas id="activity-timeline-chart"></canvas>
                </div>
            </section>

            <!-- Tool Usage Analytics -->
            <section class="dashboard-card tools-analytics-card">
                <h2>Tool Usage Analytics</h2>
                <div class="analytics-tabs">
                    <button class="tab-btn active" data-tab="frequency">Frequency</button>
                    <button class="tab-btn" data-tab="effectiveness">Effectiveness</button>
                    <button class="tab-btn" data-tab="patterns">Patterns</button>
                </div>
                <div class="analytics-content">
                    <canvas id="tool-usage-chart"></canvas>
                </div>
            </section>

            <!-- Research Velocity -->
            <section class="dashboard-card velocity-card">
                <h2>Research Velocity</h2>
                <div class="velocity-metrics">
                    <div class="metric">
                        <span class="metric-value" id="daily-velocity">--</span>
                        <span class="metric-label">Tools/Day</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value" id="weekly-velocity">--</span>
                        <span class="metric-label">Progress/Week</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value" id="completion-estimate">--</span>
                        <span class="metric-label">Est. Completion</span>
                    </div>
                </div>
                <canvas id="velocity-trend-chart"></canvas>
            </section>

            <!-- Milestones & Achievements -->
            <section class="dashboard-card milestones-card">
                <h2>Milestones & Achievements</h2>
                <div class="milestones-list" id="milestones-list"></div>
                <button id="add-milestone-btn" class="btn-secondary">Add Milestone</button>
            </section>

            <!-- Research Focus Evolution -->
            <section class="dashboard-card focus-evolution-card">
                <h2>Research Focus Evolution</h2>
                <div class="focus-visualization">
                    <canvas id="focus-evolution-chart"></canvas>
                </div>
                <div class="focus-topics" id="current-focus-topics"></div>
            </section>
        </main>
    </div>

    <script src="dashboard.js"></script>
</body>
</html>
```

**File**: `work/code/mcp/frontend/dashboard/dashboard.js`

```javascript
class ResearchDashboard {
    constructor() {
        this.wsConnection = null;
        this.currentProject = null;
        this.charts = {};
        this.refreshInterval = null;
        
        this.init();
    }
    
    async init() {
        await this.connectWebSocket();
        await this.loadCurrentProject();
        this.setupEventListeners();
        this.startAutoRefresh();
        await this.loadDashboardData();
    }
    
    async loadDashboardData() {
        try {
            // Load comprehensive progress data
            const progressData = await this.callTool('get_comprehensive_progress', {
                include_timeline: true,
                include_recommendations: true,
                format_type: 'detailed'
            });
            
            // Load interaction analytics if available
            const analyticsData = await this.callTool('analyze_research_journey', {
                time_period: this.getSelectedTimeRange(),
                analysis_depth: 'comprehensive'
            });
            
            // Update all dashboard components
            this.updateResearchActsProgress(progressData.research_acts_progress);
            this.updateActivityTimeline(progressData.timeline);
            this.updateToolUsageAnalytics(progressData.tool_usage_analysis);
            this.updateResearchVelocity(progressData.research_velocity);
            this.updateMilestones(progressData.milestones);
            
            if (analyticsData.success) {
                this.updateFocusEvolution(analyticsData.focus_evolution);
            }
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    updateResearchActsProgress(progressData) {
        const ctx = document.getElementById('research-acts-chart').getContext('2d');
        
        if (this.charts.researchActs) {
            this.charts.researchActs.destroy();
        }
        
        this.charts.researchActs = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(progressData),
                datasets: [{
                    label: 'Completion %',
                    data: Object.values(progressData).map(act => act.completion_percentage),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
        
        // Update progress details
        this.updateProgressDetails(progressData);
    }
    
    updateActivityTimeline(timelineData) {
        const ctx = document.getElementById('activity-timeline-chart').getContext('2d');
        
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }
        
        // Process timeline data for chart
        const processedData = this.processTimelineData(timelineData);
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: processedData.labels,
                datasets: [{
                    label: 'Daily Activity',
                    data: processedData.dailyActivity,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Research Activity Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Tools Used'
                        }
                    }
                }
            }
        });
    }
    
    // ... additional chart update methods
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ResearchDashboard();
});
```

### 2. Project Management Interface

**Purpose**: Enable comprehensive project management with metadata editing and project switching

#### Implementation Plan

**File**: `work/code/mcp/frontend/project-manager/project-manager.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder Project Manager</title>
    <link rel="stylesheet" href="../enhanced-styles.css">
    <link rel="stylesheet" href="project-manager-styles.css">
</head>
<body>
    <div class="project-manager-container">
        <header class="project-manager-header">
            <h1>Project Manager</h1>
            <div class="header-actions">
                <button id="new-project-btn" class="btn-primary">New Project</button>
                <button id="import-project-btn" class="btn-secondary">Import Project</button>
            </div>
        </header>

        <main class="project-manager-main">
            <!-- Project List -->
            <section class="projects-section">
                <div class="section-header">
                    <h2>Projects</h2>
                    <div class="project-filters">
                        <input type="text" id="project-search" placeholder="Search projects...">
                        <select id="project-sort">
                            <option value="recent">Recently Used</option>
                            <option value="name">Name A-Z</option>
                            <option value="created">Date Created</option>
                            <option value="progress">Progress</option>
                        </select>
                    </div>
                </div>
                
                <div class="projects-grid" id="projects-grid">
                    <!-- Project cards will be populated here -->
                </div>
            </section>

            <!-- Project Details Panel -->
            <section class="project-details-section" id="project-details-panel">
                <div class="project-details-header">
                    <h2 id="selected-project-name">Select a Project</h2>
                    <div class="project-actions">
                        <button id="edit-metadata-btn" class="btn-secondary">Edit Metadata</button>
                        <button id="switch-to-project-btn" class="btn-primary">Switch to Project</button>
                        <button id="archive-project-btn" class="btn-warning">Archive</button>
                    </div>
                </div>
                
                <div class="project-metadata" id="project-metadata">
                    <!-- Project metadata will be displayed here -->
                </div>
                
                <div class="project-progress" id="project-progress">
                    <!-- Project progress summary will be displayed here -->
                </div>
            </section>
        </main>

        <!-- Project Metadata Editor Modal -->
        <div id="metadata-editor-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit Project Metadata</h3>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <form id="metadata-form">
                        <div class="form-group">
                            <label for="project-title">Project Title</label>
                            <input type="text" id="project-title" name="title" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="project-description">Description</label>
                            <textarea id="project-description" name="description" rows="3"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="research-domain">Research Domain</label>
                            <select id="research-domain" name="domain">
                                <option value="">Select Domain</option>
                                <option value="physics">Physics</option>
                                <option value="biology">Biology</option>
                                <option value="computer_science">Computer Science</option>
                                <option value="psychology">Psychology</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="project-tags">Tags (comma-separated)</label>
                            <input type="text" id="project-tags" name="tags" placeholder="quantum, theory, experimental">
                        </div>
                        
                        <div class="form-group">
                            <label for="project-status">Status</label>
                            <select id="project-status" name="status">
                                <option value="active">Active</option>
                                <option value="on_hold">On Hold</option>
                                <option value="completed">Completed</option>
                                <option value="archived">Archived</option>
                            </select>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" id="cancel-metadata-btn" class="btn-secondary">Cancel</button>
                            <button type="submit" class="btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- New Project Modal -->
        <div id="new-project-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Project</h3>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <form id="new-project-form">
                        <div class="form-group">
                            <label for="new-project-path">Project Path</label>
                            <div class="path-input-group">
                                <input type="text" id="new-project-path" name="path" required>
                                <button type="button" id="browse-path-btn" class="btn-secondary">Browse</button>
                            </div>
                            <small class="form-help">Choose directory for the new research project</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="new-project-name">Project Name</label>
                            <input type="text" id="new-project-name" name="name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="new-project-template">Project Template</label>
                            <select id="new-project-template" name="template">
                                <option value="basic">Basic Research Project</option>
                                <option value="experimental">Experimental Research</option>
                                <option value="theoretical">Theoretical Research</option>
                                <option value="literature_review">Literature Review</option>
                                <option value="thesis">Thesis Project</option>
                            </select>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" id="cancel-new-project-btn" class="btn-secondary">Cancel</button>
                            <button type="submit" class="btn-primary">Create Project</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script src="project-manager.js"></script>
</body>
</html>
```

### 3. File Explorer and Document Management

**Purpose**: Integrated file system browser with document handling capabilities

#### Implementation Plan

**File**: `work/code/mcp/frontend/file-explorer/file-explorer.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder File Explorer</title>
    <link rel="stylesheet" href="../enhanced-styles.css">
    <link rel="stylesheet" href="file-explorer-styles.css">
</head>
<body>
    <div class="file-explorer-container">
        <header class="file-explorer-header">
            <div class="breadcrumb-nav" id="breadcrumb-nav">
                <!-- Breadcrumb navigation will be populated here -->
            </div>
            <div class="file-actions">
                <button id="new-file-btn" class="btn-secondary">New File</button>
                <button id="new-folder-btn" class="btn-secondary">New Folder</button>
                <button id="upload-files-btn" class="btn-primary">Upload Files</button>
            </div>
        </header>

        <main class="file-explorer-main">
            <!-- File Tree Sidebar -->
            <aside class="file-tree-sidebar">
                <div class="sidebar-header">
                    <h3>Project Files</h3>
                    <button id="refresh-tree-btn" class="btn-icon">↻</button>
                </div>
                <div class="file-tree" id="file-tree">
                    <!-- File tree will be populated here -->
                </div>
            </aside>

            <!-- File List and Content Area -->
            <section class="file-content-area">
                <!-- File List -->
                <div class="file-list-container">
                    <div class="file-list-header">
                        <div class="view-controls">
                            <button id="list-view-btn" class="view-btn active">List</button>
                            <button id="grid-view-btn" class="view-btn">Grid</button>
                        </div>
                        <div class="sort-controls">
                            <select id="sort-files-select">
                                <option value="name">Name</option>
                                <option value="modified">Modified</option>
                                <option value="size">Size</option>
                                <option value="type">Type</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="file-list" id="file-list">
                        <!-- File list will be populated here -->
                    </div>
                </div>

                <!-- File Preview/Editor -->
                <div class="file-preview-container" id="file-preview-container">
                    <div class="preview-header">
                        <div class="file-info">
                            <span id="preview-file-name">No file selected</span>
                            <span id="preview-file-size"></span>
                        </div>
                        <div class="preview-actions">
                            <button id="edit-file-btn" class="btn-secondary">Edit</button>
                            <button id="download-file-btn" class="btn-secondary">Download</button>
                            <button id="delete-file-btn" class="btn-warning">Delete</button>
                        </div>
                    </div>
                    
                    <div class="preview-content" id="preview-content">
                        <!-- File preview/editor will be displayed here -->
                    </div>
                </div>
            </section>
        </main>

        <!-- File Upload Modal -->
        <div id="upload-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Upload Files</h3>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="upload-area" id="upload-area">
                        <div class="upload-icon">📁</div>
                        <p>Drag and drop files here or click to select</p>
                        <input type="file" id="file-input" multiple style="display: none;">
                        <button id="select-files-btn" class="btn-primary">Select Files</button>
                    </div>
                    <div class="upload-progress" id="upload-progress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <div class="upload-status" id="upload-status"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Text Editor Modal -->
        <div id="text-editor-modal" class="modal large-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="editor-file-name">Text Editor</h3>
                    <div class="editor-actions">
                        <button id="save-file-btn" class="btn-primary">Save</button>
                        <button id="save-as-btn" class="btn-secondary">Save As</button>
                        <span class="close-modal">&times;</span>
                    </div>
                </div>
                <div class="modal-body">
                    <div class="editor-toolbar">
                        <select id="editor-language">
                            <option value="text">Plain Text</option>
                            <option value="markdown">Markdown</option>
                            <option value="latex">LaTeX</option>
                            <option value="python">Python</option>
                            <option value="javascript">JavaScript</option>
                        </select>
                        <button id="generate-latex-btn" class="btn-secondary">Generate LaTeX</button>
                        <button id="preview-markdown-btn" class="btn-secondary">Preview</button>
                    </div>
                    <div class="editor-container">
                        <textarea id="text-editor" class="code-editor"></textarea>
                        <div id="editor-preview" class="editor-preview" style="display: none;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="file-explorer.js"></script>
</body>
</html>
```

### 4. Database Explorer and Analytics

**Purpose**: Power user interface for exploring database contents and analytics

#### Implementation Plan

**File**: `work/code/mcp/frontend/database-explorer/database-explorer.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRRD-Builder Database Explorer</title>
    <link rel="stylesheet" href="../enhanced-styles.css">
    <link rel="stylesheet" href="database-explorer-styles.css">
</head>
<body>
    <div class="database-explorer-container">
        <header class="database-explorer-header">
            <h1>Database Explorer</h1>
            <div class="database-info">
                <span id="database-path">Loading...</span>
                <button id="refresh-schema-btn" class="btn-secondary">Refresh Schema</button>
            </div>
        </header>

        <main class="database-explorer-main">
            <!-- Database Schema Sidebar -->
            <aside class="schema-sidebar">
                <div class="sidebar-header">
                    <h3>Database Schema</h3>
                    <div class="schema-stats" id="schema-stats">
                        <!-- Table count and stats will be displayed here -->
                    </div>
                </div>
                
                <div class="tables-list" id="tables-list">
                    <!-- Database tables will be listed here -->
                </div>
            </aside>

            <!-- Query and Results Area -->
            <section class="query-results-area">
                <!-- Query Builder -->
                <div class="query-builder-section">
                    <div class="section-header">
                        <h3>Query Builder</h3>
                        <div class="query-actions">
                            <button id="execute-query-btn" class="btn-primary">Execute Query</button>
                            <button id="clear-query-btn" class="btn-secondary">Clear</button>
                            <button id="export-results-btn" class="btn-secondary">Export</button>
                        </div>
                    </div>
                    
                    <div class="query-input-area">
                        <textarea id="sql-query-input" class="sql-editor" placeholder="SELECT * FROM tool_usage ORDER BY timestamp DESC LIMIT 10;"></textarea>
                    </div>
                    
                    <div class="query-builder-visual" id="query-builder-visual">
                        <!-- Visual query builder will be here -->
                    </div>
                </div>

                <!-- Results Display -->
                <div class="results-section">
                    <div class="results-header">
                        <h3>Query Results</h3>
                        <div class="results-info">
                            <span id="results-count">0 rows</span>
                            <span id="execution-time">0ms</span>
                        </div>
                    </div>
                    
                    <div class="results-container" id="results-container">
                        <div class="results-placeholder">
                            Execute a query to see results
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <!-- Pre-built Analytics Queries -->
        <div class="analytics-queries-panel" id="analytics-panel">
            <h3>Analytics Queries</h3>
            <div class="analytics-buttons">
                <button class="analytics-btn" data-query="tool-usage-frequency">Tool Usage Frequency</button>
                <button class="analytics-btn" data-query="research-progress-timeline">Research Progress Timeline</button>
                <button class="analytics-btn" data-query="user-interaction-patterns">User Interaction Patterns</button>
                <button class="analytics-btn" data-query="milestone-achievements">Milestone Achievements</button>
                <button class="analytics-btn" data-query="research-focus-evolution">Research Focus Evolution</button>
                <button class="analytics-btn" data-query="productivity-analysis">Productivity Analysis</button>
            </div>
        </div>

        <!-- Table Details Modal -->
        <div id="table-details-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="table-name">Table Details</h3>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="table-info-tabs">
                        <button class="tab-btn active" data-tab="schema">Schema</button>
                        <button class="tab-btn" data-tab="data">Sample Data</button>
                        <button class="tab-btn" data-tab="stats">Statistics</button>
                    </div>
                    
                    <div class="tab-content">
                        <div id="schema-tab" class="tab-pane active">
                            <table class="schema-table" id="table-schema">
                                <!-- Table schema will be displayed here -->
                            </table>
                        </div>
                        
                        <div id="data-tab" class="tab-pane">
                            <div class="sample-data-container" id="sample-data-container">
                                <!-- Sample data will be displayed here -->
                            </div>
                        </div>
                        
                        <div id="stats-tab" class="tab-pane">
                            <div class="table-statistics" id="table-statistics">
                                <!-- Table statistics will be displayed here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="database-explorer.js"></script>
</body>
</html>
```

## Backend API Extensions

### New Web Server Endpoints

**File**: `work/code/mcp/web_server.py` (additions)

```python
from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import sqlite3
import json
from pathlib import Path

# Project Management Endpoints
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get list of available projects"""
    try:
        # Scan for projects in common locations
        projects = []
        
        # Check ~/Projects directory
        home_projects = Path.home() / 'Projects'
        if home_projects.exists():
            for project_dir in home_projects.iterdir():
                if project_dir.is_dir() and (project_dir / '.srrd').exists():
                    projects.append(get_project_info(project_dir))
        
        # Check current directory and subdirectories
        current_dir = Path.cwd()
        if (current_dir / '.srrd').exists():
            projects.append(get_project_info(current_dir))
        
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects/<project_id>/metadata', methods=['GET', 'PUT'])
def project_metadata(project_id):
    """Get or update project metadata"""
    try:
        project_path = get_project_path_by_id(project_id)
        metadata_file = project_path / '.srrd' / 'metadata.json'
        
        if request.method == 'GET':
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = create_default_metadata(project_path)
            return jsonify({'success': True, 'metadata': metadata})
        
        elif request.method == 'PUT':
            metadata = request.json
            metadata['last_modified'] = datetime.now().isoformat()
            
            os.makedirs(metadata_file.parent, exist_ok=True)
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return jsonify({'success': True, 'metadata': metadata})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# File System Endpoints
@app.route('/api/files/browse', methods=['POST'])
def browse_files():
    """Browse file system directory"""
    try:
        data = request.json
        path = Path(data.get('path', Path.cwd()))
        
        if not path.exists() or not path.is_dir():
            return jsonify({'success': False, 'error': 'Invalid directory path'})
        
        files = []
        directories = []
        
        try:
            for item in path.iterdir():
                if item.is_file():
                    files.append({
                        'name': item.name,
                        'path': str(item),
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime,
                        'type': get_file_type(item)
                    })
                elif item.is_dir():
                    directories.append({
                        'name': item.name,
                        'path': str(item),
                        'modified': item.stat().st_mtime
                    })
        except PermissionError:
            return jsonify({'success': False, 'error': 'Permission denied'})
        
        return jsonify({
            'success': True,
            'path': str(path),
            'parent': str(path.parent) if path.parent != path else None,
            'directories': sorted(directories, key=lambda x: x['name']),
            'files': sorted(files, key=lambda x: x['name'])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files/read', methods=['POST'])
def read_file():
    """Read file content"""
    try:
        data = request.json
        file_path = Path(data['path'])
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({'success': False, 'error': 'File not found'})
        
        # Check file size limit (e.g., 10MB)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'File too large'})
        
        # Determine file type and read accordingly
        file_type = get_file_type(file_path)
        
        if file_type in ['text', 'code', 'markdown', 'latex']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'content': content,
                'type': file_type,
                'size': file_path.stat().st_size
            })
        else:
            return jsonify({'success': False, 'error': 'Binary file not supported for reading'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/files/write', methods=['POST'])
def write_file():
    """Write file content"""
    try:
        data = request.json
        file_path = Path(data['path'])
        content = data['content']
        
        # Create directory if it doesn't exist
        os.makedirs(file_path.parent, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': 'File saved successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Database Explorer Endpoints
@app.route('/api/database/schema', methods=['GET'])
def get_database_schema():
    """Get database schema information"""
    try:
        db_path = get_current_project_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        schema = {}
        for (table_name,) in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            schema[table_name] = {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default_value': col[4],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ],
                'row_count': row_count
            }
        
        conn.close()
        return jsonify({'success': True, 'schema': schema})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/database/query', methods=['POST'])
def execute_database_query():
    """Execute database query"""
    try:
        data = request.json
        query = data['query']
        
        # Basic SQL injection protection (whitelist approach for safety)
        if not is_safe_query(query):
            return jsonify({'success': False, 'error': 'Query not allowed for security reasons'})
        
        db_path = get_current_project_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        start_time = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Convert results to list of dictionaries
        results_list = [dict(row) for row in results]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'results': results_list,
            'row_count': len(results_list),
            'execution_time': round(execution_time, 2)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# LaTeX Generation Endpoint
@app.route('/api/latex/generate', methods=['POST'])
def generate_latex():
    """Generate LaTeX document from content"""
    try:
        data = request.json
        content = data['content']
        template = data.get('template', 'article')
        
        # Use existing document generation tool
        result = call_mcp_tool('generate_document', {
            'content': content,
            'document_type': 'latex',
            'template': template
        })
        
        if result['success']:
            return jsonify({
                'success': True,
                'latex_content': result['data']['document_content'],
                'bibliography': result['data'].get('bibliography', ''),
                'metadata': result['data'].get('metadata', {})
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

## Cross-Platform Considerations

### Path Handling
```javascript
class CrossPlatformPathHandler {
    static normalizePath(path) {
        // Handle Windows vs Unix path separators
        return path.replace(/\\/g, '/');
    }
    
    static isAbsolutePath(path) {
        // Check for absolute paths on different platforms
        return /^([A-Z]:\\|\\\\|\/)/.test(path);
    }
    
    static joinPaths(...parts) {
        return parts.join('/').replace(/\/+/g, '/');
    }
    
    static getParentPath(path) {
        const normalized = this.normalizePath(path);
        const parts = normalized.split('/');
        return parts.slice(0, -1).join('/') || '/';
    }
}
```

### File System Access
```javascript
class FileSystemManager {
    constructor() {
        this.platform = this.detectPlatform();
    }
    
    detectPlatform() {
        // Detect platform from user agent or server response
        if (navigator.platform.indexOf('Win') !== -1) return 'windows';
        if (navigator.platform.indexOf('Mac') !== -1) return 'macos';
        return 'linux';
    }
    
    async browseDirectory(path = null) {
        if (!path) {
            // Use platform-appropriate default paths
            switch (this.platform) {
                case 'windows':
                    path = 'C:\\Users\\' + (await this.getCurrentUser()) + '\\Documents';
                    break;
                case 'macos':
                    path = '/Users/' + (await this.getCurrentUser()) + '/Documents';
                    break;
                default:
                    path = '/home/' + (await this.getCurrentUser());
            }
        }
        
        return await this.callAPI('/api/files/browse', { path });
    }
}
```

## Testing Strategy

### Unit Tests

#### test_web_dashboard.py
```python
import pytest
from unittest.mock import Mock, patch
from work.code.mcp.web_server import app

class TestWebDashboard:
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_dashboard_data_endpoint(self, client):
        """Test dashboard data API endpoint"""
        with patch('work.code.mcp.web_server.call_mcp_tool') as mock_tool:
            mock_tool.return_value = {
                'success': True,
                'data': {
                    'research_acts_progress': {
                        'conceptualization': {'completion_percentage': 75},
                        'design_planning': {'completion_percentage': 50}
                    },
                    'timeline': [
                        {'timestamp': '2024-01-01', 'tool_name': 'clarify_research_goals'},
                        {'timestamp': '2024-01-02', 'tool_name': 'suggest_methodology'}
                    ]
                }
            }
            
            response = client.get('/api/dashboard/data')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success']
            assert 'research_acts_progress' in data['data']
    
    def test_project_metadata_crud(self, client):
        """Test project metadata CRUD operations"""
        # Test GET metadata
        response = client.get('/api/projects/test-project/metadata')
        assert response.status_code == 200
        
        # Test PUT metadata  
        metadata = {
            'title': 'Test Research Project',
            'description': 'A test project for unit testing',
            'domain': 'computer_science',
            'tags': ['testing', 'research']
        }
        
        response = client.put('/api/projects/test-project/metadata', 
                            json=metadata,
                            content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        assert data['metadata']['title'] == metadata['title']
```

#### test_file_explorer.py
```python
import pytest
import tempfile
import os
from pathlib import Path
from work.code.mcp.web_server import app

class TestFileExplorer:
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / 'test_project'
            project_dir.mkdir()
            
            # Create some test files
            (project_dir / 'README.md').write_text('# Test Project')
            (project_dir / 'data.txt').write_text('Test data content')
            (project_dir / 'subdir').mkdir()
            (project_dir / 'subdir' / 'nested.txt').write_text('Nested file content')
            
            yield str(project_dir)
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_browse_files(self, client, temp_project_dir):
        """Test file browsing functionality"""
        response = client.post('/api/files/browse', 
                             json={'path': temp_project_dir},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        
        # Check that files and directories are returned
        files = data['files']
        directories = data['directories']
        
        file_names = [f['name'] for f in files]
        dir_names = [d['name'] for d in directories]
        
        assert 'README.md' in file_names
        assert 'data.txt' in file_names
        assert 'subdir' in dir_names
    
    def test_read_file(self, client, temp_project_dir):
        """Test file reading functionality"""
        file_path = str(Path(temp_project_dir) / 'README.md')
        
        response = client.post('/api/files/read',
                             json={'path': file_path},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        assert data['content'] == '# Test Project'
        assert data['type'] == 'markdown'
    
    def test_write_file(self, client, temp_project_dir):
        """Test file writing functionality"""
        file_path = str(Path(temp_project_dir) / 'new_file.txt')
        content = 'This is new file content'
        
        response = client.post('/api/files/write',
                             json={'path': file_path, 'content': content},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success']
        
        # Verify file was created
        assert Path(file_path).exists()
        assert Path(file_path).read_text() == content
```

### Integration Tests

#### test_dashboard_integration.py
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestDashboardIntegration:
    
    @pytest.fixture
    def driver(self):
        """Setup Selenium WebDriver for integration testing"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for CI
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def web_server(self):
        """Start web server for testing"""
        # Start the web server in test mode
        # This would typically be done with a test fixture or setup
        pass
    
    def test_dashboard_loads(self, driver, web_server):
        """Test that dashboard loads properly"""
        driver.get('http://localhost:8080/dashboard/')
        
        # Wait for dashboard to load
        wait = WebDriverWait(driver, 10)
        dashboard_title = wait.until(
            EC.presence_of_element_located((By.H1, "Research Project Dashboard"))
        )
        
        assert dashboard_title.is_displayed()
        
        # Check for key dashboard components
        progress_chart = driver.find_element(By.ID, "research-acts-chart")
        assert progress_chart.is_displayed()
        
        timeline_chart = driver.find_element(By.ID, "activity-timeline-chart")
        assert timeline_chart.is_displayed()
    
    def test_project_switching(self, driver, web_server):
        """Test project switching functionality"""
        driver.get('http://localhost:8080/dashboard/')
        
        # Click switch project button
        switch_btn = driver.find_element(By.ID, "switch-project-btn")
        switch_btn.click()
        
        # Wait for project manager modal to appear
        wait = WebDriverWait(driver, 10)
        project_modal = wait.until(
            EC.presence_of_element_located((By.ID, "project-manager-modal"))
        )
        
        assert project_modal.is_displayed()
        
        # Check that projects are listed
        projects_grid = driver.find_element(By.ID, "projects-grid")
        project_cards = projects_grid.find_elements(By.CLASS_NAME, "project-card")
        
        assert len(project_cards) > 0
```

## Performance Considerations

### Frontend Optimization
```javascript
// Implement virtual scrolling for large file lists
class VirtualScrollManager {
    constructor(container, itemHeight, renderItem) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.viewportHeight = container.clientHeight;
        this.visibleItems = Math.ceil(this.viewportHeight / itemHeight) + 2;
        
        this.setupScrollListener();
    }
    
    render(items) {
        const scrollTop = this.container.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = Math.min(startIndex + this.visibleItems, items.length);
        
        // Only render visible items
        const visibleItems = items.slice(startIndex, endIndex);
        
        // Update container with visible items
        this.updateContainer(visibleItems, startIndex);
    }
}

// Implement caching for dashboard data
class DashboardCache {
    constructor(ttl = 300000) { // 5 minutes default TTL
        this.cache = new Map();
        this.ttl = ttl;
    }
    
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expires) {
            this.cache.delete(key);
            return null;
        }
        
        return item.data;
    }
    
    set(key, data) {
        this.cache.set(key, {
            data: data,
            expires: Date.now() + this.ttl
        });
    }
}
```

### Backend Optimization
```python
# Implement database connection pooling
class DatabaseConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool = []
        self.pool_size = pool_size
        self.in_use = set()
        
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.pool.append(conn)
    
    def get_connection(self):
        if self.pool:
            conn = self.pool.pop()
            self.in_use.add(conn)
            return conn
        else:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.in_use.add(conn)
            return conn
    
    def return_connection(self, conn):
        if conn in self.in_use:
            self.in_use.remove(conn)
            if len(self.pool) < self.pool_size:
                self.pool.append(conn)
            else:
                conn.close()

# Implement result pagination for large queries
def paginate_query_results(query, page=1, per_page=100):
    """Add pagination to database queries"""
    offset = (page - 1) * per_page
    paginated_query = f"{query} LIMIT {per_page} OFFSET {offset}"
    
    # Also get total count
    count_query = f"SELECT COUNT(*) FROM ({query})"
    
    return paginated_query, count_query
```

## Success Metrics

### Quantitative Metrics
- Dashboard loading performance (< 2 seconds)
- File explorer responsiveness for large directories
- Database query execution time and result rendering
- Cross-platform compatibility testing coverage

### Qualitative Metrics
- User experience quality and intuitiveness
- Visual appeal and design consistency
- Feature completeness and functionality
- Accessibility and responsive design quality

## Implementation Phases

### Phase 1: Core Dashboard Infrastructure
- Implement basic dashboard layout and navigation
- Create research progress visualization components
- Set up WebSocket connections for real-time updates
- Basic project switching functionality

### Phase 2: Project Management Features
- Implement project metadata editing
- Create project creation and import workflows
- Add project search and filtering capabilities
- Project template system

### Phase 3: File Management System
- Implement file explorer with tree view and list view
- Add file upload/download functionality
- Create text editor with syntax highlighting
- LaTeX generation integration

### Phase 4: Database Explorer and Analytics
- Implement database schema exploration
- Create visual query builder
- Add pre-built analytics queries
- Export functionality for query results

### Phase 5: Polish and Optimization
- Performance optimization and caching
- Cross-platform testing and fixes
- Responsive design improvements
- User experience refinements