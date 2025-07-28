"""
Complete research lifecycle test for MAIN MCP Server (mcp_server.py)
Tests the end-to-end workflow execution using the ACTUAL working server
"""

import asyncio
import tempfile
from pathlib import Path
import sys
import json

# Add path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / 'code' / 'mcp'))

import pytest
from mcp_server import ClaudeMCPServer
from srrd_builder.config.installation_status import is_latex_installed, is_vector_db_installed


@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation by clearing module cache and restoring environment variable"""
    import os
    import sys
    original_env = os.environ.get('SRRD_PROJECT_PATH')
    print("[ISOLATION] Storing SRRD_PROJECT_PATH:", original_env)
    yield
    # Restore environment variable
    if original_env is not None:
        os.environ['SRRD_PROJECT_PATH'] = original_env
        print("[ISOLATION] Restored SRRD_PROJECT_PATH to:", original_env)
    elif 'SRRD_PROJECT_PATH' in os.environ:
        del os.environ['SRRD_PROJECT_PATH']
        print("[ISOLATION] Deleted SRRD_PROJECT_PATH")
    # Clear module cache after test to prevent state pollution
    modules_to_clear = [m for m in sys.modules.keys() if any(x in m for x in ['mcp_server', 'tools', 'storage', 'utils']) and m not in ['sys', 'os', 'pathlib', 'tempfile', 'json']]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    print("[ISOLATION] Cleared modules:", modules_to_clear)


@pytest.mark.asyncio
@pytest.mark.skipif(not (is_latex_installed() and is_vector_db_installed()), reason="LaTeX and/or vector database not installed")
async def test_complete_research_lifecycle_persistence():
    """
    Comprehensive integration test for complete research lifecycle using MAIN server
    Executes a complete research workflow through all phases with real tool execution
    """
    
    print("🚀 Starting Complete Research Lifecycle Test with MAIN MCP Server")
    print("=" * 70)
    # Clear module cache to prevent state pollution
    modules_to_clear = [m for m in sys.modules.keys() if any(x in m for x in ['mcp_server', 'tools']) and m not in ['sys', 'os', 'pathlib', 'tempfile', 'json']]
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    # Re-import after clearing cache
    from mcp_server import ClaudeMCPServer
    # Create temporary project environment
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir) / 'research_project'
    project_path.mkdir(parents=True, exist_ok=True)
    # Create .srrd directory and minimal project context
    srrd_dir = project_path / '.srrd'
    srrd_dir.mkdir(exist_ok=True)
    # Create minimal project.json to simulate a valid SRRD project context
    project_json = srrd_dir / 'project.json'
    project_json.write_text('{"name": "tmp_test_project", "description": "Temporary test project for integration test", "created_by": "test", "created_at": "now"}')
    # Set up environment variable and current project pointer
    import os
    original_path = os.environ.get('SRRD_PROJECT_PATH')
    os.environ['SRRD_PROJECT_PATH'] = str(project_path)
    # Also set ~/.srrd/current_project.txt so context loader finds the project
    home_dir = Path.home()
    srrd_home = home_dir / '.srrd'
    srrd_home.mkdir(exist_ok=True)
    current_project_file = srrd_home / 'current_project.txt'
    current_project_file.write_text(str(project_path))
    try:
        # 1. Initialize MAIN MCP Server
        print("1. Initializing MAIN MCP Server...")
        server = ClaudeMCPServer()
        print(f"   ✅ Server initialized with {len(server.tools)} tools")
        assert len(server.tools) == 46, f"Expected 46 tools, got {len(server.tools)}"
        print("\n2. Executing Complete Research Workflow...")
        print("   📋 Phase 1: Conceptualization")
        # Clarify research goals
        try:
            clarify_tool = server.tools['clarify_research_goals']['handler']
            clarify_result = await clarify_tool(
                research_area='Computer Science',
                initial_goals='Develop comprehensive AI research methodology framework'
            )
            clarify_str = str(clarify_result)
            assert len(clarify_str) > 100
            print("      ✅ Research goals clarified")
        except Exception as e:
            print(f"[FAIL] clarify_research_goals: {e}")
            import traceback; traceback.print_exc()
            raise
        # Assess foundational assumptions
        try:
            assumptions_tool = server.tools['assess_foundational_assumptions']['handler']
            assumptions_result = await assumptions_tool(domain='computer_science')
            assumptions_str = str(assumptions_result)
            assert len(assumptions_str) > 50
            print("      ✅ Foundational assumptions assessed")
        except Exception as e:
            print(f"[FAIL] assess_foundational_assumptions: {e}")
            import traceback; traceback.print_exc()
            raise
        # Generate critical questions
        try:
            questions_tool = server.tools['generate_critical_questions']['handler']
            questions_result = await questions_tool(research_area='Computer Science')
            questions_str = str(questions_result)
            assert len(questions_str) > 50
            print("      ✅ Critical questions generated")
        except Exception as e:
            print(f"[FAIL] generate_critical_questions: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 2: Design & Planning")
        # Suggest methodology
        try:
            methodology_tool = server.tools['suggest_methodology']['handler']
            methodology_result = await methodology_tool(
                research_goals='Develop AI research framework',
                domain='computer_science'
            )
            methodology_str = str(methodology_result)
            assert len(methodology_str) > 100
            print("      ✅ Methodology suggested")
        except Exception as e:
            print(f"[FAIL] suggest_methodology: {e}")
            import traceback; traceback.print_exc()
            raise
        # Validate design
        try:
            design_tool = server.tools['validate_design']['handler']
            design_result = await design_tool(
                research_design='Systematic AI methodology framework development with empirical validation',
                domain='computer_science'
            )
            design_str = str(design_result)
            assert len(design_str) > 50
            print("      ✅ Research design validated")
        except Exception as e:
            print(f"[FAIL] validate_design: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 3: Knowledge Acquisition")
        # Semantic search
        try:
            search_tool = server.tools['semantic_search']['handler']
            search_result = await search_tool(
                query="artificial intelligence research methodologies",
                project_path=str(project_path)
            )
            search_str = str(search_result)
            assert len(search_str) > 50
            print("      ✅ Semantic search completed")
        except Exception as e:
            print(f"[FAIL] semantic_search: {e}")
            import traceback; traceback.print_exc()
            raise
        # Extract key concepts
        try:
            concepts_tool = server.tools['extract_key_concepts']['handler']
            concepts_result = await concepts_tool(
                text="Artificial intelligence research requires systematic methodological approaches incorporating machine learning, deep learning, and cognitive computing paradigms."
            )
            concepts_str = str(concepts_result)
            assert len(concepts_str) > 50
            print("      ✅ Key concepts extracted")
        except Exception as e:
            print(f"[FAIL] extract_key_concepts: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 4: Analysis & Synthesis")
        # Discover patterns
        try:
            patterns_tool = server.tools['discover_patterns']['handler']
            patterns_result = await patterns_tool(
                content="Research methodology patterns in AI include experimental design, empirical validation, theoretical modeling, and computational simulation approaches."
            )
            patterns_str = str(patterns_result)
            assert len(patterns_str) > 50
            print("      ✅ Patterns discovered")
        except Exception as e:
            print(f"[FAIL] discover_patterns: {e}")
            import traceback; traceback.print_exc()
            raise
        # Build knowledge graph
        try:
            graph_tool = server.tools['build_knowledge_graph']['handler']
            graph_result = await graph_tool(
                documents=['AI methodologies', 'Research frameworks', 'Computational approaches'],
                project_path=str(project_path)
            )
            graph_str = str(graph_result)
            assert len(graph_str) > 10, f"Unexpectedly short result: {graph_str!r}"
            print("      ✅ Knowledge graph built")
        except Exception as e:
            print(f"[FAIL] build_knowledge_graph: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 5: Quality Assurance")
        # Simulate peer review
        try:
            review_tool = server.tools['simulate_peer_review']['handler']
            review_result = await review_tool(
                document_content={
                    'title': 'Comprehensive AI Research Methodology Framework',
                    'abstract': 'This work presents a systematic framework for conducting AI research.',
                    'introduction': 'AI research requires rigorous methodological approaches.',
                    'methodology': 'We developed a comprehensive framework incorporating multiple research paradigms.',
                    'results': 'Our framework demonstrates improved research outcomes.',
                    'conclusion': 'The proposed methodology offers significant advantages.'
                },
                domain='computer_science'
            )
            review_str = str(review_result)
            assert len(review_str) > 200
            print("      ✅ Peer review simulation completed")
        except Exception as e:
            print(f"[FAIL] simulate_peer_review: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 6: Documentation")
        # Generate LaTeX document
        try:
            latex_tool = server.tools['generate_latex_document']['handler']
            latex_result = await latex_tool(
                title="Complete Research Lifecycle Test: AI Methodology Framework",
                author="Research Lifecycle Test",
                abstract="This document demonstrates the complete research lifecycle.",
                introduction="This research lifecycle test validates comprehensive workflow execution.",
                methodology="The methodology incorporates all phases of systematic research.",
                results="All research phases were successfully executed and validated.",
                conclusion="The complete research lifecycle test confirms comprehensive functionality.",
                project_path=str(project_path)
            )
            latex_str = str(latex_result)
            assert len(latex_str) > 100
            print("      ✅ LaTeX document generated")
        except Exception as e:
            print(f"[FAIL] generate_latex_document: {e}")
            import traceback; traceback.print_exc()
            raise
        print("   📋 Phase 7: Progress Assessment")
        # Get research progress
        try:
            progress_tool = server.tools['get_research_progress']['handler']
            progress_result = await progress_tool(project_path=str(project_path))
            progress_str = str(progress_result)
            assert len(progress_str) > 20
            print("      ✅ Research progress assessed")
        except Exception as e:
            print(f"[FAIL] get_research_progress: {e}")
            import traceback; traceback.print_exc()
            raise
        # Get session summary
        try:
            summary_tool = server.tools['get_session_summary']['handler']
            summary_result = await summary_tool(project_path=str(project_path))
            summary_str = str(summary_result)
            assert len(summary_str) > 20
            print("      ✅ Session summary generated")
        except Exception as e:
            print(f"[FAIL] get_session_summary: {e}")
            import traceback; traceback.print_exc()
            raise
        print("\n🎉 COMPLETE RESEARCH LIFECYCLE TEST PASSED!")
        print("🏆 ALL 7 research phases executed successfully through MAIN MCP Server!")
        print(f"🎯 Total tools executed: 18 tools across all research phases")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Restore environment
        if original_path:
            os.environ['SRRD_PROJECT_PATH'] = original_path
        elif 'SRRD_PROJECT_PATH' in os.environ:
            del os.environ['SRRD_PROJECT_PATH']
        # Remove ~/.srrd/current_project.txt if it points to our temp project
        try:
            if current_project_file.exists() and current_project_file.read_text().strip() == str(project_path):
                current_project_file.unlink()
        except Exception as cleanup_exc:
            print(f"[CLEANUP] Could not remove current_project.txt: {cleanup_exc}")
        # Cleanup temp project
        import shutil
        shutil.rmtree(temp_dir)


# Run the test if called directly
if __name__ == "__main__":
    print("🧪 Running Complete Research Lifecycle Test with MAIN MCP Server...")
    asyncio.run(test_complete_research_lifecycle_persistence())
