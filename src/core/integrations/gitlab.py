import aiohttp
import logging
from typing import Optional, Dict, Any
from ..models.repository import Repository, RepositoryType
import os

logger = logging.getLogger(__name__)

class GitLabClient:
    """GitLab API client for repository operations"""
    
    def __init__(self):
        """Initialize GitLab client"""
        self.api_url = "https://gitlab.com/api/v4"
        self.token = os.getenv("GITLAB_TOKEN")
        self.headers = {
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json"
        }
        
    async def clone_repository(
        self,
        url: str,
        branch: Optional[str] = None
    ) -> Optional[Repository]:
        """Clone a GitLab repository
        
        Args:
            url: Repository URL
            branch: Optional branch to clone
            
        Returns:
            Repository object if successful, None otherwise
        """
        try:
            # Extract repository path from URL
            repo_path = url.replace("https://gitlab.com/", "").replace(".git", "")
            
            # Get repository info
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/projects/{repo_path}",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get repository info: {response.status}")
                        return None
                        
                    repo_info = await response.json()
                    
            # Create repository object
            repository = Repository(
                url=repo_path,
                type=RepositoryType.GITLAB,
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
        initialize: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new GitLab repository
        
        Args:
            name: Repository name
            description: Optional description
            private: Whether repository is private
            initialize: Whether to initialize with README
            
        Returns:
            Repository info if successful, None otherwise
        """
        try:
            data = {
                "name": name,
                "visibility": "private" if private else "public",
                "initialize_with_readme": initialize
            }
            
            if description:
                data["description"] = description
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/projects",
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
        project_id: str
    ) -> bool:
        """Delete a GitLab repository
        
        Args:
            project_id: Project ID or path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_url}/projects/{project_id}",
                    headers=self.headers
                ) as response:
                    if response.status != 204:
                        logger.error(f"Failed to delete repository: {response.status}")
                        return False
                        
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to delete repository {project_id}: {str(e)}")
            return False 