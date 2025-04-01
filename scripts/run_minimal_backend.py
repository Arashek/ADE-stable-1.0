#!/usr/bin/env python
"""
Minimal Backend Runner for ADE

This script runs a minimal version of the backend server with only the essential
components needed for the Agent Coordination System to function.
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_minimal_backend():
    """Run a minimal version of the backend server"""
    from fastapi import FastAPI, APIRouter
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    # Create FastAPI app
    app = FastAPI(title="ADE Platform - Minimal Backend")
    
    # Configure CORS
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create a basic health check route
    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "message": "ADE Minimal Backend is running",
            "version": "1.0.0"
        }
    
    # Create a basic API router for the coordination system
    coord_router = APIRouter(prefix="/api/coordination", tags=["coordination"])
    
    @coord_router.get("/status")
    async def coordination_status():
        return {
            "status": "operational",
            "agents": ["design_agent", "development_agent", "validation_agent"],
            "message": "Agent Coordination System is running"
        }
    
    # Include the router
    app.include_router(coord_router)
    
    # Run the server
    logger.info("Starting minimal ADE backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.parent)
    sys.path.insert(0, project_root)
    
    try:
        run_minimal_backend()
    except Exception as e:
        logger.error(f"Error running minimal backend: {str(e)}")
        sys.exit(1)
