import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
import yaml
import docker
from datetime import datetime

logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages deployments in the ADE Platform"""
    
    def __init__(self, deployments_dir: str = "deployments"):
        """Initialize the deployment manager
        
        Args:
            deployments_dir: Directory for storing deployment configurations
        """
        self.deployments_dir = Path(deployments_dir)
        self.deployments_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None
            
    def create_deployment(self, name: str, config: Dict) -> bool:
        """Create a new deployment configuration
        
        Args:
            name: Deployment name
            config: Deployment configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create deployment directory
            deployment_dir = self.deployments_dir / name
            deployment_dir.mkdir(parents=True, exist_ok=True)
            
            # Save deployment configuration
            config_file = deployment_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            # Create deployment metadata
            metadata = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            metadata_file = deployment_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Created deployment configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create deployment {name}: {str(e)}")
            return False
            
    def get_deployment(self, name: str) -> Optional[Dict]:
        """Get deployment information
        
        Args:
            name: Deployment name
            
        Returns:
            Dict: Deployment information if found, None otherwise
        """
        try:
            deployment_dir = self.deployments_dir / name
            if not deployment_dir.exists():
                return None
                
            # Load deployment configuration
            config_file = deployment_dir / "config.yaml"
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            # Load deployment metadata
            metadata_file = deployment_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            return {
                "name": name,
                "config": config,
                "metadata": metadata,
                "directory": str(deployment_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment {name}: {str(e)}")
            return None
            
    def deploy(self, name: str) -> bool:
        """Deploy a configuration
        
        Args:
            name: Deployment name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            deployment = self.get_deployment(name)
            if not deployment:
                return False
                
            config = deployment["config"]
            
            # Build Docker image
            if "dockerfile" in config:
                image_name = f"ade-platform-{name}:latest"
                self.docker_client.images.build(
                    path=str(deployment["directory"]),
                    dockerfile=config["dockerfile"],
                    tag=image_name
                )
                
            # Run containers
            if "services" in config:
                for service_name, service_config in config["services"].items():
                    container_name = f"ade-platform-{name}-{service_name}"
                    
                    # Stop existing container if any
                    try:
                        container = self.docker_client.containers.get(container_name)
                        container.stop()
                        container.remove()
                    except docker.errors.NotFound:
                        pass
                        
                    # Create and start new container
                    self.docker_client.containers.run(
                        image=service_config.get("image", image_name),
                        name=container_name,
                        environment=service_config.get("environment", {}),
                        ports=service_config.get("ports", {}),
                        volumes=service_config.get("volumes", {}),
                        detach=True
                    )
                    
            # Update deployment status
            self.set_deployment_status(name, "running")
            
            logger.info(f"Deployed: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy {name}: {str(e)}")
            self.set_deployment_status(name, "failed")
            return False
            
    def stop_deployment(self, name: str) -> bool:
        """Stop a deployment
        
        Args:
            name: Deployment name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            deployment = self.get_deployment(name)
            if not deployment:
                return False
                
            config = deployment["config"]
            
            # Stop containers
            if "services" in config:
                for service_name in config["services"]:
                    container_name = f"ade-platform-{name}-{service_name}"
                    try:
                        container = self.docker_client.containers.get(container_name)
                        container.stop()
                        container.remove()
                    except docker.errors.NotFound:
                        pass
                        
            # Update deployment status
            self.set_deployment_status(name, "stopped")
            
            logger.info(f"Stopped deployment: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop deployment {name}: {str(e)}")
            return False
            
    def list_deployments(self) -> List[Dict]:
        """List all deployments
        
        Returns:
            List[Dict]: List of deployment information
        """
        try:
            deployments = []
            for deployment_dir in self.deployments_dir.iterdir():
                if deployment_dir.is_dir():
                    deployment = self.get_deployment(deployment_dir.name)
                    if deployment:
                        deployments.append(deployment)
            return deployments
            
        except Exception as e:
            logger.error(f"Failed to list deployments: {str(e)}")
            return []
            
    def get_deployment_status(self, name: str) -> Optional[str]:
        """Get deployment status
        
        Args:
            name: Deployment name
            
        Returns:
            str: Deployment status if found, None otherwise
        """
        try:
            deployment = self.get_deployment(name)
            if deployment:
                return deployment["metadata"]["status"]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get deployment status for {name}: {str(e)}")
            return None
            
    def set_deployment_status(self, name: str, status: str) -> bool:
        """Set deployment status
        
        Args:
            name: Deployment name
            status: New deployment status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            deployment_dir = self.deployments_dir / name
            if not deployment_dir.exists():
                return False
                
            metadata_file = deployment_dir / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            metadata["status"] = status
            metadata["updated_at"] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated deployment status for {name}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set deployment status for {name}: {str(e)}")
            return False 