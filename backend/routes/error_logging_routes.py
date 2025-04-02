"""
API routes for error logging, analysis, and management.
These routes enable capturing frontend errors and providing error analytics.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from typing import Dict, List, Optional, Any
from datetime import datetime
from auth.auth import get_current_user, require_admin
from utils.error_logging import (
    log_error, get_recent_errors, get_error_by_id, 
    ErrorCategory, ErrorSeverity
)
from config.logging_config import logger

# Import API models
from models.api_models import (
    ErrorLogRequest,
    ErrorLogResponse,
    ErrorDetailResponse,
    ErrorFilterRequest,
    ErrorCategory,
    ErrorSeverity
)

router = APIRouter(prefix="/error-logging", tags=["error-logging"])

# Add a simple health check endpoint that doesn't require authentication
@router.get("/health", response_model=Dict[str, str])
async def error_logging_health():
    """Health check endpoint for error logging system"""
    return {
        "status": "operational",
        "system": "error-logging",
        "timestamp": datetime.utcnow().isoformat()
    }

# Error Logging Routes
@router.post("/log", response_model=ErrorLogResponse)
async def create_error_log(
    error: ErrorLogRequest,
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """Log an error from frontend or other sources"""
    try:
        # Add user_id from authenticated user if available
        if current_user and not error.user_id:
            error.user_id = current_user.get("id")
            
        # Use provided context or initialize empty dict
        context = error.context or {}
        
        # Add stack trace to context if provided
        if error.stack_trace:
            context["stack_trace"] = error.stack_trace
        
        # Log the error
        error_id = log_error(
            error=error.message,
            category=error.category,
            severity=error.severity,
            component=error.component,
            source=error.source,
            user_id=error.user_id,
            request_id=error.request_id,
            context=context
        )
        
        return ErrorLogResponse(
            error_id=error_id,
            timestamp=datetime.utcnow().isoformat(),
            status="recorded"
        )
    except Exception as e:
        logger.error(f"Error while logging error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log error")


@router.get("/recent", response_model=List[ErrorDetailResponse])
async def get_recent_error_logs(
    filter_params: ErrorFilterRequest = Depends(),
    current_user: Dict = Depends(require_admin)
):
    """Get recent error logs with optional filtering (admin only)"""
    try:
        errors = get_recent_errors(
            limit=filter_params.limit,
            category=filter_params.category,
            severity=filter_params.severity,
            component=filter_params.component
        )
        return errors
    except Exception as e:
        logger.error(f"Error retrieving error logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve error logs")


@router.get("/{error_id}", response_model=ErrorDetailResponse)
async def get_error_details(
    error_id: str,
    current_user: Dict = Depends(require_admin)
):
    """Get detailed information for a specific error (admin only)"""
    error = get_error_by_id(error_id)
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    return error


@router.get("/categories", response_model=List[str])
async def get_error_categories():
    """Get all available error categories"""
    categories = [getattr(ErrorCategory, attr) for attr in dir(ErrorCategory) 
                 if not attr.startswith("_") and isinstance(getattr(ErrorCategory, attr), str)]
    return categories


@router.get("/severities", response_model=List[str])
async def get_error_severities():
    """Get all available error severity levels"""
    severities = [getattr(ErrorSeverity, attr) for attr in dir(ErrorSeverity) 
                 if not attr.startswith("_") and isinstance(getattr(ErrorSeverity, attr), str)]
    return severities
