import os
import logging
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from .config import CloudTrainingConfig, ModelRegistryConfig
from .manager import CloudTrainingManager
from .package import TrainingPackageManager
from .sync import ModelSyncManager
from .monitoring import TrainingMonitor

logger = logging.getLogger(__name__)

async def launch_training_job(
    codebase_path: str,
    output_dir: str,
    base_model: str,
    cloud_config: CloudTrainingConfig,
    registry_config: ModelRegistryConfig,
    model_config: Optional[Dict[str, Any]] = None,
    training_config: Optional[Dict[str, Any]] = None,
    num_examples: int = 1000,
    synthetic_ratio: float = 0.3
) -> str:
    """Launch a cloud training job"""
    try:
        # Initialize managers
        training_manager = CloudTrainingManager(cloud_config, registry_config)
        package_manager = TrainingPackageManager(cloud_config)
        sync_manager = ModelSyncManager(cloud_config)
        monitor = TrainingMonitor(cloud_config)
        
        # Prepare model and training configs
        if model_config is None:
            model_config = {
                "model_type": "deepseek-coder",
                "model_path": base_model,
                "max_length": 2048,
                "batch_size": 4,
                "quantization": "4bit",
                "device": "cuda",
                "dtype": "float16"
            }
            
        if training_config is None:
            training_config = {
                "max_steps": 1000,
                "learning_rate": 2e-5,
                "weight_decay": 0.01,
                "warmup_steps": 100,
                "logging_steps": 10,
                "save_steps": 100,
                "eval_steps": 100,
                "gradient_accumulation_steps": 4,
                "gradient_checkpointing": True,
                "fp16": True,
                "bf16": False,
                "lora_rank": 8,
                "lora_alpha": 16,
                "lora_dropout": 0.05,
                "max_grad_norm": 1.0,
                "num_examples": num_examples,
                "synthetic_ratio": synthetic_ratio
            }
            
        # Package and upload training code
        logger.info("Packaging training code...")
        package_path = package_manager.package_training_code(
            source_dir=codebase_path,
            dependencies=["src/core/models/proprietary"]
        )
        
        # Create unique job name
        job_name = f"ade-training-{os.getpid()}"
        
        # Upload package
        code_s3_path = package_manager.upload_package(package_path, job_name)
        
        # Prepare training job
        logger.info("Preparing training job...")
        training_job_config = training_manager.prepare_training_job(
            training_code_path=code_s3_path,
            training_data_path=codebase_path,
            model_config=model_config,
            training_config=training_config
        )
        
        # Start training job
        logger.info("Starting training job...")
        job_name = training_manager.start_training_job(training_job_config)
        
        # Start monitoring
        monitor.start_monitoring(job_name)
        
        # Start model synchronization
        asyncio.create_task(sync_manager.sync_checkpoint(job_name, None))
        
        return job_name
        
    except Exception as e:
        logger.error(f"Failed to launch training job: {str(e)}")
        raise

def main():
    """Main function to launch cloud training jobs"""
    parser = argparse.ArgumentParser(description="Launch cloud training job")
    parser.add_argument("--codebase_path", type=str, required=True, help="Path to the codebase to train on")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the trained model")
    parser.add_argument("--base_model", type=str, default="deepseek-ai/deepseek-coder-1.3b-instruct", help="Base model to fine-tune")
    parser.add_argument("--num_examples", type=int, default=1000, help="Number of training examples to collect")
    parser.add_argument("--synthetic_ratio", type=float, default=0.3, help="Ratio of synthetic examples to generate")
    parser.add_argument("--instance_type", type=str, default="ml.g4dn.xlarge", help="SageMaker instance type")
    parser.add_argument("--instance_count", type=int, default=1, help="Number of training instances")
    parser.add_argument("--max_runtime", type=int, default=86400, help="Maximum training runtime in seconds")
    
    args = parser.parse_args()
    
    try:
        # Configure cloud training
        cloud_config = CloudTrainingConfig(
            instance_type=args.instance_type,
            instance_count=args.instance_count,
            max_runtime=args.max_runtime
        )
        
        # Configure model registry
        registry_config = ModelRegistryConfig()
        
        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Launch training job
        job_name = loop.run_until_complete(launch_training_job(
            codebase_path=args.codebase_path,
            output_dir=args.output_dir,
            base_model=args.base_model,
            cloud_config=cloud_config,
            registry_config=registry_config,
            num_examples=args.num_examples,
            synthetic_ratio=args.synthetic_ratio
        ))
        
        logger.info(f"Training job launched successfully. Job name: {job_name}")
        
    except Exception as e:
        logger.error(f"Failed to launch training job: {str(e)}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    main() 