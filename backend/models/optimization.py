from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from uuid import UUID

from models.codebase import Codebase

class OptimizationProfile(BaseModel):
    """Model representing optimization parameters and constraints"""
    profile_type: str  # "performance", "memory", "size", "general"
    target_metrics: List[str] = ["performance"]  # What metrics to optimize for
    target_file_types: List[str] = []  # File extensions to target, empty means all
    excludes: List[str] = []  # Patterns to exclude from optimization
    constraints: List[str] = []  # Constraints to observe when optimizing

class OptimizationSession(BaseModel):
    """Model representing an optimization session"""
    id: str
    codebase: Codebase
    profile: OptimizationProfile
    status: str  # "in_progress", "completed", "failed"
    optimizations: List[Dict[str, Any]] = []
    analysis: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class OptimizationResult(BaseModel):
    """Model representing the result of an optimization operation"""
    session_id: str
    optimizations: List[Dict[str, Any]] = []
    analysis: str = ""
    success: bool = False
