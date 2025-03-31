import os
import logging
import boto3
import json
from pathlib import Path
from .config import CloudTrainingConfig

logger = logging.getLogger(__name__)

def setup_aws_resources(cloud_config: CloudTrainingConfig):
    """Set up required AWS resources for training"""
    try:
        # Initialize AWS clients
        iam_client = boto3.client('iam')
        s3_client = boto3.client('s3')
        
        # Create S3 bucket if it doesn't exist
        try:
            s3_client.head_bucket(Bucket=cloud_config.bucket)
            logger.info(f"S3 bucket {cloud_config.bucket} already exists")
        except:
            s3_client.create_bucket(
                Bucket=cloud_config.bucket,
                CreateBucketConfiguration={'LocationConstraint': cloud_config.region}
            )
            logger.info(f"Created S3 bucket: {cloud_config.bucket}")
            
        # Create IAM role for SageMaker
        role_name = "SageMakerTrainingRole"
        try:
            response = iam_client.get_role(RoleName=role_name)
            role_arn = response['Role']['Arn']
            logger.info(f"IAM role {role_name} already exists")
        except:
            # Create role
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
            
            response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy)
            )
            role_arn = response['Role']['Arn']
            
            # Attach required policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            ]
            
            for policy in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy
                )
                
            logger.info(f"Created IAM role: {role_name}")
            
        # Update role ARN in config
        cloud_config.role_arn = role_arn
        
        # Create CloudWatch log group
        logs_client = boto3.client('logs')
        log_group = "/aws/sagemaker/TrainingJobs"
        try:
            logs_client.describe_log_groups(logGroupNamePrefix=log_group)
            logger.info(f"CloudWatch log group {log_group} already exists")
        except:
            logs_client.create_log_group(logGroupName=log_group)
            logger.info(f"Created CloudWatch log group: {log_group}")
            
        return {
            "bucket": cloud_config.bucket,
            "role_arn": role_arn,
            "log_group": log_group
        }
        
    except Exception as e:
        logger.error(f"Failed to set up AWS resources: {str(e)}")
        raise

def main():
    """Main function to set up AWS resources"""
    try:
        # Configure cloud training
        cloud_config = CloudTrainingConfig()
        
        # Set up AWS resources
        resources = setup_aws_resources(cloud_config)
        
        print("AWS resources set up successfully:")
        print(f"S3 bucket: {resources['bucket']}")
        print(f"IAM role: {resources['role_arn']}")
        print(f"CloudWatch log group: {resources['log_group']}")
        
    except Exception as e:
        print(f"Failed to set up AWS resources: {str(e)}")
        raise

if __name__ == "__main__":
    main() 