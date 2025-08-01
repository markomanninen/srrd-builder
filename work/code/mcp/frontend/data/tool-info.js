/**
 * SRRD-Builder Tool Information Database
 * Comprehensive information for all 52 research tools
 * Used for help modals and user guidance
 */

const TOOL_INFO_DATABASE = {
    // CONCEPTUALIZATION TOOLS
    'clarify_research_goals': {
        title: 'Clarify Research Goals',
        purpose: 'Helps researchers define and refine their research objectives through Socratic questioning methodology.',
        context: 'Essential for establishing clear, measurable, and achievable research objectives that form the foundation of rigorous scientific inquiry.',
        usage: 'Interactive tool that guides you through defining research questions and hypotheses using proven questioning techniques.',
        examples: [
            'Refine broad research interests into specific, testable hypotheses',
            'Identify potential gaps in research question formulation',
            'Develop SMART research objectives',
            'Clarify research scope and boundaries'
        ],
        tags: ['Research Planning', 'Goal Setting', 'Socratic Method']
    },

    'enhanced_socratic_dialogue': {
        title: 'Enhanced Socratic Dialogue',
        purpose: 'Progressive conversational guidance with depth-controlled questioning and user response analysis.',
        context: 'Advanced interactive dialogue system that adapts questioning depth based on user responses and provides sophisticated analysis of research thinking.',
        usage: 'Engages in multi-depth Socratic conversations, analyzing your responses to provide contextual follow-up questions and personalized guidance.',
        examples: [
            'Progressive questioning from clarification to validation',
            'User response analysis for technical sophistication',
            'Domain-specific question banks for targeted guidance',
            'Contextual follow-up generation based on uncertainty levels'
        ],
        tags: ['Enhanced Dialogue', 'Response Analysis', 'Progressive Questioning', 'Conversational AI']
    },

    'enhanced_theory_challenger': {
        title: 'Enhanced Theory Challenger',
        purpose: 'Critical examination tool with progressive challenge levels and paradigm implication analysis.',
        context: 'Advanced theory validation system that provides escalating levels of critical examination and analyzes paradigm implications.',
        usage: 'Challenges theories with adjustable intensity levels while analyzing paradigm implications and integration difficulties.',
        examples: [
            'Progressive challenge levels from gentle to rigorous',
            'Paradigm implication analysis and classification',
            'Integration difficulty assessment',
            'Critical challenge generation based on theory characteristics'
        ],
        tags: ['Theory Validation', 'Critical Analysis', 'Paradigm Assessment', 'Progressive Challenges']
    },

    'initiate_paradigm_challenge': {
        title: 'Initiate Paradigm Challenge',
        purpose: 'Systematically challenges existing paradigms to identify opportunities for groundbreaking research.',
        context: 'Facilitates paradigm-shifting research by questioning fundamental assumptions in your field.',
        usage: 'Guides you through a structured process to challenge established theories and identify research opportunities.',
        examples: [
            'Challenge foundational assumptions in your research domain',
            'Identify paradigm shift opportunities',
            'Question established theoretical frameworks',
            'Explore alternative perspectives on existing problems'
        ],
        tags: ['Paradigm Shift', 'Innovation', 'Critical Thinking']
    },

    'assess_foundational_assumptions': {
        title: 'Assess Foundational Assumptions',
        purpose: 'Systematically examines and evaluates the foundational assumptions underlying research theories.',
        context: 'Critical for ensuring research validity by identifying and examining taken-for-granted assumptions.',
        usage: 'Provides structured analysis of assumptions that underpin your research approach and theoretical framework.',
        examples: [
            'Identify hidden assumptions in research methodology',
            'Evaluate the validity of theoretical foundations',
            'Question implicit biases in research design',
            'Assess philosophical underpinnings of your approach'
        ],
        tags: ['Critical Analysis', 'Assumptions', 'Research Validity']
    },

    'generate_critical_questions': {
        title: 'Generate Critical Questions',
        purpose: 'Generates thought-provoking questions to deepen research inquiry and challenge conventional thinking.',
        context: 'Enhances research depth by providing critical questions that push beyond surface-level analysis.',
        usage: 'Generates targeted questions to guide deeper investigation and critical analysis of research topics.',
        examples: [
            'Generate probing questions for research investigation',
            'Challenge surface-level understanding',
            'Identify areas needing deeper exploration',
            'Develop questions that reveal hidden complexities'
        ],
        tags: ['Critical Thinking', 'Question Generation', 'Research Depth']
    },

    // DESIGN & PLANNING TOOLS
    'suggest_methodology': {
        title: 'Suggest Research Methodology',
        purpose: 'Recommends appropriate research methodologies based on your research goals and domain.',
        context: 'Ensures methodological rigor by suggesting evidence-based approaches suitable for your specific research domain and objectives.',
        usage: 'Analyzes your research goals and provides tailored methodology recommendations with justifications.',
        examples: [
            'Get methodology suggestions for experimental vs. observational studies',
            'Receive guidance on sample size and data collection methods',
            'Understand pros and cons of different research approaches',
            'Match methodology to research questions and constraints'
        ],
        tags: ['Methodology', 'Research Design', 'Domain-Specific']
    },

    'explain_methodology': {
        title: 'Explain Methodology',
        purpose: 'Provides detailed explanations of research methodologies and their applications.',
        context: 'Helps researchers understand the theoretical foundations and practical applications of different methodologies.',
        usage: 'Offers comprehensive explanations of methodology concepts, principles, and implementation strategies.',
        examples: [
            'Understand the principles behind specific methodologies',
            'Learn when and how to apply different research approaches',
            'Get detailed explanations of methodological concepts',
            'Explore methodology variations and adaptations'
        ],
        tags: ['Methodology', 'Education', 'Research Methods']
    },

    'compare_approaches': {
        title: 'Compare Research Approaches',
        purpose: 'Systematically compares different research approaches to help select the most appropriate method.',
        context: 'Supports informed decision-making by providing detailed comparisons of research methodologies.',
        usage: 'Compares multiple research approaches across various dimensions to guide methodology selection.',
        examples: [
            'Compare quantitative vs. qualitative approaches',
            'Evaluate different experimental designs',
            'Analyze trade-offs between methodological choices',
            'Select optimal approach for specific research contexts'
        ],
        tags: ['Methodology Comparison', 'Research Design', 'Decision Support']
    },

    'validate_design': {
        title: 'Validate Research Design',
        purpose: 'Evaluates and validates research designs for methodological soundness and feasibility.',
        context: 'Ensures research quality by identifying potential design flaws and suggesting improvements.',
        usage: 'Provides systematic validation of research designs against established criteria and best practices.',
        examples: [
            'Validate experimental design for internal validity',
            'Check research design for potential confounding factors',
            'Assess feasibility of proposed methodology',
            'Identify design improvements and refinements'
        ],
        tags: ['Design Validation', 'Research Quality', 'Methodology']
    },

    'ensure_ethics': {
        title: 'Ensure Research Ethics',
        purpose: 'Evaluates research proposals for ethical considerations and compliance requirements.',
        context: 'Critical for responsible research conduct and institutional compliance with ethical standards.',
        usage: 'Provides guidance on ethical considerations and helps ensure research meets ethical standards.',
        examples: [
            'Evaluate research for ethical concerns',
            'Identify potential risks to participants',
            'Assess compliance with ethical guidelines',
            'Develop ethical safeguards and protocols'
        ],
        tags: ['Research Ethics', 'Compliance', 'Risk Assessment']
    },

    // KNOWLEDGE ACQUISITION TOOLS
    'semantic_search': {
        title: 'Semantic Search',
        purpose: 'Performs intelligent content search using semantic understanding rather than just keywords.',
        context: 'Enables discovery of related research, concepts, and connections that traditional keyword search might miss.',
        usage: 'Search your research database for conceptually related content and discover hidden connections between ideas.',
        examples: [
            'Find related concepts even when exact terms differ',
            'Discover connections between seemingly unrelated research areas',
            'Locate relevant sources using natural language queries',
            'Identify thematically similar research papers'
        ],
        tags: ['Knowledge Discovery', 'Semantic Analysis', 'Research Connections']
    },

    'extract_key_concepts': {
        title: 'Extract Key Concepts',
        purpose: 'Automatically identifies and extracts key concepts from research texts and documents.',
        context: 'Facilitates rapid analysis of large volumes of text by identifying central concepts and themes.',
        usage: 'Processes research documents to identify and extract the most important concepts and terminology.',
        examples: [
            'Extract key terms from research papers',
            'Identify central concepts in literature reviews',
            'Generate concept maps from text documents',
            'Create glossaries of important terminology'
        ],
        tags: ['Text Analysis', 'Concept Extraction', 'Content Analysis']
    },

    'generate_research_summary': {
        title: 'Generate Research Summary',
        purpose: 'Creates comprehensive summaries of research documents and literature collections.',
        context: 'Helps researchers quickly understand and synthesize large volumes of research content.',
        usage: 'Generates structured summaries that capture key findings, methods, and implications from research documents.',
        examples: [
            'Summarize multiple research papers on a topic',
            'Create executive summaries of research findings',
            'Generate abstracts from full research documents',
            'Synthesize key points from literature collections'
        ],
        tags: ['Text Summarization', 'Literature Review', 'Research Synthesis']
    },

    'store_bibliography_reference': {
        title: 'Store Bibliography Reference',
        purpose: 'Stores and manages bibliography references in a structured, searchable format.',
        context: 'Essential for maintaining organized and accessible reference collections for research projects.',
        usage: 'Allows systematic storage and organization of research references with metadata and searchable content.',
        examples: [
            'Store research papers with full metadata',
            'Organize references by topic or project',
            'Maintain searchable bibliography database',
            'Track citation information and sources'
        ],
        tags: ['Reference Management', 'Bibliography', 'Source Organization']
    },

    'retrieve_bibliography_references': {
        title: 'Retrieve Bibliography References',
        purpose: 'Retrieves relevant references from stored bibliography database using intelligent search.',
        context: 'Enables efficient access to previously stored references based on research needs and topics.',
        usage: 'Searches and retrieves relevant bibliography references based on queries and research context.',
        examples: [
            'Find references relevant to current research topic',
            'Retrieve citations for specific research areas',
            'Locate previously stored sources by content',
            'Build targeted bibliography for manuscripts'
        ],
        tags: ['Reference Retrieval', 'Bibliography Search', 'Source Discovery']
    },

    'switch_project_context': {
        title: 'Switch Project Context',
        purpose: 'Switch MCP context to a different SRRD project for focused research work.',
        context: 'Essential for working on multiple research projects by switching the active project context.',
        usage: 'Changes the active project context so all subsequent tool calls use the target project\'s database and files.',
        examples: [
            'Switch to a specific research project by path',
            'Change active project for focused research work',
            'Access project-specific databases and files',
            'Organize research work by project boundaries'
        ],
        tags: ['Project Management', 'Context Switching', 'Project Organization']
    },

    'reset_project_context': {
        title: 'Reset Project Context',
        purpose: 'Reset MCP context to the global home project (neutral state).',
        context: 'Returns to the default global project context, removing any project-specific scoping.',
        usage: 'Removes project-specific context and returns to the global default state for general research work.',
        examples: [
            'Return to global research mode',
            'Clear project-specific context',
            'Access global research tools and databases',
            'Switch from project mode to general mode'
        ],
        tags: ['Project Management', 'Context Reset', 'Global Mode']
    },

    // ANALYSIS & SYNTHESIS TOOLS
    'discover_patterns': {
        title: 'Discover Patterns',
        purpose: 'Identifies patterns, themes, and relationships within research content and data.',
        context: 'Supports data analysis and interpretation by revealing hidden patterns and trends in research materials.',
        usage: 'Analyzes research content to identify recurring patterns, themes, and significant relationships.',
        examples: [
            'Identify recurring themes in qualitative data',
            'Discover patterns in research findings',
            'Recognize trends across multiple studies',
            'Find relationships between research variables'
        ],
        tags: ['Pattern Recognition', 'Data Analysis', 'Theme Identification']
    },

    'extract_document_sections': {
        title: 'Extract Document Sections',
        purpose: 'Automatically identifies and extracts sections from research documents for analysis.',
        context: 'Facilitates document analysis by systematically breaking down research papers into component sections.',
        usage: 'Processes research documents to identify and extract standard sections like introduction, methods, results.',
        examples: [
            'Extract methodology sections from research papers',
            'Identify results sections across multiple studies',
            'Separate introduction and discussion sections',
            'Organize document content by structural elements'
        ],
        tags: ['Document Analysis', 'Content Extraction', 'Document Structure']
    },

    'find_similar_documents': {
        title: 'Find Similar Documents',
        purpose: 'Identifies documents similar to a target document based on content and semantic similarity.',
        context: 'Enables discovery of related research by finding documents with similar content, themes, or approaches.',
        usage: 'Compares documents to find similar research based on content analysis and semantic understanding.',
        examples: [
            'Find papers similar to your current research',
            'Identify related studies in your field',
            'Discover papers with similar methodologies',
            'Locate research addressing similar problems'
        ],
        tags: ['Similarity Analysis', 'Document Comparison', 'Related Research']
    },

    'build_knowledge_graph': {
        title: 'Build Knowledge Graph',
        purpose: 'Creates visual knowledge graphs showing relationships between research concepts and entities.',
        context: 'Facilitates understanding of complex research domains by mapping relationships between key concepts.',
        usage: 'Constructs interactive knowledge graphs that visualize connections between research concepts and findings.',
        examples: [
            'Map relationships between research concepts',
            'Visualize connections in research literature',
            'Create concept networks for research domains',
            'Build interactive knowledge maps'
        ],
        tags: ['Knowledge Mapping', 'Visualization', 'Concept Networks']
    },

    'develop_alternative_framework': {
        title: 'Develop Alternative Framework',
        purpose: 'Assists in developing new theoretical frameworks and alternative conceptual approaches.',
        context: 'Supports innovative research by helping create novel theoretical frameworks and conceptual models.',
        usage: 'Guides the development of new theoretical frameworks that challenge or extend existing approaches.',
        examples: [
            'Create new theoretical models',
            'Develop alternative conceptual frameworks',
            'Design novel research paradigms',
            'Build innovative theoretical approaches'
        ],
        tags: ['Theory Development', 'Innovation', 'Conceptual Framework']
    },

    'compare_paradigms': {
        title: 'Compare Research Paradigms',
        purpose: 'Systematically compares different research paradigms and theoretical frameworks.',
        context: 'Helps researchers understand paradigmatic differences and select appropriate theoretical foundations.',
        usage: 'Provides detailed comparisons of research paradigms across philosophical and methodological dimensions.',
        examples: [
            'Compare positivist vs. interpretivist paradigms',
            'Analyze differences between theoretical frameworks',
            'Evaluate paradigmatic assumptions and implications',
            'Select appropriate paradigm for research context'
        ],
        tags: ['Paradigm Analysis', 'Theoretical Comparison', 'Research Philosophy']
    },

    // VALIDATION & REFINEMENT TOOLS
    'simulate_peer_review': {
        title: 'Simulate Peer Review',
        purpose: 'Provides AI-powered peer review simulation to identify potential issues before submission.',
        context: 'Mimics the academic peer review process to improve manuscript quality and increase publication success rates.',
        usage: 'Submit your research content for comprehensive review covering methodology, validity, clarity, and academic standards.',
        examples: [
            'Identify methodological weaknesses before submission',
            'Get feedback on clarity and structure of arguments',
            'Check for missing citations or unsupported claims',
            'Assess manuscript readiness for publication'
        ],
        tags: ['Quality Assurance', 'Peer Review', 'Publication Readiness']
    },

    'check_quality_gates': {
        title: 'Check Quality Gates',
        purpose: 'Evaluates research against quality standards and gates at different phases of the research process.',
        context: 'Ensures research quality by systematically checking against established criteria and best practices.',
        usage: 'Provides structured quality assessment across different phases of research from planning to publication.',
        examples: [
            'Validate research design quality',
            'Check methodology against standards',
            'Assess manuscript quality before submission',
            'Evaluate research rigor and completeness'
        ],
        tags: ['Quality Control', 'Research Standards', 'Quality Assurance']
    },

    'validate_novel_theory': {
        title: 'Validate Novel Theory',
        purpose: 'Systematically validates novel theories and theoretical contributions for coherence and impact.',
        context: 'Critical for groundbreaking research that proposes new theories or challenges existing paradigms.',
        usage: 'Provides comprehensive validation of novel theoretical contributions using established criteria.',
        examples: [
            'Validate new theoretical propositions',
            'Assess coherence of novel frameworks',
            'Evaluate potential impact of new theories',
            'Check theoretical consistency and logic'
        ],
        tags: ['Theory Validation', 'Innovation Assessment', 'Theoretical Rigor']
    },

    'evaluate_paradigm_shift_potential': {
        title: 'Evaluate Paradigm Shift Potential',
        purpose: 'Assesses the potential for research to create significant paradigm shifts in the field.',
        context: 'Identifies research with transformative potential that could fundamentally change field understanding.',
        usage: 'Evaluates research contributions for their potential to create paradigmatic changes in the field.',
        examples: [
            'Assess revolutionary potential of research',
            'Identify paradigm-shifting contributions',
            'Evaluate transformative impact potential',
            'Measure innovation significance'
        ],
        tags: ['Paradigm Shift', 'Innovation Impact', 'Transformative Research']
    },

    'cultivate_innovation': {
        title: 'Cultivate Innovation',
        purpose: 'Fosters innovative thinking and helps develop creative approaches to research problems.',
        context: 'Enhances research creativity by providing techniques and frameworks for innovative problem-solving.',
        usage: 'Guides researchers through processes designed to enhance creativity and generate innovative solutions.',
        examples: [
            'Generate creative research approaches',
            'Develop innovative problem-solving strategies',
            'Foster out-of-the-box thinking',
            'Create novel research methodologies'
        ],
        tags: ['Innovation', 'Creativity', 'Problem Solving']
    },

    // COMMUNICATION TOOLS
    'generate_latex_document': {
        title: 'Generate LaTeX Document',
        purpose: 'Creates professionally formatted LaTeX documents for academic publication.',
        context: 'Produces publication-ready documents following academic standards and journal formatting requirements.',
        usage: 'Generate structured academic documents with proper formatting, citations, mathematical notation, and reference management.',
        examples: [
            'Create conference paper templates with proper formatting',
            'Generate thesis chapters with consistent styling',
            'Produce journal articles following specific style guides',
            'Format manuscripts for academic submission'
        ],
        tags: ['Document Generation', 'Academic Writing', 'LaTeX', 'Publication']
    },

    'generate_document_with_database_bibliography': {
        title: 'Generate Document with Database Bibliography',
        purpose: 'Creates LaTeX documents with bibliographies automatically retrieved from reference database.',
        context: 'Streamlines document creation by integrating stored references directly into formatted manuscripts.',
        usage: 'Combines document generation with intelligent bibliography retrieval for seamless manuscript creation.',
        examples: [
            'Generate papers with automatically populated references',
            'Create documents with targeted bibliography sections',
            'Integrate stored references into new manuscripts',
            'Produce citation-rich documents efficiently'
        ],
        tags: ['Document Generation', 'Bibliography Integration', 'Automated Formatting']
    },

    'list_latex_templates': {
        title: 'List LaTeX Templates',
        purpose: 'Provides access to various LaTeX document templates for different academic purposes.',
        context: 'Offers standardized templates that ensure proper formatting for different types of academic documents.',
        usage: 'Browse and select from available LaTeX templates suited to specific document types and requirements.',
        examples: [
            'View available journal article templates',
            'Select conference paper formats',
            'Choose thesis and dissertation templates',
            'Access specialized document formats'
        ],
        tags: ['Document Templates', 'LaTeX', 'Academic Formatting']
    },

    'generate_latex_with_template': {
        title: 'Generate LaTeX with Template',
        purpose: 'Creates LaTeX documents using specific templates for consistent formatting.',
        context: 'Ensures documents meet specific formatting requirements by using established templates.',
        usage: 'Generate documents using predefined templates that match journal, conference, or institutional requirements.',
        examples: [
            'Create journal articles with specific formatting',
            'Generate conference papers using conference templates',
            'Produce thesis documents with institutional formatting',
            'Format manuscripts according to publisher requirements'
        ],
        tags: ['Template-based Generation', 'Document Formatting', 'Academic Standards']
    },

    'compile_latex': {
        title: 'Compile LaTeX',
        purpose: 'Compiles LaTeX documents to PDF format with proper formatting and typesetting.',
        context: 'Essential for producing final PDF versions of academic documents from LaTeX source files.',
        usage: 'Processes LaTeX files to generate publication-ready PDF documents with proper formatting.',
        examples: [
            'Compile research papers to PDF format',
            'Generate final versions of academic manuscripts',
            'Process LaTeX files for publication submission',
            'Create properly formatted PDF documents'
        ],
        tags: ['Document Compilation', 'PDF Generation', 'LaTeX Processing']
    },

    'format_research_content': {
        title: 'Format Research Content',
        purpose: 'Formats research content according to academic standards and style guidelines.',
        context: 'Ensures research content meets professional presentation standards for academic communication.',
        usage: 'Applies consistent formatting to research content including equations, citations, and structural elements.',
        examples: [
            'Format equations and mathematical expressions',
            'Apply consistent citation formatting',
            'Structure content according to academic conventions',
            'Ensure professional presentation standards'
        ],
        tags: ['Content Formatting', 'Academic Standards', 'Professional Presentation']
    },

    'generate_bibliography': {
        title: 'Generate Bibliography',
        purpose: 'Creates properly formatted bibliography sections from reference lists.',
        context: 'Produces citation lists that meet academic formatting standards and journal requirements.',
        usage: 'Generates formatted bibliography sections in various citation styles for academic documents.',
        examples: [
            'Create APA-formatted reference lists',
            'Generate MLA bibliography sections',
            'Format citations for specific journals',
            'Produce consistent reference formatting'
        ],
        tags: ['Bibliography Generation', 'Citation Formatting', 'Reference Management']
    },

    // PROJECT MANAGEMENT TOOLS
    'initialize_project': {
        title: 'Initialize Research Project',
        purpose: 'Sets up new research projects with proper structure and version control.',
        context: 'Establishes organized project foundations with proper file structure and management systems.',
        usage: 'Creates new research projects with standardized organization and integrated management tools.',
        examples: [
            'Set up new research project directories',
            'Initialize version control for research projects',
            'Create project templates and structures',
            'Establish project documentation frameworks'
        ],
        tags: ['Project Setup', 'Organization', 'Version Control']
    },

    'save_session': {
        title: 'Save Research Session',
        purpose: 'Saves current research session data and progress for later continuation.',
        context: 'Preserves research work and enables seamless continuation of research activities.',
        usage: 'Captures and stores current research state including data, analyses, and progress.',
        examples: [
            'Save current research progress',
            'Store session data for later access',
            'Preserve work across research sessions',
            'Maintain continuity in research workflow'
        ],
        tags: ['Session Management', 'Data Persistence', 'Workflow Continuity']
    },

    'restore_session': {
        title: 'Restore Research Session',
        purpose: 'Restores previously saved research sessions to continue work where left off.',
        context: 'Enables seamless continuation of research work by restoring previous session states.',
        usage: 'Loads previously saved research sessions with all associated data and progress.',
        examples: [
            'Continue previous research sessions',
            'Restore saved research progress',
            'Access historical research data',
            'Resume interrupted research workflows'
        ],
        tags: ['Session Restoration', 'Workflow Continuity', 'Data Recovery']
    },

    'search_knowledge': {
        title: 'Search Knowledge Base',
        purpose: 'Searches project knowledge bases and research databases for relevant information.',
        context: 'Provides efficient access to accumulated research knowledge and project-specific information.',
        usage: 'Searches across project databases to find relevant research content and previously stored information.',
        examples: [
            'Search project-specific research databases',
            'Find relevant information in knowledge bases',
            'Access previously stored research content',
            'Query project repositories for specific information'
        ],
        tags: ['Knowledge Search', 'Information Retrieval', 'Database Query']
    },

    'version_control': {
        title: 'Version Control Operations',
        purpose: 'Manages version control operations for research projects using Git.',
        context: 'Essential for tracking changes and maintaining research project integrity over time.',
        usage: 'Provides Git-based version control for research projects including commits, branches, and collaboration.',
        examples: [
            'Commit research changes to version control',
            'Create branches for experimental research',
            'Merge collaborative research contributions',
            'Track project history and changes'
        ],
        tags: ['Version Control', 'Git Operations', 'Project Management']
    },

    'backup_project': {
        title: 'Backup Research Project',
        purpose: 'Creates backups of research projects to ensure data safety and recovery capability.',
        context: 'Critical for protecting research work against data loss and ensuring project continuity.',
        usage: 'Creates comprehensive backups of research projects including all data, analyses, and documentation.',
        examples: [
            'Create full project backups',
            'Ensure data safety and recovery capability',
            'Archive completed research projects',
            'Protect against data loss'
        ],
        tags: ['Data Backup', 'Project Safety', 'Data Protection']
    },

    'get_research_act_guidance': {
        title: 'Get Research Act Guidance',
        purpose: 'Provides structured guidance for specific research acts with experience-tailored recommendations.',
        context: 'Essential for understanding research act requirements, progress tracking, and getting personalized guidance based on user experience level.',
        usage: 'Interactive tool that provides comprehensive guidance for research acts including activities, success criteria, challenges, and next steps.',
        examples: [
            'Get detailed guidance for conceptualization phase',
            'Understand design planning requirements and activities',
            'Track progress within specific research acts',
            'Receive experience-level tailored recommendations',
            'Identify next steps based on current progress'
        ],
        tags: ['Workflow Guidance', 'Research Acts', 'Progress Tracking', 'Personalized Recommendations']
    },

    'get_contextual_recommendations': {
        title: 'Get Contextual Recommendations',
        purpose: 'Provides intelligent tool recommendations based on recent usage patterns and research context.',
        context: 'Advanced recommendation engine that analyzes tool usage patterns to suggest contextually appropriate next steps.',
        usage: 'Interactive tool that examines recent activity patterns and provides prioritized recommendations with confidence scores.',
        examples: [
            'Get recommendations based on recent tool usage patterns',
            'Analyze workflow patterns for optimization suggestions',
            'Receive confidence-scored tool recommendations',
            'Get alternative research approaches and paths',
            'Understand rationale behind recommended next steps'
        ],
        tags: ['Smart Recommendations', 'Pattern Analysis', 'Workflow Intelligence', 'Contextual Guidance']
    },

    'get_research_progress': {
        title: 'Get Research Progress',
        purpose: 'Retrieves comprehensive research progress across all acts and categories.',
        context: 'Essential for tracking overall research advancement and identifying completed milestones.',
        usage: 'Provides detailed progress analysis showing completion percentages, tool usage statistics, and research velocity.',
        examples: [
            'View overall research progress across all acts',
            'Track completion percentages by research category',
            'Monitor research velocity and workflow health',
            'Identify gaps in research workflow'
        ],
        tags: ['Progress Tracking', 'Research Analytics', 'Workflow Monitoring']
    },

    'get_tool_usage_history': {
        title: 'Get Tool Usage History',
        purpose: 'Provides chronological history of tool usage for session or project analysis.',
        context: 'Critical for understanding research workflow patterns and tool effectiveness.',
        usage: 'Interactive tool that displays tool usage timeline with execution details and success rates.',
        examples: [
            'View chronological tool usage for current session',
            'Analyze tool usage patterns over time',
            'Track tool success rates and execution times',
            'Identify most frequently used research tools'
        ],
        tags: ['Usage Analytics', 'Tool Tracking', 'Session History']
    },

    'get_workflow_recommendations': {
        title: 'Get Workflow Recommendations',  
        purpose: 'Generates AI-powered recommendations for next research steps based on current progress.',
        context: 'Advanced workflow guidance system that suggests optimal next steps based on research framework analysis.',
        usage: 'Provides intelligent suggestions for research progression with priority rankings and rationale.',
        examples: [
            'Get AI-generated next step recommendations',
            'Receive priority-ranked workflow suggestions',
            'Understand rationale behind recommended actions',
            'Optimize research workflow progression'
        ],
        tags: ['AI Recommendations', 'Workflow Optimization', 'Research Guidance']
    },

    'get_research_milestones': {
        title: 'Get Research Milestones',
        purpose: 'Retrieves achieved research milestones and upcoming targets for project tracking.',
        context: 'Essential for celebrating achievements and setting realistic future goals in research projects.',
        usage: 'Displays completed milestones with achievement dates and suggests upcoming milestone targets.',
        examples: [
            'View achieved research milestones with dates',
            'Track milestone completion progress',
            'Get suggestions for upcoming milestone targets',
            'Celebrate research achievements and progress'
        ],
        tags: ['Milestone Tracking', 'Achievement Recognition', 'Goal Setting']
    },

    'start_research_session': {
        title: 'Start Research Session',
        purpose: 'Initiates a new research session with proper tracking and context management.',
        context: 'Critical for organizing research work into trackable sessions with clear objectives.',
        usage: 'Creates new research session with session ID, objectives, and automatic progress tracking setup.',
        examples: [
            'Begin new research session with clear objectives',
            'Initialize session tracking for workflow monitoring',
            'Set research focus and expected outcomes',
            'Prepare environment for productive research work'
        ],
        tags: ['Session Management', 'Research Organization', 'Workflow Initialization']
    },

    'get_session_summary': {
        title: 'Get Session Summary',
        purpose: 'Provides comprehensive summary of research session progress and achievements.',
        context: 'Essential for reviewing session productivity and planning follow-up work.',
        usage: 'Generates detailed session report including tools used, progress made, and key insights.',
        examples: [
            'Review completed session achievements',
            'Analyze session productivity metrics',
            'Get summary of tools used and outcomes',
            'Plan follow-up work based on session results'
        ],
        tags: ['Session Analysis', 'Productivity Review', 'Progress Summary']
    },

    'get_visual_progress_summary': {
        title: 'Visual Progress Summary',
        purpose: 'Generates visual progress summary with ASCII charts and comprehensive progress visualization.',
        context: 'Enhanced progress tracking that builds on existing analysis with visual elements for better comprehension.',
        usage: 'Creates ASCII progress bars, tool usage frequency charts, and velocity trends combined with detailed progress reports.',
        examples: [
            'View research acts progress with visual progress bars',
            'Analyze tool usage frequency with bar charts',
            'Track research velocity trends over time',
            'Get comprehensive visual and textual progress analysis'
        ],
        tags: ['Progress Visualization', 'ASCII Charts', 'Research Metrics', 'Visual Analytics']
    },

    'detect_and_celebrate_milestones': {
        title: 'Milestone Detection & Celebration',
        purpose: 'Automatically detects and celebrates research achievements and milestones.',
        context: 'Intelligent milestone recognition system that identifies research progress achievements and provides motivational feedback.',
        usage: 'Analyzes research activity patterns to detect act completions, usage milestones, and velocity achievements.',
        examples: [
            'Celebrate research act completion milestones',
            'Recognize tool usage achievement levels',
            'Acknowledge consistent research momentum',
            'Provide motivational progress feedback'
        ],
        tags: ['Milestone Detection', 'Achievement Recognition', 'Progress Celebration', 'Motivational Feedback']
    }
};

// Validation: Ensure all tools have complete information
const validateToolInfo = () => {
    const requiredFields = ['title', 'purpose', 'context', 'usage', 'examples', 'tags'];
    const issues = [];
    
    Object.entries(TOOL_INFO_DATABASE).forEach(([toolName, info]) => {
        requiredFields.forEach(field => {
            if (!info[field]) {
                issues.push(`${toolName} missing ${field}`);
            }
        });
        
        if (Array.isArray(info.examples) && info.examples.length < 3) {
            issues.push(`${toolName} needs more examples (has ${info.examples.length})`);
        }
    });
    
    return issues;
};

// Run validation
const validationIssues = validateToolInfo();
if (validationIssues.length > 0) {
    console.warn('Tool info validation issues:', validationIssues);
} else {
    console.log('✅ All tool information validated successfully!');
}

console.log(`Tool database includes ${Object.keys(TOOL_INFO_DATABASE).length} tools`);

// Make available for import
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TOOL_INFO_DATABASE;
} else if (typeof window !== 'undefined') {
    window.TOOL_INFO_DATABASE = TOOL_INFO_DATABASE;
}
