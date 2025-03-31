from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from ..services.cicd_service import CICDService
from ..core.config import settings
from ..core.auth import get_current_user

router = APIRouter(prefix="/api/cicd", tags=["cicd"])

@router.post("/pipelines/{project_name}/config")
async def create_pipeline_config(
    project_name: str,
    config: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new pipeline configuration."""
    cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
    result = cicd_service.create_pipeline_config(project_name, config)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/pipelines/{project_name}/execute")
async def execute_pipeline(
    project_name: str,
    environment: str,
    current_user: Dict = Depends(get_current_user)
):
    """Execute the CI/CD pipeline for a project."""
    cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
    result = cicd_service.execute_pipeline(project_name, environment)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/pipelines/{project_name}/status")
async def get_pipeline_status(
    project_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get the current status of a pipeline."""
    cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
    result = cicd_service.get_pipeline_status(project_name)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.put("/pipelines/{project_name}/environments/{environment}")
async def update_environment_config(
    project_name: str,
    environment: str,
    config: Dict,
    current_user: Dict = Depends(get_current_user)
):
    """Update the configuration for a specific environment."""
    cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
    result = cicd_service.update_environment_config(
        project_name=project_name,
        environment=environment,
        config=config
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/pipelines/{project_name}/report")
async def generate_pipeline_report(
    project_name: str,
    current_user: Dict = Depends(get_current_user)
):
    """Generate a detailed report of pipeline execution."""
    cicd_service = CICDService(settings.PIPELINE_CONFIG_PATH)
    result = cicd_service.generate_pipeline_report(project_name)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result 