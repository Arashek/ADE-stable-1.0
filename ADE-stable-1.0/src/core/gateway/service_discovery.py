from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
import random
import yaml
from pathlib import Path
import hashlib
import statistics
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    CIRCUIT_OPEN = "circuit_open"

class LoadBalanceStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    WEIGHTED = "weighted"
    CONSISTENT_HASH = "consistent_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    LEAST_ERROR_RATE = "least_error_rate"

@dataclass
class ServiceMetrics:
    """Service instance metrics."""
    response_times: deque = deque(maxlen=100)
    error_count: int = 0
    success_count: int = 0
    last_error_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    circuit_state: str = "CLOSED"
    circuit_failures: int = 0
    circuit_last_failure: Optional[datetime] = None
    circuit_last_success: Optional[datetime] = None

@dataclass
class ServiceInstance:
    """Service instance information."""
    id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    metadata: Dict[str, Any]
    last_heartbeat: datetime
    weight: float = 1.0
    connections: int = 0
    metrics: ServiceMetrics = ServiceMetrics()

@dataclass
class ServiceRegistration:
    """Service registration information."""
    name: str
    version: str
    instances: Dict[str, ServiceInstance]
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: float = 5.0
    retry_count: int = 3
    metadata: Dict[str, Any] = None

class ServiceDiscovery:
    """Service discovery and load balancing implementation."""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.services: Dict[str, ServiceRegistration] = {}
        self.instance_connections: Dict[str, Set[str]] = {}
        self.load_balance_strategy = LoadBalanceStrategy.ROUND_ROBIN
        self.instance_weights: Dict[str, float] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Load configurations
        self._load_services()
        
        # Start health check task
        self._start_health_check()
        
    def register_service(
        self,
        name: str,
        version: str,
        host: str,
        port: int,
        metadata: Dict[str, Any] = None
    ) -> ServiceInstance:
        """Register new service instance."""
        instance_id = self._generate_instance_id(name, host, port)
        
        instance = ServiceInstance(
            id=instance_id,
            service_name=name,
            host=host,
            port=port,
            status=ServiceStatus.STARTING,
            metadata=metadata or {},
            last_heartbeat=datetime.now(),
            weight=metadata.get("weight", 1.0) if metadata else 1.0
        )
        
        if name not in self.services:
            self.services[name] = ServiceRegistration(
                name=name,
                version=version,
                instances={},
                metadata={"registered_at": datetime.now().isoformat()}
            )
            
        self.services[name].instances[instance_id] = instance
        self.instance_connections[instance_id] = set()
        
        # Save updated configuration
        self._save_services()
        
        return instance
        
    def deregister_service(self, instance_id: str) -> None:
        """Deregister service instance."""
        for service in self.services.values():
            if instance_id in service.instances:
                instance = service.instances[instance_id]
                instance.status = ServiceStatus.STOPPING
                
                # Wait for active connections to close
                if instance_id in self.instance_connections:
                    while self.instance_connections[instance_id]:
                        asyncio.sleep(1)
                        
                del service.instances[instance_id]
                del self.instance_connections[instance_id]
                
                # Save updated configuration
                self._save_services()
                break
                
    def record_response_time(self, instance_id: str, response_time: float) -> None:
        """Record response time for instance."""
        for service in self.services.values():
            if instance_id in service.instances:
                service.instances[instance_id].metrics.response_times.append(response_time)
                break
                
    def record_error(self, instance_id: str) -> None:
        """Record error for instance."""
        for service in self.services.values():
            if instance_id in service.instances:
                instance = service.instances[instance_id]
                instance.metrics.error_count += 1
                instance.metrics.last_error_time = datetime.now()
                break
                
    def record_success(self, instance_id: str) -> None:
        """Record success for instance."""
        for service in self.services.values():
            if instance_id in service.instances:
                instance = service.instances[instance_id]
                instance.metrics.success_count += 1
                instance.metrics.last_success_time = datetime.now()
                break
                
    def get_service_instance(
        self,
        service_name: str,
        strategy: Optional[LoadBalanceStrategy] = None,
        request_key: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Get service instance using load balancing strategy."""
        service = self.services.get(service_name)
        if not service:
            return None
            
        # Get healthy instances
        healthy_instances = [
            instance for instance in service.instances.values()
            if instance.status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_instances:
            return None
            
        # Use specified strategy or default
        strategy = strategy or self.load_balance_strategy
        
        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin(healthy_instances)
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_instances)
        elif strategy == LoadBalanceStrategy.RANDOM:
            return self._random(healthy_instances)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            return self._weighted(healthy_instances)
        elif strategy == LoadBalanceStrategy.CONSISTENT_HASH:
            return self._consistent_hash(healthy_instances, request_key)
        elif strategy == LoadBalanceStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time(healthy_instances)
        elif strategy == LoadBalanceStrategy.LEAST_ERROR_RATE:
            return self._least_error_rate(healthy_instances)
            
        return None
        
    def record_connection(self, instance_id: str, connection_id: str) -> None:
        """Record new connection to instance."""
        if instance_id in self.instance_connections:
            self.instance_connections[instance_id].add(connection_id)
            
            # Update instance connection count
            for service in self.services.values():
                if instance_id in service.instances:
                    service.instances[instance_id].connections += 1
                    break
                    
    def remove_connection(self, instance_id: str, connection_id: str) -> None:
        """Remove connection from instance."""
        if instance_id in self.instance_connections:
            self.instance_connections[instance_id].discard(connection_id)
            
            # Update instance connection count
            for service in self.services.values():
                if instance_id in service.instances:
                    service.instances[instance_id].connections -= 1
                    break
                    
    async def check_service_health(self, instance: ServiceInstance) -> bool:
        """Check service instance health."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{instance.host}:{instance.port}/health"
                async with session.get(url, timeout=5.0) as response:
                    if response.status == 200:
                        instance.status = ServiceStatus.HEALTHY
                        instance.last_heartbeat = datetime.now()
                        return True
                    else:
                        instance.status = ServiceStatus.UNHEALTHY
                        return False
        except Exception as e:
            logger.error(f"Health check failed for {instance.id}: {str(e)}")
            instance.status = ServiceStatus.UNHEALTHY
            return False
            
    async def _health_check_task(self) -> None:
        """Background health check task."""
        while True:
            for service in self.services.values():
                for instance in service.instances.values():
                    await self.check_service_health(instance)
            await asyncio.sleep(30)
            
    def _start_health_check(self) -> None:
        """Start health check task."""
        asyncio.create_task(self._health_check_task())
        
    def _round_robin(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin load balancing."""
        if not instances:
            return None
            
        # Get instance with oldest last used time
        return min(
            instances,
            key=lambda x: x.last_heartbeat
        )
        
    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections load balancing."""
        if not instances:
            return None
            
        return min(
            instances,
            key=lambda x: x.connections
        )
        
    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random load balancing."""
        if not instances:
            return None
            
        return random.choice(instances)
        
    def _weighted(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Weighted load balancing."""
        if not instances:
            return None
            
        # Calculate total weight
        total_weight = sum(instance.weight for instance in instances)
        
        # Generate random value
        r = random.uniform(0, total_weight)
        
        # Select instance based on weight
        current_sum = 0
        for instance in instances:
            current_sum += instance.weight
            if r <= current_sum:
                return instance
                
        return instances[-1]
        
    def _consistent_hash(
        self,
        instances: List[ServiceInstance],
        request_key: str
    ) -> ServiceInstance:
        """Consistent hashing load balancing."""
        if not instances or not request_key:
            return None
            
        # Create hash ring
        hash_ring = []
        for instance in instances:
            # Create multiple virtual nodes for better distribution
            for i in range(100):
                node_key = f"{instance.id}:{i}"
                hash_value = int(hashlib.md5(node_key.encode()).hexdigest(), 16)
                hash_ring.append((hash_value, instance))
                
        # Sort hash ring
        hash_ring.sort(key=lambda x: x[0])
        
        # Hash request key
        request_hash = int(hashlib.md5(request_key.encode()).hexdigest(), 16)
        
        # Find first node with hash >= request hash
        for hash_value, instance in hash_ring:
            if hash_value >= request_hash:
                return instance
                
        # If no node found, return first node
        return hash_ring[0][1]
        
    def _least_response_time(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least response time load balancing."""
        if not instances:
            return None
            
        # Calculate average response time for each instance
        instance_times = []
        for instance in instances:
            if instance.metrics.response_times:
                avg_time = statistics.mean(instance.metrics.response_times)
                instance_times.append((avg_time, instance))
                
        if not instance_times:
            return random.choice(instances)
            
        # Return instance with lowest average response time
        return min(instance_times, key=lambda x: x[0])[1]
        
    def _least_error_rate(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least error rate load balancing."""
        if not instances:
            return None
            
        # Calculate error rate for each instance
        instance_rates = []
        for instance in instances:
            total_requests = instance.metrics.error_count + instance.metrics.success_count
            if total_requests > 0:
                error_rate = instance.metrics.error_count / total_requests
                instance_rates.append((error_rate, instance))
                
        if not instance_rates:
            return random.choice(instances)
            
        # Return instance with lowest error rate
        return min(instance_rates, key=lambda x: x[0])[1]
        
    def _generate_instance_id(
        self,
        service_name: str,
        host: str,
        port: int
    ) -> str:
        """Generate unique instance ID."""
        data = f"{service_name}:{host}:{port}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]
        
    def _load_services(self) -> None:
        """Load service configurations from file."""
        services_file = self.config_dir / "services.yaml"
        if not services_file.exists():
            return
            
        try:
            with open(services_file) as f:
                data = yaml.safe_load(f)
                for service_data in data:
                    instances = {}
                    for instance_data in service_data["instances"]:
                        instance = ServiceInstance(
                            id=instance_data["id"],
                            service_name=service_data["name"],
                            host=instance_data["host"],
                            port=instance_data["port"],
                            status=ServiceStatus(instance_data["status"]),
                            metadata=instance_data.get("metadata", {}),
                            last_heartbeat=datetime.fromisoformat(instance_data["last_heartbeat"]),
                            weight=instance_data.get("weight", 1.0),
                            connections=instance_data.get("connections", 0)
                        )
                        instances[instance.id] = instance
                        
                    service = ServiceRegistration(
                        name=service_data["name"],
                        version=service_data["version"],
                        instances=instances,
                        health_check_path=service_data.get("health_check_path", "/health"),
                        health_check_interval=service_data.get("health_check_interval", 30),
                        health_check_timeout=service_data.get("health_check_timeout", 5.0),
                        retry_count=service_data.get("retry_count", 3),
                        metadata=service_data.get("metadata", {})
                    )
                    self.services[service.name] = service
                    
        except Exception as e:
            logger.error(f"Failed to load services: {str(e)}")
            
    def _save_services(self) -> None:
        """Save service configurations to file."""
        services_file = self.config_dir / "services.yaml"
        with open(services_file, "w") as f:
            yaml.dump([
                {
                    "name": service.name,
                    "version": service.version,
                    "instances": [
                        {
                            "id": instance.id,
                            "host": instance.host,
                            "port": instance.port,
                            "status": instance.status.value,
                            "metadata": instance.metadata,
                            "last_heartbeat": instance.last_heartbeat.isoformat(),
                            "weight": instance.weight,
                            "connections": instance.connections
                        }
                        for instance in service.instances.values()
                    ],
                    "health_check_path": service.health_check_path,
                    "health_check_interval": service.health_check_interval,
                    "health_check_timeout": service.health_check_timeout,
                    "retry_count": service.retry_count,
                    "metadata": service.metadata
                }
                for service in self.services.values()
            ], f)

    def get_instance_metrics(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for service instance."""
        for service in self.services.values():
            if instance_id in service.instances:
                instance = service.instances[instance_id]
                return {
                    "id": instance.id,
                    "status": instance.status.value,
                    "connections": instance.connections,
                    "response_times": list(instance.metrics.response_times),
                    "error_count": instance.metrics.error_count,
                    "success_count": instance.metrics.success_count,
                    "error_rate": (
                        instance.metrics.error_count /
                        (instance.metrics.error_count + instance.metrics.success_count)
                        if (instance.metrics.error_count + instance.metrics.success_count) > 0
                        else 0
                    ),
                    "last_error_time": instance.metrics.last_error_time.isoformat()
                        if instance.metrics.last_error_time else None,
                    "last_success_time": instance.metrics.last_success_time.isoformat()
                        if instance.metrics.last_success_time else None,
                    "circuit_state": instance.metrics.circuit_state,
                    "circuit_failures": instance.metrics.circuit_failures
                }
        return None 