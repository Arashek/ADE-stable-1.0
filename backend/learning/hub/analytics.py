from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from .models import AnalyticsData, AnalyticsReport, InstanceData
from ...config.logging_config import logger

class AnalyticsEngine:
    """Engine for processing and analyzing collected data"""
    
    def __init__(self):
        self.data: Dict[str, List[AnalyticsData]] = {}
        self.reports: Dict[str, AnalyticsReport] = {}
        
    async def process_data(self, data: List[AnalyticsData]):
        """Process new analytics data"""
        try:
            for entry in data:
                instance_id = entry.instance_id
                if instance_id not in self.data:
                    self.data[instance_id] = []
                self.data[instance_id].append(entry)
                
            # Generate reports for updated data
            await self._generate_reports()
            
        except Exception as e:
            logger.error(f"Error processing analytics data: {str(e)}")
            
    async def _generate_reports(self):
        """Generate analytics reports"""
        try:
            # Generate performance report
            performance_report = await self._generate_performance_report()
            self.reports["performance"] = performance_report
            
            # Generate usage report
            usage_report = await self._generate_usage_report()
            self.reports["usage"] = usage_report
            
            # Generate anomaly report
            anomaly_report = await self._generate_anomaly_report()
            self.reports["anomaly"] = anomaly_report
            
        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}")
            
    async def _generate_performance_report(self) -> AnalyticsReport:
        """Generate performance analytics report"""
        try:
            performance_metrics = {}
            
            for instance_id, data in self.data.items():
                # Calculate instance performance metrics
                instance_metrics = self._calculate_instance_performance(data)
                performance_metrics[instance_id] = instance_metrics
                
            # Calculate aggregate metrics
            aggregate_metrics = self._calculate_aggregate_performance(performance_metrics)
            
            report = AnalyticsReport(
                type="performance",
                content={
                    "instance_metrics": performance_metrics,
                    "aggregate_metrics": aggregate_metrics
                },
                period={
                    "start": datetime.utcnow() - timedelta(days=7),
                    "end": datetime.utcnow()
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return None
            
    def _calculate_instance_performance(self, data: List[AnalyticsData]) -> Dict[str, float]:
        """Calculate performance metrics for an instance"""
        try:
            metrics = {}
            
            # Extract metrics from data
            metric_values = {
                metric: [entry.metrics.get(metric, 0) for entry in data]
                for metric in set().union(*[entry.metrics.keys() for entry in data])
            }
            
            # Calculate statistics for each metric
            for metric, values in metric_values.items():
                if values:
                    metrics[f"{metric}_mean"] = np.mean(values)
                    metrics[f"{metric}_std"] = np.std(values)
                    metrics[f"{metric}_min"] = np.min(values)
                    metrics[f"{metric}_max"] = np.max(values)
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating instance performance: {str(e)}")
            return {}
            
    def _calculate_aggregate_performance(self, instance_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate aggregate performance metrics"""
        try:
            aggregate = {}
            
            # Get all metric types
            metric_types = set().union(*[metrics.keys() for metrics in instance_metrics.values()])
            
            # Calculate aggregate statistics for each metric type
            for metric_type in metric_types:
                values = [
                    metrics[metric_type]
                    for metrics in instance_metrics.values()
                    if metric_type in metrics
                ]
                
                if values:
                    aggregate[f"aggregate_{metric_type}_mean"] = np.mean(values)
                    aggregate[f"aggregate_{metric_type}_std"] = np.std(values)
                    
            return aggregate
            
        except Exception as e:
            logger.error(f"Error calculating aggregate performance: {str(e)}")
            return {}
            
    async def _generate_usage_report(self) -> AnalyticsReport:
        """Generate usage analytics report"""
        try:
            usage_metrics = {}
            
            for instance_id, data in self.data.items():
                # Calculate instance usage metrics
                instance_metrics = self._calculate_instance_usage(data)
                usage_metrics[instance_id] = instance_metrics
                
            # Calculate aggregate usage
            aggregate_usage = self._calculate_aggregate_usage(usage_metrics)
            
            report = AnalyticsReport(
                type="usage",
                content={
                    "instance_usage": usage_metrics,
                    "aggregate_usage": aggregate_usage
                },
                period={
                    "start": datetime.utcnow() - timedelta(days=7),
                    "end": datetime.utcnow()
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating usage report: {str(e)}")
            return None
            
    def _calculate_instance_usage(self, data: List[AnalyticsData]) -> Dict[str, Any]:
        """Calculate usage metrics for an instance"""
        try:
            usage = {
                "total_events": len(data),
                "event_types": {},
                "time_distribution": {}
            }
            
            # Count event types
            for entry in data:
                for event in entry.events:
                    event_type = event.get("type", "unknown")
                    if event_type not in usage["event_types"]:
                        usage["event_types"][event_type] = 0
                    usage["event_types"][event_type] += 1
                    
            # Calculate time distribution
            for entry in data:
                hour = entry.timestamp.hour
                if hour not in usage["time_distribution"]:
                    usage["time_distribution"][hour] = 0
                usage["time_distribution"][hour] += 1
                
            return usage
            
        except Exception as e:
            logger.error(f"Error calculating instance usage: {str(e)}")
            return {}
            
    def _calculate_aggregate_usage(self, instance_usage: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate usage metrics"""
        try:
            aggregate = {
                "total_instances": len(instance_usage),
                "total_events": sum(usage["total_events"] for usage in instance_usage.values()),
                "event_types": {},
                "time_distribution": {}
            }
            
            # Aggregate event types
            for usage in instance_usage.values():
                for event_type, count in usage["event_types"].items():
                    if event_type not in aggregate["event_types"]:
                        aggregate["event_types"][event_type] = 0
                    aggregate["event_types"][event_type] += count
                    
            # Aggregate time distribution
            for usage in instance_usage.values():
                for hour, count in usage["time_distribution"].items():
                    if hour not in aggregate["time_distribution"]:
                        aggregate["time_distribution"][hour] = 0
                    aggregate["time_distribution"][hour] += count
                    
            return aggregate
            
        except Exception as e:
            logger.error(f"Error calculating aggregate usage: {str(e)}")
            return {}
            
    async def _generate_anomaly_report(self) -> AnalyticsReport:
        """Generate anomaly detection report"""
        try:
            anomalies = {}
            
            for instance_id, data in self.data.items():
                # Detect anomalies in instance data
                instance_anomalies = self._detect_anomalies(data)
                if instance_anomalies:
                    anomalies[instance_id] = instance_anomalies
                    
            report = AnalyticsReport(
                type="anomaly",
                content={
                    "anomalies": anomalies
                },
                period={
                    "start": datetime.utcnow() - timedelta(days=7),
                    "end": datetime.utcnow()
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating anomaly report: {str(e)}")
            return None
            
    def _detect_anomalies(self, data: List[AnalyticsData]) -> List[Dict[str, Any]]:
        """Detect anomalies in instance data"""
        try:
            anomalies = []
            
            # Extract metrics for anomaly detection
            metric_values = {
                metric: [entry.metrics.get(metric, 0) for entry in data]
                for metric in set().union(*[entry.metrics.keys() for entry in data])
            }
            
            # Detect anomalies in each metric
            for metric, values in metric_values.items():
                if len(values) > 1:
                    mean = np.mean(values)
                    std = np.std(values)
                    
                    # Check for values outside 3 standard deviations
                    for i, value in enumerate(values):
                        if abs(value - mean) > 3 * std:
                            anomalies.append({
                                "metric": metric,
                                "value": value,
                                "expected_range": [mean - 3 * std, mean + 3 * std],
                                "timestamp": data[i].timestamp
                            })
                            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return []
            
    def get_report(self, report_type: str) -> Optional[AnalyticsReport]:
        """Get a specific analytics report"""
        return self.reports.get(report_type)
        
    def get_all_reports(self) -> Dict[str, AnalyticsReport]:
        """Get all analytics reports"""
        return self.reports.copy() 