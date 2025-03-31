from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
import logging
from uuid import uuid4

from ..models.project_management import (
    Project, Task, Sprint, TimeEntry, ProjectTemplate,
    TaskStatus, SprintStatus, ProjectStatus
)
from ..config import settings
from ..integrations.github import GitHubClient
from ..integrations.gitlab import GitLabClient
from ..integrations.bitbucket import BitBucketClient
from ..container.container_manager import ContainerManager
from ..build.build_manager import BuildManager
from ..deployment.deployment_manager import DeploymentManager

logger = logging.getLogger(__name__)

class ProjectManagementService:
    """Unified project management service that integrates with ADE platform infrastructure"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self._initialize_storage()
        
        # Initialize integration clients
        self.github_client = GitHubClient()
        self.gitlab_client = GitLabClient()
        self.bitbucket_client = BitBucketClient()
        
        # Initialize infrastructure managers
        self.container_manager = ContainerManager()
        self.build_manager = BuildManager()
        self.deployment_manager = DeploymentManager()
        
    def _initialize_storage(self):
        """Initialize storage for project management data"""
        self.projects_path = self.storage_path / "projects"
        self.templates_path = self.storage_path / "templates"
        self.projects_path.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
    def create_project(self, name: str, description: str, owner: str, template_id: Optional[str] = None) -> Dict:
        """Create a new project with optional template"""
        try:
            project_id = f"PROJ-{uuid4().hex[:8]}"
            
            # Create project from template if specified
            if template_id:
                template = self.get_template(template_id)
                if template:
                    project = self._create_project_from_template(project_id, name, description, owner, template)
                else:
                    return {"status": "error", "message": "Template not found"}
            else:
                project = Project(
                    id=project_id,
                    name=name,
                    description=description,
                    owner=owner
                )
            
            # Save project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
            
            # Initialize development environment
            self._initialize_dev_environment(project)
            
            return {"status": "success", "data": project.dict()}
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def _create_project_from_template(self, project_id: str, name: str, description: str,
                                    owner: str, template: ProjectTemplate) -> Project:
        """Create a project using a template"""
        project = Project(
            id=project_id,
            name=name,
            description=description,
            owner=owner,
            settings=template.default_settings,
            container_config=template.default_container_config,
            build_config=template.default_build_config,
            deployment_config=template.default_deployment_config
        )
        
        # Apply template structure
        self._apply_template_structure(project, template)
        
        return project
        
    def _apply_template_structure(self, project: Project, template: ProjectTemplate):
        """Apply template structure to project"""
        # Create directory structure
        project_dir = self.projects_path / project.id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template files
        for source, target in template.structure.items():
            source_path = self.templates_path / template.id / source
            target_path = project_dir / target
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.exists():
                with open(source_path, 'r') as f:
                    content = f.read()
                with open(target_path, 'w') as f:
                    f.write(content)
                    
    def _initialize_dev_environment(self, project: Project):
        """Initialize development environment for project"""
        try:
            # Initialize container
            if project.container_config:
                container_id = self.container_manager.create_container(project.container_config)
                project.container_config["container_id"] = container_id
                
            # Initialize build environment
            if project.build_config:
                build_id = self.build_manager.initialize_build(project.id, project.build_config)
                project.build_config["build_id"] = build_id
                
            # Initialize deployment configuration
            if project.deployment_config:
                deployment_id = self.deployment_manager.initialize_deployment(
                    project.id, project.deployment_config
                )
                project.deployment_config["deployment_id"] = deployment_id
                
            # Save updated project configuration
            project_path = self.projects_path / f"{project.id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
        except Exception as e:
            logger.error(f"Error initializing dev environment: {str(e)}")
            raise
            
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        try:
            project_path = self.projects_path / f"{project_id}.json"
            if not project_path.exists():
                return None
                
            with open(project_path, 'r') as f:
                project_data = json.load(f)
                return Project(**project_data)
        except Exception as e:
            logger.error(f"Error getting project: {str(e)}")
            return None
            
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict:
        """Update project configuration"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            # Update project fields
            for field, value in updates.items():
                if hasattr(project, field):
                    setattr(project, field, value)
                    
            # Update metrics
            project.update_metrics()
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "data": project.dict()}
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Dict:
        """Create a new task in a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            task_id = f"TASK-{uuid4().hex[:8]}"
            task = Task(
                id=task_id,
                **task_data
            )
            
            project.tasks.append(task)
            project.update_metrics()
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "data": task.dict()}
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def create_sprint(self, project_id: str, sprint_data: Dict[str, Any]) -> Dict:
        """Create a new sprint in a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            sprint_id = f"SPRINT-{uuid4().hex[:8]}"
            sprint = Sprint(
                id=sprint_id,
                **sprint_data
            )
            
            project.sprints.append(sprint)
            project.update_metrics()
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "data": sprint.dict()}
        except Exception as e:
            logger.error(f"Error creating sprint: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def update_task_status(self, project_id: str, task_id: str, status: TaskStatus) -> Dict:
        """Update task status"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            task = next((t for t in project.tasks if t.id == task_id), None)
            if not task:
                return {"status": "error", "message": "Task not found"}
                
            task.status = status
            task.updated_at = datetime.now()
            project.update_metrics()
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "data": task.dict()}
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def log_time(self, project_id: str, task_id: str, user_id: str,
                 hours: float, description: str) -> Dict:
        """Log time spent on a task"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            task = next((t for t in project.tasks if t.id == task_id), None)
            if not task:
                return {"status": "error", "message": "Task not found"}
                
            time_entry_id = f"TIME-{uuid4().hex[:8]}"
            time_entry = TimeEntry(
                id=time_entry_id,
                task_id=task_id,
                user_id=user_id,
                hours=hours,
                description=description
            )
            
            task.time_entries.append(time_entry.dict())
            task.actual_hours += hours
            task.updated_at = datetime.now()
            project.update_metrics()
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "data": time_entry.dict()}
        except Exception as e:
            logger.error(f"Error logging time: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def get_sprint_tasks(self, project_id: str, sprint_id: str) -> Dict:
        """Get all tasks assigned to a sprint"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            sprint = next((s for s in project.sprints if s.id == sprint_id), None)
            if not sprint:
                return {"status": "error", "message": "Sprint not found"}
                
            sprint_tasks = [t for t in project.tasks if t.sprint_id == sprint_id]
            
            return {"status": "success", "data": [t.dict() for t in sprint_tasks]}
        except Exception as e:
            logger.error(f"Error getting sprint tasks: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def integrate_with_external_tool(self, project_id: str, tool_type: str,
                                  credentials: Dict[str, Any]) -> Dict:
        """Integrate with external project management tools"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            if tool_type not in ["jira", "trello", "asana"]:
                return {"status": "error", "message": "Unsupported tool type"}
                
            # Store integration credentials
            project.external_tool_integrations[tool_type] = {
                "credentials": credentials,
                "integrated_at": datetime.now().isoformat()
            }
            
            # Save updated project
            project_path = self.projects_path / f"{project_id}.json"
            with open(project_path, 'w') as f:
                json.dump(project.dict(), f, default=str)
                
            return {"status": "success", "message": f"Successfully integrated with {tool_type}"}
        except Exception as e:
            logger.error(f"Error integrating with external tool: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def get_project_metrics(self, project_id: str) -> Dict:
        """Get project metrics and statistics"""
        try:
            project = self.get_project(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
                
            # Update metrics before returning
            project.update_metrics()
            
            return {
                "status": "success",
                "data": {
                    "total_tasks": project.total_tasks,
                    "completed_tasks": project.completed_tasks,
                    "total_sprints": project.total_sprints,
                    "completed_sprints": project.completed_sprints,
                    "total_story_points": project.total_story_points,
                    "completed_story_points": project.completed_story_points,
                    "average_velocity": project.average_velocity,
                    "performance_metrics": project.performance_metrics
                }
            }
        except Exception as e:
            logger.error(f"Error getting project metrics: {str(e)}")
            return {"status": "error", "message": str(e)} 