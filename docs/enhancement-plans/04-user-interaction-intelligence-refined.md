# User Interaction Intelligence and Context Analysis - Refined

## Overview

Enhance the existing interaction tracking and user context analysis by building on the current `Interaction` data model, session management, and tool usage logging. This plan focuses on leveraging the existing infrastructure to capture richer user context and provide intelligent insights while avoiding redundant implementations.

## Current System Analysis

### Existing Interaction Infrastructure ✅

**Already Implemented:**
- `Interaction` data model with session tracking and metadata support
- Database schema with `interactions` table for multi-turn dialogues
- Tool usage logging in `tool_usage` table with timestamps and result summaries
- Session management with `sessions` table linking to projects
- Context-aware tools that capture tool parameters and execution context
- Research continuity tools that analyze tool usage patterns

**Current Capabilities:**
- Session-based interaction tracking and storage
- Tool usage patterns analysis and research progress correlation
- User context detection through project and session management
- Comprehensive tool parameter logging and result tracking

### Existing Models and Infrastructure:
- `Interaction` class in `work/code/mcp/models/interaction.py`
- `SQLiteManager` with comprehensive database operations
- `WorkflowIntelligence` for analyzing usage patterns and recommendations
- Context-aware decorator system for parameter capture

## Enhancement Strategy - Building on Existing

### 1. Enhanced User Input Analysis

**Enhancement**: Extend existing tool parameter capture to include semantic analysis

#### Implementation Plan

**File**: `work/code/mcp/utils/interaction_analyzer.py` (new, building on existing models)

```python
"""
User Interaction Analysis - Building on Existing Infrastructure
===========================================================

Enhances existing interaction tracking with semantic analysis capabilities
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from models.interaction import Interaction
from storage.sqlite_manager import SQLiteManager
from utils.current_project import get_current_project


class UserInteractionAnalyzer:
    """
    Enhanced interaction analysis building on existing Interaction model
    """
    
    def __init__(self, sqlite_manager: SQLiteManager):
        self.sqlite_manager = sqlite_manager
        
    async def analyze_tool_interaction(
        self,
        tool_name: str,
        tool_parameters: Dict[str, Any],
        tool_result: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Analyze tool interaction and extract user context insights
        
        Builds on existing tool_usage logging with enhanced analysis
        """
        # Extract user input content for analysis
        user_inputs = self._extract_user_content(tool_parameters)
        
        if not user_inputs:
            return {"analysis_available": False, "reason": "No user content to analyze"}
        
        # Perform semantic analysis
        semantic_analysis = self._analyze_semantic_content(user_inputs, tool_name)
        
        # Analyze research progression indicators
        progression_analysis = await self._analyze_research_progression(
            tool_name, tool_parameters, session_id
        )
        
        # Store enhanced interaction data using existing Interaction model
        interaction = Interaction(
            session_id=int(session_id) if session_id.isdigit() else 0,
            interaction_type="enhanced_tool_usage",
            content=json.dumps(user_inputs),
            domain_context=semantic_analysis.get("primary_domain"),
            novel_theory_context=semantic_analysis.get("novel_theory_indicators"),
            metadata={
                "tool_name": tool_name,
                "semantic_analysis": semantic_analysis,
                "progression_analysis": progression_analysis,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Store using existing database infrastructure
        await self._store_enhanced_interaction(interaction)
        
        return {
            "analysis_available": True,
            "semantic_insights": semantic_analysis,
            "progression_insights": progression_analysis,
            "interaction_stored": True
        }
    
    def _extract_user_content(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Extract user-provided textual content from tool parameters"""
        user_content = {}
        
        # Common parameter names that contain user input
        user_input_params = [
            "research_area", "initial_goals", "research_goals", "research_context",
            "theory_description", "query", "content", "hypothesis", "methodology",
            "current_understanding", "user_response", "search_query"
        ]
        
        for param_name, param_value in parameters.items():
            if param_name in user_input_params and isinstance(param_value, str):
                if len(param_value.strip()) > 0:
                    user_content[param_name] = param_value.strip()
        
        return user_content
    
    def _analyze_semantic_content(self, user_inputs: Dict[str, str], tool_name: str) -> Dict[str, Any]:
        """Analyze semantic content of user inputs"""
        combined_text = " ".join(user_inputs.values()).lower()
        
        analysis = {
            "word_count": len(combined_text.split()),
            "character_count": len(combined_text),
            "primary_domain": self._classify_research_domain(combined_text),
            "technical_sophistication": self._assess_technical_sophistication(combined_text),
            "research_intent": self._classify_research_intent(combined_text, tool_name),
            "novel_theory_indicators": self._detect_novel_theory_indicators(combined_text),
            "knowledge_level_indicators": self._assess_knowledge_level(combined_text),
            "uncertainty_markers": self._count_uncertainty_markers(combined_text),
            "specificity_score": self._calculate_specificity_score(combined_text)
        }
        
        return analysis
    
    def _classify_research_domain(self, text: str) -> str:
        """Classify research domain based on keyword analysis"""
        domain_keywords = {
            "physics": ["quantum", "particle", "relativity", "mechanics", "thermodynamics", "electromagnetic"],
            "computer_science": ["algorithm", "machine learning", "neural network", "programming", "software", "computing"],
            "biology": ["molecular", "cellular", "organism", "genetic", "protein", "evolution", "species"],
            "psychology": ["behavior", "cognitive", "mental", "brain", "consciousness", "learning", "memory"],
            "chemistry": ["molecular", "reaction", "compound", "synthesis", "catalysis", "organic"],
            "mathematics": ["theorem", "proof", "equation", "function", "calculus", "statistics", "probability"]
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        return "interdisciplinary"
    
    def _assess_technical_sophistication(self, text: str) -> float:
        """Assess technical sophistication level (0-1 scale)"""
        technical_indicators = [
            r'\b\w+tion\b',  # -tion endings (optimization, calculation)
            r'\b\w+ical\b',  # -ical endings (theoretical, empirical)  
            r'\b\w+ology\b', # -ology endings (methodology, technology)
            r'\b\w+metric\b', # -metric endings (parametric, geometric)
            r'\bmulti-\w+',   # multi- prefixes
            r'\bquasi-\w+',   # quasi- prefixes
        ]
        
        technical_count = sum(len(re.findall(pattern, text)) for pattern in technical_indicators)
        
        # Normalize by text length
        if len(text.split()) == 0:
            return 0.0
        
        sophistication = min(technical_count / len(text.split()) * 10, 1.0)
        return round(sophistication, 2)
    
    def _classify_research_intent(self, text: str, tool_name: str) -> str:
        """Classify research intent based on text and tool usage"""
        exploration_indicators = ["explore", "investigate", "understand", "learn", "discover"]
        validation_indicators = ["test", "verify", "validate", "confirm", "prove", "demonstrate"]
        application_indicators = ["apply", "implement", "develop", "create", "build", "design"]
        
        exploration_score = sum(1 for word in exploration_indicators if word in text)
        validation_score = sum(1 for word in validation_indicators if word in text)
        application_score = sum(1 for word in application_indicators if word in text)
        
        # Consider tool context
        if tool_name in ["clarify_research_goals", "semantic_search"]:
            exploration_score += 1
        elif tool_name in ["validate_novel_theory", "simulate_peer_review"]:
            validation_score += 1
        elif tool_name in ["suggest_methodology", "design_experimental_framework"]:
            application_score += 1
        
        scores = {
            "exploration": exploration_score,
            "validation": validation_score, 
            "application": application_score
        }
        
        if all(score == 0 for score in scores.values()):
            return "general_inquiry"
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _detect_novel_theory_indicators(self, text: str) -> Optional[str]:
        """Detect indicators of novel theory development"""
        novel_indicators = [
            "alternative", "novel", "new theory", "paradigm", "challenge", 
            "different approach", "innovative", "breakthrough", "revolutionary"
        ]
        
        detected = [indicator for indicator in novel_indicators if indicator in text]
        
        if detected:
            return f"Novel theory indicators detected: {', '.join(detected)}"
        return None
    
    def _assess_knowledge_level(self, text: str) -> str:
        """Assess user's knowledge level based on language sophistication"""
        beginner_indicators = ["basic", "simple", "beginner", "introduction", "help me understand"]
        intermediate_indicators = ["analyze", "compare", "evaluate", "methodology", "framework"]
        expert_indicators = ["paradigm", "theoretical foundation", "epistemological", "ontological"]
        
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in text)
        intermediate_score = sum(1 for indicator in intermediate_indicators if indicator in text)
        expert_score = sum(1 for indicator in expert_indicators if indicator in text)
        
        if expert_score > 0:
            return "expert"
        elif intermediate_score > beginner_score:
            return "intermediate"
        elif beginner_score > 0:
            return "beginner"
        else:
            return "intermediate"  # Default
    
    def _count_uncertainty_markers(self, text: str) -> int:
        """Count uncertainty markers in text"""
        uncertainty_markers = ["maybe", "perhaps", "might", "could", "possibly", "uncertain", "not sure"]
        return sum(1 for marker in uncertainty_markers if marker in text)
    
    def _calculate_specificity_score(self, text: str) -> float:
        """Calculate specificity score (0-1) based on concrete details"""
        specificity_indicators = [
            r'\b\d+\b',  # Numbers
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Proper names (e.g., "John Smith")
            r'\b\w+\s+method\b',  # Specific methods
            r'\b\w+\s+algorithm\b',  # Specific algorithms
            r'\b\w+\s+theory\b',  # Specific theories
        ]
        
        specificity_count = sum(len(re.findall(pattern, text)) for pattern in specificity_indicators)
        
        if len(text.split()) == 0:
            return 0.0
        
        specificity = min(specificity_count / len(text.split()) * 5, 1.0)
        return round(specificity, 2)
    
    async def _analyze_research_progression(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        session_id: str
    ) -> Dict[str, Any]:
        """Analyze research progression based on tool usage patterns"""
        # Get recent tool usage for this session
        recent_tools_query = """
            SELECT tool_name, timestamp FROM tool_usage 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        """
        
        async with self.sqlite_manager.connection.execute(recent_tools_query, (session_id,)) as cursor:
            recent_tools = await cursor.fetchall()
        
        tool_sequence = [row[0] for row in recent_tools]
        
        # Analyze progression patterns
        progression_analysis = {
            "current_tool": tool_name,
            "recent_sequence": tool_sequence,
            "progression_type": self._classify_progression_type(tool_sequence),
            "research_focus_shift": self._detect_focus_shifts(tool_sequence),
            "depth_progression": self._assess_depth_progression(tool_sequence)
        }
        
        return progression_analysis
    
    def _classify_progression_type(self, tool_sequence: List[str]) -> str:
        """Classify the type of research progression"""
        if len(tool_sequence) < 2:
            return "initial"
        
        # Check for logical research act progression
        act_progression_patterns = [
            ["clarify_research_goals", "suggest_methodology"],
            ["suggest_methodology", "design_experimental_framework"],
            ["semantic_search", "generate_document"]
        ]
        
        for pattern in act_progression_patterns:
            if len(tool_sequence) >= 2 and tool_sequence[-2:] == pattern:
                return "logical_progression"
        
        # Check for deepening pattern (same category tools)
        if len(set(tool_sequence)) < len(tool_sequence) * 0.7:
            return "deepening_focus"
        
        return "exploratory"
    
    def _detect_focus_shifts(self, tool_sequence: List[str]) -> List[str]:
        """Detect shifts in research focus based on tool categories"""
        tool_categories = {
            "planning": ["clarify_research_goals", "suggest_methodology"],
            "discovery": ["semantic_search", "discover_connections"],
            "validation": ["validate_novel_theory", "simulate_peer_review"],
            "generation": ["generate_document", "compile_bibliography"]
        }
        
        # Map tools to categories
        sequence_categories = []
        for tool in tool_sequence:
            for category, tools in tool_categories.items():
                if tool in tools:
                    sequence_categories.append(category)
                    break
        
        # Detect category shifts
        focus_shifts = []
        for i in range(1, len(sequence_categories)):
            if sequence_categories[i] != sequence_categories[i-1]:
                focus_shifts.append(f"{sequence_categories[i-1]} -> {sequence_categories[i]}")
        
        return focus_shifts
    
    def _assess_depth_progression(self, tool_sequence: List[str]) -> str:
        """Assess whether user is going deeper or broader"""
        if len(tool_sequence) < 3:
            return "insufficient_data"
        
        unique_tools = len(set(tool_sequence))
        total_tools = len(tool_sequence)
        
        diversity_ratio = unique_tools / total_tools
        
        if diversity_ratio > 0.8:
            return "broad_exploration"
        elif diversity_ratio < 0.5:
            return "deep_focus" 
        else:
            return "balanced_approach"
    
    async def _store_enhanced_interaction(self, interaction: Interaction):
        """Store enhanced interaction using existing database infrastructure"""
        # Use existing interactions table structure
        insert_query = """
            INSERT INTO interactions (
                session_id, interaction_type, user_input, ai_response, 
                timestamp, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        await self.sqlite_manager.connection.execute(
            insert_query,
            (
                interaction.session_id,
                interaction.interaction_type,
                interaction.content,  # User inputs as JSON
                "",  # AI response (empty for tool usage)
                datetime.now().isoformat(),
                json.dumps(interaction.metadata)
            )
        )
        await self.sqlite_manager.connection.commit()
```

### 2. Enhanced Research Journey Analysis

**Enhancement**: Build on existing workflow intelligence to provide deeper user insights

#### Implementation Plan

**File**: `work/code/mcp/tools/research_continuity.py` (extend existing)

```python
# Add to existing research_continuity.py

@context_aware(require_context=True)
async def analyze_user_research_journey(**kwargs) -> str:
    """
    Enhanced tool: Analyze user's research journey and evolution patterns
    
    Builds on existing workflow intelligence and interaction tracking
    """
    project_path = get_current_project()
    if not project_path:
        raise ContextAwareError("SRRD project context is required for this tool.")
    
    time_period = kwargs.get('time_period', 'all_time')
    include_predictions = kwargs.get('include_predictions', True)
    
    db_path = SQLiteManager.get_sessions_db_path(project_path)
    sqlite_manager = SQLiteManager(db_path)
    await sqlite_manager.initialize()
    
    # Get user interaction analysis
    analyzer = UserInteractionAnalyzer(sqlite_manager)
    
    # Analyze research journey components
    journey_analysis = await _analyze_complete_research_journey(
        sqlite_manager, analyzer, time_period
    )
    
    # Generate insights report
    insights_report = await _generate_journey_insights_report(
        journey_analysis, include_predictions
    )
    
    await sqlite_manager.close()
    return insights_report

async def _analyze_complete_research_journey(
    sqlite_manager: SQLiteManager, 
    analyzer: UserInteractionAnalyzer,
    time_period: str
) -> Dict[str, Any]:
    """Analyze complete research journey using existing data"""
    
    # Get tool usage history
    time_filter = _get_time_filter_query(time_period)
    tools_query = f"""
        SELECT tool_name, timestamp, result_summary 
        FROM tool_usage 
        WHERE {time_filter}
        ORDER BY timestamp ASC
    """
    
    async with sqlite_manager.connection.execute(tools_query) as cursor:
        tool_history = await cursor.fetchall()
    
    # Get enhanced interactions if available
    interactions_query = f"""
        SELECT interaction_type, user_input, metadata, timestamp
        FROM interactions 
        WHERE interaction_type = 'enhanced_tool_usage' AND {time_filter}
        ORDER BY timestamp ASC
    """
    
    try:
        async with sqlite_manager.connection.execute(interactions_query) as cursor:
            enhanced_interactions = await cursor.fetchall()
    except:
        enhanced_interactions = []  # Table might not exist yet
    
    # Analyze journey components
    journey_analysis = {
        "timeline": _create_research_timeline(tool_history),
        "domain_evolution": _analyze_domain_evolution(enhanced_interactions),
        "sophistication_progression": _analyze_sophistication_progression(enhanced_interactions),
        "research_focus_evolution": _analyze_focus_evolution(tool_history),
        "learning_indicators": _identify_learning_indicators(tool_history, enhanced_interactions),
        "productivity_patterns": _analyze_productivity_patterns(tool_history)
    }
    
    return journey_analysis

def _get_time_filter_query(time_period: str) -> str:
    """Get SQL time filter based on period"""
    if time_period == "last_week":
        return "timestamp >= datetime('now', '-7 days')"
    elif time_period == "last_month":
        return "timestamp >= datetime('now', '-30 days')"
    else:
        return "1=1"  # All time

def _create_research_timeline(tool_history: List) -> List[Dict[str, Any]]:
    """Create chronological research timeline"""
    timeline = []
    for tool_name, timestamp, result_summary in tool_history:
        timeline.append({
            "timestamp": timestamp,
            "tool_name": tool_name,
            "summary": result_summary,
            "research_act": _classify_tool_to_research_act(tool_name)
        })
    return timeline

def _classify_tool_to_research_act(tool_name: str) -> str:
    """Classify tool to research act for timeline analysis"""
    act_mappings = {
        "conceptualization": ["clarify_research_goals", "assess_foundational_assumptions", "generate_critical_questions"],
        "design_planning": ["suggest_methodology", "design_experimental_framework"],
        "implementation": ["execute_research_plan", "collect_data"],
        "analysis": ["analyze_data", "semantic_search", "discover_connections"],
        "synthesis": ["synthesize_findings", "validate_novel_theory"],
        "publication": ["generate_document", "compile_bibliography"]
    }
    
    for act, tools in act_mappings.items():
        if tool_name in tools:
            return act
    return "other"

async def _generate_journey_insights_report(
    journey_analysis: Dict[str, Any], 
    include_predictions: bool
) -> str:
    """Generate comprehensive journey insights report"""
    
    report_sections = []
    
    # Header
    report_sections.append("# Research Journey Analysis\n")
    
    # Timeline overview
    timeline = journey_analysis["timeline"]
    if timeline:
        report_sections.append("## Research Timeline")
        report_sections.append(f"**Research Period**: {timeline[0]['timestamp']} to {timeline[-1]['timestamp']}")
        report_sections.append(f"**Total Research Sessions**: {len(timeline)} tool interactions")
        
        # Research act progression
        acts_used = list(set(item["research_act"] for item in timeline))
        report_sections.append(f"**Research Acts Engaged**: {', '.join(acts_used)}")
    
    # Domain evolution
    domain_evolution = journey_analysis.get("domain_evolution", {})
    if domain_evolution:
        report_sections.append("\n## Research Domain Evolution")
        if "primary_domains" in domain_evolution:
            domains = domain_evolution["primary_domains"]
            report_sections.append(f"**Primary Research Domains**: {', '.join(domains)}")
        
        if "domain_shifts" in domain_evolution:
            shifts = domain_evolution["domain_shifts"]
            if shifts:
                report_sections.append("**Domain Focus Shifts Detected**:")
                for shift in shifts:
                    report_sections.append(f"- {shift}")
    
    # Learning progression
    learning_indicators = journey_analysis.get("learning_indicators", {})
    if learning_indicators:
        report_sections.append("\n## Learning and Development Indicators")
        
        if "knowledge_level_progression" in learning_indicators:
            progression = learning_indicators["knowledge_level_progression"]
            report_sections.append(f"**Knowledge Level Progression**: {progression}")
        
        if "sophistication_trend" in learning_indicators:
            trend = learning_indicators["sophistication_trend"]
            report_sections.append(f"**Technical Sophistication Trend**: {trend}")
    
    # Productivity patterns
    productivity = journey_analysis.get("productivity_patterns", {})
    if productivity:
        report_sections.append("\n## Research Productivity Patterns")
        
        if "peak_activity_times" in productivity:
            peak_times = productivity["peak_activity_times"]
            report_sections.append(f"**Peak Activity Periods**: {peak_times}")
        
        if "research_velocity" in productivity:
            velocity = productivity["research_velocity"]
            report_sections.append(f"**Average Research Velocity**: {velocity} tools per day")
    
    # Predictions if requested
    if include_predictions and timeline:
        report_sections.append("\n## Predictive Insights")
        predictions = _generate_research_predictions(journey_analysis)
        for prediction in predictions:
            report_sections.append(f"- {prediction}")
    
    return "\n".join(report_sections)

def _generate_research_predictions(journey_analysis: Dict[str, Any]) -> List[str]:
    """Generate predictive insights based on journey analysis"""
    predictions = []
    
    timeline = journey_analysis.get("timeline", [])
    if not timeline:
        return predictions
    
    # Predict next likely research act
    recent_acts = [item["research_act"] for item in timeline[-5:]]
    if recent_acts:
        current_act = recent_acts[-1]
        act_progression = {
            "conceptualization": "design_planning",
            "design_planning": "implementation", 
            "implementation": "analysis",
            "analysis": "synthesis",
            "synthesis": "publication"
        }
        
        next_act = act_progression.get(current_act)
        if next_act:
            predictions.append(f"Likely next research phase: {next_act}")
    
    # Predict research needs based on patterns
    focus_evolution = journey_analysis.get("research_focus_evolution", {})
    if focus_evolution.get("trend") == "deepening":
        predictions.append("Trend suggests deepening focus - consider validation and peer review tools")
    elif focus_evolution.get("trend") == "broadening":
        predictions.append("Trend suggests broadening scope - consider synthesis and integration tools")
    
    return predictions
```

## Testing Strategy - Following Proven Patterns

### Unit Tests Following Existing Structure

**File**: `work/tests/unit/tools/test_user_interaction_analysis.py`

```python
#!/usr/bin/env python3
"""
Unit Tests for User Interaction Analysis
=====================================

Tests enhanced user interaction analysis functionality:
- Semantic content analysis
- Research progression detection
- Journey analysis and insights
"""
import pytest
import tempfile
import json
from pathlib import Path

class TestUserInteractionAnalysis:
    """Test enhanced user interaction analysis functionality"""

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

    def test_semantic_content_analysis(self):
        """Test semantic analysis of user inputs"""
        from utils.interaction_analyzer import UserInteractionAnalyzer
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("semantic")
        db_path = temp_dir / "test.db"
        sqlite_manager = SQLiteManager(str(db_path))
        
        analyzer = UserInteractionAnalyzer(sqlite_manager)
        
        # Test sophisticated computer science input
        sophisticated_input = {
            "research_area": "machine learning optimization using gradient descent variants",
            "research_goals": "Develop novel optimization algorithms for deep neural networks"
        }
        
        analysis = analyzer._analyze_semantic_content(sophisticated_input, "clarify_research_goals")
        
        assert analysis["primary_domain"] == "computer_science"
        assert analysis["technical_sophistication"] > 0.5
        assert analysis["research_intent"] in ["exploration", "application"]
        assert analysis["knowledge_level_indicators"] in ["intermediate", "expert"]
        
        # Test beginner-level input
        beginner_input = {
            "research_area": "I want to learn about basic physics concepts",
            "initial_goals": "Help me understand how things work"
        }
        
        beginner_analysis = analyzer._analyze_semantic_content(beginner_input, "clarify_research_goals")
        
        assert beginner_analysis["knowledge_level_indicators"] == "beginner"
        assert beginner_analysis["specificity_score"] < 0.5

    def test_research_domain_classification(self):
        """Test research domain classification accuracy"""
        from utils.interaction_analyzer import UserInteractionAnalyzer
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("domain")
        db_path = temp_dir / "test.db"
        sqlite_manager = SQLiteManager(str(db_path))
        
        analyzer = UserInteractionAnalyzer(sqlite_manager)
        
        # Test physics classification
        physics_text = "quantum mechanics relativity particle physics electromagnetic theory"
        physics_domain = analyzer._classify_research_domain(physics_text)
        assert physics_domain == "physics"
        
        # Test biology classification
        biology_text = "molecular biology cellular organism genetic protein evolution"
        biology_domain = analyzer._classify_research_domain(biology_text)
        assert biology_domain == "biology"
        
        # Test interdisciplinary classification
        mixed_text = "general research question about various topics"
        mixed_domain = analyzer._classify_research_domain(mixed_text)
        assert mixed_domain == "interdisciplinary"

    def test_research_progression_analysis(self):
        """Test research progression pattern detection"""
        from utils.interaction_analyzer import UserInteractionAnalyzer
        
        analyzer = UserInteractionAnalyzer(None)  # No DB needed for this test
        
        # Test logical progression
        logical_sequence = ["clarify_research_goals", "suggest_methodology", "design_experimental_framework"]
        progression_type = analyzer._classify_progression_type(logical_sequence)
        assert progression_type == "logical_progression"
        
        # Test deepening focus (repeated tools)
        deepening_sequence = ["semantic_search", "semantic_search", "discover_connections", "semantic_search"]
        deepening_type = analyzer._classify_progression_type(deepening_sequence)
        assert deepening_type == "deepening_focus"
        
        # Test exploratory pattern
        exploratory_sequence = ["clarify_research_goals", "semantic_search", "validate_novel_theory", "generate_document"]
        exploratory_type = analyzer._classify_progression_type(exploratory_sequence)
        assert exploratory_type == "exploratory"

    @pytest.mark.asyncio
    async def test_enhanced_interaction_analysis_integration(self):
        """Test complete interaction analysis with real database"""
        from utils.interaction_analyzer import UserInteractionAnalyzer
        from storage.sqlite_manager import SQLiteManager
        
        temp_dir = self.create_temp_dir("integration")
        db_path = temp_dir / "test_sessions.db"
        
        sqlite_manager = SQLiteManager(str(db_path))
        await sqlite_manager.initialize()
        
        analyzer = UserInteractionAnalyzer(sqlite_manager)
        
        # Test tool interaction analysis
        tool_parameters = {
            "research_area": "novel quantum computing algorithms for optimization problems",
            "initial_goals": "Develop quantum algorithms that outperform classical methods",
            "experience_level": "intermediate"
        }
        
        tool_result = {"success": True, "clarified_goals": "Quantum optimization research"}
        
        analysis_result = await analyzer.analyze_tool_interaction(
            "clarify_research_goals",
            tool_parameters,
            tool_result, 
            "test_session_1"
        )
        
        assert analysis_result["analysis_available"] == True
        assert "semantic_insights" in analysis_result
        assert "progression_insights" in analysis_result
        assert analysis_result["interaction_stored"] == True
        
        # Verify semantic insights
        semantic_insights = analysis_result["semantic_insights"]
        assert semantic_insights["primary_domain"] in ["physics", "computer_science"]
        assert semantic_insights["technical_sophistication"] > 0.3
        
        await sqlite_manager.close()
```

### Integration Tests - Real Database Pattern

**File**: `work/tests/integration/test_user_journey_analysis_integration.py`

```python
#!/usr/bin/env python3
"""
Integration Tests for User Journey Analysis
========================================

Tests complete user journey analysis with real research workflow.
"""
import pytest
import tempfile
import os
from pathlib import Path

class TestUserJourneyAnalysisIntegration:
    """Test user journey analysis integration"""

    @pytest.mark.asyncio
    async def test_complete_research_journey_analysis(self):
        """Test complete research journey analysis with real workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project using existing CLI
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="computer_science", template="basic")
            result = handle_init(args)
            assert result == 0
            
            # Create research activity sequence
            from tools.research_planning import clarify_research_goals, suggest_methodology
            from tools.search_discovery import semantic_search_tool
            
            # Simulate research progression
            await clarify_research_goals(
                research_area="machine learning optimization using novel gradient descent variants",
                initial_goals="Develop optimization algorithms that converge faster than existing methods",
                experience_level="intermediate"
            )
            
            await suggest_methodology(
                research_goals="Fast convergence optimization algorithms",
                domain="computer_science"
            )
            
            await semantic_search_tool(
                query="gradient descent optimization machine learning convergence",
                search_scope="comprehensive"
            )
            
            # Test journey analysis
            from tools.research_continuity import analyze_user_research_journey
            
            journey_analysis = await analyze_user_research_journey(
                time_period="all_time",
                include_predictions=True
            )
            
            # Should contain comprehensive journey analysis
            assert "Research Journey Analysis" in journey_analysis
            assert "Research Timeline" in journey_analysis
            assert "machine learning" in journey_analysis.lower() or "computer" in journey_analysis.lower()
            
            # Should show research progression
            assert "clarify_research_goals" in journey_analysis
            assert "suggest_methodology" in journey_analysis
            assert "semantic_search" in journey_analysis
            
            # Should include predictions
            if "Predictive Insights" in journey_analysis:
                assert "next research phase" in journey_analysis.lower() or "next" in journey_analysis.lower()

    @pytest.mark.asyncio
    async def test_interaction_analysis_with_enhanced_data(self):
        """Test interaction analysis when enhanced interaction data is available"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Initialize project
            from srrd_builder.cli.commands.init import handle_init
            from tests.conftest import MockArgs
            
            args = MockArgs(domain="physics", template="theoretical")
            result = handle_init(args)
            assert result == 0
            
            # Create enhanced interaction data
            from utils.interaction_analyzer import UserInteractionAnalyzer
            from storage.sqlite_manager import SQLiteManager
            
            db_path = SQLiteManager.get_sessions_db_path(temp_dir)
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            analyzer = UserInteractionAnalyzer(sqlite_manager)
            
            # Simulate enhanced interaction
            sophisticated_params = {
                "theory_description": "Novel interpretation of quantum measurement using consciousness-based collapse mechanisms",
                "theory_domain": "quantum_physics",
                "validation_approach": "Mathematical formalism with experimental predictions"
            }
            
            analysis_result = await analyzer.analyze_tool_interaction(
                "validate_novel_theory",
                sophisticated_params,
                {"success": True, "validation_score": 0.8},
                "session_1"
            )
            
            assert analysis_result["analysis_available"] == True
            
            # Test journey analysis with enhanced data
            from tools.research_continuity import analyze_user_research_journey
            
            enhanced_journey = await analyze_user_research_journey(
                time_period="all_time",
                include_predictions=True
            )
            
            # Should incorporate enhanced analysis
            assert "Research Journey Analysis" in enhanced_journey
            
            await sqlite_manager.close()
```

## Implementation Phases

### Phase 1: Enhanced Interaction Analysis (2 weeks)
- Create `UserInteractionAnalyzer` building on existing `Interaction` model
- Implement semantic content analysis for user inputs
- Add research progression analysis using existing database
- Follow existing context-aware patterns and database schemas

### Phase 2: Journey Analysis Tools (2 weeks)
- Extend `research_continuity.py` with journey analysis capabilities
- Build on existing `WorkflowIntelligence` and progress tracking
- Add predictive insights based on usage patterns
- Integrate with existing comprehensive reporting

### Phase 3: Testing Following Proven Patterns (1 week)
- Create unit tests following existing patterns
- Add integration tests using real databases and workflows
- Follow 3-tier test structure and avoid over-mocking
- Maintain 100% test pass rate

### Phase 4: Integration and Documentation (1 week)
- Integrate with existing CLI and web interface
- Update documentation building on existing tool guides
- Performance optimization for semantic analysis
- User feedback integration and refinement

## Success Metrics

### Quantitative Metrics
- Semantic analysis accuracy (measured against manual classification)
- Journey analysis coverage (percentage of user interactions analyzed)
- Prediction accuracy for next research steps
- Integration test coverage maintaining 100% pass rate

### Qualitative Metrics
- Usefulness of semantic insights for research guidance
- Accuracy of research progression detection
- Value of predictive insights for users
- Integration quality with existing robust system

## Building on Existing Strengths

### Leveraging Current Infrastructure
- **Database Schema**: Use existing `interactions`, `tool_usage`, and `sessions` tables
- **Data Models**: Build on existing `Interaction` class and `SQLiteManager`
- **Context System**: Use existing context-aware tools and parameter capture
- **Workflow Intelligence**: Extend existing `WorkflowIntelligence` capabilities

### Avoiding Redundancy
- **Don't Recreate**: Extend existing interaction tracking infrastructure
- **Don't Replace**: Build on existing comprehensive tool usage logging
- **Don't Duplicate**: Use existing database operations and session management
- **Don't Over-Engineer**: Add intelligence incrementally to proven system

This refined plan builds systematically on the existing robust interaction tracking and session management infrastructure while adding intelligent analysis capabilities that integrate seamlessly with the current system architecture.