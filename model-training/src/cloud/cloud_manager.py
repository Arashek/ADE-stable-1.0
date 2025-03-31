import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Union

import boto3
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class CloudManager:
    """Manages cloud provider integrations for model training."""
    
    def __init__(self, config_path: str = "config/cloud_config.json"):
        self.config = self._load_config(config_path)
        self.aws_client = None
        self.gcp_client = None
        self._initialize_clients()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load cloud configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Cloud config not found at {config_path}. Using defaults.")
            return {
                "default_provider": "aws",
                "aws": {
                    "region": "us-east-1",
                    "bucket": "ade-training-data"
                },
                "gcp": {
                    "project_id": "",
                    "bucket": "ade-training-data"
                }
            }
    
    def _initialize_clients(self):
        """Initialize cloud provider clients."""
        # Initialize AWS client
        if os.path.exists("config/aws_credentials.json"):
            with open("config/aws_credentials.json", 'r') as f:
                aws_creds = json.load(f)
                self.aws_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_creds['aws_access_key_id'],
                    aws_secret_access_key=aws_creds['aws_secret_access_key'],
                    region_name=aws_creds['region']
                )
        
        # Initialize GCP client
        if os.path.exists("config/gcp_credentials.json"):
            with open("config/gcp_credentials.json", 'r') as f:
                gcp_creds = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(
                    gcp_creds
                )
                self.gcp_client = storage.Client(
                    project=gcp_creds['project_id'],
                    credentials=credentials
                )
    
    def upload_dataset(self, dataset_path: Union[str, Path], provider: Optional[str] = None) -> str:
        """Upload dataset to cloud storage."""
        provider = provider or self.config['default_provider']
        dataset_path = Path(dataset_path)
        
        if provider == "aws" and self.aws_client:
            bucket = self.config['aws']['bucket']
            key = f"datasets/{dataset_path.name}"
            self.aws_client.upload_file(str(dataset_path), bucket, key)
            return f"s3://{bucket}/{key}"
        
        elif provider == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(self.config['gcp']['bucket'])
            blob = bucket.blob(f"datasets/{dataset_path.name}")
            blob.upload_from_filename(str(dataset_path))
            return f"gs://{self.config['gcp']['bucket']}/datasets/{dataset_path.name}"
        
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")
    
    def download_dataset(self, cloud_path: str, local_path: Union[str, Path]) -> Path:
        """Download dataset from cloud storage."""
        local_path = Path(local_path)
        
        if cloud_path.startswith("s3://"):
            if not self.aws_client:
                raise ValueError("AWS client not initialized")
            bucket = cloud_path.split("/")[2]
            key = "/".join(cloud_path.split("/")[3:])
            self.aws_client.download_file(bucket, key, str(local_path))
        
        elif cloud_path.startswith("gs://"):
            if not self.gcp_client:
                raise ValueError("GCP client not initialized")
            bucket_name = cloud_path.split("/")[2]
            blob_name = "/".join(cloud_path.split("/")[3:])
            bucket = self.gcp_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(str(local_path))
        
        else:
            raise ValueError(f"Unsupported cloud path format: {cloud_path}")
        
        return local_path
    
    def upload_model(self, model_path: Union[str, Path], provider: Optional[str] = None) -> str:
        """Upload trained model to cloud storage."""
        provider = provider or self.config['default_provider']
        model_path = Path(model_path)
        
        if provider == "aws" and self.aws_client:
            bucket = self.config['aws']['bucket']
            key = f"models/{model_path.name}"
            self.aws_client.upload_file(str(model_path), bucket, key)
            return f"s3://{bucket}/{key}"
        
        elif provider == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(self.config['gcp']['bucket'])
            blob = bucket.blob(f"models/{model_path.name}")
            blob.upload_from_filename(str(model_path))
            return f"gs://{self.config['gcp']['bucket']}/models/{model_path.name}"
        
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")
    
    def download_model(self, cloud_path: str, local_path: Union[str, Path]) -> Path:
        """Download model from cloud storage."""
        return self.download_dataset(cloud_path, local_path)
    
    def list_datasets(self, provider: Optional[str] = None) -> list:
        """List available datasets in cloud storage."""
        provider = provider or self.config['default_provider']
        datasets = []
        
        if provider == "aws" and self.aws_client:
            bucket = self.config['aws']['bucket']
            response = self.aws_client.list_objects_v2(
                Bucket=bucket,
                Prefix="datasets/"
            )
            for obj in response.get('Contents', []):
                datasets.append(f"s3://{bucket}/{obj['Key']}")
        
        elif provider == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(self.config['gcp']['bucket'])
            blobs = bucket.list_blobs(prefix="datasets/")
            for blob in blobs:
                datasets.append(f"gs://{self.config['gcp']['bucket']}/{blob.name}")
        
        return datasets
    
    def list_models(self, provider: Optional[str] = None) -> list:
        """List available models in cloud storage."""
        provider = provider or self.config['default_provider']
        models = []
        
        if provider == "aws" and self.aws_client:
            bucket = self.config['aws']['bucket']
            response = self.aws_client.list_objects_v2(
                Bucket=bucket,
                Prefix="models/"
            )
            for obj in response.get('Contents', []):
                models.append(f"s3://{bucket}/{obj['Key']}")
        
        elif provider == "gcp" and self.gcp_client:
            bucket = self.gcp_client.bucket(self.config['gcp']['bucket'])
            blobs = bucket.list_blobs(prefix="models/")
            for blob in blobs:
                models.append(f"gs://{self.config['gcp']['bucket']}/{blob.name}")
        
        return models

def main():
    """Main function to run the cloud manager service."""
    logging.basicConfig(level=logging.INFO)
    cloud_manager = CloudManager()
    
    # Example usage
    try:
        # List available datasets
        datasets = cloud_manager.list_datasets()
        logger.info(f"Available datasets: {datasets}")
        
        # List available models
        models = cloud_manager.list_models()
        logger.info(f"Available models: {models}")
        
    except Exception as e:
        logger.error(f"Error in cloud manager: {e}")

if __name__ == "__main__":
    main() 