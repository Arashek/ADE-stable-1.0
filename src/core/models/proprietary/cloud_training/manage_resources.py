import os
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AWSResourceManager:
    def __init__(self):
        """Initialize AWS resource manager"""
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.s3 = boto3.client('s3')
        self.iam = boto3.client('iam')
        self.ecr = boto3.client('ecr')
        self.logs = boto3.client('logs')
        
    def create_s3_bucket(self, bucket_name: str):
        """Create an S3 bucket for training data"""
        try:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            logger.info(f"Created S3 bucket: {bucket_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                logger.info(f"S3 bucket {bucket_name} already exists")
                return True
            logger.error(f"Failed to create S3 bucket: {str(e)}")
            return False
            
    def create_sagemaker_role(self, role_name: str):
        """Create IAM role for SageMaker training"""
        try:
            # Create the role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sagemaker.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=str(assume_role_policy)
            )
            
            # Attach required policies
            required_policies = [
                'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess',
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
            ]
            
            for policy_arn in required_policies:
                self.iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                
            logger.info(f"Created SageMaker role: {role_name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                logger.info(f"SageMaker role {role_name} already exists")
                return True
            logger.error(f"Failed to create SageMaker role: {str(e)}")
            return False
            
    def create_ecr_repository(self, repo_name: str):
        """Create ECR repository for training images"""
        try:
            self.ecr.create_repository(
                repositoryName=repo_name,
                imageScanningConfiguration={
                    'scanOnPush': True
                }
            )
            logger.info(f"Created ECR repository: {repo_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
                logger.info(f"ECR repository {repo_name} already exists")
                return True
            logger.error(f"Failed to create ECR repository: {str(e)}")
            return False
            
    def create_cloudwatch_log_group(self, log_group: str):
        """Create CloudWatch log group for training logs"""
        try:
            self.logs.create_log_group(logGroupName=log_group)
            logger.info(f"Created CloudWatch log group: {log_group}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                logger.info(f"CloudWatch log group {log_group} already exists")
                return True
            logger.error(f"Failed to create CloudWatch log group: {str(e)}")
            return False
            
    def setup_resources(self):
        """Set up all required AWS resources"""
        config = {
            's3_bucket': 'ade-training-data',
            'sagemaker_role': 'SageMakerTrainingRole',
            'ecr_repo': 'ade-training',
            'log_group': '/aws/sagemaker/TrainingJobs'
        }
        
        results = {
            'S3 Bucket': self.create_s3_bucket(config['s3_bucket']),
            'SageMaker Role': self.create_sagemaker_role(config['sagemaker_role']),
            'ECR Repository': self.create_ecr_repository(config['ecr_repo']),
            'CloudWatch Logs': self.create_cloudwatch_log_group(config['log_group'])
        }
        
        # Print summary
        print("\nResource Setup Summary:")
        print("-" * 50)
        for resource, status in results.items():
            print(f"{resource}: {'✓' if status else '✗'}")
            
        return all(results.values())

def main():
    """Main function to set up AWS resources"""
    try:
        manager = AWSResourceManager()
        if manager.setup_resources():
            print("\nAll AWS resources have been set up successfully!")
        else:
            print("\nSome resources failed to set up. Please check the logs above.")
    except Exception as e:
        logger.error(f"Failed to set up AWS resources: {str(e)}")
        print("\nFailed to set up AWS resources. Please check the logs above.")

if __name__ == "__main__":
    main() 