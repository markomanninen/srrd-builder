"""
Context Detection Module for SRRD MCP Server
Automatically detects project context for context-aware tool execution
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .current_project import get_current_project

logger = logging.getLogger(__name__)


class ContextDetector:
    """
    Detects SRRD project context using multiple methods:
    1. Environment variables set by Claude Desktop configuration
    2. Directory traversal to find .srrd directories
    3. Project configuration validation
    """

    def __init__(self):
        self._cached_context = None
        self._cache_valid = False

    def detect_context(self, refresh_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        Detect the current SRRD project context

        Args:
            refresh_cache: Force refresh of cached context

        Returns:
            Dict with context information or None if no context detected
        """
        if self._cache_valid and not refresh_cache:
            return self._cached_context

        # Method 1: Check environment variables (set by Claude Desktop configuration)
        context = self._detect_from_environment()
        if context:
            self._cached_context = context
            self._cache_valid = True
            logger.info(f"Context detected from environment: {context['project_path']}")
            return context

        # Method 2: Directory traversal
        context = self._detect_from_directory()
        if context:
            self._cached_context = context
            self._cache_valid = True
            logger.info(f"Context detected from directory: {context['project_path']}")
            return context

        # No context detected
        self._cached_context = None
        self._cache_valid = True
        logger.debug("No SRRD project context detected")
        return None

    def _detect_from_environment(self) -> Optional[Dict[str, Any]]:
        """Detect context from environment variables set by Claude Desktop configuration"""
        project_path = get_current_project()  # os.environ.get("SRRD_PROJECT_PATH")
        config_path = os.environ.get("SRRD_CONFIG_PATH")

        if not project_path:
            return None

        project_path = Path(project_path)
        if not project_path.exists():
            logger.warning(
                f"SRRD_PROJECT_PATH points to non-existent directory: {project_path}"
            )
            return None

        # Validate project structure
        if not self._validate_project_structure(project_path):
            logger.warning(f"Invalid SRRD project structure at: {project_path}")
            return None

        context = {
            "project_path": str(project_path),
            "config_path": config_path,
            "method": "environment",
            "validated": True,
        }

        # Load additional config if available
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    context["config"] = config
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"Could not load config from {config_path}: {e}")

        return context

    def _detect_from_directory(self) -> Optional[Dict[str, Any]]:
        """Detect context by traversing directory structure"""
        current_dir = Path.cwd()

        # Look for .srrd directory in current or parent directories
        for path in [current_dir] + list(current_dir.parents):
            srrd_dir = path / ".srrd"
            if srrd_dir.exists() and srrd_dir.is_dir():
                if self._validate_project_structure(path):
                    config_path = srrd_dir / "config.json"
                    context = {
                        "project_path": str(path),
                        "config_path": (
                            str(config_path) if config_path.exists() else None
                        ),
                        "method": "directory_traversal",
                        "validated": True,
                    }

                    # Load config if available
                    if config_path.exists():
                        try:
                            with open(config_path, "r") as f:
                                config = json.load(f)
                                context["config"] = config
                        except (json.JSONDecodeError, FileNotFoundError) as e:
                            logger.warning(
                                f"Could not load config from {config_path}: {e}"
                            )

                    return context

        return None

    def _validate_project_structure(self, project_path: Path) -> bool:
        """Validate that the path contains a valid SRRD project structure"""
        srrd_dir = project_path / ".srrd"

        # Check for required SRRD structure
        if not srrd_dir.exists():
            return False

        if not srrd_dir.is_dir():
            return False

        # Check for essential directories (in main project, not .srrd)
        required_items = [
            "work",  # Work directory
            "data",  # Data directory
        ]

        for item in required_items:
            item_path = project_path / item
            if not item_path.exists():
                logger.debug(f"Missing required SRRD item: {item_path}")
                # Don't fail validation for missing directories, just log
                # This allows more flexible project structures
                pass

        return True

    def get_project_path(self) -> Optional[str]:
        """Get the current project path if context is available"""
        context = self.detect_context()
        return context["project_path"] if context else None

    def get_config_path(self) -> Optional[str]:
        """Get the current config path if context is available"""
        context = self.detect_context()
        return context.get("config_path") if context else None

    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the current project configuration if available"""
        context = self.detect_context()
        return context.get("config") if context else None

    def is_context_available(self) -> bool:
        """Check if SRRD project context is available"""
        return self.detect_context() is not None

    def clear_cache(self):
        """Clear the cached context (useful for testing)"""
        self._cached_context = None
        self._cache_valid = False


# Global context detector instance
_context_detector = ContextDetector()


def get_context_detector() -> ContextDetector:
    """Get the global context detector instance"""
    return _context_detector


def detect_project_context() -> Optional[Dict[str, Any]]:
    """Convenience function to detect project context"""
    return _context_detector.detect_context()


def get_project_path() -> Optional[str]:
    """Convenience function to get project path"""
    return _context_detector.get_project_path()


def is_context_available() -> bool:
    """Convenience function to check if context is available"""
    return _context_detector.is_context_available()
