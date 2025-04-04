# backend/main.py - Rewritten for clarity and Pydantic v2 compatibility

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
try:
    from config.settings import settings
except ImportError as e:
    print(f"FATAL: Error importing settings: {e}")
    print("Ensure backend/config/settings.py exists and is configured correctly.")
    sys.exit(1)
except Exception as e: 
    print(f"FATAL: Unexpected error during settings import/init: {e}")
    sys.exit(1)

# Settings import successful (or program exited)

# Logging setup (using logger)
logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL.upper())
# Revert to using settings.LOG_FORMAT now that env var conflict is confirmed removed
# log_formatter = logging.Formatter(settings.LOG_FORMAT)
# Temporarily hardcode the format due to system env var interference
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
# Ensure log directory exists and add file handler if LOG_FILE is set
if settings.LOG_FILE:
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to console and file: {settings.LOG_FILE}")
    except Exception as e:
        logger.error(f"Failed to set up file logging: {e}")
else:
    logger.info("Logging to console only (LOG_FILE not set).")

# --- Core Application Imports ---
from fastapi import FastAPI, Request, status 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from contextlib import asynccontextmanager

# --- Project-Specific Imports ---
# Services
try:
    from services.owner_panel_service import OwnerPanelService
except ImportError as e:
    # logger.warning(f"OwnerPanelService could not be imported: {e}")
    OwnerPanelService = None

try:
    from services.coordination.agent_coordinator import AgentCoordinator
except ImportError as e:
    # logger.error(f"FATAL: AgentCoordinator could not be imported: {e}")
    sys.exit(1) 

# Routers (Import necessary routers)
try:
    from routes.coordination_api import router as coordination_router
except ImportError as e:
    # logger.error(f"FATAL: Coordination API routes could not be imported: {e}")
    sys.exit(1) 

try:
    from routes.error_logging_routes import router as error_logging_router
except ImportError as e:
    # logger.error(f"Error logging routes could not be imported: {e}. Error logging API will be unavailable.")
    error_logging_router = None
except Exception as e:
    # logger.error(f"Unexpected error importing error logging routes: {e}")
    error_logging_router = None

# --- FastAPI Application Setup ---
logger.info(f"Creating FastAPI app: {settings.APP_NAME} v{settings.APP_VERSION}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Initialize services
    logger.info("Application startup: Initializing services...")

    # Ensure global AgentCoordinator instance is created
    # await AgentCoordinator.get_instance()
    # logger.info("AgentCoordinator initialized.")

    # Example: Initialize database connection pool if needed
    # await initialize_database()

    # Initialize OwnerPanelService
    # await OwnerPanelService.get_instance()
    # logger.info("OwnerPanelService initialized.")

    logger.info("Service initialization complete.")
    yield
    # Shutdown logic: Cleanup services
    logger.info("Application shutdown: Cleaning up services...")
    # Example: Close database connections
    # await close_database()
    # Add cleanup for AgentCoordinator, OwnerPanelService if necessary
    logger.info("Service cleanup complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan # Assign the lifespan context manager
)

logger.info(f"FastAPI app created: {settings.APP_NAME} v{settings.APP_VERSION}")

# --- Middleware Registration ---
logger.info("Registering middleware...")
# Security Headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS, # Use the existing setting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
# Uncomment these as needed/developed
# from middleware.request_logging_middleware import RequestLoggingMiddleware
# app.add_middleware(RequestLoggingMiddleware)
# from middleware.validation_middleware import RequestValidationMiddleware
# app.add_middleware(RequestValidationMiddleware)
# from middleware.error_handling_middleware import ErrorHandlingMiddleware
# app.add_middleware(ErrorHandlingMiddleware)
logger.info("Middleware registration complete.")

# --- API Routers Inclusion ---
logger.info("Including API routers...")
# Placeholder: Include your actual routers here
# Example:
# from api.v1.endpoints import auth, users, agents
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])

# Include Admin and Core routers
from routes.management_routes import router as admin_router
from routes.core_routes import router as core_router
app.include_router(admin_router, prefix=settings.API_V1_STR + "/admin", tags=["admin"])
app.include_router(core_router, prefix=settings.API_V1_STR + "/core", tags=["core"])

# Include Agent router
from routes.agent_routes import router as agent_router
app.include_router(agent_router, prefix=settings.API_V1_STR + "/agents", tags=["agents"])

# Include Project router
from routes.project_management_routes import router as project_router
app.include_router(project_router, prefix=settings.API_V1_STR + "/projects", tags=["projects"])

# Include Coordination router
from routes.coordination_api import router as coordination_router
app.include_router(coordination_router, prefix=settings.API_V1_STR + "/coordination", tags=["coordination"])

# Include Error Logging router
from routes.error_logging_routes import router as error_logging_router
app.include_router(error_logging_router, prefix=settings.API_V1_STR + "/error-logging", tags=["error-logging"])

logger.info("API routers included.")

# --- Static Files ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    # logger.info(f"Mounted static files directory: {static_dir}")
else:
    try:
        os.makedirs(static_dir, exist_ok=True)
        if os.path.exists(static_dir):
             app.mount("/static", StaticFiles(directory=static_dir), name="static")
             # logger.info(f"Created and mounted static files directory: {static_dir}")
        else:
             # logger.warning(f"Failed to create static directory: {static_dir}")
             pass
    except OSError as e:
        logger.error(f"Static directory not found: {static_dir}")

# --- Exception Handlers ---
# (Add custom exception handlers here if needed)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4())) 
    # logger.warning(f"Validation Error (Request ID: {request_id}): {exc.errors()}")
    try:
        from utils.error_logging import log_error, ErrorCategory, ErrorSeverity
        if log_error: 
            log_error(error=str(exc.errors()), category=ErrorCategory.VALIDATION, severity=ErrorSeverity.WARNING,
                      component="api", source=str(request.url.path), request_id=request_id, context={"validation_details": exc.errors()})
    except Exception as log_exc:
        # logger.error(f"Failed to log validation error details: {log_exc}")
        pass

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Error",
            "detail": exc.errors(),
            "request_id": request_id
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4())) 
    # logger.error(f"Unhandled Exception (Request ID: {request_id}): {exc}", exc_info=True)
    try:
        from utils.error_logging import log_error, ErrorCategory, ErrorSeverity
        if log_error: 
             log_error(error=exc, category=ErrorCategory.API, severity=ErrorSeverity.ERROR,
                       component="api", source=str(request.url.path), request_id=request_id, context={"exception_type": type(exc).__name__})
    except Exception as log_exc:
        # logger.error(f"Failed to log general exception details: {log_exc}")
        pass

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred.",
            "request_id": request_id
        },
    )

# --- Health Check Endpoint ---
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "app_name": "Minimal ADE App",
        "app_version": "0.0.1"
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "app_name": settings.APP_NAME, 
        "app_version": settings.APP_VERSION 
    }

# --- Main Execution ---
if __name__ == "__main__":
    logger.info(f"Starting Uvicorn server on {settings.HOST}:{settings.PORT}...") 
    logger.debug(f"Detected Settings - Host: {settings.HOST}, Port: {settings.PORT}, Reload: {settings.RELOAD}, Workers: {settings.WORKERS}")

    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST, 
            port=settings.PORT, 
            reload=settings.RELOAD,
            workers=settings.WORKERS,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.critical(f"Failed to start Uvicorn: {e}", exc_info=True) 
        sys.exit(1)