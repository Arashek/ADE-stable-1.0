from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "CloudEV.ai"
    APP_URL: str = os.getenv("APP_URL", "https://cloudev.ai")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "cloudev")
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@cloudev.ai")
    FROM_NAME: str = os.getenv("FROM_NAME", "CloudEV.ai Team")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 24 * 60 * 60  # 24 hours
    
    # Early access settings
    MAX_WAITLIST_SIZE: int = int(os.getenv("MAX_WAITLIST_SIZE", "1000"))
    INVITATION_CODE_LENGTH: int = 8
    INVITATION_CODE_EXPIRY_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # 1 hour
    
    # Feature flags
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "True").lower() == "true"
    ENABLE_WAITLIST: bool = os.getenv("ENABLE_WAITLIST", "True").lower() == "true"
    ENABLE_INVITATION_CODES: bool = os.getenv("ENABLE_INVITATION_CODES", "True").lower() == "true"
    
    # Social media links
    TWITTER_URL: Optional[str] = os.getenv("TWITTER_URL")
    DISCORD_URL: Optional[str] = os.getenv("DISCORD_URL")
    GITHUB_URL: Optional[str] = os.getenv("GITHUB_URL")
    
    # Support settings
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@cloudev.ai")
    SUPPORT_URL: str = os.getenv("SUPPORT_URL", "https://support.cloudev.ai")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create a global instance
settings = Settings() 