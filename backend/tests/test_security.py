import pytest
from fastapi import HTTPException
from core.security import (
    RateLimiter,
    CommandValidator,
    ResourceMonitor,
    verify_api_key,
    check_rate_limit,
    validate_command,
    check_resources,
    generate_command_hash
)

@pytest.fixture
def rate_limiter():
    return RateLimiter(max_requests=2, window_seconds=1)

@pytest.fixture
def command_validator():
    return CommandValidator()

@pytest.fixture
def resource_monitor():
    return ResourceMonitor()

def test_rate_limiter(rate_limiter):
    # Test within limits
    assert rate_limiter.is_rate_limited("127.0.0.1") is False
    assert rate_limiter.is_rate_limited("127.0.0.1") is False
    
    # Test exceeding limits
    assert rate_limiter.is_rate_limited("127.0.0.1") is True
    
    # Test different IPs
    assert rate_limiter.is_rate_limited("192.168.1.1") is False

def test_command_validator(command_validator):
    # Test safe commands
    assert command_validator.is_safe_command("ls") is True
    assert command_validator.is_safe_command("git status") is True
    
    # Test dangerous commands
    assert command_validator.is_safe_command("rm -rf /") is False
    assert command_validator.is_safe_command("sudo rm -rf /") is False
    
    # Test command sanitization
    assert command_validator.sanitize_command("ls\n") == "ls"

def test_resource_monitor(resource_monitor):
    # Test resource checking
    assert resource_monitor.check_resources() is True
    
    # Test resource usage reporting
    usage = resource_monitor.get_resource_usage()
    assert isinstance(usage, dict)
    assert all(key in usage for key in ['cpu_percent', 'memory_percent', 'disk_percent'])

@pytest.mark.asyncio
async def test_verify_api_key():
    # Test with valid API key
    assert await verify_api_key("your-secret-api-key") == "your-secret-api-key"
    
    # Test with invalid API key
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key("invalid-key")
    assert exc_info.value.status_code == 403

def test_check_rate_limit():
    # Test rate limit check
    assert check_rate_limit("127.0.0.1") is True
    
    # Test rate limit exceeded
    with pytest.raises(HTTPException) as exc_info:
        for _ in range(3):
            check_rate_limit("127.0.0.1")
    assert exc_info.value.status_code == 429

def test_validate_command():
    # Test valid command
    assert validate_command("ls") == "ls"
    
    # Test invalid command
    with pytest.raises(HTTPException) as exc_info:
        validate_command("rm -rf /")
    assert exc_info.value.status_code == 400

def test_check_resources():
    # Test resource check
    assert check_resources() is True

def test_generate_command_hash():
    command = "ls"
    timestamp = "2024-01-01T00:00:00"
    hash_value = generate_command_hash(command, timestamp)
    
    # Test hash generation
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 hash length
    
    # Test hash consistency
    assert generate_command_hash(command, timestamp) == hash_value 