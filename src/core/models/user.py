from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class User(BaseModel):
    """User model"""
    id: str = Field(...)
    username: str = Field(...)
    email: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True 