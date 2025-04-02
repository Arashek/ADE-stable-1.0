"""
API Models for the ADE Platform

This module contains all the Pydantic models used for validating API requests and responses.
These models provide strong type checking and validation for API interactions.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
import uuid
from enum import Enum


# Common Enums
class ErrorCategory(str, Enum):
    AGENT = "AGENT"
    API = "API"
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DATABASE = "DATABASE"
    SECURITY = "SECURITY"
    SYSTEM = "SYSTEM"
    COORDINATION = "COORDINATION"
    UNKNOWN = "UNKNOWN"
    VALIDATION = "VALIDATION"
    COMMUNICATION = "COMMUNICATION"
    PROCESSING = "PROCESSING"


class ErrorSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    BUSY = "busy"
    INACTIVE = "inactive"
    ERROR = "error"


class ConsensusStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


# Base Models
class BaseResponse(BaseModel):
    """Base model for all API responses with common fields"""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse):
    """Standard error response model"""
    success: bool = False
    error: str
    error_detail: Optional[str] = None
    error_code: Optional[str] = None
    error_id: Optional[str] = None
    

# Coordination API Models
class AgentStatusResponse(BaseModel):
    """Agent status information"""
    id: str
    type: str
    status: AgentStatus
    capabilities: List[str]
    last_activity: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConflictResolutionResponse(BaseModel):
    """Information about a resolved conflict"""
    attribute: str
    values: Dict[str, Any]
    selected_value: Any
    selected_agent: str
    confidence: float = Field(ge=0.0, le=1.0)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class ConsensusVoteRequest(BaseModel):
    """Request to submit a vote for a consensus decision"""
    option: Any
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(min_length=1)
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class CreateConsensusDecisionRequest(BaseModel):
    """Request to create a new consensus decision"""
    key: str = Field(min_length=1)
    description: str = Field(min_length=1)
    options: List[Any] = Field(min_items=1)
    agents: Optional[List[str]] = None
    timeout_seconds: Optional[int] = Field(default=60, ge=1, le=3600)
    
    @validator('options')
    def validate_options(cls, v):
        if not v:
            raise ValueError('At least one option must be provided')
        return v


class ConsensusDecisionResponse(BaseModel):
    """Response with consensus decision information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    description: str
    options: List[Any]
    selected_option: Optional[Any] = None
    votes: List[Dict[str, Any]] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: ConsensusStatus = Field(default=ConsensusStatus.PENDING)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CoordinationStatusResponse(BaseResponse):
    """Overall status of the coordination system"""
    active: bool
    agents: List[AgentStatusResponse]
    conflicts: List[ConflictResolutionResponse] = []
    consensus_decisions: List[ConsensusDecisionResponse] = []
    errors: Dict[str, Any] = {}


class ConflictResolutionRequest(BaseModel):
    """Request to record a conflict resolution"""
    attribute: str = Field(min_length=1)
    values: Dict[str, Any] = Field(min_items=1)
    selected_value: Any
    selected_agent: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    
    @validator('values')
    def validate_values(cls, v):
        if not v:
            raise ValueError('At least one value must be provided')
        return v
    
    @root_validator
    def validate_selected_value(cls, values):
        selected_agent = values.get('selected_agent')
        values_dict = values.get('values', {})
        
        if selected_agent and selected_agent not in values_dict:
            raise ValueError(f'Selected agent {selected_agent} must be a key in the values dictionary')
            
        return values


# Error API Models
class ErrorLogRequest(BaseModel):
    """Request to log an error"""
    message: str = Field(min_length=1)
    error_type: Optional[str] = None
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.ERROR
    component: str = "frontend"
    source: Optional[str] = None
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class ErrorLogResponse(BaseResponse):
    """Response after logging an error"""
    error_id: str
    status: str = "recorded"


class ErrorDetailResponse(BaseModel):
    """Detailed error information"""
    error_id: str
    timestamp: datetime
    error_type: str
    message: str
    traceback: Optional[str] = None
    category: ErrorCategory
    severity: ErrorSeverity
    component: str
    source: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorFilterRequest(BaseModel):
    """Request to filter errors"""
    limit: int = Field(default=100, ge=1, le=1000)
    category: Optional[ErrorCategory] = None
    severity: Optional[ErrorSeverity] = None
    component: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_term: Optional[str] = None


# Generic API models
class PaginatedResponse(BaseResponse):
    """Base model for paginated responses"""
    page: int
    page_size: int
    total_count: int
    total_pages: int
    items: List[Any]


class GenericItemResponse(BaseResponse):
    """Generic response containing a single item"""
    item: Dict[str, Any]


class GenericListResponse(BaseResponse):
    """Generic response containing a list of items"""
    items: List[Dict[str, Any]]
    count: int


class GenericErrorResponse(BaseResponse):
    """Generic error response"""
    success: bool = False
    error: str
    error_detail: Optional[str] = None
