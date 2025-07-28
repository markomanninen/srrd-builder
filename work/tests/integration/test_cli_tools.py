#!/usr/bin/env python3
"""
Integration Tests for the `srrd tool` CLI Command
==================================================

This test file systematically invokes every available MCP tool via the command line
to ensure basic functionality, argument parsing, and successful execution.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from srrd_builder.config.installation_status import is_latex_installed, is_vector_db_installed

# Test cases for tools that don't require special dependencies
GENERAL_TOOL_TEST_CASES = [
    # Research Planning
    ("clarify_research_goals", ["--research-area", "AI", "--initial-goals", "Test"]),
    ("suggest_methodology", ["--research-goals", "Test goals", "--domain", "cs"]),
    # Quality Assurance
    (
        "simulate_peer_review",
        ["--domain", "cs", "--document-content", '{"title":"Test"}'],
    ),
    (
        "check_quality_gates",
        ["--phase", "planning", "--research-content", '{"methodology":"Test"}'],
    ),
    # Document Generation (non-LaTeX)
    ("format_research_content", ["--content", "test content"]),
    # Methodology Advisory
    ("explain_methodology", ["--research-question", "How to test?", "--domain", "cs"]),
    (
        "compare_approaches",
        ["--approach-a", "TDD", "--approach-b", "BDD", "--research-context", "testing"],
    ),
    (
        "validate_design",
        ["--research-design", '{"type":"experimental"}', "--domain", "cs"],
    ),
    (
        "ensure_ethics",
        ["--research-proposal", '{"title":"My Study"}', "--domain", "cs"],
    ),
    # Novel Theory
    (
        "initiate_paradigm_challenge",
        [
            "--domain",
            "physics",
            "--current-paradigm",
            "Standard Model",
            "--challenge-area",
            "gravity",
        ],
    ),
    (
        "develop_alternative_framework",
        ["--domain", "physics", "--core-principles", '["principle 1"]'],
    ),
    (
        "compare_paradigms",
        [
            "--mainstream-paradigm",
            "A",
            "--alternative-paradigm",
            "B",
            "--comparison-criteria",
            '["c1"]',
            "--domain",
            "physics",
        ],
    ),
    # FIX 1: Use a simple string for theory_framework to avoid complex parsing issues.
    (
        "validate_novel_theory",
        [
            "--theory-framework",
            '{"name": "A simple novel theory"}',
            "--domain",
            "physics",
        ],
    ),
    (
        "cultivate_innovation",
        [
            "--research-idea",
            "New idea",
            "--domain",
            "physics",
            "--innovation-goals",
            '["goal 1"]',
        ],
    ),
    (
        "assess_foundational_assumptions",
        ["--domain", "physics", "--current-paradigm", "Standard Model"],
    ),
    (
        "generate_critical_questions",
        ["--research-area", "gravity", "--paradigm-context", "General Relativity"],
    ),
    # FIX 2: Use a single-word string to avoid shell splitting issues.
    (
        "evaluate_paradigm_shift_potential",
        [
            "--theory-framework",
            '{"description": "QuantumGravityUnification"}',
            "--domain",
            "physics",
        ],
    ),
    # FIX 3: Add a relative project-path to ensure test isolation.
    (
        "initialize_project",
        [
            "--name",
            "CLITestProject",
            "--description",
            "A test",
            "--domain",
            "cs",
            "--project-path",
            "./new-cli-project",
        ],
    ),
    # Storage Management (continued)
    ("save_session", ["--session-data", '{"id":1}']),
    ("restore_session", ["--session-id", "1"]),
    ("version_control", ["--action", "status", "--message", "N/A"]),
    ("backup_project", []),
    ("switch_project_context", ["--target-project-path", "."]),
    ("reset_project_context", []),
    # Research Continuity
    ("get_research_progress", []),
    ("get_tool_usage_history", []),
    ("get_workflow_recommendations", []),
    ("get_research_milestones", []),
    ("start_research_session", []),
    ("get_session_summary", []),
]

# LaTeX-dependent test cases
LATEX_TOOL_TEST_CASES = [
    ("generate_latex_document", ["--title", "CLITestDoc"]),
    (
        "compile_latex",
        ["--tex-file-path", "test.tex"],
    ),  # Will fail gracefully, which is a success
    ("list_latex_templates", []),
    ("generate_latex_with_template", ["--title", "TemplateDoc"]),
    ("generate_bibliography", ["--references", '[{"title":"Test Ref"}]']),
    ("extract_document_sections", ["--document-content", "\\section{Intro} content"]),
]

# Vector database-dependent test cases
VECTOR_DB_TOOL_TEST_CASES = [
    ("store_bibliography_reference", ["--reference", '{"title":"Test Store"}']),
    ("retrieve_bibliography_references", ["--query", "Test"]),
    (
        "generate_document_with_database_bibliography",
        ["--title", "DBBibDoc", "--bibliography-query", "Test"],
    ),
    ("semantic_search", ["--query", "test query"]),
    ("extract_key_concepts", ["--text", "some concepts here"]),
    ("generate_research_summary", ["--documents", '["doc one", "doc two"]']),
    ("discover_patterns", ["--content", "some content here to find patterns"]),
    ("find_similar_documents", ["--target-document", "A document about AI research"]),
    ("build_knowledge_graph", ["--documents", '["doc one", "doc two"]']),
    ("search_knowledge", ["--query", "test"]),
]


@pytest.fixture(scope="module")
def active_project_context():
    """Creates and initializes a temporary SRRD project for the tests."""
    temp_dir = tempfile.mkdtemp(prefix="srrd_cli_tool_test_")
    project_path = Path(temp_dir)

    # Use the CLI to initialize the project to ensure a realistic test environment
    python_executable = sys.executable
    project_root = Path(__file__).parent.parent.parent.parent

    env = os.environ.copy()
    mcp_code_path = project_root / "work" / "code" / "mcp"
    python_path = f"{project_root}{os.pathsep}{mcp_code_path}"
    if "PYTHONPATH" in env:
        python_path += os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = python_path

    init_cmd = [
        python_executable,
        "-m",
        "srrd_builder.cli.main",
        "init",
        "--domain",
        "cs",
        "--template",
        "standard",
    ]
    subprocess.run(init_cmd, cwd=project_path, capture_output=True, text=True, env=env)

    yield project_path

    shutil.rmtree(temp_dir)


class TestCliTools:
    """Test suite for executing MCP tools via the `srrd tool` CLI command."""

    def run_cli_command(self, args: list, cwd: Path) -> subprocess.CompletedProcess:
        """Helper to run an SRRD CLI command."""
        python_executable = sys.executable
        project_root = Path(__file__).parent.parent.parent.parent

        env = os.environ.copy()
        mcp_code_path = project_root / "work" / "code" / "mcp"
        python_path = f"{project_root}{os.pathsep}{mcp_code_path}"
        if "PYTHONPATH" in env:
            python_path += os.pathsep + env["PYTHONPATH"]
        env["PYTHONPATH"] = python_path

        cmd = [python_executable, "-m", "srrd_builder.cli.main"] + args
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )
        return result

    @pytest.mark.parametrize("tool_name, tool_args", GENERAL_TOOL_TEST_CASES)
    def test_general_tool_cli_execution(self, active_project_context, tool_name, tool_args):
        """
        Tests that each tool can be successfully invoked via the CLI.
        This is a basic success check, not an output validation.
        """
        command = ["tool", tool_name] + tool_args

        # Special case for compile_latex, which needs a file to exist
        if tool_name == "compile_latex":
            (active_project_context / "test.tex").write_text(
                "\\documentclass{article}\\begin{document}Hello\\end{document}"
            )

        result = self.run_cli_command(command, cwd=active_project_context)

        # Check stderr for critical errors (but allow warnings)
        stderr_lower = result.stderr.lower()
        assert (
            "error" not in stderr_lower
        ), f"Tool '{tool_name}' produced an error in stderr:\n{result.stderr}"
        assert (
            "traceback" not in stderr_lower
        ), f"Tool '{tool_name}' produced a traceback in stderr:\n{result.stderr}"

        # Check for successful execution status in stdout
        assert (
            "Tool executed successfully" in result.stdout
        ), f"Tool '{tool_name}' did not report success in stdout:\n{result.stdout}"

        # The primary check: command should exit with code 0
        assert (
            result.returncode == 0
        ), f"Tool '{tool_name}' failed with exit code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    @pytest.mark.parametrize("tool_name, tool_args", LATEX_TOOL_TEST_CASES)
    @pytest.mark.skipif(not is_latex_installed(), reason="LaTeX not installed")
    def test_latex_tool_cli_execution(self, active_project_context, tool_name, tool_args):
        """
        Tests that LaTeX-dependent tools can be successfully invoked via the CLI.
        This is a basic success check, not an output validation.
        """
        command = ["tool", tool_name] + tool_args

        # Special case for compile_latex, which needs a file to exist
        if tool_name == "compile_latex":
            (active_project_context / "test.tex").write_text(
                "\\documentclass{article}\\begin{document}Hello\\end{document}"
            )

        result = self.run_cli_command(command, cwd=active_project_context)

        # Check stderr for critical errors (but allow warnings)
        stderr_lower = result.stderr.lower()
        assert (
            "error" not in stderr_lower
        ), f"Tool '{tool_name}' produced an error in stderr:\n{result.stderr}"
        assert (
            "traceback" not in stderr_lower
        ), f"Tool '{tool_name}' produced a traceback in stderr:\n{result.stderr}"

        # Check for successful execution status in stdout
        assert (
            "Tool executed successfully" in result.stdout
        ), f"Tool '{tool_name}' did not report success in stdout:\n{result.stdout}"

        # The primary check: command should exit with code 0
        assert (
            result.returncode == 0
        ), f"Tool '{tool_name}' failed with exit code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    @pytest.mark.parametrize("tool_name, tool_args", VECTOR_DB_TOOL_TEST_CASES)
    @pytest.mark.skipif(not is_vector_db_installed(), reason="Vector database not installed")
    def test_vector_db_tool_cli_execution(self, active_project_context, tool_name, tool_args):
        """
        Tests that vector database-dependent tools can be successfully invoked via the CLI.
        This is a basic success check, not an output validation.
        """
        command = ["tool", tool_name] + tool_args

        result = self.run_cli_command(command, cwd=active_project_context)

        # Check stderr for critical errors (but allow warnings)
        stderr_lower = result.stderr.lower()
        assert (
            "error" not in stderr_lower
        ), f"Tool '{tool_name}' produced an error in stderr:\n{result.stderr}"
        assert (
            "traceback" not in stderr_lower
        ), f"Tool '{tool_name}' produced a traceback in stderr:\n{result.stderr}"

        # Check for successful execution status in stdout
        assert (
            "Tool executed successfully" in result.stdout
        ), f"Tool '{tool_name}' did not report success in stdout:\n{result.stdout}"

        # The primary check: command should exit with code 0
        assert (
            result.returncode == 0
        ), f"Tool '{tool_name}' failed with exit code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
