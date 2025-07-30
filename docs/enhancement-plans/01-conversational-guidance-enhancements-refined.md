# Conversational Guidance Enhancements - Refined

## Overview

Enhance existing MCP server tools to provide richer interactive guidance within Claude Desktop and VS Code chat environments. This plan builds on the current `research_planning.py` and `methodology_advisory.py` tools to avoid reinvention while adding sophisticated conversational elements.

## Current System Analysis

### Existing Conversational Infrastructure ✅

**Already Implemented:**
- `ResearchPlanningTool` with Socratic questioning capabilities
- Domain-specific question banks (theoretical_physics, general)
- Experience-level adaptation (beginner, intermediate, expert)
- Novel theory mode with paradigm innovation questions
- `user_interaction_required` and `next_step_options` in tool responses
- `Interaction` data model for storing user interactions

**Existing Tools to Enhance:**
- `clarify_research_goals` - Already has follow-up questions and methodology suggestions
- `suggest_methodology` - Already provides validation frameworks and next steps  
- Context-aware tools with proper `@context_aware` decorators

## Enhancement Strategy - Building on Existing

### 1. Enhance Existing Socratic Questioning

**Enhancement**: Expand question banks and add progressive questioning logic

#### Implementation Plan

**File**: `work/code/mcp/tools/research_planning.py` (extend existing)

```python
class ResearchPlanningTool:
    """Enhanced MCP tool for research planning with advanced Socratic questioning"""

    def __init__(self):
        # Extend existing socratic_questions with more domains and question types
        self.socratic_questions.update({
            "computer_science": {
                "clarification": [
                    "What computational problem are you trying to solve?",
                    "How does your approach differ from existing algorithms?",
                    "What are the performance requirements for your solution?",
                ],
                "assumption": [
                    "What assumptions are you making about input data characteristics?",
                    "How do you handle edge cases and error conditions?",
                    "What scalability assumptions underlie your approach?",
                ],
                "validation": [
                    "How will you benchmark your solution against existing methods?",
                    "What test datasets will you use for validation?",
                    "How will you measure and report performance improvements?",
                ]
            },
            "biology": {
                "clarification": [
                    "What biological system or process are you investigating?",
                    "At what level of organization are you focusing (molecular, cellular, organismal)?",
                    "How does this research connect to broader biological principles?",
                ],
                "methodology": [
                    "What experimental controls will you use?",
                    "How will you ensure reproducibility of biological measurements?",
                    "What ethical considerations apply to your biological research?",
                ]
            }
        })

    async def enhanced_socratic_dialogue(
        self,
        research_context: str,
        user_response: str = None,
        dialogue_depth: int = 1,
        focus_area: str = "clarification",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Enhanced tool: Progressive Socratic dialogue with depth control
        
        Builds on existing clarify_research_goals but adds progressive questioning
        """
        domain = kwargs.get('domain_specialization', 'general')
        question_bank = self.socratic_questions.get(domain, self.socratic_questions["general"])
        
        # Progressive questioning based on depth
        if dialogue_depth == 1:
            questions = question_bank.get("clarification", [])[:2]
        elif dialogue_depth == 2:
            questions = question_bank.get("assumption", [])[:2]  
        elif dialogue_depth >= 3:
            questions = question_bank.get("validation", [])[:2]
        
        # Analyze user response if provided
        response_analysis = None
        if user_response:
            response_analysis = self._analyze_user_response(user_response, focus_area)
        
        # Generate contextual follow-ups based on response
        contextual_questions = []
        if response_analysis:
            contextual_questions = self._generate_contextual_followups(
                response_analysis, domain, dialogue_depth
            )
        
        return {
            "progressive_questions": questions,
            "contextual_followups": contextual_questions,
            "response_analysis": response_analysis,
            "dialogue_depth": dialogue_depth,
            "suggested_next_depth": min(dialogue_depth + 1, 3),
            "user_interaction_required": f"Please respond to these {focus_area} questions. I'll provide deeper questions based on your answers.",
            "next_step_options": [
                f"Answer the {focus_area} questions to proceed to deeper inquiry",
                "Ask me to focus on a specific aspect that interests you most",
                "Request methodology suggestions based on your responses"
            ]
        }

    def _analyze_user_response(self, response: str, focus_area: str) -> Dict[str, Any]:
        """Analyze user response for sophistication and content patterns"""
        analysis = {
            "response_length": len(response.split()),
            "technical_terms": self._count_technical_terms(response),
            "uncertainty_indicators": self._detect_uncertainty(response),
            "specificity_level": self._assess_specificity(response),
            "follow_up_needed": []
        }
        
        # Determine follow-up needs based on analysis
        if analysis["specificity_level"] < 0.5:
            analysis["follow_up_needed"].append("More specific details needed")
        if analysis["uncertainty_indicators"] > 2:
            analysis["follow_up_needed"].append("Clarification of uncertain points")
            
        return analysis

    def _generate_contextual_followups(self, analysis: Dict, domain: str, depth: int) -> List[str]:
        """Generate contextual follow-up questions based on user response analysis"""
        followups = []
        
        if "More specific details needed" in analysis["follow_up_needed"]:
            followups.append("Can you provide more specific details about your approach?")
        
        if analysis["technical_terms"] < 2 and depth > 1:
            followups.append("What technical methods or tools are you considering?")
        
        return followups
```

### 2. Enhanced Theory Challenge Tool

**Enhancement**: Build on existing novel theory validation with critical examination

#### Implementation Plan

**File**: `work/code/mcp/tools/novel_theory_development.py` (extend existing)

```python
@context_aware(require_context=True)
async def enhanced_theory_challenger(**kwargs) -> Dict[str, Any]:
    """
    Enhanced critical examination tool building on existing validate_novel_theory
    """
    theory_description = kwargs.get('theory_description', '')
    domain = kwargs.get('theory_domain', 'general')
    challenge_intensity = kwargs.get('challenge_intensity', 'moderate')
    
    # Use existing novel theory validation as base
    base_validation = await validate_novel_theory_tool(**kwargs)
    
    # Add progressive critical challenges
    challenges = _generate_progressive_challenges(theory_description, domain, challenge_intensity)
    
    # Add paradigm comparison analysis
    paradigm_analysis = _analyze_paradigm_implications(theory_description, domain)
    
    return {
        **base_validation,  # Include existing validation results
        "critical_challenges": challenges,
        "paradigm_implications": paradigm_analysis,
        "challenge_progression": {
            "current_level": challenge_intensity,
            "next_level": _get_next_challenge_level(challenge_intensity),
            "escalation_available": challenge_intensity != 'rigorous'
        },
        "user_interaction_required": "Please address these critical challenges. I can escalate the examination intensity if needed.",
        "next_step_options": [
            "Address the critical challenges point by point",
            "Request more rigorous examination if ready",
            "Ask for specific guidance on strengthening weak points"
        ]
    }
```

## Testing Strategy - Following Proven Patterns

### Unit Tests - Following Existing Patterns

**File**: `work/tests/unit/tools/test_enhanced_research_planning.py`

```python
#!/usr/bin/env python3
"""
Unit Tests for Enhanced Research Planning Tools
============================================

Tests enhanced conversational guidance functionality:
- Progressive Socratic questioning
- User response analysis
- Contextual follow-up generation
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestEnhancedResearchPlanning:
    """Test enhanced research planning functionality"""

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

    def test_enhanced_socratic_dialogue_progression(self):
        """Test progressive Socratic dialogue functionality"""
        from tools.research_planning import ResearchPlanningTool
        
        tool = ResearchPlanningTool()
        
        # Test depth 1 (clarification questions)
        result_depth1 = await tool.enhanced_socratic_dialogue(
            research_context="quantum computing research",
            dialogue_depth=1,
            focus_area="clarification",
            domain_specialization="computer_science"
        )
        
        assert "progressive_questions" in result_depth1
        assert len(result_depth1["progressive_questions"]) <= 2
        assert result_depth1["dialogue_depth"] == 1
        assert result_depth1["suggested_next_depth"] == 2
        
        # Test depth 2 (assumption questions)
        result_depth2 = await tool.enhanced_socratic_dialogue(
            research_context="quantum computing research",
            user_response="I want to develop quantum algorithms for optimization",
            dialogue_depth=2,
            focus_area="assumption",
            domain_specialization="computer_science"
        )
        
        assert result_depth2["dialogue_depth"] == 2
        assert "response_analysis" in result_depth2
        assert result_depth2["response_analysis"] is not None

    def test_user_response_analysis(self):
        """Test user response analysis functionality"""
        from tools.research_planning import ResearchPlanningTool
        
        tool = ResearchPlanningTool()
        
        # Test sophisticated response
        sophisticated_response = "I am developing lattice-based post-quantum cryptographic algorithms using ring learning with errors problems to ensure security against quantum adversaries"
        
        analysis = tool._analyze_user_response(sophisticated_response, "clarification")
        
        assert analysis["technical_terms"] >= 3
        assert analysis["specificity_level"] > 0.7
        assert len(analysis["follow_up_needed"]) <= 1

    def test_contextual_followup_generation(self):
        """Test contextual follow-up question generation"""
        from tools.research_planning import ResearchPlanningTool
        
        tool = ResearchPlanningTool()
        
        # Test analysis that needs more specificity
        analysis = {
            "response_length": 5,
            "technical_terms": 0,
            "uncertainty_indicators": 1,
            "specificity_level": 0.3,
            "follow_up_needed": ["More specific details needed"]
        }
        
        followups = tool._generate_contextual_followups(analysis, "computer_science", 1)
        
        assert len(followups) > 0
        assert any("specific" in q.lower() for q in followups)

    def test_domain_specific_question_banks(self):
        """Test that enhanced question banks include new domains"""
        from tools.research_planning import ResearchPlanningTool
        
        tool = ResearchPlanningTool()
        
        # Test computer science domain
        assert "computer_science" in tool.socratic_questions
        assert "clarification" in tool.socratic_questions["computer_science"]
        assert "assumption" in tool.socratic_questions["computer_science"]
        
        # Test biology domain
        assert "biology" in tool.socratic_questions
        assert "methodology" in tool.socratic_questions["biology"]
```

### Integration Tests - Real Database Pattern

**File**: `work/tests/integration/test_enhanced_conversational_workflow.py`

```python  
#!/usr/bin/env python3
"""
Integration Tests for Enhanced Conversational Workflow
===================================================

Tests complete conversational workflow with real database integration.
Follows the proven pattern of using temporary directories and real databases.
"""
import pytest
import tempfile
import os
from pathlib import Path

class TestEnhancedConversationalWorkflow:
    """Test enhanced conversational workflow integration"""

    @pytest.mark.asyncio
    async def test_progressive_dialogue_with_database_persistence(self):
        """Test progressive dialogue workflow with real database storage"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="computer_science", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Test progressive dialogue sequence
            from tools.research_planning import enhanced_socratic_dialogue
            
            # Depth 1 - Initial clarification
            result1 = await enhanced_socratic_dialogue(
                research_context="machine learning optimization",
                dialogue_depth=1,
                domain_specialization="computer_science"
            )
            
            assert result1["dialogue_depth"] == 1
            assert len(result1["progressive_questions"]) > 0
            
            # Depth 2 - With user response
            result2 = await enhanced_socratic_dialogue(
                research_context="machine learning optimization", 
                user_response="I want to optimize neural network training using novel gradient descent variants",
                dialogue_depth=2,
                domain_specialization="computer_science"
            )
            
            assert result2["dialogue_depth"] == 2
            assert "response_analysis" in result2
            assert result2["response_analysis"]["technical_terms"] > 0

    @pytest.mark.asyncio
    async def test_theory_challenge_integration_with_existing_validation(self):
        """Test enhanced theory challenger integrates with existing validation tools"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="physics", template="theoretical")
            result = handle_init(args)
            assert result == 0
            
            # Test enhanced theory challenger
            from tools.novel_theory_development import enhanced_theory_challenger
            
            result = await enhanced_theory_challenger(
                theory_description="Consciousness arises from quantum coherence in neural microtubules",
                theory_domain="neuroscience",
                challenge_intensity="moderate"
            )
            
            # Should include existing validation results
            assert "equal_treatment_score" in result or "validation_results" in result
            
            # Should include new critical challenges
            assert "critical_challenges" in result
            assert "paradigm_implications" in result
            assert len(result["critical_challenges"]) > 0
```

## Implementation Phases

### Phase 1: Enhance Existing Tools (2-3 weeks)
- Extend `ResearchPlanningTool` with enhanced question banks
- Add progressive dialogue capabilities to existing tools
- Implement user response analysis methods
- Follow existing `@context_aware` decorator patterns

### Phase 2: Critical Theory Enhancement (2 weeks)  
- Enhance existing `novel_theory_development.py` tools
- Add progressive challenge capabilities
- Integrate with existing validation frameworks
- Maintain equal treatment principle implementation

### Phase 3: Testing Following Proven Patterns (1 week)
- Create unit tests following existing patterns in `work/tests/unit/tools/`
- Add integration tests using real databases and temporary directories
- Follow the 3-tier test structure (unit/integration/validation)
- Avoid over-mocking as highlighted in test suite guidelines

### Phase 4: Documentation and CLI Integration (1 week)
- Update existing tool documentation
- Add CLI examples building on existing patterns
- Integration with existing web interface for testing

## Success Metrics

### Quantitative Metrics
- Enhanced question bank coverage (add 3+ new domains)
- Progressive dialogue depth utilization (track depth progression)
- User response analysis accuracy (measured against manual analysis)
- Integration test coverage maintaining 100% pass rate

### Qualitative Metrics
- Quality of contextual follow-up questions
- Effectiveness of progressive questioning depth
- User satisfaction with enhanced guidance
- Integration quality with existing tool ecosystem

## Avoiding Common Pitfalls

### Following Test Suite Warnings
- **Real Integration Testing**: Use temporary databases and directories, not mocks
- **End-to-End Validation**: Test complete workflows from init to tool usage
- **Context-Aware Testing**: Properly test tools with `@context_aware` decorators
- **Avoid Over-Mocking**: Mock only external services, test real business logic

### Building on Existing Architecture
- **Extend, Don't Replace**: Enhance existing `ResearchPlanningTool` class
- **Follow Naming Conventions**: Use existing parameter and return value patterns
- **Maintain Context Awareness**: Use existing `@context_aware` decorator properly
- **Database Integration**: Use existing `SQLiteManager` and session management

This refined plan builds incrementally on the robust existing infrastructure while adding sophisticated conversational capabilities that enhance rather than replace the current tools.