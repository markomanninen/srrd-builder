/**
 * SRRD-Builder MCP Frontend Application
 * Enhanced frontend with parameter editing and modern UI
 */

class SRRDFrontendApp {
    constructor() {
        this.mcpClient = null;
        this.availableTools = [];
        this.currentModal = null;
        this.toolCategories = {
            'clarify_research_goals': 'research',
            'suggest_methodology': 'research', 
            'simulate_peer_review': 'quality',
            'check_quality_gates': 'quality',
            'initialize_project': 'storage',
            'save_session': 'storage',
            'restore_session': 'storage',
            'search_knowledge': 'search',
            'version_control': 'storage',
            'backup_project': 'storage',
            'generate_latex_document': 'document',
            'compile_latex': 'document',
            'format_research_content': 'document',
            'generate_bibliography': 'document',
            'extract_document_sections': 'document',
            'store_bibliography_reference': 'storage',
            'retrieve_bibliography_references': 'storage',
            'generate_document_with_database_bibliography': 'document',
            'list_latex_templates': 'document',
            'generate_latex_with_template': 'document',
            'semantic_search': 'search',
            'discover_patterns': 'search',
            'build_knowledge_graph': 'search',
            'find_similar_documents': 'search',
            'extract_key_concepts': 'search',
            'generate_research_summary': 'search',
            'explain_methodology': 'methodology',
            'compare_approaches': 'methodology',
            'validate_design': 'methodology',
            'ensure_ethics': 'methodology',
            'initiate_paradigm_challenge': 'novel',
            'develop_alternative_framework': 'novel',
            'compare_paradigms': 'novel',
            'validate_novel_theory': 'novel',
            'cultivate_innovation': 'novel',
            'assess_foundational_assumptions': 'novel',
            'generate_critical_questions': 'novel',
            'evaluate_paradigm_shift_potential': 'novel'
        };

        this.categoryInfo = {
            'research': { 
                title: 'Research Planning & Goal Setting', 
                icon: '🧪',
                description: 'Clarify research objectives and suggest methodologies'
            },
            'quality': { 
                title: 'Quality Assurance & Review', 
                icon: '✅',
                description: 'Peer review simulation and quality validation'
            },
            'storage': { 
                title: 'Storage & Project Management', 
                icon: '🗄️',
                description: 'Project initialization and data management'
            },
            'document': { 
                title: 'Document Generation & LaTeX', 
                icon: '📄',
                description: 'Academic document and bibliography generation'
            },
            'search': { 
                title: 'Search & Discovery', 
                icon: '🔍',
                description: 'Semantic search and knowledge discovery'
            },
            'methodology': { 
                title: 'Methodology & Validation', 
                icon: '⚗️',
                description: 'Research methodology analysis and validation'
            },
            'novel': { 
                title: 'Novel Theory Development', 
                icon: '🚀',
                description: 'Paradigm innovation and theory development'
            }
        };

        this.init();
    }

    // Initialize method for external calls
    initialize() {
        // Already initialized in constructor, but allow re-initialization
        this.log('🔄 Re-initializing SRRD Frontend...');
        return this;
    }

    init() {
        this.setupEventListeners();
        this.log('🚀 SRRD-Builder MCP Frontend Ready');
        this.log('');
        this.log('To get started:');
        this.log('1. Make sure MCP server is running: srrd-server');
        this.log('2. Click "Connect to Server"');
        this.log('3. Test individual tools with custom parameters');
        this.log('');
        this.log('Ready for testing! 🧪');
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

        // Clear console button
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearConsole());
        }

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeModal();
            }
        });
    }

    log(message, type = 'info') {
        const console = document.getElementById('console');
        if (!console) return;

        const timestamp = new Date().toLocaleTimeString();
        const line = document.createElement('div');
        line.className = 'console-line';
        
        let icon = '';
        switch(type) {
            case 'success': icon = '✅'; break;
            case 'error': icon = '❌'; break;
            case 'warning': icon = '⚠️'; break;
            default: icon = 'ℹ️'; break;
        }
        
        line.innerHTML = `
            <span class="console-timestamp">[${timestamp}]</span>
            <span class="console-${type}">${icon} ${message}</span>
        `;
        
        console.appendChild(line);
        console.scrollTop = console.scrollHeight;
    }

    async connectToServer() {
        const connectBtn = document.getElementById('connectBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const statsPanel = document.getElementById('statsPanel');
        
        try {
            this.setButtonLoading(connectBtn, 'Connecting...');
            statusIndicator.className = 'status-indicator connecting';
            
            this.log('Connecting to MCP server on localhost:8765...');
            
            this.mcpClient = new MCPClient('ws://localhost:8765');
            this.mcpClient.onStatusChange = (connected, message) => {
                if (connected) {
                    statusIndicator.className = 'status-indicator connected';
                    statusText.textContent = 'Connected';
                    document.getElementById('connectionStatus').textContent = 'Yes';
                    document.getElementById('refreshBtn').disabled = false;
                    statsPanel.classList.remove('hidden');
                } else {
                    statusIndicator.className = 'status-indicator disconnected';
                    statusText.textContent = 'Disconnected';
                    document.getElementById('connectionStatus').textContent = 'No';
                    document.getElementById('refreshBtn').disabled = true;
                    statsPanel.classList.add('hidden');
                }
            };
            
            await this.mcpClient.connect();
            
            // Get available tools
            const toolsResult = await this.mcpClient.listTools();
            const tools = toolsResult.tools || [];
            this.availableTools = tools;
            
            this.log(`Successfully connected! Found ${tools.length} tools`, 'success');
            this.updateStats(tools.length);
            
            this.renderTools(tools);
            
            connectBtn.innerHTML = '🔄 Reconnect';
            
        } catch (error) {
            this.log(`Connection failed: ${error.message}`, 'error');
            this.log('💡 Make sure the MCP server is running: srrd-server');
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Connection Failed';
        } finally {
            this.setButtonLoading(connectBtn, null);
        }
    }

    updateStats(toolCount) {
        document.getElementById('totalTools').textContent = toolCount;
        document.getElementById('toolCount').textContent = `(${toolCount} tools available)`;
        document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
    }

    renderTools(tools) {
        const toolsSection = document.getElementById('toolsSection');
        const statsPanel = document.getElementById('statsPanel');
        
        // Group tools by category
        const categorizedTools = {};
        
        tools.forEach(tool => {
            const category = this.toolCategories[tool.name] || 'other';
            if (!categorizedTools[category]) {
                categorizedTools[category] = [];
            }
            categorizedTools[category].push(tool);
        });
        
        // Clear existing tools (keep stats panel)
        const existingCategories = toolsSection.querySelectorAll('.tool-category');
        existingCategories.forEach(cat => {
            if (cat !== statsPanel) {
                cat.remove();
            }
        });
        
        // Render each category
        Object.keys(categorizedTools).forEach(categoryKey => {
            const categoryTools = categorizedTools[categoryKey];
            const categoryData = this.categoryInfo[categoryKey] || { 
                title: 'Other Tools', 
                icon: '⚙️',
                description: 'Additional research tools'
            };
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'tool-category';
            categoryDiv.innerHTML = `
                <h3>
                    <span class="category-icon">${categoryData.icon}</span>
                    ${categoryData.title}
                </h3>
                <p class="mb-3" style="color: var(--gray-600); font-size: 0.95rem;">${categoryData.description}</p>
                <div class="tool-grid" id="tools-${categoryKey}">
                    ${categoryTools.map(tool => this.renderToolCard(tool, categoryData)).join('')}
                </div>
            `;
            
            toolsSection.appendChild(categoryDiv);
        });
    }

    renderToolCard(tool, categoryData) {
        const toolName = tool.name;
        const description = tool.description || 'No description available';
        const formattedName = this.formatToolName(toolName);
        
        return `
            <div class="tool-card" data-tool="${toolName}">
                <div class="tool-header">
                    <span class="tool-icon">${categoryData.icon}</span>
                    <span class="tool-name">${formattedName}</span>
                </div>
                <div class="tool-description">${description}</div>
                <div class="tool-actions">
                    <button class="btn btn-primary btn-tool" onclick="app.runToolWithDefaults('${toolName}')">
                        ▶️ Run
                    </button>
                    <button class="btn-edit" onclick="app.editToolParameters('${toolName}')" title="Edit Parameters">
                        ⚙️
                    </button>
                </div>
            </div>
        `;
    }

    formatToolName(name) {
        return name.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    async runToolWithDefaults(toolName) {
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }
        
        const toolCard = document.querySelector(`[data-tool="${toolName}"]`);
        if (toolCard) {
            toolCard.classList.add('executing');
        }
        
        this.log(`Testing tool: ${toolName}...`);
        
        try {
            const toolArgs = this.getDefaultParameters(toolName);
            const result = await this.mcpClient.callTool(toolName, toolArgs);
            
            this.log(`✅ ${toolName} completed successfully`, 'success');
            this.log(`Response: ${JSON.stringify(result, null, 2)}`);
            
        } catch (error) {
            this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
        } finally {
            if (toolCard) {
                toolCard.classList.remove('executing');
            }
        }
    }

    editToolParameters(toolName) {
        const defaultParams = this.getDefaultParameters(toolName);
        const tool = this.availableTools.find(t => t.name === toolName);
        
        this.showParameterEditor(toolName, defaultParams, tool);
    }

    showParameterEditor(toolName, defaultParams, toolInfo) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const paramsJson = JSON.stringify(defaultParams, null, 2);
        
        modal.innerHTML = `
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">${this.formatToolName(toolName)}</h3>
                    <p class="modal-subtitle">${toolInfo?.description || 'Configure parameters for this tool'}</p>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Tool Parameters (JSON)</label>
                        <textarea 
                            class="form-textarea json-editor" 
                            id="paramEditor"
                            rows="12"
                            placeholder="Enter JSON parameters..."
                        >${paramsJson}</textarea>
                        <div class="form-help">
                            Edit the JSON parameters above. The default values are pre-filled.
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Quick Templates</label>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            <button class="btn btn-secondary" type="button" data-template="minimal">
                                Minimal
                            </button>
                            <button class="btn btn-secondary" type="button" data-template="full">
                                Full Example
                            </button>
                            <button class="btn btn-secondary" type="button" data-template="empty">
                                Empty
                            </button>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" type="button" id="cancelBtn">Cancel</button>
                    <button class="btn btn-primary" type="button" id="runBtn">
                        ▶️ Run Tool
                    </button>
                </div>
            </div>
        `;
        
        // Add click handler for background close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
        
        document.body.appendChild(modal);
        this.currentModal = modal;
        
        // Add event listeners for buttons
        const cancelBtn = modal.querySelector('#cancelBtn');
        const runBtn = modal.querySelector('#runBtn');
        const templateBtns = modal.querySelectorAll('[data-template]');
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeModal());
        }
        
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runToolWithCustomParams(toolName));
        }
        
        templateBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.loadParameterTemplate(toolName, btn.dataset.template);
            });
        });
        
        // Focus the textarea
        setTimeout(() => {
            const editor = modal.querySelector('#paramEditor');
            if (editor) {
                editor.focus();
                editor.setSelectionRange(0, 0);
            }
        }, 100);
    }

    loadParameterTemplate(toolName, templateType) {
        const editor = document.getElementById('paramEditor');
        if (!editor) return;
        
        let template = {};
        
        switch (templateType) {
            case 'minimal':
                template = this.getMinimalParameters(toolName);
                break;
            case 'full':
                template = this.getDefaultParameters(toolName);
                break;
            case 'empty':
                template = {};
                break;
        }
        
        editor.value = JSON.stringify(template, null, 2);
    }

    getMinimalParameters(toolName) {
        const minimal = {
            'clarify_research_goals': {
                research_area: 'physics',
                initial_goals: 'develop theory'
            },
            'suggest_methodology': {
                research_goals: 'theoretical research',
                domain: 'physics'
            },
            'simulate_peer_review': {
                document_content: { title: 'Test' },
                domain: 'physics'
            },
            'generate_latex_document': {
                title: 'Test Document'
            },
            'semantic_search': {
                query: 'test'
            }
        };
        
        return minimal[toolName] || {};
    }

    async runToolWithCustomParams(toolName) {
        const editor = document.getElementById('paramEditor');
        if (!editor) return;
        
        let params;
        try {
            params = JSON.parse(editor.value);
        } catch (error) {
            this.log(`Invalid JSON parameters: ${error.message}`, 'error');
            return;
        }
        
        this.closeModal();
        
        if (!this.mcpClient || !this.mcpClient.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }
        
        const toolCard = document.querySelector(`[data-tool="${toolName}"]`);
        if (toolCard) {
            toolCard.classList.add('executing');
        }
        
        this.log(`Running tool: ${toolName} with custom parameters...`);
        this.log(`Parameters: ${JSON.stringify(params, null, 2)}`);
        
        try {
            const result = await this.mcpClient.callTool(toolName, params);
            
            this.log(`✅ ${toolName} completed successfully`, 'success');
            this.log(`Response: ${JSON.stringify(result, null, 2)}`);
            
        } catch (error) {
            this.log(`❌ ${toolName} failed: ${error.message}`, 'error');
        } finally {
            if (toolCard) {
                toolCard.classList.remove('executing');
            }
        }
    }

    closeModal() {
        if (this.currentModal) {
            // Add fade out animation
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
            this.log('Refreshing tool list...');
            const toolsResult = await this.mcpClient.listTools();
            const tools = toolsResult.tools || [];
            this.availableTools = tools;
            
            this.log(`Tool list refreshed! Found ${tools.length} tools`, 'success');
            this.updateStats(tools.length);
            
            this.renderTools(tools);
            
        } catch (error) {
            this.log(`Failed to refresh tools: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(refreshBtn, null);
        }
    }

    clearConsole() {
        const console = document.getElementById('console');
        if (console) {
            console.innerHTML = `
                <div class="console-line">
                    <span class="console-timestamp">[${new Date().toLocaleTimeString()}]</span>
                    <span class="console-info">🧹 Console cleared</span>
                </div>
            `;
        }
    }

    setButtonLoading(button, loadingText) {
        if (!button) return;
        
        if (loadingText) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `<span class="loading"></span>${loadingText}`;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }

    getDefaultParameters(toolName) {
        const defaults = {
            // Research Planning & Goal Setting
            'clarify_research_goals': {
                research_area: 'theoretical_physics',
                initial_goals: 'develop new theoretical framework',
                experience_level: 'graduate',
                domain_specialization: 'theoretical_physics',
                novel_theory_mode: true
            },
            'suggest_methodology': {
                research_goals: 'theoretical framework development',
                domain: 'physics',
                novel_theory_flag: true,
                constraints: {
                    time_limit: '12 months',
                    resources: 'academic'
                }
            },
            
            // Quality Assurance & Review
            'simulate_peer_review': {
                document_content: {
                    title: 'Novel Quantum Theory Framework',
                    abstract: 'This paper presents a revolutionary approach to quantum mechanics',
                    methodology: 'Mathematical analysis and theoretical modeling',
                    results: 'New theoretical framework with experimental predictions'
                },
                domain: 'physics',
                review_type: 'comprehensive',
                novel_theory_mode: true
            },
            'check_quality_gates': {
                research_content: {
                    title: 'Research Quality Assessment',
                    methodology: 'experimental',
                    data_quality: 'high',
                    analysis_method: 'statistical'
                },
                phase: 'publication_readiness',
                domain_standards: {
                    peer_review: true,
                    reproducibility: true
                }
            },
            
            // Storage & Project Management
            'initialize_project': {
                name: 'Advanced Physics Research',
                description: 'Investigating novel quantum phenomena',
                domain: 'physics',
                project_path: '/tmp/physics_project'
            },
            'save_session': {
                session_data: {
                    research_phase: 'analysis',
                    current_findings: 'promising results',
                    next_steps: ['validate model', 'prepare manuscript']
                },
                project_path: '/tmp/physics_project'
            },
            'restore_session': {
                session_id: 1,
                project_path: '/tmp/physics_project'
            },
            'search_knowledge': {
                query: 'quantum field theory applications',
                project_path: '/tmp/physics_project',
                collection: 'research_docs'
            },
            'version_control': {
                action: 'commit',
                message: 'Added new theoretical analysis',
                project_path: '/tmp/physics_project',
                files: ['analysis.tex', 'data.json']
            },
            'backup_project': {
                project_path: '/tmp/physics_project',
                backup_location: '/tmp/backups'
            },
            'store_bibliography_reference': {
                reference: {
                    title: 'Quantum Mechanics and Path Integrals',
                    authors: ['Feynman, R.P.', 'Hibbs, A.R.'],
                    year: 1965,
                    journal: 'McGraw-Hill',
                    doi: '10.1063/1.3047720'
                },
                project_path: '/tmp/physics_project'
            },
            'retrieve_bibliography_references': {
                query: 'quantum mechanics path integrals',
                max_results: 10,
                project_path: '/tmp/physics_project'
            },
            
            // Document Generation & LaTeX
            'generate_latex_document': {
                title: 'Advanced Quantum Theory Research',
                author: 'Research Team',
                abstract: 'This document presents groundbreaking research in quantum theory',
                introduction: 'Quantum mechanics has revolutionized our understanding of nature',
                methodology: 'We employ advanced mathematical techniques and computational methods',
                results: 'Our findings reveal new aspects of quantum behavior',
                discussion: 'These results have significant implications for theoretical physics',
                conclusion: 'We have successfully developed a new theoretical framework',
                project_path: '/tmp/physics_project'
            },
            'compile_latex': {
                tex_file_path: '/tmp/physics_project/manuscript.tex',
                output_format: 'pdf'
            },
            'format_research_content': {
                content: 'This research demonstrates novel quantum effects in macroscopic systems',
                content_type: 'section',
                formatting_style: 'academic'
            },
            'generate_bibliography': {
                references: [
                    {
                        title: 'Quantum Field Theory',
                        authors: ['Peskin, M.E.', 'Schroeder, D.V.'],
                        year: 1995,
                        journal: 'Addison-Wesley'
                    },
                    {
                        title: 'The Feynman Lectures on Physics',
                        authors: ['Feynman, R.P.'],
                        year: 1964,
                        journal: 'Addison-Wesley'
                    }
                ]
            },
            'extract_document_sections': {
                document_content: 'Abstract: This paper... Introduction: Quantum mechanics... Methods: We used... Results: Our findings...'
            },
            'generate_document_with_database_bibliography': {
                title: 'Quantum Research with Database Bibliography',
                author: 'Research Team',
                abstract: 'Advanced quantum research with comprehensive bibliography',
                bibliography_query: 'quantum mechanics theoretical physics',
                project_path: '/tmp/physics_project'
            },
            
            // Search & Discovery
            'semantic_search': {
                query: 'quantum entanglement theoretical models',
                collection: 'research_docs',
                limit: 10,
                similarity_threshold: 0.7,
                project_path: '/tmp/physics_project'
            },
            'discover_patterns': {
                content: 'quantum mechanics entanglement superposition wave function collapse measurement theory',
                pattern_type: 'research_themes',
                min_frequency: 2
            },
            'build_knowledge_graph': {
                documents: [
                    'Quantum mechanics fundamentals and applications',
                    'Entanglement theory and experimental verification',
                    'Wave function collapse mechanisms'
                ],
                relationship_types: ['theoretical_basis', 'experimental_evidence', 'mathematical_framework'],
                project_path: '/tmp/physics_project'
            },
            'find_similar_documents': {
                target_document: 'Research on quantum entanglement and its applications in quantum computing',
                collection: 'research_docs',
                max_results: 5,
                similarity_threshold: 0.6,
                project_path: '/tmp/physics_project'
            },
            'extract_key_concepts': {
                text: 'quantum mechanics entanglement superposition decoherence measurement problem wave function',
                max_concepts: 15,
                concept_types: ['technical_terms', 'theories', 'methods']
            },
            'generate_research_summary': {
                documents: [
                    'Quantum mechanics provides the theoretical foundation for understanding atomic behavior',
                    'Entanglement represents a fundamental quantum phenomenon with practical applications',
                    'Measurement problems in quantum mechanics remain actively debated'
                ],
                summary_type: 'comprehensive',
                max_length: 500
            },
            
            // Methodology & Validation
            'explain_methodology': {
                research_question: 'How do quantum effects manifest in macroscopic systems?',
                domain: 'physics'
            },
            'compare_approaches': {
                approaches: ['theoretical modeling', 'experimental verification', 'computational simulation'],
                domain: 'physics',
                criteria: ['accuracy', 'feasibility', 'cost']
            },
            'validate_design': {
                research_design: {
                    methodology: 'experimental',
                    sample_size: 100,
                    controls: ['temperature', 'pressure'],
                    measurements: ['quantum state', 'coherence time']
                },
                domain: 'physics'
            },
            'ensure_ethics': {
                research_plan: {
                    methodology: 'theoretical analysis',
                    data_sources: 'published literature',
                    participants: 'none',
                    risks: 'minimal'
                },
                domain: 'physics'
            },
            
            // Novel Theory Development
            'initiate_paradigm_challenge': {
                domain: 'physics',
                current_paradigm: 'standard quantum mechanics',
                challenge_area: 'measurement problem and wave function collapse'
            },
            'develop_alternative_framework': {
                challenged_paradigm: 'Copenhagen interpretation',
                domain: 'physics',
                alternative_principles: [
                    'objective wave function collapse',
                    'hidden variable theories',
                    'many-worlds interpretation'
                ]
            },
            'compare_paradigms': {
                original_paradigm: 'classical mechanics',
                alternative_paradigm: 'quantum mechanics',
                domain: 'physics',
                comparison_criteria: ['predictive power', 'experimental support', 'mathematical elegance']
            },
            'validate_novel_theory': {
                theory_framework: {
                    name: 'Enhanced Quantum Theory',
                    principles: ['objective collapse', 'nonlocal interactions'],
                    predictions: ['modified Bell inequalities', 'new interference patterns']
                },
                domain: 'physics'
            },
            'cultivate_innovation': {
                research_context: {
                    domain: 'physics',
                    current_state: 'exploring quantum gravity',
                    challenges: ['unification', 'experimental verification'],
                    opportunities: ['new mathematical tools', 'advanced technology']
                }
            },
            'assess_foundational_assumptions': {
                theory_framework: {
                    name: 'Quantum Mechanics',
                    assumptions: ['wave-particle duality', 'uncertainty principle', 'observer effect']
                },
                domain: 'physics'
            },
            'generate_critical_questions': {
                research_area: 'quantum foundations',
                theory_framework: {
                    name: 'Standard Quantum Mechanics',
                    key_concepts: ['superposition', 'entanglement', 'measurement']
                },
                domain: 'physics'
            },
            'evaluate_paradigm_shift_potential': {
                theory_framework: {
                    name: 'Objective Collapse Theory',
                    principles: ['spontaneous wave function collapse', 'objective reality'],
                    implications: ['resolution of measurement problem', 'modified quantum predictions']
                },
                domain: 'physics'
            }
        };
        
        return defaults[toolName] || {
            // Fallback for any unknown tools
            test_parameter: 'test_value',
            domain: 'physics'
        };
    }
}

// Initialize the application when the page loads
let app;
window.addEventListener('load', () => {
    app = new SRRDFrontendApp();
});

// Export for global access
window.SRRDFrontendApp = SRRDFrontendApp;
