from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    """Status of a project in the ADE platform"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"
    ERROR = "error"

class Project(BaseModel):
    """Project model for the ADE platform"""
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Current project status")
    
    owner_id: str = Field(..., description="ID of the project owner")
    team_ids: List[str] = Field(default=[], description="IDs of team members")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Project creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    repository_url: Optional[str] = Field(None, description="URL to the project repository")
    configuration: Dict[str, Any] = Field(default={}, description="Project-specific configuration")
    
    class Config:
        use_enum_values = True
