#!/usr/bin/env python
"""
Basic Error Logging System for ADE Platform

This script provides a simple file-based error logging system that can be used
across both backend and frontend components of the ADE platform.
"""

import os
import sys
import json
import logging
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("error_logging")

# Constants
ERROR_LOG_DIR = os.path.join(Path(__file__).resolve().parent.parent, "logs")
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, "error_logs.json")

# Ensure logs directory exists
os.makedirs(ERROR_LOG_DIR, exist_ok=True)

# Error categories and severity levels
class ErrorCategory:
    AGENT = "AGENT"
    API = "API"
    AUTH = "AUTH"
    DATABASE = "DATABASE"
    FRONTEND = "FRONTEND"
    IMPORT = "IMPORT"
    SYSTEM = "SYSTEM"
    COORDINATION = "COORDINATION"
    UNKNOWN = "UNKNOWN"

class ErrorSeverity:
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

def log_error(
    error: Union[Exception, str],
    category: str = ErrorCategory.UNKNOWN,
    severity: str = ErrorSeverity.ERROR,
    component: str = "backend",
    source: str = None,
    user_id: str = None,
    context: Dict[str, Any] = None
) -> str:
    """Log an error with metadata"""
    error_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    if isinstance(error, Exception):
        error_message = str(error)
        error_traceback = traceback.format_exc()
    else:
        error_message = error
        error_traceback = None
    
    error_log = {
        "id": error_id,
        "timestamp": timestamp,
        "category": category,
        "severity": severity,
        "component": component,
        "source": source,
        "user_id": user_id,
        "error_message": error_message,
        "error_traceback": error_traceback,
        "context": context or {}
    }
    
    # Log to console
    logger.error(f"Error [{category}][{severity}]: {error_message}")
    
    # Save to error log file
    try:
        # Read existing logs if file exists
        if os.path.exists(ERROR_LOG_FILE):
            try:
                with open(ERROR_LOG_FILE, "r") as f:
                    error_logs = json.load(f)
            except json.JSONDecodeError:
                error_logs = []
        else:
            error_logs = []
        
        # Add new error log
        error_logs.append(error_log)
        
        # Write updated logs
        with open(ERROR_LOG_FILE, "w") as f:
            json.dump(error_logs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save error log: {str(e)}")
    
    return error_id

def get_error_logs(
    limit: int = 100,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    component: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get error logs with optional filtering"""
    try:
        # Read error logs
        if os.path.exists(ERROR_LOG_FILE):
            try:
                with open(ERROR_LOG_FILE, "r") as f:
                    error_logs = json.load(f)
            except json.JSONDecodeError:
                error_logs = []
        else:
            error_logs = []
        
        # Apply filters
        filtered_logs = error_logs
        
        if category:
            filtered_logs = [log for log in filtered_logs if log.get("category") == category]
        
        if severity:
            filtered_logs = [log for log in filtered_logs if log.get("severity") == severity]
        
        if component:
            filtered_logs = [log for log in filtered_logs if log.get("component") == component]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        limited_logs = filtered_logs[:limit]
        
        return limited_logs
    except Exception as e:
        logger.error(f"Failed to get error logs: {str(e)}")
        return []

def clear_error_logs() -> bool:
    """Clear all error logs"""
    try:
        with open(ERROR_LOG_FILE, "w") as f:
            json.dump([], f)
        return True
    except Exception as e:
        logger.error(f"Failed to clear error logs: {str(e)}")
        return False

def generate_test_logs(count: int = 10):
    """Generate test error logs for development purposes"""
    import random
    
    categories = [
        ErrorCategory.AGENT,
        ErrorCategory.API,
        ErrorCategory.FRONTEND,
        ErrorCategory.SYSTEM,
        ErrorCategory.COORDINATION
    ]
    
    severities = [
        ErrorSeverity.CRITICAL,
        ErrorSeverity.ERROR,
        ErrorSeverity.WARNING,
        ErrorSeverity.INFO
    ]
    
    components = ["backend", "frontend", "agent", "coordination"]
    
    sources = [
        "backend.main",
        "backend.agents.agent_coordinator",
        "frontend.src.components.ErrorBoundary",
        "frontend.src.services.api"
    ]
    
    error_messages = [
        "Connection refused",
        "Failed to initialize agent",
        "Invalid response format",
        "Timeout waiting for agent response",
        "Authentication failed",
        "Resource not found",
        "Invalid input format",
        "Database connection error"
    ]
    
    for i in range(count):
        log_error(
            error=random.choice(error_messages),
            category=random.choice(categories),
            severity=random.choice(severities),
            component=random.choice(components),
            source=random.choice(sources),
            user_id=f"test-user-{random.randint(1, 5)}",
            context={
                "test": True,
                "index": i,
                "random_value": random.randint(1, 1000)
            }
        )
    
    logger.info(f"Generated {count} test error logs")

def print_error_summary():
    """Print a summary of the error logs"""
    logs = get_error_logs()
    
    if not logs:
        print("No error logs found.")
        return
    
    print(f"\nFound {len(logs)} error logs:")
    
    # Count by severity
    severity_counts = {}
    for log in logs:
        severity = log.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    for severity, count in severity_counts.items():
        print(f"  - {severity}: {count}")
    
    # Count by category
    category_counts = {}
    for log in logs:
        category = log.get("category", "UNKNOWN")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print("\nErrors by category:")
    for category, count in category_counts.items():
        print(f"  - {category}: {count}")
    
    # Print most recent errors
    print("\nMost recent errors:")
    for i, log in enumerate(logs[:5]):
        timestamp = log.get("timestamp", "")
        category = log.get("category", "UNKNOWN")
        severity = log.get("severity", "UNKNOWN")
        message = log.get("error_message", "")
        source = log.get("source", "")
        
        print(f"  {i+1}. [{severity}][{category}] {message[:50]}{'...' if len(message) > 50 else ''}")
        print(f"     Source: {source}")
        print(f"     Time: {timestamp}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ADE Error Logging Tool")
    parser.add_argument("--generate", type=int, help="Generate test error logs")
    parser.add_argument("--clear", action="store_true", help="Clear all error logs")
    parser.add_argument("--summary", action="store_true", help="Print error summary")
    
    args = parser.parse_args()
    
    if args.generate:
        generate_test_logs(args.generate)
    
    if args.clear:
        clear_error_logs()
        print("All error logs cleared.")
    
    if args.summary or (not args.generate and not args.clear):
        print_error_summary()
