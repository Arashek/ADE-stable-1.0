"""
Centralized error logging utilities for capturing, storing, and analyzing errors
across both backend and frontend components of the ADE platform.

This module implements structured error logging with error categorization,
severity levels, and context capture to support systematic error resolution.
"""

import os
import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from config.settings import settings

# Configure a dedicated error logger
error_logger = logging.getLogger("ade_error_logger")
error_logger.setLevel(logging.DEBUG)

# Create error logs directory if it doesn't exist
ERROR_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "errors")
os.makedirs(ERROR_LOGS_DIR, exist_ok=True)

# Create file handler for error logging
error_file_handler = logging.FileHandler(os.path.join(ERROR_LOGS_DIR, "error_log.json"))
error_file_handler.setLevel(logging.DEBUG)
error_logger.addHandler(error_file_handler)

# Create console handler for error logging during development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
error_logger.addHandler(console_handler)

# Error severity levels
class ErrorSeverity:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING" 
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Error categories
class ErrorCategory:
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    DATABASE = "DATABASE"
    API = "API"
    VALIDATION = "VALIDATION"
    AGENT = "AGENT"
    COORDINATION = "COORDINATION"
    MEMORY = "MEMORY"
    FRONTEND = "FRONTEND"
    SYSTEM = "SYSTEM"
    INTEGRATION = "INTEGRATION"
    UNKNOWN = "UNKNOWN"

class ErrorLog:
    """Error log entry with structured metadata for error tracking and analysis"""
    
    def __init__(
        self,
        error: Union[Exception, str],
        category: str = ErrorCategory.UNKNOWN,
        severity: str = ErrorSeverity.ERROR,
        component: str = "backend",
        source: str = None,
        user_id: str = None,
        request_id: str = None,
        context: Dict[str, Any] = None
    ):
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        
        if isinstance(error, Exception):
            self.error_type = error.__class__.__name__
            self.message = str(error)
            self.traceback = traceback.format_exc()
        else:
            self.error_type = "StringError" 
            self.message = str(error)
            self.traceback = traceback.format_stack()
            
        self.category = category
        self.severity = severity
        self.component = component
        self.source = source
        self.user_id = user_id
        self.request_id = request_id
        self.context = context or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error log to dictionary for serialization"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "message": self.message,
            "traceback": self.traceback,
            "category": self.category,
            "severity": self.severity,
            "component": self.component,
            "source": self.source,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "context": self.context
        }
        
    def to_json(self) -> str:
        """Convert error log to JSON string"""
        return json.dumps(self.to_dict(), default=str, indent=2)
    
    def __str__(self) -> str:
        return f"[{self.severity}] {self.category}: {self.message}"


# Global error collection for in-memory access
_error_collection: List[ErrorLog] = []
_max_in_memory_errors = 1000  # Limit the number of errors stored in memory

def log_error(
    error: Union[Exception, str],
    category: str = ErrorCategory.UNKNOWN,
    severity: str = ErrorSeverity.ERROR,
    component: str = "backend",
    source: str = None,
    user_id: str = None,
    request_id: str = None,
    context: Dict[str, Any] = None
) -> str:
    """
    Log an error with structured metadata
    
    Args:
        error: Exception object or error message string
        category: Error category from ErrorCategory constants
        severity: Error severity from ErrorSeverity constants
        component: Component where error occurred (e.g., 'backend', 'frontend')
        source: Source module/file where error occurred
        user_id: ID of user affected by the error (if applicable)
        request_id: ID of request that triggered the error (if applicable)
        context: Additional context data relevant to the error
        
    Returns:
        error_id: Unique ID of the logged error
    """
    error_log = ErrorLog(
        error=error,
        category=category,
        severity=severity,
        component=component,
        source=source,
        user_id=user_id,
        request_id=request_id,
        context=context
    )
    
    # Add to in-memory collection (with size limit)
    _error_collection.append(error_log)
    if len(_error_collection) > _max_in_memory_errors:
        _error_collection.pop(0)  # Remove oldest error
    
    # Log to file
    try:
        error_logger.log(
            getattr(logging, severity, logging.ERROR),
            error_log.to_json()
        )
    except Exception as e:
        # Fallback to basic logging if JSON logging fails
        error_logger.error(f"Error logging failed: {str(e)}")
        error_logger.error(str(error_log))
    
    return error_log.error_id

def get_recent_errors(
    limit: int = 100,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    component: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get recent errors with optional filtering
    
    Args:
        limit: Maximum number of errors to return
        category: Filter by error category
        severity: Filter by error severity
        component: Filter by component
        start_time: Filter by start time
        end_time: Filter by end time
        
    Returns:
        List of error log dictionaries
    """
    filtered_errors = _error_collection
    
    if category:
        filtered_errors = [e for e in filtered_errors if e.category == category]
    if severity:
        filtered_errors = [e for e in filtered_errors if e.severity == severity]
    if component:
        filtered_errors = [e for e in filtered_errors if e.component == component]
    if start_time:
        filtered_errors = [e for e in filtered_errors if datetime.fromisoformat(e.timestamp) >= start_time]
    if end_time:
        filtered_errors = [e for e in filtered_errors if datetime.fromisoformat(e.timestamp) <= end_time]
    
    # Sort by timestamp (newest first) and limit
    sorted_errors = sorted(filtered_errors, key=lambda e: e.timestamp, reverse=True)
    limited_errors = sorted_errors[:limit]
    
    return [e.to_dict() for e in limited_errors]

def get_error_by_id(error_id: str) -> Optional[Dict[str, Any]]:
    """Get error details by ID"""
    for error in _error_collection:
        if error.error_id == error_id:
            return error.to_dict()
    return None

def clear_errors() -> None:
    """Clear in-memory error collection (for testing/development)"""
    _error_collection.clear()

# API routes for error logging will be implemented in routes/error_logging_routes.py
