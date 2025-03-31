import os
import logging
import shutil
import tarfile
from pathlib import Path
from typing import List, Optional
import boto3
from .config import CloudTrainingConfig

logger = logging.getLogger(__name__)

class TrainingPackageManager:
    """Manages packaging and uploading of training code"""
    
    def __init__(self, cloud_config: CloudTrainingConfig):
        self.cloud_config = cloud_config
        self.s3_client = boto3.client('s3')
        self.temp_dir = Path("temp_package")
        
    def package_training_code(
        self,
        source_dir: str,
        dependencies: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> str:
        """Package training code and dependencies"""
        try:
            # Create temporary directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Copy source code
            source_path = Path(source_dir)
            self._copy_directory(source_path, self.temp_dir, exclude_patterns)
            
            # Copy dependencies
            if dependencies:
                self._copy_dependencies(dependencies)
                
            # Create requirements.txt
            self._create_requirements()
            
            # Create entry point script
            self._create_entry_point()
            
            # Create package archive
            package_path = self._create_archive()
            
            return package_path
            
        except Exception as e:
            logger.error(f"Failed to package training code: {str(e)}")
            raise
        finally:
            # Clean up temporary directory
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                
    def upload_package(self, package_path: str, job_name: str) -> str:
        """Upload packaged code to S3"""
        try:
            s3_key = f"training/code/{job_name}/package.tar.gz"
            
            logger.info(f"Uploading package to s3://{self.cloud_config.bucket}/{s3_key}")
            
            self.s3_client.upload_file(
                package_path,
                self.cloud_config.bucket,
                s3_key
            )
            
            return f"s3://{self.cloud_config.bucket}/{s3_key}"
            
        except Exception as e:
            logger.error(f"Failed to upload package: {str(e)}")
            raise
            
    def _copy_directory(
        self,
        source: Path,
        target: Path,
        exclude_patterns: Optional[List[str]] = None
    ):
        """Copy directory with optional exclusions"""
        if exclude_patterns is None:
            exclude_patterns = [
                "*.pyc",
                "__pycache__",
                "*.git*",
                "*.env",
                "*.log"
            ]
            
        for item in source.rglob("*"):
            if item.is_file():
                # Check if file should be excluded
                if any(item.match(pattern) for pattern in exclude_patterns):
                    continue
                    
                # Calculate relative path
                rel_path = item.relative_to(source)
                target_path = target / rel_path
                
                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(item, target_path)
                
    def _copy_dependencies(self, dependencies: List[str]):
        """Copy dependency directories"""
        for dep in dependencies:
            dep_path = Path(dep)
            if not dep_path.exists():
                raise ValueError(f"Dependency directory not found: {dep}")
                
            target_path = self.temp_dir / dep_path.name
            shutil.copytree(dep_path, target_path)
            
    def _create_requirements(self):
        """Create requirements.txt file"""
        requirements = [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "datasets>=2.12.0",
            "peft>=0.4.0",
            "accelerate>=0.20.0",
            "bitsandbytes>=0.41.0",
            "sagemaker>=2.150.0",
            "boto3>=1.26.0"
        ]
        
        with open(self.temp_dir / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))
            
    def _create_entry_point(self):
        """Create entry point script for training"""
        entry_point = """#!/usr/bin/env python3
import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Load hyperparameters
    hyperparameters = json.loads(os.environ.get("SM_HYPERPARAMETERS", "{}"))
    
    # Load model and training configs
    model_config = json.loads(hyperparameters.get("model_config", "{}"))
    training_config = json.loads(hyperparameters.get("training_config", "{}"))
    
    # Set up training data path
    train_data = os.environ.get("SM_CHANNEL_TRAINING")
    if not train_data:
        raise ValueError("No training data channel found")
        
    # Import and run training
    from src.core.models.proprietary.train_code_completion import train_code_completion_model
    
    try:
        model_path = train_code_completion_model(
            codebase_path=train_data,
            output_dir=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"),
            base_model=model_config.get("model_path"),
            num_examples=training_config.get("num_examples", 1000),
            synthetic_ratio=training_config.get("synthetic_ratio", 0.3)
        )
        
        logger.info(f"Training completed. Model saved to: {model_path}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
"""
        
        entry_point_path = self.temp_dir / "train.py"
        with open(entry_point_path, "w") as f:
            f.write(entry_point)
            
        # Make entry point executable
        os.chmod(entry_point_path, 0o755)
        
    def _create_archive(self) -> str:
        """Create tar.gz archive of package"""
        archive_path = Path("package.tar.gz")
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(self.temp_dir, arcname="")
            
        return str(archive_path) 