"""
Monitoring services for the ADE platform.
Provides metrics collection and resource monitoring.

TEMPORARILY DISABLED FOR LOCAL TESTING:
This module now provides stub implementations of monitoring functions
to allow the core agent coordination system to run without Prometheus dependencies.
"""

# Stub implementations for monitoring functions
def track_agent_task(agent_type, task_type):
    """Stub implementation for agent task tracking"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_collaboration_pattern(pattern_type):
    """Stub implementation for collaboration pattern tracking"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_consensus_decision(decision_type="consensus"):
    """Stub implementation for consensus decision tracking"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_conflict_resolution(resolution_type):
    """Stub implementation for conflict resolution tracking"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def track_api_request():
    """Stub implementation for API request tracking"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def metrics_middleware(request, call_next):
    """Stub implementation for metrics middleware"""
    return await call_next(request)

def metrics_endpoint():
    """Stub implementation for metrics endpoint"""
    return "", "text/plain"

def update_resource_metrics(memory_usage, cpu_usage):
    """Stub implementation for resource metrics update"""
    pass

__all__ = [
    'track_agent_task',
    'track_collaboration_pattern',
    'track_consensus_decision',
    'track_conflict_resolution',
    'track_api_request',
    'metrics_middleware',
    'metrics_endpoint',
    'update_resource_metrics'
]
