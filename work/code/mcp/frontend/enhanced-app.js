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
        
        this.init();
    }

    async init() {
        this.mcpClient = new MCPClient('ws://localhost:8765');
        this.setupEventListeners();
        this.log('Enhanced SRRD Frontend initialized');
        
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
    }

    async connectToServer() {
        const connectBtn = document.getElementById('connectBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        this.setButtonLoading(connectBtn, 'Connecting...');

        try {
            await this.mcpClient.connect();
            
            // Update UI
            statusIndicator.className = 'status-indicator status-connected';
            statusText.textContent = 'Connected';
            connectBtn.textContent = 'Connected ✓';
            connectBtn.disabled = true;
            document.getElementById('refreshBtn').disabled = false;
            
            this.isConnected = true;
            this.log('Connected to MCP server successfully', 'success');
            
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
            
            document.getElementById('toolCount').textContent = 
                `${tools.length} tools available`;
            
            this.log(`Loaded ${tools.length} tools from server`, 'success');
            
        } catch (error) {
            this.log(`Failed to load tools: ${error.message}`, 'error');
            this.availableTools = []; // Ensure it's always an array
        }
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
                <div class="research-act-card" data-act="${actId}" onclick="app.selectResearchAct('${actId}')">
                    <div class="act-header">
                        <span class="act-icon">${act.icon}</span>
                        <h3 class="act-name">${act.name}</h3>
                    </div>
                    <p class="act-description">${act.description}</p>
                    <div class="act-categories">
                        ${act.categories.length} categories • ${toolCount} tools
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
                <div class="category-card" onclick="app.selectCategory('${category.id}')">
                    <div class="category-header">
                        <span class="category-icon">${category.icon}</span>
                        <h3>${category.name}</h3>
                    </div>
                    <p>${category.description}</p>
                    <div class="category-stats">
                        ${availableTools.length} tools available
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
                    <div class="tool-actions-header">
                        <button class="btn-info" onclick="app.showToolInfo('${toolName}')" title="Tool Information">
                            ℹ️
                        </button>
                    </div>
                </div>
                <div class="enhanced-tool-description">${description}</div>
                <div class="enhanced-tool-actions">
                    <button class="btn btn-primary btn-tool" onclick="app.runToolWithDefaults('${toolName}')">
                        ▶️ Run Tool
                    </button>
                    <button class="btn-edit" onclick="app.editToolParameters('${toolName}')" title="Edit Parameters">
                        ⚙️
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

        this.log(`Running ${toolName} with defaults...`);
        
        try {
            const result = await this.mcpClient.callTool(toolName, {});
            this.log(`✅ ${toolName} completed successfully`, 'success');
            this.log(`Result: ${JSON.stringify(result, null, 2)}`);
        } catch (error) {
            this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
        }
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
                        ${this.generateParameterForm(tool.inputSchema)}
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

    generateParameterForm(schema) {
        if (!schema || !schema.properties) {
            return '<p>No parameters required for this tool.</p>';
        }

        const defaultValues = this.getDefaultParameterValues(schema);
        const jsonDefaults = JSON.stringify(defaultValues, null, 2);

        const formFields = Object.entries(schema.properties).map(([paramName, paramDef]) => {
            const required = schema.required?.includes(paramName) || false;
            const label = paramName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            return `
                <div class="form-group">
                    <label for="${paramName}">
                        ${label}${required ? ' *' : ''}
                    </label>
                    ${this.generateInputField(paramName, paramDef, defaultValues[paramName])}
                    ${paramDef.description ? `<small class="form-help">${paramDef.description}</small>` : ''}
                </div>
            `;
        }).join('');

        return `
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
                    <textarea id="jsonParameters" class="form-textarea json-editor" rows="12" spellcheck="false">${jsonDefaults}</textarea>
                    <small class="form-help">Edit parameters as JSON. Switch back to Form View to validate.</small>
                </div>
            </div>
        `;
    }

    generateInputField(paramName, paramDef, defaultValue = null) {
        // Handle enum values with dropdown
        if (paramDef.enum && Array.isArray(paramDef.enum)) {
            const selected = defaultValue || paramDef.default || paramDef.enum[0];
            const options = paramDef.enum.map(option => 
                `<option value="${option}" ${option === selected ? 'selected' : ''}>${option}</option>`
            ).join('');
            return `<select id="${paramName}" name="${paramName}" class="form-select">${options}</select>`;
        }

        // Get default value
        const value = defaultValue !== null ? defaultValue : (paramDef.default || this.getTypeDefault(paramDef.type));
        
        switch (paramDef.type) {
            case 'string':
                return `<input type="text" id="${paramName}" name="${paramName}" class="form-input" value="${this.escapeHtml(value || '')}">`;
            case 'number':
                return `<input type="number" id="${paramName}" name="${paramName}" class="form-input" value="${value || 0}" step="any">`;
            case 'integer':
                return `<input type="number" id="${paramName}" name="${paramName}" class="form-input" value="${value || 0}" step="1">`;
            case 'boolean':
                return `<input type="checkbox" id="${paramName}" name="${paramName}" class="form-checkbox" ${value ? 'checked' : ''}>`;
            case 'array':
                const arrayValue = Array.isArray(value) ? JSON.stringify(value, null, 2) : '[]';
                return `<textarea id="${paramName}" name="${paramName}" class="form-textarea" rows="4" placeholder="Enter JSON array, e.g., [\"item1\", \"item2\"]">${this.escapeHtml(arrayValue)}</textarea>`;
            case 'object':
                const objectValue = value && typeof value === 'object' ? JSON.stringify(value, null, 2) : '{}';
                return `<textarea id="${paramName}" name="${paramName}" class="form-textarea" rows="4" placeholder="Enter JSON object, e.g., {\"key\": \"value\"}">${this.escapeHtml(objectValue)}</textarea>`;
            default:
                return `<input type="text" id="${paramName}" name="${paramName}" class="form-input" value="${this.escapeHtml(value || '')}">`;
        }
    }

    getDefaultParameterValues(schema) {
        if (!schema || !schema.properties) return {};
        
        const defaults = {};
        Object.entries(schema.properties).forEach(([paramName, paramDef]) => {
            if (paramDef.default !== undefined) {
                defaults[paramName] = paramDef.default;
            } else if (paramDef.enum && Array.isArray(paramDef.enum)) {
                defaults[paramName] = paramDef.enum[0];
            } else {
                defaults[paramName] = this.getTypeDefault(paramDef.type);
            }
        });
        
        return defaults;
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
        if (!form) return;

        // Reset form to default values
        form.reset();
        
        // Trigger default values for the form
        const event = new Event('reset');
        form.dispatchEvent(event);
        
        // If in JSON view, sync the defaults
        const jsonView = document.getElementById('jsonView');
        if (jsonView && jsonView.style.display !== 'none') {
            this.syncFormToJson();
        }
        
        this.log('Parameters reset to default values', 'info');
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
