
# ALL MCP TOOLS


# Log all output to .log file AND show in console in real time
LOG_FILE="$(dirname "$0")/all_mcp_tools_commands.log"

# Trap Ctrl+C (SIGINT) to exit cleanly
trap 'exit 130' INT

# Only print JSON lines from output (suppress all else)
run_cmd() {
  local label="$1"
  local cmd="$2"
  # 10s timeout per command, adjust if needed
  echo ""
  echo "Running command: $label " | tee -a "$LOG_FILE"
  (echo "$cmd" | timeout 10s python3 work/code/mcp/server.py --stdio 2>/dev/null | grep -Eo '\{.*\}' || true) | tee -a "$LOG_FILE"
}


# 1. initialize_project
PROJECT_NAME="Example Project $(date +%Y%m%d%H%M%S)"
run_cmd "1.1 initialize_project" '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "initialize_project", "arguments": {"name": "'"${PROJECT_NAME}"'", "description": "Demo project", "domain": "General", "project_path": ""}}}'

# 99. initialize_project
NAME_DATE=$(date +%Y%m%d%H%M%S)
TARGET_PROJECT_NAME="Example Switch Project $(NAME_DATE)"
TARGET_PROJECT_PATH="~/Projects/example_switch_project_$(NAME_DATE)"
run_cmd "99. initialize_project" "{\"jsonrpc\": \"2.0\", \"id\": 99, \"method\": \"tools/call\", \"params\": {\"name\": \"initialize_project\", \"arguments\": {\"name\": \"${TARGET_PROJECT_NAME}\", \"description\": \"Demo project for switch\", \"domain\": \"General\", \"project_path\": \"\"}}}"
# 2. save_session
run_cmd "2. save_session" '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "save_session", "arguments": {"session_data": {"note": "autosave"}}}}'

# 3. get_research_progress
run_cmd "3. get_research_progress" '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_research_progress", "arguments": {}}}'

# 4. get_tool_usage_history
run_cmd "4. get_tool_usage_history" '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_tool_usage_history", "arguments": {}}}'

# 5. get_research_milestones
run_cmd "5. get_research_milestones" '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_research_milestones", "arguments": {}}}'

# 6. explain_methodology
run_cmd "6. explain_methodology" '{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "explain_methodology", "arguments": {"research_question": "What is the best approach for X?", "domain": "AI"}}}'

# 7. clarify_research_goals
run_cmd "7. clarify_research_goals" '{"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "clarify_research_goals", "arguments": {"research_area": "AI", "initial_goals": "Build a chatbot"}}}'

# 8. suggest_methodology
run_cmd "8. suggest_methodology" '{"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "suggest_methodology", "arguments": {"domain": "AI", "research_goals": "Conversational agent"}}}'

# 9. generate_critical_questions
run_cmd "9. generate_critical_questions" '{"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "generate_critical_questions", "arguments": {"paradigm_context": "AI", "research_area": "NLP"}}}'

# 10. check_quality_gates
run_cmd "10. check_quality_gates" '{"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "check_quality_gates", "arguments": {"phase": "planning", "research_content": "Test content"}}}'

# 11. simulate_peer_review
run_cmd "11. simulate_peer_review" '{"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "simulate_peer_review", "arguments": {"document_content": {"title": "Test"}, "domain": "general"}}}'

# 12. validate_design
run_cmd "12. validate_design" '{"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "validate_design", "arguments": {"domain": "AI", "research_design": "Test design"}}}'

# 13. validate_novel_theory
run_cmd "13. validate_novel_theory" '{"jsonrpc": "2.0", "id": 13, "method": "tools/call", "params": {"name": "validate_novel_theory", "arguments": {"domain": "AI", "theory_framework": "Test theory"}}}'

# 14. ensure_ethics
run_cmd "14. ensure_ethics" '{"jsonrpc": "2.0", "id": 14, "method": "tools/call", "params": {"name": "ensure_ethics", "arguments": {"domain": "AI", "research_proposal": "Test proposal"}}}'

# 15. store_bibliography_reference
run_cmd "15. store_bibliography_reference" '{"jsonrpc": "2.0", "id": 15, "method": "tools/call", "params": {"name": "store_bibliography_reference", "arguments": {"reference": "Test reference"}}}'

# 16. retrieve_bibliography_references
run_cmd "16. retrieve_bibliography_references" '{"jsonrpc": "2.0", "id": 16, "method": "tools/call", "params": {"name": "retrieve_bibliography_references", "arguments": {"query": "AI"}}}'

# 17. generate_bibliography
run_cmd "17. generate_bibliography" '{"jsonrpc": "2.0", "id": 17, "method": "tools/call", "params": {"name": "generate_bibliography", "arguments": {"references": ["Ref1", "Ref2"]}}}'

# 18. extract_document_sections
run_cmd "18. extract_document_sections" '{"jsonrpc": "2.0", "id": 18, "method": "tools/call", "params": {"name": "extract_document_sections", "arguments": {"document_content": "Section 1\nSection 2"}}}'

# 19. extract_key_concepts
run_cmd "19. extract_key_concepts" '{"jsonrpc": "2.0", "id": 19, "method": "tools/call", "params": {"name": "extract_key_concepts", "arguments": {"text": "AI and ML are related"}}}'

# 20. format_research_content
run_cmd "20. format_research_content" '{"jsonrpc": "2.0", "id": 20, "method": "tools/call", "params": {"name": "format_research_content", "arguments": {"content": "Some text"}}}'

# 21. generate_latex_document
run_cmd "21. generate_latex_document" '{"jsonrpc": "2.0", "id": 21, "method": "tools/call", "params": {"name": "generate_latex_document", "arguments": {"title": "Test", "introduction": "Intro"}}}'

# 22. generate_latex_with_template
run_cmd "22. generate_latex_with_template" '{"jsonrpc": "2.0", "id": 22, "method": "tools/call", "params": {"name": "generate_latex_with_template", "arguments": {"title": "Test", "template_type": "article"}}}'

# 23. generate_document_with_database_bibliography
run_cmd "23. generate_document_with_database_bibliography" '{"jsonrpc": "2.0", "id": 23, "method": "tools/call", "params": {"name": "generate_document_with_database_bibliography", "arguments": {"title": "Test", "bibliography_query": "AI"}}}'

# 24. compile_latex
run_cmd "24. compile_latex" '{"jsonrpc": "2.0", "id": 24, "method": "tools/call", "params": {"name": "compile_latex", "arguments": {"tex_file_path": "test.tex"}}}'

# 25. list_latex_templates
run_cmd "25. list_latex_templates" '{"jsonrpc": "2.0", "id": 25, "method": "tools/call", "params": {"name": "list_latex_templates", "arguments": {}}}'

# 26. semantic_search
run_cmd "26. semantic_search" '{"jsonrpc": "2.0", "id": 26, "method": "tools/call", "params": {"name": "semantic_search", "arguments": {"query": "AI"}}}'

# 27. discover_patterns
run_cmd "27. discover_patterns" '{"jsonrpc": "2.0", "id": 27, "method": "tools/call", "params": {"name": "discover_patterns", "arguments": {"content": "AI, ML, AI, NLP"}}}'

# 28. build_knowledge_graph
run_cmd "28. build_knowledge_graph" '{"jsonrpc": "2.0", "id": 28, "method": "tools/call", "params": {"name": "build_knowledge_graph", "arguments": {"documents": ["doc1", "doc2"]}}}'

# 29. find_similar_documents
run_cmd "29. find_similar_documents" '{"jsonrpc": "2.0", "id": 29, "method": "tools/call", "params": {"name": "find_similar_documents", "arguments": {"target_document": "AI"}}}'

# 30. search_knowledge
run_cmd "30. search_knowledge" '{"jsonrpc": "2.0", "id": 30, "method": "tools/call", "params": {"name": "search_knowledge", "arguments": {"query": "AI"}}}'

# 31. generate_research_summary
run_cmd "31. generate_research_summary" '{"jsonrpc": "2.0", "id": 31, "method": "tools/call", "params": {"name": "generate_research_summary", "arguments": {"documents": ["Document1.txt", "Document2.txt"]}}}'

# 32. initiate_paradigm_challenge
run_cmd "32. initiate_paradigm_challenge" '{"jsonrpc": "2.0", "id": 32, "method": "tools/call", "params": {"name": "initiate_paradigm_challenge", "arguments": {"domain": "AI", "current_paradigm": "mainstream"}}}'

# 33. develop_alternative_framework
run_cmd "33. develop_alternative_framework" '{"jsonrpc": "2.0", "id": 33, "method": "tools/call", "params": {"name": "develop_alternative_framework", "arguments": {"domain": "AI", "core_principles": ["openness"]}}}'

# 34. assess_foundational_assumptions
run_cmd "34. assess_foundational_assumptions" '{"jsonrpc": "2.0", "id": 34, "method": "tools/call", "params": {"name": "assess_foundational_assumptions", "arguments": {"domain": "AI", "current_paradigm": "mainstream"}}}'

# 35. compare_approaches
run_cmd "35. compare_approaches" '{"jsonrpc": "2.0", "id": 35, "method": "tools/call", "params": {"name": "compare_approaches", "arguments": {"approach_a": "A", "approach_b": "B", "research_context": "AI"}}}'

# 36. compare_paradigms
run_cmd "36. compare_paradigms" '{"jsonrpc": "2.0", "id": 36, "method": "tools/call", "params": {"name": "compare_paradigms", "arguments": {"mainstream_paradigm": "A", "alternative_paradigm": "B", "domain": "AI", "comparison_criteria": ["validity"]}}}'

# 37. evaluate_paradigm_shift_potential
run_cmd "37. evaluate_paradigm_shift_potential" '{"jsonrpc": "2.0", "id": 37, "method": "tools/call", "params": {"name": "evaluate_paradigm_shift_potential", "arguments": {"domain": "AI", "theory_framework": "new theory"}}}'

# 38. cultivate_innovation
run_cmd "38. cultivate_innovation" '{"jsonrpc": "2.0", "id": 38, "method": "tools/call", "params": {"name": "cultivate_innovation", "arguments": {"domain": "AI", "innovation_goals": ["goal"], "research_idea": "idea"}}}'

# 39. start_research_session
run_cmd "39. start_research_session" '{"jsonrpc": "2.0", "id": 39, "method": "tools/call", "params": {"name": "start_research_session", "arguments": {"research_act": "planning", "research_focus": "AI"}}}'

# 40. get_session_summary
run_cmd "40. get_session_summary" '{"jsonrpc": "2.0", "id": 40, "method": "tools/call", "params": {"name": "get_session_summary", "arguments": {}}}'

# 41. restore_session
run_cmd "41. restore_session" '{"jsonrpc": "2.0", "id": 41, "method": "tools/call", "params": {"name": "restore_session", "arguments": {"session_id": 1}}}'

# 42. get_workflow_recommendations
run_cmd "42. get_workflow_recommendations" '{"jsonrpc": "2.0", "id": 42, "method": "tools/call", "params": {"name": "get_workflow_recommendations", "arguments": {}}}'

# 43. version_control
run_cmd "43. version_control" '{"jsonrpc": "2.0", "id": 43, "method": "tools/call", "params": {"name": "version_control", "arguments": {"action": "commit", "message": "Test commit from batch script"}}}'

# 44. switch_project_context
run_cmd "44. switch_project_context" '{"jsonrpc": "2.0", "id": 44, "method": "tools/call", "params": {"name": "switch_project_context", "arguments": {"target_project_path": "'"${TARGET_PROJECT_PATH}"'"}}}'

# 45. backup_project
run_cmd "45. backup_project" '{"jsonrpc": "2.0", "id": 45, "method": "tools/call", "params": {"name": "backup_project", "arguments": {"backup_location": "/tmp/backup"}}}'

# 46. reset_project_context
run_cmd "46. reset_project_context" '{"jsonrpc": "2.0", "id": 46, "method": "tools/call", "params": {"name": "reset_project_context", "arguments": {}}}'

exit 0