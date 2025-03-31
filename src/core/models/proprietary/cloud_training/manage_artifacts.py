import os
import logging
import boto3
import json
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ArtifactManager:
    def __init__(self):
        """Initialize artifact manager"""
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('S3_BUCKET', 'ade-training-data')
        
    def list_artifacts(self, prefix: str = 'models/'):
        """List all model artifacts in S3"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Failed to list artifacts: {str(e)}")
            return []
            
    def download_artifact(self, key: str, local_path: str):
        """Download a model artifact from S3"""
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.s3.download_file(self.bucket, key, local_path)
            logger.info(f"Downloaded artifact: {key} to {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download artifact: {str(e)}")
            return False
            
    def upload_artifact(self, local_path: str, key: str):
        """Upload a model artifact to S3"""
        try:
            self.s3.upload_file(local_path, self.bucket, key)
            logger.info(f"Uploaded artifact: {local_path} to {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload artifact: {str(e)}")
            return False
            
    def delete_artifact(self, key: str):
        """Delete a model artifact from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted artifact: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete artifact: {str(e)}")
            return False
            
    def get_artifact_metadata(self, key: str):
        """Get metadata for a model artifact"""
        try:
            response = self.s3.head_object(Bucket=self.bucket, Key=key)
            return response.get('Metadata', {})
        except ClientError as e:
            logger.error(f"Failed to get artifact metadata: {str(e)}")
            return None
            
    def update_artifact_metadata(self, key: str, metadata: dict):
        """Update metadata for a model artifact"""
        try:
            self.s3.copy_object(
                Bucket=self.bucket,
                CopySource={'Bucket': self.bucket, 'Key': key},
                Key=key,
                Metadata=metadata,
                MetadataDirective='REPLACE'
            )
            logger.info(f"Updated metadata for artifact: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to update artifact metadata: {str(e)}")
            return False
            
    def sync_artifacts(self, local_dir: str, prefix: str = 'models/'):
        """Sync model artifacts between local directory and S3"""
        try:
            # Upload new or modified files
            local_path = Path(local_dir)
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{prefix}{relative_path}"
                    
                    # Check if file exists in S3
                    try:
                        self.s3.head_object(Bucket=self.bucket, Key=s3_key)
                    except ClientError:
                        # File doesn't exist in S3, upload it
                        self.upload_artifact(str(file_path), s3_key)
                        
            # Download new or modified files from S3
            s3_objects = self.list_artifacts(prefix)
            for obj in s3_objects:
                s3_key = obj['Key']
                local_file = local_path / Path(s3_key).relative_to(prefix)
                
                if not local_file.exists() or local_file.stat().st_size != obj['Size']:
                    self.download_artifact(s3_key, str(local_file))
                    
            logger.info("Artifact sync completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync artifacts: {str(e)}")
            return False
            
    def create_version(self, model_name: str, version: str, metadata: dict = None):
        """Create a new version of a model"""
        try:
            version_key = f"models/{model_name}/versions/{version}"
            
            # Create version metadata
            version_metadata = {
                'model_name': model_name,
                'version': version,
                'created_at': datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Create version manifest
            manifest = {
                'model_name': model_name,
                'version': version,
                'created_at': version_metadata['created_at'],
                'artifacts': []
            }
            
            # Upload manifest
            manifest_key = f"{version_key}/manifest.json"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=manifest_key,
                Body=json.dumps(manifest),
                Metadata=version_metadata
            )
            
            logger.info(f"Created model version: {model_name}/{version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create model version: {str(e)}")
            return False
            
    def list_versions(self, model_name: str):
        """List all versions of a model"""
        try:
            prefix = f"models/{model_name}/versions/"
            objects = self.list_artifacts(prefix)
            
            versions = []
            for obj in objects:
                if obj['Key'].endswith('manifest.json'):
                    metadata = self.get_artifact_metadata(obj['Key'])
                    if metadata:
                        versions.append({
                            'version': metadata['version'],
                            'created_at': metadata['created_at']
                        })
                        
            return sorted(versions, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list model versions: {str(e)}")
            return []

def main():
    """Main function to manage model artifacts"""
    try:
        manager = ArtifactManager()
        
        # List all artifacts
        print("\nModel Artifacts:")
        print("-" * 50)
        artifacts = manager.list_artifacts()
        for artifact in artifacts:
            print(f"Key: {artifact['Key']}")
            print(f"Size: {artifact['Size']}")
            print(f"Last Modified: {artifact['LastModified']}")
            print("-" * 30)
            
        # Get user input for action
        print("\nAvailable actions:")
        print("1. Download artifact")
        print("2. Upload artifact")
        print("3. Delete artifact")
        print("4. Get artifact metadata")
        print("5. Update artifact metadata")
        print("6. Sync artifacts")
        print("7. Create model version")
        print("8. List model versions")
        print("9. Exit")
        
        while True:
            action = input("\nEnter action number (1-9): ")
            
            if action == '9':
                break
                
            if action in ['1', '2', '3', '4', '5']:
                key = input("Enter artifact key: ")
                
                if action == '1':
                    local_path = input("Enter local path: ")
                    if manager.download_artifact(key, local_path):
                        print(f"Successfully downloaded artifact to {local_path}")
                        
                elif action == '2':
                    local_path = input("Enter local path: ")
                    if manager.upload_artifact(local_path, key):
                        print(f"Successfully uploaded artifact from {local_path}")
                        
                elif action == '3':
                    if manager.delete_artifact(key):
                        print(f"Successfully deleted artifact: {key}")
                        
                elif action == '4':
                    metadata = manager.get_artifact_metadata(key)
                    if metadata:
                        print("\nArtifact Metadata:")
                        for k, v in metadata.items():
                            print(f"{k}: {v}")
                            
                elif action == '5':
                    metadata = {}
                    while True:
                        key = input("Enter metadata key (or 'done' to finish): ")
                        if key.lower() == 'done':
                            break
                        value = input("Enter metadata value: ")
                        metadata[key] = value
                    if manager.update_artifact_metadata(key, metadata):
                        print(f"Successfully updated metadata for artifact: {key}")
                        
            elif action == '6':
                local_dir = input("Enter local directory path: ")
                if manager.sync_artifacts(local_dir):
                    print("Successfully synced artifacts")
                    
            elif action in ['7', '8']:
                model_name = input("Enter model name: ")
                
                if action == '7':
                    version = input("Enter version: ")
                    metadata = {}
                    while True:
                        key = input("Enter metadata key (or 'done' to finish): ")
                        if key.lower() == 'done':
                            break
                        value = input("Enter metadata value: ")
                        metadata[key] = value
                    if manager.create_version(model_name, version, metadata):
                        print(f"Successfully created version {version} for model {model_name}")
                        
                elif action == '8':
                    versions = manager.list_versions(model_name)
                    if versions:
                        print(f"\nVersions for model {model_name}:")
                        for version in versions:
                            print(f"Version: {version['version']}")
                            print(f"Created: {version['created_at']}")
                            print("-" * 30)
                    else:
                        print(f"No versions found for model {model_name}")
                        
    except Exception as e:
        logger.error(f"Failed to manage artifacts: {str(e)}")
        print("\nFailed to manage artifacts. Please check the logs above.")

if __name__ == "__main__":
    main() 