"""
Health endpoint for the ADE platform backend.
This provides basic status information about the backend services
to support diagnostic monitoring from the frontend.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import platform
import psutil
import time
import sys
from typing import Dict, List, Optional

# Create a router for health-related endpoints
health_router = APIRouter(tags=["health"])

class HealthStatus(BaseModel):
    """Health status information for the ADE platform backend."""
    
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: float = 0
    python_version: str = ""
    platform: str = ""
    memory_usage: Dict[str, float] = {}
    cpu_percent: float = 0.0
    uptime_seconds: float = 0.0
    components: Dict[str, str] = {}
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": 1625147892.123,
                "python_version": "3.9.7",
                "platform": "Windows-10-10.0.19041-SP0",
                "memory_usage": {
                    "total": 16.0,
                    "available": 8.0,
                    "percent": 50.0
                },
                "cpu_percent": 25.5,
                "uptime_seconds": 3600.0,
                "components": {
                    "model_service": "running",
                    "agent_service": "running",
                    "orchestrator": "running"
                }
            }
        }
    }

# Track the start time of the server
START_TIME = time.time()

# Track the health status of components
COMPONENT_STATUS = {
    "model_service": "initializing",
    "agent_service": "initializing",
    "orchestrator": "initializing"
}

@health_router.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Get the current health status of the ADE platform backend.
    
    Returns:
        HealthStatus: The current health status.
    """
    # Get system information
    memory = psutil.virtual_memory()
    memory_info = {
        "total": round(memory.total / (1024**3), 2),  # GB
        "available": round(memory.available / (1024**3), 2),  # GB
        "percent": memory.percent
    }
    
    # Get component status
    components = COMPONENT_STATUS.copy()
    
    # Create health response
    health_response = HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=time.time(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=platform.platform(),
        memory_usage=memory_info,
        cpu_percent=psutil.cpu_percent(interval=0.1),
        uptime_seconds=time.time() - START_TIME,
        components=components
    )
    
    return health_response

def update_component_status(component: str, status: str):
    """
    Update the status of a component.
    
    Args:
        component: The name of the component.
        status: The new status of the component.
    """
    if component in COMPONENT_STATUS:
        COMPONENT_STATUS[component] = status
