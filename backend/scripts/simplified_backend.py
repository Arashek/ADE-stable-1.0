"""
ADE Platform - Simplified Backend Startup
This script initializes only the essential services needed for local testing.
"""

import sys
import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add backend directory to path if not already there
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import our health endpoint router
from scripts.health_endpoint import health_router, update_component_status
# Import our Pydantic test endpoint router
from scripts.pydantic_test_endpoint import pydantic_test_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("simplified_backend.log")
    ]
)

logger = logging.getLogger(__name__)

# Minimal set of services required for testing
required_services = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize minimal services
    logger.info("Starting simplified backend with minimal services")
    
    try:
        # Initialize environment and configuration
        from services.utils.environment import EnvironmentManager
        env_manager = EnvironmentManager()
        env_manager.load_env_file(os.path.join(backend_dir, ".env"))
        logger.info("Environment configuration loaded successfully")
        
        # Initialize LLM client for agent testing
        from services.utils.llm import LLMClient
        llm_client = LLMClient()
        logger.info("LLM client initialized")
        
        # Update component statuses for health monitoring
        update_component_status("model_service", "running")
        update_component_status("agent_service", "running")
        update_component_status("orchestrator", "running")
        
        # Add services to app state
        app.state.env_manager = env_manager
        app.state.llm_client = llm_client
        
        logger.info("All essential services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down simplified backend")
    for service in required_services:
        try:
            await service.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down service {service.__class__.__name__}: {str(e)}")

# Create FastAPI app with limited functionality
app = FastAPI(
    title="ADE Platform - Simplified Backend",
    description="Simplified backend for local testing of ADE platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the health router
app.include_router(health_router)

# Include the Pydantic test router
app.include_router(pydantic_test_router)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Simplified backend is running"}

# Echo endpoint for testing
@app.post("/api/echo")
async def echo(request: Request):
    body = await request.json()
    return {"echo": body}

# Mock prompt processing endpoint
@app.post("/api/process_prompt")
async def process_prompt(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Use LLM client for processing if available
        if hasattr(app.state, "llm_client"):
            result = await app.state.llm_client.generate_text(prompt)
            return {
                "status": "success",
                "message": "Prompt processed successfully",
                "result": result
            }
        else:
            # Fallback to mock response
            return {
                "status": "success",
                "message": "Prompt processed successfully (mock)",
                "result": f"Processed prompt: {prompt}"
            }
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")

# Mock status endpoint
@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    return {
        "task_id": task_id,
        "status": "in_progress",
        "progress": 65,
        "current_step": "Generating application code",
        "steps_completed": ["Understanding requirements", "Planning architecture"],
        "steps_remaining": ["Testing code", "Packaging application"]
    }

if __name__ == "__main__":
    # Get host and port from environment or use defaults
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8003))
    
    logger.info(f"Starting simplified backend on http://{host}:{port}")
    uvicorn.run("simplified_backend:app", host=host, port=port, reload=True)
