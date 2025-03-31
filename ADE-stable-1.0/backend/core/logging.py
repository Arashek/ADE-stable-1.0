import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class LogManager:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.setup_logging()

    def ensure_log_directory(self):
        """Ensure the log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def setup_logging(self):
        """Configure logging with both file and console handlers"""
        # Create logger
        logger = logging.getLogger("ai_execution")
        logger.setLevel(logging.DEBUG)

        # Create handlers
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.log_dir, "ai_execution.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatters and add it to handlers
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = CustomFormatter()
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        self.logger = logger

    def log_execution(self, command: str, status: str, execution_time: float,
                     error: Optional[str] = None, client_ip: Optional[str] = None):
        """Log command execution details"""
        log_data = {
            'command': command,
            'status': status,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat(),
            'client_ip': client_ip
        }
        
        if error:
            log_data['error'] = error
            self.logger.error(f"Command execution failed: {log_data}")
        else:
            self.logger.info(f"Command executed successfully: {log_data}")

    def log_resource_usage(self, cpu_percent: float, memory_percent: float,
                          disk_percent: float):
        """Log system resource usage"""
        self.logger.debug(
            f"Resource usage - CPU: {cpu_percent}%, "
            f"Memory: {memory_percent}%, "
            f"Disk: {disk_percent}%"
        )

    def log_rate_limit(self, client_ip: str, remaining_requests: int):
        """Log rate limit information"""
        self.logger.info(
            f"Rate limit check - IP: {client_ip}, "
            f"Remaining requests: {remaining_requests}"
        )

    def log_security_event(self, event_type: str, details: dict):
        """Log security-related events"""
        self.logger.warning(f"Security event - {event_type}: {details}")

# Create a global instance
log_manager = LogManager() 