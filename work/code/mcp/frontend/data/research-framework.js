/**
 * SRRD-Builder Research Framework
 * Maps all 52 tools to research acts and categories
 * Provides structured navigation for scientific research workflow
 */

const RESEARCH_FRAMEWORK = {
    acts: {
        conceptualization: {
            name: 'Conceptualization',
            description: 'Defining research problems, questions, and objectives',
            icon: '🎯',
            color: '#3b82f6',
            categories: ['goal_setting', 'problem_identification', 'critical_thinking']
        },
        design_planning: {
            name: 'Design & Planning', 
            description: 'Methodology selection and research design',
            icon: '📋',
            color: '#8b5cf6',
            categories: ['methodology', 'experimental_design', 'ethics_validation']
        },
        knowledge_acquisition: {
            name: 'Knowledge Acquisition',
            description: 'Literature review and data gathering',
            icon: '📚',
            color: '#10b981',
            categories: ['literature_search', 'data_collection', 'source_management']
        },
        analysis_synthesis: {
            name: 'Analysis & Synthesis',
            description: 'Data processing and interpretation',
            icon: '🔬',
            color: '#f59e0b',
            categories: ['data_analysis', 'pattern_recognition', 'semantic_analysis', 'knowledge_building']
        },
        validation_refinement: {
            name: 'Validation & Refinement',
            description: 'Quality assurance and improvement',
            icon: '✅',
            color: '#ef4444',
            categories: ['peer_review', 'quality_control', 'paradigm_validation']
        },
        communication: {
            name: 'Communication & Dissemination',
            description: 'Writing, formatting, and publishing',
            icon: '📄',
            color: '#06b6d4',
            categories: ['document_generation', 'formatting', 'project_management', 'workflow_tracking']
        }
    },

    categories: {
        // CONCEPTUALIZATION
        goal_setting: {
            name: 'Goal Setting',
            description: 'Define and refine research objectives',
            icon: '🎯',
            act: 'conceptualization',
            tools: ['clarify_research_goals', 'enhanced_socratic_dialogue']
        },
        problem_identification: {
            name: 'Problem Identification', 
            description: 'Identify and frame research problems',
            icon: '❓',
            act: 'conceptualization',
            tools: ['initiate_paradigm_challenge']
        },
        critical_thinking: {
            name: 'Critical Thinking',
            description: 'Question assumptions and generate critical questions',
            icon: '🤔',
            act: 'conceptualization',
            tools: ['assess_foundational_assumptions', 'generate_critical_questions', 'enhanced_theory_challenger']
        },

        // DESIGN & PLANNING
        methodology: {
            name: 'Methodology',
            description: 'Research method selection and design',
            icon: '🔧',
            act: 'design_planning',
            tools: ['suggest_methodology', 'explain_methodology', 'compare_approaches']
        },
        experimental_design: {
            name: 'Experimental Design',
            description: 'Design experiments and studies',
            icon: '⚗️',
            act: 'design_planning', 
            tools: ['validate_design']
        },
        ethics_validation: {
            name: 'Ethics Validation',
            description: 'Ensure ethical research practices',
            icon: '⚖️',
            act: 'design_planning',
            tools: ['ensure_ethics']
        },

        // KNOWLEDGE ACQUISITION
        literature_search: {
            name: 'Literature Search',
            description: 'Find and organize research literature',
            icon: '🔍',
            act: 'knowledge_acquisition',
            tools: ['semantic_search']
        },
        data_collection: {
            name: 'Data Collection',
            description: 'Gather research data and sources',
            icon: '📊',
            act: 'knowledge_acquisition',
            tools: ['extract_key_concepts', 'generate_research_summary']
        },
        source_management: {
            name: 'Source Management',
            description: 'Organize and manage references',
            icon: '📚',
            act: 'knowledge_acquisition',
            tools: ['store_bibliography_reference', 'retrieve_bibliography_references']
        },

        // ANALYSIS & SYNTHESIS
        data_analysis: {
            name: 'Data Analysis',
            description: 'Statistical and computational analysis',
            icon: '📈',
            act: 'analysis_synthesis',
            tools: ['discover_patterns', 'extract_document_sections']
        },
        pattern_recognition: {
            name: 'Pattern Recognition',
            description: 'Identify patterns and relationships',
            icon: '🧩',
            act: 'analysis_synthesis',
            tools: ['find_similar_documents']
        },
        semantic_analysis: {
            name: 'Semantic Analysis',
            description: 'Meaning and concept analysis',
            icon: '🧠',
            act: 'analysis_synthesis',
            tools: ['build_knowledge_graph']
        },
        knowledge_building: {
            name: 'Knowledge Building',
            description: 'Synthesize information and build new knowledge',
            icon: '🏗️',
            act: 'analysis_synthesis',
            tools: ['develop_alternative_framework', 'compare_paradigms']
        },

        // VALIDATION & REFINEMENT
        peer_review: {
            name: 'Peer Review',
            description: 'Quality assessment and feedback',
            icon: '👥',
            act: 'validation_refinement',
            tools: ['simulate_peer_review']
        },
        quality_control: {
            name: 'Quality Control',
            description: 'Ensure research quality and integrity',
            icon: '🛡️',
            act: 'validation_refinement',
            tools: ['check_quality_gates']
        },
        paradigm_validation: {
            name: 'Paradigm Validation',
            description: 'Validate novel theories and paradigm shifts',
            icon: '🔄',
            act: 'validation_refinement',
            tools: ['validate_novel_theory', 'evaluate_paradigm_shift_potential', 'cultivate_innovation']
        },

        // COMMUNICATION
        document_generation: {
            name: 'Document Generation',
            description: 'Create research documents',
            icon: '📝',
            act: 'communication',
            tools: ['generate_latex_document', 'generate_document_with_database_bibliography', 'list_latex_templates', 'generate_latex_with_template']
        },
        formatting: {
            name: 'Formatting',
            description: 'Format documents and citations',
            icon: '✏️',
            act: 'communication',
            tools: ['compile_latex', 'format_research_content', 'generate_bibliography']
        },
        project_management: {
            name: 'Project Management',
            description: 'Manage research projects and data',
            icon: '📁',
            act: 'communication',
            tools: ['initialize_project', 'save_session', 'restore_session', 'search_knowledge', 'version_control', 'backup_project', 'switch_project_context', 'reset_project_context']
        },
        workflow_tracking: {
            name: 'Workflow Tracking',
            description: 'Track research progress and workflow guidance',
            icon: '🔄',
            act: 'communication',
            tools: ['get_research_progress', 'get_tool_usage_history', 'get_workflow_recommendations', 'get_research_milestones', 'start_research_session', 'get_session_summary', 'get_research_act_guidance', 'get_contextual_recommendations', 'get_visual_progress_summary', 'detect_and_celebrate_milestones']
        }
    }
};

// Validation: Count all tools to ensure we have all 50
const allTools = Object.values(RESEARCH_FRAMEWORK.categories)
    .flatMap(category => category.tools);

const uniqueTools = [...new Set(allTools)];

console.log(`Framework includes ${uniqueTools.length} tools:`, uniqueTools.sort());

// Expected 52 tools (as identified from codebase):
const expectedTools = [
    'assess_foundational_assumptions',
    'backup_project', 
    'build_knowledge_graph',
    'check_quality_gates',
    'clarify_research_goals',
    'compare_approaches',
    'compare_paradigms',
    'compile_latex',
    'cultivate_innovation',
    'detect_and_celebrate_milestones',
    'develop_alternative_framework',
    'discover_patterns',
    'enhanced_socratic_dialogue',
    'enhanced_theory_challenger',
    'ensure_ethics',
    'evaluate_paradigm_shift_potential',
    'explain_methodology',
    'extract_document_sections',
    'extract_key_concepts',
    'find_similar_documents',
    'format_research_content',
    'generate_bibliography',
    'generate_critical_questions',
    'generate_document_with_database_bibliography',
    'generate_latex_document',
    'generate_latex_with_template',
    'generate_research_summary',
    'get_contextual_recommendations',
    'get_research_act_guidance',
    'get_research_milestones',
    'get_research_progress', 
    'get_session_summary',
    'get_tool_usage_history',
    'get_visual_progress_summary',
    'get_workflow_recommendations',
    'initialize_project',
    'initiate_paradigm_challenge',
    'list_latex_templates',
    'reset_project_context',
    'restore_session',
    'retrieve_bibliography_references',
    'save_session',
    'search_knowledge',
    'semantic_search',
    'simulate_peer_review',
    'start_research_session',
    'store_bibliography_reference',
    'suggest_methodology',
    'switch_project_context',
    'validate_design',
    'validate_novel_theory',
    'version_control'
];

// Verify we have all tools
const missingTools = expectedTools.filter(tool => !uniqueTools.includes(tool));
const extraTools = uniqueTools.filter(tool => !expectedTools.includes(tool));

if (missingTools.length > 0) {
    console.error('Missing tools:', missingTools);
}
if (extraTools.length > 0) {
    console.error('Extra tools:', extraTools);
}
if (missingTools.length === 0 && extraTools.length === 0) {
    console.log('✅ All 52 tools successfully mapped to framework!');
}

// Make available for import
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RESEARCH_FRAMEWORK;
} else if (typeof window !== 'undefined') {
    window.RESEARCH_FRAMEWORK = RESEARCH_FRAMEWORK;
}
