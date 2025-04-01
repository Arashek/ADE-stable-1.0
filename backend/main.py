import logging
import logging.handlers
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, Any
import asyncio
import psutil

from config.settings import settings
from routes.owner_panel_routes import router as owner_panel_router
from routes.coordination_api import router as coordination_router
from services.owner_panel_service import OwnerPanelService
from services.coordination.agent_coordinator import AgentCoordinator
# Temporarily disabled memory services for initial Owner Panel testing
# from services.memory.memory_service import memory_service
# from services.memory.api.memory_api import router as memory_router
# Temporarily disabled visual perception for initial Owner Panel testing
# from services.mcp.visual_perception_mcp import get_visual_perception_router
# Temporarily disabled for local testing
# from services.monitoring import metrics_middleware, metrics_endpoint, update_resource_metrics

# Import error logging system
from utils.error_logging import log_error, ErrorCategory, ErrorSeverity
from routes.error_logging_routes import router as error_logging_router

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.handlers.RotatingFileHandler(
            settings.get_log_file_path(),
            maxBytes=settings.LOG_MAX_SIZE,
            backupCount=settings.LOG_BACKUP_COUNT
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    try:
        # Initialize services
        app.state.owner_service = OwnerPanelService()
        
        # Initialize agent coordinator
        app.state.agent_coordinator = AgentCoordinator()
        # Initialize agents asynchronously
        asyncio.create_task(app.state.agent_coordinator._initialize_agents())
        
        # Initialize memory service if enabled
        if settings.MEMORY_ENABLED:
            # await memory_service.initialize()
            # app.state.memory_service = memory_service
            logger.info("Memory service initialization skipped")
        
        # Initialize Visual Perception MCP
        # app.state.visual_perception_router = get_visual_perception_router(
        #     # memory_service=app.state.memory_service if settings.MEMORY_ENABLED else None,
        #     memory_service=None,
        #     agent_coordinator=app.state.agent_coordinator
        # )
        logger.info("Visual Perception MCP initialization skipped")
        
        logger.info("Application services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing application services: {str(e)}")
        raise

    yield

    # Shutdown
    try:
        # Cleanup services
        await app.state.owner_service.cleanup()
        
        # Shutdown memory service if enabled
        if settings.MEMORY_ENABLED:
            # await memory_service.shutdown()
            logger.info("Memory service shutdown skipped")
            
        logger.info("Application services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up application services: {str(e)}")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for ADE Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a simple health check route for testing
@app.get("/health")
async def health_check():
    return {"status": "ok", "owner_panel_enabled": True}

# Include routers
app.include_router(owner_panel_router, prefix=settings.API_PREFIX)
app.include_router(coordination_router)
app.include_router(error_logging_router, prefix=settings.API_PREFIX)

# Include memory router if enabled
if settings.MEMORY_ENABLED:
    # app.include_router(memory_router, prefix=settings.API_PREFIX)
    logger.info("Memory API routes registration skipped")
    logger.info("Memory API is disabled")

# Include Visual Perception MCP router
# app.include_router(app.state.visual_perception_router)
logger.info("Visual Perception MCP routes registration skipped")

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "message": "Internal server error"
        }
    )

# API documentation
@app.get("/docs")
async def get_api_docs():
    """Get API documentation"""
    return app.openapi()

def start():
    """Start the application"""
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL.lower()
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise

if __name__ == "__main__":
    start()