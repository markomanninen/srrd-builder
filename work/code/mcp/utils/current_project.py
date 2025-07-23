"""
Current Project Manager for SRRD MCP System
Manages the currently active project via ~/.srrd/current_project.txt
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CurrentProjectManager:
    """Manages the currently active SRRD project"""

    def __init__(self):
        self.home_dir = Path.home()
        self.srrd_home = self.home_dir / ".srrd"
        self.current_project_file = self.srrd_home / "current_project.txt"
        self.global_config_file = self.srrd_home / "global_config.json"

        # Ensure ~/.srrd directory exists
        self.srrd_home.mkdir(exist_ok=True)

    def get_current_project(self) -> Optional[str]:
        """
        Get the currently active project path

        Returns:
            str: Absolute path to current project, or None if no project is active
        """
        try:
            if not self.current_project_file.exists():
                logger.debug("No current project file found")
                return None

            project_path = self.current_project_file.read_text().strip()

            if not project_path:
                logger.debug("Current project file is empty")
                return None

            # Validate project exists and has .srrd directory
            project_dir = Path(project_path)
            if not project_dir.exists():
                logger.warning(f"Current project path does not exist: {project_path}")
                self.clear_current_project()
                return None

            srrd_dir = project_dir / ".srrd"
            if not srrd_dir.exists():
                logger.warning(f"Project missing .srrd directory: {project_path}")
                self.clear_current_project()
                return None

            return str(project_dir.resolve())

        except Exception as e:
            logger.error(f"Error reading current project: {e}")
            return None

    def set_current_project(self, project_path: str) -> bool:
        """
        Set the currently active project

        Args:
            project_path: Absolute path to the project

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = Path(project_path).resolve()

            # Validate project exists
            if not project_dir.exists():
                logger.error(f"Project path does not exist: {project_path}")
                return False

            # Validate .srrd directory exists
            srrd_dir = project_dir / ".srrd"
            if not srrd_dir.exists():
                logger.error(f"Project missing .srrd directory: {project_path}")
                return False

            # Validate config.json exists
            config_file = srrd_dir / "config.json"
            if not config_file.exists():
                logger.error(f"Project missing config.json: {project_path}")
                return False

            # Write current project file atomically
            temp_file = self.current_project_file.with_suffix(".tmp")
            temp_file.write_text(str(project_dir))
            temp_file.replace(self.current_project_file)

            logger.info(f"Set current project to: {project_dir}")
            return True

        except Exception as e:
            logger.error(f"Error setting current project: {e}")
            return False

    def clear_current_project(self) -> bool:
        """
        Clear the currently active project

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.current_project_file.exists():
                self.current_project_file.unlink()
            logger.info("Cleared current project")
            return True
        except Exception as e:
            logger.error(f"Error clearing current project: {e}")
            return False

    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the config for the currently active project

        Returns:
            dict: Project configuration, or None if no current project
        """
        project_path = self.get_current_project()
        if not project_path:
            return None

        try:
            config_file = Path(project_path) / ".srrd" / "config.json"
            if not config_file.exists():
                logger.error(f"Config file not found: {config_file}")
                return None

            with open(config_file, "r") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error reading project config: {e}")
            return None

    def get_current_database_path(self) -> Optional[str]:
        """
        Get the database path for the currently active project

        Returns:
            str: Path to sessions.db, or None if no current project
        """
        project_path = self.get_current_project()
        if not project_path:
            return None

        db_path = Path(project_path) / ".srrd" / "sessions.db"
        return str(db_path)

    def has_current_project(self) -> bool:
        """Check if there's a valid current project"""
        return self.get_current_project() is not None

    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive info about current project

        Returns:
            dict: Project info including path, config, and status
        """
        project_path = self.get_current_project()
        if not project_path:
            return None

        config = self.get_current_config()
        db_path = self.get_current_database_path()

        return {
            "project_path": project_path,
            "config_path": str(Path(project_path) / ".srrd" / "config.json"),
            "database_path": db_path,
            "config": config,
            "project_name": (
                config.get("project_name", "Unknown") if config else "Unknown"
            ),
            "domain": config.get("domain", "Unknown") if config else "Unknown",
        }


# Global instance
_current_project_manager = None


def get_current_project_manager() -> CurrentProjectManager:
    """Get the global current project manager instance"""
    global _current_project_manager
    if _current_project_manager is None:
        _current_project_manager = CurrentProjectManager()
    return _current_project_manager


# Convenience functions
def get_current_project() -> Optional[str]:
    """Get the currently active project path"""
    return get_current_project_manager().get_current_project()


def set_current_project(project_path: str) -> bool:
    """Set the currently active project"""
    return get_current_project_manager().set_current_project(project_path)


def clear_current_project() -> bool:
    """Clear the currently active project"""
    return get_current_project_manager().clear_current_project()


def get_current_config() -> Optional[Dict[str, Any]]:
    """Get the config for the currently active project"""
    return get_current_project_manager().get_current_config()


def get_current_database_path() -> Optional[str]:
    """Get the database path for the currently active project"""
    return get_current_project_manager().get_current_database_path()


def has_current_project() -> bool:
    """Check if there's a valid current project"""
    return get_current_project_manager().has_current_project()


def get_project_info() -> Optional[Dict[str, Any]]:
    """Get comprehensive info about current project"""
    return get_current_project_manager().get_project_info()
