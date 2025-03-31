from typing import Dict, Optional
from pydantic import BaseModel, Field
from uuid import UUID

class Project(BaseModel):
    """
    Project configuration
    """
    name: str
    description: str
    tech_stack: Optional[Dict] = None
    constraints: Optional[Dict] = None
    style_guide: Optional[Dict] = None
    quality_standards: Optional[Dict] = None
    deployment_config: Optional[Dict] = None

class AgentRequest(BaseModel):
    """
    Request model for agent service
    """
    request_type: str = Field(..., description="Type of request (create_project, update_project, analyze_code)")
    project: Optional[Project] = Field(None, description="Project configuration for creation")
    project_id: Optional[str] = Field(None, description="Project ID for updates")
    changes: Optional[Dict] = Field(None, description="Changes for project update")
    code: Optional[str] = Field(None, description="Code for analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "request_type": "create_project",
                "project": {
                    "name": "MyProject",
                    "description": "A web application with user authentication",
                    "tech_stack": {
                        "frontend": "react",
                        "backend": "fastapi",
                        "database": "mongodb"
                    }
                }
            }
        }

class AgentResponse(BaseModel):
    """
    Response model for agent service
    """
    task_id: str = Field(..., description="Unique identifier for the task")
    status: str = Field(..., description="Current status of the task")
    result: Optional[Dict] = Field(None, description="Task result when completed")
    error: Optional[str] = Field(None, description="Error message if task failed")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "result": {
                    "project_id": "proj-123",
                    "status": "success",
                    "files_created": 10,
                    "tests_generated": 5
                }
            }
        }
