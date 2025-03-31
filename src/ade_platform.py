import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import logging

from .utils.settings import get_settings
from .utils.logging import setup_logging, get_logger
from .middleware.rate_limit import RateLimitMiddleware
from .database.connection import DatabaseManager
from .tools.architect_interface import ArchitectInterface
from .tools.self_improvement.cli import main as self_improvement_main
from .tools.web_interface import WebInterface
from core.agents.agent_registry import AgentRegistry
from core.providers import ProviderRegistry
from core.config import settings
from core.agent.base import AgentCapability

# Initialize settings and logging
settings = get_settings()
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="ADE Platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# Initialize interfaces
project_dir = os.getenv("ADE_PROJECT_DIR", settings.ADE_PROJECT_DIR)
architect = ArchitectInterface(project_dir)
web_interface = WebInterface(project_dir)

class ADEPlatform:
    """Main ADE platform application"""
    
    def __init__(self):
        self.provider_registry = ProviderRegistry()
        self.agent_registry = AgentRegistry()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the ADE platform"""
        try:
            # Initialize provider registry
            await self.provider_registry.initialize()
            
            # Initialize workflow agents
            self.agent_registry.initialize_workflow_agents(self.provider_registry)
            
            self.logger.info("ADE platform initialized successfully")
            return {"status": "success", "message": "Platform initialized"}
        except Exception as e:
            self.logger.error(f"Error initializing ADE platform: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def handle_workflow_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a workflow-related request"""
        try:
            request_type = request.get("type")
            
            if request_type == "git_operation":
                return await self._handle_git_request(request)
            elif request_type == "code_review":
                return await self._handle_code_review_request(request)
            elif request_type == "cicd_pipeline":
                return await self._handle_cicd_request(request)
            elif request_type == "project_management":
                return await self._handle_project_request(request)
            else:
                return {"status": "error", "message": f"Unknown request type: {request_type}"}
        except Exception as e:
            self.logger.error(f"Error handling workflow request: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def _handle_git_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git-related requests"""
        workflow_manager = self.agent_registry.get_agents_by_capability(AgentCapability.GIT_OPERATIONS)[0]
        return await workflow_manager.process_task({
            "type": "git_operation",
            "operation": request.get("operation"),
            **request.get("parameters", {})
        })
        
    async def _handle_code_review_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code review requests"""
        workflow_manager = self.agent_registry.get_agents_by_capability(AgentCapability.CODE_REVIEW)[0]
        
        # Start collaboration with code analysis agent if needed
        if request.get("needs_analysis", False):
            code_analysts = self.agent_registry.get_agents_by_capability(AgentCapability.CODE_ANALYSIS)
            if code_analysts:
                collaboration = self.agent_registry.start_collaboration(
                    source_agent_id=workflow_manager.agent_id,
                    target_agent_id=code_analysts[0].agent_id,
                    task=request
                )
                if collaboration["status"] == "success":
                    return await workflow_manager.collaborate(code_analysts[0], request)
                    
        return await workflow_manager.process_task({
            "type": "code_review",
            "operation": request.get("operation"),
            **request.get("parameters", {})
        })
        
    async def _handle_cicd_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CI/CD pipeline requests"""
        workflow_manager = self.agent_registry.get_agents_by_capability(AgentCapability.CICD_PIPELINE)[0]
        
        # Start collaboration with resource optimization agent if needed
        if request.get("needs_optimization", False):
            optimizers = self.agent_registry.get_agents_by_capability(AgentCapability.RESOURCE_OPTIMIZATION)
            if optimizers:
                collaboration = self.agent_registry.start_collaboration(
                    source_agent_id=workflow_manager.agent_id,
                    target_agent_id=optimizers[0].agent_id,
                    task=request
                )
                if collaboration["status"] == "success":
                    return await workflow_manager.collaborate(optimizers[0], request)
                    
        return await workflow_manager.process_task({
            "type": "cicd_pipeline",
            "operation": request.get("operation"),
            **request.get("parameters", {})
        })
        
    async def _handle_project_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project management requests"""
        workflow_manager = self.agent_registry.get_agents_by_capability(AgentCapability.PROJECT_MANAGEMENT)[0]
        
        # Start collaboration with planner agent if needed
        if request.get("needs_planning", False):
            planners = self.agent_registry.get_agents_by_capability(AgentCapability.TASK_PLANNING)
            if planners:
                collaboration = self.agent_registry.start_collaboration(
                    source_agent_id=workflow_manager.agent_id,
                    target_agent_id=planners[0].agent_id,
                    task=request
                )
                if collaboration["status"] == "success":
                    return await workflow_manager.collaborate(planners[0], request)
                    
        return await workflow_manager.process_task({
            "type": "project_management",
            "operation": request.get("operation"),
            **request.get("parameters", {})
        })
        
    async def shutdown(self):
        """Shutdown the ADE platform"""
        try:
            # End all active collaborations
            for collaboration_id in list(self.agent_registry.active_collaborations.keys()):
                await self.agent_registry.end_collaboration(collaboration_id)
                
            # Unregister all agents
            for agent_id in list(self.agent_registry.agents.keys()):
                await self.agent_registry.unregister_agent(agent_id)
                
            self.logger.info("ADE platform shut down successfully")
            return {"status": "success", "message": "Platform shut down"}
        except Exception as e:
            self.logger.error(f"Error shutting down ADE platform: {str(e)}")
            return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize database connections
        await DatabaseManager.get_mongodb()
        DatabaseManager.get_redis()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await DatabaseManager.close_connections()
        logger.info("All services closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": [
            "architect_interface",
            "self_improvement",
            "project_management",
            "web_dashboard"
        ],
        "endpoints": {
            "dashboard": "/dashboard",
            "api_docs": "/docs" if settings.ENVIRONMENT == "development" else None
        }
    }

@app.get("/dashboard")
async def dashboard():
    """Serve the web dashboard"""
    return web_interface.app.get("/")

@app.post("/projects/new")
async def create_project(project_data: Dict[str, Any]):
    """Create a new project"""
    try:
        architect.start_new_project()
        return {"status": "success", "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/design")
async def request_design(project_id: str, requirements: Dict[str, Any]):
    """Request architectural design"""
    try:
        architect.request_design()
        return {"status": "success", "message": "Design request processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/implement")
async def request_implementation(project_id: str, component: Dict[str, Any]):
    """Request component implementation"""
    try:
        architect.request_implementation()
        return {"status": "success", "message": "Implementation request processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/improve")
async def request_improvements(project_id: str, improvements: Dict[str, Any]):
    """Request improvements"""
    try:
        architect.request_improvements()
        return {"status": "success", "message": "Improvement request processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """Get project status"""
    try:
        architect.check_status()
        return {"status": "success", "message": "Status retrieved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/report")
async def get_project_report(project_id: str):
    """Get project report"""
    try:
        architect.generate_report()
        return {"status": "success", "message": "Report generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connections
        mongodb = await DatabaseManager.get_mongodb()
        await mongodb.admin.command('ping')
        
        redis = DatabaseManager.get_redis()
        redis.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "redis": "connected",
                "ai_providers": "available"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

def main():
    """Main entry point"""
    try:
        # Create necessary directories
        Path(project_dir).mkdir(parents=True, exist_ok=True)
        
        # Start the FastAPI server
        uvicorn.run(
            "src.ade_platform:app",
            host="0.0.0.0",
            port=8000,
            log_level=settings.LOG_LEVEL.lower(),
            reload=settings.ENVIRONMENT == "development"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 