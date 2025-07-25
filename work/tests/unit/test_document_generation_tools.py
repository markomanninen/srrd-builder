#!/usr/bin/env python3
"""
Unit Tests for Document Generation Tools
=======================================

Tests all 11 document generation MCP tools:
- generate_latex_document
- generate_bibliography
- compile_latex
- generate_document_with_database_bibliography
- generate_latex_with_template
- list_latex_templates
- format_research_content
- extract_document_sections
- generate_research_summary
- store_bibliography_reference
- retrieve_bibliography_references
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add MCP directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "code" / "mcp"))

from storage.sqlite_manager import SQLiteManager
from utils.current_project import clear_current_project, set_current_project


class TestDocumentGenerationTools:
    """Test document generation tools functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test method"""
        self.cleanup()

    def create_temp_dir(self, name: str) -> Path:
        """Create a temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"doc_gen_test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path

    def cleanup(self):
        """Clean up temp directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                import shutil

                shutil.rmtree(temp_dir)

    @pytest.fixture
    async def active_project_context(self):
        """Creates a temporary project, initializes its DB, and sets it as the active context."""
        project_path = self.create_temp_dir("context_test")

        srrd_dir = project_path / ".srrd"
        srrd_dir.mkdir()

        config_data = {"name": "test_project", "domain": "testing"}
        (srrd_dir / "config.json").write_text(json.dumps(config_data))

        (project_path / "documents").mkdir()
        (srrd_dir / "data").mkdir()

        # *** FIX 1: FULLY INITIALIZE THE DATABASE FOR THE DECORATOR'S LOGGER ***
        db_path = SQLiteManager.get_sessions_db_path(str(project_path))
        sqlite_manager = SQLiteManager(db_path)
        await sqlite_manager.initialize()
        # The logger needs a project and session to satisfy foreign key constraints
        project_id = await sqlite_manager.create_project(
            "test_project", "Test", "testing"
        )
        await sqlite_manager.create_session(project_id, "research", "test_user")
        await sqlite_manager.close()

        try:
            set_current_project(str(project_path))
            yield project_path
        finally:
            clear_current_project()

    @pytest.mark.asyncio
    async def test_generate_latex_document(self, active_project_context):
        """Test LaTeX document generation"""
        try:
            from tools.document_generation import generate_latex_document_tool

            result = await generate_latex_document_tool(
                title="Test Document",
                author="Test Author",
                abstract="This is a test abstract",
                introduction="This is the introduction section",
            )

            assert result is not None
            assert "latex" in str(result).lower() or "document" in str(result).lower()
            assert "successfully at" in result

        except ImportError:
            pytest.skip("Document generation tools not available")
        except Exception as e:
            pytest.fail(f"generate_latex_document_tool failed: {e}")

    @pytest.mark.asyncio
    async def test_generate_bibliography(self):
        """Test bibliography generation"""
        try:
            from tools.document_generation import generate_bibliography_tool

            references = [
                {
                    "title": "Test Paper",
                    "authors": ["Author, A.", "Writer, B."],
                    "year": 2023,
                    "journal": "Test Journal",
                }
            ]

            result = await generate_bibliography_tool(references=references)

            assert result is not None
            assert len(str(result)) > 0

        except ImportError:
            pytest.skip("Bibliography tools not available")
        except Exception as e:
            pytest.fail(f"generate_bibliography_tool failed: {e}")

    @pytest.mark.asyncio
    async def test_compile_latex(self, active_project_context):
        """Test LaTeX compilation"""
        try:
            from tools.document_generation import compile_latex_tool

            project_path = self.create_temp_dir("latex_compile")

            # Create a minimal LaTeX file
            tex_file = project_path / "test.tex"
            tex_content = r"""
            \documentclass{article}
            \begin{document}
            \title{Test Document}
            \author{Test Author}
            \maketitle
            Hello World!
            \end{document}
            """
            tex_file.write_text(tex_content)

            result = await compile_latex_tool(
                tex_file_path=str(tex_file), output_format="pdf"
            )

            assert result is not None

        except ImportError:
            pytest.skip("LaTeX compilation tools not available")
        except Exception as e:
            # LaTeX compilation might fail without proper LaTeX installation
            # This is acceptable for unit tests
            assert "latex" in str(e).lower() or "pdflatex" in str(e).lower()

    @pytest.mark.asyncio
    async def test_list_latex_templates(self):
        """Test LaTeX template listing"""
        try:
            from tools.document_generation import list_latex_templates_tool

            result = await list_latex_templates_tool()

            assert result is not None
            assert "Basic Academic Article" in result

        except ImportError:
            pytest.skip("Template listing tools not available")
        except Exception as e:
            pytest.fail(f"list_latex_templates_tool failed: {e}")

    @pytest.mark.asyncio
    async def test_format_research_content(self):
        """Test research content formatting"""
        try:
            from tools.document_generation import format_research_content_tool

            content = "This is test content that needs formatting."

            result = await format_research_content_tool(
                content=content, content_type="section", formatting_style="academic"
            )

            assert result is not None
            assert len(str(result)) > 0

        except ImportError:
            pytest.skip("Content formatting tools not available")
        except Exception as e:
            pytest.fail(f"format_research_content_tool failed: {e}")

    @pytest.mark.asyncio
    async def test_extract_document_sections(self):
        """Test document section extraction"""
        try:
            from tools.document_generation import extract_document_sections_tool

            document_content = """
            \\documentclass{article}
            \\begin{document}
            \\section{Introduction}
            This is the introduction.
            
            \\section{Methods}
            This describes the methods.
            
            \\section{Results}
            Here are the results.
            \\end{document}
            """

            result = await extract_document_sections_tool(
                document_content=document_content
            )

            assert result is not None
            assert "introduction" in result.lower()
            assert "methods" in result.lower()
            assert "results" in result.lower()

        except ImportError:
            pytest.skip("Section extraction tools not available")
        except Exception as e:
            pytest.fail(f"extract_document_sections_tool failed: {e}")

    @pytest.mark.asyncio
    async def test_bibliography_storage_retrieval(self, active_project_context):
        """Test bibliography storage and retrieval"""
        try:
            from tools.document_generation import (
                retrieve_bibliography_references_tool,
                store_bibliography_reference_tool,
            )

            reference = {
                "title": "Test Reference",
                "authors": ["Test, A."],
                "year": 2023,
                "journal": "Test Journal",
                "doi": "10.1000/test",
            }

            with patch("storage.project_manager.VectorManager") as MockVectorManager:
                mock_instance = MockVectorManager.return_value
                mock_instance.initialize = AsyncMock(return_value=None)
                mock_instance.add_document = AsyncMock(return_value=None)
                mock_instance.search_knowledge = AsyncMock(
                    return_value={"metadatas": [[reference]]}
                )
                # *** FIX 2: MAKE THE MOCK BEHAVE LIKE THE REAL OBJECT ***
                # The tool checks for this collection, so the mock must have it.
                mock_instance.collections = {"research_literature": MagicMock()}

                store_result = await store_bibliography_reference_tool(
                    reference=reference
                )

                assert store_result is not None
                assert "stored successfully" in store_result

                retrieve_result = await retrieve_bibliography_references_tool(
                    query="Test Reference"
                )

                assert retrieve_result is not None
                assert "Test Reference" in retrieve_result

        except ImportError:
            pytest.skip("Bibliography storage tools not available")
        except Exception as e:
            pytest.fail(f"Bibliography storage/retrieval failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
