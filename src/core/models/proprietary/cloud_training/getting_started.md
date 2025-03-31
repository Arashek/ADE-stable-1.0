# Getting Started with Cloud Training

This guide will help you set up and use the cloud training system for your ADE models.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Docker installed locally
4. Python 3.8+ with required packages installed

## Setup Steps

1. Configure AWS Credentials:
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and default region.

2. Set up AWS Resources:
   ```bash
   python -m src.core.models.proprietary.cloud_training.setup_aws
   ```
   This will create:
   - S3 bucket for training data and artifacts
   - IAM role for SageMaker training
   - CloudWatch log group for training metrics

3. Build and Push Training Image:
   ```bash
   python -m src.core.models.proprietary.cloud_training.build_image
   ```
   This will:
   - Build the Docker image with training environment
   - Push the image to Amazon ECR

4. Launch a Training Job:
   ```bash
   python -m src.core.models.proprietary.cloud_training.launch \
     --codebase_path src \
     --output_dir trained_models \
     --base_model deepseek-ai/deepseek-coder-1.3b-instruct \
     --num_examples 1000 \
     --synthetic_ratio 0.3 \
     --instance_type ml.g4dn.xlarge \
     --instance_count 1 \
     --max_runtime 3600
   ```

## Monitoring Training

1. View Training Metrics:
   - Access CloudWatch metrics in the AWS Console
   - Look for metrics under the namespace "SageMaker/TrainingJobs"

2. Monitor Costs:
   - Check AWS Cost Explorer for training costs
   - Set up CloudWatch alarms for cost thresholds

3. View Logs:
   - Access training logs in CloudWatch Logs
   - Look for logs under "/aws/sagemaker/TrainingJobs"

## Model Synchronization

The system automatically syncs model checkpoints and final models to your local storage:
- Checkpoints are synced every 30 minutes (configurable)
- Final model is synced when training completes
- Models are registered in the local registry

## Troubleshooting

1. Training Job Fails:
   - Check CloudWatch logs for error messages
   - Verify IAM permissions
   - Ensure sufficient resources (memory, GPU)

2. Sync Issues:
   - Check S3 bucket permissions
   - Verify local storage space
   - Check network connectivity

3. Cost Issues:
   - Monitor instance usage
   - Set up cost alerts
   - Use spot instances for cost savings

## Best Practices

1. Resource Management:
   - Use appropriate instance types
   - Set reasonable max runtime
   - Monitor resource utilization

2. Cost Optimization:
   - Use spot instances when possible
   - Clean up unused resources
   - Monitor and set cost alerts

3. Security:
   - Use IAM roles with least privilege
   - Encrypt sensitive data
   - Follow AWS security best practices

## Support

For issues or questions:
1. Check the logs in CloudWatch
2. Review AWS documentation
3. Contact the development team 