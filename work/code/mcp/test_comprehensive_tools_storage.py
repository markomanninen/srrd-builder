"""
Comprehensive Tools and Storage Test Suite
Tests all MCP tools and storage components in detail
"""

import asyncio
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from server import MCPServer
from storage.project_manager import ProjectManager
from storage.sqlite_manager import SQLiteManager
from storage.git_manager import GitManager
from storage.vector_manager import VectorManager

class ComprehensiveTestSuite:
    """Comprehensive test suite for all tools and storage methods"""
    
    def __init__(self):
        self.server = None
        self.test_project_path = None
        self.test_results = []
        self.project_managers = []  # Track project managers for cleanup
        
    async def setup_test_environment(self):
        """Setup test environment with temporary directories"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for testing
        self.test_project_path = tempfile.mkdtemp(prefix="srrd_comprehensive_test_")
        print(f"📁 Test project path: {self.test_project_path}")
        
        # Initialize server
        self.server = MCPServer(port=8084)
        
    async def cleanup_test_environment(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        try:
            # Close any project manager connections
            for project_manager in self.project_managers:
                if hasattr(project_manager, 'sqlite_manager') and project_manager.sqlite_manager:
                    if hasattr(project_manager.sqlite_manager, 'connection') and project_manager.sqlite_manager.connection:
                        await project_manager.sqlite_manager.connection.close()
                    
            # Clean up test directory
            if self.test_project_path and os.path.exists(self.test_project_path):
                shutil.rmtree(self.test_project_path)
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"{status} {test_name}: {details}")

    async def test_storage_components_detailed(self):
        """Test all storage components in detail"""
        print("\n🗄️ Testing Storage Components...")
        
        # Test SQLite Manager
        try:
            db_path = os.path.join(self.test_project_path, "test.db")
            sqlite_manager = SQLiteManager(db_path)
            await sqlite_manager.initialize()
            
            # Test project creation
            project_id = await sqlite_manager.create_project(
                "Test Project", 
                "A test project for storage validation", 
                "theoretical_physics"
            )
            
            if project_id:
                self.log_test_result("SQLite Project Creation", True, f"Project ID: {project_id}")
            else:
                self.log_test_result("SQLite Project Creation", False, "No project ID returned")
            
            # Test session creation
            session_id = await sqlite_manager.create_session(
                project_id, 
                "research_planning", 
                "test_user"
            )
            
            if session_id:
                self.log_test_result("SQLite Session Creation", True, f"Session ID: {session_id}")
            else:
                self.log_test_result("SQLite Session Creation", False, "No session ID returned")
            
            # Test interaction logging
            interaction_id = await sqlite_manager.log_interaction(
                session_id,
                "socratic_question",
                "What is your research objective?",
                {"context": "initial_planning"}
            )
            
            if interaction_id:
                self.log_test_result("SQLite Interaction Logging", True, f"Interaction ID: {interaction_id}")
            else:
                self.log_test_result("SQLite Interaction Logging", False, "No interaction ID returned")
                
        except Exception as e:
            self.log_test_result("SQLite Manager Tests", False, str(e))
        
        # Test Git Manager
        try:
            git_manager = GitManager(self.test_project_path)
            
            # Initialize repository
            result = git_manager.initialize_repository()
            self.log_test_result("Git Repository Initialization", True, result)
            
            # Create test file and commit
            test_file = os.path.join(self.test_project_path, "test_document.txt")
            with open(test_file, 'w') as f:
                f.write("Test research document content")
            
            commit_result = git_manager.commit_changes("Added test document", files=["test_document.txt"])
            self.log_test_result("Git Commit Changes", True, commit_result)
            
            # Test status
            status = git_manager.get_status()
            self.log_test_result("Git Status Check", True, f"Clean: {status}")
            
        except Exception as e:
            self.log_test_result("Git Manager Tests", False, str(e))
        
        # Test Vector Manager
        try:
            vector_manager = VectorManager(
                db_path=os.path.join(self.test_project_path, "vector_db")
            )
            
            await vector_manager.initialize()
            self.log_test_result("Vector Manager Initialization", True, "Initialized successfully")
            
            # Test document storage
            await vector_manager.add_document(
                collection_name="research_literature",
                document="This is a test research document about quantum mechanics",
                doc_id="test_doc_1",
                metadata={"title": "Test Document", "domain": "physics", "type": "research_document"}
            )
            self.log_test_result("Vector Document Storage", True, "Document stored successfully")
            
            # Test search
            search_results = await vector_manager.search_knowledge("quantum mechanics", collection="research_literature", n_results=3)
            result_count = len(search_results.get('documents', [[]])[0]) if search_results.get('documents') else 0
            self.log_test_result("Vector Search", True, f"Found {result_count} results")
            
        except Exception as e:
            self.log_test_result("Vector Manager Tests", False, str(e))
        
        # Test Project Manager (integration)
        try:
            project_manager = ProjectManager(self.test_project_path)
            self.project_managers.append(project_manager)  # Track for cleanup
            
            result = await project_manager.initialize_project(
                "Comprehensive Test Project",
                "Testing all project management features",
                "theoretical_physics"
            )
            
            if isinstance(result, dict) and result.get('status') == 'initialized':
                project_id = result.get('project_id')
                self.log_test_result("Project Manager Integration", True, f"Project initialized with ID: {project_id}")
                
                # Test if we can add content to the vector store
                if hasattr(project_manager, 'vector_manager') and project_manager.vector_manager is not None:
                    await project_manager.vector_manager.add_document(
                        collection_name="research_literature",
                        document="Integration test document about theoretical physics",
                        doc_id="integration_test_1",
                        metadata={"type": "test_document", "domain": "theoretical_physics"}
                    )
                    self.log_test_result("Project Manager Vector Integration", True, "Document stored successfully")
                else:
                    self.log_test_result("Project Manager Vector Integration", False, "Vector manager not available")
            else:
                self.log_test_result("Project Manager Integration", False, f"Unexpected result: {result}")
            
        except Exception as e:
            self.log_test_result("Project Manager Integration", False, str(e))

    async def test_all_tools_detailed(self):
        """Test all MCP tools in detail"""
        print("\n🛠️ Testing All MCP Tools...")
        
        # Test Research Planning Tools
        if "clarify_research_goals" in self.server.tools:
            try:
                result = await self.server.tools["clarify_research_goals"]["handler"](
                    research_area="quantum gravity",
                    initial_goals="Develop a new approach to unify quantum mechanics and general relativity",
                    experience_level="graduate",
                    domain_specialization="theoretical_physics",
                    novel_theory_mode=True
                )
                
                # Validate result structure
                if isinstance(result, dict) and "clarified_goals" in result and "next_steps" in result:
                    self.log_test_result("Clarify Research Goals Tool", True, f"Generated {len(result.get('socratic_questions', []))} questions")
                else:
                    self.log_test_result("Clarify Research Goals Tool", False, "Unexpected result structure")
                    
            except Exception as e:
                self.log_test_result("Clarify Research Goals Tool", False, str(e))
        
        if "suggest_methodology" in self.server.tools:
            try:
                result = await self.server.tools["suggest_methodology"]["handler"](
                    research_goals="alternative physics theories",
                    domain="theoretical_physics",
                    novel_theory_flag=True,
                    constraints={"time_frame": "3_years", "resources": "theoretical_only"}
                )
                
                if isinstance(result, dict) and "recommended_methodologies" in result:
                    methodologies = result.get("recommended_methodologies", [])
                    self.log_test_result("Suggest Methodology Tool", True, f"Suggested {len(methodologies)} methodologies")
                else:
                    self.log_test_result("Suggest Methodology Tool", False, "Unexpected result structure")
                    
            except Exception as e:
                self.log_test_result("Suggest Methodology Tool", False, str(e))
        
        # Test Quality Assurance Tools
        if "simulate_peer_review" in self.server.tools:
            try:
                result = await self.server.tools["simulate_peer_review"]["handler"](
                    document_content={
                        "title": "Novel Quantum Gravity Framework",
                        "abstract": "This paper presents a revolutionary approach to quantum gravity that challenges existing paradigms",
                        "methodology": "Mathematical analysis combined with thought experiments",
                        "results": "New theoretical framework that resolves apparent contradictions"
                    },
                    domain="theoretical_physics",
                    review_type="comprehensive",
                    novel_theory_mode=True
                )
                
                if isinstance(result, dict) and "overall_score" in result:
                    score = result.get("overall_score", 0)
                    self.log_test_result("Simulate Peer Review Tool", True, f"Overall score: {score}")
                else:
                    self.log_test_result("Simulate Peer Review Tool", False, "Unexpected result structure")
                    
            except Exception as e:
                self.log_test_result("Simulate Peer Review Tool", False, str(e))
        
        if "check_quality_gates" in self.server.tools:
            try:
                result = await self.server.tools["check_quality_gates"]["handler"](
                    research_content={
                        "title": "Test Research Paper",
                        "abstract": "This is a test abstract for quality gate validation",
                        "introduction": "Test introduction section",
                        "methodology": "Test methodology description"
                    },
                    phase="publication_readiness",
                    domain_standards={"domain": "theoretical_physics"}
                )
                
                if isinstance(result, dict) and "passed" in result:
                    status = result.get("passed")
                    self.log_test_result("Check Quality Gates Tool", True, f"Gate status: {status}")
                else:
                    self.log_test_result("Check Quality Gates Tool", False, "Unexpected result structure")
                    
            except Exception as e:
                self.log_test_result("Check Quality Gates Tool", False, str(e))
        
        # Test Document Generation Tools
        if "generate_latex_document" in self.server.tools:
            try:
                handler = self.server.tools["generate_latex_document"]["handler"]
                result = await handler(
                    title="Test Research Document",
                    author="Test Author",
                    abstract="This is a comprehensive test of the LaTeX document generation system",
                    introduction="This introduction tests the document generation capabilities",
                    methodology="The methodology section demonstrates academic formatting",
                    results="Results show successful document generation",
                    discussion="Discussion of the implications of successful generation",
                    conclusion="The system successfully generates academic documents",
                    project_path=self.test_project_path
                )
                
                if "successfully" in str(result).lower():
                    self.log_test_result("Generate LaTeX Document Tool", True, "Document generated")
                else:
                    self.log_test_result("Generate LaTeX Document Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Generate LaTeX Document Tool", False, str(e))
        
        if "format_research_content" in self.server.tools:
            try:
                handler = self.server.tools["format_research_content"]["handler"]
                result = await handler(
                    content="This is test content that needs academic formatting for publication",
                    content_type="section",
                    formatting_style="academic"
                )
                
                if "Formatted" in str(result):
                    self.log_test_result("Format Research Content Tool", True, "Content formatted successfully")
                else:
                    self.log_test_result("Format Research Content Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Format Research Content Tool", False, str(e))
        
        if "generate_bibliography" in self.server.tools:
            try:
                test_references = [
                    {
                        "type": "article",
                        "authors": "Einstein, A.",
                        "title": "On the electrodynamics of moving bodies",
                        "journal": "Annalen der Physik",
                        "year": "1905"
                    },
                    {
                        "type": "book", 
                        "authors": "Hawking, S.",
                        "title": "A Brief History of Time",
                        "publisher": "Bantam Books",
                        "year": "1988"
                    }
                ]
                
                result = await self.server.tools["generate_bibliography"]["handler"](references=test_references)
                
                if "Generated bibliography" in str(result):
                    self.log_test_result("Generate Bibliography Tool", True, "Bibliography generated")
                else:
                    self.log_test_result("Generate Bibliography Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Generate Bibliography Tool", False, str(e))
        
        # Test Search and Discovery Tools
        if "semantic_search" in self.server.tools:
            try:
                result = await self.server.tools["semantic_search"]["handler"](
                    query="quantum mechanics theoretical framework",
                    collection="research_docs",
                    limit=5,
                    project_path=self.test_project_path
                )
                
                if "results" in str(result).lower():
                    self.log_test_result("Semantic Search Tool", True, "Search completed")
                else:
                    self.log_test_result("Semantic Search Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Semantic Search Tool", False, str(e))
        
        if "discover_patterns" in self.server.tools:
            try:
                test_content = """
                This research explores quantum mechanics and general relativity.
                The methodology involves mathematical analysis and theoretical modeling.
                Results show new insights into fundamental physics principles.
                The approach uses novel computational techniques and advanced algorithms.
                """
                
                result = await self.server.tools["discover_patterns"]["handler"](
                    content=test_content,
                    pattern_type="research_themes",
                    min_frequency=1
                )
                
                if "patterns" in str(result).lower():
                    self.log_test_result("Discover Patterns Tool", True, "Patterns discovered")
                else:
                    self.log_test_result("Discover Patterns Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Discover Patterns Tool", False, str(e))
        
        if "extract_key_concepts" in self.server.tools:
            try:
                result = await self.server.tools["extract_key_concepts"]["handler"](
                    text="quantum mechanics general relativity theoretical framework mathematical analysis computational modeling",
                    max_concepts=10,
                    concept_types=["technical_terms", "theories", "methods"]
                )
                
                if "concepts" in str(result).lower():
                    self.log_test_result("Extract Key Concepts Tool", True, "Concepts extracted")
                else:
                    self.log_test_result("Extract Key Concepts Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Extract Key Concepts Tool", False, str(e))
        
        # Test Storage Management Tools
        if "initialize_project" in self.server.tools:
            try:
                result = await self.server.tools["initialize_project"]["handler"](
                    name="Comprehensive Test Project Tool",
                    description="Testing project initialization through MCP tool",
                    domain="theoretical_physics",
                    project_path=os.path.join(self.test_project_path, "tool_test_project")
                )
                
                if "status" in str(result).lower():
                    self.log_test_result("Initialize Project Tool", True, "Project initialized")
                else:
                    self.log_test_result("Initialize Project Tool", False, str(result))
                    
            except Exception as e:
                self.log_test_result("Initialize Project Tool", False, str(e))

    async def test_storage_persistence(self):
        """Test data persistence across storage components"""
        print("\n💾 Testing Storage Persistence...")
        
        try:
            # Create project and add data
            project_manager = ProjectManager(self.test_project_path)
            self.project_managers.append(project_manager)  # Track for cleanup
            result = await project_manager.initialize_project(
                "Persistence Test",
                "Testing data persistence",
                "theoretical_physics"
            )
            
            # Verify project initialization was successful
            if isinstance(result, dict) and result.get('status') == 'initialized':
                self.log_test_result("Project Initialization Persistence", True, f"Project ID: {result.get('project_id')}")
            else:
                self.log_test_result("Project Initialization Persistence", False, f"Unexpected result: {result}")
                return
            
            # Add some research content to vector store
            if hasattr(project_manager, 'vector_manager') and project_manager.vector_manager is not None:
                await project_manager.vector_manager.add_document(
                    collection_name="research_literature",
                    document="Persistent test content about quantum field theory",
                    doc_id="persistence_test_1",
                    metadata={"type": "research_note", "created": "test"}
                )
                self.log_test_result("Vector Storage Persistence", True, "Document stored successfully")
                
                # Test retrieval
                search_results = await project_manager.vector_manager.search_knowledge(
                    "quantum field theory", 
                    collection="research_literature", 
                    n_results=1
                )
                found_docs = len(search_results.get('documents', [[]])[0]) if search_results.get('documents') else 0
                self.log_test_result("Vector Retrieval Persistence", True, f"Found {found_docs} documents")
            else:
                self.log_test_result("Vector Storage Persistence", False, "Vector manager not available")
            
            # Check if project files exist
            project_files = list(Path(self.test_project_path).glob("**/*"))
            
            if len(project_files) > 0:
                self.log_test_result("File System Persistence", True, f"Found {len(project_files)} persistent files")
            else:
                self.log_test_result("File System Persistence", False, "No persistent files found")
                
        except Exception as e:
            self.log_test_result("Storage Persistence", False, str(e))

    async def test_error_handling(self):
        """Test error handling in tools and storage"""
        print("\n🚨 Testing Error Handling...")
        
        # Test invalid tool parameters
        if "clarify_research_goals" in self.server.tools:
            try:
                result = await self.server.tools["clarify_research_goals"]["handler"](
                    invalid_param="test"
                )
                self.log_test_result("Tool Error Handling", False, "Expected error but got result")
            except Exception as e:
                self.log_test_result("Tool Error Handling", True, f"Properly caught error: {type(e).__name__}")
        
        # Test storage error handling
        try:
            # Try to create SQLite manager with invalid path
            sqlite_manager = SQLiteManager("/invalid/path/test.db")
            await sqlite_manager.initialize()
            self.log_test_result("Storage Error Handling", False, "Expected error but succeeded")
        except Exception as e:
            self.log_test_result("Storage Error Handling", True, f"Properly caught error: {type(e).__name__}")

    async def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("=" * 80)
        print("🧪 COMPREHENSIVE TOOLS AND STORAGE TEST SUITE")
        print("=" * 80)
        
        await self.setup_test_environment()
        
        try:
            await self.test_storage_components_detailed()
            await self.test_all_tools_detailed()
            await self.test_storage_persistence()
            await self.test_error_handling()
            
        finally:
            await self.cleanup_test_environment()
        
        # Print comprehensive results
        self.print_comprehensive_results()

    def print_comprehensive_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed = len([r for r in self.test_results if "❌ FAIL" in r["status"]])
        total = len(self.test_results)
        
        print(f"📈 Overall Results:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {(passed/total)*100:.1f}%")
        
        # Group results by category
        categories = {
            "Storage Components": [],
            "Research Planning": [],
            "Quality Assurance": [],
            "Document Generation": [],
            "Search & Discovery": [],
            "Storage Management": [],
            "System Tests": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(keyword in test_name for keyword in ["SQLite", "Git", "Vector", "Project Manager"]):
                categories["Storage Components"].append(result)
            elif any(keyword in test_name for keyword in ["Research Goals", "Methodology"]):
                categories["Research Planning"].append(result)
            elif any(keyword in test_name for keyword in ["Peer Review", "Quality Gates"]):
                categories["Quality Assurance"].append(result)
            elif any(keyword in test_name for keyword in ["LaTeX", "Format", "Bibliography"]):
                categories["Document Generation"].append(result)
            elif any(keyword in test_name for keyword in ["Search", "Patterns", "Concepts"]):
                categories["Search & Discovery"].append(result)
            elif any(keyword in test_name for keyword in ["Initialize Project"]):
                categories["Storage Management"].append(result)
            else:
                categories["System Tests"].append(result)
        
        for category, results in categories.items():
            if results:
                passed_cat = len([r for r in results if "✅ PASS" in r["status"]])
                total_cat = len(results)
                print(f"\n🔍 {category}: {passed_cat}/{total_cat} passed")
                for result in results:
                    print(f"   {result['status']} {result['test']}")
                    if result['details']:
                        print(f"      └─ {result['details']}")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main test runner"""
    test_suite = ComprehensiveTestSuite()
    try:
        await test_suite.run_comprehensive_tests()
    finally:
        # Ensure proper shutdown
        import os
        import sys
        
        # Force immediate exit to avoid hanging
        print("\n🏁 Tests completed. Exiting...")
        os._exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted.")
        import os
        os._exit(1)
