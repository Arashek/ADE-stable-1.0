import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)

class ProjectManager:
    """Manages projects in the ADE Platform"""
    
    def __init__(self, projects_dir: str = "projects"):
        """Initialize the project manager
        
        Args:
            projects_dir: Directory for storing projects
        """
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
    def create_project(self, name: str, config: Dict) -> bool:
        """Create a new project
        
        Args:
            name: Project name
            config: Project configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create project directory
            project_dir = self.projects_dir / name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create project structure
            (project_dir / "src").mkdir()
            (project_dir / "tests").mkdir()
            (project_dir / "docs").mkdir()
            (project_dir / "data").mkdir()
            
            # Save project configuration
            config_file = project_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            # Create project metadata
            metadata = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Created project: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project {name}: {str(e)}")
            return False
            
    def get_project(self, name: str) -> Optional[Dict]:
        """Get project information
        
        Args:
            name: Project name
            
        Returns:
            Dict: Project information if found, None otherwise
        """
        try:
            project_dir = self.projects_dir / name
            if not project_dir.exists():
                return None
                
            # Load project configuration
            config_file = project_dir / "config.yaml"
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            # Load project metadata
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            return {
                "name": name,
                "config": config,
                "metadata": metadata,
                "directory": str(project_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get project {name}: {str(e)}")
            return None
            
    def update_project(self, name: str, config: Dict) -> bool:
        """Update project configuration
        
        Args:
            name: Project name
            config: Updated project configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = self.projects_dir / name
            if not project_dir.exists():
                return False
                
            # Update project configuration
            config_file = project_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            # Update metadata
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            metadata["updated_at"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated project: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project {name}: {str(e)}")
            return False
            
    def delete_project(self, name: str) -> bool:
        """Delete a project
        
        Args:
            name: Project name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = self.projects_dir / name
            if not project_dir.exists():
                return False
                
            # Remove project directory
            import shutil
            shutil.rmtree(project_dir)
            
            logger.info(f"Deleted project: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {name}: {str(e)}")
            return False
            
    def list_projects(self) -> List[Dict]:
        """List all projects
        
        Returns:
            List[Dict]: List of project information
        """
        try:
            projects = []
            for project_dir in self.projects_dir.iterdir():
                if project_dir.is_dir():
                    project = self.get_project(project_dir.name)
                    if project:
                        projects.append(project)
            return projects
            
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            return []
            
    def get_project_status(self, name: str) -> Optional[str]:
        """Get project status
        
        Args:
            name: Project name
            
        Returns:
            str: Project status if found, None otherwise
        """
        try:
            project = self.get_project(name)
            if project:
                return project["metadata"]["status"]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get project status for {name}: {str(e)}")
            return None
            
    def set_project_status(self, name: str, status: str) -> bool:
        """Set project status
        
        Args:
            name: Project name
            status: New project status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = self.projects_dir / name
            if not project_dir.exists():
                return False
                
            metadata_file = project_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            metadata["status"] = status
            metadata["updated_at"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated project status for {name}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set project status for {name}: {str(e)}")
            return False 