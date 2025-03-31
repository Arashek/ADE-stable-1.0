import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import yaml
import json
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of pipeline validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict = field(default_factory=dict)

class PipelineValidator:
    """Validates pipeline configurations and verifies requirements"""
    
    def __init__(self):
        """Initialize the pipeline validator"""
        self.required_fields = {
            "name": str,
            "description": str,
            "version": str,
            "type": str,
            "build_stages": list,
            "services": list
        }
        
        self.stage_required_fields = {
            "name": str,
            "commands": list,
            "dependencies": list,
            "environment": dict,
            "timeout": int,
            "retries": int
        }
        
        self.service_required_fields = {
            "name": str,
            "image": str,
            "ports": list,
            "environment": dict,
            "volumes": list,
            "resources": dict,
            "health_check": dict,
            "depends_on": list
        }
        
    def validate_config(self, config: Dict) -> ValidationResult:
        """Validate a pipeline configuration
        
        Args:
            config: Pipeline configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate required fields
            for field_name, field_type in self.required_fields.items():
                if field_name not in config:
                    result.is_valid = False
                    result.errors.append(f"Missing required field: {field_name}")
                elif not isinstance(config[field_name], field_type):
                    result.is_valid = False
                    result.errors.append(f"Invalid type for {field_name}: expected {field_type.__name__}")
                    
            # Validate build stages
            if "build_stages" in config:
                for stage in config["build_stages"]:
                    stage_result = self._validate_stage(stage)
                    if not stage_result.is_valid:
                        result.is_valid = False
                        result.errors.extend(stage_result.errors)
                    result.warnings.extend(stage_result.warnings)
                    
            # Validate services
            if "services" in config:
                for service in config["services"]:
                    service_result = self._validate_service(service)
                    if not service_result.is_valid:
                        result.is_valid = False
                        result.errors.extend(service_result.errors)
                    result.warnings.extend(service_result.warnings)
                    
            # Validate dependencies
            if result.is_valid:
                dep_result = self._validate_dependencies(config)
                if not dep_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(dep_result.errors)
                    
            # Validate resources
            if result.is_valid:
                resource_result = self._validate_resources(config)
                if not resource_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(resource_result.errors)
                    
            # Add validation details
            result.details = {
                "config_version": config.get("version"),
                "num_stages": len(config.get("build_stages", [])),
                "num_services": len(config.get("services", [])),
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation error: {str(e)}")
            
        return result
        
    def _validate_stage(self, stage: Dict) -> ValidationResult:
        """Validate a build stage configuration
        
        Args:
            stage: Stage configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate required fields
            for field_name, field_type in self.stage_required_fields.items():
                if field_name not in stage:
                    result.is_valid = False
                    result.errors.append(f"Stage missing required field: {field_name}")
                elif not isinstance(stage[field_name], field_type):
                    result.is_valid = False
                    result.errors.append(f"Invalid type for stage field {field_name}: expected {field_type.__name__}")
                    
            # Validate commands
            if "commands" in stage and not stage["commands"]:
                result.warnings.append(f"Stage {stage.get('name', 'unnamed')} has no commands")
                
            # Validate timeout
            if "timeout" in stage and stage["timeout"] <= 0:
                result.is_valid = False
                result.errors.append(f"Invalid timeout value for stage {stage.get('name', 'unnamed')}")
                
            # Validate retries
            if "retries" in stage and stage["retries"] < 0:
                result.is_valid = False
                result.errors.append(f"Invalid retries value for stage {stage.get('name', 'unnamed')}")
                
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Stage validation error: {str(e)}")
            
        return result
        
    def _validate_service(self, service: Dict) -> ValidationResult:
        """Validate a service configuration
        
        Args:
            service: Service configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate required fields
            for field_name, field_type in self.service_required_fields.items():
                if field_name not in service:
                    result.is_valid = False
                    result.errors.append(f"Service missing required field: {field_name}")
                elif not isinstance(service[field_name], field_type):
                    result.is_valid = False
                    result.errors.append(f"Invalid type for service field {field_name}: expected {field_type.__name__}")
                    
            # Validate ports
            if "ports" in service:
                for port in service["ports"]:
                    if not isinstance(port, dict) or "host" not in port or "container" not in port:
                        result.is_valid = False
                        result.errors.append(f"Invalid port configuration for service {service.get('name', 'unnamed')}")
                        
            # Validate volumes
            if "volumes" in service:
                for volume in service["volumes"]:
                    if not isinstance(volume, dict) or "host" not in volume or "container" not in volume:
                        result.is_valid = False
                        result.errors.append(f"Invalid volume configuration for service {service.get('name', 'unnamed')}")
                        
            # Validate resources
            if "resources" in service:
                resource_result = self._validate_service_resources(service["resources"])
                if not resource_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(resource_result.errors)
                    
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Service validation error: {str(e)}")
            
        return result
        
    def _validate_dependencies(self, config: Dict) -> ValidationResult:
        """Validate pipeline dependencies
        
        Args:
            config: Pipeline configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Get all stage names
            stage_names = {stage["name"] for stage in config.get("build_stages", [])}
            
            # Validate stage dependencies
            for stage in config.get("build_stages", []):
                for dep in stage.get("dependencies", []):
                    if dep not in stage_names:
                        result.is_valid = False
                        result.errors.append(f"Invalid dependency '{dep}' in stage '{stage['name']}'")
                        
            # Get all service names
            service_names = {service["name"] for service in config.get("services", [])}
            
            # Validate service dependencies
            for service in config.get("services", []):
                for dep in service.get("depends_on", []):
                    if dep not in service_names:
                        result.is_valid = False
                        result.errors.append(f"Invalid dependency '{dep}' in service '{service['name']}'")
                        
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Dependency validation error: {str(e)}")
            
        return result
        
    def _validate_resources(self, config: Dict) -> ValidationResult:
        """Validate resource configurations
        
        Args:
            config: Pipeline configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate service resources
            for service in config.get("services", []):
                if "resources" in service:
                    resource_result = self._validate_service_resources(service["resources"])
                    if not resource_result.is_valid:
                        result.is_valid = False
                        result.errors.extend(resource_result.errors)
                        
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Resource validation error: {str(e)}")
            
        return result
        
    def _validate_service_resources(self, resources: Dict) -> ValidationResult:
        """Validate service resource configurations
        
        Args:
            resources: Service resource configuration dictionary
            
        Returns:
            ValidationResult: Result of validation
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Validate CPU limits
            if "cpu" in resources:
                if not isinstance(resources["cpu"], (int, float)) or resources["cpu"] <= 0:
                    result.is_valid = False
                    result.errors.append("Invalid CPU limit")
                    
            # Validate memory limits
            if "memory" in resources:
                if not isinstance(resources["memory"], str):
                    result.is_valid = False
                    result.errors.append("Invalid memory limit format")
                else:
                    # Validate memory string format (e.g., "1Gi", "512Mi")
                    import re
                    if not re.match(r'^\d+[KMGTPEZY]i?$', resources["memory"]):
                        result.is_valid = False
                        result.errors.append("Invalid memory limit format")
                        
            # Validate GPU limits
            if "gpu" in resources:
                if not isinstance(resources["gpu"], int) or resources["gpu"] < 0:
                    result.is_valid = False
                    result.errors.append("Invalid GPU limit")
                    
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Service resource validation error: {str(e)}")
            
        return result
        
    def verify_requirements(self, config: Dict) -> ValidationResult:
        """Verify pipeline requirements
        
        Args:
            config: Pipeline configuration dictionary
            
        Returns:
            ValidationResult: Result of verification
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Verify Docker availability
            if not self._verify_docker():
                result.is_valid = False
                result.errors.append("Docker is not available")
                
            # Verify required images
            for service in config.get("services", []):
                if "image" in service:
                    if not self._verify_docker_image(service["image"]):
                        result.warnings.append(f"Docker image not found: {service['image']}")
                        
            # Verify volume paths
            for service in config.get("services", []):
                if "volumes" in service:
                    for volume in service["volumes"]:
                        if "host" in volume:
                            if not Path(volume["host"]).exists():
                                result.warnings.append(f"Volume path does not exist: {volume['host']}")
                                
            # Verify port availability
            for service in config.get("services", []):
                if "ports" in service:
                    for port in service["ports"]:
                        if "host" in port and not self._verify_port_available(port["host"]):
                            result.warnings.append(f"Port may be in use: {port['host']}")
                            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Requirement verification error: {str(e)}")
            
        return result
        
    def _verify_docker(self) -> bool:
        """Verify Docker availability
        
        Returns:
            bool: True if Docker is available, False otherwise
        """
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False
            
    def _verify_docker_image(self, image: str) -> bool:
        """Verify Docker image availability
        
        Args:
            image: Docker image name
            
        Returns:
            bool: True if image exists, False otherwise
        """
        try:
            import docker
            client = docker.from_env()
            client.images.get(image)
            return True
        except Exception:
            return False
            
    def _verify_port_available(self, port: int) -> bool:
        """Verify port availability
        
        Args:
            port: Port number
            
        Returns:
            bool: True if port is available, False otherwise
        """
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return True
        except Exception:
            return False 