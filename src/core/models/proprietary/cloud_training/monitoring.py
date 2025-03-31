import os
import logging
import json
import boto3
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from .config import CloudTrainingConfig

logger = logging.getLogger(__name__)

class TrainingMonitor:
    """Monitors training progress and costs"""
    
    def __init__(self, cloud_config: CloudTrainingConfig):
        self.cloud_config = cloud_config
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.sagemaker_client = boto3.client('sagemaker')
        self.metrics_cache = {}
        self.cost_cache = {}
        
    def start_monitoring(self, job_name: str):
        """Start monitoring a training job"""
        try:
            logger.info(f"Starting monitoring for job: {job_name}")
            
            # Initialize metrics cache
            self.metrics_cache[job_name] = {
                "loss": [],
                "eval_loss": [],
                "learning_rate": [],
                "last_update": None
            }
            
            # Initialize cost cache
            self.cost_cache[job_name] = {
                "total_cost": 0.0,
                "last_update": None
            }
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            raise
            
    def get_latest_metrics(self, job_name: str) -> Dict[str, Any]:
        """Get latest training metrics"""
        try:
            # Check if we need to update metrics
            current_time = time.time()
            last_update = self.metrics_cache[job_name]["last_update"]
            
            if (last_update is None or 
                current_time - last_update > self.cloud_config.metrics_interval):
                
                # Get metrics from CloudWatch
                metrics = self._fetch_metrics(job_name)
                
                # Update cache
                self.metrics_cache[job_name].update(metrics)
                self.metrics_cache[job_name]["last_update"] = current_time
                
            return {
                "loss": self.metrics_cache[job_name]["loss"][-1] if self.metrics_cache[job_name]["loss"] else None,
                "eval_loss": self.metrics_cache[job_name]["eval_loss"][-1] if self.metrics_cache[job_name]["eval_loss"] else None,
                "learning_rate": self.metrics_cache[job_name]["learning_rate"][-1] if self.metrics_cache[job_name]["learning_rate"] else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get latest metrics: {str(e)}")
            raise
            
    def get_estimated_cost(self, job_name: str) -> float:
        """Get estimated cost for the training job"""
        try:
            # Check if we need to update cost
            current_time = time.time()
            last_update = self.cost_cache[job_name]["last_update"]
            
            if (last_update is None or 
                current_time - last_update > self.cloud_config.metrics_interval):
                
                # Get cost from CloudWatch
                cost = self._fetch_cost(job_name)
                
                # Update cache
                self.cost_cache[job_name]["total_cost"] = cost
                self.cost_cache[job_name]["last_update"] = current_time
                
                # Check cost alert threshold
                if cost > self.cloud_config.cost_alert_threshold:
                    logger.warning(f"Training cost ({cost:.2f} USD) exceeds threshold ({self.cloud_config.cost_alert_threshold} USD)")
                    
            return self.cost_cache[job_name]["total_cost"]
            
        except Exception as e:
            logger.error(f"Failed to get estimated cost: {str(e)}")
            raise
            
    def _fetch_metrics(self, job_name: str) -> Dict[str, List[float]]:
        """Fetch metrics from CloudWatch"""
        try:
            metrics = {
                "loss": [],
                "eval_loss": [],
                "learning_rate": []
            }
            
            # Get metrics for each metric name
            for metric_name in metrics.keys():
                response = self.cloudwatch_client.get_metric_data(
                    MetricDataQueries=[
                        {
                            "Id": f"m1_{metric_name}",
                            "MetricStat": {
                                "Metric": {
                                    "Namespace": "SageMaker",
                                    "MetricName": metric_name,
                                    "Dimensions": [
                                        {
                                            "Name": "TrainingJobName",
                                            "Value": job_name
                                        }
                                    ]
                                },
                                "Period": 60,
                                "Stat": "Average"
                            },
                            "StartTime": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                            "EndTime": datetime.now()
                        }
                    ]
                )
                
                # Extract metric values
                if response["MetricDataResults"]:
                    metrics[metric_name] = [
                        float(value) for value in response["MetricDataResults"][0]["Values"]
                    ]
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch metrics: {str(e)}")
            raise
            
    def _fetch_cost(self, job_name: str) -> float:
        """Fetch cost from CloudWatch"""
        try:
            # Get job details to determine instance type and count
            response = self.sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            
            instance_type = response["ResourceConfig"]["InstanceType"]
            instance_count = response["ResourceConfig"]["InstanceCount"]
            
            # Get cost metrics
            response = self.cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        "Id": "m1_cost",
                        "MetricStat": {
                            "Metric": {
                                "Namespace": "AWS/SageMaker",
                                "MetricName": "Cost",
                                "Dimensions": [
                                    {
                                        "Name": "TrainingJobName",
                                        "Value": job_name
                                    }
                                ]
                            },
                            "Period": 3600,  # 1 hour
                            "Stat": "Sum"
                        },
                        "StartTime": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                        "EndTime": datetime.now()
                    }
                ]
            )
            
            # Calculate total cost
            if response["MetricDataResults"]:
                return sum(float(value) for value in response["MetricDataResults"][0]["Values"])
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to fetch cost: {str(e)}")
            raise 