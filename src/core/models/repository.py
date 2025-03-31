from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class RepositoryType(Enum):
    """Supported repository types"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"

@dataclass
class Repository:
    """Repository configuration and metadata"""
    url: str
    type: RepositoryType
    branch: Optional[str] = None
    commit: Optional[str] = None
    remote_name: str = "origin"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert repository to dictionary"""
        return {
            "url": self.url,
            "type": self.type.value,
            "branch": self.branch,
            "commit": self.commit,
            "remote_name": self.remote_name
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Repository":
        """Create repository from dictionary"""
        return cls(
            url=data["url"],
            type=RepositoryType(data["type"]),
            branch=data.get("branch"),
            commit=data.get("commit"),
            remote_name=data.get("remote_name", "origin")
        )
        
    @property
    def clone_url(self) -> str:
        """Get repository clone URL"""
        if self.type == RepositoryType.GITHUB:
            return f"https://github.com/{self.url}.git"
        elif self.type == RepositoryType.GITLAB:
            return f"https://gitlab.com/{self.url}.git"
        elif self.type == RepositoryType.BITBUCKET:
            return f"https://bitbucket.org/{self.url}.git"
        else:
            return self.url 