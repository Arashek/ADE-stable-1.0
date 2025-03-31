import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
import git
from github import Github, GithubException, Repository, Branch, PullRequest
from github.Repository import Repository as GitHubRepository
from github.Branch import Branch as GitHubBranch
from github.PullRequest import PullRequest as GitHubPullRequest
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from github.GithubException import GithubException
from ..config import settings
from ..models.repository import Repository as RepoModel, RepositoryType
from ..models.user import User
from ..utils.cache import Cache
from ..utils.events import EventType, event_emitter

logger = logging.getLogger(__name__)

class GitHubRateLimit:
    """Handles GitHub API rate limiting."""
    
    def __init__(self):
        self.remaining: int = 0
        self.limit: int = 0
        self.reset_time: Optional[datetime] = None
        self.last_request: Optional[datetime] = None
        self.min_delay: float = 0.1  # Minimum delay between requests
        
    def update(self, remaining: int, limit: int, reset_time: datetime):
        """Update rate limit information.
        
        Args:
            remaining: Remaining API calls
            limit: Total API call limit
            reset_time: When the limit resets
        """
        self.remaining = remaining
        self.limit = limit
        self.reset_time = reset_time
        
    def can_make_request(self) -> bool:
        """Check if a request can be made.
        
        Returns:
            True if a request is allowed
        """
        if self.remaining > 0:
            return True
            
        if self.reset_time and datetime.now() >= self.reset_time:
            return True
            
        return False
        
    def get_delay(self) -> float:
        """Calculate delay for next request.
        
        Returns:
            Delay in seconds
        """
        if self.last_request:
            elapsed = (datetime.now() - self.last_request).total_seconds()
            if elapsed < self.min_delay:
                return self.min_delay - elapsed
                
        return 0

class GitHubClient:
    """GitHub API client for repository operations"""
    
    def __init__(self):
        """Initialize GitHub client"""
        self.api_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    async def clone_repository(
        self,
        url: str,
        branch: Optional[str] = None
    ) -> Optional[Repository]:
        """Clone a GitHub repository
        
        Args:
            url: Repository URL
            branch: Optional branch to clone
            
        Returns:
            Repository object if successful, None otherwise
        """
        try:
            # Extract repository path from URL
            repo_path = url.replace("https://github.com/", "").replace(".git", "")
            
            # Get repository info
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/repos/{repo_path}",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get repository info: {response.status}")
                        return None
                        
                    repo_info = await response.json()
                    
            # Create repository object
            repository = Repository(
                url=repo_path,
                type=RepositoryType.GITHUB,
                branch=branch or repo_info["default_branch"]
            )
            
            return repository
            
        except Exception as e:
            logger.error(f"Failed to clone repository {url}: {str(e)}")
            return None
            
    async def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new GitHub repository
        
        Args:
            name: Repository name
            description: Optional description
            private: Whether repository is private
            auto_init: Whether to initialize with README
            
        Returns:
            Repository info if successful, None otherwise
        """
        try:
            data = {
                "name": name,
                "private": private,
                "auto_init": auto_init
            }
            
            if description:
                data["description"] = description
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/user/repos",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status != 201:
                        logger.error(f"Failed to create repository: {response.status}")
                        return None
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Failed to create repository {name}: {str(e)}")
            return None
            
    async def delete_repository(
        self,
        owner: str,
        repo: str
    ) -> bool:
        """Delete a GitHub repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_url}/repos/{owner}/{repo}",
                    headers=self.headers
                ) as response:
                    if response.status != 204:
                        logger.error(f"Failed to delete repository: {response.status}")
                        return False
                        
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to delete repository {owner}/{repo}: {str(e)}")
            return False

# Global GitHub client instance
github_client = GitHubClient() 