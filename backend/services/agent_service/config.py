from typing import Dict, Optional
from pydantic import BaseModel

class AgentConfig(BaseModel):
    """
    Configuration for the agent service
    """
    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8081
    debug: bool = False
    
    # Agent pool configuration
    max_concurrent_tasks: int = 10
    task_timeout: int = 3600  # 1 hour
    
    # Model service configuration
    model_service_url: str = "http://model-service:8080"
    
    # Storage configuration
    storage_path: str = "/data/agents"
    
    # Monitoring
    telemetry_enabled: bool = True
    prometheus_enabled: bool = True
    
    # Security
    allowed_origins: list = ["*"]
    api_key_required: bool = True
    
    # Resource limits
    max_memory_mb: int = 4096
    max_cpu_cores: int = 2
    
    class Config:
        env_prefix = "AGENT_"
        case_sensitive = False
