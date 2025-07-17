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
    status TEXT DEFAULT 'active'
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_interactions_session_id ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_novel_theories_project_id ON novel_theories(project_id);
