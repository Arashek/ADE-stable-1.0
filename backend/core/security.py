from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from typing import Dict, Optional
import time
import hashlib
from datetime import datetime, timedelta

# API Key configuration
API_KEY_NAME = "X-API-Key"
API_KEY = "your-secret-api-key"  # In production, use environment variables
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_rate_limited(self, client_ip: str) -> bool:
        now = datetime.now()
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Remove old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]

        # Check if rate limit is exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            return True

        # Add new request
        self.requests[client_ip].append(now)
        return False

    def get_remaining_requests(self, client_ip: str) -> int:
        now = datetime.now()
        if client_ip not in self.requests:
            return self.max_requests

        # Remove old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]

        return max(0, self.max_requests - len(self.requests[client_ip]))

class CommandValidator:
    def __init__(self):
        self.dangerous_commands = {
            'rm', 'mkfs', 'dd', 'chmod', 'chown', 'sudo', 'su',
            'mkfs.ext4', 'mkfs.ext3', 'mkfs.ext2', 'mkfs.ntfs',
            'mkfs.vfat', 'mkfs.fat', 'mkfs.msdos', 'mkfs.udf',
            'mkfs.bfs', 'mkfs.cramfs', 'mkfs.exfat', 'mkfs.f2fs',
            'mkfs.jfs', 'mkfs.minix', 'mkfs.nilfs2', 'mkfs.ocfs2',
            'mkfs.reiserfs', 'mkfs.xfs', 'mkfs.zfs'
        }

    def is_safe_command(self, command: str) -> bool:
        # Split command into parts and check first part
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False

        base_cmd = cmd_parts[0].lower()
        return base_cmd not in self.dangerous_commands

    def sanitize_command(self, command: str) -> str:
        # Remove any potentially dangerous characters
        return ''.join(c for c in command if c.isprintable())

class ResourceMonitor:
    def __init__(self):
        self.max_cpu_percent = 80
        self.max_memory_percent = 80
        self.max_disk_percent = 90

    def check_resources(self) -> bool:
        # In a real implementation, you would check actual system resources
        # For now, we'll return True to indicate resources are available
        return True

    def get_resource_usage(self) -> Dict[str, float]:
        # In a real implementation, you would get actual system metrics
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0
        }

# Create instances
rate_limiter = RateLimiter()
command_validator = CommandValidator()
resource_monitor = ResourceMonitor()

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

def check_rate_limit(client_ip: str) -> bool:
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    return True

def validate_command(command: str) -> str:
    if not command_validator.is_safe_command(command):
        raise HTTPException(
            status_code=400,
            detail="Command not allowed"
        )
    return command_validator.sanitize_command(command)

def check_resources() -> bool:
    if not resource_monitor.check_resources():
        raise HTTPException(
            status_code=503,
            detail="System resources unavailable"
        )
    return True

def generate_command_hash(command: str, timestamp: str) -> str:
    data = f"{command}:{timestamp}".encode()
    return hashlib.sha256(data).hexdigest() 