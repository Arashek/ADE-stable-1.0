import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import shutil
import docker
from dataclasses import dataclass, field
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Configuration for model deployment"""
    model_name: str
    version: str
    environment: Dict
    resources: Dict
    scaling: Dict
    health_check: Dict
    metadata: Dict = field(default_factory=dict)

class ModelDeploymentManager:
    """Manages model deployment and versioning"""
    
    def __init__(self, models_dir: str = "models", deployments_dir: str = "deployments"):
        """Initialize the model deployment manager
        
        Args:
            models_dir: Directory containing trained models
            deployments_dir: Directory for deployment configurations
        """
        self.models_dir = Path(models_dir)
        self.deployments_dir = Path(deployments_dir)
        self.deployments_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None
            
    def deploy_model(self, config: DeploymentConfig) -> bool:
        """Deploy a model with specified configuration
        
        Args:
            config: Deployment configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create deployment directory
            deployment_dir = self.deployments_dir / f"{config.model_name}-{config.version}"
            deployment_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy model files
            if not self._copy_model_files(config.model_name, deployment_dir):
                return False
                
            # Create deployment configuration
            if not self._create_deployment_config(config, deployment_dir):
                return False
                
            # Build and deploy Docker container
            if not self._deploy_container(config, deployment_dir):
                return False
                
            logger.info(f"Successfully deployed model {config.model_name} version {config.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy model: {str(e)}")
            return False
            
    def _copy_model_files(self, model_name: str, deployment_dir: Path) -> bool:
        """Copy model files to deployment directory
        
        Args:
            model_name: Name of the model
            deployment_dir: Deployment directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Copy model file
            model_file = self.models_dir / f"{model_name}.h5"
            if not model_file.exists():
                logger.error(f"Model file not found: {model_file}")
                return False
                
            shutil.copy2(model_file, deployment_dir / "model.h5")
            
            # Copy metadata file
            metadata_file = self.models_dir / f"{model_name}_metadata.json"
            if metadata_file.exists():
                shutil.copy2(metadata_file, deployment_dir / "metadata.json")
                
            # Copy scaler if exists
            scaler_file = self.models_dir / f"{model_name}_scaler.pkl"
            if scaler_file.exists():
                shutil.copy2(scaler_file, deployment_dir / "scaler.pkl")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy model files: {str(e)}")
            return False
            
    def _create_deployment_config(self, config: DeploymentConfig, deployment_dir: Path) -> bool:
        """Create deployment configuration file
        
        Args:
            config: Deployment configuration
            deployment_dir: Deployment directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            deployment_config = {
                "model_name": config.model_name,
                "version": config.version,
                "environment": config.environment,
                "resources": config.resources,
                "scaling": config.scaling,
                "health_check": config.health_check,
                "metadata": config.metadata,
                "created_at": datetime.now().isoformat()
            }
            
            config_file = deployment_dir / "deployment_config.json"
            with open(config_file, 'w') as f:
                json.dump(deployment_config, f, indent=4)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to create deployment config: {str(e)}")
            return False
            
    def _deploy_container(self, config: DeploymentConfig, deployment_dir: Path) -> bool:
        """Deploy model as Docker container
        
        Args:
            config: Deployment configuration
            deployment_dir: Deployment directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.docker_client:
                logger.error("Docker client not available")
                return False
                
            # Create Dockerfile
            dockerfile_content = self._generate_dockerfile(config)
            dockerfile_path = deployment_dir / "Dockerfile"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
                
            # Build image
            image_name = f"{config.model_name}:{config.version}"
            self.docker_client.images.build(
                path=str(deployment_dir),
                dockerfile="Dockerfile",
                tag=image_name
            )
            
            # Create container
            container_config = {
                "image": image_name,
                "name": f"{config.model_name}-{config.version}",
                "environment": config.environment,
                "ports": config.resources.get("ports", {}),
                "mem_limit": config.resources.get("memory", "1g"),
                "cpu_count": config.resources.get("cpu", 1),
                "healthcheck": config.health_check,
                "detach": True
            }
            
            container = self.docker_client.containers.create(**container_config)
            container.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy container: {str(e)}")
            return False
            
    def _generate_dockerfile(self, config: DeploymentConfig) -> str:
        """Generate Dockerfile for model deployment
        
        Args:
            config: Deployment configuration
            
        Returns:
            str: Dockerfile content
        """
        return f"""
FROM python:3.8-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy model files
COPY model.h5 .
COPY metadata.json .
COPY scaler.pkl .
COPY deployment_config.json .

# Create API service
COPY api.py .

# Expose port
EXPOSE {config.resources.get("ports", {}).get("api", 8000)}

# Start service
CMD ["python", "api.py"]
"""
            
    def rollback_deployment(self, model_name: str, version: str) -> bool:
        """Rollback model deployment to previous version
        
        Args:
            model_name: Name of the model
            version: Version to rollback to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Stop current deployment
            current_container = self._get_deployment_container(model_name)
            if current_container:
                current_container.stop()
                current_container.remove()
                
            # Deploy previous version
            deployment_dir = self.deployments_dir / f"{model_name}-{version}"
            if not deployment_dir.exists():
                logger.error(f"Deployment directory not found: {deployment_dir}")
                return False
                
            # Load deployment config
            config_file = deployment_dir / "deployment_config.json"
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                
            config = DeploymentConfig(**config_data)
            
            # Redeploy container
            return self._deploy_container(config, deployment_dir)
            
        except Exception as e:
            logger.error(f"Failed to rollback deployment: {str(e)}")
            return False
            
    def _get_deployment_container(self, model_name: str) -> Optional[docker.models.containers.Container]:
        """Get currently deployed container for a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Optional[docker.models.containers.Container]: Container if found, None otherwise
        """
        try:
            containers = self.docker_client.containers.list(
                filters={"name": model_name}
            )
            return containers[0] if containers else None
            
        except Exception as e:
            logger.error(f"Failed to get deployment container: {str(e)}")
            return None
            
    def get_deployment_status(self, model_name: str) -> Optional[Dict]:
        """Get status of model deployment
        
        Args:
            model_name: Name of the model
            
        Returns:
            Optional[Dict]: Deployment status if found, None otherwise
        """
        try:
            container = self._get_deployment_container(model_name)
            if not container:
                return None
                
            return {
                "model_name": model_name,
                "version": container.image.tags[0].split(":")[1],
                "status": container.status,
                "health": container.attrs["State"]["Health"]["Status"],
                "created_at": container.attrs["Created"],
                "started_at": container.attrs["State"]["StartedAt"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            return None
            
    def list_deployments(self) -> List[Dict]:
        """List all model deployments
        
        Returns:
            List[Dict]: List of deployment information
        """
        try:
            deployments = []
            for deployment_dir in self.deployments_dir.iterdir():
                if not deployment_dir.is_dir():
                    continue
                    
                config_file = deployment_dir / "deployment_config.json"
                if not config_file.exists():
                    continue
                    
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                status = self.get_deployment_status(config["model_name"])
                if status:
                    deployments.append(status)
                    
            return deployments
            
        except Exception as e:
            logger.error(f"Failed to list deployments: {str(e)}")
            return []
            
    def clean_deployment(self, model_name: str, version: Optional[str] = None) -> bool:
        """Clean up deployment artifacts
        
        Args:
            model_name: Name of the model
            version: Optional version to clean
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if version:
                # Clean specific version
                deployment_dir = self.deployments_dir / f"{model_name}-{version}"
                if deployment_dir.exists():
                    shutil.rmtree(deployment_dir)
                    
                # Remove container and image
                container = self._get_deployment_container(model_name)
                if container:
                    container.stop()
                    container.remove()
                    
                image_name = f"{model_name}:{version}"
                try:
                    self.docker_client.images.remove(image_name)
                except:
                    pass
            else:
                # Clean all versions
                for deployment_dir in self.deployments_dir.glob(f"{model_name}-*"):
                    shutil.rmtree(deployment_dir)
                    
                # Remove all containers and images
                containers = self.docker_client.containers.list(
                    filters={"name": model_name}
                )
                for container in containers:
                    container.stop()
                    container.remove()
                    
                images = self.docker_client.images.list(
                    filters={"reference": f"{model_name}:*"}
                )
                for image in images:
                    try:
                        self.docker_client.images.remove(image.id)
                    except:
                        pass
                        
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean deployment: {str(e)}")
            return False 