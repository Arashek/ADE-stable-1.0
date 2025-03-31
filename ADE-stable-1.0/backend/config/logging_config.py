import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ..config.settings import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure file handler
file_handler = RotatingFileHandler(
    filename=logs_dir / "app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(settings.LOG_LEVEL)

# Configure console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(settings.LOG_LEVEL)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Configure specific loggers
def setup_logger(name: str, level: str = None) -> logging.Logger:
    """Configure a specific logger with optional custom level"""
    logger = logging.getLogger(name)
    logger.setLevel(level or settings.LOG_LEVEL)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers for different components
auth_logger = setup_logger("auth")
api_logger = setup_logger("api")
db_logger = setup_logger("database")
cache_logger = setup_logger("cache")
security_logger = setup_logger("security")
notification_logger = setup_logger("notification")
marketplace_logger = setup_logger("marketplace")
deployment_logger = setup_logger("deployment")
monitoring_logger = setup_logger("monitoring")

# Configure third-party loggers
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("redis").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name"""
    return logging.getLogger(name) 