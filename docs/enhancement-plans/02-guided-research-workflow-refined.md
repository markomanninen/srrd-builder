# Guided Research Workflow and Educational Support - Refined

## Overview

Enhance the existing research workflow intelligence system to provide more structured guidance through research phases. This plan builds on the current `ResearchFrameworkService`, `WorkflowIntelligence`, and existing research continuity tools to avoid redundancy while adding sophisticated workflow management.

## Current System Analysis

### Existing Workflow Infrastructure ✅

**Already Implemented:**
- `ResearchFrameworkService` with 6 research acts framework
- `WorkflowIntelligence` class for progress analysis and recommendations
- `get_research_progress_tool` with comprehensive progress tracking
- Research acts defined: conceptualization, design_planning, implementation, analysis, synthesis, publication
- Database schema with `sessions`, `projects`, `tool_usage`, and `research_progress` tables
- Context-aware tools with proper project detection

**Current Workflow Capabilities:**
- Research progress tracking across acts
- Tool usage analysis and patterns
- Session management and continuity
- Project-based context awareness

### Existing Tools to Enhance:
- `get_research_progress_tool` - Already provides act completion percentages
- `start_research_session_tool` - Already manages research sessions
- `get_workflow_recommendations` - Already provides next-step suggestions

## Enhancement Strategy - Building on Existing

### 1. Enhance Research Act Guidance

**Enhancement**: Add structured guidance for each research act while using existing framework

#### Implementation Plan

**File**: `work/code/mcp/tools/research_continuity.py` (extend existing)

```python
# Add to existing research_continuity.py

@context_aware(require_context=True)
async def get_research_act_guidance(**kwargs) -> str:
    """
    Enhanced tool: Get structured guidance for current or specified research act
    
    Builds on existing ResearchFrameworkService and WorkflowIntelligence
    """
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    
    # Get parameters
    target_act = kwargs.get('target_act', None)
    user_experience = kwargs.get('user_experience', 'intermediate')
    detailed_guidance = kwargs.get('detailed_guidance', True)
    
    # Use existing research framework service
    research_framework = _get_research_framework()
    if not research_framework:
        return "Research framework service not available."
    
    # Get current progress using existing functionality
    db_path = SQLiteManager.get_sessions_db_path(project_path)
    sqlite_manager = SQLiteManager(db_path)
    await sqlite_manager.initialize()
    
    # Determine current act if not specified
    if not target_act:
        # Use existing WorkflowIntelligence to determine current focus
        workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
        current_analysis = await workflow_intelligence.analyze_current_context()
        target_act = current_analysis.get('suggested_current_act', 'conceptualization')
    
    # Get enhanced guidance for the target act
    act_guidance = await _get_enhanced_act_guidance(
        target_act, user_experience, detailed_guidance, sqlite_manager, research_framework
    )
    
    await sqlite_manager.close()
    return act_guidance

async def _get_enhanced_act_guidance(
    act_name: str, 
    experience: str, 
    detailed: bool, 
    sqlite_manager: SQLiteManager,
    research_framework: ResearchFrameworkService
) -> str:
    """Generate enhanced guidance for specific research act"""
    
    # Extended act definitions building on existing framework
    act_definitions = {
        "conceptualization": {
            "purpose": "Defining research problems, questions, and objectives",
            "key_activities": [
                "clarify_research_goals",
                "assess_foundational_assumptions", 
                "generate_critical_questions",
                "semantic_search (for background research)"
            ],
            "success_criteria": [
                "Clear, specific research question formulated",
                "Key assumptions identified and examined", 
                "Research scope properly defined",
                "Initial literature review completed"
            ],
            "common_challenges": [
                "Research question too broad or vague",
                "Unexamined assumptions",
                "Insufficient background research",
                "Unclear success metrics"
            ],
            "experience_adaptations": {
                "beginner": {
                    "additional_tools": ["explain_methodology"],
                    "extra_guidance": "Take time to thoroughly understand the domain before narrowing focus"
                },
                "expert": {
                    "additional_tools": ["validate_novel_theory"],
                    "extra_guidance": "Consider paradigm-challenging possibilities early"
                }
            }
        },
        "design_planning": {
            "purpose": "Planning methodology and research approach",
            "key_activities": [
                "suggest_methodology",
                "design_experimental_framework",
                "plan_data_collection",
                "assess_resources_requirements"
            ],
            "success_criteria": [
                "Appropriate methodology selected and justified",
                "Research design is feasible and rigorous",
                "Data collection plan is detailed and realistic",
                "Resource requirements identified"
            ],
            "common_challenges": [
                "Methodology doesn't match research question",
                "Unrealistic scope or timeline",
                "Missing ethical considerations",
                "Inadequate resource planning"
            ]
        }
        # ... continue for other acts
    }
    
    act_info = act_definitions.get(act_name, {})
    if not act_info:
        return f"Unknown research act: {act_name}"
    
    # Check current progress in this act using existing database
    act_progress = await _get_act_specific_progress(act_name, sqlite_manager)
    
    # Generate guidance based on progress and experience level
    guidance_sections = []
    
    # Act overview
    guidance_sections.append(f"# {act_name.title()} Research Act Guidance")
    guidance_sections.append(f"\n**Purpose**: {act_info['purpose']}")
    
    # Current progress
    if act_progress:
        completion_pct = act_progress.get('completion_percentage', 0)
        guidance_sections.append(f"\n**Current Progress**: {completion_pct:.1f}% complete")
        
        if completion_pct > 0:
            completed_tools = act_progress.get('completed_tools', [])
            guidance_sections.append(f"**Completed Tools**: {', '.join(completed_tools)}")
    
    # Key activities and tools
    guidance_sections.append(f"\n## Key Activities for {act_name.title()}")
    for i, activity in enumerate(act_info.get('key_activities', []), 1):
        guidance_sections.append(f"{i}. **{activity}**")
        if detailed:
            tool_guidance = _get_tool_specific_guidance(activity, experience)
            if tool_guidance:
                guidance_sections.append(f"   - {tool_guidance}")
    
    # Success criteria
    guidance_sections.append(f"\n## Success Criteria")
    for criterion in act_info.get('success_criteria', []):
        guidance_sections.append(f"- {criterion}")
    
    # Experience-specific adaptations
    experience_adapt = act_info.get('experience_adaptations', {}).get(experience, {})
    if experience_adapt:
        guidance_sections.append(f"\n## {experience.title()}-Level Guidance")
        if 'additional_tools' in experience_adapt:
            guidance_sections.append("**Additional Recommended Tools**:")
            for tool in experience_adapt['additional_tools']:
                guidance_sections.append(f"- {tool}")
        if 'extra_guidance' in experience_adapt:
            guidance_sections.append(f"**Special Considerations**: {experience_adapt['extra_guidance']}")
    
    # Common challenges and how to avoid them
    guidance_sections.append(f"\n## Common Challenges to Avoid")
    for challenge in act_info.get('common_challenges', []):
        guidance_sections.append(f"- {challenge}")
    
    # Next steps based on current progress
    guidance_sections.append(f"\n## Recommended Next Steps")
    next_tools = await _get_smart_next_tools(act_name, act_progress, sqlite_manager)
    for tool in next_tools:
        guidance_sections.append(f"- Use **{tool['name']}**: {tool['rationale']}")
    
    return "\n".join(guidance_sections)

async def _get_act_specific_progress(act_name: str, sqlite_manager: SQLiteManager) -> Dict[str, Any]:
    """Get progress specific to a research act using existing database"""
    # Query existing tool_usage table to determine act progress
    act_tools_map = {
        "conceptualization": ["clarify_research_goals", "assess_foundational_assumptions", "generate_critical_questions"],
        "design_planning": ["suggest_methodology", "design_experimental_framework", "plan_data_collection"],
        # ... add other acts
    }
    
    relevant_tools = act_tools_map.get(act_name, [])
    if not relevant_tools:
        return {}
    
    # Query database for tools used in this act
    placeholders = ','.join(['?' for _ in relevant_tools])
    query = f"""
        SELECT tool_name, COUNT(*) as usage_count, MAX(timestamp) as last_used
        FROM tool_usage 
        WHERE tool_name IN ({placeholders})
        GROUP BY tool_name
        ORDER BY last_used DESC
    """
    
    async with sqlite_manager.connection.execute(query, relevant_tools) as cursor:
        tool_usage = await cursor.fetchall()
    
    completed_tools = [row[0] for row in tool_usage]
    completion_pct = (len(completed_tools) / len(relevant_tools)) * 100
    
    return {
        "completion_percentage": completion_pct,
        "completed_tools": completed_tools,
        "total_tools": len(relevant_tools),
        "last_activity": tool_usage[0][2] if tool_usage else None
    }

async def _get_smart_next_tools(act_name: str, progress: Dict, sqlite_manager: SQLiteManager) -> List[Dict[str, str]]:
    """Get smart next tool recommendations based on act progress"""
    completed_tools = progress.get('completed_tools', [])
    
    # Act-specific tool progressions
    tool_progressions = {
        "conceptualization": [
            {"name": "clarify_research_goals", "rationale": "Start by clarifying your research objectives"},
            {"name": "semantic_search", "rationale": "Search existing literature for background"},
            {"name": "assess_foundational_assumptions", "rationale": "Examine underlying assumptions"},
            {"name": "generate_critical_questions", "rationale": "Develop critical thinking questions"}
        ],
        "design_planning": [
            {"name": "suggest_methodology", "rationale": "Get methodology recommendations"},
            {"name": "design_experimental_framework", "rationale": "Design your research approach"},
            {"name": "assess_resource_requirements", "rationale": "Plan required resources"}
        ]
    }
    
    progression = tool_progressions.get(act_name, [])
    next_tools = []
    
    for tool in progression:
        if tool["name"] not in completed_tools:
            next_tools.append(tool)
            if len(next_tools) >= 3:  # Limit to top 3 recommendations
                break
    
    return next_tools

def _get_tool_specific_guidance(tool_name: str, experience: str) -> str:
    """Get guidance for using specific tools"""
    tool_guidance = {
        "clarify_research_goals": {
            "beginner": "Take time to really think through your research interests",
            "intermediate": "Focus on making your goals specific and measurable", 
            "expert": "Consider novel angles and paradigm implications"
        },
        "suggest_methodology": {
            "beginner": "Ask for detailed explanations of recommended methodologies",
            "intermediate": "Consider multiple methodologies and their trade-offs",
            "expert": "Evaluate methodology appropriateness for novel approaches"
        }
    }
    
    return tool_guidance.get(tool_name, {}).get(experience, "")
```

### 2. Enhanced Smart Recommendations

**Enhancement**: Build on existing `get_workflow_recommendations` with context-aware intelligence

#### Implementation Plan

**File**: `work/code/mcp/utils/workflow_intelligence.py` (extend existing)

```python
# Add to existing WorkflowIntelligence class

class WorkflowIntelligence:
    """Enhanced workflow intelligence building on existing functionality"""
    
    async def get_contextual_recommendations(
        self, 
        last_tool_used: str = None,
        user_context: Dict[str, Any] = None,
        recommendation_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Enhanced contextual recommendations building on existing analyze_current_context
        """
        # Get existing analysis as foundation
        current_context = await self.analyze_current_context()
        
        # Enhance with tool sequence analysis
        recent_tools = await self._get_recent_tool_sequence(limit=5)
        tool_patterns = self._analyze_tool_patterns(recent_tools)
        
        # Generate enhanced recommendations
        recommendations = await self._generate_enhanced_recommendations(
            current_context, 
            recent_tools, 
            tool_patterns,
            last_tool_used,
            recommendation_depth
        )
        
        return {
            "current_context": current_context,
            "recent_activity_pattern": tool_patterns,
            "prioritized_recommendations": recommendations,
            "rationale": self._explain_recommendations(recommendations, tool_patterns),
            "alternative_paths": await self._get_alternative_approaches(recommendations)
        }
    
    async def _get_recent_tool_sequence(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent tool usage sequence from existing database"""
        query = """
            SELECT tool_name, timestamp, result_summary
            FROM tool_usage 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        
        async with self.sqlite_manager.connection.execute(query, (limit,)) as cursor:
            results = await cursor.fetchall()
        
        return [
            {
                "tool_name": row[0],
                "timestamp": row[1], 
                "result_summary": row[2]
            }
            for row in results
        ]
    
    def _analyze_tool_patterns(self, recent_tools: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in recent tool usage"""
        if not recent_tools:
            return {"pattern_type": "no_activity", "confidence": 0}
        
        tool_names = [t["tool_name"] for t in recent_tools]
        
        # Detect common patterns
        if len(set(tool_names)) == 1:
            return {
                "pattern_type": "repetitive",
                "repeated_tool": tool_names[0],
                "confidence": 0.8,
                "suggestion": "Consider diversifying tool usage"
            }
        
        # Check for logical progressions
        logical_sequences = [
            ["clarify_research_goals", "suggest_methodology"],
            ["semantic_search", "generate_document"],
            ["suggest_methodology", "design_experimental_framework"]
        ]
        
        for sequence in logical_sequences:
            if self._check_sequence_match(tool_names, sequence):
                return {
                    "pattern_type": "logical_progression",
                    "sequence": sequence,
                    "confidence": 0.9,
                    "suggestion": "Good workflow progression detected"
                }
        
        return {
            "pattern_type": "exploratory",
            "diversity": len(set(tool_names)) / len(tool_names),
            "confidence": 0.6
        }
```

## Testing Strategy - Following Proven Patterns

### Unit Tests Following Existing Structure

**File**: `work/tests/unit/tools/test_enhanced_workflow_guidance.py`

```python
#!/usr/bin/env python3
"""
Unit Tests for Enhanced Workflow Guidance
=======================================

Tests enhanced research workflow guidance functionality:
- Research act guidance generation
- Smart contextual recommendations  
- Tool progression logic
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

class TestEnhancedWorkflowGuidance:
    """Test enhanced workflow guidance functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def create_temp_dir(self, name: str) -> Path:
        """Create temporary directory for testing"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix=f"test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path

    @pytest.mark.asyncio
    async def test_research_act_guidance_generation(self):
        """Test research act guidance generation functionality"""
        # Test using real function (not mocked) following test suite guidelines
        from tools.research_continuity import _get_enhanced_act_guidance
        from storage.sqlite_manager import SQLiteManager
        from utils.research_framework import ResearchFrameworkService
        
        # Create temporary database
        temp_dir = self.create_temp_dir("act_guidance")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        research_framework = ResearchFrameworkService()
        
        # Test conceptualization act guidance
        guidance = await _get_enhanced_act_guidance(
            "conceptualization",
            "intermediate", 
            True,
            sqlite_manager,
            research_framework
        )
        
        assert "Conceptualization Research Act Guidance" in guidance
        assert "Purpose" in guidance
        assert "Key Activities" in guidance
        assert "Success Criteria" in guidance
        assert "clarify_research_goals" in guidance
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_act_specific_progress_calculation(self):
        """Test act-specific progress calculation using real database"""
        from tools.research_continuity import _get_act_specific_progress
        from storage.sqlite_manager import SQLiteManager
        
        # Create temporary database with some tool usage data
        temp_dir = self.create_temp_dir("progress_calc")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Insert some test tool usage data
        await sqlite_manager.connection.execute(
            "INSERT INTO tool_usage (tool_name, timestamp, result_summary) VALUES (?, ?, ?)",
            ("clarify_research_goals", "2024-01-01 10:00:00", "Research goals clarified")
        )
        await sqlite_manager.connection.execute(
            "INSERT INTO tool_usage (tool_name, timestamp, result_summary) VALUES (?, ?, ?)",
            ("semantic_search", "2024-01-01 11:00:00", "Literature search completed")
        )
        await sqlite_manager.connection.commit()
        
        # Test progress calculation
        progress = await _get_act_specific_progress("conceptualization", sqlite_manager)
        
        assert "completion_percentage" in progress
        assert progress["completion_percentage"] > 0
        assert "completed_tools" in progress
        assert "clarify_research_goals" in progress["completed_tools"]
        
        await sqlite_manager.close()

    @pytest.mark.asyncio
    async def test_smart_next_tools_recommendation(self):
        """Test smart next tool recommendations based on progress"""
        from tools.research_continuity import _get_smart_next_tools
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("next_tools")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        # Test with partial progress
        progress = {
            "completion_percentage": 33.3,
            "completed_tools": ["clarify_research_goals"],
            "total_tools": 3
        }
        
        recommendations = await _get_smart_next_tools("conceptualization", progress, sqlite_manager)
        
        assert len(recommendations) > 0
        assert all("name" in rec and "rationale" in rec for rec in recommendations)
        # Should not recommend already completed tools
        tool_names = [rec["name"] for rec in recommendations]
        assert "clarify_research_goals" not in tool_names
        
        await sqlite_manager.close()
```

### Integration Tests - Real Database Pattern

**File**: `work/tests/integration/test_enhanced_workflow_integration.py`

```python
#!/usr/bin/env python3
"""
Integration Tests for Enhanced Workflow System
===========================================

Tests complete enhanced workflow system with real database integration.
Follows proven pattern of using temporary directories and real databases.
"""
import pytest
import tempfile
import os
from pathlib import Path

class TestEnhancedWorkflowIntegration:
    """Test enhanced workflow system integration"""

    @pytest.mark.asyncio
    async def test_complete_workflow_guidance_cycle(self):
        """Test complete workflow guidance cycle with real database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="computer_science", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Test enhanced workflow guidance
            from tools.research_continuity import get_research_act_guidance
            
            # Get guidance for conceptualization act
            guidance_result = await get_research_act_guidance(
                target_act="conceptualization",
                user_experience="intermediate",
                detailed_guidance=True
            )
            
            assert "Conceptualization Research Act Guidance" in guidance_result
            assert "Key Activities" in guidance_result
            assert "Recommended Next Steps" in guidance_result
            
            # Use a recommended tool to create progress
            from tools.research_planning import clarify_research_goals
            
            planning_result = await clarify_research_goals(
                research_area="machine learning optimization",
                initial_goals="Improve neural network training efficiency"
            )
            
            assert "clarified_goals" in planning_result
            
            # Get updated guidance after tool usage
            updated_guidance = await get_research_act_guidance(
                target_act="conceptualization",
                user_experience="intermediate"
            )
            
            # Should show progress has been made
            assert "Current Progress" in updated_guidance
            assert "clarify_research_goals" in updated_guidance

    @pytest.mark.asyncio 
    async def test_contextual_recommendations_with_tool_history(self):
        """Test contextual recommendations based on actual tool usage history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="physics", template="theoretical")
            result = handle_init(args)
            assert result == 0
            
            # Create tool usage history
            from tools.research_planning import clarify_research_goals, suggest_methodology
            
            # Step 1: Clarify goals
            await clarify_research_goals(
                research_area="quantum mechanics",
                initial_goals="Develop new interpretation of quantum measurement"
            )
            
            # Step 2: Get methodology suggestions
            await suggest_methodology(
                research_goals="New quantum measurement interpretation",
                domain="theoretical_physics"
            )
            
            # Test contextual recommendations
            from utils.workflow_intelligence import WorkflowIntelligence
            from storage.sqlite_manager import SQLiteManager
            from utils.research_framework import ResearchFrameworkService
            
            db_path = SQLiteManager.get_sessions_db_path(temp_dir)
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            research_framework = ResearchFrameworkService()
            workflow_intelligence = WorkflowIntelligence(sqlite_manager, research_framework)
            
            recommendations = await workflow_intelligence.get_contextual_recommendations(
                last_tool_used="suggest_methodology",
                recommendation_depth=3
            )
            
            assert "prioritized_recommendations" in recommendations
            assert "rationale" in recommendations
            assert "recent_activity_pattern" in recommendations
            
            # Verify recommendations are contextually appropriate
            rec_tools = [r.get("tool_name", "") for r in recommendations["prioritized_recommendations"]]
            # After methodology selection, should suggest implementation-related tools
            implementation_tools = ["design_experimental_framework", "assess_foundational_assumptions", "generate_critical_questions"]
            assert any(tool in rec_tools for tool in implementation_tools)
            
            await sqlite_manager.close()
```

## Implementation Phases

### Phase 1: Enhance Act Guidance (2 weeks)
- Extend `research_continuity.py` with `get_research_act_guidance` tool
- Add detailed act definitions and guidance templates
- Implement act-specific progress calculation using existing database
- Follow existing `@context_aware` patterns

### Phase 2: Smart Recommendations Enhancement (2 weeks)
- Extend `WorkflowIntelligence` class with contextual recommendations
- Add tool pattern analysis and sequence detection
- Implement progressive recommendation depth
- Integrate with existing `get_workflow_recommendations`

### Phase 3: Testing Following Proven Patterns (1 week)
- Create unit tests following existing patterns in `work/tests/unit/tools/`
- Add integration tests using real databases and temporary directories
- Follow 3-tier test structure and avoid over-mocking
- Maintain 100% test pass rate

### Phase 4: Documentation and Integration (1 week)
- Update existing tool documentation
- Add CLI examples building on existing commands
- Integration with existing web interface
- Performance optimization

## Success Metrics

### Quantitative Metrics
- Act guidance coverage (detailed guidance for all 6 research acts)
- Contextual recommendation accuracy (measured against research progression)
- Tool usage pattern recognition effectiveness
- Integration test coverage maintaining 100% pass rate

### Qualitative Metrics
- Quality and usefulness of act-specific guidance
- Relevance of contextual recommendations
- Effectiveness of progressive workflow support
- Integration quality with existing ecosystem

## Building on Existing Strengths

### Leveraging Current Infrastructure
- **Database Schema**: Use existing `tool_usage`, `sessions`, and `projects` tables
- **Research Framework**: Build on existing 6-act research framework
- **Context Awareness**: Use existing `@context_aware` decorator system
- **CLI Integration**: Follow existing command patterns and project detection

### Avoiding Redundancy
- **Don't Recreate**: Enhance existing `ResearchFrameworkService` and `WorkflowIntelligence`
- **Don't Replace**: Extend existing tools rather than creating new ones
- **Don't Duplicate**: Use existing database queries and session management
- **Don't Over-Engineer**: Build incrementally on proven patterns

## Frontend Integration Notes for Implementation

### Frontend Integration Requirements

When implementing new workflow guidance tools, ensure proper frontend integration:

**Tool Information Database Updates:**

- Add new workflow tools to `work/code/mcp/frontend/data/tool-info.js`
- Include comprehensive metadata: title, purpose, context, usage, examples, tags
- Update tool count in header comments

**Research Framework Integration:**

- Map new tools to appropriate research acts and categories in `work/code/mcp/frontend/data/research-framework.js`
- Add tools to the `expectedTools` validation array
- Update framework validation logic for correct tool counts

**Recommended Integration Process:**

1. Add complete tool metadata to `tool-info.js`
2. Map tools to research acts/categories in `research-framework.js`
3. Update tool count references in both files
4. Add tools to validation arrays
5. **CRITICAL**: Add default parameters to `getToolParameterDefaults()` in `enhanced-app.js`
6. Test integration via console validation logs

**Frontend Parameter Handling - CRITICAL:**

For tools with required parameters, you MUST add default values to `work/code/mcp/frontend/enhanced-app.js` in the `getToolParameterDefaults()` function, or the frontend will fail with "missing required parameter" errors. See Plan 1 documentation for detailed implementation examples.

**Category Mapping Guidelines:**

- **Workflow tracking tools** → Communication & Dissemination act, workflow_tracking category
- **Progress analysis tools** → Communication & Dissemination act, workflow_tracking category  
- **Guidance tools** → Conceptualization act, goal_setting or critical_thinking categories
- **Recommendation tools** → Design & Planning act, methodology category

This refined plan builds systematically on the existing workflow intelligence infrastructure while adding sophisticated guidance capabilities that integrate seamlessly with the current system architecture.
