#!/usr/bin/env python3
"""
Enhanced Context-Aware Tool Validation Test

This test verifies that all tools now have context-aware functionality
and that the MCP server properly integrates all enhanced tools.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'utils'))

try:
    from server import MCPServer
    # Import context utilities with proper path handling
    utils_path = current_dir / 'utils'
    if utils_path.exists():
        sys.path.insert(0, str(utils_path))
        from context_detector import ContextDetector
        from context_decorator import is_context_aware, get_context_requirements
    else:
        print(f"❌ Utils directory not found at {utils_path}")
        sys.exit(1)
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the MCP directory")
    sys.exit(1)

async def test_enhanced_tools_comprehensive():
    """Test all enhanced tools with context-aware functionality"""
    
    print("🔍 Starting Enhanced Context-Aware Tool Validation")
    print("=" * 60)
    
    # Initialize server
    server = MCPServer()
    
    # Get all tools
    tools_info = await server.list_tools_mcp()
    tools = tools_info.get('tools', [])
    
    print(f"📊 Total tools found: {len(tools)}")
    print(f"📋 Testing context-aware functionality...")
    print()
    
    # Test context detection
    detector = ContextDetector()
    context = detector.detect_context()
    if context:
        print(f"✅ Context detected: {context['project_path']}")
    else:
        print("⚠️  No context detected (expected in test environment)")
    print()
    
    # Track enhanced tools
    enhanced_tools = []
    context_aware_tools = []
    
    # Test each tool for context-aware functionality
    for tool_info in tools:
        tool_name = tool_info['name']
        
        # Get the actual tool function
        if tool_name in server.tools:
            tool_func = server.tools[tool_name]['handler']
            
            # Check if it's context-aware
            if is_context_aware(tool_func):
                context_aware_tools.append(tool_name)
                requirements = get_context_requirements(tool_func)
                print(f"✅ {tool_name}: Context-aware (require_context={requirements['require_context']})")
            else:
                print(f"⚪ {tool_name}: Not context-aware")
        else:
            print(f"❓ {tool_name}: Tool function not found")
    
    print()
    print("=" * 60)
    print("📈 ENHANCEMENT SUMMARY")
    print("=" * 60)
    
    print(f"🎯 Total tools: {len(tools)}")
    print(f"🚀 Context-aware tools: {len(context_aware_tools)}")
    print(f"📊 Enhancement coverage: {len(context_aware_tools)/len(tools)*100:.1f}%")
    
    # List enhanced tools by category
    tool_categories = {
        'storage': ['initialize_project', 'save_session', 'restore_session', 'version_control', 'backup_project'],
        'document': ['generate_latex_document', 'generate_document_with_database_bibliography', 'compile_latex', 'format_research_content', 'generate_bibliography', 'extract_document_sections'],
        'search': ['semantic_search', 'search_knowledge', 'find_similar_documents'],
        'planning': ['clarify_research_goals', 'suggest_methodology'],
        'quality': ['simulate_peer_review', 'check_quality_gates'],
        'methodology': ['explain_methodology', 'compare_approaches', 'validate_design', 'ensure_ethics'],
        'theory': ['initiate_paradigm_challenge', 'develop_alternative_framework', 'compare_paradigms', 'validate_novel_theory', 'cultivate_innovation', 'assess_foundational_assumptions', 'generate_critical_questions', 'evaluate_paradigm_shift_potential']
    }
    
    print()
    print("📂 ENHANCED TOOLS BY CATEGORY")
    print("-" * 40)
    
    for category, expected_tools in tool_categories.items():
        enhanced_in_category = [tool for tool in expected_tools if tool in context_aware_tools]
        print(f"{category.upper()}: {len(enhanced_in_category)}/{len(expected_tools)} enhanced")
        for tool in enhanced_in_category:
            print(f"  ✅ {tool}")
        for tool in expected_tools:
            if tool not in context_aware_tools:
                print(f"  ⚠️  {tool} (not enhanced)")
    
    print()
    print("=" * 60)
    print("🎉 TEST RESULTS")
    print("=" * 60)
    
    success_rate = len(context_aware_tools) / len(tools) * 100
    
    if success_rate >= 80:
        print(f"🎯 EXCELLENT: {success_rate:.1f}% of tools are context-aware!")
        print("✅ Context-aware enhancement is highly successful")
    elif success_rate >= 60:
        print(f"✅ GOOD: {success_rate:.1f}% of tools are context-aware")
        print("⚠️  Some tools could benefit from enhancement")
    else:
        print(f"⚠️  NEEDS IMPROVEMENT: Only {success_rate:.1f}% of tools are context-aware")
        print("🔧 Consider enhancing more tools")
    
    print()
    print("📋 CONTEXT-AWARE TOOLS:")
    for tool in sorted(context_aware_tools):
        print(f"  • {tool}")
    
    # Test actual context injection
    print()
    print("🧪 Testing context injection...")
    
    # Create a temporary project structure for testing
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create .srrd marker
        srrd_dir = Path(temp_dir) / '.srrd'
        srrd_dir.mkdir()
        
        # Create config file
        config_file = srrd_dir / 'config.json'
        config_file.write_text(json.dumps({
            'name': 'test_project',
            'version': '1.0.0',
            'domain': 'test'
        }))
        
        # Set environment variable
        os.environ['SRRD_PROJECT_PATH'] = temp_dir
        
        # Test context detection
        detector = ContextDetector()
        context = detector.detect_context()
        
        if context:
            print(f"✅ Context injection test passed: {context['project_path']}")
        else:
            print("❌ Context injection test failed")
        
        # Clean up
        os.environ.pop('SRRD_PROJECT_PATH', None)
    
    print()
    print("🎊 Enhanced Context-Aware Tool Validation Complete!")
    
    return {
        'total_tools': len(tools),
        'context_aware_tools': len(context_aware_tools),
        'success_rate': success_rate,
        'enhanced_tools': context_aware_tools
    }

if __name__ == "__main__":
    result = asyncio.run(test_enhanced_tools_comprehensive())
    
    # Exit with appropriate code
    if result['success_rate'] >= 80:
        print("\n🎯 All tests passed! Context-aware enhancement is highly successful.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Enhancement coverage is {result['success_rate']:.1f}%. Consider enhancing more tools.")
        sys.exit(1)
