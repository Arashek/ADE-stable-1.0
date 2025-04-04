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
# Hardcoding format string *again* as a temporary measure until env var is fully cleared
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Revert to using settings.LOG_FORMAT now that env var conflict is resolved
# log_formatter = logging.Formatter(settings.LOG_FORMAT)
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
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ADE Platform Backend API",
    debug=settings.DEBUG 
)

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
        # logger.warning(f"Static files directory not found and could not be created: {static_dir}. Error: {e}")
        pass

# --- Default Error Handlers ---
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