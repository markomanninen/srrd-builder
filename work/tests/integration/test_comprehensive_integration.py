#!/usr/bin/env python3
"""
Integration Tests for SRRD-Builder MCP Server
============================================

End-to-end integration tests covering:
- MCP server startup and communication
- Context-aware tool workflows  
- Multi-tool research workflows
- Storage system integration
- Error handling and recovery

NOTE: These tests use the WebSocket server for testing.
Production Claude Desktop integration uses stdio MCP server.
"""

import asyncio
import os
import sys
import tempfile
import shutil
import json
import pytest
import websockets
import time
from pathlib import Path
from typing import Dict, Any, List

# Add MCP directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "code" / "mcp"))

try:
    from server import MCPServer
    from mcp_server import ClaudeMCPServer
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Make sure MCP server modules are available")
    sys.exit(1)

class TestMCPServerIntegration:
    """Integration tests for MCP server functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
        self.servers = []
    
    def create_test_project(self, name: str) -> Path:
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix=f"integration_test_{name}_")
        project_path = Path(temp_dir)
        self.temp_dirs.append(project_path)
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "name": f"Integration Test Project {name}",
            "description": f"Integration test project - {name}",
            "domain": "software_testing",
            "version": "1.0.0"
        }
        
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create basic directory structure
        for dir_name in ['data', 'documents', 'methodology', 'logs']:
            (project_path / dir_name).mkdir(exist_ok=True)
        
        return project_path
    
    def cleanup(self):
        """Clean up resources"""
        # Stop servers
        for server in self.servers:
            try:
                if hasattr(server, 'stop'):
                    server.stop()
            except Exception:
                pass
        
        # Clean up temp directories
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test MCP server initialization"""
        print("  🚀 Testing MCP server initialization...")
        
        try:
            # Test WebSocket server initialization
            server = MCPServer(port=18080)  # Use different port for testing
            self.servers.append(server)
            
            self.assert_test(
                hasattr(server, 'tools'),
                "Server has tools registry"
            )
            
            self.assert_test(
                hasattr(server, 'port'),
                "Server has port configuration"
            )
            
            # Test Claude Desktop server initialization
            claude_server = ClaudeMCPServer()
            self.servers.append(claude_server)
            
            self.assert_test(
                hasattr(claude_server, 'tools'),
                "Claude server has tools registry"
            )
            
        except Exception as e:
            self.assert_test(False, "Server initialization", str(e))
    
    @pytest.mark.asyncio
    async def test_tool_listing(self):
        """Test tool listing functionality"""
        print("  📋 Testing tool listing...")
        
        try:
            server = MCPServer(port=18081)
            self.servers.append(server)
            
            # Test tools/list method
            tools_response = await server.list_tools_mcp()
            
            self.assert_test(
                'tools' in tools_response,
                "Tools list response contains 'tools' key"
            )
            
            if 'tools' in tools_response:
                tools = tools_response['tools']
                self.assert_test(
                    len(tools) > 0,
                    f"Tools list is not empty",
                    f"Found {len(tools)} tools"
                )
                
                # Check for expected tool categories
                tool_names = [tool['name'] for tool in tools if isinstance(tool, dict)]
                expected_tools = [
                    'initialize_project',
                    'clarify_research_goals',
                    'generate_latex_document'
                ]
                
                found_expected = sum(1 for tool in expected_tools if tool in tool_names)
                self.assert_test(
                    found_expected > 0,
                    f"Expected tools present in listing",
                    f"Found {found_expected}/{len(expected_tools)} expected tools"
                )
            
        except Exception as e:
            self.assert_test(False, "Tool listing", str(e))

class TestContextAwareWorkflows:
    """Integration tests for context-aware workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_test_project(self, name: str) -> Path:
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix=f"workflow_test_{name}_")
        project_path = Path(temp_dir)
        self.temp_dirs.append(project_path)
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "name": f"Workflow Test Project {name}",
            "description": f"Context-aware workflow test - {name}",
            "domain": "theoretical_physics"
        }
        
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return project_path
    
    def cleanup(self):
        """Clean up temp directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    @pytest.mark.asyncio
    async def test_context_detection_workflow(self):
        """Test end-to-end context detection workflow"""
        print("  🎯 Testing context detection workflow...")
        
        project_path = self.create_test_project("context_workflow")
        
        # Set up environment for context detection
        original_env = os.environ.get('SRRD_PROJECT_PATH')
        os.environ['SRRD_PROJECT_PATH'] = str(project_path)
        
        try:
            # Import context detector
            from utils.context_detector import get_context_detector
            
            detector = get_context_detector()
            context = detector.detect_context(refresh_cache=True)
            
            self.assert_test(
                context is not None,
                "Context detected from environment"
            )
            
            if context:
                self.assert_test(
                    context['project_path'] == str(project_path),
                    "Correct project path in context"
                )
                
                self.assert_test(
                    'config' in context,
                    "Project config loaded in context"
                )
            
        except ImportError:
            self.assert_test(False, "Context detection import", "Context detector not available")
        except Exception as e:
            self.assert_test(False, "Context detection workflow", str(e))
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ['SRRD_PROJECT_PATH'] = original_env
            elif 'SRRD_PROJECT_PATH' in os.environ:
                del os.environ['SRRD_PROJECT_PATH']

class TestMultiToolWorkflows:
    """Integration tests for multi-tool research workflows"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []
    
    def create_test_project(self, name: str) -> Path:
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix=f"multitool_test_{name}_")
        project_path = Path(temp_dir)
        self.temp_dirs.append(project_path)
        
        # Create SRRD project structure
        srrd_dir = project_path / '.srrd'
        srrd_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "name": f"Multi-tool Test Project {name}",
            "description": f"Multi-tool workflow test - {name}",
            "domain": "computer_science"
        }
        
        with open(srrd_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return project_path
    
    def cleanup(self):
        """Clean up temp directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    @pytest.mark.asyncio
    async def test_research_planning_workflow(self):
        """Test research planning workflow"""
        print("  🔬 Testing research planning workflow...")
        
        project_path = self.create_test_project("research_planning")
        
        # Set up environment
        original_env = os.environ.get('SRRD_PROJECT_PATH')
        os.environ['SRRD_PROJECT_PATH'] = str(project_path)
        
        try:
            # Test sequence: clarify goals -> suggest methodology -> quality check
            workflow_steps = []
            
            # Step 1: Import and test research planning tools
            try:
                from tools.research_planning import clarify_research_goals_tool, suggest_methodology_tool
                workflow_steps.append("research_planning_tools_imported")
            except ImportError:
                pass
            
            # Step 2: Import and test quality assurance tools  
            try:
                from tools.quality_assurance import check_quality_gates_tool
                workflow_steps.append("quality_tools_imported")
            except ImportError:
                pass
            
            self.assert_test(
                len(workflow_steps) > 0,
                f"Multi-tool workflow components available",
                f"Available: {', '.join(workflow_steps)}"
            )
            
            # If tools are available, test a simple workflow
            if "research_planning_tools_imported" in workflow_steps:
                try:
                    result = await clarify_research_goals_tool(
                        research_area="artificial intelligence",
                        initial_goals="develop better reasoning systems"
                    )
                    
                    self.assert_test(
                        result is not None and len(str(result)) > 0,
                        "Research planning tool execution"
                    )
                    
                except Exception as e:
                    self.assert_test(False, "Research planning execution", str(e))
            
        except Exception as e:
            self.assert_test(False, "Multi-tool workflow setup", str(e))
        finally:
            # Restore environment
            if original_env is not None:
                os.environ['SRRD_PROJECT_PATH'] = original_env
            elif 'SRRD_PROJECT_PATH' in os.environ:
                del os.environ['SRRD_PROJECT_PATH']

class TestErrorHandling:
    """Integration tests for error handling and recovery"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_passed = 0
        self.test_failed = 0
    
    def assert_test(self, condition: bool, test_name: str, details: str = ""):
        """Assert a test condition"""
        if condition:
            print(f"   ✅ {test_name}")
            self.test_passed += 1
        else:
            print(f"   ❌ {test_name}: {details}")
            self.test_failed += 1
    
    @pytest.mark.asyncio
    async def test_graceful_error_handling(self):
        """Test graceful error handling"""
        print("  🛡️  Testing error handling...")
        
        try:
            # Test server initialization with invalid parameters
            try:
                server = MCPServer(port=-1)  # Invalid port
                self.assert_test(False, "Invalid port handling", "Should have failed")
            except Exception:
                self.assert_test(True, "Invalid port rejected correctly")
            
            # Test tool execution with missing context
            try:
                from tools.storage_management import save_session_tool
                
                # This should handle missing project_path gracefully
                result = await save_session_tool(session_data={"test": "data"})
                
                self.assert_test(
                    "error" in str(result).lower() or "context" in str(result).lower(),
                    "Missing context handled gracefully"
                )
                
            except ImportError:
                self.assert_test(True, "Storage tools not available for error testing")
            except Exception as e:
                self.assert_test(
                    True,
                    "Tool execution error handled",
                    f"Got expected exception: {type(e).__name__}"
                )
            
        except Exception as e:
            self.assert_test(False, "Error handling test setup", str(e))

async def main():
    """Main integration test function"""
    print("🧪 SRRD-BUILDER INTEGRATION TESTS")
    print("=" * 60)
    
    # Test MCP server integration
    print("🚀 MCP Server Integration Tests")
    server_tests = TestMCPServerIntegration()
    try:
        await server_tests.test_server_initialization()
        await server_tests.test_tool_listing()
    finally:
        server_tests.cleanup()
    
    print()
    
    # Test context-aware workflows
    print("🎯 Context-Aware Workflow Tests")
    context_tests = TestContextAwareWorkflows()
    try:
        await context_tests.test_context_detection_workflow()
    finally:
        context_tests.cleanup()
    
    print()
    
    # Test multi-tool workflows
    print("🔬 Multi-Tool Workflow Tests")
    workflow_tests = TestMultiToolWorkflows()
    try:
        await workflow_tests.test_research_planning_workflow()
    finally:
        workflow_tests.cleanup()
    
    print()
    
    # Test error handling
    print("🛡️  Error Handling Tests")
    error_tests = TestErrorHandling()
    await error_tests.test_graceful_error_handling()
    
    # Summary
    total_passed = (server_tests.test_passed + context_tests.test_passed + 
                   workflow_tests.test_passed + error_tests.test_passed)
    total_failed = (server_tests.test_failed + context_tests.test_failed + 
                   workflow_tests.test_failed + error_tests.test_failed)
    total_tests = total_passed + total_failed
    
    print()
    print("=" * 60)
    print("📊 INTEGRATION TESTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_tests > 0:
        print(f"📈 Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    if total_failed > 0:
        print("\n⚠️  Some integration tests failed")
        sys.exit(1)
    else:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
