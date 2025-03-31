from typing import Dict, List, Optional
import git
from git.exc import GitCommandError
from pathlib import Path
import os
from ..core.config import settings

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = None
        self._initialize_repo()

    def _initialize_repo(self):
        """Initialize or load the Git repository."""
        try:
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True)
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = git.Repo.init(self.repo_path)

    def clone_repository(self, url: str, branch: Optional[str] = None) -> Dict:
        """Clone a remote repository."""
        try:
            if branch:
                self.repo = git.Repo.clone_from(url, self.repo_path, branch=branch)
            else:
                self.repo = git.Repo.clone_from(url, self.repo_path)
            return {"status": "success", "message": f"Successfully cloned repository from {url}"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> Dict:
        """Commit changes to the repository."""
        try:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.index.add("*")
            self.repo.index.commit(message)
            return {"status": "success", "message": "Changes committed successfully"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def push_changes(self, remote: str = "origin", branch: str = "main") -> Dict:
        """Push changes to remote repository."""
        try:
            self.repo.remote(remote).push(branch)
            return {"status": "success", "message": "Changes pushed successfully"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def pull_changes(self, remote: str = "origin", branch: str = "main") -> Dict:
        """Pull changes from remote repository."""
        try:
            self.repo.remote(remote).pull(branch)
            return {"status": "success", "message": "Changes pulled successfully"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def create_branch(self, branch_name: str, source: str = "main") -> Dict:
        """Create a new branch."""
        try:
            new_branch = self.repo.create_head(branch_name, source)
            new_branch.checkout()
            return {"status": "success", "message": f"Created and switched to branch {branch_name}"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def merge_branch(self, source_branch: str, target_branch: str = "main") -> Dict:
        """Merge a branch into target branch."""
        try:
            self.repo.git.checkout(target_branch)
            self.repo.git.merge(source_branch)
            return {"status": "success", "message": f"Successfully merged {source_branch} into {target_branch}"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def rebase_branch(self, source_branch: str, target_branch: str = "main") -> Dict:
        """Rebase a branch onto target branch."""
        try:
            self.repo.git.checkout(source_branch)
            self.repo.git.rebase(target_branch)
            return {"status": "success", "message": f"Successfully rebased {source_branch} onto {target_branch}"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def resolve_conflicts(self, files: List[str]) -> Dict:
        """Mark files as resolved after manual conflict resolution."""
        try:
            for file in files:
                self.repo.index.add(file)
            return {"status": "success", "message": "Conflicts resolved successfully"}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict:
        """Get the current status of the repository."""
        try:
            status = {
                "current_branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff('HEAD')],
                "remotes": [remote.name for remote in self.repo.remotes]
            }
            return {"status": "success", "data": status}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)} 