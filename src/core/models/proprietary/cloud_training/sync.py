import os
import logging
import json
import boto3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from .config import CloudTrainingConfig

logger = logging.getLogger(__name__)

class ModelSyncManager:
    """Manages synchronization of model artifacts between cloud and local storage"""
    
    def __init__(self, cloud_config: CloudTrainingConfig):
        self.cloud_config = cloud_config
        self.s3_client = boto3.client('s3')
        self.local_base_path = Path("models/local")
        self.local_base_path.mkdir(parents=True, exist_ok=True)
        
    def sync_checkpoint(
        self,
        job_name: str,
        checkpoint_path: str,
        local_path: Optional[str] = None
    ) -> str:
        """Sync a model checkpoint from S3 to local storage"""
        try:
            # Determine local path
            if local_path is None:
                local_path = self.local_base_path / job_name / "checkpoints"
            else:
                local_path = Path(local_path)
                
            local_path.mkdir(parents=True, exist_ok=True)
            
            # Download checkpoint
            checkpoint_name = Path(checkpoint_path).name
            local_checkpoint_path = local_path / checkpoint_name
            
            logger.info(f"Downloading checkpoint {checkpoint_name} to {local_checkpoint_path}")
            
            self.s3_client.download_file(
                self.cloud_config.bucket,
                checkpoint_path,
                str(local_checkpoint_path)
            )
            
            # Verify download
            if not self._verify_checkpoint(checkpoint_path, local_checkpoint_path):
                raise ValueError("Checkpoint verification failed")
                
            return str(local_checkpoint_path)
            
        except Exception as e:
            logger.error(f"Failed to sync checkpoint: {str(e)}")
            raise
            
    def sync_model(
        self,
        job_name: str,
        model_artifacts: str,
        local_path: Optional[str] = None
    ) -> str:
        """Sync a complete model from S3 to local storage"""
        try:
            # Determine local path
            if local_path is None:
                local_path = self.local_base_path / job_name / "model"
            else:
                local_path = Path(local_path)
                
            local_path.mkdir(parents=True, exist_ok=True)
            
            # Download model artifacts
            logger.info(f"Downloading model artifacts to {local_path}")
            
            self.s3_client.download_file(
                self.cloud_config.bucket,
                model_artifacts,
                str(local_path / "model.tar.gz")
            )
            
            # Extract model
            self._extract_model(local_path)
            
            # Verify model
            if not self._verify_model(local_path):
                raise ValueError("Model verification failed")
                
            return str(local_path)
            
        except Exception as e:
            logger.error(f"Failed to sync model: {str(e)}")
            raise
            
    def get_checkpoint_list(self, job_name: str) -> List[str]:
        """Get list of available checkpoints for a job"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.cloud_config.bucket,
                Prefix=f"output/{job_name}/checkpoints/"
            )
            
            checkpoints = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pt'):
                    checkpoints.append(obj['Key'])
                    
            return sorted(checkpoints)
            
        except Exception as e:
            logger.error(f"Failed to get checkpoint list: {str(e)}")
            raise
            
    def _verify_checkpoint(self, s3_path: str, local_path: Path) -> bool:
        """Verify downloaded checkpoint integrity"""
        try:
            # Get S3 object metadata
            response = self.s3_client.head_object(
                Bucket=self.cloud_config.bucket,
                Key=s3_path
            )
            s3_etag = response['ETag'].strip('"')
            
            # Calculate local file hash
            local_hash = self._calculate_file_hash(local_path)
            
            return s3_etag == local_hash
            
        except Exception as e:
            logger.error(f"Failed to verify checkpoint: {str(e)}")
            return False
            
    def _verify_model(self, model_path: Path) -> bool:
        """Verify downloaded model integrity"""
        try:
            # Check for required files
            required_files = [
                "config.json",
                "pytorch_model.bin",
                "tokenizer.json"
            ]
            
            for file in required_files:
                if not (model_path / file).exists():
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify model: {str(e)}")
            return False
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def _extract_model(self, model_path: Path):
        """Extract model artifacts from tar.gz"""
        import tarfile
        
        tar_path = model_path / "model.tar.gz"
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=model_path)
            
        # Remove tar file after extraction
        tar_path.unlink() 