/**
 * Enhanced SRRD-Builder MCP Frontend Application
 * Implements research acts navigation and comprehensive tool information system
 */

class EnhancedSRRDApp {
    constructor() {
        this.mcpClient = null;
        this.availableTools = []; // Initialize as empty array
        this.currentModal = null;
        this.isConnected = false;
        this.currentView = 'home'; // home, acts, categories, tools
        this.selectedAct = null;
        this.selectedCategory = null;
        this.navigationHistory = [];
        
        // Load external data
        this.framework = window.RESEARCH_FRAMEWORK || {};
        this.toolInfo = window.TOOL_INFO_DATABASE || {};
        
        // Batch execution state
        this.batchExecution = {
            isRunning: false,
            currentTool: null,
            progress: 0,
            results: [],
            totalTools: 0
        };
        
        // Tool dependency and execution order
        this.toolDependencies = this.initializeToolDependencies();
        
        // Test suite integration
        this.testSuite = null;
        
        this.init();
    }

    async init() {
        this.mcpClient = new MCPClient(`ws://localhost:8765?v=${Date.now()}`); // Cache bust
        this.setupEventListeners();
        this.log('Enhanced SRRD Frontend initialized');
        
        // Add cleanup handler to prevent WebSocket errors on page unload
        window.addEventListener('beforeunload', () => {
            if (this.mcpClient && this.isConnected) {
                this.mcpClient.disconnect();
            }
        });
        
        // Try to auto-connect
        setTimeout(() => this.connectToServer(), 1000);
    }

    setupEventListeners() {
        // Connect button
        const connectBtn = document.getElementById('connectBtn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connectToServer());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshTools());
        }

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeModal();
            }
        });

        // View switcher buttons
        const viewButtons = {
            'actsViewBtn': 'acts',
            'categoriesViewBtn': 'categories', 
            'allToolsViewBtn': 'tools'
        };

        Object.entries(viewButtons).forEach(([btnId, view]) => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => this.switchView(view));
            }
        });

        // Batch execution buttons
        const runAllBtn = document.getElementById('runAllToolsBtn');
        if (runAllBtn) {
            runAllBtn.addEventListener('click', () => this.runAllTools());
        }
    }

    initializeToolDependencies() {
        // Define tool execution order and dependencies based on research workflow
        return {
            // Prerequisites - should run first
            prerequisites: ['initialize_project', 'clarify_research_goals'],
            
            // Research workflow order - Complete list of all 46 tools
            executionOrder: [
                // Project setup and initialization
                'initialize_project',
                'clarify_research_goals',
                'start_research_session',
                
                // Problem identification and planning
                'assess_foundational_assumptions',
                'generate_critical_questions',
                'explain_methodology',
                'suggest_methodology',
                'validate_design',
                'ensure_ethics',
                
                // Knowledge acquisition - Literature and search
                'search_knowledge',
                'semantic_search',
                'find_similar_documents',
                'extract_key_concepts',
                'extract_document_sections',
                
                // Source management and bibliography
                'store_bibliography_reference',
                'retrieve_bibliography_references',
                'generate_bibliography',
                
                // Analysis and synthesis
                'build_knowledge_graph',
                'discover_patterns',
                'generate_research_summary',
                
                // Advanced reasoning and theory development
                'compare_approaches',
                'compare_paradigms',
                'initiate_paradigm_challenge',
                'develop_alternative_framework',
                'validate_novel_theory',
                'evaluate_paradigm_shift_potential',
                'cultivate_innovation',
                
                // Quality assurance and validation
                'simulate_peer_review',
                'check_quality_gates',
                
                // Document generation and templates
                'list_latex_templates',
                'generate_latex_document',
                'generate_latex_with_template',
                'generate_document_with_database_bibliography',
                'format_research_content',
                'compile_latex',
                
                // Project management and tracking
                'get_research_progress',
                'get_research_milestones',
                'get_tool_usage_history',
                'get_workflow_recommendations',
                'get_session_summary',
                
                // Session and context management
                'save_session',
                'restore_session',
                'switch_project_context',
                'reset_project_context',
                
                // Version control and backup
                'version_control',
                'backup_project'
            ],
            
            // Tools that depend on others
            dependencies: {
                'generate_bibliography': ['extract_key_concepts'],
                'compile_latex': ['generate_latex_document'],
                'check_quality_gates': ['generate_research_summary'],
                'simulate_peer_review': ['format_research_content']
            }
        };
    }

    async connectToServer() {
        const connectBtn = document.getElementById('connectBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        this.setButtonLoading(connectBtn, 'Connecting...');

        try {
            const initResponse = await this.mcpClient.connect();
            
            // Store server info from initialize response
            if (initResponse && initResponse.serverInfo) {
                this.serverInfo = initResponse.serverInfo;
                this.log(`Server info received: ${JSON.stringify(this.serverInfo)}`, 'info');
            } else if (initResponse && initResponse.result && initResponse.result.serverInfo) {
                this.serverInfo = initResponse.result.serverInfo;
                this.log(`Server info received: ${JSON.stringify(this.serverInfo)}`, 'info');
            } else {
                this.log('No server info received in initialize response', 'warning');
                // Do not set any fallback - let the system get the path dynamically
                this.serverInfo = null;
            }
            
            // Update UI
            statusIndicator.className = 'status-indicator status-connected';
            statusText.textContent = 'Connected';
            connectBtn.textContent = 'Connected ✓';
            connectBtn.disabled = true;
            document.getElementById('refreshBtn').disabled = false;
            document.getElementById('runAllToolsBtn').disabled = false;
            
            this.isConnected = true;
            this.log('Connected to MCP server successfully', 'success');
            
            // Initialize test suite integration
            if (typeof TestSuiteRunner !== 'undefined') {
                this.testSuite = new TestSuiteRunner(this.mcpClient);
                this.testSuite.app = this; // Cross-reference for integration
            }
            
            // Load tools and switch to research acts view
            await this.loadTools();
            this.switchView('acts');
            
        } catch (error) {
            this.log(`Connection failed: ${error.message}`, 'error');
            statusIndicator.className = 'status-indicator status-error';
            statusText.textContent = 'Connection Failed';
            connectBtn.textContent = 'Retry Connection';
            connectBtn.disabled = false;
        }
    }

    async loadTools() {
        try {
            const response = await this.mcpClient.listTools();
            
            // Debug logging to understand the response format
            this.log(`Raw response type: ${typeof response}`, 'info');
            this.log(`Raw response: ${JSON.stringify(response, null, 2)}`, 'info');
            
            // Handle different response formats
            let tools = [];
            if (Array.isArray(response)) {
                tools = response;
            } else if (response && Array.isArray(response.tools)) {
                tools = response.tools;
            } else if (response && response.result && Array.isArray(response.result.tools)) {
                tools = response.result.tools;
            } else {
                this.log('Unexpected tools format received from server', 'warning');
                this.log(`Response: ${JSON.stringify(response, null, 2)}`);
                tools = [];
            }
            
            this.availableTools = tools;
            
            // Debug: Log all available tool names
            const toolNames = tools.map(t => t.name).sort();
            this.log(`Available tools (${toolNames.length}): ${toolNames.join(', ')}`, 'info');
            
            // Debug: Check specifically for bibliography tools
            const bibliographyTools = toolNames.filter(name => name.includes('bibliography') || name.includes('reference'));
            this.log(`Bibliography-related tools found: ${bibliographyTools.join(', ') || 'None'}`, 'info');
            
            // Check for missing optional dependencies and show system status
            this.checkAndDisplaySystemStatus(toolNames);
            
            // Get the working directory from the server
            const workingDir = await this.getWorkingDirectory();
            const pathContext = workingDir ? ` • ${this.extractProjectPath(workingDir)}` : '';
            
            const displayText = `${tools.length} tools available${pathContext}`;
            const toolCountElement = document.getElementById('toolCount');
            toolCountElement.textContent = displayText;
            
            // Add clickable hover tooltip with full project path
            // Always make it clickable, even if workingDir is not available initially
            toolCountElement.style.cursor = 'pointer';
            
            // Remove any existing click listeners to avoid duplicates
            toolCountElement.removeEventListener('click', this._pathClickHandler);
            
            // Create and store the click handler
            this._pathClickHandler = () => {
                const currentWorkingDir = this.serverInfo?.projectPath || workingDir;
                if (currentWorkingDir) {
                    console.log('🔥 COPYING PATH:', currentWorkingDir);
                    navigator.clipboard.writeText(currentWorkingDir).then(() => {
                        this.log(`Copied path to clipboard: ${currentWorkingDir}`, 'success');
                        // Show temporary feedback
                        const originalText = toolCountElement.textContent;
                        toolCountElement.textContent = '📋 Path copied!';
                        setTimeout(() => {
                            toolCountElement.textContent = originalText;
                        }, 1500);
                    }).catch((error) => {
                        console.error('❌ CLIPBOARD ERROR:', error);
                        this.log('Failed to copy path to clipboard', 'error');
                        // Fallback: show path in alert
                        alert(`Path: ${currentWorkingDir}`);
                    });
                } else {
                    console.log('⚠️ NO PATH AVAILABLE TO COPY');
                    this.log('No project path available to copy', 'warning');
                }
            };
            
            // Add the click listener
            toolCountElement.addEventListener('click', this._pathClickHandler);
            
            // Set tooltip
            if (workingDir) {
                toolCountElement.title = `Full project path: ${workingDir} (Click to copy)`;
            } else {
                toolCountElement.title = 'Click to copy project path (when available)';
            }
            
            this.log(`Loaded ${tools.length} tools from server`, 'success');
            
        } catch (error) {
            this.log(`Failed to load tools: ${error.message}`, 'error');
            this.availableTools = []; // Ensure it's always an array
        }
    }

    async getWorkingDirectory() {
        // Get project path from serverInfo received during initialize
        if (this.serverInfo && this.serverInfo.projectPath) {
            return this.serverInfo.projectPath;
        }
        
        return null;
    }

    extractProjectPath(fullPath) {
        if (!fullPath) return '';
        
        // Extract meaningful project context from the path
        const pathParts = fullPath.split('/');
        const relevantParts = [];
        
        // Look for project indicators, working backwards from the end
        let foundProject = false;
        for (let i = pathParts.length - 1; i >= 0; i--) {
            const part = pathParts[i];
            relevantParts.unshift(part);
            
            // Stop when we find a clear project boundary
            if (part.includes('srrd-builder') || part === 'work' || part === 'code' || part === 'mcp') {
                foundProject = true;
                break;
            }
            
            // Don't go too deep
            if (relevantParts.length >= 3) break;
        }
        
        return foundProject ? relevantParts.join('/') : pathParts[pathParts.length - 1] || '';
    }

    switchView(view) {
        // Hide all views
        const views = ['toolsSection', 'researchActsView', 'categoriesView', 'toolsView'];
        views.forEach(viewId => {
            const element = document.getElementById(viewId);
            if (element) element.style.display = 'none';
        });

        // Update button states
        document.querySelectorAll('.view-switcher .btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-secondary');
        });

        const breadcrumb = document.getElementById('breadcrumb');

        switch (view) {
            case 'acts':
                this.currentView = 'acts';
                this.renderResearchActs();
                document.getElementById('researchActsView').style.display = 'block';
                document.getElementById('actsViewBtn').classList.remove('btn-secondary');
                document.getElementById('actsViewBtn').classList.add('btn-primary');
                breadcrumb.style.display = 'none';
                break;
                
            case 'categories':
                if (!this.selectedAct) {
                    this.switchView('acts');
                    return;
                }
                this.currentView = 'categories';
                this.renderCategoriesForAct(this.selectedAct);
                document.getElementById('categoriesView').style.display = 'block';
                document.getElementById('categoriesViewBtn').classList.remove('btn-secondary');
                document.getElementById('categoriesViewBtn').classList.add('btn-primary');
                this.updateBreadcrumb(`${this.framework.acts[this.selectedAct]?.name || 'Unknown Act'}`);
                break;
                
            case 'tools':
                this.currentView = 'tools';
                this.renderAllTools();
                document.getElementById('toolsView').style.display = 'block';
                document.getElementById('allToolsViewBtn').classList.remove('btn-secondary');
                document.getElementById('allToolsViewBtn').classList.add('btn-primary');
                breadcrumb.style.display = 'none';
                break;
                
            default:
                document.getElementById('toolsSection').style.display = 'block';
                breadcrumb.style.display = 'none';
        }
    }

    renderResearchActs() {
        const actsGrid = document.getElementById('actsGrid');
        if (!actsGrid || !this.framework.acts) return;

        const actsHtml = Object.entries(this.framework.acts).map(([actId, act]) => {
            const toolCount = this.getActToolCount(actId);
            return `
                <div class="research-act-card" data-act="${actId}">
                    <div class="act-header" onclick="app.selectResearchAct('${actId}')">
                        <span class="act-icon">${act.icon}</span>
                        <h3 class="act-name">${act.name}</h3>
                    </div>
                    <p class="act-description">${act.description}</p>
                    <div class="act-categories">
                        ${act.categories.length} categories • ${toolCount} tools
                    </div>
                    <div class="act-actions">
                        <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); app.runToolGroup('act', '${actId}')">
                            ▶️ Run All Tools
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        actsGrid.innerHTML = actsHtml;
    }

    selectResearchAct(actId) {
        this.selectedAct = actId;
        this.navigationHistory.push({view: 'acts', actId: null, categoryId: null});
        this.switchView('categories');
    }

    renderCategoriesForAct(actId) {
        const act = this.framework.acts[actId];
        if (!act) return;

        // Update header
        document.getElementById('selectedActTitle').textContent = `${act.icon} ${act.name}`;
        document.getElementById('selectedActDescription').textContent = act.description;

        // Render categories
        const categoriesGrid = document.getElementById('categoriesGrid');
        if (!categoriesGrid) return;

        const categories = act.categories.map(catId => ({
            id: catId,
            ...this.framework.categories[catId]
        })).filter(cat => cat.name); // Filter out undefined categories

        const categoriesHtml = categories.map(category => {
            const availableTools = Array.isArray(this.availableTools) && Array.isArray(category.tools) 
                ? category.tools.filter(toolName => 
                    this.availableTools.some(t => t && t.name === toolName)
                  )
                : [];
            
            return `
                <div class="category-card">
                    <div class="category-header" onclick="app.selectCategory('${category.id}')">
                        <span class="category-icon">${category.icon}</span>
                        <h3>${category.name}</h3>
                    </div>
                    <p>${category.description}</p>
                    <div class="category-stats">
                        ${availableTools.length} tools available
                    </div>
                    <div class="category-actions">
                        <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); app.runToolGroup('category', '${category.id}')">
                            ▶️ Run Category
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        categoriesGrid.innerHTML = categoriesHtml;
    }

    selectCategory(categoryId) {
        this.selectedCategory = categoryId;
        this.navigationHistory.push({view: 'categories', actId: this.selectedAct, categoryId: null});
        this.renderToolsForCategory(categoryId);
        document.getElementById('categoriesView').style.display = 'none';
        document.getElementById('toolsView').style.display = 'block';
        
        const category = this.framework.categories[categoryId];
        if (category) {
            document.getElementById('selectedCategoryTitle').textContent = `${category.icon} ${category.name}`;
            document.getElementById('selectedCategoryDescription').textContent = category.description;
            this.updateBreadcrumb(`${this.framework.acts[this.selectedAct]?.name} › ${category.name}`);
        }
    }

    renderToolsForCategory(categoryId) {
        const category = this.framework.categories[categoryId];
        if (!category) return;

        const toolsGrid = document.getElementById('toolsGrid');
        if (!toolsGrid) return;

        if (!Array.isArray(this.availableTools) || !Array.isArray(category.tools)) {
            toolsGrid.innerHTML = '<p>No tools available for this category.</p>';
            return;
        }

        const categoryTools = category.tools
            .map(toolName => this.availableTools.find(t => t && t.name === toolName))
            .filter(tool => tool); // Filter out undefined tools

        const toolsHtml = categoryTools.map(tool => this.renderEnhancedToolCard(tool, category)).join('');
        toolsGrid.innerHTML = toolsHtml;
    }

    renderAllTools() {
        const toolsGrid = document.getElementById('toolsGrid');
        if (!toolsGrid) return;

        document.getElementById('selectedCategoryTitle').textContent = '🔧 All Tools';
        document.getElementById('selectedCategoryDescription').textContent = 'Complete list of available research tools';

        if (!Array.isArray(this.availableTools)) {
            toolsGrid.innerHTML = '<p>No tools available. Please connect to the server first.</p>';
            return;
        }

        const toolsHtml = this.availableTools.map(tool => {
            if (!tool || !tool.name) return ''; // Skip invalid tools
            
            // Find the category for context
            const categoryEntry = Object.entries(this.framework.categories).find(([_, cat]) => 
                cat.tools && Array.isArray(cat.tools) && cat.tools.includes(tool.name)
            );
            const category = categoryEntry ? categoryEntry[1] : { icon: '🔧', name: 'General' };
            
            return this.renderEnhancedToolCard(tool, category);
        }).filter(html => html).join(''); // Filter out empty strings
        
        toolsGrid.innerHTML = toolsHtml || '<p>No valid tools found.</p>';
    }

    renderEnhancedToolCard(tool, categoryContext) {
        const toolName = tool.name;
        const description = tool.description || 'No description available';
        const formattedName = this.formatToolName(toolName);
        
        return `
            <div class="enhanced-tool-card" data-tool="${toolName}">
                <div class="enhanced-tool-header">
                    <div class="tool-title-section">
                        <span class="enhanced-tool-icon">${categoryContext.icon}</span>
                        <h3 class="enhanced-tool-name">${formattedName}</h3>
                    </div>
                </div>
                <div class="enhanced-tool-description">${description}</div>
                <div class="enhanced-tool-actions">
                    <button class="btn btn-primary btn-tool" onclick="app.runToolWithDefaults('${toolName}')">
                        ▶️ Run Tool
                    </button>
                    <button class="btn btn-secondary" onclick="app.editToolParameters('${toolName}')" title="Edit Parameters">
                        ⚙️ Params
                    </button>
                    <button class="btn btn-info" onclick="app.showToolInfo('${toolName}')" title="Tool Information">
                        ℹ️
                    </button>
                </div>
            </div>
        `;
    }

    showToolInfo(toolName) {
        const toolInfo = this.toolInfo[toolName] || this.getDefaultToolInfo(toolName);
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay tool-info-modal';
        
        modal.innerHTML = `
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">${toolInfo.title}</h3>
                    <p class="modal-subtitle">Research Tool Guide</p>
                </div>
                <div class="modal-body">
                    <div class="info-section">
                        <h4>🎯 What it does</h4>
                        <p>${toolInfo.purpose}</p>
                    </div>
                    
                    <div class="info-section">
                        <h4>🔬 Research Context</h4>
                        <p>${toolInfo.context}</p>
                    </div>
                    
                    <div class="info-section">
                        <h4>💡 How to Use</h4>
                        <p>${toolInfo.usage}</p>
                    </div>
                    
                    <div class="info-section">
                        <h4>📋 Example Applications</h4>
                        <ul class="examples-list">
                            ${toolInfo.examples.map(example => `<li>${example}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="info-section">
                        <div class="context-tags">
                            ${toolInfo.tags.map(tag => `<span class="context-tag">${tag}</span>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" type="button" onclick="app.closeModal()">
                        Got it!
                    </button>
                </div>
            </div>
        `;
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
        
        document.body.appendChild(modal);
        this.currentModal = modal;
    }

    getDefaultToolInfo(toolName) {
        return {
            title: this.formatToolName(toolName),
            purpose: 'This tool provides specialized functionality for scientific research workflows.',
            context: 'Part of the SRRD-Builder suite designed to enhance research productivity and quality.',
            usage: 'Use this tool to enhance your research workflow with AI assistance.',
            examples: ['Enhance research productivity', 'Improve research quality', 'Streamline workflows'],
            tags: ['Research Tool']
        };
    }

    navigateToHome() {
        this.selectedAct = null;
        this.selectedCategory = null;
        this.navigationHistory = [];
        this.switchView('acts');
    }

    navigateBack() {
        if (this.navigationHistory.length > 0) {
            const previous = this.navigationHistory.pop();
            if (previous.view === 'acts') {
                this.navigateToHome();
            } else if (previous.view === 'categories') {
                this.selectedCategory = null;
                this.switchView('categories');
            }
        } else {
            this.navigateToHome();
        }
    }

    updateBreadcrumb(text) {
        const breadcrumb = document.getElementById('breadcrumb');
        const current = document.getElementById('breadcrumbCurrent');
        if (breadcrumb && current) {
            current.textContent = text;
            breadcrumb.style.display = 'block';
        }
    }

    getActToolCount(actId) {
        const act = this.framework.acts[actId];
        if (!act || !act.categories || !Array.isArray(this.availableTools)) return 0;
        
        return act.categories.reduce((count, catId) => {
            const category = this.framework.categories[catId];
            if (category && category.tools && Array.isArray(category.tools)) {
                const availableTools = category.tools.filter(toolName => 
                    this.availableTools.some(t => t && t.name === toolName)
                );
                return count + availableTools.length;
            }
            return count;
        }, 0);
    }

    // Legacy methods for compatibility with existing functionality
    async runToolWithDefaults(toolName) {
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }

        this.log(`🔍 Looking for tool: ${toolName}`, 'info');
        
        // Find the tool to get its schema
        const tool = Array.isArray(this.availableTools) ? 
            this.availableTools.find(t => t && t.name === toolName) : null;
            
        if (!tool) {
            this.log(`❌ Tool ${toolName} not found in available tools`, 'error');
            return;
        }

        this.log(`✅ Found tool: ${tool.name}`, 'info');

        // Generate default parameters for the tool
        let parameters = this.getToolParameters(tool);
        
        try {
            this.log(`� Calling MCP server with parameters: ${JSON.stringify(parameters, null, 2)}`, 'info');
            const result = await this.mcpClient.callTool(toolName, parameters);
            this.log(`✅ ${toolName} completed successfully`, 'success');
            this.log(`Result: ${JSON.stringify(result, null, 2)}`);
        } catch (error) {
            this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
            
            // If the tool failed due to missing required parameters, parse the error and suggest parameters
            if (error.message.includes('Missing required parameters')) {
                const missingParams = this.extractMissingParametersFromError(error.message);
                if (missingParams.length > 0) {
                    this.log(`🔧 Detected missing parameters: ${missingParams.join(', ')}. Retrying with generated values...`, 'info');
                    
                    // Generate parameters based on error message
                    const fallbackParams = this.generateFallbackParameters(missingParams);
                    
                    try {
                        const retryResult = await this.mcpClient.callTool(toolName, fallbackParams);
                        this.log(`✅ ${toolName} completed successfully on retry`, 'success');
                        this.log(`Result: ${JSON.stringify(retryResult, null, 2)}`);
                    } catch (retryError) {
                        this.log(`❌ ${toolName} still failed after retry: ${retryError.message}`, 'error');
                        this.log(`💡 Use the "Params" button to manually configure parameters for this tool`, 'info');
                    }
                } else {
                    this.log(`� Use the "Params" button to configure required fields for this tool`, 'info');
                }
            }
        }
    }

    getToolParameters(tool) {
        // Always try to get default parameters from our verified list first.
        const defaultParams = this.getToolParameterDefaults(tool.name);

        if (defaultParams) {
            return defaultParams;
        }

        // If no defaults are found, and the tool has a schema,
        // we can't proceed, so we return null to open the editor.
        if (tool.inputSchema && Object.keys(tool.inputSchema).length > 0) {
            return null; 
        }
        
        // For tools without a schema and no defaults, return an empty object.
        return {};
    }

    getToolParameterDefaults(toolName) {
        // Get current project path from server if available
        let currentProjectPath;
        
        // Method 1: Try serverInfo
        if (this.serverInfo && this.serverInfo.projectPath) {
            currentProjectPath = this.serverInfo.projectPath;
        } else {
            // Method 2: Extract from UI element (toolCount has the path)
            const toolCountElement = document.getElementById('toolCount');
            if (toolCountElement && toolCountElement.title) {
                const match = toolCountElement.title.match(/Full project path: ([^(]+)/);
                if (match) {
                    currentProjectPath = match[1].trim();
                }
            }
        }
        
        // ALWAYS continue with tool parameter definitions - project path is just one parameter
        // Don't return null even if project path is missing
        
        // === COMPREHENSIVE TOOL PARAMETER DEFINITIONS ===
        // All tools with their correct, validated parameter sets
        const toolParameters = {
            // === TOOLS WITH PROPER SCHEMAS (VALIDATED PARAMETERS) ===
            'clarify_research_goals': {
                research_area: 'machine learning and data science',
                initial_goals: 'To investigate the effectiveness of novel approaches in improving predictive accuracy and interpretability in machine learning systems'
            },
            'suggest_methodology': {
                research_goals: 'To develop and evaluate innovative methodologies for solving complex problems in artificial intelligence and data science',
                domain: 'artificial intelligence'
            },
            'simulate_peer_review': {
                document_content: {
                    title: 'Novel Approaches in AI Research',
                    abstract: 'This paper presents innovative methodologies for advancing artificial intelligence research',
                    content: 'Comprehensive research content focusing on AI methodology and practical applications',
                    methodology: 'Mixed-methods approach with quantitative analysis and qualitative validation'
                },
                domain: 'artificial intelligence'
            },
            'check_quality_gates': {
                research_content: {
                    title: 'AI Methodology Research',
                    phase: 'analysis',
                    content: 'Research content for quality assessment',
                    methodology: 'systematic approach'
                },
                phase: 'analysis'
            },
            'generate_latex_document': {
                title: 'Advanced Research in Artificial Intelligence Applications'
            },
            'compile_latex': {
                tex_file_path: '/project/manuscript/main.tex'
            },
            'semantic_search': {
                query: 'machine learning research methods and applications'
            },
            'discover_patterns': {
                content: 'Comprehensive research text for detailed analysis, evaluation, and systematic processing using advanced computational methods'
            },
            'build_knowledge_graph': {
                documents: ['ai-research-paper.pdf', 'methodology-guide.txt', 'experimental-results.xlsx'],
                relationship_types: ['citation', 'methodology', 'thematic', 'experimental']
            },
            'find_similar_documents': {
                target_document: 'Research document focusing on machine learning applications and methodological innovations in artificial intelligence'
            },
            'extract_key_concepts': {
                text: 'Research text focusing on artificial intelligence methodology, experimental design, and practical applications in scientific domains'
            },
            'generate_research_summary': {
                documents: ['ai-research-paper.pdf', 'methodology-guide.txt', 'experimental-results.xlsx']
                // Note: summary_type and max_length are optional - omit them to use server defaults
            },
            
            // === TOOLS WITH VALIDATED PARAMETER SETS ===
            // All parameters have been tested and verified to work correctly
            'compare_approaches': {
                approach_a: 'Traditional supervised learning approach using established algorithms and conventional feature engineering techniques',
                approach_b: 'Novel deep learning approach utilizing advanced neural network architectures and automated feature learning mechanisms',
                research_context: 'Advanced AI research methodology focusing on practical applications, theoretical foundations, and experimental validation'
            },
            'validate_design': {
                research_design: 'Comprehensive experimental research design investigating the effectiveness of novel machine learning algorithms through systematic evaluation, comparative analysis, and rigorous statistical validation',
                domain: 'artificial intelligence'
            },
            'ensure_ethics': {
                research_proposal: 'A detailed research proposal investigating the effectiveness of novel artificial intelligence methodologies in advancing scientific discovery, improving problem-solving capabilities, and enhancing practical applications across diverse domains',
                domain: 'artificial intelligence'
            },
            'initiate_paradigm_challenge': {
                domain: 'artificial intelligence'
            },
            'generate_critical_questions': {
                research_area: 'machine learning and data science'
            },
            'develop_alternative_framework': {
                domain: 'artificial intelligence',
                current_framework: 'Traditional supervised learning paradigm with manual feature engineering'
            },
            'assess_foundational_assumptions': {
                domain: 'artificial intelligence',
                assumptions: 'Core assumptions about machine learning effectiveness and generalization capabilities'
            },
            'compare_paradigms': {
                mainstream_paradigm: 'Traditional supervised learning paradigm',
                alternative_paradigm: 'Modern deep learning paradigm',
                domain: 'artificial intelligence'
            },
            'validate_novel_theory': {
                theory_framework: 'Novel theoretical framework for AI generalization combining deep learning principles with symbolic reasoning approaches',
                domain: 'artificial intelligence'
            },
            'cultivate_innovation': {
                domain: 'artificial intelligence',
                current_state: 'Established machine learning methodologies'
            },
            'evaluate_paradigm_shift_potential': {
                domain: 'artificial intelligence',
                proposed_shift: 'From traditional ML to advanced AI systems',
                theory_framework: 'Novel theoretical framework for AI generalization combining deep learning principles with symbolic reasoning approaches'
            },
            'explain_methodology': {
                research_question: 'How can mixed-methods research approach combining quantitative analysis and qualitative insights improve AI research effectiveness?',
                domain: 'artificial intelligence'
            },
            'initialize_project': {
                name: 'AI Research Project',
                description: 'Comprehensive AI research project',
                domain: 'artificial intelligence',
                project_path: currentProjectPath || ''
            },
            'save_session': {
                session_data: {
                    session_id: 'session_001',
                    timestamp: new Date().toISOString(),
                    user: 'researcher',
                    project: 'ai_research'
                },
                project_path: currentProjectPath || ''
            },
            'search_knowledge': {
                query: 'machine learning research methods',
                project_path: currentProjectPath || ''
            },
            'version_control': {
                action: 'commit',
                message: 'Add research findings and analysis',
                project_path: currentProjectPath || ''
            },
            'backup_project': {
                project_path: currentProjectPath || ''
            },
            'restore_session': {
                session_id: 1,
                project_path: currentProjectPath || ''
            },
            'format_research_content': {
                content: 'Research content for formatting',
                content_type: 'academic_section',
                formatting_style: 'academic'
            },
            'generate_bibliography': {
                references: [
                    {'title': 'AI Research Methods', 'author': 'Smith, J.', 'year': 2024, 'journal': 'AI Journal'}
                ]
            },
            'extract_document_sections': {
                document_content: 'Comprehensive research document with multiple sections for analysis'
            },
            'store_bibliography_reference': {
                reference: {
                    'title': 'Advanced AI Techniques',
                    'author': 'Johnson, M.',
                    'year': 2024,
                    'journal': 'Machine Learning Review'
                }
            },
            'retrieve_bibliography_references': {
                query: 'machine learning artificial intelligence',
                max_results: 20
            },
            'generate_document_with_database_bibliography': {
                title: 'Advanced AI Research Document',
                bibliography_query: 'machine learning deep learning AI'
            },
            'list_latex_templates': {
                // This tool has empty schema and may not need parameters
            },
            'generate_latex_with_template': {
                template_name: 'academic_paper',
                title: 'AI Research Paper',
                content: 'Research content for LaTeX generation'
            },
            'get_research_progress': {
                project_path: currentProjectPath || ''
            },
            'get_tool_usage_history': {
                project_path: currentProjectPath || ''
            },
            'get_workflow_recommendations': {
                project_path: currentProjectPath || ''
            },
            'get_research_milestones': {
                project_path: currentProjectPath || ''
            },
            'start_research_session': {
                project_path: currentProjectPath || ''
            },
            'get_session_summary': {
                project_path: currentProjectPath || ''
            }
        };
        
        return toolParameters[toolName] || null;
    }

    extractMissingParametersFromError(errorMessage) {
        // Parse error messages like:
        // "Missing required parameters (approach_a, approach_b, research_context)"
        // "Missing required parameter (domain)"
        // "Error: Missing required parameter (research_area)"
        
        let match = errorMessage.match(/Missing required parameters? \(([^)]+)\)/);
        if (match) {
            return match[1].split(',').map(param => param.trim());
        }
        
        // Also handle cases where the error is wrapped with "Error: "
        match = errorMessage.match(/Error: Missing required parameters? \(([^)]+)\)/);
        if (match) {
            return match[1].split(',').map(param => param.trim());
        }
        
        return [];
    }

    generateFallbackParameters(parameterNames) {
        const parameters = {};
        parameterNames.forEach(paramName => {
            // Use the smart example value system
            parameters[paramName] = this.getExampleValue(paramName, 'string');
        });
        return parameters;
    }

    async runAllTools() {
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }

        if (this.batchExecution.isRunning) {
            this.log('Batch execution already in progress', 'warning');
            return;
        }

        const availableToolNames = this.availableTools.map(t => t.name);
        const toolsToRun = this.toolDependencies.executionOrder.filter(toolName => 
            availableToolNames.includes(toolName)
        );

        if (toolsToRun.length === 0) {
            this.log('No tools available to run', 'warning');
            return;
        }

        this.startBatchExecution(toolsToRun);
    }

    async runToolGroup(groupType, groupValue) {
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }

        if (this.batchExecution.isRunning) {
            this.log('Batch execution already in progress', 'warning');
            return;
        }

        let toolsToRun = [];

        if (groupType === 'act') {
            // Get all tools for a research act
            const categories = Object.values(this.framework.categories).filter(cat => cat.act === groupValue);
            toolsToRun = categories.flatMap(cat => cat.tools);
        } else if (groupType === 'category') {
            // Get all tools for a category
            const category = this.framework.categories[groupValue];
            if (category) {
                toolsToRun = category.tools;
            }
        }

        // Debug: Log what tools are expected for this group
        this.log(`Expected tools for ${groupType} '${groupValue}': ${toolsToRun.join(', ')}`, 'info');
        
        // Filter to only available tools and order by dependencies
        const availableToolNames = this.availableTools.map(t => t.name);
        const originalToolCount = toolsToRun.length;
        const originalToolList = [...toolsToRun]; // Copy before filtering
        
        toolsToRun = this.orderToolsByDependencies(toolsToRun.filter(toolName => 
            availableToolNames.includes(toolName)
        ));

        // Debug: Log filtering results
        this.log(`After filtering: ${toolsToRun.length}/${originalToolCount} tools available`, 'info');
        if (toolsToRun.length !== originalToolCount) {
            const missingTools = originalToolList.filter(tool => !availableToolNames.includes(tool));
            this.log(`Missing tools: ${missingTools.join(', ') || 'None'}`, 'warning');
            
            // Check if missing tools have known dependency issues
            const dependencyHints = this.getDependencyHints(missingTools);
            if (dependencyHints.length > 0) {
                this.log(`💡 Dependency hints:\n${dependencyHints.join('\n')}`, 'info');
            }
        }

        if (toolsToRun.length === 0) {
            // Enhanced error messaging with dependency hints
            const dependencyHints = this.getDependencyHints(originalToolList);
            let message = `No tools available to run for ${groupType}: ${groupValue}`;
            
            if (dependencyHints.length > 0) {
                message += `\n\n💡 Possible causes:\n${dependencyHints.join('\n')}`;
                this.log(message, 'warning');
                this.showDependencyModal(groupType, groupValue, originalToolList, dependencyHints);
            } else {
                this.log(message, 'warning');
            }
            return;
        }

        this.log(`Running ${toolsToRun.length} tools for ${groupType}: ${groupValue}`, 'info');
        this.startBatchExecution(toolsToRun);
    }

    orderToolsByDependencies(tools) {
        // Order tools based on execution order and dependencies
        const ordered = [];
        const executionOrder = this.toolDependencies.executionOrder;
        
        // Add tools in execution order
        for (const toolName of executionOrder) {
            if (tools.includes(toolName) && !ordered.includes(toolName)) {
                ordered.push(toolName);
            }
        }
        
        // Add any remaining tools
        for (const toolName of tools) {
            if (!ordered.includes(toolName)) {
                ordered.push(toolName);
            }
        }
        
        return ordered;
    }

    async startBatchExecution(toolsToRun) {
        this.batchExecution = {
            isRunning: true,
            currentTool: null,
            progress: 0,
            results: [],
            totalTools: toolsToRun.length
        };

        this.updateBatchProgressUI();
        this.log(`Starting batch execution of ${toolsToRun.length} tools`, 'info');

        for (let i = 0; i < toolsToRun.length; i++) {
            const toolName = toolsToRun[i];
            this.batchExecution.currentTool = toolName;
            this.batchExecution.progress = Math.round((i / toolsToRun.length) * 100);
            
            this.updateBatchProgressUI();
            this.log(`Running tool ${i + 1}/${toolsToRun.length}: ${toolName}`, 'info');

            try {
                const result = await this.runToolForBatch(toolName);
                this.batchExecution.results.push({
                    tool: toolName,
                    success: true,
                    result: result,
                    timestamp: new Date().toISOString()
                });
                this.log(`✅ ${toolName} completed successfully`, 'success');
            } catch (error) {
                this.batchExecution.results.push({
                    tool: toolName,
                    success: false,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
                this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
            }

            // Small delay between tools
            await this.delay(1000);
        }

        this.completeBatchExecution();
    }

    async runToolForBatch(toolName) {
        const tool = this.availableTools.find(t => t && t.name === toolName);
        if (!tool) {
            throw new Error(`Tool ${toolName} not found`);
        }

        const parameters = this.getToolParameters(tool) || {};
        return await this.mcpClient.callTool(toolName, parameters);
    }

    completeBatchExecution() {
        this.batchExecution.isRunning = false;
        this.batchExecution.currentTool = null;
        this.batchExecution.progress = 100;
        
        this.updateBatchProgressUI();
        
        const successCount = this.batchExecution.results.filter(r => r.success).length;
        const totalCount = this.batchExecution.results.length;
        
        this.log(`Batch execution completed: ${successCount}/${totalCount} tools succeeded`, 
                 successCount === totalCount ? 'success' : 'warning');
        
        this.showBatchSummary();
    }

    updateBatchProgressUI() {
        const progressContainer = document.getElementById('batchProgress');
        if (!progressContainer) return;

        if (this.batchExecution.isRunning) {
            progressContainer.style.display = 'block';
            progressContainer.innerHTML = `
                <div class="batch-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${this.batchExecution.progress}%"></div>
                    </div>
                    <div class="progress-text">
                        ${this.batchExecution.currentTool ? `Running: ${this.batchExecution.currentTool}` : 'Preparing...'}
                        (${this.batchExecution.progress}%)
                    </div>
                </div>
            `;
        } else {
            progressContainer.style.display = 'none';
        }
    }

    showBatchSummary() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const successCount = this.batchExecution.results.filter(r => r.success).length;
        const failCount = this.batchExecution.results.filter(r => !r.success).length;
        
        const resultsList = this.batchExecution.results.map(result => `
            <div class="batch-result-item ${result.success ? 'success' : 'error'}">
                <span class="result-icon">${result.success ? '✅' : '❌'}</span>
                <span class="result-tool">${result.tool}</span>
                <span class="result-message">${result.success ? 'Success' : result.error}</span>
            </div>
        `).join('');

        modal.innerHTML = `
            <div class="modal batch-summary-modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">Batch Execution Summary</h3>
                    <p class="modal-subtitle">Completed ${this.batchExecution.totalTools} tools</p>
                </div>
                <div class="modal-body">
                    <div class="batch-stats">
                        <div class="stat-item success">
                            <span class="stat-number">${successCount}</span>
                            <span class="stat-label">Successful</span>
                        </div>
                        <div class="stat-item error">
                            <span class="stat-number">${failCount}</span>
                            <span class="stat-label">Failed</span>
                        </div>
                    </div>
                    <div class="batch-results-list">
                        ${resultsList}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" type="button" onclick="app.closeModal()">
                        Close
                    </button>
                </div>
            </div>
        `;

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        document.body.appendChild(modal);
        this.currentModal = modal;
    }

    checkAndDisplaySystemStatus(availableToolNames) {
        // Define expected optional tools
        const optionalTools = [
            'store_bibliography_reference',
            'retrieve_bibliography_references', 
            'semantic_search',
            'build_knowledge_graph'
        ];
        
        const missingOptionalTools = optionalTools.filter(tool => !availableToolNames.includes(tool));
        
        if (missingOptionalTools.length > 0) {
            const dependencyInfo = this.getDependencyHints(missingOptionalTools);
            
            // Show subtle status indicator
            const statusText = document.getElementById('statusText');
            if (statusText) {
                statusText.innerHTML = `Connected <span style="color: #f59e0b; font-size: 0.8em;">⚠️ ${missingOptionalTools.length} optional features unavailable</span>`;
                statusText.title = `Missing optional tools: ${missingOptionalTools.join(', ')}\nClick for details`;
                statusText.style.cursor = 'pointer';
                
                // Add click handler for system status
                statusText.onclick = () => {
                    this.showSystemStatusModal(missingOptionalTools, dependencyInfo);
                };
            }
            
            this.log(`📊 System Status: ${availableToolNames.length} tools available, ${missingOptionalTools.length} optional features unavailable`, 'info');
        } else {
            const statusText = document.getElementById('statusText');
            if (statusText) {
                statusText.textContent = 'Connected • All features available';
                statusText.style.color = '#10b981';
            }
            this.log(`📊 System Status: All ${availableToolNames.length} tools available - full functionality enabled`, 'success');
        }
    }

    showSystemStatusModal(missingTools, dependencyInfo) {
        this.showDependencyModal('system', 'optional features', missingTools, dependencyInfo);
    }

    getDependencyHints(missingTools) {
        const hints = [];
        const toolDependencies = {
            'store_bibliography_reference': {
                dependency: 'Vector Database',
                solution: 'Reinstall: sh setup.sh --with-vector-database',
                optional: true
            },
            'retrieve_bibliography_references': {
                dependency: 'Vector Database', 
                solution: 'Reinstall: sh setup.sh --with-vector-database',
                optional: true
            },
            'semantic_search': {
                dependency: 'Vector Database',
                solution: 'Reinstall: sh setup.sh --with-vector-database',
                optional: true
            },
            'build_knowledge_graph': {
                dependency: 'Graph Database or Vector DB',
                solution: 'Reinstall: sh setup.sh --with-vector-database',
                optional: true
            }
        };

        const dependencyGroups = {};
        
        missingTools.forEach(tool => {
            const depInfo = toolDependencies[tool];
            if (depInfo) {
                if (!dependencyGroups[depInfo.dependency]) {
                    dependencyGroups[depInfo.dependency] = {
                        tools: [],
                        solution: depInfo.solution,
                        optional: depInfo.optional
                    };
                }
                dependencyGroups[depInfo.dependency].tools.push(tool);
            }
        });

        Object.entries(dependencyGroups).forEach(([dependency, info]) => {
            const toolList = info.tools.join(', ');
            const optionalText = info.optional ? ' (optional feature)' : '';
            hints.push(`• Missing ${dependency}${optionalText} required for: ${toolList}`);
            hints.push(`  Solution: ${info.solution}`);
        });

        return hints;
    }

    showDependencyModal(groupType, groupValue, missingTools, hints) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const toolsList = missingTools.join(', ');
        const hintsHtml = hints.map(hint => 
            hint.startsWith('•') ? `<div class="dependency-hint">${hint}</div>` : 
            `<div class="dependency-solution">${hint}</div>`
        ).join('');

        modal.innerHTML = `
            <div class="modal dependency-modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">⚠️ Missing Dependencies</h3>
                    <p class="modal-subtitle">Some tools require additional setup</p>
                </div>
                <div class="modal-body">
                    <div class="missing-tools-info">
                        <h4>Category: ${groupValue}</h4>
                        <p><strong>Missing tools:</strong> ${toolsList}</p>
                    </div>
                    <div class="dependency-hints">
                        ${hintsHtml}
                    </div>
                    <div class="dependency-note">
                        <p><strong>Note:</strong> These are optional features. The main SRRD Builder functionality works without them.</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" type="button" onclick="app.closeModal()">
                        Got it
                    </button>
                </div>
            </div>
        `;

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        document.body.appendChild(modal);
        this.currentModal = modal;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    editToolParameters(toolName) {
        if (!Array.isArray(this.availableTools)) {
            this.log('No tools available. Please connect to the server first.', 'error');
            return;
        }
        
        const tool = this.availableTools.find(t => t && t.name === toolName);
        if (!tool) {
            this.log(`Tool ${toolName} not found`, 'error');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const toolInfo = this.toolInfo[toolName];
        modal.innerHTML = `
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">${this.formatToolName(toolName)}</h3>
                    <p class="modal-subtitle">${toolInfo?.description || 'Configure parameters for this tool'}</p>
                </div>
                <div class="modal-body">
                    <form id="toolForm">
                        ${this.generateParameterForm(tool.inputSchema, toolName)}
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" type="button" onclick="app.executeToolFromForm('${toolName}')">
                        ▶️ Run Tool
                    </button>
                    <button class="btn btn-secondary" type="button" onclick="app.closeModal()">
                        Cancel
                    </button>
                </div>
            </div>
        `;

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        document.body.appendChild(modal);
        this.currentModal = modal;
    }

    formatParameterName(name) {
        if (typeof name !== 'string') return '';
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    generateInputField(paramName, paramDetails, defaultValue) {
        const { type, description, enum: enumValues } = paramDetails;
        let field = `<div class="form-group">`;
        field += `<label for="${paramName}">${this.formatParameterName(paramName)}</label>`;
        
        // Create a container for the input and its description
        field += `<div class="input-wrapper">`;

        if (type === 'boolean') {
            field += `<input type="checkbox" id="${paramName}" name="${paramName}" ${defaultValue ? 'checked' : ''}>`;
        } else if (enumValues) {
            field += `<select id="${paramName}" name="${paramName}" class="form-input">`;
            enumValues.forEach(option => {
                field += `<option value="${option}" ${defaultValue === option ? 'selected' : ''}>${option}</option>`;
            });
            field += `</select>`;
        } else if (type === 'integer' || type === 'number') {
            field += `<input type="number" id="${paramName}" name="${paramName}" value="${defaultValue || ''}" class="form-input">`;
        } else {
            field += `<input type="text" id="${paramName}" name="${paramName}" value="${defaultValue || ''}" class="form-input">`;
        }

        if (description) {
            field += `<div class="param-description">${description}</div>`;
        }
        
        field += `</div>`; // Close input-wrapper
        field += `</div>`; // Close form-group
        return field;
    }

    generateParameterForm(schema, toolName) {
        // Check if we have known parameters for this tool (verified parameter database)
        const knownParams = this.getToolParameterDefaults(toolName);
        const hasKnownParams = knownParams && Object.keys(knownParams).length > 0;
        
        // Check if tool has valid schema
        const hasValidSchema = schema && 
                               schema.properties && 
                               Object.keys(schema.properties).length > 0;

        // Check if this is a tool that legitimately takes no parameters
        const noParameterTools = [
            'reset_project_context',
            'assess_foundational_assumptions',
            'compare_approaches',
            'compare_paradigms',
            'cultivate_innovation',
            'develop_alternative_framework',
            'ensure_ethics',
            'evaluate_paradigm_shift_potential',
            'explain_methodology',
            'generate_critical_questions',
            'generate_latex_with_template',
            'initiate_paradigm_challenge',
            'list_latex_templates',
            'validate_design',
            'validate_novel_theory'
        ];
        
        const isNoParameterTool = noParameterTools.includes(toolName);

        if (!hasValidSchema && hasKnownParams) {
            // If we have known verified parameters, create a clean form (no warnings)
            return this.generateCleanParameterForm(knownParams, toolName);
        }
        
        // If tool has valid schema, use it
        if (hasValidSchema) {
            const fields = Object.entries(schema.properties).map(([paramName, paramDetails]) => {
                const defaultValue = knownParams ? knownParams[paramName] : (paramDetails.default || '');
                return this.generateInputField(paramName, paramDetails, defaultValue);
            });

            return fields.join('');
        }
        
        // If this is a tool that takes no parameters, show appropriate message
        if (isNoParameterTool) {
            return `
                <div class="parameter-note">
                    <p><strong>Info:</strong> This tool requires no parameters and can be executed directly.</p>
                </div>
            `;
        }
        
        // Only show fallback form with warnings for truly unknown tools
        return this.generateFallbackParameterForm(toolName);
    }
    
    generateCleanParameterForm(knownParams, toolName) {
        const fields = Object.entries(knownParams).map(([paramName, defaultValue]) => {
            const paramType = typeof defaultValue === 'boolean' ? 'boolean' : 'string';
            return this.generateInputField(paramName, {type: paramType}, defaultValue);
        });
        return fields.join('');
    }

    generateFallbackParameterForm(toolName) {
        // This method now only handles tools with no known parameters
        // (Tools with known parameters use generateCleanParameterForm instead)
        const commonParams = this.getCommonParametersForTool(toolName);
        
        const formFields = Object.entries(commonParams).map(([paramName, paramInfo]) => {
            const label = paramName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            return `
                <div class="form-group">
                    <label for="${paramName}">${label}</label>
                    ${this.generateInputField(paramName, {type: paramInfo.type}, paramInfo.default)}
                    <small class="form-help">${paramInfo.description}</small>
                </div>
            `;
        }).join('');

        const jsonDefaults = JSON.stringify(
            Object.fromEntries(Object.entries(commonParams).map(([name, info]) => [name, info.default])), 
            null, 2
        );

        return `
            <div class="parameter-note">
                <p><strong>Note:</strong> This tool has no documented parameters. Common research parameters are provided below.</p>
            </div>
            
            <div class="parameter-view-switcher">
                <div class="btn-group">
                    <button type="button" class="btn btn-sm btn-primary" id="formViewBtn" onclick="app.toggleParameterView('form')">
                        📋 Form View
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary" id="jsonViewBtn" onclick="app.toggleParameterView('json')">
                        {} JSON View
                    </button>
                </div>
                <button type="button" class="btn btn-sm btn-outline" onclick="app.resetToDefaults()" title="Reset to default values">
                    🔄 Reset Defaults
                </button>
            </div>
            
            <div id="formView" class="parameter-view">
                ${formFields}
            </div>
            
            <div id="jsonView" class="parameter-view" style="display: none;">
                <div class="form-group">
                    <label for="jsonParameters">Parameters (JSON)</label>
                    <textarea id="jsonParameters" class="form-textarea json-editor" rows="12" spellcheck="false">${this.escapeHtml(jsonDefaults)}</textarea>
                    <small class="form-help">Edit parameters as JSON. These are generic parameters for unknown tools.</small>
                </div>
            </div>
        `;
    }

    getCommonParametersForTool(toolName) {
        // Get current project path from server if available, otherwise extract from UI
        let currentProjectPath;
        
        if (this.serverInfo && this.serverInfo.projectPath) {
            currentProjectPath = this.serverInfo.projectPath;
        } else {
            // Extract from UI element (toolCount has the path)
            const toolCountElement = document.getElementById('toolCount');
            if (toolCountElement && toolCountElement.title) {
                const match = toolCountElement.title.match(/Full project path: ([^(]+)/);
                if (match) {
                    currentProjectPath = match[1].trim();
                }
            }
        }
        
        // Define common parameters based on tool name patterns
        const baseParams = {
            query: {
                type: 'string',
                default: 'research question or search query',
                description: 'Search query or research question'
            },
            text: {
                type: 'string', 
                default: 'Sample research text for analysis and processing',
                description: 'Text content to analyze or process'
            },
            content: {
                type: 'string',
                default: 'Research content to analyze',
                description: 'Content or document text'
            },
            project_path: {
                type: 'string',
                default: currentProjectPath,
                description: 'Path to the research project directory'
            },
            domain: {
                type: 'string',
                default: 'artificial intelligence',
                description: 'Research domain or field of study'
            }
        };

        // Tool-specific parameter suggestions based on common patterns
        if (toolName.includes('compare')) {
            return {
                approach_a: {
                    type: 'string',
                    default: 'First research approach or methodology to compare',
                    description: 'First approach for comparison'
                },
                approach_b: {
                    type: 'string', 
                    default: 'Second research approach or methodology to compare',
                    description: 'Second approach for comparison'
                },
                research_context: {
                    type: 'string',
                    default: 'Artificial intelligence and machine learning research context',
                    description: 'Research domain or contextual framework'
                },
                ...baseParams
            };
        }
        
        if (toolName.includes('validate') || toolName.includes('assess')) {
            return {
                research_design: {
                    type: 'string',
                    default: 'Experimental design employing mixed-methods approach with quantitative analysis and qualitative validation to investigate the effectiveness of novel AI algorithms',
                    description: 'Research design or methodology to validate'
                },
                research_proposal: {
                    type: 'string',
                    default: 'A comprehensive proposal investigating novel methodologies in AI research',
                    description: 'Research proposal or document to analyze'
                },
                ...baseParams
            };
        }
        
        if (toolName.includes('analyze') || toolName.includes('review')) {
            return {
                research_proposal: {
                    type: 'string',
                    default: 'A comprehensive proposal investigating novel methodologies in AI research',
                    description: 'Research proposal or document to analyze'
                },
                document_content: {
                    type: 'string',
                    default: 'Research document content for comprehensive analysis and review',
                    description: 'Document content to analyze'
                },
                ...baseParams
            };
        }
        
        if (toolName.includes('generate') || toolName.includes('create')) {
            return {
                title: {
                    type: 'string',
                    default: 'Novel Approaches in Research Methodology',
                    description: 'Title for the generated content'
                },
                description: {
                    type: 'string',
                    default: 'Comprehensive research methodology description',
                    description: 'Description of what to generate'
                },
                ...baseParams
            };
        }

        if (toolName.includes('paradigm') || toolName.includes('framework')) {
            return {
                research_context: {
                    type: 'string',
                    default: 'Artificial intelligence and machine learning research paradigm',
                    description: 'Research context or paradigm framework'
                },
                current_paradigm: {
                    type: 'string',
                    default: 'Traditional supervised learning approaches',
                    description: 'Current paradigm or framework'
                },
                ...baseParams
            };
        }

        if (toolName.includes('ethics') || toolName.includes('ethical')) {
            return {
                research_proposal: {
                    type: 'string',
                    default: 'A research proposal investigating AI ethics and responsible AI development practices',
                    description: 'Research proposal to evaluate for ethical considerations'
                },
                ethical_considerations: {
                    type: 'string',
                    default: 'Privacy protection, bias mitigation, transparency, and social impact assessment',
                    description: 'Ethical considerations and concerns'
                },
                ...baseParams
            };
        }

        if (toolName.includes('methodology') || toolName.includes('method')) {
            return {
                research_goals: {
                    type: 'string',
                    default: 'To investigate effectiveness of novel approaches in AI research',
                    description: 'Research goals and objectives'
                },
                methodology: {
                    type: 'string',
                    default: 'Mixed-methods approach combining quantitative experiments with qualitative analysis',
                    description: 'Research methodology description'
                },
                ...baseParams
            };
        }

        // Return enhanced base parameters for unknown tools
        return {
            ...baseParams,
            research_design: {
                type: 'string',
                default: 'Comprehensive experimental design with control groups and systematic evaluation metrics',
                description: 'Research design or experimental setup'
            },
            research_proposal: {
                type: 'string',
                default: 'A detailed proposal investigating innovative approaches to complex research problems',
                description: 'Research proposal or study description'
            }
        };
    }

    getDynamicExamples() {
        // Get current project path from server if available, otherwise extract from UI
        let currentProjectPath;
        
        if (this.serverInfo && this.serverInfo.projectPath) {
            currentProjectPath = this.serverInfo.projectPath;
        } else {
            // Extract from UI element (toolCount has the path)
            const toolCountElement = document.getElementById('toolCount');
            if (toolCountElement && toolCountElement.title) {
                const match = toolCountElement.title.match(/Full project path: ([^(]+)/);
                if (match) {
                    currentProjectPath = match[1].trim();
                }
            }
        }
        
        return {
            // === VERIFIED PARAMETERS FROM ACTUAL MCP SERVER SCHEMAS AND ERROR TESTING ===
            'research_area': 'machine learning and data science',
            'initial_goals': 'To investigate the effectiveness of novel approaches in improving predictive accuracy and interpretability in machine learning systems',
            'research_goals': 'To develop and evaluate innovative methodologies for solving complex problems in artificial intelligence and data science',
            'domain': 'artificial intelligence',
            'document_content': {
                'title': 'Novel Approaches in AI Research',
                'abstract': 'This paper presents innovative methodologies for advancing artificial intelligence research',
                'content': 'Comprehensive research content focusing on AI methodology and practical applications',
                'methodology': 'Mixed-methods approach with quantitative analysis and qualitative validation'
            },
            'title': 'Advanced Research in Artificial Intelligence Applications',
            'query': 'machine learning research methods and applications',
            'content': 'Comprehensive research text for detailed analysis, evaluation, and systematic processing using advanced computational methods',
            'text': 'Research text focusing on artificial intelligence methodology, experimental design, and practical applications in scientific domains',
            'documents': ['ai-research-paper.pdf', 'methodology-guide.txt', 'experimental-results.xlsx'],
            'target_document': 'Research document focusing on machine learning applications and methodological innovations in artificial intelligence',
            
            // === PARAMETERS FROM ERROR MESSAGES (TOOLS WITH BROKEN SCHEMAS) ===
            'approach_a': 'Traditional supervised learning approach using established algorithms and conventional feature engineering techniques',
            'approach_b': 'Novel deep learning approach utilizing advanced neural network architectures and automated feature learning mechanisms',
            'research_context': 'Advanced AI research methodology focusing on practical applications, theoretical foundations, and experimental validation',
            'research_design': 'Comprehensive experimental research design investigating the effectiveness of novel machine learning algorithms through systematic evaluation, comparative analysis, and rigorous statistical validation',
            'research_proposal': 'A detailed research proposal investigating the effectiveness of novel artificial intelligence methodologies in advancing scientific discovery, improving problem-solving capabilities, and enhancing practical applications across diverse domains',
            'theory_framework': 'Novel theoretical framework for AI generalization combining deep learning principles with symbolic reasoning approaches for improved performance and interpretability',
            
            // === COMMON RESEARCH PARAMETERS ===
            'author': 'Dr. Jane Smith, PhD in Computer Science',
            'abstract': 'This paper presents a comprehensive investigation of novel approaches in artificial intelligence research, focusing on methodological innovations and practical applications',
            'introduction': 'In recent years, the field of artificial intelligence has witnessed remarkable advances in both theoretical foundations and practical applications across diverse domains',
            'methodology': 'We employed a comprehensive mixed-methods approach combining rigorous quantitative analysis with qualitative insights from domain experts and systematic evaluation protocols',
            'results': 'The comprehensive analysis revealed statistically significant findings that substantially advance our understanding of the underlying mechanisms and their practical implications',
            'discussion': 'The results have important implications for both theoretical understanding and practical applications, providing valuable insights for future research directions and methodological improvements',
            'conclusion': 'This study demonstrates the effectiveness of the proposed methodology and opens new avenues for future research in artificial intelligence applications and scientific discovery',
            'bibliography': 'Smith, J. et al. (2024). Advanced Machine Learning Techniques. AI Research Quarterly. Johnson, M. (2023). Data Science Methodologies. Computational Science Review.',
            'name': 'AI Research Project Alpha',
            'description': 'Comprehensive research project investigating advanced methodologies in artificial intelligence with focus on practical applications and theoretical contributions',
            'project_path': currentProjectPath, // Use dynamic project path
            
            // === FILE AND PATH PARAMETERS ===
            'tex_file_path': '/project/manuscript/main.tex',
            'file_path': '/research/documents/methodology-paper.pdf',
            'document_path': '/research/papers/ai-research-findings.pdf',
            'resource_path': '/workspace/research-resources',
            
            // === COLLECTIONS AND METADATA ===
            'references': [
                {'title': 'Advanced Machine Learning Techniques in Scientific Research', 'author': 'Smith, J. et al.', 'year': 2024, 'journal': 'AI Research Quarterly'},
                {'title': 'Data Science Methodologies for Complex Problem Solving', 'author': 'Johnson, M.', 'year': 2023, 'journal': 'Computational Science Review'}
            ],
            'relationship_types': ['citation', 'methodology', 'thematic', 'experimental'],
            'concept_types': ['technical', 'theoretical', 'methodological'],
            'constraints': {
                'time_limit': '6 months',
                'budget': 'limited',
                'resources': 'academic',
                'scope': 'focused'
            },
            'research_content': {
                'title': 'AI Methodology Research',
                'phase': 'analysis',
                'content': 'Research content for quality assessment',
                'methodology': 'systematic approach'
            },
            'phase': 'analysis',
            'domain_standards': {
                'peer_review': 'required',
                'reproducibility': 'essential',
                'ethical_approval': 'obtained'
            },
            'innovation_criteria': {
                'novelty': 'high',
                'impact': 'significant',
                'feasibility': 'proven'
            },
            'session_data': {
                'session_id': 'session_001',
                'timestamp': new Date().toISOString(),
                'user': 'researcher',
                'project': 'ai_research'
            },
            
            // === CONFIGURATION PARAMETERS ===
            'collection': 'research_papers_2024',
            'pattern_type': 'thematic_analysis',
            'content_type': 'academic_section',
            'formatting_style': 'academic',
            'summary_type': 'comprehensive_overview',
            'review_type': 'comprehensive_peer_review',
            'output_format': 'pdf',
            'experience_level': 'advanced',
            'domain_specialization': 'machine learning',
            'novel_theory_mode': false,
            'novel_theory_flag': false,
            'bibliography_query': 'machine learning neural networks deep learning',
            'action': 'commit',
            'message': 'Add comprehensive research analysis and experimental findings',
            
            // === NUMERIC PARAMETERS ===
            'max_results': 25,
            'max_concepts': 15,
            'limit': 50,
            'min_frequency': 3,
            'similarity_threshold': 0.75,
            'max_length': 2000,
            'session_id': 1001
        };
    }

    getExampleValue(paramName, type) {
        // === PRIORITIZE ACTUAL PROJECT PATH FROM SERVER ===
        const paramLower = paramName.toLowerCase();
        
        // For project_path parameters, use the actual project path from server if available
        if (paramLower.includes('project_path') || paramLower === 'project_path') {
            // Method 1: Check serverInfo for project path first
            if (this.serverInfo && this.serverInfo.projectPath) {
                return this.serverInfo.projectPath;
            }
            // Method 2: Extract from UI element (toolCount has the path)
            const toolCountElement = document.getElementById('toolCount');
            if (toolCountElement && toolCountElement.title) {
                const match = toolCountElement.title.match(/Full project path: ([^(]+)/);
                if (match) {
                    return match[1].trim();
                }
            }
            // Method 3: Fallback - no hardcoded paths, return null if not available
            return null;
        }
        
        // Get dynamic examples with current project path
        const examples = this.getDynamicExamples();

        // Check for exact match first
        if (examples[paramName] !== undefined) {
            return examples[paramName];
        }

        // Check for partial matches (case insensitive)
        for (const [key, value] of Object.entries(examples)) {
            if (paramLower.includes(key.toLowerCase()) || key.toLowerCase().includes(paramLower)) {
                return value;
            }
        }

        // Fall back to type-based defaults with comprehensive examples
        switch (type) {
            case 'string': 
                if (paramLower.includes('domain')) return 'artificial intelligence';
                if (paramLower.includes('area')) return 'machine learning and data science';
                if (paramLower.includes('design')) return 'Comprehensive experimental research design for systematic investigation';
                if (paramLower.includes('context')) return 'Advanced research methodology and practical applications';
                if (paramLower.includes('proposal')) return 'Detailed research proposal investigating novel approaches and methodologies';
                if (paramLower.includes('approach')) return 'Systematic methodological approach using advanced techniques';
                if (paramLower.includes('path')) {
                    // Use actual server project path if available, otherwise fallback
                    if (this.serverInfo && this.serverInfo.projectPath) {
                        return this.serverInfo.projectPath;
                    }
                    return '/research/project/path';
                }
                if (paramLower.includes('query')) return 'comprehensive research query and analysis';
                if (paramLower.includes('title')) return 'Advanced Research in Scientific Methodology';
                if (paramLower.includes('name')) return 'Comprehensive Research Project';
                return 'comprehensive example research content';
                
            case 'number': 
            case 'integer': 
                if (paramLower.includes('threshold')) return 0.8;
                if (paramLower.includes('limit') || paramLower.includes('max')) return 25;
                if (paramLower.includes('min')) return 1;
                if (paramLower.includes('id')) return 1;
                if (paramLower.includes('frequency')) return 5;
                return 10;
                
            case 'boolean': 
                return false;
                
            case 'array': 
                if (paramLower.includes('document')) return ['research-doc-1.pdf', 'analysis-notes.txt'];
                if (paramLower.includes('tool')) return ['analysis_tool', 'visualization_tool'];
                if (paramLower.includes('file')) return ['data.csv', 'results.json'];
                if (paramLower.includes('reference')) return ['Smith2024', 'Johnson2023'];
                return ['example_item_1', 'example_item_2'];
                
            case 'object': 
                if (paramLower.includes('content')) return {'title': 'Research Content', 'text': 'comprehensive analysis'};
                if (paramLower.includes('data')) return {'type': 'research_data', 'format': 'structured'};
                if (paramLower.includes('config')) return {'mode': 'analysis', 'precision': 'high'};
                if (paramLower.includes('session')) return {'id': 'session_001', 'active': true};
                return {'example_key': 'example_value', 'type': 'comprehensive_object'};
                
            default: 
                return 'comprehensive_example_value';
        }
    }

    getTypeDefault(type) {
        switch (type) {
            case 'string': return '';
            case 'number': 
            case 'integer': return 0;
            case 'boolean': return false;
            case 'array': return [];
            case 'object': return {};
            default: return '';
        }
    }

    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    toggleParameterView(view) {
        const formView = document.getElementById('formView');
        const jsonView = document.getElementById('jsonView');
        const formBtn = document.getElementById('formViewBtn');
        const jsonBtn = document.getElementById('jsonViewBtn');
        
        if (view === 'json') {
            // Sync form data to JSON before switching
            this.syncFormToJson();
            
            formView.style.display = 'none';
            jsonView.style.display = 'block';
            formBtn.classList.remove('btn-primary');
            formBtn.classList.add('btn-secondary');
            jsonBtn.classList.remove('btn-secondary');
            jsonBtn.classList.add('btn-primary');
        } else {
            // Sync JSON data to form before switching
            this.syncJsonToForm();
            
            formView.style.display = 'block';
            jsonView.style.display = 'none';
            formBtn.classList.remove('btn-secondary');
            formBtn.classList.add('btn-primary');
            jsonBtn.classList.remove('btn-primary');
            jsonBtn.classList.add('btn-secondary');
        }
    }

    syncFormToJson() {
        const form = document.getElementById('toolForm');
        const jsonTextarea = document.getElementById('jsonParameters');
        
        if (!form || !jsonTextarea) return;

        const formData = new FormData(form);
        const parameters = {};

        for (const [key, value] of formData.entries()) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    parameters[key] = input.checked;
                } else if (input.type === 'number') {
                    parameters[key] = input.step === '1' ? parseInt(value) || 0 : parseFloat(value) || 0;
                } else if (input.tagName === 'TEXTAREA') {
                    try {
                        parameters[key] = JSON.parse(value || (input.placeholder.includes('array') ? '[]' : '{}'));
                    } catch {
                        parameters[key] = value;
                    }
                } else {
                    parameters[key] = value;
                }
            }
        }

        jsonTextarea.value = JSON.stringify(parameters, null, 2);
    }

    syncJsonToForm() {
        const form = document.getElementById('toolForm');
        const jsonTextarea = document.getElementById('jsonParameters');
        
        if (!form || !jsonTextarea) return;

        try {
            const parameters = JSON.parse(jsonTextarea.value || '{}');
            
            Object.entries(parameters).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = Boolean(value);
                    } else if (input.tagName === 'TEXTAREA') {
                        input.value = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;
                    } else {
                        input.value = value;
                    }
                }
            });
        } catch (error) {
            this.log(`Invalid JSON in parameter editor: ${error.message}`, 'error');
        }
    }

    resetToDefaults() {
        const form = document.getElementById('toolForm');
        const jsonTextarea = document.getElementById('jsonParameters');
        
        if (!form) return;

        // Get the current tool being edited from the modal title
        const modalTitle = document.querySelector('.modal-title');
        if (!modalTitle) return;
        
        const toolName = modalTitle.textContent.trim();
        const tool = Array.isArray(this.availableTools) ? 
            this.availableTools.find(t => t && this.formatToolName(t.name) === toolName) : null;

        if (tool && tool.inputSchema) {
            // Generate fresh default values
            const defaultValues = this.getDefaultParameterValues(tool.inputSchema);
            
            // Update form fields
            Object.entries(defaultValues).forEach(([paramName, value]) => {
                const input = form.querySelector(`[name="${paramName}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = Boolean(value);
                    } else if (input.tagName === 'TEXTAREA') {
                        input.value = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;
                    } else {
                        input.value = value || '';
                    }
                }
            });
            
            // Update JSON view if active
            if (jsonTextarea) {
                jsonTextarea.value = JSON.stringify(defaultValues, null, 2);
            }
            
            this.log('Parameters reset to default example values', 'info');
        } else {
            // Fallback to basic form reset
            form.reset();
            this.log('Form reset to empty values', 'info');
        }
    }

    async executeToolFromForm(toolName) {
        const form = document.getElementById('toolForm');
        const jsonView = document.getElementById('jsonView');
        const jsonTextarea = document.getElementById('jsonParameters');
        
        if (!form) return;

        let parameters = {};

        // Check if we're in JSON view mode
        if (jsonView && jsonView.style.display !== 'none' && jsonTextarea) {
            // Parse from JSON
            try {
                parameters = JSON.parse(jsonTextarea.value || '{}');
            } catch (error) {
                this.log(`Invalid JSON parameters: ${error.message}`, 'error');
                return;
            }
        } else {
            // Parse from form
            const formData = new FormData(form);

            for (const [key, value] of formData.entries()) {
                if (value.trim() !== '') {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input?.type === 'checkbox') {
                        parameters[key] = input.checked;
                    } else if (input?.type === 'number') {
                        parameters[key] = input.step === '1' ? parseInt(value) || 0 : parseFloat(value) || 0;
                    } else if (input?.tagName === 'TEXTAREA') {
                        try {
                            parameters[key] = JSON.parse(value);
                        } catch {
                            parameters[key] = value;
                        }
                    } else {
                        parameters[key] = value;
                    }
                }
            }
        }

        this.closeModal();
        
        this.log(`Running ${toolName} with parameters: ${JSON.stringify(parameters, null, 2)}`);
        
        try {
            const result = await this.mcpClient.callTool(toolName, parameters);
            this.log(`✅ ${toolName} completed successfully`, 'success');
            this.log(`Result: ${JSON.stringify(result, null, 2)}`);
        } catch (error) {
            this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
        }
    }

    closeModal() {
        if (this.currentModal) {
            this.currentModal.style.opacity = '0';
            setTimeout(() => {
                if (this.currentModal && this.currentModal.parentNode) {
                    this.currentModal.parentNode.removeChild(this.currentModal);
                }
                this.currentModal = null;
            }, 200);
        }
    }

    async refreshTools() {
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }
        
        const refreshBtn = document.getElementById('refreshBtn');
        this.setButtonLoading(refreshBtn, 'Refreshing...');
        
        try {
            await this.loadTools();
            
            // Re-render current view
            if (this.currentView === 'acts') {
                this.renderResearchActs();
            } else if (this.currentView === 'categories' && this.selectedAct) {
                this.renderCategoriesForAct(this.selectedAct);
            } else if (this.currentView === 'tools') {
                if (this.selectedCategory) {
                    this.renderToolsForCategory(this.selectedCategory);
                } else {
                    this.renderAllTools();
                }
            }
            
            this.log('Tools refreshed successfully', 'success');
        } catch (error) {
            this.log(`Failed to refresh tools: ${error.message}`, 'error');
        } finally {
            refreshBtn.textContent = 'Refresh Tools';
            refreshBtn.disabled = false;
        }
    }

    formatToolName(name) {
        return name.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    setButtonLoading(button, text) {
        if (button) {
            button.textContent = text;
            button.disabled = true;
        }
    }

    log(message, type = 'info') {
        const console = document.getElementById('console');
        if (!console) return;

        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'console-line';
        
        logEntry.innerHTML = `
            <span class="console-timestamp">[${timestamp}]</span>
            <span class="console-${type}">${message}</span>
        `;
        
        console.appendChild(logEntry);
        console.scrollTop = console.scrollHeight;
    }

    clearConsole() {
        const console = document.getElementById('console');
        if (console) {
            console.innerHTML = `
                <div class="console-line">
                    <span class="console-timestamp">[Ready]</span>
                    <span class="console-info">Enhanced SRRD-Builder MCP Frontend Ready</span>
                </div>
            `;
        }
    }
}
