# Conversational Guidance Enhancements

## Overview

Enhance existing MCP server tools to provide better interactive guidance within Claude Desktop and VS Code chat environments. Focus on improving the quality and interactivity of existing tools rather than creating complex multi-turn conversation systems.

## Goals

- Enhance existing MCP tools with better prompting and guidance
- Improve tool outputs to be more interactive and educational
- Add "follow-up suggestion" capabilities to existing tools
- Enable better theory challenging through enhanced tool responses

## Features

### 1. Enhanced Socratic Questioning Tool

**Current State**: `clarify_research_goals` provides basic research goal clarification

**Enhancement**: Improve the tool to provide more Socratic-style questioning within a single response

#### Implementation Plan

**File**: `srrd_builder/tools/research_planning.py`

```python
@mcp_tool("enhanced_socratic_guidance")
async def enhanced_socratic_guidance(
    research_area: str,
    current_understanding: str,
    guidance_focus: str = "research_question"
) -> dict:
    """
    Provide Socratic-style guidance with follow-up questions and suggestions
    
    Args:
        research_area: The research domain or topic
        current_understanding: User's current grasp of the topic
        guidance_focus: What to focus on (research_question, methodology, assumptions)
    
    Returns:
        dict: Socratic questions, guidance, and suggested next steps
    """
    # Enhanced logic that provides:
    # - Multiple probing questions
    # - Explanations of why each question matters
    # - Suggested follow-up tools to run
    # - Areas that need deeper exploration
```

### 2. Theory Challenge and Critique Tool

**Current State**: `validate_novel_theory` provides analysis but limited critical examination

**Enhancement**: Create a dedicated tool for critical theory examination

#### Implementation Plan

**File**: `srrd_builder/tools/novel_theory_development.py`

```python
@mcp_tool("challenge_theory_critically")
async def challenge_theory_critically(
    theory_description: str,
    theory_domain: str,
    challenge_level: str = "moderate"
) -> dict:
    """
    Provide critical challenges to a theory with specific questions and concerns
    
    Args:
        theory_description: The theory to examine
        theory_domain: Scientific domain (physics, biology, etc.)
        challenge_level: gentle, moderate, or rigorous
    
    Returns:
        dict: Critical questions, potential weaknesses, and areas for strengthening
    """
    # Provides:
    # - Specific critical questions about the theory
    # - Potential counterarguments to consider
    # - Suggestions for strengthening the theory
    # - Recommended validation approaches
```

### 3. Research Guidance with Next Steps

**Enhancement**: Add "what to do next" suggestions to existing tools

#### Implementation Plan

Enhance existing tools to include `recommended_next_tools` in their responses:

```python
# Example enhancement to existing tools
def add_next_step_recommendations(tool_result: dict, context: dict) -> dict:
    """Add intelligent next-step recommendations to tool results"""
    tool_result["recommended_next_steps"] = {
        "immediate_actions": ["tool1", "tool2"],
        "explanation": "Based on your results, consider these next steps...",
        "alternative_paths": ["tool3", "tool4"]
    }
    return tool_result
```

## Technical Implementation

### Enhanced Tool Structure

```python
# Enhanced tool response format
{
    "primary_result": "Main tool output",
    "socratic_questions": [
        {
            "question": "What specific aspect interests you most?",
            "purpose": "Helps narrow focus and identify passion areas",
            "follow_up_tools": ["semantic_search", "literature_review"]
        }
    ],
    "critical_considerations": [
        "Have you considered alternative explanations?",
        "What evidence would contradict your hypothesis?"
    ],
    "recommended_next_steps": {
        "immediate": ["suggest_methodology", "assess_foundational_assumptions"],
        "reasoning": "Your clarified goals suggest methodology selection is the logical next step"
    },
    "learning_prompts": "Key concepts to explore further..."
}
```

### Database Schema Updates

```sql
-- Track tool enhancement usage
CREATE TABLE IF NOT EXISTS enhanced_tool_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name VARCHAR(100) NOT NULL,
    enhancement_type VARCHAR(50) NOT NULL, -- socratic, critical, guidance
    user_satisfaction INTEGER, -- 1-5 rating if provided
    follow_up_tool_used VARCHAR(100),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Testing Strategy

### Unit Tests

#### test_enhanced_socratic_guidance.py
```python
import pytest
from srrd_builder.tools.research_planning import enhanced_socratic_guidance

class TestEnhancedSocraticGuidance:
    
    @pytest.mark.asyncio
    async def test_basic_socratic_guidance(self):
        """Test basic Socratic guidance functionality"""
        result = await enhanced_socratic_guidance(
            research_area="quantum computing",
            current_understanding="I know basic quantum mechanics",
            guidance_focus="research_question"
        )
        
        assert "socratic_questions" in result
        assert "recommended_next_steps" in result
        assert len(result["socratic_questions"]) >= 3
        
        # Verify question quality
        questions = result["socratic_questions"]
        assert any("what" in q["question"].lower() for q in questions)
        assert any("why" in q["question"].lower() for q in questions)
        assert any("how" in q["question"].lower() for q in questions)
    
    @pytest.mark.asyncio
    async def test_focus_area_adaptation(self):
        """Test that guidance adapts to different focus areas"""
        methodology_result = await enhanced_socratic_guidance(
            research_area="machine learning",
            current_understanding="I understand basic algorithms",
            guidance_focus="methodology"
        )
        
        assumptions_result = await enhanced_socratic_guidance(
            research_area="machine learning", 
            current_understanding="I understand basic algorithms",
            guidance_focus="assumptions"
        )
        
        # Results should differ based on focus
        assert methodology_result["socratic_questions"] != assumptions_result["socratic_questions"]
        assert "methodology" in str(methodology_result).lower()
        assert "assumption" in str(assumptions_result).lower()
    
    @pytest.mark.asyncio
    async def test_next_step_recommendations(self):
        """Test that appropriate next steps are recommended"""
        result = await enhanced_socratic_guidance(
            research_area="climate science",
            current_understanding="Basic understanding of climate systems",
            guidance_focus="research_question"
        )
        
        next_steps = result["recommended_next_steps"]
        assert "immediate" in next_steps
        assert "reasoning" in next_steps
        assert isinstance(next_steps["immediate"], list)
        assert len(next_steps["immediate"]) > 0
```

#### test_theory_challenge.py
```python
import pytest
from srrd_builder.tools.novel_theory_development import challenge_theory_critically

class TestTheoryChallenge:
    
    @pytest.mark.asyncio
    async def test_gentle_challenge(self):
        """Test gentle theory challenging"""
        theory = "Consciousness arises from quantum processes in the brain"
        
        result = await challenge_theory_critically(
            theory_description=theory,
            theory_domain="neuroscience",
            challenge_level="gentle"
        )
        
        assert "critical_questions" in result
        assert "potential_strengths" in result
        assert "areas_for_development" in result
        
        # Gentle challenges should be constructive
        questions = result["critical_questions"]
        assert len(questions) <= 5  # Not overwhelming
        assert any("consider" in q.lower() for q in questions)
    
    @pytest.mark.asyncio
    async def test_rigorous_challenge(self):
        """Test rigorous theory challenging"""
        theory = "Time travel is possible through quantum tunneling"
        
        result = await challenge_theory_critically(
            theory_description=theory,
            theory_domain="physics",
            challenge_level="rigorous"
        )
        
        assert len(result["critical_questions"]) >= 5
        assert "potential_weaknesses" in result
        assert "counterarguments" in result
        
        # Should identify specific issues
        weaknesses = result["potential_weaknesses"]
        assert len(weaknesses) > 0
        assert any("evidence" in w.lower() or "testable" in w.lower() for w in weaknesses)
    
    @pytest.mark.asyncio
    async def test_domain_specific_challenges(self):
        """Test that challenges are appropriate for the domain"""
        physics_result = await challenge_theory_critically(
            theory_description="New model of dark matter",
            theory_domain="physics",
            challenge_level="moderate"
        )
        
        biology_result = await challenge_theory_critically(
            theory_description="New evolutionary mechanism",
            theory_domain="biology", 
            challenge_level="moderate"
        )
        
        # Should contain domain-appropriate terminology
        physics_text = str(physics_result).lower()
        biology_text = str(biology_result).lower()
        
        assert any(term in physics_text for term in ["experiment", "prediction", "measurement"])
        assert any(term in biology_text for term in ["evolution", "selection", "organism"])
```

### Integration Tests

#### test_enhanced_tools_integration.py
```python
import pytest
from srrd_builder.server.mcp_server import MCPServer

class TestEnhancedToolsIntegration:
    
    @pytest.fixture
    def mcp_server(self):
        return MCPServer(test_mode=True)
    
    @pytest.mark.asyncio
    async def test_enhanced_tool_workflow(self, mcp_server):
        """Test enhanced tools work together in a research workflow"""
        
        # Start with enhanced Socratic guidance
        guidance_result = await mcp_server.call_tool(
            "enhanced_socratic_guidance",
            {
                "research_area": "artificial intelligence ethics",
                "current_understanding": "Basic knowledge of AI systems",
                "guidance_focus": "research_question"
            }
        )
        
        assert guidance_result["success"]
        next_tools = guidance_result["data"]["recommended_next_steps"]["immediate"]
        
        # Use one of the recommended tools
        if "assess_foundational_assumptions" in next_tools:
            assumptions_result = await mcp_server.call_tool(
                "assess_foundational_assumptions",
                {"research_context": "AI ethics research"}
            )
            assert assumptions_result["success"]
    
    @pytest.mark.asyncio 
    async def test_theory_challenge_integration(self, mcp_server):
        """Test theory challenge integrates with other validation tools"""
        
        # Challenge a theory
        challenge_result = await mcp_server.call_tool(
            "challenge_theory_critically",
            {
                "theory_description": "AI consciousness emerges at sufficient complexity",
                "theory_domain": "computer_science",
                "challenge_level": "moderate"
            }
        )
        
        assert challenge_result["success"]
        
        # Should suggest validation tools
        data = challenge_result["data"]
        assert "recommended_validation_approaches" in data
```

## CLI Integration

### New Commands
```bash
# Enhanced research guidance
srrd tool enhanced_socratic_guidance --research_area "quantum physics" --current_understanding "undergraduate level" --guidance_focus "methodology"

# Theory challenging
srrd tool challenge_theory_critically --theory_description "My theory about..." --theory_domain "physics" --challenge_level "rigorous"

# Get enhanced recommendations for any research context
srrd tool get_enhanced_recommendations --current_context "literature review completed" --research_domain "biology"
```

## Documentation Updates

### Tool Documentation
Each enhanced tool should include:
- Purpose and educational value
- When to use in research workflow
- How to interpret Socratic questions
- Following up on recommendations

### Integration with Existing Framework
- Tools work with existing research act structure
- Enhanced outputs integrate with progress tracking
- Recommendations align with workflow intelligence

## Success Metrics

### Quantitative
- Tool usage frequency increase
- Follow-up tool usage after recommendations
- Research session progression improvement

### Qualitative  
- Quality of Socratic questions generated
- Relevance of critical challenges
- User satisfaction with guidance depth

## Implementation Phases

### Phase 1: Core Tool Enhancements
- Enhance `clarify_research_goals` with Socratic elements
- Add critical challenge capabilities to theory validation
- Implement next-step recommendation system

### Phase 2: Integration and Testing
- Integrate enhanced tools with existing workflow
- Comprehensive testing suite
- Documentation updates

### Phase 3: Refinement
- User feedback integration
- Performance optimization  
- Additional enhancement patterns