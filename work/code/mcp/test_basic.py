"""
Basic functionality test for SRRD Builder MCP Server
Tests core components without complex dependencies
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

async def test_basic_imports():
    """Test that all modules can be imported"""
    print("Testing basic imports...")
    
    try:
        from config.config_manager import ConfigManager
        print("✓ ConfigManager imported successfully")
        
        from utils.logging_setup import setup_logging
        print("✓ Logging setup imported successfully")
        
        from storage.sqlite_manager import SQLiteManager
        print("✓ SQLiteManager imported successfully")
        
        from storage.git_manager import GitManager
        print("✓ GitManager imported successfully")
        
        # Test storage managers
        temp_dir = tempfile.mkdtemp()
        
        try:
            git_manager = GitManager(temp_dir)
            print("✓ GitManager initialized successfully")
            
            sqlite_manager = SQLiteManager(os.path.join(temp_dir, "test.db"))
            await sqlite_manager.initialize()
            print("✓ SQLiteManager initialized successfully")
            
        finally:
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

async def test_tools_import():
    """Test that all tools can be imported"""
    print("\nTesting tool imports...")
    
    try:
        from tools.research_planning import register_research_tools
        print("✓ Research planning tools imported")
        
        from tools.quality_assurance import register_quality_tools
        print("✓ Quality assurance tools imported")
        
        from tools.storage_management import register_storage_tools
        print("✓ Storage management tools imported")
        
        from tools.document_generation import register_document_tools
        print("✓ Document generation tools imported")
        
        from tools.search_discovery import register_search_tools
        print("✓ Search discovery tools imported")
        
        from tools import register_all_tools
        print("✓ All tools registration imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Tools import test failed: {e}")
        return False

async def test_server_basic():
    """Test basic server functionality"""
    print("\nTesting server initialization...")
    
    try:
        from server import MCPServer
        
        # Create server instance
        server = MCPServer(port=8082)
        print(f"✓ Server created with {len(server.tools)} tools")
        
        # Test tool listing
        tools_info = await server.list_tools()
        print(f"✓ Tools list generated: {tools_info.get('tool_count', 0)} tools")
        
        # Test a simple tool
        if "clarify_research_goals" in server.tools:
            result = await server.tools["clarify_research_goals"](
                research_area="quantum gravity",
                initial_goals="Develop alternative theory of quantum gravity",
                experience_level="undergraduate",
                domain_specialization="theoretical_physics"
            )
            print("✓ Research planning tool executed successfully")
        else:
            print("⚠ Research planning tool not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False

async def test_configuration():
    """Test configuration system"""
    print("\nTesting configuration system...")
    
    try:
        from config.config_manager import ConfigManager
        
        config = ConfigManager()
        print(f"✓ Configuration loaded from: {config.config_path}")
        
        # Test config validation
        issues = config.validate_config()
        print(f"✓ Configuration validated with {len(issues)} issues")
        
        # Test directory setup
        config.setup_directories()
        print("✓ Directories setup completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("=" * 60)
    print("SRRD Builder MCP Server - Basic Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Tools Import", test_tools_import),
        ("Server Basic", test_server_basic),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 All basic tests passed! The MCP server is functional.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
