from typing import Dict, Any, List
import aiohttp
import asyncio
from datetime import datetime
from .models import AnalyticsData
from ...config.logging_config import logger

class DataCollector:
    """Collector for gathering anonymous data from ADE instances"""
    
    def __init__(self):
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.collection_interval = 3600  # 1 hour
        
    async def collect_anonymous_data(self) -> List[AnalyticsData]:
        """Collect anonymous data from all active instances"""
        try:
            data = []
            
            # Get active instances
            active_instances = await self._get_active_instances()
            
            # Collect data from each instance
            tasks = []
            for instance_id in active_instances:
                task = self._collect_instance_data(instance_id)
                tasks.append(task)
                
            # Wait for all collections to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, AnalyticsData):
                    data.append(result)
                    
            return data
            
        except Exception as e:
            logger.error(f"Error collecting anonymous data: {str(e)}")
            return []
            
    async def _get_active_instances(self) -> List[str]:
        """Get list of active ADE instances"""
        try:
            # In production, this would query a database or service registry
            # For now, return mock data
            return [
                "instance_1",
                "instance_2",
                "instance_3"
            ]
            
        except Exception as e:
            logger.error(f"Error getting active instances: {str(e)}")
            return []
            
    async def _collect_instance_data(self, instance_id: str) -> AnalyticsData:
        """Collect data from a specific instance"""
        try:
            # In production, this would make API calls to the instance
            # For now, generate mock data
            metrics = {
                "cpu_usage": 0.5,
                "memory_usage": 0.6,
                "response_time": 0.1,
                "error_rate": 0.01
            }
            
            events = [
                {
                    "type": "api_call",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"endpoint": "/api/v1/endpoint"}
                },
                {
                    "type": "error",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"error_type": "validation_error"}
                }
            ]
            
            metadata = {
                "type": "production",
                "region": "us-west-2",
                "version": "1.0.0"
            }
            
            return AnalyticsData(
                instance_id=instance_id,
                timestamp=datetime.now(),
                metrics=metrics,
                events=events,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error collecting instance data: {str(e)}")
            return None
            
    async def register_instance(self, instance_id: str, metadata: Dict[str, Any]):
        """Register a new ADE instance"""
        try:
            self.instances[instance_id] = {
                "metadata": metadata,
                "registered_at": datetime.now(),
                "last_seen": datetime.now()
            }
            
            logger.info(f"Registered new instance: {instance_id}")
            
        except Exception as e:
            logger.error(f"Error registering instance: {str(e)}")
            
    async def unregister_instance(self, instance_id: str):
        """Unregister an ADE instance"""
        try:
            if instance_id in self.instances:
                del self.instances[instance_id]
                logger.info(f"Unregistered instance: {instance_id}")
                
        except Exception as e:
            logger.error(f"Error unregistering instance: {str(e)}")
            
    async def update_instance_metadata(self, instance_id: str, metadata: Dict[str, Any]):
        """Update metadata for an instance"""
        try:
            if instance_id in self.instances:
                self.instances[instance_id]["metadata"].update(metadata)
                self.instances[instance_id]["last_seen"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error updating instance metadata: {str(e)}")
            
    async def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get status information for an instance"""
        try:
            if instance_id not in self.instances:
                return None
                
            instance = self.instances[instance_id]
            last_seen = instance["last_seen"]
            now = datetime.now()
            
            # Calculate uptime
            uptime = (now - instance["registered_at"]).total_seconds()
            
            # Check if instance is active
            is_active = (now - last_seen).total_seconds() < self.collection_interval * 2
            
            return {
                "instance_id": instance_id,
                "metadata": instance["metadata"],
                "registered_at": instance["registered_at"].isoformat(),
                "last_seen": last_seen.isoformat(),
                "uptime": uptime,
                "is_active": is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting instance status: {str(e)}")
            return None
            
    async def get_all_instances_status(self) -> List[Dict[str, Any]]:
        """Get status information for all instances"""
        try:
            status_list = []
            
            for instance_id in self.instances:
                status = await self.get_instance_status(instance_id)
                if status:
                    status_list.append(status)
                    
            return status_list
            
        except Exception as e:
            logger.error(f"Error getting all instances status: {str(e)}")
            return [] 