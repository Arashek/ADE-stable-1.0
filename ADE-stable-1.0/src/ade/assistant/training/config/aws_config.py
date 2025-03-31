from typing import Dict, Optional, List
from dataclasses import dataclass
import boto3
import botocore
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from pathlib import Path
import json

@dataclass
class AWSServiceConfig:
    """Configuration for AWS services."""
    region: str
    access_key: str
    secret_key: str
    session_token: Optional[str] = None
    profile_name: Optional[str] = None

@dataclass
class AWSServiceStatus:
    """Status of AWS service verification."""
    service_name: str
    is_available: bool
    error_message: Optional[str] = None
    additional_info: Optional[Dict] = None

class AWSServiceVerifier:
    """Verifies AWS service availability and configuration."""
    
    def __init__(self, config: AWSServiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = self._create_session()
        
    def _create_session(self) -> boto3.Session:
        """Create AWS session with credentials."""
        try:
            if self.config.profile_name:
                return boto3.Session(profile_name=self.config.profile_name)
            else:
                return boto3.Session(
                    aws_access_key_id=self.config.access_key,
                    aws_secret_access_key=self.config.secret_key,
                    aws_session_token=self.config.session_token,
                    region_name=self.config.region
                )
        except Exception as e:
            self.logger.error(f"Failed to create AWS session: {e}")
            raise
            
    def verify_services(self) -> List[AWSServiceStatus]:
        """Verify availability of required AWS services."""
        required_services = [
            "s3",
            "ec2",
            "sagemaker",
            "iam",
            "cloudwatch"
        ]
        
        statuses = []
        for service in required_services:
            status = self._verify_service(service)
            statuses.append(status)
            
        return statuses
        
    def _verify_service(self, service_name: str) -> AWSServiceStatus:
        """Verify availability of a specific AWS service."""
        try:
            client = self.session.client(service_name)
            
            # Service-specific verification
            if service_name == "s3":
                client.list_buckets()
            elif service_name == "ec2":
                client.describe_regions()
            elif service_name == "sagemaker":
                client.list_training_jobs()
            elif service_name == "iam":
                client.get_user()
            elif service_name == "cloudwatch":
                client.describe_alarms()
                
            return AWSServiceStatus(
                service_name=service_name,
                is_available=True
            )
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            return AWSServiceStatus(
                service_name=service_name,
                is_available=False,
                error_message=f"Service error: {error_code}",
                additional_info={"error_code": error_code}
            )
        except NoCredentialsError:
            return AWSServiceStatus(
                service_name=service_name,
                is_available=False,
                error_message="No credentials found"
            )
        except Exception as e:
            return AWSServiceStatus(
                service_name=service_name,
                is_available=False,
                error_message=str(e)
            )
            
    def verify_s3_bucket(self, bucket_name: str) -> AWSServiceStatus:
        """Verify access to a specific S3 bucket."""
        try:
            s3_client = self.session.client("s3")
            s3_client.head_bucket(Bucket=bucket_name)
            
            return AWSServiceStatus(
                service_name="s3_bucket",
                is_available=True,
                additional_info={"bucket_name": bucket_name}
            )
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            return AWSServiceStatus(
                service_name="s3_bucket",
                is_available=False,
                error_message=f"Bucket error: {error_code}",
                additional_info={
                    "bucket_name": bucket_name,
                    "error_code": error_code
                }
            )
            
    def verify_sagemaker_role(self, role_name: str) -> AWSServiceStatus:
        """Verify SageMaker execution role."""
        try:
            iam_client = self.session.client("iam")
            role = iam_client.get_role(RoleName=role_name)
            
            # Check for required permissions
            required_permissions = [
                "sagemaker:*",
                "s3:*",
                "ecr:*",
                "cloudwatch:*"
            ]
            
            policy_documents = role.get("Role", {}).get("AssumeRolePolicyDocument", {})
            statements = policy_documents.get("Statement", [])
            
            has_permissions = False
            for statement in statements:
                if statement.get("Effect") == "Allow":
                    actions = statement.get("Action", [])
                    if isinstance(actions, str):
                        actions = [actions]
                    if all(perm in actions for perm in required_permissions):
                        has_permissions = True
                        break
                        
            return AWSServiceStatus(
                service_name="sagemaker_role",
                is_available=has_permissions,
                additional_info={
                    "role_name": role_name,
                    "has_required_permissions": has_permissions
                }
            )
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            return AWSServiceStatus(
                service_name="sagemaker_role",
                is_available=False,
                error_message=f"Role error: {error_code}",
                additional_info={
                    "role_name": role_name,
                    "error_code": error_code
                }
            )

class AWSConfigManager:
    """Manages AWS configuration and credentials."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> Optional[AWSServiceConfig]:
        """Load AWS configuration from file."""
        try:
            if not self.config_path.exists():
                self.logger.error(f"Config file not found: {self.config_path}")
                return None
                
            with open(self.config_path, "r") as f:
                config_data = json.load(f)
                
            return AWSServiceConfig(**config_data)
            
        except Exception as e:
            self.logger.error(f"Failed to load AWS config: {e}")
            return None
            
    def save_config(self, config: AWSServiceConfig) -> bool:
        """Save AWS configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w") as f:
                json.dump(config.__dict__, f, indent=2)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save AWS config: {e}")
            return False
            
    def create_default_config(self) -> AWSServiceConfig:
        """Create a default AWS configuration."""
        return AWSServiceConfig(
            region="us-east-1",
            access_key="",
            secret_key="",
            session_token=None,
            profile_name=None
        ) 