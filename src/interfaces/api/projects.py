from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ...core.project_manager import ProjectManager
from ...core.models.project import Project
from ...core.auth.auth_middleware import get_current_user
from ...core.models.user import User

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    """Project creation request"""
    name: str
    config: dict
    template: Optional[str] = None
    repository_url: Optional[str] = None
    branch: Optional[str] = None

class ProjectUpdate(BaseModel):
    """Project update request"""
    name: Optional[str] = None
    config: Optional[dict] = None
    status: Optional[str] = None

@router.post("", response_model=Project)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    try:
        project_manager = ProjectManager()
        new_project = await project_manager.create_project(
            name=project.name,
            config=project.config,
            template=project.template,
            repository_url=project.repository_url,
            branch=project.branch
        )
        
        if not new_project:
            raise HTTPException(
                status_code=400,
                detail="Failed to create project"
            )
            
        return new_project
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("", response_model=List[Project])
async def list_projects(
    current_user: User = Depends(get_current_user)
):
    """List all projects"""
    try:
        project_manager = ProjectManager()
        projects = await project_manager.list_projects()
        return projects
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    try:
        project_manager = ProjectManager()
        project = await project_manager.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return project
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update project details"""
    try:
        project_manager = ProjectManager()
        updated_project = await project_manager.update_project(
            project_id=project_id,
            name=project_update.name,
            config=project_update.config,
            status=project_update.status
        )
        
        if not updated_project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return updated_project
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a project"""
    try:
        project_manager = ProjectManager()
        success = await project_manager.delete_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return {"message": "Project deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/{project_id}/clone")
async def clone_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Clone a project"""
    try:
        project_manager = ProjectManager()
        cloned_project = await project_manager.clone_project(project_id)
        
        if not cloned_project:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return cloned_project
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/{project_id}/archive")
async def archive_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Archive a project"""
    try:
        project_manager = ProjectManager()
        success = await project_manager.archive_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return {"message": "Project archived successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/{project_id}/restore")
async def restore_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Restore an archived project"""
    try:
        project_manager = ProjectManager()
        success = await project_manager.restore_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
            
        return {"message": "Project restored successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 