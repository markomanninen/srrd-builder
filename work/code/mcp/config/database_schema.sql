-- SRRD-Builder Database Schema
-- Core database schema for MCP server implementation

-- Project management
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT,
    methodology TEXT,
    novel_theory_mode BOOLEAN DEFAULT FALSE,
    paradigm_focus TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research sessions
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    session_type TEXT, -- planning, execution, analysis, publication, novel_theory
    paradigm_innovation_session BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    user_id TEXT,
    status TEXT DEFAULT 'active',
    current_research_act TEXT,
    research_focus TEXT,
    session_goals JSON
);

-- User interactions and Socratic questioning
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    interaction_type TEXT, -- socratic_question, methodology_advice, paradigm_challenge
    content TEXT NOT NULL,
    domain_context TEXT,
    novel_theory_context TEXT,
    metadata JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paradigm comparison for novel theory development
CREATE TABLE IF NOT EXISTS paradigm_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    mainstream_paradigm TEXT NOT NULL,
    alternative_paradigm TEXT NOT NULL,
    comparison_criteria JSON,
    validation_results JSON,
    equal_treatment_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Novel theory tracking
CREATE TABLE IF NOT EXISTS novel_theories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    theory_name TEXT NOT NULL,
    core_principles JSON,
    mathematical_framework TEXT,
    empirical_predictions JSON,
    validation_status TEXT,
    peer_review_simulation JSON,
    development_stage TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research templates and documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    document_type TEXT, -- proposal, manuscript, thesis, novel_theory
    template_used TEXT,
    content JSON,
    latex_source TEXT,
    compilation_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality assurance tracking
CREATE TABLE IF NOT EXISTS quality_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    check_type TEXT, -- peer_review_sim, methodology_validation, novelty_assessment
    criteria JSON,
    results JSON,
    passed BOOLEAN,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool usage tracking with research act context
CREATE TABLE IF NOT EXISTS tool_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    tool_name TEXT NOT NULL,
    research_act TEXT NOT NULL,
    research_category TEXT NOT NULL,
    arguments JSON,
    result_summary TEXT,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research progress tracking across acts and categories
CREATE TABLE IF NOT EXISTS research_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    research_act TEXT NOT NULL,
    research_category TEXT NOT NULL,
    status TEXT DEFAULT 'not_started', -- not_started, in_progress, completed, reviewed
    completion_percentage INTEGER DEFAULT 0,
    tools_used JSON, -- Array of tool names used in this category
    milestone_reached BOOLEAN DEFAULT FALSE,
    notes TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI-powered workflow recommendations
CREATE TABLE IF NOT EXISTS workflow_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    session_id INTEGER REFERENCES sessions(id),
    current_research_act TEXT NOT NULL,
    recommended_next_act TEXT,
    recommended_tools JSON, -- Array of recommended tool names
    reasoning TEXT,
    priority INTEGER DEFAULT 1, -- 1=high, 2=medium, 3=low
    status TEXT DEFAULT 'pending', -- pending, accepted, dismissed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research milestones tracking
CREATE TABLE IF NOT EXISTS research_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    milestone_type TEXT NOT NULL, -- research_act_completed, category_completed, theory_validated, document_generated
    milestone_name TEXT NOT NULL,
    description TEXT,
    research_act TEXT,
    research_category TEXT,
    completion_criteria JSON,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tools_involved JSON,
    impact_score INTEGER DEFAULT 1 -- 1-5 scale of milestone importance
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_interactions_session_id ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_novel_theories_project_id ON novel_theories(project_id);
CREATE INDEX IF NOT EXISTS idx_tool_usage_session_id ON tool_usage(session_id);
CREATE INDEX IF NOT EXISTS idx_tool_usage_research_act ON tool_usage(research_act);
CREATE INDEX IF NOT EXISTS idx_tool_usage_tool_name ON tool_usage(tool_name);
CREATE INDEX IF NOT EXISTS idx_research_progress_project_id ON research_progress(project_id);
CREATE INDEX IF NOT EXISTS idx_research_progress_research_act ON research_progress(research_act);
CREATE INDEX IF NOT EXISTS idx_workflow_recommendations_project_id ON workflow_recommendations(project_id);
CREATE INDEX IF NOT EXISTS idx_research_milestones_project_id ON research_milestones(project_id);