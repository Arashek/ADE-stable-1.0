# ADE Cloud Training System

This module provides functionality for training ADE models on cloud GPU services while maintaining local access to the models. It supports AWS SageMaker for distributed training and includes features for model synchronization, monitoring, and versioning.

## Features

- Cloud GPU training pipeline using AWS SageMaker
- Secure credential management for cloud access
- Real-time training monitoring and cost optimization
- Bidirectional model synchronization
- Model registry with versioning and metadata
- Integration with ADE platform provider registry

## Prerequisites

1. AWS Account with SageMaker access
2. AWS CLI configured with appropriate credentials
3. Required Python packages:
   ```
   boto3>=1.26.0
   sagemaker>=2.150.0
   torch>=2.0.0
   transformers>=4.30.0
   datasets>=2.12.0
   peft>=0.4.0
   accelerate>=0.20.0
   bitsandbytes>=0.41.0
   ```

## Configuration

1. Set up AWS credentials:
   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   export AWS_DEFAULT_REGION="your_region"
   ```

2. Configure SageMaker role:
   - Create an IAM role with SageMaker permissions
   - Update the `role_arn` in `CloudTrainingConfig`

3. Set up S3 bucket:
   - Create an S3 bucket for training artifacts
   - Update the `bucket` parameter in `CloudTrainingConfig`

## Usage

### Launch Training Job

```python
from src.core.models.proprietary.cloud_training.launch import launch_training_job
from src.core.models.proprietary.cloud_training.config import CloudTrainingConfig, ModelRegistryConfig

# Configure cloud training
cloud_config = CloudTrainingConfig(
    instance_type="ml.g4dn.xlarge",  # GPU instance
    instance_count=1,
    max_runtime=86400  # 24 hours
)

# Configure model registry
registry_config = ModelRegistryConfig()

# Launch training job
job_name = await launch_training_job(
    codebase_path="path/to/codebase",
    output_dir="path/to/output",
    base_model="deepseek-ai/deepseek-coder-1.3b-instruct",
    cloud_config=cloud_config,
    registry_config=registry_config,
    num_examples=1000,
    synthetic_ratio=0.3
)
```

### Command Line Interface

```bash
python -m src.core.models.proprietary.cloud_training.launch \
    --codebase_path path/to/codebase \
    --output_dir path/to/output \
    --base_model deepseek-ai/deepseek-coder-1.3b-instruct \
    --num_examples 1000 \
    --synthetic_ratio 0.3 \
    --instance_type ml.g4dn.xlarge \
    --instance_count 1 \
    --max_runtime 86400
```

## Architecture

### Components

1. **CloudTrainingManager**: Manages cloud-based training operations
   - Handles AWS SageMaker job creation and management
   - Manages S3 storage for training artifacts
   - Coordinates with other components

2. **TrainingPackageManager**: Packages and uploads training code
   - Creates training package with dependencies
   - Handles code upload to S3
   - Manages entry point script creation

3. **ModelSyncManager**: Handles model synchronization
   - Downloads model checkpoints during training
   - Syncs completed models to local storage
   - Manages version tracking

4. **TrainingMonitor**: Tracks training progress and costs
   - Monitors training metrics via CloudWatch
   - Tracks resource usage and costs
   - Provides real-time status updates

### Data Flow

1. Training code and data are packaged and uploaded to S3
2. SageMaker training job is launched with configured parameters
3. Training progress is monitored via CloudWatch metrics
4. Model checkpoints are periodically synced to local storage
5. Completed models are registered in the model registry

## Model Registry

The model registry provides:
- Version tracking for trained models
- Performance metrics storage
- Model metadata management
- Integration with ADE platform provider registry

### Registry Structure

```
models/
  registry/
    model_name-v1/
      metadata.json
      performance_metrics.json
      model_artifacts/
    model_name-v2/
      ...
```

## Cost Optimization

The system includes several cost optimization features:
- Automatic cost monitoring and alerts
- Configurable training time limits
- Resource usage optimization
- Checkpoint-based training resumption

## Security

- AWS credentials are managed securely
- S3 bucket access is controlled via IAM roles
- Training data is encrypted in transit and at rest
- Model artifacts are protected with versioning

## Monitoring and Logging

- Real-time training metrics via CloudWatch
- Cost tracking and alerts
- Training progress monitoring
- Error logging and debugging

## Troubleshooting

Common issues and solutions:

1. **Credential Errors**
   - Verify AWS credentials are properly configured
   - Check IAM role permissions

2. **S3 Access Issues**
   - Verify bucket permissions
   - Check IAM role S3 access

3. **Training Job Failures**
   - Check CloudWatch logs
   - Verify resource limits
   - Review error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This module is part of the ADE platform and follows its licensing terms. 