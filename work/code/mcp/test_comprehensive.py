"""
Comprehensive test suite for SRRD Builder MCP Server
Tests all tools, storage components, and server functionality
"""

import asyncio
import json
import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from server import MCPServer
from storage.project_manager import ProjectManager
from storage.vector_manager import VectorManager
from config.config_manager import ConfigManager
from utils.logging_setup import setup_logging

class MCPTestSuite:
    """Comprehensive test suite for MCP server and tools"""
    
    def __init__(self):
        self.server = None
        self.test_project_path = None
        self.test_results = []
        
    async def setup_test_environment(self):
        """Setup test environment with temporary directories"""
        print("Setting up test environment...")
        
        # Create temporary directory for testing
        self.test_project_path = tempfile.mkdtemp(prefix="srrd_test_")
        print(f"Test project path: {self.test_project_path}")
        
        # Initialize server with test configuration
        self.server = MCPServer(port=8081)  # Use different port for testing
        
    async def cleanup_test_environment(self):
        """Clean up test environment"""
        print("Cleaning up test environment...")
        
        if self.test_project_path and os.path.exists(self.test_project_path):
            shutil.rmtree(self.test_project_path)
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"[{status}] {test_name}: {details}")
    
    async def test_server_initialization(self):
        """Test MCP server initialization"""
        try:
            # Test server creation
            assert self.server is not None
            assert len(self.server.tools) > 0
            
            # Test tool registration
            expected_tools = [
                "clarify_research_goals",
                "suggest_methodology",
                "simulate_peer_review",
                "check_quality_gates",
                "initialize_project",
                "generate_latex_document",
                "semantic_search"
            ]
            
            missing_tools = [tool for tool in expected_tools if tool not in self.server.tools]
            
            if missing_tools:
                self.log_test_result(
                    "Server Initialization", 
                    False, 
                    f"Missing tools: {missing_tools}"
                )
            else:
                self.log_test_result(
                    "Server Initialization", 
                    True, 
                    f"All {len(self.server.tools)} tools registered"
                )
        
        except Exception as e:
            self.log_test_result("Server Initialization", False, str(e))
    
    async def test_storage_components(self):
        """Test storage management components"""
        try:
            # Test ProjectManager initialization
            project_manager = ProjectManager(self.test_project_path)
            
            # Test project initialization
            result = project_manager.initialize_project(
                name="Test Project",
                description="Test project for MCP server",
                domain="theoretical_physics"
            )
            
            if "success" in result.lower():
                self.log_test_result("Project Initialization", True, "Project created successfully")
            else:
                self.log_test_result("Project Initialization", False, result)
            
            # Test vector manager
            vector_manager = VectorManager()
            self.log_test_result("Vector Manager", True, "Vector manager initialized")
            
        except Exception as e:
            self.log_test_result("Storage Components", False, str(e))
    
    async def test_research_planning_tools(self):
        """Test research planning tools"""
        try:
            # Test clarify_research_goals
            if "clarify_research_goals" in self.server.tools:
                result = await self.server.tools["clarify_research_goals"](
                    goals="Develop alternative theory of quantum gravity",
                    current_understanding="Basic knowledge of general relativity and quantum mechanics",
                    domain="theoretical_physics",
                    research_level="phd"
                )
                
                if isinstance(result, dict) and "clarified_goals" in result:
                    self.log_test_result("Clarify Research Goals", True, "Goals clarified successfully")
                else:
                    self.log_test_result("Clarify Research Goals", False, "Unexpected result format")
            
            # Test suggest_methodology
            if "suggest_methodology" in self.server.tools:
                result = await self.server.tools["suggest_methodology"](
                    research_area="quantum gravity",
                    domain="theoretical_physics",
                    novel_theory_flag=True,
                    constraints={"time_frame": "2_years", "resources": "theoretical_only"}
                )
                
                if isinstance(result, dict) and "recommended_methodologies" in result:
                    self.log_test_result("Suggest Methodology", True, "Methodology suggestions generated")
                else:
                    self.log_test_result("Suggest Methodology", False, "Unexpected result format")
        
        except Exception as e:
            self.log_test_result("Research Planning Tools", False, str(e))
    
    async def test_quality_assurance_tools(self):
        """Test quality assurance tools"""
        try:
            # Test simulate_peer_review
            if "simulate_peer_review" in self.server.tools:
                result = await self.server.tools["simulate_peer_review"](
                    content={
                        "abstract": "A novel approach to quantum gravity",
                        "methodology": "Mathematical analysis and theoretical modeling",
                        "results": "New framework for understanding quantum spacetime"
                    },
                    domain="theoretical_physics",
                    review_criteria=["originality", "rigor", "clarity"],
                    novel_theory_considerations=True
                )
                
                if isinstance(result, dict) and "overall_assessment" in result:
                    self.log_test_result("Simulate Peer Review", True, "Peer review completed")
                else:
                    self.log_test_result("Simulate Peer Review", False, "Unexpected result format")
            
            # Test check_quality_gates
            if "check_quality_gates" in self.server.tools:
                result = await self.server.tools["check_quality_gates"](
                    research_content={"title": "Test Research", "abstract": "Test abstract"},
                    phase="planning"
                )
                
                if isinstance(result, dict) and "passed" in result:
                    self.log_test_result("Check Quality Gates", True, "Quality gates checked")
                else:
                    self.log_test_result("Check Quality Gates", False, "Unexpected result format")
        
        except Exception as e:
            self.log_test_result("Quality Assurance Tools", False, str(e))
    
    async def test_document_generation_tools(self):
        """Test document generation tools"""
        try:
            # Test LaTeX document generation
            if "generate_latex_document" in self.server.tools:
                result = await self.server.tools["generate_latex_document"](
                    title="Test Research Document",
                    author="Test Author",
                    abstract="This is a test abstract for document generation",
                    introduction="This is the introduction section",
                    project_path=self.test_project_path
                )
                
                if "successfully" in str(result).lower():
                    self.log_test_result("Generate LaTeX Document", True, "Document generated")
                else:
                    self.log_test_result("Generate LaTeX Document", False, str(result))
            
            # Test format_research_content
            if "format_research_content" in self.server.tools:
                result = await self.server.tools["format_research_content"](
                    content="This is test content that needs formatting",
                    content_type="section",
                    formatting_style="academic"
                )
                
                if "Formatted" in str(result):
                    self.log_test_result("Format Research Content", True, "Content formatted")
                else:
                    self.log_test_result("Format Research Content", False, str(result))
        
        except Exception as e:
            self.log_test_result("Document Generation Tools", False, str(e))
    
    async def test_search_discovery_tools(self):
        """Test search and discovery tools"""
        try:
            # Test semantic search
            if "semantic_search" in self.server.tools:
                result = await self.server.tools["semantic_search"](
                    query="quantum gravity research",
                    collection="research_docs",
                    limit=5,
                    project_path=self.test_project_path
                )
                
                if "results" in str(result).lower():
                    self.log_test_result("Semantic Search", True, "Search completed")
                else:
                    self.log_test_result("Semantic Search", False, str(result))
            
            # Test discover patterns
            if "discover_patterns" in self.server.tools:
                result = await self.server.tools["discover_patterns"](
                    content="This is research content about quantum mechanics and general relativity theory",
                    pattern_type="research_themes",
                    min_frequency=1
                )
                
                if "patterns" in str(result).lower():
                    self.log_test_result("Discover Patterns", True, "Patterns discovered")
                else:
                    self.log_test_result("Discover Patterns", False, str(result))
        
        except Exception as e:
            self.log_test_result("Search Discovery Tools", False, str(e))
    
    async def test_storage_management_tools(self):
        """Test storage management tools"""
        try:
            # Test initialize_project
            if "initialize_project" in self.server.tools:
                result = await self.server.tools["initialize_project"](
                    name="Test Storage Project",
                    description="Testing storage management",
                    domain="theoretical_physics",
                    project_path=self.test_project_path
                )
                
                if "status" in str(result).lower():
                    self.log_test_result("Initialize Project Tool", True, "Project initialized")
                else:
                    self.log_test_result("Initialize Project Tool", False, str(result))
        
        except Exception as e:
            self.log_test_result("Storage Management Tools", False, str(e))
    
    async def test_configuration_system(self):
        """Test configuration management"""
        try:
            # Test config loading
            config_manager = ConfigManager()
            
            # Test configuration validation
            issues = config_manager.validate_config()
            
            # Test directory creation
            config_manager.setup_directories()
            
            self.log_test_result("Configuration System", True, f"Config loaded with {len(issues)} issues")
        
        except Exception as e:
            self.log_test_result("Configuration System", False, str(e))
    
    async def run_all_tests(self):
        """Run all tests in the test suite"""
        print("=" * 60)
        print("SRRD Builder MCP Server - Comprehensive Test Suite")
        print("=" * 60)
        
        await self.setup_test_environment()
        
        try:
            # Run all test categories
            await self.test_server_initialization()
            await self.test_storage_components()
            await self.test_research_planning_tools()
            await self.test_quality_assurance_tools()
            await self.test_document_generation_tools()
            await self.test_search_discovery_tools()
            await self.test_storage_management_tools()
            await self.test_configuration_system()
            
        finally:
            await self.cleanup_test_environment()
        
        # Print test summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        if failed > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            print(f"  {status_symbol} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")

async def main():
    """Main test runner"""
    test_suite = MCPTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
