from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from uuid import UUID

from models.codebase import Codebase

class Error(BaseModel):
    """Model representing a code error"""
    error_type: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class DebugSession(BaseModel):
    """Model representing a debugging session"""
    id: str
    error: Error
    status: str  # "in_progress", "completed", "failed"
    codebase: Codebase
    fixes: List[Dict[str, Any]] = []
    analysis: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class DebugResult(BaseModel):
    """Model representing the result of a debugging operation"""
    session_id: str
    error: Error
    fixes: List[Dict[str, Any]] = []
    analysis: str = ""
    success: bool = False
