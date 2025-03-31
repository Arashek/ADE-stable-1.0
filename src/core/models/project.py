from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from .repository import Repository

@dataclass
class ProjectTemplate:
    """Project template configuration"""
    name: str
    description: str
    structure: Dict[str, str]  # Maps source paths to target paths
    dependencies: Dict[str, Dict[str, str]]  # Maps language to package versions
    setup_scripts: List[str]  # List of setup script paths

@dataclass
class Project:
    """Project configuration and metadata"""
    id: str
    name: str
    directory: str
    config: Dict[str, Any]
    metadata: Dict[str, Any]
    repository: Optional[Repository] = None
    
    @property
    def created_at(self) -> datetime:
        """Get project creation timestamp"""
        return datetime.fromisoformat(self.metadata["created_at"])
        
    @property
    def updated_at(self) -> datetime:
        """Get project last update timestamp"""
        return datetime.fromisoformat(self.metadata["updated_at"])
        
    @property
    def status(self) -> str:
        """Get project status"""
        return self.metadata["status"]
        
    @property
    def template(self) -> Optional[str]:
        """Get project template name"""
        return self.metadata.get("template")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "directory": self.directory,
            "config": self.config,
            "metadata": self.metadata,
            "repository": self.repository.to_dict() if self.repository else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create project from dictionary"""
        repository = None
        if data.get("repository"):
            repository = Repository.from_dict(data["repository"])
            
        return cls(
            id=data["id"],
            name=data["name"],
            directory=data["directory"],
            config=data["config"],
            metadata=data["metadata"],
            repository=repository
        ) 