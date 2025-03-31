# ADE Training Manager Interactive Tutorial

This tutorial will guide you through setting up and using the ADE Training Manager, including AWS credential management, dataset preparation, and model training.

## Prerequisites

1. Python 3.8 or higher
2. AWS Account with appropriate permissions
3. ADE Platform access
4. Git (for version control)

## Step 1: Environment Setup

First, let's set up the Python environment and install dependencies:

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r src/ade/training_manager/requirements.txt
```

## Step 2: AWS Credential Management

### 2.1 Configure AWS Credentials

1. Open AWS Console and navigate to IAM
2. Create a new IAM user or use existing one
3. Attach the following policies:
   - `AmazonS3FullAccess`
   - `AmazonSageMakerFullAccess`
   - `CloudWatchLogsFullAccess`

4. Generate access keys:
   - Go to IAM → Users → Your User → Security credentials
   - Click "Create access key"
   - Save the Access Key ID and Secret Access Key

5. Update `aws_config.json`:
```json
{
  "region": "us-east-1",  // Update with your region
  "access_key": "YOUR_ACCESS_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "profile_name": "ade-platform",
  "s3_bucket": "your-bucket-name"
}
```

### 2.2 Verify AWS Access

Run the following command to verify AWS credentials:
```bash
python -m ade.training_manager.manager --config config/aws_config.json verify-aws
```

Expected output:
```
✓ AWS credentials verified
✓ S3 bucket access confirmed
✓ SageMaker role permissions verified
```

## Step 3: Dataset Management

### 3.1 Dataset Structure

Create the following directory structure:
```
data/
├── train/
│   ├── code_completion.json
│   └── tool_use.json
├── validation/
│   ├── code_completion.json
│   └── tool_use.json
└── test/
    ├── code_completion.json
    └── tool_use.json
```

### 3.2 Dataset Format

Each dataset file should follow this format:
```json
{
  "data": [
    {
      "input": "Your input text",
      "output": "Expected output",
      "metadata": {
        "source": "source_name",
        "language": "programming_language",
        "difficulty": "easy/medium/hard"
      }
    }
  ]
}
```

### 3.3 Dataset Validation

Run the dataset validation:
```bash
python -m ade.training_manager.manager --config config/training_config.json validate-datasets
```

Expected output:
```
✓ Dataset structure verified
✓ Code completion dataset validated
✓ Tool use dataset validated
```

## Step 4: Training Configuration

### 4.1 Update Training Config

Edit `training_config.json`:
```json
{
  "models": [
    {
      "name": "code_assistant",
      "type": "transformer",
      "base_model": "microsoft/codebert-base",
      "max_length": 512,
      "batch_size": 8,
      "learning_rate": 2e-5,
      "num_train_epochs": 3
    }
  ],
  "datasets": {
    "code_completion": {
      "train_data_path": "data/train/code_completion.json",
      "validation_data_path": "data/validation/code_completion.json",
      "test_data_path": "data/test/code_completion.json"
    }
  }
}
```

### 4.2 Initialize Training Manager

```bash
python -m ade.training_manager.manager --config config/training_config.json init
```

Expected output:
```
✓ Training manager initialized
✓ Directories created
✓ Logging configured
✓ Experiment tracking enabled
```

## Step 5: Model Training

### 5.1 Start Training

```bash
python -m ade.training_manager.manager --config config/training_config.json train code_assistant code_completion
```

Monitor training progress:
```
Epoch 1/3: 100%|██████████| 1000/1000 [00:45<00:00, 22.22it/s]
Loss: 0.1234, Accuracy: 0.8765
```

### 5.2 Monitor Training

1. View training logs:
```bash
python -m ade.training_manager.manager --config config/training_config.json logs
```

2. Check metrics in Weights & Biases:
```bash
python -m ade.training_manager.manager --config config/training_config.json metrics
```

## Step 6: Model Evaluation

### 6.1 Run Evaluation

```bash
python -m ade.training_manager.manager --config config/training_config.json evaluate code_assistant code_completion
```

Expected output:
```
Evaluation Results:
- Accuracy: 0.8765
- F1 Score: 0.8234
- Perplexity: 45.67
```

### 6.2 Generate Reports

```bash
python -m ade.training_manager.manager --config config/training_config.json report code_assistant code_completion
```

## Step 7: Model Deployment

### 7.1 Deploy to AWS

```bash
python -m ade.training_manager.manager --config config/training_config.json deploy code_assistant code_completion production
```

### 7.2 Verify Deployment

```bash
python -m ade.training_manager.manager --config config/training_config.json verify-deployment code_assistant code_completion
```

## Step 8: Platform Integration

### 8.1 Sync with ADE Platform

```bash
python -m ade.training_manager.manager --config config/training_config.json sync
```

### 8.2 Verify Integration

```bash
python -m ade.training_manager.manager --config config/training_config.json verify-integration
```

## Troubleshooting

### Common Issues

1. AWS Credentials
   - Error: "Invalid credentials"
   - Solution: Verify access key and secret key in aws_config.json

2. Dataset Loading
   - Error: "Invalid dataset format"
   - Solution: Check dataset JSON structure matches required format

3. Training Issues
   - Error: "CUDA out of memory"
   - Solution: Reduce batch_size or enable gradient checkpointing

4. Deployment Failures
   - Error: "SageMaker role permissions"
   - Solution: Verify IAM role permissions

## Best Practices

1. Dataset Management
   - Keep datasets versioned
   - Use consistent naming conventions
   - Include metadata for tracking

2. Training
   - Start with small batch size
   - Monitor GPU memory usage
   - Use early stopping

3. Deployment
   - Test in staging first
   - Monitor endpoint metrics
   - Set up alerts

4. Version Control
   - Track configuration changes
   - Document model versions
   - Maintain changelog

## Next Steps

1. Advanced Training
   - Implement distributed training
   - Add custom metrics
   - Optimize hyperparameters

2. Monitoring
   - Set up CloudWatch alerts
   - Configure custom dashboards
   - Implement A/B testing

3. Automation
   - Create CI/CD pipeline
   - Set up automated testing
   - Implement rollback procedures 