
# ALL MCP TOOLS

# Global ID counter for JSON-RPC calls
ID=1

# Log all output to .log file AND show in console in real time
LOG_FILE="$(dirname "$0")/all_mcp_tools_commands.log"

# Trap Ctrl+C (SIGINT) to exit cleanly
trap 'exit 130' INT

# Only print JSON lines from output (suppress all else)
run_cmd() {
  local label="$1"
  local cmd="$2"
  # Replace __ID__ placeholder with current ID value
  cmd="${cmd//__ID__/$ID}"
  # 10s timeout per command, adjust if needed
  echo ""
  echo "Running command: $ID. $label " | tee -a "$LOG_FILE"
  (echo "$cmd" | timeout 10s python3 work/code/mcp/server.py --stdio 2>/dev/null | grep -Eo '\{.*\}' || true) | tee -a "$LOG_FILE"
  ((ID++))
}


# initialize_project
PROJECT_NAME="Example Project $(date +%Y%m%d%H%M%S)"
run_cmd "initialize_project" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "initialize_project", "arguments": {"name": "'"${PROJECT_NAME}"'", "description": "Demo project", "domain": "General", "project_path": ""}}}'

# initialize_project for switch test
NAME_DATE=$(date +%Y%m%d%H%M%S)
TARGET_PROJECT_NAME="Example Switch Project ${NAME_DATE}"
TARGET_PROJECT_PATH="$HOME/Projects/example_switch_project_${NAME_DATE}"
run_cmd "initialize_project_for_switch" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "initialize_project", "arguments": {"name": "'"${TARGET_PROJECT_NAME}"'", "description": "Demo project for switch", "domain": "General", "project_path": ""}}}'
# 2. save_session
run_cmd "save_session" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "save_session", "arguments": {"session_data": {"note": "autosave"}}}}'

# 3. get_research_progress
run_cmd "get_research_progress" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "get_research_progress", "arguments": {}}}'

# 4. get_tool_usage_history
run_cmd "get_tool_usage_history" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "get_tool_usage_history", "arguments": {}}}'

# 5. get_research_milestones
run_cmd "get_research_milestones" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "get_research_milestones", "arguments": {}}}'

# 6. explain_methodology
run_cmd "explain_methodology" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "explain_methodology", "arguments": {"research_question": "What is the best approach for X?", "domain": "AI"}}}'

# 7. clarify_research_goals
run_cmd "clarify_research_goals" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "clarify_research_goals", "arguments": {"research_area": "AI", "initial_goals": "Build a chatbot"}}}'

# 8. suggest_methodology
run_cmd "suggest_methodology" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "suggest_methodology", "arguments": {"domain": "AI", "research_goals": "Conversational agent"}}}'

# 9. generate_critical_questions
run_cmd "generate_critical_questions" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_critical_questions", "arguments": {"paradigm_context": "AI", "research_area": "NLP"}}}'

# 10. check_quality_gates
run_cmd "check_quality_gates" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "check_quality_gates", "arguments": {"phase": "planning", "research_content": "Test content"}}}'

# 11. simulate_peer_review
run_cmd "simulate_peer_review" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "simulate_peer_review", "arguments": {"document_content": {"title": "Test"}, "domain": "general"}}}'

# 12. validate_design
run_cmd "validate_design" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "validate_design", "arguments": {"domain": "AI", "research_design": "Test design"}}}'

# 13. validate_novel_theory
run_cmd "validate_novel_theory" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "validate_novel_theory", "arguments": {"domain": "AI", "theory_framework": "Test theory"}}}'

# 14. ensure_ethics
run_cmd "ensure_ethics" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "ensure_ethics", "arguments": {"domain": "AI", "research_proposal": "Test proposal"}}}'

# 15. store_bibliography_reference - Add meaningful references
run_cmd "store_bibliography_reference_ai" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "store_bibliography_reference", "arguments": {"reference": {"title": "Attention Is All You Need", "authors": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., Polosukhin, I.", "year": "2017", "journal": "Advances in Neural Information Processing Systems", "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms."}}}}'

run_cmd "store_bibliography_reference_ml" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "store_bibliography_reference", "arguments": {"reference": {"title": "Deep Learning", "authors": "Goodfellow, Ian, Bengio, Yoshua, Courville, Aaron", "year": "2016", "journal": "MIT Press", "abstract": "Deep learning allows computational models that are composed of multiple processing layers to learn representations of data with multiple levels of abstraction. These methods have dramatically improved the state-of-the-art in speech recognition, visual object recognition, object detection and many other domains."}}}}'

run_cmd "store_bibliography_reference_nlp" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "store_bibliography_reference", "arguments": {"reference": {"title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", "authors": "Devlin, J., Chang, M. W., Lee, K., Toutanova, K.", "year": "2018", "journal": "arXiv preprint arXiv:1810.04805", "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text."}}}}'

# 16. retrieve_bibliography_references
run_cmd "retrieve_bibliography_references" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "retrieve_bibliography_references", "arguments": {"query": "AI"}}}'

# 17. generate_bibliography
run_cmd "generate_bibliography" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_bibliography", "arguments": {"references": ["Ref1", "Ref2"]}}}'

# 18. extract_document_sections - Add realistic document structure
run_cmd "extract_document_sections" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "extract_document_sections", "arguments": {"document_content": "# Introduction\nThis paper presents a novel approach to natural language processing using transformer architectures.\n\n## Background\nPrevious work in neural machine translation relied heavily on recurrent neural networks.\n\n## Methodology\nWe propose using self-attention mechanisms to eliminate the need for recurrence.\n\n## Results\nOur model achieves state-of-the-art performance on multiple benchmarks.\n\n## Conclusion\nTransformer architectures represent a significant advancement in sequence modeling."}}}'

# 19. extract_key_concepts - Use comprehensive text
run_cmd "extract_key_concepts" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "extract_key_concepts", "arguments": {"text": "Artificial intelligence encompasses machine learning algorithms that enable computers to learn from data without explicit programming. Deep learning utilizes neural networks with multiple layers to extract hierarchical features from raw input. Natural language processing combines computational linguistics with machine learning to help computers understand human language. Computer vision applies deep learning techniques to analyze and interpret visual information from images and videos. Reinforcement learning trains agents to make sequential decisions through interaction with environments."}}}'

# 20. format_research_content - Use structured research content
run_cmd "format_research_content" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "format_research_content", "arguments": {"content": "**Research Question**: How can transformer architectures improve natural language understanding?\n\n**Hypothesis**: Self-attention mechanisms in transformers can capture long-range dependencies more effectively than recurrent neural networks.\n\n**Methodology**: We will compare transformer models against LSTM baselines on multiple NLP tasks including sentiment analysis, question answering, and machine translation.\n\n**Expected Outcomes**: Transformers should demonstrate superior performance due to parallel processing capabilities and better handling of sequential dependencies."}}}'

# 21. generate_latex_document
run_cmd "generate_latex_document" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_latex_document", "arguments": {"title": "Test", "introduction": "Intro"}}}'

# 22. generate_latex_with_template
run_cmd "generate_latex_with_template" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_latex_with_template", "arguments": {"title": "Test", "template_type": "article"}}}'

# 23. generate_document_with_database_bibliography
run_cmd "generate_document_with_database_bibliography" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_document_with_database_bibliography", "arguments": {"title": "Test", "bibliography_query": "AI"}}}'

# 24. compile_latex
run_cmd "compile_latex" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "compile_latex", "arguments": {"tex_file_path": "test.tex"}}}'

# 25. list_latex_templates
run_cmd "list_latex_templates" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "list_latex_templates", "arguments": {}}}'

# 26. semantic_search
run_cmd "semantic_search" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "semantic_search", "arguments": {"query": "AI"}}}'

# 27. discover_patterns - Use richer content
run_cmd "discover_patterns" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "discover_patterns", "arguments": {"content": "Machine learning and artificial intelligence are transforming natural language processing. Deep neural networks enable sophisticated language understanding. Transformer architectures have revolutionized machine translation and text generation. Attention mechanisms allow models to focus on relevant information. Large language models demonstrate emergent capabilities in reasoning and comprehension. Neural networks learn hierarchical representations from data. Supervised learning requires labeled datasets while unsupervised learning discovers hidden patterns. Reinforcement learning optimizes decision-making through trial and error."}}}'

# 28. build_knowledge_graph - Use realistic documents
run_cmd "build_knowledge_graph" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "build_knowledge_graph", "arguments": {"documents": ["Transformer architectures use self-attention mechanisms to process sequential data. The attention mechanism allows the model to focus on different parts of the input sequence when producing each element of the output sequence.", "BERT employs bidirectional training to understand context from both directions. This approach significantly improves performance on natural language understanding tasks compared to unidirectional models.", "GPT models use autoregressive generation where each token is predicted based on previous tokens. This approach enables coherent text generation but limits bidirectional understanding."]}}}'

# 29. find_similar_documents - Use detailed target document
run_cmd "find_similar_documents" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "find_similar_documents", "arguments": {"target_document": "Neural networks with attention mechanisms have revolutionized natural language processing by enabling models to selectively focus on relevant parts of input sequences, leading to significant improvements in machine translation and text understanding tasks."}}}'

# 30. search_knowledge
run_cmd "search_knowledge" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "search_knowledge", "arguments": {"query": "AI"}}}'

# 31. generate_research_summary - Use actual document content
run_cmd "generate_research_summary" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "generate_research_summary", "arguments": {"documents": ["The Transformer model introduced the concept of self-attention, allowing each position in a sequence to attend to all positions in the previous layer. This architecture eliminated the need for recurrence and convolutions entirely, relying solely on attention mechanisms to draw global dependencies between input and output.", "BERT represents words and sentences in a way that incorporates context from both directions. By training on a masked language model objective, BERT learns rich representations that can be fine-tuned for various downstream tasks with minimal architecture changes.", "Large language models like GPT demonstrate emergent abilities as they scale, including few-shot learning, reasoning, and creative text generation. These capabilities arise from training on diverse text corpora and scaling both model size and compute resources."]}}}'

# 32. initiate_paradigm_challenge
run_cmd "initiate_paradigm_challenge" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "initiate_paradigm_challenge", "arguments": {"domain": "AI", "current_paradigm": "mainstream"}}}'

# 33. develop_alternative_framework
run_cmd "develop_alternative_framework" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "develop_alternative_framework", "arguments": {"domain": "AI", "core_principles": ["openness"]}}}'

# 34. assess_foundational_assumptions
run_cmd "assess_foundational_assumptions" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "assess_foundational_assumptions", "arguments": {"domain": "AI", "current_paradigm": "mainstream"}}}'

# 35. compare_approaches
run_cmd "compare_approaches" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "compare_approaches", "arguments": {"approach_a": "A", "approach_b": "B", "research_context": "AI"}}}'

# 36. compare_paradigms
run_cmd "compare_paradigms" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "compare_paradigms", "arguments": {"mainstream_paradigm": "A", "alternative_paradigm": "B", "domain": "AI", "comparison_criteria": ["validity"]}}}'

# 37. evaluate_paradigm_shift_potential
run_cmd "evaluate_paradigm_shift_potential" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "evaluate_paradigm_shift_potential", "arguments": {"domain": "AI", "theory_framework": "new theory"}}}'

# 38. cultivate_innovation
run_cmd "cultivate_innovation" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "cultivate_innovation", "arguments": {"domain": "AI", "innovation_goals": ["goal"], "research_idea": "idea"}}}'

# 39. start_research_session
run_cmd "start_research_session" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "start_research_session", "arguments": {"research_act": "planning", "research_focus": "AI"}}}'

# 40. get_session_summary
run_cmd "get_session_summary" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "get_session_summary", "arguments": {}}}'

# 41. restore_session
run_cmd "restore_session" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "restore_session", "arguments": {"session_id": 1}}}'

# 42. get_workflow_recommendations
run_cmd "get_workflow_recommendations" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "get_workflow_recommendations", "arguments": {}}}'

# 43. version_control
run_cmd "version_control" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "version_control", "arguments": {"action": "commit", "message": "Test commit from batch script"}}}'

# 44. switch_project_context
run_cmd "switch_project_context" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "switch_project_context", "arguments": {"target_project_path": "'"${TARGET_PROJECT_PATH}"'"}}}'

# 45. backup_project
run_cmd "backup_project" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "backup_project", "arguments": {"backup_location": "/tmp/backup"}}}'

# 46. reset_project_context
run_cmd "reset_project_context" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "reset_project_context", "arguments": {}}}'

# NEW ENHANCED CONVERSATIONAL GUIDANCE TOOLS

# 47. enhanced_socratic_dialogue
run_cmd "enhanced_socratic_dialogue" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_socratic_dialogue", "arguments": {"research_context": "quantum computing research", "dialogue_depth": 1, "focus_area": "clarification", "domain_specialization": "computer_science"}}}'

# 48. enhanced_socratic_dialogue with user response
run_cmd "enhanced_socratic_dialogue_with_response" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_socratic_dialogue", "arguments": {"research_context": "machine learning optimization", "user_response": "I want to develop neural network algorithms for image recognition", "dialogue_depth": 2, "focus_area": "assumption", "domain_specialization": "computer_science"}}}'

# 49. enhanced_socratic_dialogue depth 3
run_cmd "enhanced_socratic_dialogue_depth3" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_socratic_dialogue", "arguments": {"research_context": "biological systems modeling", "user_response": "I will use mathematical models to simulate enzyme kinetics", "dialogue_depth": 3, "focus_area": "validation", "domain_specialization": "biology"}}}'

# 50. enhanced_theory_challenger
run_cmd "enhanced_theory_challenger" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_theory_challenger", "arguments": {"theory_description": "Consciousness emerges from quantum coherence in neural microtubules", "domain": "neuroscience", "challenge_intensity": "moderate"}}}'

# 51. enhanced_theory_challenger gentle
run_cmd "enhanced_theory_challenger_gentle" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_theory_challenger", "arguments": {"theory_description": "Machine learning models can achieve general intelligence through scaling", "domain": "computer_science", "challenge_intensity": "gentle"}}}'

# 52. enhanced_theory_challenger rigorous
run_cmd "enhanced_theory_challenger_rigorous" '{"jsonrpc": "2.0", "id": __ID__, "method": "tools/call", "params": {"name": "enhanced_theory_challenger", "arguments": {"theory_description": "Dark matter consists of primordial black holes", "domain": "physics", "challenge_intensity": "rigorous"}}}'

exit 0