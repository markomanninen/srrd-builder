"""
Research Planning MCP Tool
Provides Socratic questioning and methodology guidance for research planning
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import context-aware decorator
import sys
from pathlib import Path

# Fix import path issues by adding utils directory to sys.path
current_dir = Path(__file__).parent.parent
utils_dir = current_dir / "utils"
if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

from context_decorator import context_aware, project_required

class ResearchPlanningTool:
    """MCP tool for research planning with Socratic questioning"""
    
    def __init__(self):
        self.socratic_questions = {
            "theoretical_physics": {
                "clarification": [
                    "What specific aspect of theoretical physics does your research address?",
                    "What existing theories or models are you building upon?",
                    "How does your approach differ from current mainstream theories?"
                ],
                "assumption": [
                    "What fundamental assumptions underlie your theoretical framework?",
                    "Which of these assumptions have been experimentally validated?",
                    "Are there alternative assumptions that could lead to different conclusions?"
                ],
                "evidence": [
                    "What mathematical formalism supports your theoretical predictions?",
                    "What experimental evidence would validate your theory?",
                    "How does your theory explain existing experimental observations?"
                ],
                "paradigm_innovation": [
                    "How does your theory challenge existing paradigms in physics?",
                    "What foundational principles of current physics does your work question?",
                    "What would be the implications if your alternative framework is correct?"
                ]
            },
            "general": {
                "clarification": [
                    "What is the core research question you're trying to answer?",
                    "Why is this research important to your field?",
                    "What gap in current knowledge does this address?"
                ],
                "assumption": [
                    "What assumptions are you making about your research approach?",
                    "What background knowledge are you taking for granted?",
                    "How might these assumptions limit your conclusions?"
                ],
                "evidence": [
                    "What evidence supports your research hypothesis?",
                    "What methods will you use to gather evidence?",
                    "How will you know if your hypothesis is wrong?"
                ]
            }
        }
    
    async def clarify_research_goals(self, research_area: str, initial_goals: str, 
                                   experience_level: str = "intermediate",
                                   domain_specialization: str = "general",
                                   novel_theory_mode: bool = False) -> Dict[str, Any]:
        """
        MCP tool: Clarify research objectives through Socratic questioning
        """
        
        # Select appropriate question bank
        question_bank = self.socratic_questions.get(domain_specialization, 
                                                   self.socratic_questions["general"])
        
        # Generate contextual questions
        questions = []
        
        # Start with clarification questions
        clarification_questions = question_bank["clarification"]
        questions.extend(clarification_questions[:2])  # First 2 questions
        
        # Add assumption questions for intermediate/expert level
        if experience_level in ["intermediate", "expert"]:
            assumption_questions = question_bank["assumption"]
            questions.extend(assumption_questions[:1])
        
        # Add paradigm innovation questions for novel theory mode
        if novel_theory_mode and "paradigm_innovation" in question_bank:
            paradigm_questions = question_bank["paradigm_innovation"]
            questions.extend(paradigm_questions[:1])
        
        # Generate methodology suggestions based on domain
        methodology_suggestions = self._suggest_methodologies(domain_specialization, 
                                                            research_area, novel_theory_mode)
        
        # Generate next steps
        next_steps = self._generate_next_steps(research_area, experience_level, novel_theory_mode)
        
        return {
            "clarified_goals": self._analyze_goals(initial_goals, domain_specialization),
            "follow_up_questions": questions,
            "methodology_suggestions": methodology_suggestions,
            "next_steps": next_steps,
            "novel_theory_guidance": self._get_novel_theory_guidance() if novel_theory_mode else None
        }
    
    async def suggest_methodology(self, research_goals: str, domain: str,
                                constraints: Optional[Dict[str, Any]] = None,
                                novel_theory_flag: bool = False) -> Dict[str, Any]:
        """
        MCP tool: Recommend appropriate research methodologies
        """
        
        methodologies = []
        
        if domain == "theoretical_physics":
            methodologies = [
                {
                    "name": "Mathematical Modeling",
                    "description": "Develop mathematical formalism for theoretical predictions",
                    "suitability": "High for theoretical work",
                    "time_requirement": "6-12 months",
                    "resources_needed": ["Mathematical software", "Literature access"]
                },
                {
                    "name": "Computational Simulation", 
                    "description": "Numerical validation of theoretical predictions",
                    "suitability": "Medium to High",
                    "time_requirement": "3-9 months",
                    "resources_needed": ["Computing resources", "Programming skills"]
                }
            ]
            
            if novel_theory_flag:
                methodologies.append({
                    "name": "Paradigm Comparison Analysis",
                    "description": "Systematic comparison with existing theoretical frameworks",
                    "suitability": "Essential for novel theories",
                    "time_requirement": "4-8 months", 
                    "resources_needed": ["Comprehensive literature review", "Analytical framework"]
                })
        
        else:  # General methodologies
            methodologies = [
                {
                    "name": "Literature Review",
                    "description": "Systematic analysis of existing research",
                    "suitability": "Essential for all research",
                    "time_requirement": "2-4 months",
                    "resources_needed": ["Database access", "Reference management"]
                },
                {
                    "name": "Experimental Design",
                    "description": "Design controlled experiments to test hypotheses",
                    "suitability": "High for empirical research",
                    "time_requirement": "3-6 months",
                    "resources_needed": ["Lab access", "Equipment", "Participants"]
                }
            ]
        
        # Filter based on constraints
        if constraints:
            methodologies = self._filter_by_constraints(methodologies, constraints)
        
        return {
            "recommended_methodologies": methodologies,
            "domain_specific_considerations": self._get_domain_considerations(domain),
            "novel_theory_adaptations": self._get_novel_theory_adaptations() if novel_theory_flag else None,
            "validation_framework": self._get_validation_framework(domain, novel_theory_flag)
        }
    
    def _analyze_goals(self, goals: str, domain: str) -> str:
        """Analyze and refine research goals"""
        # Simple analysis - in real implementation, would use AI
        analysis = f"Based on your stated goals in {domain}, "
        
        if "novel" in goals.lower() or "alternative" in goals.lower():
            analysis += "you appear to be pursuing innovative theoretical work. "
            analysis += "Consider the paradigm implications and validation requirements."
        else:
            analysis += "you are building on established theoretical foundations. "
            analysis += "Focus on incremental advances and empirical validation."
        
        return analysis
    
    def _suggest_methodologies(self, domain: str, research_area: str, novel_theory: bool) -> List[str]:
        """Generate methodology suggestions"""
        base_methods = ["Literature Review", "Theoretical Analysis"]
        
        if domain == "theoretical_physics":
            base_methods.extend(["Mathematical Modeling", "Computational Validation"])
            if novel_theory:
                base_methods.append("Paradigm Comparison Analysis")
        
        return base_methods
    
    def _generate_next_steps(self, research_area: str, level: str, novel_theory: bool) -> List[str]:
        """Generate recommended next steps"""
        steps = [
            "Conduct comprehensive literature review",
            "Define specific research questions",
            "Develop theoretical framework"
        ]
        
        if novel_theory:
            steps.extend([
                "Identify challenged paradigms",
                "Develop alternative framework",
                "Plan validation strategy"
            ])
        
        return steps
    
    def _get_novel_theory_guidance(self) -> Dict[str, Any]:
        """Provide guidance for novel theory development"""
        return {
            "equal_treatment_principle": "Ensure your alternative theory receives the same rigorous development as mainstream approaches",
            "validation_requirements": [
                "Mathematical consistency",
                "Empirical testability", 
                "Predictive power",
                "Explanatory scope"
            ],
            "paradigm_challenge_framework": [
                "Identify specific limitations of current paradigms",
                "Propose clear alternative principles",
                "Demonstrate advantages of new framework",
                "Address potential objections"
            ]
        }
    
    def _filter_by_constraints(self, methodologies: List[Dict], constraints: Dict) -> List[Dict]:
        """Filter methodologies based on constraints"""
        # Simple filtering - in real implementation would be more sophisticated
        return methodologies  # For now, return all
    
    def _get_domain_considerations(self, domain: str) -> List[str]:
        """Get domain-specific considerations"""
        if domain == "theoretical_physics":
            return [
                "Ensure mathematical rigor",
                "Consider experimental testability",
                "Address foundational assumptions",
                "Validate against known phenomena"
            ]
        return ["Follow established research protocols", "Ensure reproducibility"]
    
    def _get_novel_theory_adaptations(self) -> List[str]:
        """Get adaptations for novel theory development"""
        return [
            "Apply equal treatment validation",
            "Include paradigm comparison analysis",
            "Address foundational assumption challenges",
            "Develop comprehensive alternative framework"
        ]
    
    def _get_validation_framework(self, domain: str, novel_theory: bool) -> Dict[str, Any]:
        """Get validation framework"""
        framework = {
            "standard_validation": [
                "Peer review simulation",
                "Methodology validation",
                "Result verification"
            ]
        }
        
        if novel_theory:
            framework["novel_theory_validation"] = [
                "Equal treatment scoring",
                "Paradigm comparison analysis",
                "Alternative framework assessment"
            ]
        
        return framework

# MCP tool registration
@context_aware()
async def clarify_research_goals(**kwargs) -> Dict[str, Any]:
    """MCP tool wrapper for research goal clarification"""
    # Filter out context parameters
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['project_path', 'config_path', 'config']}
    tool = ResearchPlanningTool()
    return await tool.clarify_research_goals(**filtered_kwargs)

@context_aware()
async def suggest_methodology(**kwargs) -> Dict[str, Any]:
    """MCP tool wrapper for methodology suggestion"""
    # Filter out context parameters
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['project_path', 'config_path', 'config']}
    tool = ResearchPlanningTool()
    return await tool.suggest_methodology(**filtered_kwargs)

def register_research_tools(server):
    """Register research planning tools with the MCP server"""
    
    server.register_tool(
        name="clarify_research_goals",
        description="Clarify research objectives through Socratic questioning",
        parameters={
            "type": "object",
            "properties": {
                "research_area": {"type": "string"},
                "initial_goals": {"type": "string"}, 
                "experience_level": {"type": "string"},
                "domain_specialization": {"type": "string"},
                "novel_theory_mode": {"type": "boolean"}
            },
            "required": ["research_area", "initial_goals"]
        },
        handler=clarify_research_goals
    )
    
    server.register_tool(
        name="suggest_methodology",
        description="Recommend appropriate research methodologies",
        parameters={
            "type": "object",
            "properties": {
                "research_goals": {"type": "string"},
                "domain": {"type": "string"},
                "constraints": {"type": "object"},
                "novel_theory_flag": {"type": "boolean"}
            },
            "required": ["research_goals", "domain"]
        },
        handler=suggest_methodology
    )
