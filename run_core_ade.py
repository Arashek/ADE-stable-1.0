#!/usr/bin/env python
"""
Core ADE Runner

This script runs the core ADE platform with only the essential components,
focusing on the agent coordination system which is central to ADE's functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('core_ade.log')
    ]
)
logger = logging.getLogger("core_ade")

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.append(backend_dir)

# Import FastAPI components
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import core ADE components
from services.coordination.agent_coordinator import AgentCoordinator
from services.coordination.agent_registry import AgentRegistry
from services.agents.specialized.validation_agent import ValidationAgent
from services.agents.specialized.design_agent import DesignAgent
from services.agents.specialized.architecture_agent import ArchitectureAgent
from services.agents.specialized.security_agent import SecurityAgent
from services.agents.specialized.performance_agent import PerformanceAgent

# Create FastAPI app
app = FastAPI(
    title="Core ADE Platform",
    description="Core Application Development Ecosystem with specialized AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for agent coordination
coordination_router = APIRouter(
    prefix="/api/coordination",
    tags=["coordination"]
)

# Initialize agent coordinator and registry
agent_coordinator = AgentCoordinator()
agent_registry = AgentRegistry()

# Register specialized agents
agent_registry.register_agent(ValidationAgent())
agent_registry.register_agent(DesignAgent())
agent_registry.register_agent(ArchitectureAgent())
agent_registry.register_agent(SecurityAgent())
agent_registry.register_agent(PerformanceAgent())

# API endpoints for agent coordination
@coordination_router.get("/agents")
async def get_agents():
    """Get all registered agents"""
    agents = agent_registry.get_all_agents()
    return {"agents": [{"id": agent.agent_id, "status": agent.status} for agent in agents]}

@coordination_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    agent = agent_registry.get_agent(agent_id)
    if agent:
        return {"id": agent.agent_id, "status": agent.status}
    return {"error": "Agent not found"}

@coordination_router.post("/tasks")
async def create_task(task_data: dict):
    """Create a new task for the agent coordinator"""
    task_id = agent_coordinator.create_task(task_data)
    return {"task_id": task_id, "status": "created"}

@coordination_router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get the status of a task"""
    task = agent_coordinator.get_task(task_id)
    if task:
        return task
    return {"error": "Task not found"}

# Include the coordination router
app.include_router(coordination_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

def main():
    """Run the core ADE platform"""
    logger.info("Starting core ADE platform")
    
    # Run the FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
