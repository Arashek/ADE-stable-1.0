import os
import logging
import json
import boto3
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ModelRegistry:
    def __init__(self):
        """Initialize model registry"""
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('S3_BUCKET', 'ade-training-data')
        self.registry_prefix = 'registry/'
        
    def register_model(self, model_name: str, version: str, metadata: dict = None):
        """Register a new model version in the registry"""
        try:
            # Create registry entry
            entry = {
                'model_name': model_name,
                'version': version,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'metadata': metadata or {},
                'artifacts': []
            }
            
            # Save registry entry
            key = f"{self.registry_prefix}{model_name}/versions/{version}/entry.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(entry),
                Metadata={
                    'model_name': model_name,
                    'version': version,
                    'created_at': entry['created_at']
                }
            )
            
            logger.info(f"Registered model: {model_name}/{version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            return False
            
    def list_models(self):
        """List all registered models"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.registry_prefix,
                Delimiter='/'
            )
            
            models = []
            for prefix in response.get('CommonPrefixes', []):
                model_name = prefix['Prefix'].split('/')[-2]
                models.append(model_name)
                
            return sorted(models)
            
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
            
    def list_versions(self, model_name: str):
        """List all versions of a model"""
        try:
            prefix = f"{self.registry_prefix}{model_name}/versions/"
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                Delimiter='/'
            )
            
            versions = []
            for prefix in response.get('CommonPrefixes', []):
                version = prefix['Prefix'].split('/')[-2]
                entry = self.get_version_entry(model_name, version)
                if entry:
                    versions.append(entry)
                    
            return sorted(versions, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list versions: {str(e)}")
            return []
            
    def get_version_entry(self, model_name: str, version: str):
        """Get registry entry for a specific model version"""
        try:
            key = f"{self.registry_prefix}{model_name}/versions/{version}/entry.json"
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response['Body'].read().decode('utf-8'))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            logger.error(f"Failed to get version entry: {str(e)}")
            return None
            
    def update_version_status(self, model_name: str, version: str, status: str):
        """Update status of a model version"""
        try:
            entry = self.get_version_entry(model_name, version)
            if not entry:
                return False
                
            entry['status'] = status
            entry['updated_at'] = datetime.utcnow().isoformat()
            
            key = f"{self.registry_prefix}{model_name}/versions/{version}/entry.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(entry),
                Metadata={
                    'model_name': model_name,
                    'version': version,
                    'status': status,
                    'updated_at': entry['updated_at']
                }
            )
            
            logger.info(f"Updated status for {model_name}/{version} to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update version status: {str(e)}")
            return False
            
    def add_artifact(self, model_name: str, version: str, artifact_key: str, metadata: dict = None):
        """Add an artifact to a model version"""
        try:
            entry = self.get_version_entry(model_name, version)
            if not entry:
                return False
                
            artifact = {
                'key': artifact_key,
                'added_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            entry['artifacts'].append(artifact)
            
            key = f"{self.registry_prefix}{model_name}/versions/{version}/entry.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(entry),
                Metadata={
                    'model_name': model_name,
                    'version': version,
                    'updated_at': entry.get('updated_at', entry['created_at'])
                }
            )
            
            logger.info(f"Added artifact {artifact_key} to {model_name}/{version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add artifact: {str(e)}")
            return False
            
    def get_latest_version(self, model_name: str):
        """Get the latest version of a model"""
        try:
            versions = self.list_versions(model_name)
            if not versions:
                return None
                
            # Find the latest active version
            active_versions = [v for v in versions if v['status'] == 'active']
            if not active_versions:
                return None
                
            return max(active_versions, key=lambda x: x['created_at'])
            
        except Exception as e:
            logger.error(f"Failed to get latest version: {str(e)}")
            return None
            
    def deprecate_version(self, model_name: str, version: str):
        """Deprecate a model version"""
        return self.update_version_status(model_name, version, 'deprecated')
        
    def archive_version(self, model_name: str, version: str):
        """Archive a model version"""
        return self.update_version_status(model_name, version, 'archived')

def main():
    """Main function to manage model registry"""
    try:
        registry = ModelRegistry()
        
        # List all models
        print("\nRegistered Models:")
        print("-" * 50)
        models = registry.list_models()
        for model in models:
            print(f"Model: {model}")
            versions = registry.list_versions(model)
            print("Versions:")
            for version in versions:
                print(f"  - {version['version']} ({version['status']})")
            print("-" * 30)
            
        # Get user input for action
        print("\nAvailable actions:")
        print("1. Register new model version")
        print("2. List model versions")
        print("3. Get version details")
        print("4. Update version status")
        print("5. Add artifact to version")
        print("6. Get latest version")
        print("7. Deprecate version")
        print("8. Archive version")
        print("9. Exit")
        
        while True:
            action = input("\nEnter action number (1-9): ")
            
            if action == '9':
                break
                
            model_name = input("Enter model name: ")
            
            if action == '1':
                version = input("Enter version: ")
                metadata = {}
                while True:
                    key = input("Enter metadata key (or 'done' to finish): ")
                    if key.lower() == 'done':
                        break
                    value = input("Enter metadata value: ")
                    metadata[key] = value
                if registry.register_model(model_name, version, metadata):
                    print(f"Successfully registered model version: {model_name}/{version}")
                    
            elif action == '2':
                versions = registry.list_versions(model_name)
                if versions:
                    print(f"\nVersions for model {model_name}:")
                    for version in versions:
                        print(f"Version: {version['version']}")
                        print(f"Status: {version['status']}")
                        print(f"Created: {version['created_at']}")
                        print("-" * 30)
                else:
                    print(f"No versions found for model {model_name}")
                    
            elif action == '3':
                version = input("Enter version: ")
                entry = registry.get_version_entry(model_name, version)
                if entry:
                    print("\nVersion Details:")
                    print(f"Model: {entry['model_name']}")
                    print(f"Version: {entry['version']}")
                    print(f"Status: {entry['status']}")
                    print(f"Created: {entry['created_at']}")
                    if 'updated_at' in entry:
                        print(f"Updated: {entry['updated_at']}")
                    print("\nMetadata:")
                    for k, v in entry['metadata'].items():
                        print(f"{k}: {v}")
                    print("\nArtifacts:")
                    for artifact in entry['artifacts']:
                        print(f"- {artifact['key']}")
                else:
                    print(f"Version {version} not found for model {model_name}")
                    
            elif action == '4':
                version = input("Enter version: ")
                status = input("Enter new status (active/deprecated/archived): ")
                if registry.update_version_status(model_name, version, status):
                    print(f"Successfully updated status for {model_name}/{version}")
                    
            elif action == '5':
                version = input("Enter version: ")
                artifact_key = input("Enter artifact key: ")
                metadata = {}
                while True:
                    key = input("Enter artifact metadata key (or 'done' to finish): ")
                    if key.lower() == 'done':
                        break
                    value = input("Enter artifact metadata value: ")
                    metadata[key] = value
                if registry.add_artifact(model_name, version, artifact_key, metadata):
                    print(f"Successfully added artifact to {model_name}/{version}")
                    
            elif action == '6':
                latest = registry.get_latest_version(model_name)
                if latest:
                    print(f"\nLatest version for model {model_name}:")
                    print(f"Version: {latest['version']}")
                    print(f"Status: {latest['status']}")
                    print(f"Created: {latest['created_at']}")
                else:
                    print(f"No active versions found for model {model_name}")
                    
            elif action == '7':
                version = input("Enter version: ")
                if registry.deprecate_version(model_name, version):
                    print(f"Successfully deprecated version {version} for model {model_name}")
                    
            elif action == '8':
                version = input("Enter version: ")
                if registry.archive_version(model_name, version):
                    print(f"Successfully archived version {version} for model {model_name}")
                    
    except Exception as e:
        logger.error(f"Failed to manage registry: {str(e)}")
        print("\nFailed to manage registry. Please check the logs above.")

if __name__ == "__main__":
    main() 