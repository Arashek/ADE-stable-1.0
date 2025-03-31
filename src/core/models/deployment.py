from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
import json
import os
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class DeploymentConfig(BaseModel):
    """Deployment configuration"""
    name: str
    version: str
    environment: str
    resources: Dict[str, Any]
    dependencies: List[str]
    settings: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class DeploymentStatus(BaseModel):
    """Deployment status"""
    status: str
    timestamp: datetime
    message: str
    metrics: Dict[str, Any] = {}
    issues: List[Dict[str, Any]] = []

class DeploymentOptimizer:
    """System for optimizing analysis deployments"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.deployments: Dict[str, DeploymentConfig] = {}
        self.status_history: Dict[str, List[DeploymentStatus]] = {}
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.base_path / 'deployments',
            self.base_path / 'configs',
            self.base_path / 'logs',
            self.base_path / 'cache'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def create_deployment(self, config: DeploymentConfig) -> bool:
        """Create a new deployment"""
        try:
            # Validate deployment
            if not self._validate_deployment(config):
                return False
                
            # Create deployment directory
            deployment_path = self.base_path / 'deployments' / config.name
            deployment_path.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            config_path = deployment_path / 'config.json'
            with open(config_path, 'w') as f:
                json.dump(config.dict(), f, indent=2)
                
            # Install dependencies
            if not self._install_dependencies(config):
                return False
                
            # Initialize deployment
            if not self._initialize_deployment(config):
                return False
                
            # Store deployment
            self.deployments[config.name] = config
            self.status_history[config.name] = []
            
            # Record initial status
            self._record_status(config.name, 'initialized', 'Deployment created successfully')
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating deployment: {str(e)}")
            return False
            
    def update_deployment(self, name: str, config: DeploymentConfig) -> bool:
        """Update an existing deployment"""
        try:
            if name not in self.deployments:
                return False
                
            # Validate deployment
            if not self._validate_deployment(config):
                return False
                
            # Update deployment directory
            deployment_path = self.base_path / 'deployments' / name
            if not deployment_path.exists():
                return False
                
            # Save new configuration
            config_path = deployment_path / 'config.json'
            with open(config_path, 'w') as f:
                json.dump(config.dict(), f, indent=2)
                
            # Update dependencies
            if not self._update_dependencies(name, config):
                return False
                
            # Update deployment
            self.deployments[name] = config
            
            # Record status
            self._record_status(name, 'updated', 'Deployment updated successfully')
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating deployment: {str(e)}")
            return False
            
    def delete_deployment(self, name: str) -> bool:
        """Delete a deployment"""
        try:
            if name not in self.deployments:
                return False
                
            # Clean up deployment directory
            deployment_path = self.base_path / 'deployments' / name
            if deployment_path.exists():
                shutil.rmtree(deployment_path)
                
            # Remove from tracking
            del self.deployments[name]
            del self.status_history[name]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting deployment: {str(e)}")
            return False
            
    def get_deployment_status(self, name: str) -> Optional[DeploymentStatus]:
        """Get latest deployment status"""
        if name not in self.status_history or not self.status_history[name]:
            return None
        return self.status_history[name][-1]
        
    def get_deployment_config(self, name: str) -> Optional[DeploymentConfig]:
        """Get deployment configuration"""
        return self.deployments.get(name)
        
    def optimize_deployment(self, name: str) -> bool:
        """Optimize a deployment"""
        try:
            if name not in self.deployments:
                return False
                
            config = self.deployments[name]
            
            # Optimize resources
            if not self._optimize_resources(config):
                return False
                
            # Optimize dependencies
            if not self._optimize_dependencies(config):
                return False
                
            # Optimize settings
            if not self._optimize_settings(config):
                return False
                
            # Record status
            self._record_status(name, 'optimized', 'Deployment optimized successfully')
            
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing deployment: {str(e)}")
            return False
            
    def _validate_deployment(self, config: DeploymentConfig) -> bool:
        """Validate deployment configuration"""
        try:
            # Check required fields
            if not config.name or not config.version or not config.environment:
                return False
                
            # Check resources
            required_resources = ['cpu', 'memory', 'storage']
            if not all(r in config.resources for r in required_resources):
                return False
                
            # Check dependencies
            if not isinstance(config.dependencies, list):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating deployment: {str(e)}")
            return False
            
    def _install_dependencies(self, config: DeploymentConfig) -> bool:
        """Install deployment dependencies"""
        try:
            # Create virtual environment
            venv_path = self.base_path / 'deployments' / config.name / 'venv'
            subprocess.run(['python', '-m', 'venv', str(venv_path)], check=True)
            
            # Install dependencies
            pip_path = venv_path / 'Scripts' / 'pip.exe' if os.name == 'nt' else venv_path / 'bin' / 'pip'
            for dep in config.dependencies:
                subprocess.run([str(pip_path), 'install', dep], check=True)
                
            return True
            
        except Exception as e:
            logger.error(f"Error installing dependencies: {str(e)}")
            return False
            
    def _initialize_deployment(self, config: DeploymentConfig) -> bool:
        """Initialize deployment"""
        try:
            # Create necessary directories
            deployment_path = self.base_path / 'deployments' / config.name
            directories = ['data', 'logs', 'cache', 'temp']
            
            for directory in directories:
                (deployment_path / directory).mkdir(exist_ok=True)
                
            # Create initial configuration files
            config_files = {
                'settings.json': config.settings,
                'metadata.json': config.metadata
            }
            
            for filename, content in config_files.items():
                with open(deployment_path / filename, 'w') as f:
                    json.dump(content, f, indent=2)
                    
            return True
            
        except Exception as e:
            logger.error(f"Error initializing deployment: {str(e)}")
            return False
            
    def _update_dependencies(self, name: str, config: DeploymentConfig) -> bool:
        """Update deployment dependencies"""
        try:
            # Get current dependencies
            current_config = self.deployments[name]
            
            # Install new dependencies
            new_deps = set(config.dependencies) - set(current_config.dependencies)
            if new_deps:
                venv_path = self.base_path / 'deployments' / name / 'venv'
                pip_path = venv_path / 'Scripts' / 'pip.exe' if os.name == 'nt' else venv_path / 'bin' / 'pip'
                
                for dep in new_deps:
                    subprocess.run([str(pip_path), 'install', dep], check=True)
                    
            return True
            
        except Exception as e:
            logger.error(f"Error updating dependencies: {str(e)}")
            return False
            
    def _optimize_resources(self, config: DeploymentConfig) -> bool:
        """Optimize deployment resources"""
        try:
            # Adjust resource allocation based on usage patterns
            if 'resource_usage' in config.metadata:
                usage = config.metadata['resource_usage']
                
                # Optimize CPU
                if usage.get('cpu_percent', 0) > 80:
                    config.resources['cpu'] = min(
                        config.resources['cpu'] * 1.5,
                        config.resources.get('max_cpu', float('inf'))
                    )
                    
                # Optimize memory
                if usage.get('memory_percent', 0) > 80:
                    config.resources['memory'] = min(
                        config.resources['memory'] * 1.5,
                        config.resources.get('max_memory', float('inf'))
                    )
                    
                # Optimize storage
                if usage.get('storage_percent', 0) > 80:
                    config.resources['storage'] = min(
                        config.resources['storage'] * 1.5,
                        config.resources.get('max_storage', float('inf'))
                    )
                    
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing resources: {str(e)}")
            return False
            
    def _optimize_dependencies(self, config: DeploymentConfig) -> bool:
        """Optimize deployment dependencies"""
        try:
            # Remove unused dependencies
            if 'dependency_usage' in config.metadata:
                usage = config.metadata['dependency_usage']
                config.dependencies = [
                    dep for dep in config.dependencies
                    if dep in usage and usage[dep] > 0
                ]
                
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing dependencies: {str(e)}")
            return False
            
    def _optimize_settings(self, config: DeploymentConfig) -> bool:
        """Optimize deployment settings"""
        try:
            # Optimize cache settings
            if 'cache_metrics' in config.metadata:
                metrics = config.metadata['cache_metrics']
                if metrics.get('hit_rate', 0) < 0.5:
                    config.settings['cache_size'] = min(
                        config.settings.get('cache_size', 1000) * 1.5,
                        config.settings.get('max_cache_size', 10000)
                    )
                    
            # Optimize logging settings
            if 'log_metrics' in config.metadata:
                metrics = config.metadata['log_metrics']
                if metrics.get('error_rate', 0) > 0.1:
                    config.settings['log_level'] = 'DEBUG'
                    
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing settings: {str(e)}")
            return False
            
    def _record_status(
        self,
        name: str,
        status: str,
        message: str,
        metrics: Dict[str, Any] = None,
        issues: List[Dict[str, Any]] = None
    ):
        """Record deployment status"""
        status_obj = DeploymentStatus(
            status=status,
            timestamp=datetime.now(),
            message=message,
            metrics=metrics or {},
            issues=issues or []
        )
        
        if name not in self.status_history:
            self.status_history[name] = []
            
        self.status_history[name].append(status_obj)
        
        # Keep only last 100 status records
        if len(self.status_history[name]) > 100:
            self.status_history[name] = self.status_history[name][-100:] 