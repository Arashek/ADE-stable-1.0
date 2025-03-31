"""
Container Template Repository

This module provides functionality for managing container templates for different types of applications.
Templates define the base configuration for containers, including images, resource requirements,
environment variables, and other settings.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

class ApplicationType(str, Enum):
    """Types of applications that can be containerized."""
    WEB_FRONTEND = "web_frontend"
    WEB_BACKEND = "web_backend"
    MOBILE = "mobile"
    DATA_PROCESSING = "data_processing"
    IOT = "iot"
    MACHINE_LEARNING = "machine_learning"
    MICROSERVICE = "microservice"
    FULLSTACK = "fullstack"

class TemplateType(str, Enum):
    """Types of container templates."""
    USER = "user"
    PROJECT = "project"
    APPLICATION = "application"

class TemplateResource(BaseModel):
    """Resource requirements for a container template."""
    cpu_min: str = Field(..., description="Minimum CPU allocation (e.g., '0.1' or '100m')")
    cpu_max: str = Field(..., description="Maximum CPU allocation (e.g., '1' or '1000m')")
    memory_min: str = Field(..., description="Minimum memory allocation (e.g., '64Mi' or '1Gi')")
    memory_max: str = Field(..., description="Maximum memory allocation (e.g., '512Mi' or '4Gi')")
    disk_min: str = Field(..., description="Minimum disk allocation (e.g., '1Gi')")
    disk_max: str = Field(..., description="Maximum disk allocation (e.g., '10Gi')")

class ContainerTemplate(BaseModel):
    """Template for creating containers."""
    id: str
    name: str
    description: str
    type: TemplateType
    application_type: Optional[ApplicationType] = None
    base_image: str
    version: str
    created_at: datetime
    updated_at: datetime
    resources: TemplateResource
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    ports: Dict[int, str] = Field(default_factory=dict)  # {port: description}
    volumes: Dict[str, str] = Field(default_factory=dict)  # {path: description}
    commands: List[str] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)
    security_settings: Dict[str, Union[str, bool]] = Field(default_factory=dict)

class TemplateRepository:
    """
    Container Template Repository
    
    Manages container templates for different types of applications, including:
    - Storing and retrieving templates
    - Versioning templates
    - Validating templates
    - Generating container configurations from templates
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the Template Repository.
        
        Args:
            templates_dir: Directory to store template files
        """
        self.templates: Dict[str, ContainerTemplate] = {}
        self.templates_dir = templates_dir or os.path.join(os.getcwd(), "data", "container_templates")
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load built-in templates
        self._load_built_in_templates()
        
        # Load custom templates from disk
        self._load_templates_from_disk()
        
        logger.info(f"Template Repository initialized with {len(self.templates)} templates")
    
    def _load_built_in_templates(self):
        """Load built-in templates."""
        # User container template
        user_template = ContainerTemplate(
            id="user-base",
            name="User Base Template",
            description="Base template for user containers",
            type=TemplateType.USER,
            base_image="ade/user-base:latest",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resources=TemplateResource(
                cpu_min="0.5",
                cpu_max="2",
                memory_min="512Mi",
                memory_max="4Gi",
                disk_min="5Gi",
                disk_max="20Gi"
            ),
            environment_variables={
                "ADE_ENVIRONMENT": "production"
            },
            security_settings={
                "encrypted": True,
                "network_policy": "restricted"
            }
        )
        self.templates[user_template.id] = user_template
        
        # Project container template
        project_template = ContainerTemplate(
            id="project-base",
            name="Project Base Template",
            description="Base template for project containers",
            type=TemplateType.PROJECT,
            base_image="ade/project-base:latest",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resources=TemplateResource(
                cpu_min="0.2",
                cpu_max="1",
                memory_min="256Mi",
                memory_max="2Gi",
                disk_min="1Gi",
                disk_max="10Gi"
            ),
            environment_variables={
                "ADE_ENVIRONMENT": "production"
            },
            security_settings={
                "encrypted": True,
                "network_policy": "project-only"
            }
        )
        self.templates[project_template.id] = project_template
        
        # Web frontend application template
        web_frontend_template = ContainerTemplate(
            id="app-web-frontend",
            name="Web Frontend Application Template",
            description="Template for web frontend applications",
            type=TemplateType.APPLICATION,
            application_type=ApplicationType.WEB_FRONTEND,
            base_image="ade/app-web-frontend:latest",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resources=TemplateResource(
                cpu_min="0.1",
                cpu_max="0.5",
                memory_min="128Mi",
                memory_max="1Gi",
                disk_min="500Mi",
                disk_max="2Gi"
            ),
            environment_variables={
                "NODE_ENV": "production"
            },
            ports={
                80: "HTTP",
                443: "HTTPS"
            },
            commands=["npm", "start"],
            security_settings={
                "encrypted": False,
                "network_policy": "public"
            }
        )
        self.templates[web_frontend_template.id] = web_frontend_template
        
        # Web backend application template
        web_backend_template = ContainerTemplate(
            id="app-web-backend",
            name="Web Backend Application Template",
            description="Template for web backend applications",
            type=TemplateType.APPLICATION,
            application_type=ApplicationType.WEB_BACKEND,
            base_image="ade/app-web-backend:latest",
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resources=TemplateResource(
                cpu_min="0.2",
                cpu_max="1",
                memory_min="256Mi",
                memory_max="2Gi",
                disk_min="1Gi",
                disk_max="5Gi"
            ),
            environment_variables={
                "PYTHON_ENV": "production"
            },
            ports={
                8000: "API"
            },
            commands=["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            security_settings={
                "encrypted": False,
                "network_policy": "internal"
            }
        )
        self.templates[web_backend_template.id] = web_backend_template
    
    def _load_templates_from_disk(self):
        """Load custom templates from disk."""
        if not os.path.exists(self.templates_dir):
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(file_path, "r") as f:
                        template_data = json.load(f)
                        template = ContainerTemplate(**template_data)
                        self.templates[template.id] = template
                except Exception as e:
                    logger.error(f"Error loading template from {file_path}: {e}")
    
    def _save_template_to_disk(self, template: ContainerTemplate):
        """
        Save a template to disk.
        
        Args:
            template: Template to save
        """
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
        
        file_path = os.path.join(self.templates_dir, f"{template.id}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(template.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {e}")
    
    def get_template(self, template_id: str) -> ContainerTemplate:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            The template
        """
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        return self.templates[template_id]
    
    def list_templates(
        self, 
        template_type: Optional[TemplateType] = None,
        application_type: Optional[ApplicationType] = None
    ) -> List[ContainerTemplate]:
        """
        List templates with optional filtering.
        
        Args:
            template_type: Filter by template type
            application_type: Filter by application type
            
        Returns:
            List of templates matching the filters
        """
        templates = list(self.templates.values())
        
        if template_type:
            templates = [t for t in templates if t.type == template_type]
        
        if application_type:
            templates = [t for t in templates if t.application_type == application_type]
        
        return templates
    
    def create_template(self, template: ContainerTemplate) -> ContainerTemplate:
        """
        Create a new template.
        
        Args:
            template: Template to create
            
        Returns:
            The created template
        """
        if template.id in self.templates:
            raise ValueError(f"Template already exists: {template.id}")
        
        self.templates[template.id] = template
        self._save_template_to_disk(template)
        
        logger.info(f"Template created: {template.id}")
        return template
    
    def update_template(self, template: ContainerTemplate) -> ContainerTemplate:
        """
        Update an existing template.
        
        Args:
            template: Template to update
            
        Returns:
            The updated template
        """
        if template.id not in self.templates:
            raise ValueError(f"Template not found: {template.id}")
        
        template.updated_at = datetime.now()
        self.templates[template.id] = template
        self._save_template_to_disk(template)
        
        logger.info(f"Template updated: {template.id}")
        return template
    
    def delete_template(self, template_id: str) -> None:
        """
        Delete a template.
        
        Args:
            template_id: ID of the template to delete
        """
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        # Check if it's a built-in template
        if template_id in ["user-base", "project-base", "app-web-frontend", "app-web-backend"]:
            raise ValueError(f"Cannot delete built-in template: {template_id}")
        
        del self.templates[template_id]
        
        # Delete template file
        file_path = os.path.join(self.templates_dir, f"{template_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.info(f"Template deleted: {template_id}")

# Singleton instance
template_repository = TemplateRepository()
