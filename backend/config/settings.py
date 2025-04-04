from typing import List, Optional, Union, Dict, Any
# Correct Pydantic V2 imports
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, EmailStr, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
# load_dotenv() # Rely on Pydantic's built-in .env loading via SettingsConfigDict

class Settings(BaseSettings):
    # Explicitly ignore extra environment variables and load from .env
    model_config = SettingsConfigDict(
        extra='ignore', 
        case_sensitive=True, 
        env_file=".env", # Re-enable Pydantic's .env loading
        env_file_encoding='utf-8'
        # No env_prefix means don't load from environment variables by default?
        # Let's be explicit: Pydantic v2 doesn't have a simple flag. 
        # Need to ensure individual fields don't match env vars if we want to avoid this.
        # Or, we can control loading order/priority if needed.
        # For now, let's keep env_file commented out and assume the issue was the env var.
        # We will proceed by re-enabling env_file loading carefully later.
    )

    # Application settings
    APP_NAME: str = "ADE Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API settings
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api"  # Added to align with main.py reference
    PROJECT_NAME: str = "ADE Platform API"
    HOST: str = os.getenv("HOST", "127.0.0.1") # Changed default HOST to localhost
    PORT: int = int(os.getenv("PORT", 8000)) # Added PORT setting for Uvicorn
    WORKERS: int = int(os.getenv("WORKERS", 1)) # Added WORKERS setting for Uvicorn
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true" # Added RELOAD setting for Uvicorn
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []
   
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ade_platform")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_URL: Optional[str] = None  # Used by owner_panel_db.py
   
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
   
    # File storage settings
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx", "txt"]
   
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Force standard format string, ignoring .env value for this specific setting during debug
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
   
    # Cache settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_URL: Optional[str] = None
   
    # Agent Configuration
    AGENT_POOL_SIZE: int = 5
    MAX_CONCURRENT_AGENTS: int = 10
    AGENT_HEARTBEAT_INTERVAL: int = 30  # seconds
    AGENT_TIMEOUT: int = 300  # seconds
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai" # e.g., openai, anthropic, google, groq
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Service-specific configurations
    MEMORY_ENABLED: bool = True
    MEMORY_DB_TYPE: str = "redis" # or "postgres", "filesystem"
    
    VISUAL_PERCEPTION_ENABLED: bool = True
    VISUAL_PERCEPTION_MODEL: str = "openai/clip-vit-large-patch14"
    VISUAL_PERCEPTION_STORAGE_PATH: Path = Path("data/visual_perception_storage")
    
    OWNER_PANEL_DB_URL: Optional[str] = os.getenv("OWNER_PANEL_DB_URL")

    @model_validator(mode='before')
    def assemble_db_connection(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("SQLALCHEMY_DATABASE_URI") or data.get("DATABASE_URL"):
                if data.get("SQLALCHEMY_DATABASE_URI") and not data.get("DATABASE_URL"):
                    data["DATABASE_URL"] = data["SQLALCHEMY_DATABASE_URI"]
                elif data.get("DATABASE_URL") and not data.get("SQLALCHEMY_DATABASE_URI"):
                    data["SQLALCHEMY_DATABASE_URI"] = data["DATABASE_URL"]
                return data
    
            postgres_server = data.get("POSTGRES_SERVER", "localhost")
            postgres_user = data.get("POSTGRES_USER", "postgres")
            postgres_password = data.get("POSTGRES_PASSWORD", "postgres")
            postgres_db = data.get("POSTGRES_DB", "ade_platform")
            
            db_uri = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_server}/{postgres_db}"
            data["SQLALCHEMY_DATABASE_URI"] = db_uri
            data["DATABASE_URL"] = db_uri 
            
        return data
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("UPLOAD_DIR", mode='before') 
    def create_upload_dir(cls, v: Union[str, Path]) -> Path:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @field_validator("VISUAL_PERCEPTION_STORAGE_PATH", mode='before') 
    def create_visual_perception_storage_dir(cls, v: Union[str, Path]) -> Path:
        path = Path(v)
        if os.getenv("VISUAL_PERCEPTION_STORAGE_ENABLED", "True").lower() == "true":
            path.mkdir(parents=True, exist_ok=True)
        return path

# Create global settings instance
settings = Settings()