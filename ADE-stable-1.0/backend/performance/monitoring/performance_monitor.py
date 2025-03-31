from typing import Dict, Any, List, Optional
import psutil
import time
from datetime import datetime, timedelta
import asyncio
from ...config.logging_config import logger
from ...database.redis_client import redis_client
from ..profiling.api_profiler import APIProfiler
from ..memory.memory_analyzer import MemoryAnalyzer
from ...utils.cache import Cache
from ...utils.anomaly_detection import AnomalyDetector

class PerformanceMonitor:
    """Service for monitoring application performance"""
    
    def __init__(self):
        self.api_profiler = APIProfiler()
        self.memory_analyzer = MemoryAnalyzer()
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 80.0,
            "disk_percent": 90.0,
            "response_time": 2.0,  # seconds
            "error_rate": 5.0  # percentage
        }
        self.cache = Cache()  # Add caching
        self.anomaly_detector = AnomalyDetector()  # Add anomaly detection
        
    async def start_monitoring(self):
        """Start performance monitoring"""
        try:
            self.memory_analyzer.start_tracking()
            
            # Start background monitoring task
            asyncio.create_task(self._monitor_background())
            
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {str(e)}")
            
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        try:
            self.memory_analyzer.stop_tracking()
        except Exception as e:
            logger.error(f"Error stopping performance monitoring: {str(e)}")
            
    async def _monitor_background(self):
        """Background task for continuous monitoring"""
        while True:
            try:
                metrics = await self.collect_metrics()
                await self.analyze_metrics(metrics)
                await self.store_metrics(metrics)
                
                # Sleep for 1 minute before next collection
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
                
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system and application metrics with caching"""
        cache_key = f"metrics_{int(time.time() / 60)}"  # Cache per minute
        
        # Try to get from cache first
        cached_metrics = await self.cache.get(cache_key)
        if cached_metrics:
            return cached_metrics
            
        metrics = {
            "system": await self._collect_system_metrics(),
            "application": await self._collect_app_metrics(),
            "ml_metrics": await self._collect_ml_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in cache
        await self.cache.set(cache_key, metrics, ttl=60)
        
        # Detect anomalies
        await self.anomaly_detector.check_metrics(metrics)
        
        return metrics
            
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
            
    async def _collect_app_metrics(self) -> Dict[str, Any]:
        """Collect application metrics"""
        try:
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "memory_rss": process_memory.rss / 1024 / 1024,  # MB
                "memory_vms": process_memory.vms / 1024 / 1024,  # MB
                "cpu_percent": process.cpu_percent()
            }
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {str(e)}")
            return {}
            
    async def _collect_ml_metrics(self) -> Dict[str, Any]:
        """Collect machine learning metrics"""
        try:
            # TO DO: implement machine learning metrics collection
            return {}
            
        except Exception as e:
            logger.error(f"Error collecting machine learning metrics: {str(e)}")
            return {}
            
    async def analyze_metrics(self, metrics: Dict[str, Any]):
        """Analyze collected metrics for anomalies"""
        try:
            alerts = []
            
            # Check CPU usage
            if metrics["system"]["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
                alerts.append({
                    "type": "high_cpu_usage",
                    "value": metrics["system"]["cpu_percent"],
                    "threshold": self.alert_thresholds["cpu_percent"],
                    "timestamp": metrics["timestamp"]
                })
                
            # Check memory usage
            if metrics["system"]["memory_percent"] > self.alert_thresholds["memory_percent"]:
                alerts.append({
                    "type": "high_memory_usage",
                    "value": metrics["system"]["memory_percent"],
                    "threshold": self.alert_thresholds["memory_percent"],
                    "timestamp": metrics["timestamp"]
                })
                
            # Check disk usage
            if metrics["system"]["disk_percent"] > self.alert_thresholds["disk_percent"]:
                alerts.append({
                    "type": "high_disk_usage",
                    "value": metrics["system"]["disk_percent"],
                    "threshold": self.alert_thresholds["disk_percent"],
                    "timestamp": metrics["timestamp"]
                })
                
            # Store alerts if any
            if alerts:
                await self.store_alerts(alerts)
                
        except Exception as e:
            logger.error(f"Error analyzing metrics: {str(e)}")
            
    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis"""
        try:
            # Store current metrics
            key = f"performance_metrics:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.set(key, metrics, expire=7 * 24 * 60 * 60)  # 7 days TTL
            
            # Store in historical data
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:  # Keep last 1000 metrics
                self.metrics_history = self.metrics_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")
            
    async def store_alerts(self, alerts: List[Dict[str, Any]]):
        """Store performance alerts"""
        try:
            key = f"performance_alerts:{datetime.utcnow().strftime('%Y%m%d')}"
            await redis_client.set(key, alerts, expire=30 * 24 * 60 * 60)  # 30 days TTL
        except Exception as e:
            logger.error(f"Error storing alerts: {str(e)}")
            
    async def get_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        try:
            report = {
                "current_metrics": await self.collect_metrics(),
                "historical_data": self.metrics_history[-days * 24 * 60:],  # Last N days
                "memory_analysis": self.memory_analyzer.generate_memory_report(),
                "recommendations": self.memory_analyzer.get_memory_recommendations(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return {}
            
    async def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        try:
            trends = {
                "cpu_trend": [],
                "memory_trend": [],
                "disk_trend": [],
                "response_time_trend": []
            }
            
            # Get historical data
            historical_data = self.metrics_history[-days * 24 * 60:]
            
            # Calculate trends
            for metric in historical_data:
                trends["cpu_trend"].append({
                    "timestamp": metric["timestamp"],
                    "value": metric["system"]["cpu_percent"]
                })
                trends["memory_trend"].append({
                    "timestamp": metric["timestamp"],
                    "value": metric["system"]["memory_percent"]
                })
                trends["disk_trend"].append({
                    "timestamp": metric["timestamp"],
                    "value": metric["system"]["disk_percent"]
                })
                
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {} 