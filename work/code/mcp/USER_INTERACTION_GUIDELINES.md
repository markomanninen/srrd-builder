# SRRD MCP Server User Interaction Guidelines

## CRITICAL: Interactive Research Tools

The SRRD MCP Server provides **44 research tools** categorized by interaction requirements:

## Tool Categories by Interaction Type

### AUTOMATIC/INFORMATIONAL TOOLS (11 tools)
*No user interaction required - just return requested data*

- `list_latex_templates`, `get_research_progress`, `get_tool_usage_history`, `get_research_milestones`, `get_session_summary`
- `search_knowledge`, `semantic_search`, `discover_patterns`, `find_similar_documents`, `extract_key_concepts`, `retrieve_bibliography_references`

### GUIDANCE/ADVISORY TOOLS (16 tools) 
*MUST end with user choice question*

✅ **FIXED** (4 tools):
- `clarify_research_goals` ✅, `suggest_methodology` ✅, `get_workflow_recommendations` ✅, `initialize_project` ✅

✅ **RECENTLY FIXED** (2 tools):
- `explain_methodology` ✅ (removed automatic next_steps)
- `compare_paradigms` ✅ (removed automatic next_steps)

❌ **NEEDS FIXING** (10 tools):
- `compare_approaches`, `validate_design`, `ensure_ethics` (methodology_advisory.py)
- `simulate_peer_review`, `check_quality_gates` (quality_assurance.py)
- `initiate_paradigm_challenge`, `develop_alternative_framework`, `validate_novel_theory`, `cultivate_innovation`, `assess_foundational_assumptions`, `generate_critical_questions`, `evaluate_paradigm_shift_potential` (novel_theory_development.py)

### ACTION/COMPLETION TOOLS (17 tools)
*Just notify completion - no follow-up needed*

- All document generation, storage, and utility tools

## Proper Usage Patterns

❌ **WRONG** - Automatic tool chaining:
```
Assistant: *calls clarify_research_goals → suggest_methodology → start_research_session*
```

✅ **CORRECT** - User choice required:
```
Assistant: *calls clarify_research_goals*
Assistant: "Here are your clarified goals. Which aspect would you like to explore further?"
User: "I'd like to understand methodology options"
Assistant: *calls suggest_methodology*
```

## Fixed Issues

**CRITICAL FIXES COMPLETED:**
- `explain_methodology`: Removed `"next_steps": [...]` → Added `"user_interaction_required"`
- `compare_paradigms`: Removed `"next_steps": [...]` → Added `"user_interaction_required"`

These fixes prevent Claude from automatically executing suggested research steps.
