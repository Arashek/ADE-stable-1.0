from typing import Dict, List, Optional, Union, Any
from pydantic import BaseSettings, validator, AnyHttpUrl
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "ADE Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # API settings
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api"  # Added to align with main.py reference
    PROJECT_NAME: str = "ADE Platform API"
    
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
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Cache settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_PREFIX: str = "ade_platform"

    # External service settings
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY", None)
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET", None)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    AWS_REGION: Optional[str] = os.getenv("AWS_REGION", None)
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET", None)

    # Monitoring settings
    ENABLE_METRICS = False
    PROMETHEUS_MULTIPROC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prometheus_multiproc")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN", None)
    NEW_RELIC_LICENSE_KEY: Optional[str] = os.getenv("NEW_RELIC_LICENSE_KEY", None)

    # Rate limiting settings
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000

    # Notification settings
    MAX_NOTIFICATIONS_PER_USER: int = 1000
    NOTIFICATION_RETENTION_DAYS: int = 30

    # Memory infrastructure settings
    MEMORY_ENABLED: bool = False  # Disabled for initial local testing
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "ade_memory")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    VECTOR_SIMILARITY_THRESHOLD: float = 0.7
    KNOWLEDGE_GRAPH_MAX_DEPTH: int = 3

    # Visual Perception MCP settings
    VISUAL_PERCEPTION_ENABLED: bool = True
    TESSERACT_CMD_PATH: str = os.getenv("TESSERACT_CMD_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    VISUAL_PERCEPTION_CAPTURE_INTERVAL: int = 5000  # milliseconds
    VISUAL_PERCEPTION_AUTO_CAPTURE: bool = False
    VISUAL_PERCEPTION_STORAGE_ENABLED: bool = True
    VISUAL_PERCEPTION_STORAGE_PATH: Path = Path("storage/visual_perception")
    VISUAL_PERCEPTION_MAX_STORED_IMAGES: int = 100

    def get_log_file_path(self) -> str:
        """Get the log file path, creating directories if needed"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        return str(log_dir / "app.log")
        
    def get_cors_origins(self) -> List[str]:
        """Get the list of allowed CORS origins"""
        return self.BACKEND_CORS_ORIGINS

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("UPLOAD_DIR")
    def create_upload_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("LOG_FILE")
    def create_log_dir(cls, v: str) -> str:
        log_dir = Path(v).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        return v

    @validator("SQLALCHEMY_DATABASE_URI", "DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        postgres_server = values.get("POSTGRES_SERVER")
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_db = values.get("POSTGRES_DB")
        
        # Construct PostgreSQL connection string
        return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_server}/{postgres_db}"

    @validator("VISUAL_PERCEPTION_STORAGE_PATH")
    def create_visual_perception_storage_dir(cls, v: Path) -> Path:
        if os.getenv("VISUAL_PERCEPTION_STORAGE_ENABLED", "True").lower() == "true":
            v.mkdir(parents=True, exist_ok=True)
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

# Create global settings instance
settings = Settings()