from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class CloudTrainingConfig:
    """Configuration for cloud-based training"""
    
    # AWS configuration
    region: str = "us-east-1"
    bucket: str = "ade-training"
    role_arn: str = "arn:aws:iam::YOUR_ACCOUNT_ID:role/SageMakerTrainingRole"
    
    # Training infrastructure
    instance_type: str = "ml.g4dn.xlarge"  # GPU instance
    instance_count: int = 1
    volume_size: int = 100  # GB
    max_runtime: int = 86400  # 24 hours in seconds
    
    # Training image
    training_image: str = "YOUR_ECR_REPO:latest"
    
    # Monitoring settings
    metrics_interval: int = 60  # seconds
    cost_alert_threshold: float = 100.0  # USD
    
    # Sync settings
    sync_interval: int = 300  # 5 minutes
    checkpoint_interval: int = 3600  # 1 hour
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "region": self.region,
            "bucket": self.bucket,
            "role_arn": self.role_arn,
            "instance_type": self.instance_type,
            "instance_count": self.instance_count,
            "volume_size": self.volume_size,
            "max_runtime": self.max_runtime,
            "training_image": self.training_image,
            "metrics_interval": self.metrics_interval,
            "cost_alert_threshold": self.cost_alert_threshold,
            "sync_interval": self.sync_interval,
            "checkpoint_interval": self.checkpoint_interval
        }

@dataclass
class ModelRegistryConfig:
    """Configuration for model registry"""
    
    # Registry location
    registry_path: str = "models/registry"
    
    # Versioning settings
    max_versions: int = 10
    version_format: str = "{model_name}-v{version}"
    
    # Metadata settings
    required_metadata: list = None
    
    def __post_init__(self):
        if self.required_metadata is None:
            self.required_metadata = [
                "model_name",
                "version",
                "base_model",
                "training_config",
                "performance_metrics",
                "created_at"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "registry_path": self.registry_path,
            "max_versions": self.max_versions,
            "version_format": self.version_format,
            "required_metadata": self.required_metadata
        } 