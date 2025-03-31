import os
import logging
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TrainingJobManager:
    def __init__(self):
        """Initialize training job manager"""
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.sagemaker = boto3.client('sagemaker')
        self.s3 = boto3.client('s3')
        
    def list_jobs(self, status=None):
        """List all training jobs with optional status filter"""
        try:
            params = {}
            if status:
                params['StatusEquals'] = status
                
            jobs = self.sagemaker.list_training_jobs(**params)
            return jobs['TrainingJobSummaries']
        except ClientError as e:
            logger.error(f"Failed to list training jobs: {str(e)}")
            return []
            
    def get_job_details(self, job_name: str):
        """Get detailed information about a training job"""
        try:
            job = self.sagemaker.describe_training_job(TrainingJobName=job_name)
            return job
        except ClientError as e:
            logger.error(f"Failed to get job details: {str(e)}")
            return None
            
    def stop_job(self, job_name: str):
        """Stop a running training job"""
        try:
            self.sagemaker.stop_training_job(TrainingJobName=job_name)
            logger.info(f"Stopped training job: {job_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to stop training job: {str(e)}")
            return False
            
    def delete_job(self, job_name: str):
        """Delete a completed training job"""
        try:
            self.sagemaker.delete_training_job(TrainingJobName=job_name)
            logger.info(f"Deleted training job: {job_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete training job: {str(e)}")
            return False
            
    def get_job_metrics(self, job_name: str):
        """Get training metrics for a job"""
        try:
            job = self.get_job_details(job_name)
            if not job:
                return None
                
            metrics = []
            for metric in job.get('FinalMetricDataList', []):
                metrics.append({
                    'name': metric['MetricName'],
                    'value': metric['Value'],
                    'timestamp': metric['Timestamp']
                })
            return metrics
        except Exception as e:
            logger.error(f"Failed to get job metrics: {str(e)}")
            return None
            
    def get_job_logs(self, job_name: str):
        """Get CloudWatch logs for a training job"""
        try:
            job = self.get_job_details(job_name)
            if not job:
                return None
                
            log_group = f"/aws/sagemaker/TrainingJobs/{job_name}"
            logs = boto3.client('logs')
            log_streams = logs.describe_log_streams(logGroupName=log_group)
            
            logs_data = []
            for stream in log_streams['logStreams']:
                events = logs.get_log_events(
                    logGroupName=log_group,
                    logStreamName=stream['logStreamName']
                )
                logs_data.extend(events['events'])
                
            return logs_data
        except Exception as e:
            logger.error(f"Failed to get job logs: {str(e)}")
            return None
            
    def get_job_cost(self, job_name: str):
        """Get estimated cost for a training job"""
        try:
            job = self.get_job_details(job_name)
            if not job:
                return None
                
            # Calculate cost based on instance type and duration
            instance_type = job['ResourceConfig']['InstanceType']
            instance_count = job['ResourceConfig']['InstanceCount']
            duration = job['TrainingTimeInSeconds']
            
            # Get pricing information
            pricing = boto3.client('pricing')
            price_response = pricing.get_products(
                ServiceCode='AmazonSageMaker',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                    {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': self.region},
                    {'Type': 'TERM_MATCH', 'Field': 'usageType', 'Value': 'Training'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                    {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
                ]
            )
            
            if not price_response['PriceList']:
                return None
                
            price = float(price_response['PriceList'][0]['terms']['OnDemand']['pricePerUnit']['USD'])
            hourly_cost = price * instance_count
            total_cost = hourly_cost * (duration / 3600)  # Convert seconds to hours
            
            return {
                'instance_type': instance_type,
                'instance_count': instance_count,
                'duration_hours': duration / 3600,
                'hourly_cost': hourly_cost,
                'total_cost': total_cost
            }
        except Exception as e:
            logger.error(f"Failed to get job cost: {str(e)}")
            return None

def main():
    """Main function to manage training jobs"""
    try:
        manager = TrainingJobManager()
        
        # List all jobs
        print("\nTraining Jobs:")
        print("-" * 50)
        jobs = manager.list_jobs()
        for job in jobs:
            print(f"Name: {job['TrainingJobName']}")
            print(f"Status: {job['TrainingJobStatus']}")
            print(f"Creation Time: {job['CreationTime']}")
            print("-" * 30)
            
        # Get user input for action
        print("\nAvailable actions:")
        print("1. Get job details")
        print("2. Stop job")
        print("3. Delete job")
        print("4. Get job metrics")
        print("5. Get job logs")
        print("6. Get job cost")
        print("7. Exit")
        
        while True:
            action = input("\nEnter action number (1-7): ")
            
            if action == '7':
                break
                
            job_name = input("Enter job name: ")
            
            if action == '1':
                details = manager.get_job_details(job_name)
                if details:
                    print("\nJob Details:")
                    print(f"Status: {details['TrainingJobStatus']}")
                    print(f"Creation Time: {details['CreationTime']}")
                    print(f"Last Modified: {details['LastModifiedTime']}")
                    print(f"Instance Type: {details['ResourceConfig']['InstanceType']}")
                    print(f"Instance Count: {details['ResourceConfig']['InstanceCount']}")
                    
            elif action == '2':
                if manager.stop_job(job_name):
                    print(f"Successfully stopped job: {job_name}")
                    
            elif action == '3':
                if manager.delete_job(job_name):
                    print(f"Successfully deleted job: {job_name}")
                    
            elif action == '4':
                metrics = manager.get_job_metrics(job_name)
                if metrics:
                    print("\nJob Metrics:")
                    for metric in metrics:
                        print(f"{metric['name']}: {metric['value']}")
                        
            elif action == '5':
                logs = manager.get_job_logs(job_name)
                if logs:
                    print("\nJob Logs:")
                    for log in logs:
                        print(f"{log['timestamp']}: {log['message']}")
                        
            elif action == '6':
                cost = manager.get_job_cost(job_name)
                if cost:
                    print("\nJob Cost:")
                    print(f"Instance Type: {cost['instance_type']}")
                    print(f"Instance Count: {cost['instance_count']}")
                    print(f"Duration (hours): {cost['duration_hours']:.2f}")
                    print(f"Hourly Cost: ${cost['hourly_cost']:.2f}")
                    print(f"Total Cost: ${cost['total_cost']:.2f}")
                    
    except Exception as e:
        logger.error(f"Failed to manage training jobs: {str(e)}")
        print("\nFailed to manage training jobs. Please check the logs above.")

if __name__ == "__main__":
    main() 