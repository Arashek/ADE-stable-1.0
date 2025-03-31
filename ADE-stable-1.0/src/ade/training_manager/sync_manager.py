import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import shutil
import requests
from requests.exceptions import RequestException

from .aws_manager import AWSManager
from .model_manager import ModelManager

class SyncManager:
    """Manages synchronization of models with the ADE platform."""
    
    def __init__(self, aws_manager: AWSManager, model_manager: ModelManager):
        self.aws_manager = aws_manager
        self.model_manager = model_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize sync configuration
        self.sync_config = self._load_sync_config()
        
    def sync_model(self, model_name: str, phase: str) -> bool:
        """Synchronize a model with the ADE platform."""
        try:
            # Get model status
            model = {'name': model_name, 'phase': phase}
            status = self.model_manager.get_model_status(model)
            
            if status == 'Not Trained':
                self.logger.error(f"Model {model_name} - {phase} has not been trained")
                return False
                
            # Prepare sync data
            sync_data = self._prepare_sync_data(model_name, phase, status)
            
            # Upload to AWS
            if not self.aws_manager.upload_model(model_name, phase):
                return False
                
            # Sync with ADE platform
            if not self._sync_with_platform(sync_data):
                return False
                
            # Update sync status
            self._update_sync_status(model_name, phase, sync_data)
            
            self.logger.info(f"Model {model_name} - {phase} synchronized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync model: {e}")
            return False
            
    def sync_all_models(self) -> bool:
        """Synchronize all models with the ADE platform."""
        try:
            # Get list of models
            models = self.model_manager.get_model_list()
            
            for model in models:
                if not self.sync_model(model['name'], model['phase']):
                    return False
                    
            self.logger.info("All models synchronized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync all models: {e}")
            return False
            
    def get_sync_status(self, model_name: str, phase: str) -> Dict[str, Any]:
        """Get the synchronization status of a model."""
        try:
            status_file = Path(self.sync_config['status_dir']) / f"{model_name}_{phase}_status.json"
            if not status_file.exists():
                return {'status': 'Not Synced'}
                
            with open(status_file, 'r') as f:
                status = json.load(f)
                
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get sync status: {e}")
            return {'status': 'Unknown'}
            
    def verify_sync(self, model_name: str, phase: str) -> bool:
        """Verify model synchronization with the ADE platform."""
        try:
            # Get sync status
            status = self.get_sync_status(model_name, phase)
            if status['status'] != 'Synced':
                return False
                
            # Verify model files
            model_dir = Path(self.model_manager.config.output_dir) / model_name / phase
            if not model_dir.exists():
                return False
                
            # Verify AWS deployment
            aws_status = self.aws_manager.get_model_status(model_name, phase)
            if not aws_status or aws_status['endpoint_status'] != 'InService':
                return False
                
            # Verify platform integration
            if not self._verify_platform_integration(model_name, phase):
                return False
                
            self.logger.info(f"Model {model_name} - {phase} sync verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify sync: {e}")
            return False
            
    def _load_sync_config(self) -> Dict[str, Any]:
        """Load synchronization configuration."""
        try:
            config_path = Path('config/sync_config.json')
            if not config_path.exists():
                return self._create_default_sync_config()
                
            with open(config_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load sync config: {e}")
            return self._create_default_sync_config()
            
    def _create_default_sync_config(self) -> Dict[str, Any]:
        """Create default synchronization configuration."""
        config = {
            'platform_url': 'https://api.ade-platform.com',
            'api_key': None,
            'status_dir': 'sync_status',
            'retry_attempts': 3,
            'retry_delay': 5,
            'timeout': 30
        }
        
        # Create status directory
        Path(config['status_dir']).mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config_path = Path('config/sync_config.json')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config
        
    def _prepare_sync_data(self, model_name: str, phase: str, status: str) -> Dict[str, Any]:
        """Prepare data for platform synchronization."""
        try:
            # Get model metrics
            metrics = {}
            eval_file = Path(self.model_manager.config.output_dir) / model_name / phase / 'eval_results.json'
            if eval_file.exists():
                with open(eval_file, 'r') as f:
                    metrics = json.load(f)
                    
            # Get deployment config
            deployment_config = {}
            for env in ['development', 'production']:
                config_file = Path(self.model_manager.config.output_dir) / model_name / phase / env / 'deployment_config.json'
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        deployment_config[env] = json.load(f)
                        
            return {
                'model_name': model_name,
                'phase': phase,
                'status': status,
                'metrics': metrics,
                'deployment_config': deployment_config,
                'last_updated': datetime.now().isoformat(),
                'aws_endpoint': self.aws_manager.config.endpoint_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to prepare sync data: {e}")
            return {}
            
    def _sync_with_platform(self, sync_data: Dict[str, Any]) -> bool:
        """Synchronize data with the ADE platform."""
        try:
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.sync_config['api_key']}"
            }
            
            # Send request
            response = requests.post(
                f"{self.sync_config['platform_url']}/api/v1/models/sync",
                json=sync_data,
                headers=headers,
                timeout=self.sync_config['timeout']
            )
            
            # Check response
            if response.status_code != 200:
                self.logger.error(f"Platform sync failed: {response.text}")
                return False
                
            return True
            
        except RequestException as e:
            self.logger.error(f"Failed to sync with platform: {e}")
            return False
            
    def _update_sync_status(self, model_name: str, phase: str, sync_data: Dict[str, Any]) -> None:
        """Update the synchronization status of a model."""
        try:
            status_file = Path(self.sync_config['status_dir']) / f"{model_name}_{phase}_status.json"
            with open(status_file, 'w') as f:
                json.dump(sync_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to update sync status: {e}")
            
    def _verify_platform_integration(self, model_name: str, phase: str) -> bool:
        """Verify model integration with the ADE platform."""
        try:
            # Prepare request
            headers = {
                'Authorization': f"Bearer {self.sync_config['api_key']}"
            }
            
            # Send request
            response = requests.get(
                f"{self.sync_config['platform_url']}/api/v1/models/{model_name}/{phase}/status",
                headers=headers,
                timeout=self.sync_config['timeout']
            )
            
            # Check response
            if response.status_code != 200:
                return False
                
            status = response.json()
            return status.get('status') == 'active'
            
        except RequestException as e:
            self.logger.error(f"Failed to verify platform integration: {e}")
            return False 