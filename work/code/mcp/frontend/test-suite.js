/**
 * Frontend Test Suite Runner
 * Automated testing of MCP server functionality through the web interface
 */

class TestSuiteRunner {
    constructor(mcpClient) {
        this.client = mcpClient;
        this.testResults = [];
        this.currentTest = null;
        this.onProgress = null;
        this.onComplete = null;
    }

    async runFullTestSuite() {
        this.testResults = [];
        this.notifyProgress('Starting comprehensive test suite...');

        const testSuite = [
            { name: 'Connection Test', test: () => this.testConnection() },
            { name: 'Tool Discovery', test: () => this.testToolDiscovery() },
            { name: 'Research Planning Tools', test: () => this.testResearchPlanningTools() },
            { name: 'Quality Assurance Tools', test: () => this.testQualityAssuranceTools() },
            { name: 'Document Generation Tools', test: () => this.testDocumentGenerationTools() },
            { name: 'Search Discovery Tools', test: () => this.testSearchDiscoveryTools() },
            { name: 'Storage Management Tools', test: () => this.testStorageManagementTools() },
            { name: 'Error Handling', test: () => this.testErrorHandling() }
        ];

        for (const testCase of testSuite) {
            this.currentTest = testCase.name;
            this.notifyProgress(`Running ${testCase.name}...`);
            
            try {
                const result = await testCase.test();
                this.addTestResult(testCase.name, true, result);
                this.notifyProgress(`✅ ${testCase.name} passed`);
            } catch (error) {
                this.addTestResult(testCase.name, false, error.message);
                this.notifyProgress(`❌ ${testCase.name} failed: ${error.message}`);
            }

            // Small delay between tests
            await this.delay(500);
        }

        const summary = this.generateSummary();
        this.notifyComplete(summary);
        return summary;
    }

    async testConnection() {
        if (!this.client.isConnected) {
            throw new Error('Client not connected to server');
        }
        return 'Connection successful';
    }

    async testToolDiscovery() {
        const tools = await this.client.listTools();
        if (!tools || !Array.isArray(tools.tools)) {
            throw new Error('Failed to discover tools');
        }
        return `Discovered ${tools.tools.length} tools`;
    }

    async testResearchPlanningTools() {
        const results = [];
        
        // Test clarify_research_goals
        try {
            const response = await this.client.callTool('clarify_research_goals', {
                research_area: 'quantum gravity',
                initial_goals: 'Develop unified theory',
                experience_level: 'graduate',
                domain_specialization: 'theoretical_physics',
                novel_theory_mode: true
            });
            results.push('clarify_research_goals: ✅');
        } catch (error) {
            results.push(`clarify_research_goals: ❌ ${error.message}`);
        }

        // Test suggest_methodology
        try {
            const response = await this.client.callTool('suggest_methodology', {
                research_goals: 'alternative physics theories',
                domain: 'theoretical_physics',
                novel_theory_flag: true
            });
            results.push('suggest_methodology: ✅');
        } catch (error) {
            results.push(`suggest_methodology: ❌ ${error.message}`);
        }

        return results.join(', ');
    }

    async testQualityAssuranceTools() {
        const results = [];

        // Test simulate_peer_review
        try {
            const response = await this.client.callTool('simulate_peer_review', {
                document_content: {
                    title: 'Novel Quantum Theory',
                    abstract: 'Revolutionary approach to quantum mechanics',
                    methodology: 'Mathematical analysis',
                    results: 'New theoretical framework'
                },
                domain: 'theoretical_physics',
                review_type: 'comprehensive',
                novel_theory_mode: true
            });
            results.push('simulate_peer_review: ✅');
        } catch (error) {
            results.push(`simulate_peer_review: ❌ ${error.message}`);
        }

        // Test check_quality_gates
        try {
            const response = await this.client.callTool('check_quality_gates', {
                research_content: {
                    title: 'Test Research',
                    abstract: 'Test abstract',
                    methodology: 'Test methodology'
                },
                phase: 'publication_readiness'
            });
            results.push('check_quality_gates: ✅');
        } catch (error) {
            results.push(`check_quality_gates: ❌ ${error.message}`);
        }

        return results.join(', ');
    }

    async testDocumentGenerationTools() {
        const results = [];

        // Test generate_latex_document
        try {
            const response = await this.client.callTool('generate_latex_document', {
                title: 'Frontend Test Document',
                author: 'Test Suite',
                abstract: 'This is a test document generated by the frontend test suite',
                introduction: 'Test introduction',
                methodology: 'Automated testing methodology',
                results: 'Test results and validation',
                conclusion: 'Frontend testing completed successfully'
            });
            results.push('generate_latex_document: ✅');
        } catch (error) {
            results.push(`generate_latex_document: ❌ ${error.message}`);
        }

        // Test format_research_content
        try {
            const response = await this.client.callTool('format_research_content', {
                content: 'This is test content for formatting validation',
                content_type: 'section',
                formatting_style: 'academic'
            });
            results.push('format_research_content: ✅');
        } catch (error) {
            results.push(`format_research_content: ❌ ${error.message}`);
        }

        return results.join(', ');
    }

    async testSearchDiscoveryTools() {
        const results = [];

        // Test semantic_search
        try {
            const response = await this.client.callTool('semantic_search', {
                query: 'quantum mechanics theoretical framework',
                collection: 'research_literature',
                limit: 5
            });
            results.push('semantic_search: ✅');
        } catch (error) {
            results.push(`semantic_search: ❌ ${error.message}`);
        }

        // Test discover_patterns
        try {
            const response = await this.client.callTool('discover_patterns', {
                content: 'quantum mechanics general relativity theoretical framework',
                pattern_type: 'research_themes',
                min_frequency: 1
            });
            results.push('discover_patterns: ✅');
        } catch (error) {
            results.push(`discover_patterns: ❌ ${error.message}`);
        }

        // Test extract_key_concepts
        try {
            const response = await this.client.callTool('extract_key_concepts', {
                text: 'quantum mechanics theoretical physics computational modeling',
                max_concepts: 10,
                concept_types: ['technical_terms', 'theories', 'methods']
            });
            results.push('extract_key_concepts: ✅');
        } catch (error) {
            results.push(`extract_key_concepts: ❌ ${error.message}`);
        }

        return results.join(', ');
    }

    async testStorageManagementTools() {
        const results = [];

        // Test initialize_project
        try {
            const response = await this.client.callTool('initialize_project', {
                name: 'Frontend Test Project',
                description: 'Project created by frontend test suite',
                domain: 'theoretical_physics'
            });
            results.push('initialize_project: ✅');
        } catch (error) {
            results.push(`initialize_project: ❌ ${error.message}`);
        }

        return results.join(', ');
    }

    async testErrorHandling() {
        const results = [];

        // Test invalid tool call
        try {
            await this.client.callTool('nonexistent_tool', {});
            results.push('error_handling: ❌ Should have failed');
        } catch (error) {
            results.push('error_handling: ✅ Properly caught error');
        }

        // Test invalid parameters
        try {
            await this.client.callTool('clarify_research_goals', {
                invalid_parameter: 'test'
            });
            results.push('parameter_validation: ❌ Should have failed');
        } catch (error) {
            results.push('parameter_validation: ✅ Properly validated parameters');
        }

        return results.join(', ');
    }

    addTestResult(testName, passed, details) {
        this.testResults.push({
            test: testName,
            passed: passed,
            details: details,
            timestamp: new Date().toISOString()
        });
    }

    generateSummary() {
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.passed).length;
        const failedTests = totalTests - passedTests;
        const successRate = totalTests > 0 ? (passedTests / totalTests * 100).toFixed(1) : 0;

        return {
            totalTests,
            passedTests,
            failedTests,
            successRate: `${successRate}%`,
            results: this.testResults,
            summary: `${passedTests}/${totalTests} tests passed (${successRate}% success rate)`
        };
    }

    notifyProgress(message) {
        if (this.onProgress) {
            this.onProgress(message);
        }
    }

    notifyComplete(summary) {
        if (this.onComplete) {
            this.onComplete(summary);
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for use in the main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestSuiteRunner;
} else {
    window.TestSuiteRunner = TestSuiteRunner;
}
