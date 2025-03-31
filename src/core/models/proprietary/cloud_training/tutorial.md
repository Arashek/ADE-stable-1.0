# ADE Cloud Training Tutorial

This tutorial will guide you through setting up and using the ADE cloud training system with AWS integration.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Docker installed locally
4. Python 3.8+ with required packages installed
5. Git installed

## Step 1: AWS Setup

### 1.1 Create AWS Account
1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Click "Create an AWS Account"
3. Follow the registration process
4. Set up billing information

### 1.2 Configure AWS CLI
1. Install AWS CLI:
   ```bash
   # Windows (using PowerShell)
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

   # Linux
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```
   Enter your:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., us-east-1)
   - Default output format (json)

### 1.3 Create IAM User
1. Go to AWS IAM Console
2. Click "Users" → "Add user"
3. Set username (e.g., "ade-training")
4. Select "Access key - Programmatic access"
5. Click "Next: Permissions"
6. Click "Attach existing policies directly"
7. Add these policies:
   - AmazonSageMakerFullAccess
   - AmazonS3FullAccess
   - CloudWatchLogsFullAccess
8. Complete user creation
9. Save the Access Key ID and Secret Access Key

## Step 2: Local Environment Setup

### 2.1 Install Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install required packages
pip install -r src/core/models/proprietary/cloud_training/requirements.txt
```

### 2.2 Configure Environment Variables
Create a `.env` file in your project root:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

## Step 3: Set Up AWS Resources

### 3.1 Run Setup Script
```bash
python -m src.core.models.proprietary.cloud_training.setup_aws
```

This will create:
- S3 bucket for training data
- IAM role for SageMaker
- CloudWatch log group

### 3.2 Build and Push Docker Image
```bash
python -m src.core.models.proprietary.cloud_training.build_image
```

This will:
1. Build the training Docker image
2. Create ECR repository
3. Push the image to ECR

## Step 4: Start Training Monitor

### 4.1 Start the Web Interface
```bash
python -m src.core.models.proprietary.training_chat.serve
```

### 4.2 Access the Web Interface
1. Open your browser
2. Navigate to `http://localhost:8000`
3. You should see the ADE Training Monitor interface

## Step 5: Launch Training Job

### 5.1 Prepare Training Data
1. Place your training data in the appropriate directory
2. Ensure data format matches requirements

### 5.2 Start Training
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

### 5.3 Monitor Training
1. In the web interface, click on your training session
2. View real-time metrics:
   - Training loss
   - Validation loss
   - Resource usage
3. Monitor checkpoints
4. Use control buttons to:
   - Pause training
   - Resume training
   - Stop training

## Step 6: AWS Console Monitoring

### 6.1 SageMaker Console
1. Go to AWS SageMaker Console
2. Click "Training jobs"
3. Find your training job
4. View:
   - Job status
   - Training metrics
   - Resource utilization

### 6.2 CloudWatch
1. Go to AWS CloudWatch Console
2. Navigate to "Log groups"
3. Find "/aws/sagemaker/TrainingJobs"
4. View detailed logs

### 6.3 S3 Console
1. Go to AWS S3 Console
2. Find your training bucket
3. View:
   - Training data
   - Model checkpoints
   - Training artifacts

## Step 7: Model Synchronization

### 7.1 Check Local Storage
1. Navigate to your output directory
2. Verify model checkpoints
3. Check final model files

### 7.2 Model Registry
1. Access the model registry
2. View model versions
3. Check model metadata

## Troubleshooting

### Common Issues

1. AWS Credentials
   - Verify credentials in `.env`
   - Check IAM permissions
   - Ensure AWS CLI is configured

2. Web Interface
   - Check if server is running
   - Verify port 8000 is available
   - Check browser console for errors

3. Training Jobs
   - Check CloudWatch logs
   - Verify instance type availability
   - Check S3 bucket permissions

4. Resource Issues
   - Monitor instance limits
   - Check GPU availability
   - Verify storage space

### Getting Help

1. Check logs:
   ```bash
   # View server logs
   tail -f logs/server.log

   # View training logs
   tail -f logs/training.log
   ```

2. Contact support:
   - Email: support@ade-platform.com
   - GitHub Issues: [ADE Platform Issues](https://github.com/your-repo/issues)

## Best Practices

1. Resource Management
   - Use appropriate instance types
   - Set reasonable timeouts
   - Clean up unused resources

2. Cost Optimization
   - Use spot instances when possible
   - Monitor resource usage
   - Set up cost alerts

3. Security
   - Rotate AWS credentials
   - Use IAM roles
   - Enable encryption

4. Monitoring
   - Set up CloudWatch alarms
   - Monitor training metrics
   - Track resource utilization 