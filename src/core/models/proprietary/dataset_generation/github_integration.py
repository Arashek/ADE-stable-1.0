import os
import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
import requests
from requests.exceptions import RequestException
from github import Github, GithubException
from github.Repository import Repository
from github.Branch import Branch
from github.Commit import Commit
from github.FileContent import FileContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubIntegration:
    """Handles GitHub repository access and processing"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub integration"""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token is required")
            
        self.github = Github(self.token)
        self.rate_limit = self.github.get_rate_limit()
        
    def _check_rate_limit(self):
        """Check and handle rate limiting"""
        if self.rate_limit.core.remaining < 10:
            reset_time = self.rate_limit.core.reset
            sleep_time = (reset_time - time.time()) + 1
            if sleep_time > 0:
                logger.warning(f"Rate limit low, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                
    def search_repositories(
        self,
        language: str,
        min_stars: int = 100,
        min_activity: int = 10
    ) -> List[Repository]:
        """Search for repositories matching criteria"""
        self._check_rate_limit()
        
        query = f"language:{language} stars:>={min_stars}"
        try:
            repos = self.github.search_repositories(query=query)
            return [
                repo for repo in repos
                if self._check_repository_activity(repo, min_activity)
            ]
        except GithubException as e:
            logger.error(f"Error searching repositories: {str(e)}")
            return []
            
    def _check_repository_activity(self, repo: Repository, min_activity: int) -> bool:
        """Check if repository has sufficient activity"""
        try:
            commits = repo.get_commits()
            return commits.totalCount >= min_activity
        except GithubException:
            return False
            
    def clone_repository(self, repo: Repository, local_path: str) -> Optional[Path]:
        """Clone a repository to local storage"""
        try:
            repo_path = Path(local_path) / repo.name
            if repo_path.exists():
                logger.info(f"Repository {repo.name} already exists")
                return repo_path
                
            repo.clone_from(repo.clone_url, str(repo_path))
            logger.info(f"Cloned repository: {repo.name}")
            return repo_path
            
        except Exception as e:
            logger.error(f"Error cloning repository {repo.name}: {str(e)}")
            return None
            
    def extract_code_patterns(
        self,
        repo_path: Path,
        language: str,
        pattern_types: List[str]
    ) -> List[Dict]:
        """Extract code patterns from repository"""
        patterns = []
        
        try:
            for file_path in repo_path.rglob(f"*.{language}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Extract patterns based on type
                    for pattern_type in pattern_types:
                        if pattern_type == "code_pair":
                            patterns.extend(self._extract_code_pairs(content))
                        elif pattern_type == "bug_fix":
                            patterns.extend(self._extract_bug_fixes(content))
                        elif pattern_type == "comment_code":
                            patterns.extend(self._extract_comment_code_pairs(content))
                        elif pattern_type == "project_structure":
                            patterns.extend(self._extract_project_structure(content))
                            
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting patterns: {str(e)}")
            
        return patterns
        
    def _extract_code_pairs(self, content: str) -> List[Dict]:
        """Extract code completion pairs"""
        # TODO: Implement code pair extraction
        return []
        
    def _extract_bug_fixes(self, content: str) -> List[Dict]:
        """Extract bug fix examples"""
        # TODO: Implement bug fix extraction
        return []
        
    def _extract_comment_code_pairs(self, content: str) -> List[Dict]:
        """Extract comment-code pairs"""
        # TODO: Implement comment-code pair extraction
        return []
        
    def _extract_project_structure(self, content: str) -> List[Dict]:
        """Extract project structure examples"""
        # TODO: Implement project structure extraction
        return []
        
    def get_file_history(
        self,
        repo: Repository,
        file_path: str,
        max_commits: int = 10
    ) -> List[Dict]:
        """Get file history with changes"""
        try:
            commits = repo.get_commits(path=file_path)
            history = []
            
            for commit in commits[:max_commits]:
                try:
                    file_content = commit.get_contents(path=file_path)
                    history.append({
                        "sha": commit.sha,
                        "date": commit.commit.author.date.isoformat(),
                        "content": file_content.decoded_content.decode("utf-8")
                    })
                except Exception as e:
                    logger.error(f"Error getting file content for commit {commit.sha}: {str(e)}")
                    continue
                    
            return history
            
        except GithubException as e:
            logger.error(f"Error getting file history: {str(e)}")
            return []
            
    def get_repository_metadata(self, repo: Repository) -> Dict:
        """Get repository metadata"""
        try:
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "size": repo.size,
                "topics": repo.get_topics(),
                "license": repo.license.name if repo.license else None
            }
        except GithubException as e:
            logger.error(f"Error getting repository metadata: {str(e)}")
            return {}
            
    def cleanup(self):
        """Clean up GitHub client"""
        self.github.close() 