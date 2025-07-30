# Guided Research Workflow and Educational Support

## Overview

Enhance the SRRD-Builder MCP server with structured workflow guidance tools that help users navigate through research phases systematically. Focus on creating MCP tools that provide step-by-step guidance and educational support within Claude Desktop and VS Code environments.

## Goals

- Provide structured guidance through the 6 Research Acts 
- Help users know what to do next at each research phase
- Create educational support through research methodology guidance
- Implement proactive tool recommendations based on current context

## Features

### 1. Research Act Guidance Tools

**Current State**: Framework has 6 research acts defined, WorkflowIntelligence provides recommendations

**Enhancement**: Create dedicated MCP tools for each research act with structured guidance

#### Implementation Plan

**File**: `srrd_builder/tools/workflow_guidance.py`

```python
@mcp_tool("start_research_act")
async def start_research_act(
    act_name: str,
    project_context: str,
    user_experience_level: str = "intermediate"
) -> dict:
    """
    Start guided workflow for a specific research act
    
    Args:
        act_name: One of the 6 research acts (conceptualization, design_planning, etc.)
        project_context: Brief description of the research project
        user_experience_level: beginner, intermediate, advanced
    
    Returns:
        dict: Structured guidance, tool sequence, and educational content
    """
    # Returns:
    # - Overview of the research act
    # - Recommended tool sequence for this act
    # - Educational explanations for each step
    # - Tips and best practices
    # - Success criteria for completing the act
```

**File**: `srrd_builder/tools/workflow_guidance.py`

```python
@mcp_tool("get_act_progress_guidance")
async def get_act_progress_guidance(
    current_act: str,
    completed_tools: List[str],
    research_domain: str = "general"
) -> dict:
    """
    Get progress-specific guidance for current research act
    
    Args:
        current_act: Current research act in progress
        completed_tools: List of tools already used in this act
        research_domain: Research field for domain-specific guidance
    
    Returns:
        dict: Progress assessment, remaining steps, and next recommendations
    """
    # Analyzes progress and provides:
    # - What's been accomplished so far
    # - What's remaining in current act
    # - Specific next tool recommendations
    # - Quality checkpoints
```

### 2. Smart Next-Step Recommendations

**Current State**: `get_workflow_recommendations` exists but provides general advice

**Enhancement**: Create context-aware recommendation tools

#### Implementation Plan

**File**: `srrd_builder/tools/workflow_intelligence.py`

```python
@mcp_tool("get_smart_next_steps")
async def get_smart_next_steps(
    last_tool_used: str,
    last_tool_result_summary: str,
    current_research_phase: str,
    research_goals: str
) -> dict:
    """
    Provide intelligent next-step recommendations based on context
    
    Args:
        last_tool_used: The most recently used tool
        last_tool_result_summary: Brief summary of the last result
        current_research_phase: Current phase of research
        research_goals: User's research objectives
    
    Returns:
        dict: Prioritized next steps with explanations
    """
    # Provides:
    # - 3-5 prioritized next tool recommendations
    # - Explanation for why each tool is recommended
    # - Alternative paths if user wants different approach
    # - Warning about potential issues or dependencies
```

### 3. Research Methodology Education Tools

**Enhancement**: Create educational tools that teach research methodology concepts

#### Implementation Plan

**File**: `srrd_builder/tools/research_education.py`

```python
@mcp_tool("explain_research_concept")
async def explain_research_concept(
    concept: str,
    research_context: str,
    detail_level: str = "practical"
) -> dict:
    """
    Explain research methodology concepts with practical applications
    
    Args:
        concept: Research concept to explain (hypothesis, methodology, validation, etc.)
        research_context: User's research area for contextualized examples
        detail_level: basic, practical, or comprehensive
    
    Returns:
        dict: Concept explanation with examples and application guidance
    """
    # Provides:
    # - Clear definition of the concept
    # - Why it matters in research
    # - Practical examples in user's domain
    # - Common mistakes to avoid
    # - Related tools in SRRD framework
```

**File**: `srrd_builder/tools/research_education.py`

```python
@mcp_tool("research_act_tutorial")
async def research_act_tutorial(
    act_name: str,
    research_domain: str,
    learning_style: str = "example_based"
) -> dict:
    """
    Provide tutorial-style guidance for research acts
    
    Args:
        act_name: Research act to learn about
        research_domain: Field of research for relevant examples
        learning_style: example_based, step_by_step, or overview
    
    Returns:
        dict: Tutorial content with examples and exercises
    """
    # Provides:
    # - Step-by-step walkthrough of the research act
    # - Real examples from the specified domain
    # - Mini-exercises to practice concepts
    # - Common pitfalls and how to avoid them
```

## Technical Implementation

### Research Act Definitions

```python
# Enhanced research act definitions with guidance
RESEARCH_ACTS = {
    "conceptualization": {
        "description": "Defining research problems, questions, and objectives",
        "key_activities": [
            "clarify_research_goals",
            "assess_foundational_assumptions", 
            "generate_critical_questions"
        ],
        "success_criteria": [
            "Clear research question formulated",
            "Key assumptions identified",
            "Scope properly defined"
        ],
        "common_mistakes": [
            "Research question too broad",
            "Assumptions not examined",
            "Unclear objectives"
        ]
    },
    "design_planning": {
        "description": "Planning methodology and research approach",
        "key_activities": [
            "suggest_methodology",
            "design_experimental_framework",
            "plan_data_collection"
        ],
        "success_criteria": [
            "Appropriate methodology selected",
            "Research design is feasible",
            "Data collection plan is clear"
        ],
        "common_mistakes": [
            "Methodology doesn't fit question",
            "Unrealistic scope",
            "Missing ethical considerations"
        ]
    }
    # ... other acts
}
```

### Workflow State Management

```python
class WorkflowState:
    """Track current workflow state and progress"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.current_act = None
        self.completed_acts = []
        self.tools_used_in_current_act = []
        self.act_progress = {}
    
    def update_progress(self, tool_name: str, result_summary: str):
        """Update progress when tool is used"""
        pass
    
    def get_act_completion_percentage(self, act_name: str) -> float:
        """Calculate completion percentage for an act"""
        pass
    
    def recommend_next_tools(self) -> List[str]:
        """Get context-aware tool recommendations"""
        pass
```

## Testing Strategy

### Unit Tests

#### test_workflow_guidance.py
```python
import pytest
from srrd_builder.tools.workflow_guidance import start_research_act, get_act_progress_guidance

class TestWorkflowGuidance:
    
    @pytest.mark.asyncio
    async def test_start_research_act_conceptualization(self):
        """Test starting conceptualization act guidance"""
        result = await start_research_act(
            act_name="conceptualization",
            project_context="Studying the effects of meditation on cognitive performance",
            user_experience_level="beginner"
        )
        
        assert "act_overview" in result
        assert "recommended_tool_sequence" in result
        assert "educational_content" in result
        assert "success_criteria" in result
        
        # Should include beginner-appropriate content
        content = str(result).lower()
        assert "conceptualization" in content
        assert "research question" in content
        
        # Should recommend appropriate tools
        tools = result["recommended_tool_sequence"]
        assert "clarify_research_goals" in tools
        assert "assess_foundational_assumptions" in tools
    
    @pytest.mark.asyncio
    async def test_act_progress_guidance(self):
        """Test progress-based guidance"""
        result = await get_act_progress_guidance(
            current_act="design_planning",
            completed_tools=["clarify_research_goals", "assess_foundational_assumptions"],
            research_domain="psychology"
        )
        
        assert "progress_assessment" in result
        assert "remaining_steps" in result
        assert "next_recommendations" in result
        
        # Should recognize completed work
        assessment = result["progress_assessment"]
        assert "clarify_research_goals" in str(assessment)
        
        # Should provide domain-specific guidance
        psychology_terms = ["participant", "behavior", "measurement", "validity"]
        content = str(result).lower()
        assert any(term in content for term in psychology_terms)
    
    @pytest.mark.asyncio
    async def test_user_experience_adaptation(self):
        """Test that guidance adapts to user experience level"""
        beginner_result = await start_research_act(
            act_name="analysis",
            project_context="Data analysis project",
            user_experience_level="beginner"
        )
        
        advanced_result = await start_research_act(
            act_name="analysis", 
            project_context="Data analysis project",
            user_experience_level="advanced"
        )
        
        # Beginner should get more detailed explanations
        beginner_content = str(beginner_result)
        advanced_content = str(advanced_result)
        
        assert len(beginner_content) > len(advanced_content)
        assert "step by step" in beginner_content.lower()
```

#### test_smart_recommendations.py
```python
import pytest
from srrd_builder.tools.workflow_intelligence import get_smart_next_steps

class TestSmartRecommendations:
    
    @pytest.mark.asyncio
    async def test_context_aware_recommendations(self):
        """Test recommendations based on previous tool usage"""
        result = await get_smart_next_steps(
            last_tool_used="clarify_research_goals",
            last_tool_result_summary="Defined research question about social media impact on learning",
            current_research_phase="conceptualization",
            research_goals="Understand how social media affects student academic performance"
        )
        
        assert "prioritized_recommendations" in result
        assert "explanations" in result
        assert "alternative_paths" in result
        
        recommendations = result["prioritized_recommendations"]
        assert len(recommendations) >= 3
        
        # Should recommend logical next steps after goal clarification
        likely_next_tools = ["assess_foundational_assumptions", "generate_critical_questions", "suggest_methodology"]
        assert any(tool in recommendations for tool in likely_next_tools)
    
    @pytest.mark.asyncio
    async def test_phase_appropriate_recommendations(self):
        """Test that recommendations match current research phase"""
        design_result = await get_smart_next_steps(
            last_tool_used="suggest_methodology",
            last_tool_result_summary="Selected survey methodology for data collection",
            current_research_phase="design_planning",
            research_goals="Survey students about social media usage patterns"
        )
        
        analysis_result = await get_smart_next_steps(
            last_tool_used="collect_data",
            last_tool_result_summary="Collected survey responses from 500 students", 
            current_research_phase="analysis",
            research_goals="Analyze relationship between social media and grades"
        )
        
        # Design phase should focus on planning tools
        design_tools = design_result["prioritized_recommendations"]
        design_related = ["experimental_design", "ethical_review", "data_collection"]
        assert any(tool in str(design_tools) for tool in design_related)
        
        # Analysis phase should focus on analysis tools
        analysis_tools = analysis_result["prioritized_recommendations"]
        analysis_related = ["statistical_analysis", "data_interpretation", "validate_findings"]
        assert any(tool in str(analysis_tools) for tool in analysis_related)
    
    @pytest.mark.asyncio
    async def test_warning_detection(self):
        """Test that warnings are provided for potential issues"""
        result = await get_smart_next_steps(
            last_tool_used="generate_document",
            last_tool_result_summary="Generated paper without completing data analysis",
            current_research_phase="publication",
            research_goals="Publish findings on machine learning applications"
        )
        
        assert "warnings" in result
        warnings = result["warnings"]
        assert len(warnings) > 0
        
        # Should warn about skipping analysis
        warning_text = str(warnings).lower()
        assert any(keyword in warning_text for keyword in ["analysis", "premature", "incomplete"])
```

#### test_research_education.py
```python
import pytest
from srrd_builder.tools.research_education import explain_research_concept, research_act_tutorial

class TestResearchEducation:
    
    @pytest.mark.asyncio
    async def test_concept_explanation(self):
        """Test research concept explanations"""
        result = await explain_research_concept(
            concept="hypothesis",
            research_context="psychology experiment",
            detail_level="practical"
        )
        
        assert "definition" in result
        assert "practical_examples" in result
        assert "why_it_matters" in result
        assert "common_mistakes" in result
        assert "related_tools" in result
        
        # Should be contextualized to psychology
        content = str(result).lower()
        assert "hypothesis" in content
        assert any(term in content for term in ["psychology", "experiment", "behavior"])
    
    @pytest.mark.asyncio
    async def test_act_tutorial(self):
        """Test research act tutorials"""
        result = await research_act_tutorial(
            act_name="literature_review",
            research_domain="computer_science",
            learning_style="example_based"
        )
        
        assert "tutorial_steps" in result
        assert "examples" in result
        assert "practice_exercises" in result
        assert "pitfalls_to_avoid" in result
        
        # Should include computer science examples
        content = str(result).lower()
        cs_terms = ["algorithm", "software", "computing", "programming"]
        assert any(term in content for term in cs_terms)
        
        # Should include practical exercises
        exercises = result["practice_exercises"]
        assert len(exercises) > 0
        assert all("exercise" in str(ex).lower() for ex in exercises)
    
    @pytest.mark.asyncio
    async def test_detail_level_adaptation(self):
        """Test that explanations adapt to requested detail level"""
        basic_result = await explain_research_concept(
            concept="statistical_significance",
            research_context="medical research",
            detail_level="basic"
        )
        
        comprehensive_result = await explain_research_concept(
            concept="statistical_significance",
            research_context="medical research", 
            detail_level="comprehensive"
        )
        
        # Comprehensive should be longer and more detailed
        basic_length = len(str(basic_result))
        comprehensive_length = len(str(comprehensive_result))
        
        assert comprehensive_length > basic_length * 1.5
        
        # Comprehensive should include more technical terms
        comp_content = str(comprehensive_result).lower()
        technical_terms = ["p-value", "confidence interval", "null hypothesis", "statistical power"]
        technical_count = sum(1 for term in technical_terms if term in comp_content)
        assert technical_count >= 2
```

### Integration Tests

#### test_workflow_integration.py
```python
import pytest
from srrd_builder.server.mcp_server import MCPServer
from srrd_builder.storage.sqlite_manager import SQLiteManager

class TestWorkflowIntegration:
    
    @pytest.fixture
    def mcp_server(self):
        return MCPServer(test_mode=True)
    
    @pytest.mark.asyncio
    async def test_complete_act_workflow(self, mcp_server):
        """Test complete workflow through a research act"""
        
        # Start conceptualization act
        start_result = await mcp_server.call_tool(
            "start_research_act",
            {
                "act_name": "conceptualization",
                "project_context": "Studying renewable energy adoption",
                "user_experience_level": "intermediate"
            }
        )
        
        assert start_result["success"]
        recommended_tools = start_result["data"]["recommended_tool_sequence"]
        
        # Use first recommended tool
        first_tool = recommended_tools[0]
        tool_result = await mcp_server.call_tool(
            first_tool,
            {"research_context": "renewable energy adoption patterns"}
        )
        
        assert tool_result["success"]
        
        # Get progress guidance
        progress_result = await mcp_server.call_tool(
            "get_act_progress_guidance",
            {
                "current_act": "conceptualization",
                "completed_tools": [first_tool],
                "research_domain": "environmental_science"
            }
        )
        
        assert progress_result["success"]
        assert "progress_assessment" in progress_result["data"]
        assert "next_recommendations" in progress_result["data"]
    
    @pytest.mark.asyncio
    async def test_smart_recommendations_workflow(self, mcp_server):
        """Test smart recommendations integrate with tool usage"""
        
        # Use a research tool
        tool_result = await mcp_server.call_tool(
            "clarify_research_goals",
            {"research_area": "artificial intelligence safety"}
        )
        
        assert tool_result["success"]
        
        # Get smart next steps
        next_steps_result = await mcp_server.call_tool(
            "get_smart_next_steps",
            {
                "last_tool_used": "clarify_research_goals",
                "last_tool_result_summary": "Defined research goals for AI safety",
                "current_research_phase": "conceptualization",
                "research_goals": "Develop safety frameworks for AI systems"
            }
        )
        
        assert next_steps_result["success"]
        recommendations = next_steps_result["data"]["prioritized_recommendations"]
        
        # Should provide relevant next steps
        assert len(recommendations) >= 3
        assert any("assumption" in rec.lower() or "methodology" in rec.lower() for rec in recommendations)
```

## CLI Integration

### New Workflow Commands
```bash
# Start guided research act
srrd workflow start-act --act conceptualization --context "climate change research" --level beginner

# Get progress guidance  
srrd workflow progress --act design_planning --completed "clarify_research_goals,suggest_methodology"

# Get smart next step recommendations
srrd workflow next-steps --last-tool semantic_search --summary "found 50 relevant papers" --phase literature_review

# Learn about research concepts
srrd learn concept --concept hypothesis --context biology --level practical

# Get tutorial for research act
srrd learn act-tutorial --act data_collection --domain psychology --style step_by_step
```

## Success Metrics

### Quantitative Metrics
- Tool usage sequences that follow recommended workflows
- Time between tool uses (shorter indicates better guidance)
- Research act completion rates
- Educational tool usage frequency

### Qualitative Metrics
- User satisfaction with workflow guidance
- Learning effectiveness of educational content
- Quality of research methodology application
- Appropriateness of next-step recommendations

## Implementation Phases

### Phase 1: Core Workflow Tools
- Implement `start_research_act` and `get_act_progress_guidance`
- Create research act definitions and success criteria
- Basic workflow state tracking

### Phase 2: Smart Recommendations
- Implement `get_smart_next_steps` with context awareness
- Integration with existing workflow intelligence
- Warning and dependency detection

### Phase 3: Educational Support
- Implement research education tools
- Create comprehensive concept explanations
- Tutorial-style guidance for each research act

### Phase 4: Integration and Refinement
- CLI command integration
- Comprehensive testing and validation
- User feedback integration and improvements