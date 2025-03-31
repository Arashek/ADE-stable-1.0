from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import git
from datetime import datetime

logger = logging.getLogger(__name__)

class VersionControlManager:
    """Manager for version control operations"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.repo = git.Repo(project_dir)
        self.commit_history: Dict[str, List[Dict[str, Any]]] = {}
        self.branch_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def commit_changes(
        self,
        files: List[str],
        message: str,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Commit changes to version control"""
        try:
            # Switch branch if specified
            if branch:
                current = self.repo.active_branch.name
                if current != branch:
                    self.repo.git.checkout(branch)
                    
            # Stage files
            for file_path in files:
                self.repo.index.add(str(Path(file_path).relative_to(self.project_dir)))
                
            # Create commit
            commit = self.repo.index.commit(message)
            
            # Record in history
            self.commit_history.setdefault(branch or 'main', []).append({
                'hash': commit.hexsha,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'files': files
            })
            
            return {
                'success': True,
                'commit_hash': commit.hexsha,
                'branch': branch or 'main'
            }
            
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            raise
            
    async def create_branch(
        self,
        name: str,
        from_branch: str = 'main'
    ) -> Dict[str, Any]:
        """Create a new branch"""
        try:
            # Check if branch exists
            if name in self.repo.heads:
                raise ValueError(f"Branch {name} already exists")
                
            # Create branch
            current = self.repo.active_branch
            self.repo.git.checkout(from_branch)
            new_branch = self.repo.create_head(name)
            new_branch.checkout()
            
            # Record in history
            self.branch_history.setdefault(from_branch, []).append({
                'name': name,
                'created_from': from_branch,
                'timestamp': datetime.now().isoformat()
            })
            
            # Restore previous branch
            current.checkout()
            
            return {
                'success': True,
                'branch': name,
                'from_branch': from_branch
            }
            
        except Exception as e:
            logger.error(f"Error creating branch: {str(e)}")
            raise
            
    async def merge_branches(
        self,
        source: str,
        target: str,
        strategy: str = 'recursive'
    ) -> Dict[str, Any]:
        """Merge two branches"""
        try:
            current = self.repo.active_branch
            
            # Switch to target branch
            self.repo.git.checkout(target)
            
            # Perform merge
            merge_base = self.repo.merge_base(source, target)
            self.repo.index.merge_tree(source, base=merge_base)
            self.repo.git.merge(source, strategy=strategy)
            
            # Record merge in history
            self.branch_history.setdefault(target, []).append({
                'type': 'merge',
                'source': source,
                'target': target,
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy
            })
            
            # Restore previous branch
            current.checkout()
            
            return {
                'success': True,
                'source': source,
                'target': target,
                'strategy': strategy
            }
            
        except git.GitCommandError as e:
            logger.error(f"Merge conflict: {str(e)}")
            return {
                'success': False,
                'error': 'merge_conflict',
                'message': str(e)
            }
        except Exception as e:
            logger.error(f"Error merging branches: {str(e)}")
            raise
            
    async def get_history(
        self,
        branch: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get commit history for a branch"""
        try:
            if branch:
                commits = list(self.repo.iter_commits(branch, max_count=limit))
            else:
                commits = list(self.repo.iter_commits(max_count=limit))
                
            return [{
                'hash': c.hexsha,
                'message': c.message,
                'author': c.author.name,
                'timestamp': c.committed_datetime.isoformat(),
                'branch': branch or 'main'
            } for c in commits]
            
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return []
            
    async def get_status(self) -> Dict[str, Any]:
        """Get repository status"""
        try:
            return {
                'current_branch': self.repo.active_branch.name,
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': self.repo.untracked_files,
                'branches': [h.name for h in self.repo.heads],
                'remotes': [r.name for r in self.repo.remotes]
            }
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {}
