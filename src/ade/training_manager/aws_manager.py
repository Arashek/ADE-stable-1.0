import boto3
import botocore
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import json
import yaml
from datetime import datetime, timedelta

from .config import AWSConfig

class AWSManager:
    """Manages AWS interactions for model training and deployment."""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self.s3_client = None
        self.sagemaker_client = None
        self.iam_client = None
        
    def verify_credentials(self) -> bool:
        """Verify AWS credentials and permissions."""
        try:
            # Create session
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                aws_session_token=self.config.session_token,
                profile_name=self.config.profile_name,
                region_name=self.config.region
            )
            
            # Initialize clients
            self.s3_client = session.client('s3')
            self.sagemaker_client = session.client('sagemaker')
            self.iam_client = session.client('iam')
            
            # Verify S3 access
            self.s3_client.head_bucket(Bucket=self.config.s3_bucket)
            
            # Verify SageMaker role
            self.iam_client.get_role(RoleName=self.config.sagemaker_role)
            
            self.logger.info("AWS credentials verified successfully")
            return True
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found")
            return False
        except ClientError as e:
            self.logger.error(f"AWS credentials verification failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during AWS verification: {e}")
            return False
            
    def upload_model(self, model_name: str, phase: str) -> bool:
        """Upload model artifacts to S3."""
        try:
            # Prepare model artifacts
            model_dir = Path(f"models/{model_name}/{phase}")
            if not model_dir.exists():
                self.logger.error(f"Model directory not found: {model_dir}")
                return False
                
            # Create tar archive
            archive_path = model_dir / "model.tar.gz"
            self._create_tar_archive(model_dir, archive_path)
            
            # Upload to S3
            s3_key = f"models/{model_name}/{phase}/model.tar.gz"
            self.s3_client.upload_file(
                str(archive_path),
                self.config.s3_bucket,
                s3_key
            )
            
            self.logger.info(f"Model uploaded successfully to s3://{self.config.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload model: {e}")
            return False
            
    def download_model(self, model_name: str, phase: str) -> bool:
        """Download model artifacts from S3."""
        try:
            # Create local directory
            model_dir = Path(f"models/{model_name}/{phase}")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download from S3
            s3_key = f"models/{model_name}/{phase}/model.tar.gz"
            archive_path = model_dir / "model.tar.gz"
            
            self.s3_client.download_file(
                self.config.s3_bucket,
                s3_key,
                str(archive_path)
            )
            
            # Extract archive
            self._extract_tar_archive(archive_path, model_dir)
            
            self.logger.info(f"Model downloaded successfully from s3://{self.config.s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            return False
            
    def deploy_model(self, model_name: str, phase: str) -> bool:
        """Deploy model to SageMaker endpoint."""
        try:
            # Prepare deployment configuration
            deployment_config = self._prepare_deployment_config(model_name, phase)
            
            # Create or update endpoint
            self.sagemaker_client.create_endpoint_config(**deployment_config)
            
            # Update endpoint if it exists, create if it doesn't
            try:
                self.sagemaker_client.update_endpoint(
                    EndpointName=self.config.endpoint_name,
                    EndpointConfigName=f"{model_name}-{phase}-config"
                )
            except ClientError:
                self.sagemaker_client.create_endpoint(
                    EndpointName=self.config.endpoint_name,
                    EndpointConfigName=f"{model_name}-{phase}-config"
                )
                
            self.logger.info(f"Model deployed successfully to endpoint: {self.config.endpoint_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy model: {e}")
            return False
            
    def get_model_status(self, model_name: str, phase: str) -> Dict[str, Any]:
        """Get the status of a deployed model."""
        try:
            # Get endpoint status
            endpoint_status = self.sagemaker_client.describe_endpoint(
                EndpointName=self.config.endpoint_name
            )
            
            # Get model metrics
            metrics = self._get_model_metrics(model_name, phase)
            
            return {
                'endpoint_status': endpoint_status['EndpointStatus'],
                'metrics': metrics,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model status: {e}")
            return {}
            
    def _create_tar_archive(self, source_dir: Path, target_path: Path) -> None:
        """Create a tar archive of model artifacts."""
        import tarfile
        
        with tarfile.open(target_path, "w:gz") as tar:
            tar.add(source_dir, arcname=source_dir.name)
            
    def _extract_tar_archive(self, archive_path: Path, target_dir: Path) -> None:
        """Extract a tar archive of model artifacts."""
        import tarfile
        
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=target_dir)
            
    def _prepare_deployment_config(self, model_name: str, phase: str) -> Dict[str, Any]:
        """Prepare configuration for model deployment."""
        return {
            'EndpointConfigName': f"{model_name}-{phase}-config",
            'ProductionVariants': [{
                'VariantName': 'AllTraffic',
                'ModelName': f"{model_name}-{phase}",
                'InstanceType': 'ml.m5.xlarge',
                'InitialInstanceCount': 1
            }],
            'Tags': [
                {'Key': 'ModelName', 'Value': model_name},
                {'Key': 'Phase', 'Value': phase},
                {'Key': 'DeploymentTime', 'Value': datetime.now().isoformat()}
            ]
        }
        
    def _get_model_metrics(self, model_name: str, phase: str) -> Dict[str, float]:
        """Get model performance metrics from CloudWatch."""
        try:
            cloudwatch = boto3.client('cloudwatch')
            
            # Get metrics for the last hour
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            metrics = cloudwatch.get_metric_statistics(
                Namespace='SageMaker',
                MetricName='Invocation4XXErrors',
                Dimensions=[
                    {'Name': 'EndpointName', 'Value': self.config.endpoint_name},
                    {'Name': 'VariantName', 'Value': 'AllTraffic'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            return {
                'error_rate': metrics['Datapoints'][0]['Sum'] if metrics['Datapoints'] else 0.0,
                'timestamp': end_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model metrics: {e}")
            return {} 