import git
from pathlib import Path
from typing import Optional, List

class GitManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.repo: Optional[git.Repo] = None
        if self.project_path.exists() and self.project_path.is_dir():
            try:
                self.repo = git.Repo(self.project_path)
            except git.InvalidGitRepositoryError:
                self.repo = None
        else:
            self.project_path.mkdir(parents=True, exist_ok=True)
            self.repo = None

    def initialize_repository(self) -> bool:
        """Initialize Git repository in project directory"""
        if not self.repo:
            self.repo = git.Repo.init(self.project_path)
            return True
        return False

    def commit_changes(self, message: str, files: List[str] = None) -> str:
        """Commit changes with message, return commit hash"""
        if self.repo:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.index.add(self.repo.untracked_files)
            commit = self.repo.index.commit(message)
            return commit.hexsha
        return ""

    def create_branch(self, branch_name: str) -> bool:
        """Create new branch for research phase"""
        if self.repo:
            self.repo.create_head(branch_name)
            return True
        return False

    def get_commit_history(self, max_count: int = 50) -> List[dict]:
        """Get commit history with metadata"""
        if self.repo:
            commits = list(self.repo.iter_commits(max_count=max_count))
            return [
                {
                    "hash": c.hexsha,
                    "message": c.message,
                    "author": c.author.name,
                    "date": c.authored_datetime.isoformat(),
                }
                for c in commits
            ]
        return []

    def backup_to_remote(self, remote_url: str) -> bool:
        """Backup repository to remote Git server"""
        if self.repo:
            if "origin" not in self.repo.remotes:
                self.repo.create_remote("origin", remote_url)
            self.repo.remotes.origin.push()
            return True
        return ""

    def get_status(self) -> bool:
        """Get repository status - returns True if clean"""
        if self.repo:
            return not self.repo.is_dirty()
        return False
