from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class FileType(str, Enum):
    """Types of files in a codebase"""
    SOURCE = "source"
    TEST = "test"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    STATIC = "static"
    TEMPLATE = "template"
    DATA = "data"
    OTHER = "other"

class File(BaseModel):
    """File in a codebase"""
    id: str = Field(..., description="Unique file identifier")
    path: str = Field(..., description="File path relative to project root")
    name: str = Field(..., description="File name")
    type: FileType = Field(default=FileType.SOURCE, description="File type")
    
    content: Optional[str] = Field(None, description="File content")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")
    
    created_at: datetime = Field(default_factory=datetime.now, description="File creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    metadata: Dict[str, Any] = Field(default={}, description="Additional file metadata")
    
    class Config:
        use_enum_values = True

class Directory(BaseModel):
    """Directory in a codebase"""
    id: str = Field(..., description="Unique directory identifier")
    path: str = Field(..., description="Directory path relative to project root")
    name: str = Field(..., description="Directory name")
    
    files: List[str] = Field(default=[], description="IDs of files in this directory")
    subdirectories: List[str] = Field(default=[], description="IDs of subdirectories")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Directory creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    metadata: Dict[str, Any] = Field(default={}, description="Additional directory metadata")

class Codebase(BaseModel):
    """Complete codebase for a project"""
    id: str = Field(..., description="Unique codebase identifier")
    project_id: str = Field(..., description="ID of the project this codebase belongs to")
    
    name: str = Field(..., description="Codebase name")
    description: Optional[str] = Field(None, description="Codebase description")
    version: str = Field(default="1.0", description="Codebase version")
    
    root_directory_id: str = Field(..., description="ID of the root directory")
    
    directories: Dict[str, Directory] = Field(default={}, description="Directories by ID")
    files: Dict[str, File] = Field(default={}, description="Files by ID")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Statistics and metadata
    total_files: int = Field(default=0, description="Total number of files")
    total_directories: int = Field(default=0, description="Total number of directories")
    total_lines: int = Field(default=0, description="Total lines of code")
    
    languages: Dict[str, int] = Field(default={}, description="Languages and line counts")
    technologies: List[str] = Field(default=[], description="Technologies used")
    
    repository_url: Optional[str] = Field(None, description="URL to the code repository")
    
    metadata: Dict[str, Any] = Field(default={}, description="Additional codebase metadata")
    
    class Config:
        use_enum_values = True
