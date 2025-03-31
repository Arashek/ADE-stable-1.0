from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class Repository(BaseModel):
    """Repository model for managing code repositories."""
    id: str = Field(..., description="Unique identifier for the repository")
    name: str = Field(..., description="Name of the repository")
    url: str = Field(..., description="URL of the repository")
    local_path: str = Field(..., description="Local path where the repository is cloned")
    branch: str = Field(default="main", description="Branch to clone")
    last_sync: Optional[datetime] = Field(None, description="Last time the repository was synced")
    status: str = Field(default="pending", description="Current status of the repository")
    metadata: Dict = Field(default_factory=dict, description="Additional repository metadata")

class FileInfo(BaseModel):
    """File information model for managing file metadata."""
    path: str = Field(..., description="Relative path of the file")
    name: str = Field(..., description="Name of the file")
    extension: str = Field(..., description="File extension")
    size: int = Field(..., description="File size in bytes")
    last_modified: datetime = Field(..., description="Last modification timestamp")
    content_type: str = Field(..., description="MIME type of the file")
    is_binary: bool = Field(..., description="Whether the file is binary")
    encoding: Optional[str] = Field(None, description="File encoding if text")
    line_count: Optional[int] = Field(None, description="Number of lines if text file")
    metadata: Dict = Field(default_factory=dict, description="Additional file metadata")

class FileChange(BaseModel):
    """Model for tracking file changes."""
    path: str = Field(..., description="Path of the changed file")
    change_type: str = Field(..., description="Type of change (created, modified, deleted)")
    timestamp: datetime = Field(..., description="When the change occurred")
    old_content: Optional[str] = Field(None, description="Previous content if modified")
    new_content: Optional[str] = Field(None, description="New content if modified")
    metadata: Dict = Field(default_factory=dict, description="Additional change metadata")

class FileSearchResult(BaseModel):
    """Model for file search results."""
    file: FileInfo = Field(..., description="File information")
    matches: List[Dict] = Field(..., description="List of matches with line numbers and context")
    score: float = Field(..., description="Search relevance score")
    metadata: Dict = Field(default_factory=dict, description="Additional search metadata") 