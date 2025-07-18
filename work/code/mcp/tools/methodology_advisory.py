"""
Methodology Advisory MCP Tools
Provides expert-level guidance on research methodologies, design validation, and ethics
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import context-aware decorator
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'utils'))
from context_decorator import context_aware, project_required

class MethodologyAdvisoryTool:
    """MCP tool for methodology advisory and guidance"""
    
    def __init__(self):
        self.methodologies = {
            "experimental": {
                "description": "Controlled experimental research design",
                "requirements": ["Control groups", "Random assignment", "Dependent/independent variables"],
                "best_practices": ["Blinding", "Randomization", "Sample size calculation"],
                "domains": ["psychology", "medicine", "biology", "physics"],
                "ethics_considerations": ["Informed consent", "Risk assessment", "IRB approval"]
            },
            "observational": {
                "description": "Observation-based research without intervention",
                "requirements": ["Clear observation criteria", "Systematic data collection"],
                "best_practices": ["Inter-rater reliability", "Longitudinal tracking", "Bias control"],
                "domains": ["anthropology", "sociology", "ecology", "astronomy"],
                "ethics_considerations": ["Privacy protection", "Observational consent", "Data anonymization"]
            },
            "theoretical": {
                "description": "Mathematical or conceptual theory development",
                "requirements": ["Mathematical framework", "Logical consistency", "Testable predictions"],
                "best_practices": ["Peer review", "Model validation", "Falsifiability"],
                "domains": ["physics", "mathematics", "computer_science", "philosophy"],
                "ethics_considerations": ["Intellectual property", "Citation ethics", "Open science"]
            },
            "mixed_methods": {
                "description": "Combination of quantitative and qualitative approaches",
                "requirements": ["Clear integration strategy", "Appropriate weighting"],
                "best_practices": ["Sequential design", "Triangulation", "Mixed analysis"],
                "domains": ["social_sciences", "education", "health_sciences"],
                "ethics_considerations": ["Comprehensive consent", "Data integration ethics"]
            },
            "systematic_review": {
                "description": "Comprehensive synthesis of existing research",
                "requirements": ["Search strategy", "Inclusion/exclusion criteria", "Quality assessment"],
                "best_practices": ["PRISMA guidelines", "Meta-analysis", "Risk of bias assessment"],
                "domains": ["medicine", "psychology", "education"],
                "ethics_considerations": ["Publication bias", "Selective reporting"]
            }
        }
        
        self.research_designs = {
            "randomized_controlled_trial": {
                "description": "Gold standard for causal inference",
                "strengths": ["High internal validity", "Causal inference", "Bias control"],
                "limitations": ["External validity concerns", "Ethical constraints", "High cost"],
                "requirements": ["Random assignment", "Control group", "Outcome measures"]
            },
            "cohort_study": {
                "description": "Longitudinal observational study",
                "strengths": ["Temporal relationships", "Multiple outcomes", "Natural progression"],
                "limitations": ["Time intensive", "Attrition", "Confounding"],
                "requirements": ["Baseline measurement", "Follow-up protocol", "Exposure definition"]
            },
            "case_control": {
                "description": "Retrospective comparison study",
                "strengths": ["Efficient for rare outcomes", "Cost effective", "Quick results"],
                "limitations": ["Recall bias", "Selection bias", "Temporal ambiguity"],
                "requirements": ["Case definition", "Control selection", "Exposure measurement"]
            },
            "cross_sectional": {
                "description": "Snapshot study at single time point",
                "strengths": ["Quick data collection", "Prevalence estimation", "Hypothesis generation"],
                "limitations": ["No causality", "Temporal ambiguity", "Survival bias"],
                "requirements": ["Representative sampling", "Standardized measurement"]
            }
        }
        
        self.ethics_frameworks = {
            "principlism": {
                "principles": ["Autonomy", "Beneficence", "Non-maleficence", "Justice"],
                "application": "Standard bioethics framework for research",
                "considerations": ["Informed consent", "Risk-benefit analysis", "Fair subject selection"]
            },
            "utilitarian": {
                "principles": ["Greatest good for greatest number"],
                "application": "Public health and population studies",
                "considerations": ["Population benefit", "Resource allocation", "Social utility"]
            },
            "deontological": {
                "principles": ["Duty-based ethics", "Categorical imperatives"],
                "application": "Rights-based research ethics",
                "considerations": ["Absolute rights", "Duty to subjects", "Moral rules"]
            },
            "virtue_ethics": {
                "principles": ["Character-based ethics", "Professional virtues"],
                "application": "Research integrity and conduct",
                "considerations": ["Honesty", "Compassion", "Professional responsibility"]
            }
        }

@context_aware()
async def explain_methodology(**kwargs) -> str:
    """Explain methodology for research question"""
    
    research_question = kwargs.get("research_question")
    domain = kwargs.get("domain")
    methodology_type = kwargs.get("methodology_type")
    
    if not research_question or not domain:
        return "Error: Missing required parameters (research_question, domain)"
    
    tool = MethodologyAdvisoryTool()
    
    response = {
        "research_question": research_question,
        "domain": domain,
        "methodology_analysis": {},
        "recommendations": [],
        "next_steps": []
    }
    
    # If specific methodology requested, provide detailed explanation
    if methodology_type and methodology_type in tool.methodologies:
        methodology = tool.methodologies[methodology_type]
        response["methodology_analysis"] = {
            "methodology": methodology_type,
            "description": methodology["description"],
            "requirements": methodology["requirements"],
            "best_practices": methodology["best_practices"],
            "suitability_for_domain": methodology_type in methodology.get("domains", []),
            "ethics_considerations": methodology["ethics_considerations"]
        }
    else:
        # Recommend suitable methodologies based on question and domain
        suitable_methodologies = []
        for method_name, method_info in tool.methodologies.items():
            if domain in method_info.get("domains", []):
                suitable_methodologies.append({
                    "methodology": method_name,
                    "description": method_info["description"],
                    "suitability_score": _calculate_suitability(research_question, method_info)
                })
        
        response["methodology_analysis"] = {
            "suitable_methodologies": sorted(suitable_methodologies, 
                                           key=lambda x: x["suitability_score"], reverse=True)[:3]
        }
    
    # Generate recommendations
    response["recommendations"] = [
        f"Consider {methodology_type or 'appropriate methodology'} for your {domain} research",
        "Ensure ethical approval before beginning data collection",
        "Develop detailed protocol with clear inclusion/exclusion criteria",
        "Plan for adequate sample size and statistical power"
    ]
    
    response["next_steps"] = [
        "Refine research question to be more specific",
        "Consult with methodology expert in your field",
        "Submit research protocol for ethical review",
        "Pilot test your methodology on small sample"
    ]
    
    return json.dumps(response, indent=2)

def _calculate_suitability(research_question: str, methodology_info: Dict) -> float:
    """Calculate methodology suitability score"""
    score = 0.5  # Base score
    
    # Simple keyword matching for demonstration
    question_lower = research_question.lower()
    
    if "cause" in question_lower or "effect" in question_lower:
        if "experimental" in methodology_info["description"]:
            score += 0.3
    
    if "observe" in question_lower or "describe" in question_lower:
        if "observational" in methodology_info["description"]:
            score += 0.3
    
    if "theory" in question_lower or "model" in question_lower:
        if "theoretical" in methodology_info["description"]:
            score += 0.3
    
    return min(score, 1.0)

@context_aware()
async def compare_approaches(**kwargs) -> str:
    """Compare different research approaches"""
    
    approach_a = kwargs.get("approach_a")
    approach_b = kwargs.get("approach_b")
    research_context = kwargs.get("research_context")
    
    if not approach_a or not approach_b or not research_context:
        return "Error: Missing required parameters (approach_a, approach_b, research_context)"
    
    tool = MethodologyAdvisoryTool()
    
    def get_approach_info(approach_name: str) -> Dict:
        # Check if it's a methodology
        if approach_name in tool.methodologies:
            return {
                "type": "methodology",
                "info": tool.methodologies[approach_name]
            }
        # Check if it's a research design
        elif approach_name in tool.research_designs:
            return {
                "type": "design",
                "info": tool.research_designs[approach_name]
            }
        else:
            return {
                "type": "unknown",
                "info": {"description": f"Unknown approach: {approach_name}"}
            }
    
    approach_a_info = get_approach_info(approach_a)
    approach_b_info = get_approach_info(approach_b)
    
    comparison = {
        "research_context": research_context,
        "comparison": {
            "approach_a": {
                "name": approach_a,
                "type": approach_a_info["type"],
                "details": approach_a_info["info"]
            },
            "approach_b": {
                "name": approach_b,
                "type": approach_b_info["type"],
                "details": approach_b_info["info"]
            }
        },
        "strengths_weaknesses": {},
        "recommendation": "",
        "considerations": []
    }
    
    # Add strengths/weaknesses if available
    if approach_a_info["type"] == "design":
        comparison["strengths_weaknesses"]["approach_a"] = {
            "strengths": approach_a_info["info"].get("strengths", []),
            "limitations": approach_a_info["info"].get("limitations", [])
        }
    
    if approach_b_info["type"] == "design":
        comparison["strengths_weaknesses"]["approach_b"] = {
            "strengths": approach_b_info["info"].get("strengths", []),
            "limitations": approach_b_info["info"].get("limitations", [])
        }
    
    # Generate recommendation
    comparison["recommendation"] = f"For your research context '{research_context}', consider the trade-offs between {approach_a} and {approach_b}. The choice depends on your specific research question, available resources, and ethical considerations."
    
    comparison["considerations"] = [
        "Internal vs external validity trade-offs",
        "Resource requirements and feasibility",
        "Ethical implications of each approach",
        "Timeline and practical constraints",
        "Statistical power and sample size requirements"
    ]
    
    return json.dumps(comparison, indent=2)

@context_aware()
async def validate_design(**kwargs) -> str:
    """Validate research design and provide improvement suggestions"""
    
    research_design = kwargs.get("research_design")
    domain = kwargs.get("domain")
    constraints = kwargs.get("constraints")
    
    if not research_design or not domain:
        return "Error: Missing required parameters (research_design, domain)"
    
    validation_results = {
        "design_overview": research_design,
        "domain": domain,
        "constraints": constraints or {},
        "validation_results": {
            "validity_checks": [],
            "methodological_rigor": "",
            "ethical_assessment": "",
            "feasibility_analysis": ""
        },
        "improvement_suggestions": [],
        "critical_issues": [],
        "approval_status": ""
    }
    
    # Validate key components
    required_components = ["research_question", "methodology", "sample", "data_collection", "analysis_plan"]
    missing_components = [comp for comp in required_components if comp not in research_design]
    
    if missing_components:
        validation_results["critical_issues"].extend([
            f"Missing critical component: {comp}" for comp in missing_components
        ])
    
    # Check validity
    validity_checks = []
    
    # Internal validity
    if "control_group" in research_design or "randomization" in research_design:
        validity_checks.append("✓ Internal validity: Control measures present")
    else:
        validity_checks.append("⚠ Internal validity: Consider adding control measures")
    
    # External validity
    if "sample" in research_design:
        sample_info = research_design["sample"]
        if isinstance(sample_info, dict) and sample_info.get("representative"):
            validity_checks.append("✓ External validity: Representative sampling planned")
        else:
            validity_checks.append("⚠ External validity: Ensure representative sampling")
    
    # Construct validity
    if "measurement" in research_design:
        validity_checks.append("✓ Construct validity: Measurement plan specified")
    else:
        validity_checks.append("⚠ Construct validity: Define measurement instruments")
    
    validation_results["validation_results"]["validity_checks"] = validity_checks
    
    # Methodological rigor assessment
    rigor_score = 0
    rigor_factors = []
    
    if "methodology" in research_design:
        rigor_score += 2
        rigor_factors.append("Methodology specified")
    
    if "sample_size_calculation" in research_design:
        rigor_score += 2
        rigor_factors.append("Power analysis conducted")
    
    if "bias_control" in research_design:
        rigor_score += 2
        rigor_factors.append("Bias control measures")
    
    if "quality_control" in research_design:
        rigor_score += 1
        rigor_factors.append("Quality control procedures")
    
    validation_results["validation_results"]["methodological_rigor"] = f"Score: {rigor_score}/7 - {', '.join(rigor_factors)}"
    
    # Ethical assessment
    ethical_issues = []
    if "ethics_approval" not in research_design:
        ethical_issues.append("Ethics approval not mentioned")
    if "informed_consent" not in research_design:
        ethical_issues.append("Informed consent procedure not specified")
    if "risk_assessment" not in research_design:
        ethical_issues.append("Risk assessment not included")
    
    if ethical_issues:
        validation_results["validation_results"]["ethical_assessment"] = "⚠ Issues: " + ", ".join(ethical_issues)
    else:
        validation_results["validation_results"]["ethical_assessment"] = "✓ Ethical considerations addressed"
    
    # Feasibility analysis
    feasibility_concerns = []
    if constraints:
        if constraints.get("timeline") == "short" and "longitudinal" in str(research_design).lower():
            feasibility_concerns.append("Timeline may be insufficient for longitudinal design")
        if constraints.get("budget") == "low" and "large_sample" in str(research_design).lower():
            feasibility_concerns.append("Budget constraints may limit large sample recruitment")
    
    validation_results["validation_results"]["feasibility_analysis"] = (
        "✓ Design appears feasible" if not feasibility_concerns 
        else "⚠ Concerns: " + ", ".join(feasibility_concerns)
    )
    
    # Generate improvement suggestions
    suggestions = []
    if rigor_score < 5:
        suggestions.append("Consider adding power analysis and sample size calculation")
    if "pilot_study" not in research_design:
        suggestions.append("Plan a pilot study to test procedures")
    if "data_management" not in research_design:
        suggestions.append("Develop detailed data management plan")
    
    validation_results["improvement_suggestions"] = suggestions
    
    # Overall approval status
    critical_count = len(validation_results["critical_issues"])
    if critical_count == 0 and rigor_score >= 5:
        validation_results["approval_status"] = "✓ Ready for implementation with minor refinements"
    elif critical_count <= 2:
        validation_results["approval_status"] = "⚠ Needs revision before implementation"
    else:
        validation_results["approval_status"] = "❌ Major revisions required"
    
    return json.dumps(validation_results, indent=2)

@context_aware()
async def ensure_ethics(**kwargs) -> str:
    """Provide ethical review and compliance checking"""
    
    research_proposal = kwargs.get("research_proposal")
    domain = kwargs.get("domain")
    participant_type = kwargs.get("participant_type", "adults")
    
    if not research_proposal or not domain:
        return "Error: Missing required parameters (research_proposal, domain)"
    
    tool = MethodologyAdvisoryTool()
    
    ethics_review = {
        "proposal_summary": research_proposal,
        "domain": domain,
        "participant_type": participant_type,
        "ethical_framework_analysis": {},
        "compliance_checklist": {},
        "risk_assessment": {},
        "recommendations": [],
        "required_approvals": []
    }
    
    # Analyze using principlism framework (most common in research ethics)
    framework = tool.ethics_frameworks["principlism"]
    ethics_review["ethical_framework_analysis"] = {
        "framework": "principlism",
        "principles": framework["principles"],
        "analysis": {}
    }
    
    # Autonomy analysis
    autonomy_issues = []
    proposal_dict = research_proposal if isinstance(research_proposal, dict) else {}
    if "informed_consent" not in proposal_dict:
        autonomy_issues.append("Informed consent procedure not specified")
    if "voluntary_participation" not in proposal_dict:
        autonomy_issues.append("Voluntary participation not addressed")
    if participant_type in ["minors", "vulnerable_populations"]:
        autonomy_issues.append("Special consent procedures needed for vulnerable populations")
    
    ethics_review["ethical_framework_analysis"]["analysis"]["autonomy"] = {
        "status": "✓ Adequate" if not autonomy_issues else "⚠ Needs attention",
        "issues": autonomy_issues
    }
    
    # Beneficence/Non-maleficence analysis
    benefit_risk_issues = []
    if "risk_assessment" not in proposal_dict:
        benefit_risk_issues.append("Risk assessment not provided")
    if "potential_benefits" not in proposal_dict:
        benefit_risk_issues.append("Potential benefits not specified")
    
    ethics_review["ethical_framework_analysis"]["analysis"]["beneficence"] = {
        "status": "✓ Adequate" if not benefit_risk_issues else "⚠ Needs attention",
        "issues": benefit_risk_issues
    }
    
    # Justice analysis
    justice_issues = []
    if "participant_selection" not in proposal_dict:
        justice_issues.append("Fair participant selection criteria not specified")
    if "data_sharing" not in proposal_dict:
        justice_issues.append("Data sharing and benefit distribution not addressed")
    
    ethics_review["ethical_framework_analysis"]["analysis"]["justice"] = {
        "status": "✓ Adequate" if not justice_issues else "⚠ Needs attention",
        "issues": justice_issues
    }
    
    # Compliance checklist
    compliance_items = {
        "IRB_approval": "ethics_approval" in proposal_dict,
        "informed_consent_form": "informed_consent" in proposal_dict,
        "data_protection_plan": "data_protection" in proposal_dict,
        "risk_mitigation_plan": "risk_mitigation" in proposal_dict,
        "adverse_event_reporting": "adverse_event_plan" in proposal_dict,
        "data_retention_policy": "data_retention" in proposal_dict
    }
    
    ethics_review["compliance_checklist"] = {
        item: "✓ Complete" if status else "❌ Missing"
        for item, status in compliance_items.items()
    }
    
    # Risk assessment
    risk_levels = {
        "minimal_risk": "Standard procedures, no greater than daily life risks",
        "minor_increase": "Slightly above minimal risk, manageable",
        "moderate_risk": "Significant but manageable risks, requires monitoring",
        "high_risk": "Substantial risks, requires extensive safeguards"
    }
    
    # Determine risk level based on proposal content
    risk_indicators = str(research_proposal).lower()
    if any(word in risk_indicators for word in ["invasive", "medication", "psychological_stress"]):
        estimated_risk = "moderate_risk"
    elif any(word in risk_indicators for word in ["survey", "interview", "observation"]):
        estimated_risk = "minimal_risk"
    else:
        estimated_risk = "minor_increase"
    
    ethics_review["risk_assessment"] = {
        "estimated_risk_level": estimated_risk,
        "description": risk_levels[estimated_risk],
        "mitigation_required": estimated_risk in ["moderate_risk", "high_risk"]
    }
    
    # Generate recommendations
    recommendations = []
    if any(not status for status in compliance_items.values()):
        recommendations.append("Complete all missing compliance documentation")
    if estimated_risk in ["moderate_risk", "high_risk"]:
        recommendations.append("Develop comprehensive risk mitigation plan")
    if participant_type in ["minors", "vulnerable_populations"]:
        recommendations.append("Obtain specialized ethical approval for vulnerable populations")
    
    ethics_review["recommendations"] = recommendations
    
    # Required approvals
    approvals = ["Institutional Review Board (IRB)"]
    if domain in ["medicine", "psychology"]:
        approvals.append("Disciplinary ethics committee")
    if "international" in str(research_proposal).lower():
        approvals.append("Multi-site ethics approval")
    
    ethics_review["required_approvals"] = approvals
    
    return json.dumps(ethics_review, indent=2)

def register_methodology_tools(server):
    """Register methodology advisory tools with the MCP server"""
    
    server.register_tool(
        name="explain_methodology",
        description="Detailed explanation of research methodologies",
        parameters={
            "type": "object",
            "properties": {
                "research_question": {"type": "string", "description": "Research question to address"},
                "domain": {"type": "string", "description": "Research domain"},
                "methodology_type": {"type": "string", "description": "Specific methodology to explain (optional)"}
            },
            "required": ["research_question", "domain"]
        },
        handler=explain_methodology
    )
    
    server.register_tool(
        name="compare_approaches",
        description="Comparative analysis of different research approaches",
        parameters={
            "type": "object",
            "properties": {
                "approach_a": {"type": "string", "description": "First research approach"},
                "approach_b": {"type": "string", "description": "Second research approach"},
                "research_context": {"type": "string", "description": "Research context for comparison"}
            },
            "required": ["approach_a", "approach_b", "research_context"]
        },
        handler=compare_approaches
    )
    
    server.register_tool(
        name="validate_design",
        description="Research design validation and improvement suggestions",
        parameters={
            "type": "object",
            "properties": {
                "research_design": {"type": "object", "description": "Research design to validate"},
                "domain": {"type": "string", "description": "Research domain"},
                "constraints": {"type": "object", "description": "Resource or other constraints"}
            },
            "required": ["research_design", "domain"]
        },
        handler=validate_design
    )
    
    server.register_tool(
        name="ensure_ethics",
        description="Ethical review and compliance checking",
        parameters={
            "type": "object",
            "properties": {
                "research_proposal": {"type": "object", "description": "Research proposal to review"},
                "domain": {"type": "string", "description": "Research domain"},
                "participant_type": {"type": "string", "description": "Type of participants (adults, minors, vulnerable_populations)", "default": "adults"}
            },
            "required": ["research_proposal", "domain"]
        },
        handler=ensure_ethics
    )
