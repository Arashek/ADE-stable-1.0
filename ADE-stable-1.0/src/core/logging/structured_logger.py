import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler

class StructuredFormatter(logging.Formatter):
    """Formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

class StructuredLogger:
    """Structured logging system with JSON formatting"""
    
    def __init__(
        self,
        name: str,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatters
        json_formatter = StructuredFormatter()
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)
        
        # Add console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(json_formatter)
            self.logger.addHandler(console_handler)
    
    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ) -> None:
        """Internal logging method"""
        if extra is None:
            extra = {}
            
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def info(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info message"""
        self._log(logging.INFO, message, extra)
    
    def warning(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, extra)
    
    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ) -> None:
        """Log error message"""
        self._log(logging.ERROR, message, extra, exc_info)
    
    def debug(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, extra)
    
    def critical(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ) -> None:
        """Log critical message"""
        self._log(logging.CRITICAL, message, extra, exc_info)
    
    def request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log HTTP request"""
        log_data = {
            "type": "http_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip
        }
        
        if extra:
            log_data.update(extra)
            
        self.info("HTTP Request", extra=log_data)
    
    def performance(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log performance metric"""
        log_data = {
            "type": "performance",
            "metric": metric_name,
            "value": value,
            "tags": tags or {}
        }
        
        if extra:
            log_data.update(extra)
            
        self.info("Performance Metric", extra=log_data)
    
    def security(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "info",
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security event"""
        log_data = {
            "type": "security",
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if extra:
            log_data.update(extra)
            
        if severity == "error":
            self.error("Security Event", extra=log_data)
        else:
            self.info("Security Event", extra=log_data) 