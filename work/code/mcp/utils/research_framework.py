"""
Research Framework Service
Integrates frontend research act categorization with backend persistence
"""

from typing import Any, Dict, List, Optional


class ResearchFrameworkService:
    """Service for managing research act categorization and workflow intelligence"""

    def __init__(self):
        self.acts = {
            "conceptualization": {
                "name": "Conceptualization",
                "description": "Defining research problems, questions, and objectives",
                "icon": "🎯",
                "color": "#3b82f6",
                "categories": [
                    "goal_setting",
                    "problem_identification",
                    "critical_thinking",
                ],
            },
            "design_planning": {
                "name": "Design & Planning",
                "description": "Methodology selection and research design",
                "icon": "📋",
                "color": "#8b5cf6",
                "categories": [
                    "methodology",
                    "experimental_design",
                    "ethics_validation",
                ],
            },
            "knowledge_acquisition": {
                "name": "Knowledge Acquisition",
                "description": "Literature review and data gathering",
                "icon": "📚",
                "color": "#10b981",
                "categories": [
                    "literature_search",
                    "data_collection",
                    "source_management",
                ],
            },
            "analysis_synthesis": {
                "name": "Analysis & Synthesis",
                "description": "Data processing and interpretation",
                "icon": "🔬",
                "color": "#f59e0b",
                "categories": [
                    "data_analysis",
                    "pattern_recognition",
                    "semantic_analysis",
                    "knowledge_building",
                ],
            },
            "validation_refinement": {
                "name": "Validation & Refinement",
                "description": "Quality assurance and improvement",
                "icon": "✅",
                "color": "#ef4444",
                "categories": ["peer_review", "quality_control", "paradigm_validation"],
            },
            "communication": {
                "name": "Communication & Dissemination",
                "description": "Writing, formatting, and publishing",
                "icon": "📄",
                "color": "#06b6d4",
                "categories": [
                    "document_generation",
                    "formatting",
                    "project_management",
                    "workflow_tracking",
                ],
            },
        }

        self.categories = {
            # CONCEPTUALIZATION
            "goal_setting": {
                "name": "Goal Setting",
                "description": "Define and refine research objectives",
                "icon": "🎯",
                "act": "conceptualization",
                "tools": ["clarify_research_goals"],
            },
            "problem_identification": {
                "name": "Problem Identification",
                "description": "Identify and frame research problems",
                "icon": "❓",
                "act": "conceptualization",
                "tools": ["initiate_paradigm_challenge"],
            },
            "critical_thinking": {
                "name": "Critical Thinking",
                "description": "Question assumptions and generate critical questions",
                "icon": "🤔",
                "act": "conceptualization",
                "tools": [
                    "assess_foundational_assumptions",
                    "generate_critical_questions",
                ],
            },
            # DESIGN & PLANNING
            "methodology": {
                "name": "Methodology",
                "description": "Research method selection and design",
                "icon": "🔧",
                "act": "design_planning",
                "tools": [
                    "suggest_methodology",
                    "explain_methodology",
                    "compare_approaches",
                ],
            },
            "experimental_design": {
                "name": "Experimental Design",
                "description": "Design experiments and studies",
                "icon": "⚗️",
                "act": "design_planning",
                "tools": ["validate_design"],
            },
            "ethics_validation": {
                "name": "Ethics Validation",
                "description": "Ensure ethical research practices",
                "icon": "⚖️",
                "act": "design_planning",
                "tools": ["ensure_ethics"],
            },
            # KNOWLEDGE ACQUISITION
            "literature_search": {
                "name": "Literature Search",
                "description": "Find and organize research literature",
                "icon": "🔍",
                "act": "knowledge_acquisition",
                "tools": ["semantic_search"],
            },
            "data_collection": {
                "name": "Data Collection",
                "description": "Gather research data and sources",
                "icon": "📊",
                "act": "knowledge_acquisition",
                "tools": ["extract_key_concepts", "generate_research_summary"],
            },
            "source_management": {
                "name": "Source Management",
                "description": "Organize and manage references",
                "icon": "📚",
                "act": "knowledge_acquisition",
                "tools": [
                    "store_bibliography_reference",
                    "retrieve_bibliography_references",
                ],
            },
            # ANALYSIS & SYNTHESIS
            "data_analysis": {
                "name": "Data Analysis",
                "description": "Statistical and computational analysis",
                "icon": "📈",
                "act": "analysis_synthesis",
                "tools": ["discover_patterns", "extract_document_sections"],
            },
            "pattern_recognition": {
                "name": "Pattern Recognition",
                "description": "Identify patterns and relationships",
                "icon": "🧩",
                "act": "analysis_synthesis",
                "tools": ["find_similar_documents"],
            },
            "semantic_analysis": {
                "name": "Semantic Analysis",
                "description": "Meaning and concept analysis",
                "icon": "🧠",
                "act": "analysis_synthesis",
                "tools": ["build_knowledge_graph"],
            },
            "knowledge_building": {
                "name": "Knowledge Building",
                "description": "Synthesize information and build new knowledge",
                "icon": "🏗️",
                "act": "analysis_synthesis",
                "tools": ["develop_alternative_framework", "compare_paradigms"],
            },
            # VALIDATION & REFINEMENT
            "peer_review": {
                "name": "Peer Review",
                "description": "Quality assessment and feedback",
                "icon": "👥",
                "act": "validation_refinement",
                "tools": ["simulate_peer_review"],
            },
            "quality_control": {
                "name": "Quality Control",
                "description": "Ensure research quality and integrity",
                "icon": "🛡️",
                "act": "validation_refinement",
                "tools": ["check_quality_gates"],
            },
            "paradigm_validation": {
                "name": "Paradigm Validation",
                "description": "Validate novel theories and paradigm shifts",
                "icon": "🔄",
                "act": "validation_refinement",
                "tools": [
                    "validate_novel_theory",
                    "evaluate_paradigm_shift_potential",
                    "cultivate_innovation",
                ],
            },
            # COMMUNICATION
            "document_generation": {
                "name": "Document Generation",
                "description": "Create research documents",
                "icon": "📝",
                "act": "communication",
                "tools": [
                    "generate_latex_document",
                    "generate_document_with_database_bibliography",
                    "list_latex_templates",
                    "generate_latex_with_template",
                ],
            },
            "formatting": {
                "name": "Formatting",
                "description": "Format documents and citations",
                "icon": "✏️",
                "act": "communication",
                "tools": [
                    "compile_latex",
                    "format_research_content",
                    "generate_bibliography",
                ],
            },
            "project_management": {
                "name": "Project Management",
                "description": "Manage research projects and data",
                "icon": "📁",
                "act": "communication",
                "tools": [
                    "initialize_project",
                    "save_session",
                    "restore_session",
                    "search_knowledge",
                    "version_control",
                    "backup_project",
                ],
            },
            "workflow_tracking": {
                "name": "Workflow Tracking",
                "description": "Track research progress and workflow guidance",
                "icon": "🔄",
                "act": "communication",
                "tools": [
                    "get_research_progress",
                    "get_tool_usage_history",
                    "get_workflow_recommendations",
                    "get_research_milestones",
                    "start_research_session",
                    "get_session_summary",
                ],
            },
        }

        # Create reverse mapping: tool -> research context
        self.tool_mappings = {}
        for category_name, category_data in self.categories.items():
            for tool in category_data["tools"]:
                self.tool_mappings[tool] = {
                    "act": category_data["act"],
                    "category": category_name,
                    "category_name": category_data["name"],
                    "act_name": self.acts[category_data["act"]]["name"],
                }

    def get_tool_research_context(self, tool_name: str) -> Optional[Dict[str, str]]:
        """Get research act and category for a tool"""
        return self.tool_mappings.get(tool_name)

    def get_all_tools(self) -> List[str]:
        """Get list of all tools"""
        return list(self.tool_mappings.keys())

    def get_tools_by_act(self, research_act: str) -> List[str]:
        """Get all tools for a specific research act"""
        tools = []
        for tool, context in self.tool_mappings.items():
            if context["act"] == research_act:
                tools.append(tool)
        return tools

    def get_tools_by_category(self, category: str) -> List[str]:
        """Get all tools for a specific category"""
        if category in self.categories:
            return self.categories[category]["tools"]
        return []

    def get_act_categories(self, research_act: str) -> List[str]:
        """Get all categories for a research act"""
        if research_act in self.acts:
            return self.acts[research_act]["categories"]
        return []

    def calculate_act_completion(
        self, tools_used: List[str], research_act: str
    ) -> Dict[str, Any]:
        """Calculate completion percentage for a research act"""
        act_tools = self.get_tools_by_act(research_act)
        act_categories = self.get_act_categories(research_act)

        if not act_tools:
            return {
                "completion_percentage": 0,
                "categories_completed": 0,
                "tools_used": 0,
            }

        # Calculate tools used in this act
        tools_used_in_act = [tool for tool in tools_used if tool in act_tools]

        # Calculate categories with at least one tool used
        categories_with_tools = set()
        for tool in tools_used_in_act:
            context = self.get_tool_research_context(tool)
            if context and context["act"] == research_act:
                categories_with_tools.add(context["category"])

        # Calculate completion percentages
        tool_completion = (len(tools_used_in_act) / len(act_tools)) * 100
        category_completion = (len(categories_with_tools) / len(act_categories)) * 100

        # Weighted completion (60% categories, 40% tools)
        overall_completion = (category_completion * 0.6) + (tool_completion * 0.4)

        return {
            "completion_percentage": min(100, round(overall_completion, 1)),
            "categories_completed": len(categories_with_tools),
            "total_categories": len(act_categories),
            "tools_used": len(tools_used_in_act),
            "total_tools": len(act_tools),
            "categories_with_tools": list(categories_with_tools),
        }

    def calculate_category_completion(
        self, tools_used: List[str], category: str
    ) -> Dict[str, Any]:
        """Calculate completion percentage for a research category"""
        if category not in self.categories:
            return {"completion_percentage": 0, "tools_used": 0}

        category_tools = self.categories[category]["tools"]
        tools_used_in_category = [tool for tool in tools_used if tool in category_tools]

        completion_percentage = (
            len(tools_used_in_category) / len(category_tools)
        ) * 100

        return {
            "completion_percentage": min(100, round(completion_percentage, 1)),
            "tools_used": len(tools_used_in_category),
            "total_tools": len(category_tools),
            "tools_used_list": tools_used_in_category,
        }

    def recommend_next_tools(
        self, tools_used: List[str], current_act: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recommend next tools based on current research state"""
        recommendations = []

        # If no current act specified, determine from most recent tool usage
        if not current_act and tools_used:
            last_tool = tools_used[-1]
            context = self.get_tool_research_context(last_tool)
            if context:
                current_act = context["act"]

        # Get act order for progression
        act_order = [
            "conceptualization",
            "design_planning",
            "knowledge_acquisition",
            "analysis_synthesis",
            "validation_refinement",
            "communication",
        ]

        if current_act:
            # Recommend unused tools in current act
            current_act_tools = self.get_tools_by_act(current_act)
            unused_current_tools = [
                tool for tool in current_act_tools if tool not in tools_used
            ]

            for tool in unused_current_tools[:3]:  # Top 3 recommendations
                context = self.get_tool_research_context(tool)
                recommendations.append(
                    {
                        "tool": tool,
                        "priority": "high",
                        "reason": f'Complete {context["category_name"]} in current research act',
                        "research_act": current_act,
                        "category": context["category"],
                    }
                )

            # Recommend next act if current act seems complete
            current_completion = self.calculate_act_completion(tools_used, current_act)
            if current_completion["completion_percentage"] > 70:
                try:
                    current_index = act_order.index(current_act)
                    if current_index < len(act_order) - 1:
                        next_act = act_order[current_index + 1]
                        next_act_tools = self.get_tools_by_act(next_act)

                        for tool in next_act_tools[:2]:  # Top 2 from next act
                            context = self.get_tool_research_context(tool)
                            recommendations.append(
                                {
                                    "tool": tool,
                                    "priority": "medium",
                                    "reason": f'Begin {self.acts[next_act]["name"]} phase',
                                    "research_act": next_act,
                                    "category": context["category"],
                                }
                            )
                except ValueError:
                    pass

        else:
            # No current act, recommend starting with conceptualization
            conceptualization_tools = self.get_tools_by_act("conceptualization")
            for tool in conceptualization_tools[:3]:
                context = self.get_tool_research_context(tool)
                recommendations.append(
                    {
                        "tool": tool,
                        "priority": "high",
                        "reason": "Start research project with conceptualization",
                        "research_act": "conceptualization",
                        "category": context["category"],
                    }
                )

        return recommendations

    def detect_workflow_gaps(self, tools_used: List[str]) -> List[Dict[str, Any]]:
        """Identify missing steps in research workflow"""
        gaps = []

        # Check each research act for gaps
        for act_name, act_data in self.acts.items():
            completion = self.calculate_act_completion(tools_used, act_name)

            # Identify missing categories
            for category in act_data["categories"]:
                category_completion = self.calculate_category_completion(
                    tools_used, category
                )
                if category_completion["completion_percentage"] == 0:
                    gaps.append(
                        {
                            "type": "missing_category",
                            "research_act": act_name,
                            "category": category,
                            "category_name": self.categories[category]["name"],
                            "severity": (
                                "high"
                                if act_name in ["conceptualization", "design_planning"]
                                else "medium"
                            ),
                            "recommendation": f"Consider using tools from {self.categories[category]['name']} category",
                        }
                    )

        # Check for act sequence gaps
        act_order = [
            "conceptualization",
            "design_planning",
            "knowledge_acquisition",
            "analysis_synthesis",
            "validation_refinement",
            "communication",
        ]

        acts_with_tools = set()
        for tool in tools_used:
            context = self.get_tool_research_context(tool)
            if context:
                acts_with_tools.add(context["act"])

        # Find skipped acts
        for i, act in enumerate(act_order[:-1]):
            next_act = act_order[i + 1]
            if act not in acts_with_tools and next_act in acts_with_tools:
                gaps.append(
                    {
                        "type": "skipped_act",
                        "research_act": act,
                        "severity": "high",
                        "recommendation": f"Consider going back to {self.acts[act]['name']} before proceeding",
                    }
                )

        return gaps

    def generate_research_summary(self, tools_used: List[str]) -> Dict[str, Any]:
        """Generate comprehensive research progress summary"""
        summary = {
            "overall_progress": {},
            "acts_progress": {},
            "categories_progress": {},
            "recommendations": [],
            "gaps": [],
            "milestones": [],
        }

        # Calculate overall progress
        total_tools = len(self.get_all_tools())
        unique_tools_used = len(set(tools_used))
        summary["overall_progress"] = {
            "completion_percentage": (unique_tools_used / total_tools) * 100,
            "tools_used": unique_tools_used,
            "total_tools": total_tools,
        }

        # Calculate progress for each act
        for act_name in self.acts.keys():
            summary["acts_progress"][act_name] = self.calculate_act_completion(
                tools_used, act_name
            )

        # Calculate progress for each category
        for category_name in self.categories.keys():
            summary["categories_progress"][category_name] = (
                self.calculate_category_completion(tools_used, category_name)
            )

        # Generate recommendations
        summary["recommendations"] = self.recommend_next_tools(tools_used)

        # Detect gaps
        summary["gaps"] = self.detect_workflow_gaps(tools_used)

        # Identify milestones
        for act_name, act_progress in summary["acts_progress"].items():
            if act_progress["completion_percentage"] >= 100:
                summary["milestones"].append(
                    {
                        "type": "act_completed",
                        "name": f"{self.acts[act_name]['name']} Completed",
                        "research_act": act_name,
                        "impact_score": 5,
                    }
                )
            elif act_progress["completion_percentage"] >= 50:
                summary["milestones"].append(
                    {
                        "type": "act_halfway",
                        "name": f"{self.acts[act_name]['name']} 50% Complete",
                        "research_act": act_name,
                        "impact_score": 3,
                    }
                )

        return summary
