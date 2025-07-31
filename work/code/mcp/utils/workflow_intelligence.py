"""
Workflow Intelligence Service
AI-powered workflow guidance and research progression analysis
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List


class WorkflowIntelligence:
    """Service for AI-powered workflow guidance and research progression analysis"""

    def __init__(self, sqlite_manager, research_framework):
        self.sqlite_manager = sqlite_manager
        self.research_framework = research_framework

    async def analyze_research_progress(self, project_id: int) -> Dict[str, Any]:
        """Analyze current research progress and identify next steps"""

        # Get tools used in project
        tools_used = await self.sqlite_manager.get_tools_used_in_project(project_id)

        # Get research framework summary
        framework_summary = self.research_framework.generate_research_summary(
            tools_used
        )

        # Get database progress data
        db_summary = await self.sqlite_manager.get_research_progress_summary(project_id)

        # Get research act statistics
        act_stats = await self.sqlite_manager.get_research_act_statistics(project_id)

        # Combine analysis
        analysis = {
            "project_id": project_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_progress": framework_summary["overall_progress"],
            "research_acts": framework_summary["acts_progress"],
            "categories": framework_summary["categories_progress"],
            "tool_usage_stats": act_stats,
            "research_velocity": await self._calculate_research_velocity(project_id),
            "workflow_health": await self._assess_workflow_health(
                project_id, tools_used
            ),
            "next_steps": framework_summary["recommendations"],
            "workflow_gaps": framework_summary["gaps"],
            "milestones": framework_summary["milestones"],
        }

        return analysis

    async def generate_recommendations(
        self, project_id: int, session_id: int
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered workflow recommendations"""

        # Get current state
        tools_used = await self.sqlite_manager.get_tools_used_in_project(project_id)

        # Get framework recommendations
        framework_recs = self.research_framework.recommend_next_tools(tools_used)

        # Enhance with context-aware intelligence
        enhanced_recommendations = []

        for rec in framework_recs:
            enhanced_rec = await self._enhance_recommendation(
                project_id, rec, tools_used
            )
            enhanced_recommendations.append(enhanced_rec)

            # Store recommendation in database
            await self.sqlite_manager.create_workflow_recommendation(
                project_id=project_id,
                session_id=session_id,
                current_research_act=rec["research_act"],
                recommended_next_act=rec.get("next_act"),
                recommended_tools=[rec["tool"]],
                reasoning=enhanced_rec["enhanced_reasoning"],
                priority=(
                    1
                    if rec["priority"] == "high"
                    else 2 if rec["priority"] == "medium" else 3
                ),
            )

        return enhanced_recommendations

    async def detect_milestones(self, project_id: int) -> List[Dict[str, Any]]:
        """Detect achieved milestones and suggest new targets"""

        tools_used = await self.sqlite_manager.get_tools_used_in_project(project_id)
        milestones = []

        # Check for research act completion milestones
        for act_name in self.research_framework.acts.keys():
            completion = self.research_framework.calculate_act_completion(
                tools_used, act_name
            )

            if completion["completion_percentage"] >= 100:
                milestone = {
                    "type": "research_act_completed",
                    "name": f"{self.research_framework.acts[act_name]['name']} Completed",
                    "description": f"Successfully completed all categories in {act_name}",
                    "research_act": act_name,
                    "completion_criteria": completion,
                    "tools_involved": await self._get_tools_for_act(
                        project_id, act_name
                    ),
                    "impact_score": 5,
                    "achieved_at": datetime.now().isoformat(),
                }

                # Record in database
                await self.sqlite_manager.record_research_milestone(
                    project_id=project_id,
                    milestone_type=milestone["type"],
                    milestone_name=milestone["name"],
                    description=milestone["description"],
                    research_act=act_name,
                    completion_criteria=completion,
                    tools_involved=milestone["tools_involved"],
                    impact_score=5,
                )

                milestones.append(milestone)

            elif completion["completion_percentage"] >= 75:
                milestone = {
                    "type": "research_act_advanced",
                    "name": f"{self.research_framework.acts[act_name]['name']} Nearly Complete",
                    "description": f"Advanced progress in {act_name} (75%+ complete)",
                    "research_act": act_name,
                    "completion_criteria": completion,
                    "tools_involved": await self._get_tools_for_act(
                        project_id, act_name
                    ),
                    "impact_score": 4,
                    "achieved_at": datetime.now().isoformat(),
                }
                milestones.append(milestone)

            elif completion["completion_percentage"] >= 50:
                milestone = {
                    "type": "research_act_halfway",
                    "name": f"{self.research_framework.acts[act_name]['name']} 50% Complete",
                    "description": f"Halfway through {act_name} research phase",
                    "research_act": act_name,
                    "completion_criteria": completion,
                    "tools_involved": await self._get_tools_for_act(
                        project_id, act_name
                    ),
                    "impact_score": 3,
                    "achieved_at": datetime.now().isoformat(),
                }
                milestones.append(milestone)

            elif completion["completion_percentage"] >= 25:
                milestone = {
                    "type": "research_act_started",
                    "name": f"{self.research_framework.acts[act_name]['name']} Started",
                    "description": f"Began working on {act_name} phase",
                    "research_act": act_name,
                    "completion_criteria": completion,
                    "tools_involved": await self._get_tools_for_act(
                        project_id, act_name
                    ),
                    "impact_score": 2,
                    "achieved_at": datetime.now().isoformat(),
                }
                milestones.append(milestone)

        # Check for special achievement milestones
        total_tools_used = len(set(tools_used))
        if total_tools_used >= 20:
            milestone = {
                "type": "tool_mastery",
                "name": "Research Tool Master",
                "description": f"Used {total_tools_used} different research tools",
                "impact_score": 4,
                "achieved_at": datetime.now().isoformat(),
            }
            milestones.append(milestone)
        elif total_tools_used >= 15:
            milestone = {
                "type": "tool_explorer",
                "name": "Research Tool Explorer",
                "description": f"Explored {total_tools_used} different research tools",
                "impact_score": 3,
                "achieved_at": datetime.now().isoformat(),
            }
            milestones.append(milestone)
        elif total_tools_used >= 10:
            milestone = {
                "type": "tool_practitioner",
                "name": "Research Tool Practitioner",
                "description": f"Practiced with {total_tools_used} different research tools",
                "impact_score": 2,
                "achieved_at": datetime.now().isoformat(),
            }
            milestones.append(milestone)

        # Check for workflow breadth milestone
        acts_touched = len(
            set(
                self.research_framework.get_tool_research_context(tool)["act"]
                for tool in tools_used
                if self.research_framework.get_tool_research_context(tool)
            )
        )

        if acts_touched >= 6:
            milestone = {
                "type": "complete_workflow",
                "name": "Complete Research Workflow",
                "description": "Touched all 6 research acts in the lifecycle",
                "impact_score": 5,
                "achieved_at": datetime.now().isoformat(),
            }
            milestones.append(milestone)
        elif acts_touched >= 4:
            milestone = {
                "type": "broad_workflow",
                "name": "Broad Research Workflow",
                "description": f"Worked across {acts_touched} different research acts",
                "impact_score": 3,
                "achieved_at": datetime.now().isoformat(),
            }
            milestones.append(milestone)

        return milestones

    async def calculate_research_velocity(self, project_id: int) -> Dict[str, Any]:
        """Calculate research progress velocity and predict completion"""

        # Get tool usage over time
        tool_usage_data = await self.sqlite_manager.get_research_progress_summary(
            project_id
        )
        tool_usage = tool_usage_data["tool_usage"]

        if not tool_usage:
            return {
                "tools_per_day": 0,
                "estimated_completion_days": None,
                "velocity_trend": "no_data",
            }

        # Calculate tools per day
        first_usage = min(tool_usage, key=lambda x: x[10])  # timestamp column
        last_usage = max(tool_usage, key=lambda x: x[10])

        first_date = datetime.fromisoformat(first_usage[10].replace("Z", "+00:00"))
        last_date = datetime.fromisoformat(last_usage[10].replace("Z", "+00:00"))

        days_active = (last_date - first_date).days + 1
        tools_per_day = len(tool_usage) / days_active if days_active > 0 else 0

        # Calculate remaining tools needed
        all_tools = self.research_framework.get_all_tools()
        tools_used = set(usage[2] for usage in tool_usage)  # tool_name column
        remaining_tools = len(all_tools) - len(tools_used)

        # Estimate completion
        estimated_days = remaining_tools / tools_per_day if tools_per_day > 0 else None

        # Analyze velocity trend (last 7 days vs previous 7 days)
        recent_cutoff = datetime.now() - timedelta(days=7)
        previous_cutoff = datetime.now() - timedelta(days=14)

        recent_usage = [
            u
            for u in tool_usage
            if datetime.fromisoformat(u[10].replace("Z", "+00:00")) >= recent_cutoff
        ]
        previous_usage = [
            u
            for u in tool_usage
            if previous_cutoff
            <= datetime.fromisoformat(u[10].replace("Z", "+00:00"))
            < recent_cutoff
        ]

        velocity_trend = "stable"
        if len(recent_usage) > len(previous_usage) * 1.2:
            velocity_trend = "accelerating"
        elif len(recent_usage) < len(previous_usage) * 0.8:
            velocity_trend = "decelerating"

        return {
            "tools_per_day": round(tools_per_day, 2),
            "total_tools_used": len(tools_used),
            "remaining_tools": remaining_tools,
            "estimated_completion_days": (
                round(estimated_days) if estimated_days else None
            ),
            "velocity_trend": velocity_trend,
            "recent_activity": len(recent_usage),
            "days_active": days_active,
        }

    async def _calculate_research_velocity(self, project_id: int) -> Dict[str, Any]:
        """Internal method to calculate research velocity"""
        return await self.calculate_research_velocity(project_id)

    async def _assess_workflow_health(
        self, project_id: int, tools_used: List[str]
    ) -> Dict[str, Any]:
        """Assess overall workflow health"""

        # Detect workflow gaps
        gaps = self.research_framework.detect_workflow_gaps(tools_used)

        # Calculate balance across research acts
        act_usage = {}
        for tool in tools_used:
            context = self.research_framework.get_tool_research_context(tool)
            if context:
                act = context["act"]
                act_usage[act] = act_usage.get(act, 0) + 1

        # Calculate balance score (0-100)
        if not act_usage:
            balance_score = 0
        else:
            total_usage = sum(act_usage.values())
            expected_per_act = total_usage / 6  # 6 research acts
            variance = (
                sum((count - expected_per_act) ** 2 for count in act_usage.values()) / 6
            )
            balance_score = max(0, 100 - (variance / expected_per_act * 100))

        # Assess health
        health_score = 100
        health_issues = []

        # Deduct for gaps
        high_severity_gaps = len([g for g in gaps if g.get("severity") == "high"])
        medium_severity_gaps = len([g for g in gaps if g.get("severity") == "medium"])
        health_score -= (high_severity_gaps * 20) + (medium_severity_gaps * 10)

        if high_severity_gaps > 0:
            health_issues.append(f"{high_severity_gaps} high-severity workflow gaps")
        if medium_severity_gaps > 0:
            health_issues.append(
                f"{medium_severity_gaps} medium-severity workflow gaps"
            )

        # Deduct for poor balance
        if balance_score < 50:
            health_score -= 20
            health_issues.append("Unbalanced research act usage")

        # Determine overall health status
        if health_score >= 80:
            health_status = "excellent"
        elif health_score >= 60:
            health_status = "good"
        elif health_score >= 40:
            health_status = "fair"
        else:
            health_status = "poor"

        return {
            "health_score": max(0, health_score),
            "health_status": health_status,
            "balance_score": round(balance_score, 1),
            "issues": health_issues,
            "gaps_count": len(gaps),
            "act_usage_distribution": act_usage,
        }

    async def _enhance_recommendation(
        self, project_id: int, recommendation: Dict[str, Any], tools_used: List[str]
    ) -> Dict[str, Any]:
        """Enhance a recommendation with additional context"""

        # Get project context
        velocity = await self.calculate_research_velocity(project_id)

        # Add context-aware reasoning
        enhanced_reasoning = recommendation["reason"]

        # Add velocity context
        if velocity["velocity_trend"] == "decelerating":
            enhanced_reasoning += (
                ". Consider focusing on this tool to maintain research momentum."
            )
        elif velocity["velocity_trend"] == "accelerating":
            enhanced_reasoning += ". Your research velocity is strong - this tool fits well with your current pace."

        # Add prerequisite checking
        tool_context = self.research_framework.get_tool_research_context(
            recommendation["tool"]
        )
        if tool_context:
            act = tool_context["act"]
            act_completion = self.research_framework.calculate_act_completion(
                tools_used, act
            )

            if act_completion["completion_percentage"] < 25:
                enhanced_reasoning += (
                    f" This is an early step in {tool_context['act_name']}."
                )
            elif act_completion["completion_percentage"] > 75:
                enhanced_reasoning += (
                    f" This will help complete the {tool_context['act_name']} phase."
                )

        # Add estimated effort
        effort_estimate = "low"  # Could be enhanced with ML model
        if recommendation["tool"] in [
            "generate_latex_document",
            "simulate_peer_review",
            "build_knowledge_graph",
        ]:
            effort_estimate = "high"
        elif recommendation["tool"] in [
            "clarify_research_goals",
            "suggest_methodology",
        ]:
            effort_estimate = "medium"

        enhanced_rec = recommendation.copy()
        enhanced_rec.update(
            {
                "enhanced_reasoning": enhanced_reasoning,
                "effort_estimate": effort_estimate,
                "context": {
                    "project_velocity": velocity["velocity_trend"],
                    "act_completion": act_completion if tool_context else None,
                },
            }
        )

        return enhanced_rec

    async def _get_tools_for_act(self, project_id: int, research_act: str) -> List[str]:
        """Get tools used for a specific research act in a project"""

        tool_usage_data = await self.sqlite_manager.get_research_progress_summary(
            project_id
        )
        tool_usage = tool_usage_data["tool_usage"]

        # Filter tools by research act
        act_tools = []
        for usage in tool_usage:
            if usage[3] == research_act:  # research_act column
                act_tools.append(usage[2])  # tool_name column

        return list(set(act_tools))  # Remove duplicates

    async def generate_session_summary(self, session_id: int) -> Dict[str, Any]:
        """Generate comprehensive summary of a research session"""

        # Get tool usage for session
        tool_usage = await self.sqlite_manager.get_tool_usage_history(session_id)

        if not tool_usage:
            return {
                "session_id": session_id,
                "summary": "No tools used in this session",
                "tools_used": [],
                "research_acts_involved": [],
                "duration_minutes": 0.0,
                "total_tool_calls": 0,
                "successful_calls": 0,
                "avg_execution_time_ms": 0.0,
                "start_time": None,
                "end_time": None,
            }

        # Calculate session metrics
        start_time = datetime.fromisoformat(tool_usage[0]["timestamp"])
        end_time = datetime.fromisoformat(tool_usage[-1]["timestamp"])
        duration_minutes = (end_time - start_time).total_seconds() / 60

        # Analyze research acts and categories
        acts_involved = set()
        categories_involved = set()
        tools_used_list = []

        for usage in tool_usage:
            acts_involved.add(usage["research_act"])
            categories_involved.add(usage["research_category"])
            tools_used_list.append(usage["tool_name"])

        # Calculate productivity metrics
        successful_tools = [u for u in tool_usage if u["success"]]
        avg_execution_time = (
            sum(
                u["execution_time_ms"]
                for u in successful_tools
                if u["execution_time_ms"]
            )
            / len(successful_tools)
            if successful_tools
            else 0
        )

        return {
            "session_id": session_id,
            "summary": f"Used {len(set(tools_used_list))} unique tools across {len(acts_involved)} research acts",
            "tools_used": list(set(tools_used_list)),
            "research_acts_involved": list(acts_involved),
            "categories_involved": list(categories_involved),
            "duration_minutes": round(duration_minutes, 1),
            "total_tool_calls": len(tool_usage),
            "successful_calls": len(successful_tools),
            "avg_execution_time_ms": round(avg_execution_time, 1),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

    async def get_contextual_recommendations(
        self, 
        project_id: int,
        last_tool_used: str = None,
        user_context: Dict[str, Any] = None,
        recommendation_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Enhanced contextual recommendations building on existing functionality
        """
        # Get existing analysis as foundation
        current_context = await self.analyze_research_progress(project_id)
        
        # Enhance with tool sequence analysis
        recent_tools = await self._get_recent_tool_sequence(project_id, limit=5)
        tool_patterns = self._analyze_tool_patterns(recent_tools)
        
        # Generate enhanced recommendations
        recommendations = await self._generate_enhanced_recommendations(
            project_id,
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
            "alternative_paths": await self._get_alternative_approaches(project_id, recommendations)
        }
    
    async def _get_recent_tool_sequence(self, project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent tool usage sequence from existing database"""
        query = """
            SELECT tu.tool_name, tu.timestamp, tu.result_summary
            FROM tool_usage tu
            JOIN sessions s ON tu.session_id = s.id
            WHERE s.project_id = ?
            ORDER BY tu.timestamp DESC 
            LIMIT ?
        """
        
        try:
            async with self.sqlite_manager.connection.execute(query, (project_id, limit)) as cursor:
                results = await cursor.fetchall()
            
            return [
                {
                    "tool_name": row[0],
                    "timestamp": row[1], 
                    "result_summary": row[2]
                }
                for row in results
            ]
        except Exception:
            return []
    
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
            ["suggest_methodology", "design_experimental_framework"],
            ["assess_foundational_assumptions", "generate_critical_questions"]
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
    
    def _check_sequence_match(self, tool_names: List[str], sequence: List[str]) -> bool:
        """Check if tool names contain a logical sequence"""
        if len(tool_names) < len(sequence):
            return False
        
        # Check if sequence appears in any order within recent tools
        sequence_indices = []
        for seq_tool in sequence:
            if seq_tool in tool_names:
                sequence_indices.append(tool_names.index(seq_tool))
        
        # If we found all tools in sequence, check if they appear in logical order
        return len(sequence_indices) == len(sequence) and sequence_indices == sorted(sequence_indices, reverse=True)
    
    async def _generate_enhanced_recommendations(
        self,
        project_id: int,
        current_context: Dict[str, Any], 
        recent_tools: List[Dict], 
        tool_patterns: Dict[str, Any],
        last_tool_used: str,
        recommendation_depth: int
    ) -> List[Dict[str, Any]]:
        """Generate enhanced recommendations based on context and patterns"""
        
        # Get base recommendations from existing framework
        base_recommendations = await self.generate_recommendations(project_id, 1)  # Use session_id=1 as default
        
        enhanced_recommendations = []
        
        # Enhance each recommendation with pattern-based intelligence
        for rec in base_recommendations[:recommendation_depth]:
            enhanced_rec = {
                "tool_name": rec.get("tool", ""),
                "research_act": rec.get("research_act", ""),
                "priority": rec.get("priority", "medium"),
                "base_reasoning": rec.get("enhanced_reasoning", ""),
                "pattern_context": self._get_pattern_context(rec.get("tool", ""), tool_patterns),
                "confidence": self._calculate_recommendation_confidence(rec, recent_tools, tool_patterns)
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return enhanced_recommendations
    
    def _get_pattern_context(self, tool_name: str, patterns: Dict[str, Any]) -> str:
        """Get pattern-specific context for a tool recommendation"""
        pattern_type = patterns.get("pattern_type", "unknown")
        
        if pattern_type == "repetitive":
            return f"Breaks repetitive pattern of {patterns.get('repeated_tool', 'unknown')}"
        elif pattern_type == "logical_progression":
            return f"Continues logical workflow progression"
        elif pattern_type == "exploratory":
            return f"Supports exploratory research approach"
        else:
            return "General recommendation"
    
    def _calculate_recommendation_confidence(self, rec: Dict, recent_tools: List[Dict], patterns: Dict) -> float:
        """Calculate confidence score for recommendation based on patterns"""
        base_confidence = 0.7  # Default confidence
        
        # Boost confidence for logical progressions
        if patterns.get("pattern_type") == "logical_progression":
            base_confidence += 0.2
        
        # Reduce confidence for repetitive patterns
        if patterns.get("pattern_type") == "repetitive":
            base_confidence -= 0.1
        
        # Adjust based on tool usage recency
        tool_name = rec.get("tool", "")
        recent_tool_names = [t["tool_name"] for t in recent_tools]
        if tool_name in recent_tool_names:
            base_confidence -= 0.1  # Slight penalty for recently used tools
        
        return max(0.1, min(1.0, base_confidence))  # Clamp between 0.1 and 1.0
    
    def _explain_recommendations(self, recommendations: List[Dict], patterns: Dict) -> str:
        """Generate explanation for the recommendation set"""
        if not recommendations:
            return "No specific recommendations available at this time."
        
        pattern_type = patterns.get("pattern_type", "unknown")
        
        explanations = [
            f"Based on your recent {pattern_type} research pattern, I recommend:",
        ]
        
        for i, rec in enumerate(recommendations, 1):
            explanations.append(
                f"{i}. **{rec['tool_name']}** ({rec['priority']} priority) - {rec['pattern_context']}"
            )
        
        if pattern_type == "repetitive":
            explanations.append("\nConsider diversifying your approach to explore new research dimensions.")
        elif pattern_type == "logical_progression":
            explanations.append("\nYour workflow shows good logical progression. Continue building on this foundation.")
        
        return "\n".join(explanations)
    
    async def _get_alternative_approaches(self, project_id: int, recommendations: List[Dict]) -> List[str]:
        """Suggest alternative research approaches"""
        # Get current research acts with significant progress
        query = """
            SELECT tu.research_act, COUNT(*) as count
            FROM tool_usage tu
            JOIN sessions s ON tu.session_id = s.id
            WHERE s.project_id = ? AND tu.success = 1
            GROUP BY tu.research_act
        """
        
        alternatives = []
        
        try:
            async with self.sqlite_manager.connection.execute(query, (project_id,)) as cursor:
                act_usage_rows = await cursor.fetchall()
            
            act_usage = {row[0]: row[1] for row in act_usage_rows}
        except Exception:
            act_usage = {}
        
        underused_acts = [act for act, count in act_usage.items() if count < 3]
        
        if underused_acts:
            alternatives.append(f"Explore underused research acts: {', '.join(underused_acts)}")
        
        # Suggest methodology diversity
        if len(set(rec["research_act"] for rec in recommendations)) < 2:
            alternatives.append("Consider incorporating tools from multiple research acts for a more comprehensive approach")
        
        return alternatives
