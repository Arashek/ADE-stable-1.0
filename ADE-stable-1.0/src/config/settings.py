from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    MONGODB_URI: str
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_DATABASE: str = "ade"
    
    # Redis
    REDIS_PASSWORD: str
    
    # Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Model Configuration
    DEFAULT_OPENAI_MODEL: str = "gpt-4"
    DEFAULT_ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    DEFAULT_GOOGLE_MODEL: str = "gemini-pro"
    DEFAULT_PROVIDER_TIER: str = "standard"
    OLLAMA_SERVER_URL: str = "http://localhost:11434"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp"
    
    # Security
    ENCRYPTION_KEY: str
    API_KEY_HEADER: str = "X-API-Key"
    
    # Application
    ENVIRONMENT: str = "development"
    ADE_PROJECT_DIR: str = "projects"
    API_RELOAD: bool = False
    
    # Usage Tracking
    USAGE_RETENTION_DAYS: int = 90
    USAGE_CLEANUP_INTERVAL: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 