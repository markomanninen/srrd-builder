"""
Git utilities for SRRD-Builder
"""

import subprocess
from pathlib import Path
from typing import Optional

def is_git_repository(path: Path) -> bool:
    """Check if path is inside a Git repository"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=path,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_git_root(path: Path) -> Optional[Path]:
    """Get the root directory of the Git repository"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=path,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
        return None
    except FileNotFoundError:
        return None

def get_git_branch(path: Path) -> Optional[str]:
    """Get current Git branch name"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=path,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except FileNotFoundError:
        return None
