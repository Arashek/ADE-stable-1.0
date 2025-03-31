from typing import Dict, Optional
from pydantic import BaseModel

class ModelConfig(BaseModel):
    """
    Configuration for the model service
    """
    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    
    # Model endpoints
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Default models
    default_model: str = "gpt-4"
    code_generation_model: str = "gpt-4"
    analysis_model: str = "gpt-4"
    explanation_model: str = "gpt-3.5-turbo"
    
    # Model parameters
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    # Cache configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # 1 minute
    
    # Monitoring
    telemetry_enabled: bool = True
    prometheus_enabled: bool = True
    
    # Security
    allowed_origins: list = ["*"]
    api_key_required: bool = True
    
    class Config:
        env_prefix = "MODEL_"
        case_sensitive = False
