import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import yaml
from datetime import datetime

from .project_manager import ProjectManager
from .build_manager import BuildManager
from .deployment_manager import DeploymentManager

logger = logging.getLogger(__name__)

class PipelineManager:
    """Orchestrates the build and deployment pipeline in the ADE Platform"""
    
    def __init__(self, projects_dir: str = "projects", builds_dir: str = "builds", deployments_dir: str = "deployments"):
        """Initialize the pipeline manager
        
        Args:
            projects_dir: Directory for storing projects
            builds_dir: Directory for storing build artifacts
            deployments_dir: Directory for storing deployment configurations
        """
        self.project_manager = ProjectManager(projects_dir)
        self.build_manager = BuildManager(builds_dir)
        self.deployment_manager = DeploymentManager(deployments_dir)
        
    def create_pipeline(self, project_name: str, config: Dict) -> Optional[str]:
        """Create a new pipeline configuration
        
        Args:
            project_name: Name of the project
            config: Pipeline configuration
            
        Returns:
            str: Pipeline ID if successful, None otherwise
        """
        try:
            # Create project if it doesn't exist
            if not self.project_manager.get_project(project_name):
                project_config = {
                    "name": project_name,
                    "description": config.get("description", ""),
                    "type": config.get("type", "application"),
                    "version": config.get("version", "1.0.0")
                }
                if not self.project_manager.create_project(project_name, project_config):
                    return None
                    
            # Create build configuration
            build_config = {
                "project_name": project_name,
                "stages": config.get("build_stages", []),
                "dependencies": config.get("dependencies", {}),
                "environment": config.get("environment", {})
            }
            
            build_id = self.build_manager.create_build(project_name, build_config)
            if not build_id:
                return None
                
            # Create deployment configuration
            deployment_config = {
                "project_name": project_name,
                "build_id": build_id,
                "services": config.get("services", {}),
                "environment": config.get("environment", {}),
                "resources": config.get("resources", {})
            }
            
            if not self.deployment_manager.create_deployment(project_name, deployment_config):
                self.build_manager.clean_build(build_id)
                return None
                
            logger.info(f"Created pipeline for project: {project_name}")
            return build_id
            
        except Exception as e:
            logger.error(f"Failed to create pipeline for project {project_name}: {str(e)}")
            return None
            
    def run_pipeline(self, project_name: str) -> bool:
        """Run the complete pipeline for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get project information
            project = self.project_manager.get_project(project_name)
            if not project:
                return False
                
            # Get latest build
            builds = self.build_manager.list_builds(project_name)
            if not builds:
                return False
                
            latest_build = builds[-1]  # Most recent build
            build_id = latest_build["build_id"]
            
            # Update project status
            self.project_manager.set_project_status(project_name, "building")
            
            # Run build process
            if not self.build_manager.build(build_id):
                self.project_manager.set_project_status(project_name, "build_failed")
                return False
                
            # Update project status
            self.project_manager.set_project_status(project_name, "deploying")
            
            # Deploy the build
            if not self.deployment_manager.deploy(project_name):
                self.project_manager.set_project_status(project_name, "deploy_failed")
                return False
                
            # Update project status
            self.project_manager.set_project_status(project_name, "running")
            
            logger.info(f"Completed pipeline for project: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run pipeline for project {project_name}: {str(e)}")
            self.project_manager.set_project_status(project_name, "failed")
            return False
            
    def stop_pipeline(self, project_name: str) -> bool:
        """Stop the pipeline for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Stop deployment
            if not self.deployment_manager.stop_deployment(project_name):
                return False
                
            # Update project status
            self.project_manager.set_project_status(project_name, "stopped")
            
            logger.info(f"Stopped pipeline for project: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop pipeline for project {project_name}: {str(e)}")
            return False
            
    def get_pipeline_status(self, project_name: str) -> Optional[Dict]:
        """Get the current status of a project's pipeline
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dict: Pipeline status information if found, None otherwise
        """
        try:
            # Get project status
            project = self.project_manager.get_project(project_name)
            if not project:
                return None
                
            # Get latest build status
            builds = self.build_manager.list_builds(project_name)
            build_status = None
            if builds:
                latest_build = builds[-1]
                build_status = self.build_manager.get_build_status(latest_build["build_id"])
                
            # Get deployment status
            deployment_status = self.deployment_manager.get_deployment_status(project_name)
            
            return {
                "project_name": project_name,
                "project_status": project["metadata"]["status"],
                "build_status": build_status,
                "deployment_status": deployment_status,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status for project {project_name}: {str(e)}")
            return None
            
    def list_pipelines(self) -> List[Dict]:
        """List all pipelines
        
        Returns:
            List[Dict]: List of pipeline information
        """
        try:
            pipelines = []
            projects = self.project_manager.list_projects()
            
            for project in projects:
                project_name = project["name"]
                status = self.get_pipeline_status(project_name)
                if status:
                    pipelines.append(status)
                    
            return pipelines
            
        except Exception as e:
            logger.error(f"Failed to list pipelines: {str(e)}")
            return []
            
    def clean_pipeline(self, project_name: str) -> bool:
        """Clean up pipeline artifacts for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Stop pipeline if running
            self.stop_pipeline(project_name)
            
            # Clean builds
            builds = self.build_manager.list_builds(project_name)
            for build in builds:
                self.build_manager.clean_build(build["build_id"])
                
            # Clean deployment
            deployment_dir = self.deployment_manager.deployments_dir / project_name
            if deployment_dir.exists():
                deployment_dir.rmdir()
                
            logger.info(f"Cleaned pipeline for project: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean pipeline for project {project_name}: {str(e)}")
            return False 