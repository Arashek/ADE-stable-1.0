import time
import logging
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any, Callable
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client.exposition import start_http_server
from prometheus_client.metrics_core import Metric
import structlog
from structlog.contextvars import bound_contextvars

# Context variables for correlation tracking
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
request_id: ContextVar[str] = ContextVar("request_id", default="")
user_id: ContextVar[str] = ContextVar("user_id", default="")

# Prometheus metrics
# API metrics
api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint", "status_code"]
)

api_request_count = Counter(
    "api_request_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"]
)

# Provider metrics
provider_request_duration = Histogram(
    "provider_request_duration_seconds",
    "Provider API request duration in seconds",
    ["provider", "capability", "status"]
)

provider_request_count = Counter(
    "provider_request_total",
    "Total number of provider API requests",
    ["provider", "capability", "status"]
)

provider_cost = Counter(
    "provider_cost_total",
    "Total cost of provider API calls",
    ["provider", "capability"]
)

# Task metrics
task_execution_duration = Histogram(
    "task_execution_duration_seconds",
    "Task execution duration in seconds",
    ["task_type", "status"]
)

task_count = Counter(
    "task_total",
    "Total number of tasks",
    ["task_type", "status"]
)

# System metrics
active_tasks = Gauge(
    "active_tasks",
    "Number of currently active tasks",
    ["task_type"]
)

memory_usage = Gauge(
    "memory_usage_bytes",
    "Current memory usage in bytes"
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

class MonitoringManager:
    """Manages monitoring and metrics collection"""
    
    def __init__(
        self,
        prometheus_port: int = 9090,
        enable_metrics: bool = True,
        enable_logging: bool = True
    ):
        """
        Initialize the monitoring manager
        
        Args:
            prometheus_port: Port for Prometheus metrics server
            enable_metrics: Whether to enable Prometheus metrics
            enable_logging: Whether to enable structured logging
        """
        self.enable_metrics = enable_metrics
        self.enable_logging = enable_logging
        
        if enable_metrics:
            start_http_server(prometheus_port)
            logger.info("Prometheus metrics server started", port=prometheus_port)
    
    def get_correlation_context(self) -> Dict[str, str]:
        """Get the current correlation context"""
        return {
            "correlation_id": correlation_id.get(),
            "request_id": request_id.get(),
            "user_id": user_id.get()
        }
    
    def set_correlation_context(
        self,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Set the correlation context"""
        if correlation_id:
            self.correlation_id.set(correlation_id)
        if request_id:
            self.request_id.set(request_id)
        if user_id:
            self.user_id.set(user_id)
    
    def clear_correlation_context(self) -> None:
        """Clear the correlation context"""
        correlation_id.set("")
        request_id.set("")
        user_id.set("")
    
    def track_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ) -> None:
        """Track API request metrics"""
        if not self.enable_metrics:
            return
            
        api_request_duration.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).observe(duration)
        
        api_request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
    
    def track_provider_request(
        self,
        provider: str,
        capability: str,
        status: str,
        duration: float,
        cost: float
    ) -> None:
        """Track provider request metrics"""
        if not self.enable_metrics:
            return
            
        provider_request_duration.labels(
            provider=provider,
            capability=capability,
            status=status
        ).observe(duration)
        
        provider_request_count.labels(
            provider=provider,
            capability=capability,
            status=status
        ).inc()
        
        provider_cost.labels(
            provider=provider,
            capability=capability
        ).inc(cost)
    
    def track_task_execution(
        self,
        task_type: str,
        status: str,
        duration: float
    ) -> None:
        """Track task execution metrics"""
        if not self.enable_metrics:
            return
            
        task_execution_duration.labels(
            task_type=task_type,
            status=status
        ).observe(duration)
        
        task_count.labels(
            task_type=task_type,
            status=status
        ).inc()
    
    def update_active_tasks(self, task_type: str, count: int) -> None:
        """Update the number of active tasks"""
        if not self.enable_metrics:
            return
            
        active_tasks.labels(task_type=task_type).set(count)
    
    def update_memory_usage(self, usage_bytes: int) -> None:
        """Update memory usage metric"""
        if not self.enable_metrics:
            return
            
        memory_usage.set(usage_bytes)
    
    def log_event(
        self,
        event: str,
        level: str = "info",
        **kwargs
    ) -> None:
        """Log an event with correlation context"""
        if not self.enable_logging:
            return
            
        context = self.get_correlation_context()
        log_method = getattr(logger, level.lower())
        log_method(event, **{**context, **kwargs})

def monitor_api_request(
    method: str,
    endpoint: str,
    status_code: int
) -> Callable:
    """Decorator for monitoring API requests"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitoring_manager.track_api_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitoring_manager.track_api_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=500,
                    duration=duration
                )
                raise
        return wrapper
    return decorator

def monitor_provider_request(
    provider: str,
    capability: str
) -> Callable:
    """Decorator for monitoring provider requests"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitoring_manager.track_provider_request(
                    provider=provider,
                    capability=capability,
                    status="success",
                    duration=duration,
                    cost=result.get("cost", 0.0)
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitoring_manager.track_provider_request(
                    provider=provider,
                    capability=capability,
                    status="error",
                    duration=duration,
                    cost=0.0
                )
                raise
        return wrapper
    return decorator

def monitor_task_execution(
    task_type: str
) -> Callable:
    """Decorator for monitoring task execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            monitoring_manager.update_active_tasks(task_type, 1)
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitoring_manager.track_task_execution(
                    task_type=task_type,
                    status="success",
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitoring_manager.track_task_execution(
                    task_type=task_type,
                    status="error",
                    duration=duration
                )
                raise
            finally:
                monitoring_manager.update_active_tasks(task_type, 0)
        return wrapper
    return decorator

# Create a global instance of the monitoring manager
monitoring_manager = MonitoringManager()

# Example usage:
"""
from utils.monitoring import (
    monitoring_manager,
    monitor_api_request,
    monitor_provider_request,
    monitor_task_execution
)

# API endpoint with monitoring
@monitor_api_request(method="POST", endpoint="/api/v1/plans", status_code=201)
async def create_plan(plan_data: dict):
    # Set correlation context
    monitoring_manager.set_correlation_context(
        correlation_id=str(uuid.uuid4()),
        request_id=str(uuid.uuid4())
    )
    
    try:
        # Create plan logic
        plan = await plan_service.create(plan_data)
        
        # Log success
        monitoring_manager.log_event(
            "plan_created",
            plan_id=plan.id,
            title=plan.title
        )
        
        return plan
    finally:
        monitoring_manager.clear_correlation_context()

# Provider request with monitoring
@monitor_provider_request(provider="openai", capability="text_generation")
async def generate_text(prompt: str):
    # Provider request logic
    pass

# Task execution with monitoring
@monitor_task_execution(task_type="plan_execution")
async def execute_plan(plan_id: str):
    # Task execution logic
    pass
""" 