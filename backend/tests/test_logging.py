import pytest
import os
import logging
from datetime import datetime
from core.logging import LogManager, CustomFormatter

@pytest.fixture
def log_manager(tmp_path):
    """Create a LogManager instance with a temporary log directory"""
    log_dir = str(tmp_path / "logs")
    return LogManager(log_dir=log_dir)

def test_log_directory_creation(log_manager):
    """Test that the log directory is created"""
    assert os.path.exists(log_manager.log_dir)

def test_logger_setup(log_manager):
    """Test that the logger is properly configured"""
    assert isinstance(log_manager.logger, logging.Logger)
    assert log_manager.logger.level == logging.DEBUG
    assert len(log_manager.logger.handlers) == 2  # File and console handlers

def test_log_execution(log_manager, caplog):
    """Test logging of command execution"""
    command = "ls"
    status = "success"
    execution_time = 0.5
    client_ip = "127.0.0.1"
    
    log_manager.log_execution(command, status, execution_time, client_ip=client_ip)
    
    # Check that the log message was created
    assert any(
        f"Command executed successfully: {{'command': '{command}', 'status': '{status}'"
        in record.message
        for record in caplog.records
    )

def test_log_execution_error(log_manager, caplog):
    """Test logging of command execution errors"""
    command = "invalid_command"
    status = "error"
    execution_time = 0.1
    error = "Command not found"
    
    log_manager.log_execution(command, status, execution_time, error=error)
    
    # Check that the error log message was created
    assert any(
        f"Command execution failed: {{'command': '{command}', 'status': '{status}'"
        in record.message
        for record in caplog.records
    )

def test_log_resource_usage(log_manager, caplog):
    """Test logging of resource usage"""
    cpu_percent = 50.0
    memory_percent = 60.0
    disk_percent = 70.0
    
    log_manager.log_resource_usage(cpu_percent, memory_percent, disk_percent)
    
    # Check that the resource usage log message was created
    assert any(
        f"Resource usage - CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent}%"
        in record.message
        for record in caplog.records
    )

def test_log_rate_limit(log_manager, caplog):
    """Test logging of rate limit information"""
    client_ip = "127.0.0.1"
    remaining_requests = 5
    
    log_manager.log_rate_limit(client_ip, remaining_requests)
    
    # Check that the rate limit log message was created
    assert any(
        f"Rate limit check - IP: {client_ip}, Remaining requests: {remaining_requests}"
        in record.message
        for record in caplog.records
    )

def test_log_security_event(log_manager, caplog):
    """Test logging of security events"""
    event_type = "invalid_api_key"
    details = {"ip": "127.0.0.1", "attempts": 3}
    
    log_manager.log_security_event(event_type, details)
    
    # Check that the security event log message was created
    assert any(
        f"Security event - {event_type}: {details}"
        in record.message
        for record in caplog.records
    )

def test_custom_formatter():
    """Test the custom formatter"""
    formatter = CustomFormatter()
    
    # Create a test record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Format the record
    formatted = formatter.format(record)
    
    # Check that the formatted message contains the expected components
    assert "Test message" in formatted
    assert "INFO" in formatted
    assert "test" in formatted

def test_log_rotation(log_manager):
    """Test log file rotation"""
    log_file = os.path.join(log_manager.log_dir, "ai_execution.log")
    
    # Write enough logs to trigger rotation
    for i in range(1000):
        log_manager.log_execution(f"command_{i}", "success", 0.1)
    
    # Check that backup files were created
    backup_files = [f for f in os.listdir(log_manager.log_dir) 
                   if f.startswith("ai_execution.log.")]
    assert len(backup_files) > 0 