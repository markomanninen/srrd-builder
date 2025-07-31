"""
Research Planning MCP Tool
Provides Socratic questioning and methodology guidance for research planning
"""

# Import context-aware decorator
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
                    "How does your approach differ from current mainstream theories?",
                ],
                "assumption": [
                    "What fundamental assumptions underlie your theoretical framework?",
                    "Which of these assumptions have been experimentally validated?",
                    "Are there alternative assumptions that could lead to different conclusions?",
                ],
                "evidence": [
                    "What mathematical formalism supports your theoretical predictions?",
                    "What experimental evidence would validate your theory?",
                    "How does your theory explain existing experimental observations?",
                ],
                "paradigm_innovation": [
                    "How does your theory challenge existing paradigms in physics?",
                    "What foundational principles of current physics does your work question?",
                    "What would be the implications if your alternative framework is correct?",
                ],
                "validation": [
                    "What testable predictions does your theory make?",
                    "How would you distinguish your theory from existing alternatives?",
                    "What would constitute compelling evidence for your theoretical framework?",
                ],
            },
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
                ],
                "methodology": [
                    "What development methodology will you follow?",
                    "How will you ensure code quality and maintainability?",
                    "What testing strategies will you employ?",
                ],
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
                ],
                "validation": [
                    "How will you validate your biological findings?",
                    "What statistical methods will you use for data analysis?",
                    "How will you address potential confounding variables?",
                ],
                "assumption": [
                    "What biological assumptions underlie your experimental design?",
                    "How do environmental factors affect your system?",
                    "What limitations exist in your experimental model?",
                ],
            },
            "psychology": {
                "clarification": [
                    "What psychological phenomenon are you investigating?",
                    "What theoretical framework guides your research?",
                    "How does your study contribute to psychological understanding?",
                ],
                "methodology": [
                    "What research design will you use (experimental, correlational, longitudinal)?",
                    "How will you address ethical considerations in human research?",
                    "What measures will you use to assess psychological constructs?",
                ],
                "assumption": [
                    "What assumptions about human behavior guide your research?",
                    "How do cultural factors influence your research design?",
                    "What biases might affect your data collection or interpretation?",
                ],
                "validation": [
                    "How will you ensure the validity and reliability of your measures?",
                    "What statistical analyses will you use?",
                    "How will you address alternative explanations for your findings?",
                ],
            },
            "general": {
                "clarification": [
                    "What is the core research question you're trying to answer?",
                    "Why is this research important to your field?",
                    "What gap in current knowledge does this address?",
                ],
                "assumption": [
                    "What assumptions are you making about your research approach?",
                    "What background knowledge are you taking for granted?",
                    "How might these assumptions limit your conclusions?",
                ],
                "evidence": [
                    "What evidence supports your research hypothesis?",
                    "What methods will you use to gather evidence?",
                    "How will you know if your hypothesis is wrong?",
                ],
                "validation": [
                    "How will you validate your research findings?",
                    "What quality controls will you implement?",
                    "How will you ensure your results are reproducible?",
                ],
            },
        }

    async def enhanced_socratic_dialogue(
        self,
        research_context: str,
        user_response: str = None,
        dialogue_depth: int = 1,
        focus_area: str = "clarification",
        domain_specialization: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Enhanced tool: Progressive Socratic dialogue with depth control
        
        Builds on existing clarify_research_goals but adds progressive questioning
        """
        question_bank = self.socratic_questions.get(domain_specialization, self.socratic_questions["general"])
        
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
                response_analysis, domain_specialization, dialogue_depth
            )
        
        return {
            "progressive_questions": questions,
            "contextual_followups": contextual_questions,
            "response_analysis": response_analysis,
            "dialogue_depth": dialogue_depth,
            "suggested_next_depth": min(dialogue_depth + 1, 3),
            "research_context": research_context,
            "focus_area": focus_area,
            "domain": domain_specialization,
            "user_interaction_required": f"Please respond to these {focus_area} questions. I'll provide deeper questions based on your answers.",
            "next_step_options": [
                f"Answer the {focus_area} questions to proceed to deeper inquiry",
                "Ask me to focus on a specific aspect that interests you most",
                "Request methodology suggestions based on your responses"
            ]
        }

    def _analyze_user_response(self, response: str, focus_area: str) -> Dict[str, Any]:
        """Analyze user response for sophistication and content patterns"""
        words = response.split()
        analysis = {
            "response_length": len(words),
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
        if analysis["technical_terms"] < 2 and len(words) > 10:
            analysis["follow_up_needed"].append("More technical detail would be helpful")
            
        return analysis

    def _count_technical_terms(self, text: str) -> int:
        """Count technical terms in user response"""
        technical_indicators = [
            'algorithm', 'method', 'approach', 'framework', 'model', 'theory',
            'hypothesis', 'analysis', 'research', 'study', 'experiment', 'data',
            'statistical', 'computational', 'mathematical', 'empirical', 'validation',
            'methodology', 'paradigm', 'theoretical', 'experimental', 'quantitative',
            # Computer science terms
            'cryptographic', 'quantum', 'lattice', 'neural', 'network', 'machine',
            'learning', 'artificial', 'intelligence', 'optimization', 'security',
            # Biology/science terms
            'molecular', 'cellular', 'enzyme', 'protein', 'genetic', 'biochemical',
            'biological', 'microscopy', 'fluorescence', 'kinetics', 'systematic',
            # Physics terms
            'electromagnetic', 'particle', 'wave', 'relativity', 'mechanics',
            # General academic terms
            'systematic', 'rigorous', 'sophisticated', 'comprehensive', 'innovative'
        ]
        
        text_lower = text.lower()
        count = sum(1 for term in technical_indicators if term in text_lower)
        return count

    def _detect_uncertainty(self, text: str) -> int:
        """Detect uncertainty indicators in user response"""
        uncertainty_words = [
            'maybe', 'perhaps', 'possibly', 'might', 'could', 'uncertain',
            'unclear', 'not sure', 'think', 'believe', 'probably', 'likely'
        ]
        
        text_lower = text.lower()
        count = sum(1 for word in uncertainty_words if word in text_lower)
        return count

    def _assess_specificity(self, text: str) -> float:
        """Assess specificity level of user response (0.0 to 1.0)"""
        specific_indicators = [
            'specific', 'exactly', 'precisely', 'particular', 'detailed',
            'measure', 'quantify', 'calculate', 'implement', 'design', 'developing',
            'using', 'algorithm', 'method', 'technique', 'approach'
        ]
        
        general_indicators = [
            'general', 'overall', 'broadly', 'basically', 'simply',
            'just', 'kind of', 'sort of', 'something', 'things'
        ]
        
        # Technical specificity indicators (specific algorithms, methods, etc.)
        technical_specificity = [
            'lattice-based', 'post-quantum', 'cryptographic', 'neural network',
            'machine learning', 'deep learning', 'reinforcement learning',
            'quantum computing', 'blockchain', 'neural networks', 'regression',
            'classification', 'clustering', 'optimization', 'gradient descent',
            'backpropagation', 'convolutional', 'recurrent', 'transformer'
        ]
        
        text_lower = text.lower()
        specific_count = sum(1 for indicator in specific_indicators if indicator in text_lower)
        general_count = sum(1 for indicator in general_indicators if indicator in text_lower)
        technical_spec_count = sum(1 for tech in technical_specificity if tech in text_lower)
        
        # Get technical terms count for additional specificity
        technical_terms = self._count_technical_terms(text)
        
        # Enhanced scoring considering multiple factors
        words_count = len(text.split())
        if words_count == 0:
            return 0.0
        
        # Base score from specific vs general indicators
        base_score = (specific_count * 2 - general_count) / max(words_count / 10, 1)
        
        # Bonus for technical specificity
        tech_bonus = (technical_spec_count * 0.3) + (technical_terms * 0.1)
        
        # Bonus for longer, more detailed responses
        length_bonus = min(0.2, words_count / 100)
        
        final_score = 0.5 + (base_score * 0.3) + tech_bonus + length_bonus
        return max(0.0, min(1.0, final_score))

    def _generate_contextual_followups(self, analysis: Dict, domain: str, depth: int) -> List[str]:
        """Generate contextual follow-up questions based on user response analysis"""
        followups = []
        
        if "More specific details needed" in analysis["follow_up_needed"]:
            followups.append("Can you provide more specific details about your approach?")
        
        if analysis["technical_terms"] < 2 and depth > 1:
            followups.append("What technical methods or tools are you considering?")
        
        if "Clarification of uncertain points" in analysis["follow_up_needed"]:
            followups.append("Which aspects are you most uncertain about? Let's explore those together.")
        
        if domain == "computer_science" and analysis["specificity_level"] < 0.4:
            followups.append("What specific algorithms or data structures are relevant to your problem?")
        
        if domain == "biology" and "methodology" not in analysis:
            followups.append("What experimental techniques are you planning to use?")
            
        return followups

    async def clarify_research_goals(
        self,
        research_area: str,
        initial_goals: str,
        experience_level: str = "intermediate",
        domain_specialization: str = "general",
        novel_theory_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        MCP tool: Clarify research objectives through Socratic questioning
        """

        # Select appropriate question bank
        question_bank = self.socratic_questions.get(
            domain_specialization, self.socratic_questions["general"]
        )

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
        methodology_suggestions = self._suggest_methodologies(
            domain_specialization, research_area, novel_theory_mode
        )

        # Generate next steps
        next_steps = self._generate_next_steps(
            research_area, experience_level, novel_theory_mode
        )

        return {
            "clarified_goals": self._analyze_goals(
                initial_goals, domain_specialization
            ),
            "follow_up_questions": questions,
            "methodology_suggestions": methodology_suggestions,
            "novel_theory_guidance": (
                self._get_novel_theory_guidance() if novel_theory_mode else None
            ),
            "user_interaction_required": "Please review these clarified goals and questions. Which specific aspect would you like to explore further? You can use suggest_methodology to get detailed methodology recommendations, or ask me to clarify any of these points.",
            "next_step_options": [
                "Use 'suggest_methodology' if you want detailed research methodology recommendations",
                "Use 'generate_critical_questions' if you want more focused critical thinking questions",
                "Tell me which follow-up questions most interest you and I'll help you explore them",
            ],
        }

    async def suggest_methodology(
        self,
        research_goals: str,
        domain: str,
        constraints: Optional[Dict[str, Any]] = None,
        novel_theory_flag: bool = False,
    ) -> Dict[str, Any]:
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
                    "resources_needed": ["Mathematical software", "Literature access"],
                },
                {
                    "name": "Computational Simulation",
                    "description": "Numerical validation of theoretical predictions",
                    "suitability": "Medium to High",
                    "time_requirement": "3-9 months",
                    "resources_needed": ["Computing resources", "Programming skills"],
                },
            ]

            if novel_theory_flag:
                methodologies.append(
                    {
                        "name": "Paradigm Comparison Analysis",
                        "description": "Systematic comparison with existing theoretical frameworks",
                        "suitability": "Essential for novel theories",
                        "time_requirement": "4-8 months",
                        "resources_needed": [
                            "Comprehensive literature review",
                            "Analytical framework",
                        ],
                    }
                )

        else:  # General methodologies
            methodologies = [
                {
                    "name": "Literature Review",
                    "description": "Systematic analysis of existing research",
                    "suitability": "Essential for all research",
                    "time_requirement": "2-4 months",
                    "resources_needed": ["Database access", "Reference management"],
                },
                {
                    "name": "Experimental Design",
                    "description": "Design controlled experiments to test hypotheses",
                    "suitability": "High for empirical research",
                    "time_requirement": "3-6 months",
                    "resources_needed": ["Lab access", "Equipment", "Participants"],
                },
            ]

        # Filter based on constraints
        if constraints:
            methodologies = self._filter_by_constraints(methodologies, constraints)

        return {
            "recommended_methodologies": methodologies,
            "domain_specific_considerations": self._get_domain_considerations(domain),
            "novel_theory_adaptations": (
                self._get_novel_theory_adaptations() if novel_theory_flag else None
            ),
            "validation_framework": self._get_validation_framework(
                domain, novel_theory_flag
            ),
            "user_interaction_required": "Please review these methodology recommendations. Which methodology most interests you or fits your constraints? I can provide more detailed guidance on any specific approach.",
            "next_step_options": [
                "Ask me to elaborate on any specific methodology that interests you",
                "Use 'explain_methodology' for detailed explanation of a particular approach",
                "Tell me about your specific constraints and I'll help refine these recommendations",
            ],
        }

    def _analyze_goals(self, goals: str, domain: str) -> str:
        """Analyze and refine research goals"""
        # Simple analysis - in real implementation, would use AI
        analysis = f"Based on your stated goals in {domain}, "

        if "novel" in goals.lower() or "alternative" in goals.lower():
            analysis += "you appear to be pursuing innovative theoretical work. "
            analysis += (
                "Consider the paradigm implications and validation requirements."
            )
        else:
            analysis += "you are building on established theoretical foundations. "
            analysis += "Focus on incremental advances and empirical validation."

        return analysis

    def _suggest_methodologies(
        self, domain: str, research_area: str, novel_theory: bool
    ) -> List[str]:
        """Generate methodology suggestions"""
        base_methods = ["Literature Review", "Theoretical Analysis"]

        if domain == "theoretical_physics":
            base_methods.extend(["Mathematical Modeling", "Computational Validation"])
            if novel_theory:
                base_methods.append("Paradigm Comparison Analysis")

        return base_methods

    def _generate_next_steps(
        self, research_area: str, level: str, novel_theory: bool
    ) -> List[str]:
        """Generate recommended next steps"""
        steps = [
            "Conduct comprehensive literature review",
            "Define specific research questions",
            "Develop theoretical framework",
        ]

        if novel_theory:
            steps.extend(
                [
                    "Identify challenged paradigms",
                    "Develop alternative framework",
                    "Plan validation strategy",
                ]
            )

        return steps

    def _get_novel_theory_guidance(self) -> Dict[str, Any]:
        """Provide guidance for novel theory development"""
        return {
            "equal_treatment_principle": "Ensure your alternative theory receives the same rigorous development as mainstream approaches",
            "validation_requirements": [
                "Mathematical consistency",
                "Empirical testability",
                "Predictive power",
                "Explanatory scope",
            ],
            "paradigm_challenge_framework": [
                "Identify specific limitations of current paradigms",
                "Propose clear alternative principles",
                "Demonstrate advantages of new framework",
                "Address potential objections",
            ],
        }

    def _filter_by_constraints(
        self, methodologies: List[Dict], constraints: Dict
    ) -> List[Dict]:
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
                "Validate against known phenomena",
            ]
        return ["Follow established research protocols", "Ensure reproducibility"]

    def _get_novel_theory_adaptations(self) -> List[str]:
        """Get adaptations for novel theory development"""
        return [
            "Apply equal treatment validation",
            "Include paradigm comparison analysis",
            "Address foundational assumption challenges",
            "Develop comprehensive alternative framework",
        ]

    def _get_validation_framework(
        self, domain: str, novel_theory: bool
    ) -> Dict[str, Any]:
        """Get validation framework"""
        framework = {
            "standard_validation": [
                "Peer review simulation",
                "Methodology validation",
                "Result verification",
            ]
        }

        if novel_theory:
            framework["novel_theory_validation"] = [
                "Equal treatment scoring",
                "Paradigm comparison analysis",
                "Alternative framework assessment",
            ]

        return framework


# MCP tool registration
@context_aware(require_context=True)
async def clarify_research_goals(**kwargs) -> Dict[str, Any]:
    """MCP tool wrapper for research goal clarification"""
    # Filter out context parameters
    filtered_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["project_path", "config_path", "config"]
    }
    tool = ResearchPlanningTool()
    return await tool.clarify_research_goals(**filtered_kwargs)


@context_aware(require_context=True)
async def suggest_methodology(**kwargs) -> Dict[str, Any]:
    """MCP tool wrapper for methodology suggestion"""
    # Filter out context parameters
    filtered_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["project_path", "config_path", "config"]
    }
    tool = ResearchPlanningTool()
    return await tool.suggest_methodology(**filtered_kwargs)


@context_aware(require_context=True)
async def enhanced_socratic_dialogue(**kwargs) -> Dict[str, Any]:
    """MCP tool wrapper for enhanced Socratic dialogue"""
    # Filter out context parameters
    filtered_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["project_path", "config_path", "config"]
    }
    tool = ResearchPlanningTool()
    return await tool.enhanced_socratic_dialogue(**filtered_kwargs)


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
                "novel_theory_mode": {"type": "boolean"},
            },
            "required": ["research_area", "initial_goals"],
        },
        handler=clarify_research_goals,
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
                "novel_theory_flag": {"type": "boolean"},
            },
            "required": ["research_goals", "domain"],
        },
        handler=suggest_methodology,
    )

    server.register_tool(
        name="enhanced_socratic_dialogue",
        description="Progressive Socratic dialogue with depth control and response analysis",
        parameters={
            "type": "object",
            "properties": {
                "research_context": {"type": "string"},
                "user_response": {"type": "string"},
                "dialogue_depth": {"type": "integer"},
                "focus_area": {"type": "string"},
                "domain_specialization": {"type": "string"},
            },
            "required": ["research_context"],
        },
        handler=enhanced_socratic_dialogue,
    )
