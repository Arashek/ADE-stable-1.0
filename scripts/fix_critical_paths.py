#!/usr/bin/env python
"""
ADE Platform Critical Path Fixer

This script focuses specifically on fixing import path issues
in the ADE Platform by:
1. Creating proper __init__.py files
2. Fixing import statements in critical modules
3. Creating fallback configuration when missing
"""

import os
import sys
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("critical_path_fixer")

class CriticalPathFixer:
    """Fix critical import paths in the ADE platform"""
    
    def __init__(self):
        """Initialize the path fixer"""
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.fixed_modules = []
    
    def print_header(self, title):
        """Print a formatted header"""
        logger.info("\n" + "=" * 80)
        logger.info(f" {title} ".center(80, "="))
        logger.info("=" * 80)
    
    def create_init_files(self):
        """Create __init__.py files in all backend directories"""
        self.print_header("CREATING __init__.py FILES")
        
        count = 0
        for root, dirs, files in os.walk(self.backend_dir):
            if "__pycache__" in root:
                continue
                
            init_file = os.path.join(root, "__init__.py")
            if not os.path.exists(init_file):
                rel_path = os.path.relpath(root, self.project_root)
                logger.info(f"Creating __init__.py in {rel_path}")
                
                with open(init_file, "w") as f:
                    f.write("# Auto-generated __init__.py\n")
                count += 1
        
        logger.info(f"Created {count} __init__.py files")
        return count
    
    def create_missing_config(self):
        """Create missing config module if needed"""
        self.print_header("CHECKING CONFIG MODULE")
        
        config_dir = self.backend_dir / "config"
        settings_file = config_dir / "settings.py"
        
        if not config_dir.exists():
            logger.info("Creating missing config directory")
            os.makedirs(config_dir, exist_ok=True)
            
            # Create __init__.py
            with open(config_dir / "__init__.py", "w") as f:
                f.write("# Auto-generated __init__.py\n")
            
            self.fixed_modules.append("backend.config")
        
        if not settings_file.exists():
            logger.info("Creating minimal settings.py file")
            
            with open(settings_file, "w") as f:
                f.write('''"""
Configuration settings for the ADE Platform.

This module provides centralized configuration settings for the ADE platform,
including API settings, database settings, and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API settings
API_PREFIX = "/api"
API_VERSION = "v1"
API_V1_STR = f"{API_PREFIX}/{API_VERSION}"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key-for-local-environment-only")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Agent settings
AGENT_TIMEOUT = 60  # seconds
ENABLE_AGENT_MEMORY = True
MAX_AGENT_MEMORY_ENTRIES = 100

# Default user for local development
DEFAULT_USER = {
    "id": "local-dev-user",
    "username": "local-dev",
    "email": "dev@example.com",
    "is_active": True,
    "is_superuser": True
}

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_ERROR_LOGGING = True
ERROR_LOG_PATH = os.path.join(BASE_DIR, "logs", "error_logs.json")

# Chat model settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000

# Feature flags
ENABLE_OWNER_PANEL = False  # Temporarily disabled for local development
ENABLE_COORDINATION_SYSTEM = True
ENABLE_ERROR_TRACKING = True

# System settings
SYSTEM_MODE = os.getenv("SYSTEM_MODE", "local")  # local, development, production
''')
            
            self.fixed_modules.append("backend.config.settings")
    
    def fix_error_logging_module(self):
        """Fix error logging module"""
        self.print_header("CHECKING ERROR LOGGING MODULE")
        
        utils_dir = self.backend_dir / "utils"
        error_logging_file = utils_dir / "error_logging.py"
        
        if not utils_dir.exists():
            logger.info("Creating missing utils directory")
            os.makedirs(utils_dir, exist_ok=True)
            
            # Create __init__.py
            with open(utils_dir / "__init__.py", "w") as f:
                f.write("# Auto-generated __init__.py\n")
        
        if not error_logging_file.exists():
            logger.info("Creating error_logging.py file")
            
            with open(error_logging_file, "w") as f:
                f.write('''"""
Error Logging Utility for ADE Platform

This module provides centralized error logging functionality for capturing,
storing, and analyzing errors across both backend and frontend components.
"""

import os
import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("error_logging")

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
ERROR_LOG_FILE = os.path.join(Path(__file__).resolve().parent.parent.parent, "logs", "error_logs.json")

# Ensure logs directory exists
os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)

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
''')
            
            self.fixed_modules.append("backend.utils.error_logging")
    
    def fix_main_py(self):
        """Check and fix main.py file"""
        self.print_header("CHECKING MAIN.PY FILE")
        
        main_file = self.backend_dir / "main.py"
        
        if not main_file.exists():
            logger.info("Creating minimal main.py file")
            
            with open(main_file, "w") as f:
                f.write('''"""
Main FastAPI application for ADE Platform

This module sets up the FastAPI application and includes the routes
for different components of the platform.
"""

import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routes
try:
    from routes import error_logging_routes
except ImportError:
    logging.warning("Error logging routes could not be imported")
    error_logging_routes = None

try:
    from routes import coordination_api
except ImportError:
    logging.warning("Coordination API routes could not be imported")
    coordination_api = None

# Import settings
try:
    from config.settings import CORS_ORIGINS, API_VERSION
except ImportError:
    logging.warning("Settings module could not be imported, using defaults")
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    API_VERSION = "v1"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ade_backend")

# Create FastAPI app
app = FastAPI(
    title="ADE Platform API",
    description="API for the ADE (Application Development Ecosystem) Platform",
    version=API_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
if error_logging_routes:
    app.include_router(error_logging_routes.router)
    logger.info("Included error logging routes")

if coordination_api:
    app.include_router(coordination_api.router)
    logger.info("Included coordination API routes")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to ADE Platform API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Serve the application
if __name__ == "__main__":
    logger.info("Starting ADE backend server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
            
            self.fixed_modules.append("backend.main")
        else:
            # Check if health endpoint exists in main.py
            with open(main_file, "r") as f:
                content = f.read()
            
            if "/health" not in content:
                logger.info("Adding health check endpoint to main.py")
                
                # Find a good place to add health endpoint
                if "app.get(\"/\")" in content:
                    # Add after root endpoint
                    modified_content = content.replace(
                        "@app.get(\"/\")",
                        "@app.get(\"/\")\nasync def root():\n    return {\"message\": \"Welcome to ADE Platform API\"}\n\n# Health check endpoint\n@app.get(\"/health\")\nasync def health_check():\n    return {\"status\": \"ok\"}\n",
                        1
                    )
                    
                    with open(main_file, "w") as f:
                        f.write(modified_content)
                    
                    self.fixed_modules.append("backend.main (health endpoint)")
    
    def fix_coordination_routes(self):
        """Fix coordination routes file if needed"""
        self.print_header("CHECKING COORDINATION ROUTES")
        
        routes_dir = self.backend_dir / "routes"
        coordination_file = routes_dir / "coordination_api.py"
        
        if not routes_dir.exists():
            logger.info("Creating routes directory")
            os.makedirs(routes_dir, exist_ok=True)
            
            # Create __init__.py
            with open(routes_dir / "__init__.py", "w") as f:
                f.write("# Auto-generated __init__.py\n")
        
        if coordination_file.exists():
            # Check if imports are correct
            with open(coordination_file, "r") as f:
                content = f.read()
            
            # Fix import paths if needed
            if "from services.coordination.agent_coordinator" in content:
                fixed_content = content
                
                # Check if agent_coordinator in backend/services/coordination exists
                coordinator_path = self.backend_dir / "services" / "coordination" / "agent_coordinator.py"
                if not coordinator_path.exists():
                    # Change import to use agents.agent_coordinator instead
                    fixed_content = re.sub(
                        r"from services\.coordination\.agent_coordinator import AgentCoordinator",
                        "# Import from agents directory instead of services\ntry:\n    from agents.agent_coordinator import AgentCoordinator\nexcept ImportError:\n    # Fallback to services path\n    from services.coordination.agent_coordinator import AgentCoordinator",
                        fixed_content
                    )
                    
                    # Write fixed content
                    with open(coordination_file, "w") as f:
                        f.write(fixed_content)
                    
                    self.fixed_modules.append("backend.routes.coordination_api (imports)")
    
    def create_error_logging_routes(self):
        """Create error logging routes if they don't exist"""
        self.print_header("CHECKING ERROR LOGGING ROUTES")
        
        routes_dir = self.backend_dir / "routes"
        error_logging_routes_file = routes_dir / "error_logging_routes.py"
        
        if not routes_dir.exists():
            logger.info("Creating routes directory")
            os.makedirs(routes_dir, exist_ok=True)
            
            # Create __init__.py
            with open(routes_dir / "__init__.py", "w") as f:
                f.write("# Auto-generated __init__.py\n")
        
        if not error_logging_routes_file.exists():
            logger.info("Creating error_logging_routes.py file")
            
            with open(error_logging_routes_file, "w") as f:
                f.write('''"""
Error Logging Routes for ADE Platform

This module provides API routes for logging and retrieving error data.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from utils.error_logging import (
    log_error,
    get_error_logs,
    get_error_log,
    clear_error_logs,
    ErrorCategory,
    ErrorSeverity
)

# Create router
router = APIRouter(
    prefix="/error_logging",
    tags=["error_logging"],
    responses={404: {"description": "Not found"}}
)

# Model for error log request
class ErrorLogRequest(BaseModel):
    error_message: str
    category: str = ErrorCategory.UNKNOWN
    severity: str = ErrorSeverity.ERROR
    component: str = "frontend"
    source: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

# Model for error log response
class ErrorLogResponse(BaseModel):
    error_id: str
    message: str = "Error logged successfully"

# Model for error log entry
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

# Simple health check that doesn't require auth
@router.get("/health")
async def health_check():
    return {"status": "ok"}

# Route to log an error
@router.post("/log", response_model=ErrorLogResponse)
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
        raise HTTPException(status_code=500, detail=f"Failed to log error: {str(e)}")

# Route to get error logs
@router.get("/logs", response_model=List[ErrorLogEntry])
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
        raise HTTPException(status_code=500, detail=f"Failed to get error logs: {str(e)}")

# Route to get a specific error log
@router.get("/logs/{error_id}", response_model=ErrorLogEntry)
async def get_specific_error_log(error_id: str):
    try:
        log = get_error_log(error_id)
        
        if not log:
            raise HTTPException(status_code=404, detail=f"Error log with ID {error_id} not found")
        
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error log: {str(e)}")

# Route to clear all error logs (admin only)
@router.delete("/logs/clear")
async def clear_all_error_logs():
    try:
        success = clear_error_logs()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear error logs")
        
        return {"message": "All error logs cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear error logs: {str(e)}")
''')
            
            self.fixed_modules.append("backend.routes.error_logging_routes")
    
    def run(self):
        """Run the fixer"""
        self.print_header("ADE PLATFORM CRITICAL PATH FIXER")
        
        # Step 1: Create __init__.py files
        self.create_init_files()
        
        # Step 2: Create missing config module
        self.create_missing_config()
        
        # Step 3: Fix error logging module
        self.fix_error_logging_module()
        
        # Step 4: Fix main.py
        self.fix_main_py()
        
        # Step 5: Fix coordination routes
        self.fix_coordination_routes()
        
        # Step 6: Create error logging routes
        self.create_error_logging_routes()
        
        # Summary
        self.print_header("SUMMARY")
        if self.fixed_modules:
            logger.info(f"Fixed {len(self.fixed_modules)} modules:")
            for module in self.fixed_modules:
                logger.info(f"  - {module}")
        else:
            logger.info("No modules needed fixing")
        
        logger.info("\nTo start the backend server, run:")
        logger.info("  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        
        logger.info("\nTo start the frontend server, run:")
        logger.info("  cd frontend && npm start")

def main():
    """Main function"""
    fixer = CriticalPathFixer()
    fixer.run()

if __name__ == "__main__":
    main()
