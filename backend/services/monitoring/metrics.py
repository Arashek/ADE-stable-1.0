"""
Metrics collection module for the ADE platform.
Collects and exposes metrics for Prometheus to scrape.
"""
import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, multiprocess, CollectorRegistry, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST

# Agent metrics
agent_tasks_total = Counter(
    'agent_tasks_total', 
    'Total number of tasks processed by each agent',
    ['agent_type', 'task_type']
)

agent_task_duration_seconds = Histogram(
    'agent_task_duration_seconds', 
    'Time spent processing tasks by each agent',
    ['agent_type', 'task_type'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
)

agent_task_success_rate = Gauge(
    'agent_task_success_rate', 
    'Success rate of tasks processed by each agent',
    ['agent_type']
)

# Collaboration metrics
collaboration_pattern_executions_total = Counter(
    'collaboration_pattern_executions_total', 
    'Total number of collaboration pattern executions',
    ['pattern']
)

collaboration_pattern_duration_seconds = Histogram(
    'collaboration_pattern_duration_seconds', 
    'Time spent executing collaboration patterns',
    ['pattern'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
)

# Consensus metrics
consensus_decisions_total = Counter(
    'consensus_decisions_total', 
    'Total number of consensus decisions',
    ['status']
)

consensus_decision_duration_seconds = Histogram(
    'consensus_decision_duration_seconds', 
    'Time spent making consensus decisions',
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Conflict resolution metrics
conflict_resolutions_total = Counter(
    'conflict_resolutions_total', 
    'Total number of conflict resolutions',
    ['resolution_strategy']
)

conflict_resolution_duration_seconds = Histogram(
    'conflict_resolution_duration_seconds', 
    'Time spent resolving conflicts',
    ['resolution_strategy'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# API metrics
api_requests_total = Counter(
    'api_requests_total', 
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds', 
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Resource metrics
memory_usage_bytes = Gauge(
    'memory_usage_bytes', 
    'Memory usage in bytes',
    ['service']
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent', 
    'CPU usage percentage',
    ['service']
)

# Utility decorators for metrics collection
def track_agent_task(agent_type, task_type):
    """Decorator to track agent task execution time and count."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                agent_tasks_total.labels(agent_type=agent_type, task_type=task_type).inc()
                # Update success rate (simplified approach)
                agent_task_success_rate.labels(agent_type=agent_type).set(1.0)
                return result
            except Exception as e:
                # Update success rate on failure
                agent_task_success_rate.labels(agent_type=agent_type).set(0.0)
                raise e
            finally:
                duration = time.time() - start_time
                agent_task_duration_seconds.labels(
                    agent_type=agent_type, task_type=task_type
                ).observe(duration)
        return wrapper
    return decorator

def track_collaboration_pattern(pattern):
    """Decorator to track collaboration pattern execution time and count."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                collaboration_pattern_executions_total.labels(pattern=pattern).inc()
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                collaboration_pattern_duration_seconds.labels(pattern=pattern).observe(duration)
        return wrapper
    return decorator

def track_consensus_decision():
    """Decorator to track consensus decision time."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                status = "success" if result else "failure"
                consensus_decisions_total.labels(status=status).inc()
                return result
            finally:
                duration = time.time() - start_time
                consensus_decision_duration_seconds.observe(duration)
        return wrapper
    return decorator

def track_conflict_resolution(resolution_strategy):
    """Decorator to track conflict resolution time and count."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                conflict_resolutions_total.labels(resolution_strategy=resolution_strategy).inc()
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                conflict_resolution_duration_seconds.labels(
                    resolution_strategy=resolution_strategy
                ).observe(duration)
        return wrapper
    return decorator

def track_api_request(endpoint):
    """Decorator to track API request time and count."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                status_code = result.status_code if hasattr(result, 'status_code') else 200
                api_requests_total.labels(
                    method=kwargs.get('request').method if 'request' in kwargs else 'UNKNOWN',
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                return result
            except Exception as e:
                api_requests_total.labels(
                    method=kwargs.get('request').method if 'request' in kwargs else 'UNKNOWN',
                    endpoint=endpoint,
                    status_code=500
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                api_request_duration_seconds.labels(
                    method=kwargs.get('request').method if 'request' in kwargs else 'UNKNOWN',
                    endpoint=endpoint
                ).observe(duration)
        return wrapper
    return decorator

# FastAPI middleware for metrics collection
async def metrics_middleware(request, call_next):
    """Middleware to collect API metrics."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    api_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    api_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Metrics endpoint for Prometheus to scrape
def metrics_endpoint():
    """Generate metrics for Prometheus."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return data, CONTENT_TYPE_LATEST

# Resource usage tracking
def update_resource_metrics(memory_usage, cpu_usage, service_name="backend"):
    """Update resource usage metrics."""
    memory_usage_bytes.labels(service=service_name).set(memory_usage)
    cpu_usage_percent.labels(service=service_name).set(cpu_usage)
