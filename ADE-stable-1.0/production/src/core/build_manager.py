import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import yaml
import docker
from datetime import datetime
import shutil
import subprocess

logger = logging.getLogger(__name__)

class BuildManager:
    """Manages build processes in the ADE Platform"""
    
    def __init__(self, builds_dir: str = "builds"):
        """Initialize the build manager
        
        Args:
            builds_dir: Directory for storing build artifacts
        """
        self.builds_dir = Path(builds_dir)
        self.builds_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None
            
    def create_build(self, project_name: str, config: Dict) -> Optional[str]:
        """Create a new build configuration
        
        Args:
            project_name: Name of the project to build
            config: Build configuration
            
        Returns:
            str: Build ID if successful, None otherwise
        """
        try:
            # Generate build ID
            build_id = f"{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create build directory
            build_dir = self.builds_dir / build_id
            build_dir.mkdir(parents=True, exist_ok=True)
            
            # Save build configuration
            config_file = build_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            # Create build metadata
            metadata = {
                "build_id": build_id,
                "project_name": project_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "pending",
                "stages": []
            }
            
            metadata_file = build_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Created build configuration: {build_id}")
            return build_id
            
        except Exception as e:
            logger.error(f"Failed to create build for project {project_name}: {str(e)}")
            return None
            
    def get_build(self, build_id: str) -> Optional[Dict]:
        """Get build information
        
        Args:
            build_id: Build ID
            
        Returns:
            Dict: Build information if found, None otherwise
        """
        try:
            build_dir = self.builds_dir / build_id
            if not build_dir.exists():
                return None
                
            # Load build configuration
            config_file = build_dir / "config.yaml"
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            # Load build metadata
            metadata_file = build_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            return {
                "build_id": build_id,
                "config": config,
                "metadata": metadata,
                "directory": str(build_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get build {build_id}: {str(e)}")
            return None
            
    def build(self, build_id: str) -> bool:
        """Execute build process
        
        Args:
            build_id: Build ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            build = self.get_build(build_id)
            if not build:
                return False
                
            config = build["config"]
            build_dir = Path(build["directory"])
            
            # Update build status
            self.set_build_status(build_id, "building")
            
            # Execute build stages
            for stage in config.get("stages", []):
                stage_name = stage.get("name", "unknown")
                self.add_build_stage(build_id, stage_name, "running")
                
                try:
                    # Execute stage commands
                    if "commands" in stage:
                        for cmd in stage["commands"]:
                            subprocess.run(cmd, shell=True, check=True, cwd=build_dir)
                            
                    # Build Docker image if specified
                    if "dockerfile" in stage:
                        image_name = f"ade-platform-{build_id}-{stage_name}:latest"
                        self.docker_client.images.build(
                            path=str(build_dir),
                            dockerfile=stage["dockerfile"],
                            tag=image_name
                        )
                        
                    self.add_build_stage(build_id, stage_name, "completed")
                    
                except Exception as e:
                    self.add_build_stage(build_id, stage_name, "failed")
                    raise
                    
            # Update build status
            self.set_build_status(build_id, "completed")
            
            logger.info(f"Completed build: {build_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to build {build_id}: {str(e)}")
            self.set_build_status(build_id, "failed")
            return False
            
    def clean_build(self, build_id: str) -> bool:
        """Clean build artifacts
        
        Args:
            build_id: Build ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            build_dir = self.builds_dir / build_id
            if not build_dir.exists():
                return False
                
            # Remove build directory
            shutil.rmtree(build_dir)
            
            logger.info(f"Cleaned build: {build_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean build {build_id}: {str(e)}")
            return False
            
    def list_builds(self, project_name: Optional[str] = None) -> List[Dict]:
        """List all builds
        
        Args:
            project_name: Optional project name to filter builds
            
        Returns:
            List[Dict]: List of build information
        """
        try:
            builds = []
            for build_dir in self.builds_dir.iterdir():
                if build_dir.is_dir():
                    build = self.get_build(build_dir.name)
                    if build and (not project_name or build["metadata"]["project_name"] == project_name):
                        builds.append(build)
            return builds
            
        except Exception as e:
            logger.error(f"Failed to list builds: {str(e)}")
            return []
            
    def get_build_status(self, build_id: str) -> Optional[str]:
        """Get build status
        
        Args:
            build_id: Build ID
            
        Returns:
            str: Build status if found, None otherwise
        """
        try:
            build = self.get_build(build_id)
            if build:
                return build["metadata"]["status"]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get build status for {build_id}: {str(e)}")
            return None
            
    def set_build_status(self, build_id: str, status: str) -> bool:
        """Set build status
        
        Args:
            build_id: Build ID
            status: New build status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            build_dir = self.builds_dir / build_id
            if not build_dir.exists():
                return False
                
            metadata_file = build_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            metadata["status"] = status
            metadata["updated_at"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated build status for {build_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set build status for {build_id}: {str(e)}")
            return False
            
    def add_build_stage(self, build_id: str, stage_name: str, status: str) -> bool:
        """Add or update build stage
        
        Args:
            build_id: Build ID
            stage_name: Stage name
            status: Stage status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            build_dir = self.builds_dir / build_id
            if not build_dir.exists():
                return False
                
            metadata_file = build_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            # Update or add stage
            stage = {"name": stage_name, "status": status, "updated_at": datetime.now().isoformat()}
            stages = metadata["stages"]
            for i, s in enumerate(stages):
                if s["name"] == stage_name:
                    stages[i] = stage
                    break
            else:
                stages.append(stage)
                
            metadata["updated_at"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated build stage for {build_id}: {stage_name} - {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add build stage for {build_id}: {str(e)}")
            return False 