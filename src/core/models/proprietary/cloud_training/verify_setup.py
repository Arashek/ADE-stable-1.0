import os
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_aws_credentials():
    """Verify AWS credentials are properly configured"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check required environment variables
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_DEFAULT_REGION'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Try to make an AWS API call
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"Successfully authenticated as: {identity['Arn']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to verify AWS credentials: {str(e)}")
        return False

def verify_s3_bucket(bucket_name: str):
    """Verify S3 bucket exists and is accessible"""
    try:
        s3 = boto3.client('s3')
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"S3 bucket '{bucket_name}' exists and is accessible")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logger.error(f"S3 bucket '{bucket_name}' does not exist")
        elif error_code == '403':
            logger.error(f"Access denied to S3 bucket '{bucket_name}'")
        else:
            logger.error(f"Error accessing S3 bucket '{bucket_name}': {str(e)}")
        return False

def verify_sagemaker_role(role_name: str):
    """Verify SageMaker IAM role exists and has correct permissions"""
    try:
        iam = boto3.client('iam')
        role = iam.get_role(RoleName=role_name)
        logger.info(f"IAM role '{role_name}' exists")
        
        # Check attached policies
        policies = iam.list_attached_role_policies(RoleName=role_name)
        required_policies = {
            'AmazonSageMakerFullAccess',
            'AmazonS3FullAccess',
            'CloudWatchLogsFullAccess'
        }
        
        attached_policies = {p['PolicyName'] for p in policies['AttachedPolicies']}
        missing_policies = required_policies - attached_policies
        
        if missing_policies:
            logger.error(f"Missing required policies: {', '.join(missing_policies)}")
            return False
            
        logger.info("All required policies are attached")
        return True
        
    except ClientError as e:
        logger.error(f"Error verifying IAM role: {str(e)}")
        return False

def verify_ecr_repository(repo_name: str):
    """Verify ECR repository exists"""
    try:
        ecr = boto3.client('ecr')
        ecr.describe_repositories(repositoryNames=[repo_name])
        logger.info(f"ECR repository '{repo_name}' exists")
        return True
    except ClientError as e:
        logger.error(f"Error verifying ECR repository: {str(e)}")
        return False

def verify_cloudwatch_logs(log_group: str):
    """Verify CloudWatch log group exists"""
    try:
        logs = boto3.client('logs')
        logs.describe_log_groups(logGroupNamePrefix=log_group)
        logger.info(f"CloudWatch log group '{log_group}' exists")
        return True
    except ClientError as e:
        logger.error(f"Error verifying CloudWatch log group: {str(e)}")
        return False

def verify_setup():
    """Verify all AWS resources are properly configured"""
    # Configuration
    config = {
        's3_bucket': 'ade-training-data',
        'sagemaker_role': 'SageMakerTrainingRole',
        'ecr_repo': 'ade-training',
        'log_group': '/aws/sagemaker/TrainingJobs'
    }
    
    # Run verifications
    checks = {
        'AWS Credentials': verify_aws_credentials(),
        'S3 Bucket': verify_s3_bucket(config['s3_bucket']),
        'SageMaker Role': verify_sagemaker_role(config['sagemaker_role']),
        'ECR Repository': verify_ecr_repository(config['ecr_repo']),
        'CloudWatch Logs': verify_cloudwatch_logs(config['log_group'])
    }
    
    # Print summary
    print("\nSetup Verification Summary:")
    print("-" * 50)
    for check, status in checks.items():
        print(f"{check}: {'✓' if status else '✗'}")
    
    return all(checks.values())

if __name__ == "__main__":
    if verify_setup():
        print("\nAll checks passed! Your AWS setup is ready for training.")
    else:
        print("\nSome checks failed. Please review the error messages above.") 