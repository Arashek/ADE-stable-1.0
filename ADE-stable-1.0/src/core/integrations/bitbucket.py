import aiohttp
import logging
from typing import Optional, Dict, Any
from ..models.repository import Repository, RepositoryType
import os
import base64

logger = logging.getLogger(__name__)

class BitBucketClient:
    """BitBucket API client for repository operations"""
    
    def __init__(self):
        """Initialize BitBucket client"""
        self.api_url = "https://api.bitbucket.org/2.0"
        self.username = os.getenv("BITBUCKET_USERNAME")
        self.token = os.getenv("BITBUCKET_TOKEN")
        self.auth = base64.b64encode(
            f"{self.username}:{self.token}".encode()
        ).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }
        
    async def clone_repository(
        self,
        url: str,
        branch: Optional[str] = None
    ) -> Optional[Repository]:
        """Clone a BitBucket repository
        
        Args:
            url: Repository URL
            branch: Optional branch to clone
            
        Returns:
            Repository object if successful, None otherwise
        """
        try:
            # Extract repository path from URL
            repo_path = url.replace("https://bitbucket.org/", "").replace(".git", "")
            
            # Get repository info
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/repositories/{repo_path}",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get repository info: {response.status}")
                        return None
                        
                    repo_info = await response.json()
                    
            # Create repository object
            repository = Repository(
                url=repo_path,
                type=RepositoryType.BITBUCKET,
                branch=branch or repo_info["mainbranch"]["name"]
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
        """Create a new BitBucket repository
        
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
                "is_private": private,
                "scm": "git"
            }
            
            if description:
                data["description"] = description
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/repositories/{self.username}/{name}",
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
        repo_name: str
    ) -> bool:
        """Delete a BitBucket repository
        
        Args:
            repo_name: Repository name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_url}/repositories/{self.username}/{repo_name}",
                    headers=self.headers
                ) as response:
                    if response.status != 204:
                        logger.error(f"Failed to delete repository: {response.status}")
                        return False
                        
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_name}: {str(e)}")
            return False 