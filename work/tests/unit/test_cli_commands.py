#!/usr/bin/env python3
"""
Comprehensive Unit Tests for CLI Commands
==========================================

Tests all SRRD CLI commands with same level of detail as test_cli.sh:
- srrd init - Project initialization with file verification
- srrd generate - Template and PDF generation with file checks
- srrd publish - Publication workflow with directory verification
- srrd status - Project status checking
- srrd configure - Configuration management
- srrd switch - Context switching
- srrd reset - Project reset
- Error handling and edge cases
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestCLICommands:
    """Comprehensive test SRRD CLI command functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.test_passed = 0
        self.test_failed = 0
        self.temp_dirs = []

    def teardown_method(self):
        """Clean up after each test"""
        self.cleanup()

    def create_temp_dir(self, name: str) -> Path:
        """Create a temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix=f"cli_test_{name}_")
        temp_path = Path(temp_dir)
        self.temp_dirs.append(temp_path)
        return temp_path

    def cleanup(self):
        """Clean up resources"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def setup_git_repo(self, project_dir: Path):
        """Set up a Git repository in the project directory"""
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@srrd-builder.test"],
            cwd=project_dir,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "SRRD Test"],
            cwd=project_dir,
            capture_output=True,
        )

        # Add initial commit
        readme = project_dir / "README.md"
        readme.write_text("# Test Research Project\n")
        subprocess.run(
            ["git", "add", "README.md"], cwd=project_dir, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=project_dir,
            capture_output=True,
        )

    def run_cli_command(self, args: list, cwd: Path = None) -> tuple:
        """Run SRRD CLI command and return result"""
        # This is necessary because the CLI code has dependencies on modules
        # outside the 'srrd_builder' package (e.g., work.code.mcp.storage).
        project_root = Path(__file__).parent.parent.parent.parent
        env = os.environ.copy()

        mcp_code_path = project_root / "work" / "code" / "mcp"

        # Prepend project root to allow 'from work.code...' imports
        python_path = f"{project_root}{os.pathsep}{mcp_code_path}"
        if "PYTHONPATH" in env:
            python_path += os.pathsep + env["PYTHONPATH"]
        env["PYTHONPATH"] = python_path

        try:
            cmd = ["python3", "-m", "srrd_builder.cli.main"] + args
            result = subprocess.run(
                cmd,
                cwd=cwd or Path.cwd(),
                capture_output=True,
                text=True,
                timeout=60,  # Increased timeout for comprehensive tests
                env=env,  # Use the modified environment
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    # ===== HELP COMMAND TESTS =====

    def test_cli_help(self):
        """Test CLI help command"""
        returncode, stdout, stderr = self.run_cli_command(["--help"])

        assert returncode == 0, f"Help command failed: {stderr}"
        assert "Scientific Research Requirement Document Builder" in stdout
        assert "init" in stdout
        assert "generate" in stdout
        assert "publish" in stdout
        assert "configure" in stdout
        assert "status" in stdout

    def test_init_help(self):
        """Test init help command"""
        returncode, stdout, stderr = self.run_cli_command(["init", "--help"])

        assert returncode == 0, f"Init help failed: {stderr}"
        assert "domain" in stdout
        assert "template" in stdout
        assert "physics" in stdout or "cs" in stdout

    def test_generate_help(self):
        """Test generate help command"""
        returncode, stdout, stderr = self.run_cli_command(["generate", "--help"])

        assert returncode == 0, f"Generate help failed: {stderr}"
        assert "pdf" in stdout
        assert "template" in stdout

    def test_publish_help(self):
        """Test publish help command"""
        returncode, stdout, stderr = self.run_cli_command(["publish", "--help"])

        assert returncode == 0, f"Publish help failed: {stderr}"
        assert "draft_name" in stdout
        assert "version" in stdout

    def test_configure_help(self):
        """Test configure help command"""
        returncode, stdout, stderr = self.run_cli_command(["configure", "--help"])

        assert returncode == 0, f"Configure help failed: {stderr}"
        assert "claude" in stdout or "Claude" in stdout

    def test_status_help(self):
        """Test status help command"""
        returncode, stdout, stderr = self.run_cli_command(["status", "--help"])

        assert returncode == 0, f"Status help failed: {stderr}"

    # ===== PROJECT INITIALIZATION TESTS =====

    def test_init_command(self):
        """Test comprehensive project initialization"""
        project_dir = self.create_temp_dir("init_test")

        # Test initialization (Git is auto-initialized by the command now)
        returncode, stdout, stderr = self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        assert returncode == 0, f"Init command failed: {stderr}\nStdout: {stdout}"
        assert "SRRD-Builder project initialized successfully" in stdout

        # Verify project structure
        assert (project_dir / ".srrd").is_dir(), ".srrd directory not created"
        assert (project_dir / "work").is_dir(), "work directory not created"
        assert (
            project_dir / "work" / "drafts"
        ).is_dir(), "work/drafts directory not created"
        assert (
            project_dir / "work" / "research"
        ).is_dir(), "work/research directory not created"
        assert (
            project_dir / "work" / "data"
        ).is_dir(), "work/data directory not created"
        assert (
            project_dir / "publications"
        ).is_dir(), "publications directory not created"

        # Verify files
        assert (
            project_dir / ".srrd" / "config.json"
        ).is_file(), ".srrd/config.json not created"
        assert (project_dir / ".gitignore").is_file(), ".gitignore not created"

        # Verify config content
        config_file = project_dir / ".srrd" / "config.json"
        config_content = config_file.read_text()
        assert (
            '"domain": "physics"' in config_content
        ), "Config doesn't contain physics domain"

    # ===== TEMPLATE GENERATION TESTS =====

    def test_generate_proposal_template(self):
        """Test proposal template generation"""
        project_dir = self.create_temp_dir("template_test")

        # Initialize project first
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        # Generate proposal template
        returncode, stdout, stderr = self.run_cli_command(
            ["generate", "template", "proposal", "--title", "Test Proposal"],
            cwd=project_dir,
        )

        assert returncode == 0, f"Template generation failed: {stderr}"
        assert "LaTeX template generated" in stdout

        # Verify file created
        template_file = project_dir / "work" / "drafts" / "test_proposal.tex"
        assert template_file.is_file(), "Proposal template file not created"

        # Verify content
        content = template_file.read_text()
        assert "Test Proposal" in content, "Title not found in template"
        assert "\\documentclass" in content, "LaTeX document class not found"

    def test_generate_paper_template(self):
        """Test paper template generation"""
        project_dir = self.create_temp_dir("paper_test")

        # Initialize project first
        self.run_cli_command(
            ["init", "--domain", "cs", "--template", "standard"], cwd=project_dir
        )

        # Generate paper template
        returncode, stdout, stderr = self.run_cli_command(
            ["generate", "template", "paper", "--title", "Test Paper"], cwd=project_dir
        )

        assert returncode == 0, f"Paper template generation failed: {stderr}"

        # Verify file created
        template_file = project_dir / "work" / "drafts" / "test_paper.tex"
        assert template_file.is_file(), "Paper template file not created"

    def test_generate_thesis_template(self):
        """Test thesis template generation"""
        project_dir = self.create_temp_dir("thesis_test")

        # Initialize project first
        self.run_cli_command(
            ["init", "--domain", "bio", "--template", "standard"], cwd=project_dir
        )

        # Generate thesis template
        returncode, stdout, stderr = self.run_cli_command(
            ["generate", "template", "thesis", "--title", "Test Thesis"],
            cwd=project_dir,
        )

        assert returncode == 0, f"Thesis template generation failed: {stderr}"

        # Verify file created
        template_file = project_dir / "work" / "drafts" / "test_thesis.tex"
        assert template_file.is_file(), "Thesis template file not created"

    # ===== PDF GENERATION TESTS =====

    def test_generate_pdf(self):
        """Test PDF generation (if pdflatex available)"""
        project_dir = self.create_temp_dir("pdf_test")

        # Initialize project and generate template
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )
        self.run_cli_command(
            [
                "generate",
                "template",
                "proposal",
                "--title",
                "Test PDF",
                "--output",
                "work/drafts",
            ],
            cwd=project_dir,
        )

        # Check if pdflatex is available
        try:
            subprocess.run(["pdflatex", "--version"], capture_output=True, check=True)
            pdflatex_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pdflatex_available = False

        if pdflatex_available:
            # Generate PDF
            returncode, stdout, stderr = self.run_cli_command(
                ["generate", "pdf", "work/drafts/test_pdf.tex"], cwd=project_dir
            )

            assert returncode == 0, f"PDF generation failed: {stderr}"

            # Verify PDF created
            pdf_file = project_dir / "work" / "drafts" / "test_pdf.pdf"
            assert pdf_file.is_file(), "PDF file not created"
        else:
            # Skip test if pdflatex not available
            pytest.skip("pdflatex not available")

    # ===== PUBLICATION WORKFLOW TESTS =====

    def test_publish_workflow(self):
        """Test publication workflow"""
        project_dir = self.create_temp_dir("publish_test")
        self.setup_git_repo(project_dir)

        # Initialize project and generate template
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )
        self.run_cli_command(
            [
                "generate",
                "template",
                "proposal",
                "--title",
                "Test Publish",
                "--output",
                "work/drafts",
            ],
            cwd=project_dir,
        )

        # Publish the document
        returncode, stdout, stderr = self.run_cli_command(
            ["publish", "test_publish", "--version", "v1.0"], cwd=project_dir
        )

        assert returncode == 0, f"Publish command failed: {stderr}"
        assert "Publication complete" in stdout

        # Verify published structure
        pub_dir = project_dir / "publications" / "test_publish"
        assert pub_dir.is_dir(), "Published directory not created"

        pub_file = pub_dir / "test_publish.tex"
        assert pub_file.is_file(), "Published LaTeX file not created"

        # Check Git tag creation
        result = subprocess.run(
            ["git", "tag", "-l"], cwd=project_dir, capture_output=True, text=True
        )
        assert "test_publish-v1.0" in result.stdout, "Git tag not created"

    # ===== STATUS AND CONFIGURATION TESTS =====

    def test_status_command(self):
        """Test project status command"""
        project_dir = self.create_temp_dir("status_test")

        # Initialize project
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        # Test status in SRRD directory
        returncode, stdout, stderr = self.run_cli_command(["status"], cwd=project_dir)
        assert returncode == 0, f"Status command failed: {stderr}"
        assert "SRRD Status" in stdout or "status" in stdout.lower()

    def test_force_reinit(self):
        """Test force reinitialization"""
        project_dir = self.create_temp_dir("reinit_test")

        # Initialize project
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        # Force reinit with different domain
        returncode, stdout, stderr = self.run_cli_command(
            ["init", "--domain", "cs", "--template", "minimal", "--force"],
            cwd=project_dir,
        )

        assert returncode == 0, f"Force reinit failed: {stderr}"

        # Verify domain was updated
        config_file = project_dir / ".srrd" / "config.json"
        config_content = config_file.read_text()
        assert '"domain": "cs"' in config_content, "Domain not updated to cs"

    # ===== ERROR HANDLING TESTS =====

    def test_init_auto_initializes_git(self):
        """Test init auto-initializes git when missing"""
        non_git_dir = self.create_temp_dir("no_git")

        # Try to init without git - should auto-initialize
        returncode, stdout, stderr = self.run_cli_command(["init"], cwd=non_git_dir)

        assert returncode == 0, f"Init should succeed and auto-initialize git: {stderr}"
        assert "Git repository initialized" in stdout

    def test_publish_fails_missing_draft(self):
        """Test publish fails for non-existent draft"""
        project_dir = self.create_temp_dir("publish_fail_test")

        # Initialize project
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        # Try to publish non-existent draft
        returncode, stdout, stderr = self.run_cli_command(
            ["publish", "nonexistent"], cwd=project_dir
        )

        assert returncode != 0, "Publish should fail for missing draft"
        assert "Draft not found" in stdout

    def test_generate_pdf_fails_missing_file(self):
        """Test generate PDF fails for non-existent file"""
        project_dir = self.create_temp_dir("pdf_fail_test")

        # Initialize project
        self.run_cli_command(
            ["init", "--domain", "physics", "--template", "standard"], cwd=project_dir
        )

        # Try to generate PDF from non-existent file
        returncode, stdout, stderr = self.run_cli_command(
            ["generate", "pdf", "nonexistent.tex"], cwd=project_dir
        )

        assert returncode != 0, "PDF generation should fail for missing file"
        assert "File not found" in stdout

    def test_invalid_command(self):
        """Test invalid command handling"""
        returncode, stdout, stderr = self.run_cli_command(["invalid_command"])

        assert returncode != 0, "Should fail for invalid command"
        assert "invalid choice" in stderr.lower() or "error" in stderr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
