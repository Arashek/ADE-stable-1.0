import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

@dataclass
class BuildStage:
    """Configuration for a build stage"""
    name: str
    commands: List[str]
    dependencies: List[str]
    environment: Dict[str, str]
    timeout: int
    retries: int
    dockerfile: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    image: str
    ports: List[Dict[str, int]]
    environment: Dict[str, str]
    volumes: List[Dict[str, str]]
    resources: Dict[str, Union[int, str]]
    health_check: Dict[str, Union[str, int, List[str]]]
    depends_on: List[str]
    metadata: Dict = field(default_factory=dict)

@dataclass
class PipelineConfig:
    """Main pipeline configuration"""
    name: str
    description: str
    version: str
    type: str
    build_stages: List[BuildStage]
    services: List[ServiceConfig]
    environment: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, Union[int, str]] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

class PipelineConfigManager:
    """Manages pipeline configurations"""
    
    def __init__(self, config_dir: str = "configs"):
        """Initialize the pipeline config manager
        
        Args:
            config_dir: Directory for storing configurations
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_config(self, config: PipelineConfig) -> bool:
        """Create a new pipeline configuration
        
        Args:
            config: Pipeline configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create config directory
            config_path = self.config_dir / config.name
            config_path.mkdir(parents=True, exist_ok=True)
            
            # Save main config
            config_file = config_path / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(self._config_to_dict(config), f, default_flow_style=False)
                
            # Save metadata
            metadata_file = config_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    "name": config.name,
                    "version": config.version,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "metadata": config.metadata
                }, f, indent=4)
                
            logger.info(f"Created pipeline configuration: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pipeline configuration: {str(e)}")
            return False
            
    def load_config(self, name: str) -> Optional[PipelineConfig]:
        """Load a pipeline configuration
        
        Args:
            name: Name of the pipeline
            
        Returns:
            Optional[PipelineConfig]: Pipeline configuration if found, None otherwise
        """
        try:
            config_path = self.config_dir / name
            if not config_path.exists():
                return None
                
            # Load main config
            config_file = config_path / "config.yaml"
            with open(config_file, 'r') as f:
                config_dict = yaml.safe_load(f)
                
            # Load metadata
            metadata_file = config_path / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            # Create config object
            config = self._dict_to_config(config_dict)
            config.metadata.update(metadata.get("metadata", {}))
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load pipeline configuration: {str(e)}")
            return None
            
    def update_config(self, config: PipelineConfig) -> bool:
        """Update an existing pipeline configuration
        
        Args:
            config: Updated pipeline configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path = self.config_dir / config.name
            if not config_path.exists():
                return False
                
            # Update main config
            config_file = config_path / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(self._config_to_dict(config), f, default_flow_style=False)
                
            # Update metadata
            metadata_file = config_path / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                
            metadata["updated_at"] = datetime.now().isoformat()
            metadata["version"] = config.version
            metadata["metadata"] = config.metadata
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            logger.info(f"Updated pipeline configuration: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update pipeline configuration: {str(e)}")
            return False
            
    def delete_config(self, name: str) -> bool:
        """Delete a pipeline configuration
        
        Args:
            name: Name of the pipeline
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path = self.config_dir / name
            if not config_path.exists():
                return False
                
            shutil.rmtree(config_path)
            logger.info(f"Deleted pipeline configuration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete pipeline configuration: {str(e)}")
            return False
            
    def list_configs(self) -> List[str]:
        """List all pipeline configurations
        
        Returns:
            List[str]: List of pipeline names
        """
        try:
            return [d.name for d in self.config_dir.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Failed to list pipeline configurations: {str(e)}")
            return []
            
    def get_config_metadata(self, name: str) -> Optional[Dict]:
        """Get metadata for a pipeline configuration
        
        Args:
            name: Name of the pipeline
            
        Returns:
            Optional[Dict]: Configuration metadata if found, None otherwise
        """
        try:
            metadata_file = self.config_dir / name / "metadata.json"
            if not metadata_file.exists():
                return None
                
            with open(metadata_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to get configuration metadata: {str(e)}")
            return None
            
    def _config_to_dict(self, config: PipelineConfig) -> Dict:
        """Convert PipelineConfig to dictionary
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Dict: Configuration dictionary
        """
        return {
            "name": config.name,
            "description": config.description,
            "version": config.version,
            "type": config.type,
            "build_stages": [
                {
                    "name": stage.name,
                    "commands": stage.commands,
                    "dependencies": stage.dependencies,
                    "environment": stage.environment,
                    "timeout": stage.timeout,
                    "retries": stage.retries,
                    "dockerfile": stage.dockerfile,
                    "metadata": stage.metadata
                }
                for stage in config.build_stages
            ],
            "services": [
                {
                    "name": service.name,
                    "image": service.image,
                    "ports": service.ports,
                    "environment": service.environment,
                    "volumes": service.volumes,
                    "resources": service.resources,
                    "health_check": service.health_check,
                    "depends_on": service.depends_on,
                    "metadata": service.metadata
                }
                for service in config.services
            ],
            "environment": config.environment,
            "resources": config.resources,
            "metadata": config.metadata
        }
        
    def _dict_to_config(self, config_dict: Dict) -> PipelineConfig:
        """Convert dictionary to PipelineConfig
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            PipelineConfig: Pipeline configuration
        """
        return PipelineConfig(
            name=config_dict["name"],
            description=config_dict["description"],
            version=config_dict["version"],
            type=config_dict["type"],
            build_stages=[
                BuildStage(
                    name=stage["name"],
                    commands=stage["commands"],
                    dependencies=stage["dependencies"],
                    environment=stage["environment"],
                    timeout=stage["timeout"],
                    retries=stage["retries"],
                    dockerfile=stage.get("dockerfile"),
                    metadata=stage.get("metadata", {})
                )
                for stage in config_dict["build_stages"]
            ],
            services=[
                ServiceConfig(
                    name=service["name"],
                    image=service["image"],
                    ports=service["ports"],
                    environment=service["environment"],
                    volumes=service["volumes"],
                    resources=service["resources"],
                    health_check=service["health_check"],
                    depends_on=service["depends_on"],
                    metadata=service.get("metadata", {})
                )
                for service in config_dict["services"]
            ],
            environment=config_dict.get("environment", {}),
            resources=config_dict.get("resources", {}),
            metadata=config_dict.get("metadata", {})
        ) 