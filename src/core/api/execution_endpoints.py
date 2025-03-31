from fastapi import APIRouter, HTTPException, Depends, Body, Path, WebSocket, WebSocketDisconnect
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from ..environments.container_manager import ContainerManager, ContainerConfig, ExecutionResult
from ..security.auth import get_current_user
from ..models.user import User
from fastapi.responses import Response
import networkx as nx

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize container manager
container_manager = ContainerManager()

class ContainerDependencyRequest(BaseModel):
    """Request model for container dependencies."""
    name: str = Field(..., description="Name of the dependency container")
    image: str = Field(..., description="Docker image to use")
    environment: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    ports: Optional[Dict[str, str]] = Field(default=None, description="Port mappings")
    volumes: Optional[Dict[str, str]] = Field(default=None, description="Volume mappings")
    health_check: Optional[Dict[str, Any]] = Field(default=None, description="Health check configuration")
    depends_on: Optional[List[str]] = Field(default=None, description="Container dependencies")

class CodeExecutionRequest(BaseModel):
    """Request model for code execution."""
    code: str = Field(..., description="Code to execute")
    language: str = Field(..., description="Programming language")
    memory_limit: str = Field(default="512m", description="Memory limit for container")
    cpu_period: int = Field(default=100000, description="CPU period")
    cpu_quota: int = Field(default=50000, description="CPU quota (0.5 CPU)")
    network_disabled: bool = Field(default=True, description="Disable network access")
    timeout: int = Field(default=30, description="Execution timeout in seconds")
    max_output_size: int = Field(default=1024 * 1024, description="Maximum output size in bytes")
    max_log_size: int = Field(default=10 * 1024 * 1024, description="Maximum log size in bytes")
    log_retention_days: int = Field(default=7, description="Number of days to retain logs")
    dependencies: Optional[List[ContainerDependencyRequest]] = Field(default=None, description="Container dependencies")

    @validator('dependencies')
    def validate_dependencies(cls, v):
        """Validate container dependencies."""
        if v:
            # Check for circular dependencies
            graph = nx.DiGraph()
            for dep in v:
                graph.add_node(dep.name)
                if dep.depends_on:
                    for dep_name in dep.depends_on:
                        graph.add_edge(dep_name, dep.name)
            
            try:
                nx.topological_sort(graph)
            except nx.NetworkXUnfeasible:
                raise ValueError("Circular dependency detected")
        return v

class ExecutionResponse(BaseModel):
    """Response model for code execution."""
    execution_id: str
    status: str
    output: str
    error: Optional[str] = None
    exit_code: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    resource_usage: Optional[Dict[str, Any]] = None

@router.post("/run", response_model=ExecutionResponse)
async def run_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute code in an isolated container with optional dependencies."""
    try:
        # Create container configuration
        config = ContainerConfig(
            language=request.language,
            memory_limit=request.memory_limit,
            cpu_period=request.cpu_period,
            cpu_quota=request.cpu_quota,
            network_disabled=request.network_disabled,
            timeout=request.timeout,
            max_output_size=request.max_output_size,
            max_log_size=request.max_log_size,
            log_retention_days=request.log_retention_days
        )

        # Convert dependencies to ContainerDependency objects
        dependencies = None
        if request.dependencies:
            dependencies = [
                ContainerDependency(
                    name=dep.name,
                    image=dep.image,
                    environment=dep.environment,
                    ports=dep.ports,
                    volumes=dep.volumes,
                    health_check=dep.health_check,
                    depends_on=dep.depends_on
                )
                for dep in request.dependencies
            ]

        # Create container with dependencies and execute code
        execution_id = await container_manager.create_container_with_dependencies(
            request.code,
            config,
            dependencies
        )
        result = await container_manager.execute_code(execution_id, config)

        return ExecutionResponse(
            execution_id=result.execution_id,
            status=result.status,
            output=result.output,
            error=result.error,
            exit_code=result.exit_code,
            start_time=result.start_time,
            end_time=result.end_time,
            resource_usage=result.resource_usage
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution_status(
    execution_id: str = Path(..., description="Execution ID"),
    current_user: User = Depends(get_current_user)
):
    """Get the status and results of a code execution."""
    result = container_manager.get_execution_status(execution_id)
    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")

    return ExecutionResponse(
        execution_id=result.execution_id,
        status=result.status,
        output=result.output,
        error=result.error,
        exit_code=result.exit_code,
        start_time=result.start_time,
        end_time=result.end_time,
        resource_usage=result.resource_usage
    )

@router.delete("/{execution_id}")
async def stop_execution(
    execution_id: str = Path(..., description="Execution ID"),
    current_user: User = Depends(get_current_user)
):
    """Stop a running code execution."""
    try:
        await container_manager.stop_execution(execution_id)
        return {"status": "success", "message": "Execution stopped"}
    except Exception as e:
        logger.error(f"Error stopping execution: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.websocket("/interactive/{execution_id}")
async def interactive_execution(
    websocket: WebSocket,
    execution_id: str = Path(..., description="Execution ID"),
    current_user: User = Depends(get_current_user)
):
    """WebSocket endpoint for interactive code execution."""
    try:
        await websocket.accept()
        
        # Start interactive session
        await container_manager.start_interactive_session(execution_id, websocket)
        
        try:
            while True:
                # Keep the connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            await container_manager.stop_interactive_session(execution_id)
    except Exception as e:
        logger.error(f"Error in interactive session: {str(e)}")
        try:
            await websocket.close()
        except:
            pass

@router.get("/metrics")
async def get_metrics():
    """Get container metrics in Prometheus format."""
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain") 