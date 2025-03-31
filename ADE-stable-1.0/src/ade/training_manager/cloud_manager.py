import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, List
import boto3
from google.cloud import storage, compute_v1
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential

class CloudProvider(ABC):
    """Abstract base class for cloud providers."""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the cloud provider."""
        pass
    
    @abstractmethod
    def get_available_regions(self) -> List[str]:
        """Get list of available regions."""
        pass
    
    @abstractmethod
    def get_instance_types(self) -> List[str]:
        """Get list of available instance types."""
        pass
    
    @abstractmethod
    def create_training_job(self, config: Dict) -> str:
        """Create a training job."""
        pass
    
    @abstractmethod
    def stop_training_job(self, job_id: str) -> bool:
        """Stop a training job."""
        pass
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> Dict:
        """Get the status of a training job."""
        pass

class AWSProvider(CloudProvider):
    """AWS cloud provider implementation."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = None
        self.sagemaker = None
    
    def authenticate(self) -> bool:
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.config["access_key"],
                aws_secret_access_key=self.config["secret_key"],
                region_name=self.config["region"]
            )
            self.sagemaker = self.session.client("sagemaker")
            return True
        except Exception as e:
            logging.error(f"AWS authentication failed: {str(e)}")
            return False
    
    def get_available_regions(self) -> List[str]:
        try:
            ec2 = self.session.client("ec2")
            regions = ec2.describe_regions()
            return [region["RegionName"] for region in regions["Regions"]]
        except Exception as e:
            logging.error(f"Failed to get AWS regions: {str(e)}")
            return []
    
    def get_instance_types(self) -> List[str]:
        try:
            ec2 = self.session.client("ec2")
            instances = ec2.describe_instance_types()
            return [instance["InstanceType"] for instance in instances["InstanceTypes"]]
        except Exception as e:
            logging.error(f"Failed to get AWS instance types: {str(e)}")
            return []
    
    def create_training_job(self, config: Dict) -> str:
        try:
            response = self.sagemaker.create_training_job(
                TrainingJobName=config["job_name"],
                AlgorithmSpecification=config["algorithm_spec"],
                RoleArn=config["role_arn"],
                InputDataConfig=config["input_data"],
                OutputDataConfig=config["output_data"],
                ResourceConfig=config["resource_config"],
                StoppingCondition=config["stopping_condition"]
            )
            return response["TrainingJobArn"]
        except Exception as e:
            logging.error(f"Failed to create AWS training job: {str(e)}")
            raise
    
    def stop_training_job(self, job_id: str) -> bool:
        try:
            self.sagemaker.stop_training_job(TrainingJobName=job_id)
            return True
        except Exception as e:
            logging.error(f"Failed to stop AWS training job: {str(e)}")
            return False
    
    def get_job_status(self, job_id: str) -> Dict:
        try:
            response = self.sagemaker.describe_training_job(TrainingJobName=job_id)
            return {
                "status": response["TrainingJobStatus"],
                "metrics": response.get("FinalMetricDataList", []),
                "progress": response.get("Progress", 0)
            }
        except Exception as e:
            logging.error(f"Failed to get AWS job status: {str(e)}")
            return {"status": "ERROR", "error": str(e)}

class GoogleCloudProvider(CloudProvider):
    """Google Cloud provider implementation."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.storage_client = None
        self.compute_client = None
    
    def authenticate(self) -> bool:
        try:
            self.storage_client = storage.Client.from_service_account_json(
                self.config["service_account_path"]
            )
            self.compute_client = compute_v1.InstancesClient.from_service_account_json(
                self.config["service_account_path"]
            )
            return True
        except Exception as e:
            logging.error(f"Google Cloud authentication failed: {str(e)}")
            return False
    
    def get_available_regions(self) -> List[str]:
        try:
            compute = compute_v1.RegionsClient.from_service_account_json(
                self.config["service_account_path"]
            )
            regions = compute.list(project=self.config["project_id"])
            return [region.name for region in regions]
        except Exception as e:
            logging.error(f"Failed to get Google Cloud regions: {str(e)}")
            return []
    
    def get_instance_types(self) -> List[str]:
        try:
            compute = compute_v1.MachineTypesClient.from_service_account_json(
                self.config["service_account_path"]
            )
            machine_types = compute.list(project=self.config["project_id"])
            return [mt.name for mt in machine_types]
        except Exception as e:
            logging.error(f"Failed to get Google Cloud instance types: {str(e)}")
            return []
    
    def create_training_job(self, config: Dict) -> str:
        # Implement Vertex AI training job creation
        pass
    
    def stop_training_job(self, job_id: str) -> bool:
        # Implement Vertex AI training job stopping
        pass
    
    def get_job_status(self, job_id: str) -> Dict:
        # Implement Vertex AI job status retrieval
        pass

class AzureProvider(CloudProvider):
    """Azure cloud provider implementation."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.credential = None
        self.resource_client = None
    
    def authenticate(self) -> bool:
        try:
            self.credential = DefaultAzureCredential()
            self.resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.config["subscription_id"]
            )
            return True
        except Exception as e:
            logging.error(f"Azure authentication failed: {str(e)}")
            return False
    
    def get_available_regions(self) -> List[str]:
        try:
            locations = self.resource_client.providers.get("Microsoft.Compute").resource_types
            return [loc.name for loc in locations]
        except Exception as e:
            logging.error(f"Failed to get Azure regions: {str(e)}")
            return []
    
    def get_instance_types(self) -> List[str]:
        try:
            compute_client = ComputeManagementClient(
                credential=self.credential,
                subscription_id=self.config["subscription_id"]
            )
            sizes = compute_client.virtual_machine_sizes.list(
                location=self.config["region"]
            )
            return [size.name for size in sizes]
        except Exception as e:
            logging.error(f"Failed to get Azure instance types: {str(e)}")
            return []
    
    def create_training_job(self, config: Dict) -> str:
        # Implement Azure ML training job creation
        pass
    
    def stop_training_job(self, job_id: str) -> bool:
        # Implement Azure ML training job stopping
        pass
    
    def get_job_status(self, job_id: str) -> Dict:
        # Implement Azure ML job status retrieval
        pass

class CloudManager:
    """Manager class for handling multiple cloud providers."""
    
    def __init__(self, config_path: str = "config/cloud_config.json"):
        self.config_path = Path(config_path)
        self.providers: Dict[str, CloudProvider] = {}
        self._load_config()
    
    def _load_config(self):
        """Load cloud provider configurations."""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                    for provider, settings in config.items():
                        self._initialize_provider(provider, settings)
        except Exception as e:
            logging.error(f"Failed to load cloud config: {str(e)}")
    
    def _initialize_provider(self, provider: str, settings: Dict):
        """Initialize a cloud provider with its settings."""
        if provider == "aws":
            self.providers["aws"] = AWSProvider(settings)
        elif provider == "google":
            self.providers["google"] = GoogleCloudProvider(settings)
        elif provider == "azure":
            self.providers["azure"] = AzureProvider(settings)
    
    def save_config(self):
        """Save cloud provider configurations."""
        try:
            config = {}
            for provider, instance in self.providers.items():
                config[provider] = instance.config
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save cloud config: {str(e)}")
    
    def get_provider(self, provider: str) -> Optional[CloudProvider]:
        """Get a cloud provider instance."""
        return self.providers.get(provider)
    
    def add_provider(self, provider: str, settings: Dict):
        """Add a new cloud provider."""
        self._initialize_provider(provider, settings)
        self.save_config()
    
    def remove_provider(self, provider: str):
        """Remove a cloud provider."""
        if provider in self.providers:
            del self.providers[provider]
            self.save_config()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available cloud providers."""
        return list(self.providers.keys())
    
    def authenticate_provider(self, provider: str) -> bool:
        """Authenticate with a specific cloud provider."""
        if provider in self.providers:
            return self.providers[provider].authenticate()
        return False 