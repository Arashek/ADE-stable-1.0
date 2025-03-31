from typing import Dict, Any, Optional, List
import os
import logging
import json
import boto3
import sagemaker
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError
from .config import CloudTrainingConfig, ModelRegistryConfig
from .sync import ModelSyncManager
from .monitoring import TrainingMonitor

logger = logging.getLogger(__name__)

class CloudTrainingManager:
    """Manages cloud-based model training operations"""
    
    def __init__(
        self,
        cloud_config: CloudTrainingConfig,
        registry_config: ModelRegistryConfig
    ):
        self.cloud_config = cloud_config
        self.registry_config = registry_config
        self.sync_manager = ModelSyncManager(cloud_config)
        self.monitor = TrainingMonitor(cloud_config)
        
        # Initialize AWS clients
        self.sagemaker_client = boto3.client('sagemaker')
        self.s3_client = boto3.client('s3')
        
        # Set up credentials
        self._setup_credentials()
        
    def _setup_credentials(self):
        """Set up AWS credentials and configuration"""
        try:
            # Load credentials from environment or AWS credentials file
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', self.cloud_config.region)
            
            if not all([aws_access_key, aws_secret_key, aws_region]):
                raise ValueError("Missing AWS credentials or region")
                
            # Configure AWS session
            session = boto3.Session(
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
            
            # Initialize SageMaker session
            self.sagemaker_session = sagemaker.Session(session)
            
        except Exception as e:
            logger.error(f"Failed to set up AWS credentials: {str(e)}")
            raise
            
    def prepare_training_job(
        self,
        training_code_path: str,
        training_data_path: str,
        model_config: Dict[str, Any],
        training_config: Dict[str, Any]
    ) -> str:
        """Prepare and upload training code and data"""
        try:
            # Create unique job name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            job_name = f"ade-training-{timestamp}"
            
            # Upload training code
            code_s3_path = self._upload_training_code(training_code_path)
            
            # Upload training data
            data_s3_path = self._upload_training_data(training_data_path)
            
            # Create training job configuration
            training_job_config = {
                "TrainingJobName": job_name,
                "AlgorithmSpecification": {
                    "TrainingImage": self.cloud_config.training_image,
                    "TrainingInputMode": "File",
                    "MetricDefinitions": [
                        {"Name": "loss", "Regex": "loss: ([0-9\\.]+)"},
                        {"Name": "eval_loss", "Regex": "eval_loss: ([0-9\\.]+)"}
                    ]
                },
                "RoleArn": self.cloud_config.role_arn,
                "InputDataConfig": [
                    {
                        "ChannelName": "training",
                        "DataSource": {
                            "S3DataSource": {
                                "S3DataType": "S3Prefix",
                                "S3Uri": data_s3_path,
                                "S3DataDistributionType": "ShardedByS3Key"
                            }
                        }
                    }
                ],
                "OutputDataConfig": {
                    "S3OutputPath": f"s3://{self.cloud_config.bucket}/output/{job_name}"
                },
                "ResourceConfig": {
                    "InstanceCount": self.cloud_config.instance_count,
                    "InstanceType": self.cloud_config.instance_type,
                    "VolumeSizeInGB": self.cloud_config.volume_size
                },
                "StoppingCondition": {
                    "MaxRuntimeInSeconds": self.cloud_config.max_runtime
                },
                "HyperParameters": {
                    "model_config": json.dumps(model_config),
                    "training_config": json.dumps(training_config)
                }
            }
            
            return training_job_config
            
        except Exception as e:
            logger.error(f"Failed to prepare training job: {str(e)}")
            raise
            
    def start_training_job(self, training_job_config: Dict[str, Any]) -> str:
        """Start a training job on SageMaker"""
        try:
            # Create training job
            response = self.sagemaker_client.create_training_job(**training_job_config)
            job_name = response['TrainingJobArn'].split('/')[-1]
            
            logger.info(f"Started training job: {job_name}")
            
            # Start monitoring
            self.monitor.start_monitoring(job_name)
            
            return job_name
            
        except Exception as e:
            logger.error(f"Failed to start training job: {str(e)}")
            raise
            
    def _upload_training_code(self, code_path: str) -> str:
        """Upload training code to S3"""
        try:
            code_path = Path(code_path)
            s3_key = f"training/code/{code_path.name}"
            
            self.s3_client.upload_file(
                str(code_path),
                self.cloud_config.bucket,
                s3_key
            )
            
            return f"s3://{self.cloud_config.bucket}/{s3_key}"
            
        except Exception as e:
            logger.error(f"Failed to upload training code: {str(e)}")
            raise
            
    def _upload_training_data(self, data_path: str) -> str:
        """Upload training data to S3"""
        try:
            data_path = Path(data_path)
            s3_key = f"training/data/{data_path.name}"
            
            self.s3_client.upload_file(
                str(data_path),
                self.cloud_config.bucket,
                s3_key
            )
            
            return f"s3://{self.cloud_config.bucket}/{s3_key}"
            
        except Exception as e:
            logger.error(f"Failed to upload training data: {str(e)}")
            raise
            
    def get_training_status(self, job_name: str) -> Dict[str, Any]:
        """Get current status of a training job"""
        try:
            response = self.sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            
            return {
                "status": response['TrainingJobStatus'],
                "metrics": self.monitor.get_latest_metrics(job_name),
                "cost": self.monitor.get_estimated_cost(job_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to get training status: {str(e)}")
            raise
            
    def stop_training_job(self, job_name: str):
        """Stop a running training job"""
        try:
            self.sagemaker_client.stop_training_job(
                TrainingJobName=job_name
            )
            logger.info(f"Stopped training job: {job_name}")
            
        except Exception as e:
            logger.error(f"Failed to stop training job: {str(e)}")
            raise
            
    def register_model(self, job_name: str, model_metadata: Dict[str, Any]):
        """Register a trained model in the registry"""
        try:
            # Get model artifacts location
            response = self.sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            model_artifacts = response['ModelArtifacts']['S3ModelArtifacts']
            
            # Create model version
            version = {
                "job_name": job_name,
                "model_artifacts": model_artifacts,
                "metadata": model_metadata,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Save to registry
            registry_path = Path(self.registry_config.registry_path)
            registry_path.mkdir(parents=True, exist_ok=True)
            
            version_file = registry_path / f"{job_name}.json"
            with open(version_file, 'w') as f:
                json.dump(version, f, indent=2)
                
            logger.info(f"Registered model version: {job_name}")
            
        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            raise 