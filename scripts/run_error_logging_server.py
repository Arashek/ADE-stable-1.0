#!/usr/bin/env python
"""
Minimal Error Logging Server for ADE Platform

This script runs a minimal FastAPI server that implements the error logging API,
allowing for testing and development of the error logging system without
requiring the full ADE platform to be operational.
"""

import os
import sys
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("error_logging_server")

# Import FastAPI
try:
    from fastapi import FastAPI, HTTPException, Depends, Body
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    logger.error("Required packages not found. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "pydantic"])
    
    from fastapi import FastAPI, HTTPException, Depends, Body
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn

# Constants for error categories and severity levels
class ErrorCategory:
    """Constants for error categories"""
    AGENT = "AGENT"
    API = "API"
    AUTH = "AUTH"
    DATABASE = "DATABASE"
    FILE_SYSTEM = "FILE_SYSTEM"
    FRONTEND = "FRONTEND"
    IMPORT = "IMPORT"
    NETWORK = "NETWORK"
    PERMISSION = "PERMISSION"
    SYSTEM = "SYSTEM"
    TASK = "TASK"
    UNKNOWN = "UNKNOWN"
    USER_INPUT = "USER_INPUT"
    VALIDATION = "VALIDATION"
    COORDINATION = "COORDINATION"
    TESTING = "TESTING"

class ErrorSeverity:
    """Constants for error severity levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

# Path to error log file
ERROR_LOG_FILE = os.path.join(project_root, "logs", "error_logs.json")

# Ensure logs directory exists
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)

# Error logging functions
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
    Log an error with structured metadata.
    
    Args:
        error: The exception object or error message
        category: Category of the error
        severity: Severity level of the error
        component: Component where the error occurred (backend/frontend)
        source: Source file or module where the error occurred
        user_id: ID of the user who experienced the error
        request_id: ID of the request associated with the error
        context: Additional context information
        
    Returns:
        ID of the error log entry
    """
    # Generate error ID
    error_id = str(uuid.uuid4())
    
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    # Extract error message and traceback
    if isinstance(error, Exception):
        error_message = str(error)
        error_traceback = traceback.format_exc()
    else:
        error_message = error
        error_traceback = None
    
    # Create error log entry
    error_log = {
        "id": error_id,
        "timestamp": timestamp,
        "category": category,
        "severity": severity,
        "component": component,
        "source": source,
        "user_id": user_id,
        "request_id": request_id,
        "error_message": error_message,
        "error_traceback": error_traceback,
        "context": context or {}
    }
    
    # Log to console
    logger.error(f"Error [{category}][{severity}]: {error_message}")
    
    # Save to error log file
    try:
        # Read existing logs if file exists
        if os.path.exists(ERROR_LOG_FILE):
            try:
                with open(ERROR_LOG_FILE, "r") as f:
                    error_logs = json.load(f)
            except json.JSONDecodeError:
                # File exists but is not valid JSON
                error_logs = []
        else:
            error_logs = []
        
        # Add new error log
        error_logs.append(error_log)
        
        # Write updated logs
        with open(ERROR_LOG_FILE, "w") as f:
            json.dump(error_logs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save error log: {str(e)}")
    
    return error_id

def get_error_logs(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    component: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get error logs with optional filtering.
    
    Args:
        limit: Maximum number of logs to return
        offset: Offset for pagination
        category: Filter by error category
        severity: Filter by error severity
        component: Filter by component
        start_time: Filter by start time (ISO format)
        end_time: Filter by end time (ISO format)
        user_id: Filter by user ID
        
    Returns:
        List of error logs matching the filters
    """
    try:
        # Read error logs
        if os.path.exists(ERROR_LOG_FILE):
            try:
                with open(ERROR_LOG_FILE, "r") as f:
                    error_logs = json.load(f)
            except json.JSONDecodeError:
                error_logs = []
        else:
            error_logs = []
        
        # Apply filters
        filtered_logs = error_logs
        
        if category:
            filtered_logs = [log for log in filtered_logs if log.get("category") == category]
        
        if severity:
            filtered_logs = [log for log in filtered_logs if log.get("severity") == severity]
        
        if component:
            filtered_logs = [log for log in filtered_logs if log.get("component") == component]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.get("timestamp", "") >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.get("timestamp", "") <= end_time]
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        paginated_logs = filtered_logs[offset:offset + limit]
        
        return paginated_logs
    except Exception as e:
        logger.error(f"Failed to get error logs: {str(e)}")
        return []

def get_error_log(error_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific error log by ID.
    
    Args:
        error_id: ID of the error log
        
    Returns:
        Error log entry or None if not found
    """
    try:
        # Read error logs
        if os.path.exists(ERROR_LOG_FILE):
            try:
                with open(ERROR_LOG_FILE, "r") as f:
                    error_logs = json.load(f)
            except json.JSONDecodeError:
                error_logs = []
        else:
            error_logs = []
        
        # Find error log by ID
        for log in error_logs:
            if log.get("id") == error_id:
                return log
        
        return None
    except Exception as e:
        logger.error(f"Failed to get error log: {str(e)}")
        return None

def clear_error_logs() -> bool:
    """
    Clear all error logs.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create empty error log file
        with open(ERROR_LOG_FILE, "w") as f:
            json.dump([], f)
        
        return True
    except Exception as e:
        logger.error(f"Failed to clear error logs: {str(e)}")
        return False

# Pydantic models
class ErrorLogRequest(BaseModel):
    error_message: str
    category: str = ErrorCategory.UNKNOWN
    severity: str = ErrorSeverity.ERROR
    component: str = "frontend"
    source: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ErrorLogResponse(BaseModel):
    error_id: str
    message: str = "Error logged successfully"

class ErrorLogEntry(BaseModel):
    id: str
    timestamp: str
    category: str
    severity: str
    component: str
    source: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    error_message: str
    error_traceback: Optional[str] = None
    context: Dict[str, Any] = {}

# Create FastAPI app
app = FastAPI(
    title="ADE Error Logging API",
    description="Minimal API for error logging in the ADE Platform",
    version="1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router
router = app.router

# Root endpoint
@app.get("/")
async def root():
    return {"message": "ADE Error Logging API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Route to log an error
@app.post("/error_logging/log", response_model=ErrorLogResponse)
async def create_error_log(error: ErrorLogRequest):
    try:
        error_id = log_error(
            error=error.error_message,
            category=error.category,
            severity=error.severity,
            component=error.component,
            source=error.source,
            user_id=error.user_id,
            request_id=error.request_id,
            context=error.context
        )
        
        return {"error_id": error_id, "message": "Error logged successfully"}
    except Exception as e:
        logger.error(f"Failed to log error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to log error: {str(e)}")

# Route to get error logs
@app.get("/error_logging/logs", response_model=List[ErrorLogEntry])
async def get_all_error_logs(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    component: Optional[str] = None
):
    try:
        logs = get_error_logs(
            limit=limit,
            offset=offset,
            category=category,
            severity=severity,
            component=component
        )
        
        return logs
    except Exception as e:
        logger.error(f"Failed to get error logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get error logs: {str(e)}")

# Route to get a specific error log
@app.get("/error_logging/logs/{error_id}", response_model=ErrorLogEntry)
async def get_specific_error_log(error_id: str):
    try:
        log = get_error_log(error_id)
        
        if not log:
            raise HTTPException(status_code=404, detail=f"Error log with ID {error_id} not found")
        
        return log
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get error log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get error log: {str(e)}")

# Route to clear all error logs
@app.delete("/error_logging/logs/clear")
async def clear_all_error_logs():
    try:
        success = clear_error_logs()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear error logs")
        
        return {"message": "All error logs cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear error logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear error logs: {str(e)}")

# Generate test error logs
@app.post("/error_logging/generate_test_logs")
async def generate_test_logs(count: int = 10):
    """Generate test error logs for development purposes"""
    try:
        categories = [
            ErrorCategory.AGENT,
            ErrorCategory.API,
            ErrorCategory.FRONTEND,
            ErrorCategory.SYSTEM,
            ErrorCategory.COORDINATION
        ]
        
        severities = [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.ERROR,
            ErrorSeverity.WARNING,
            ErrorSeverity.INFO
        ]
        
        components = ["backend", "frontend", "agent", "coordination"]
        
        sources = [
            "backend.main",
            "backend.agents.agent_coordinator",
            "backend.services.coordination.agent_interface",
            "frontend.src.components.ErrorBoundary",
            "frontend.src.services.api"
        ]
        
        error_messages = [
            "Connection refused",
            "Failed to initialize agent",
            "Invalid response format",
            "Timeout waiting for agent response",
            "Authentication failed",
            "Permission denied",
            "Resource not found",
            "Invalid input format",
            "Database connection error",
            "Memory limit exceeded"
        ]
        
        import random
        
        for i in range(count):
            log_error(
                error=random.choice(error_messages),
                category=random.choice(categories),
                severity=random.choice(severities),
                component=random.choice(components),
                source=random.choice(sources),
                user_id=f"test-user-{random.randint(1, 5)}",
                request_id=f"test-request-{uuid.uuid4()}",
                context={
                    "test": True,
                    "index": i,
                    "random_value": random.randint(1, 1000)
                }
            )
        
        return {"message": f"Generated {count} test error logs"}
    except Exception as e:
        logger.error(f"Failed to generate test logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate test logs: {str(e)}")

def main():
    """Run the error logging server"""
    logger.info("Starting ADE Error Logging Server")
    
    # Kill any existing process on port 8000
    import platform
    if platform.system() == "Windows":
        os.system("powershell -Command \"Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }\"")
    else:
        os.system("lsof -ti:8000 | xargs kill -9")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Import traceback for error logging
    import traceback
    main()
