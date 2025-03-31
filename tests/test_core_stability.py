import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.core.persistence.database import DatabaseManager
from src.core.tasks.queue_manager import TaskQueueManager, TaskStatus
from src.core.providers.registry import ProviderRegistry
from src.core.health.checker import HealthChecker, ComponentStatus

@pytest.fixture
async def database_manager():
    """Create a test database manager"""
    manager = DatabaseManager(
        connection_string="mongodb://localhost:27017",
        database_name="ade_test"
    )
    await manager.connect()
    yield manager
    await manager.disconnect()

@pytest.fixture
async def task_queue_manager():
    """Create a test task queue manager"""
    manager = TaskQueueManager(
        max_concurrent_tasks=5,
        max_retries=3,
        retry_delay=0.1
    )
    await manager.start()
    yield manager
    await manager.stop()

@pytest.fixture
def provider_registry():
    """Create a test provider registry"""
    return ProviderRegistry()

@pytest.fixture
async def health_checker(database_manager, task_queue_manager, provider_registry):
    """Create a test health checker"""
    return HealthChecker(
        database_manager=database_manager,
        task_queue_manager=task_queue_manager,
        provider_registry=provider_registry
    )

async def test_database_connection(database_manager):
    """Test database connection and basic operations"""
    # Test connection
    assert database_manager._is_connected
    
    # Test collection access
    collection = await database_manager.get_collection("test")
    assert collection is not None
    
    # Test basic operation
    test_doc = {"test": "data", "timestamp": datetime.now().isoformat()}
    result = await database_manager.execute_operation(
        collection.insert_one,
        test_doc
    )
    assert result.inserted_id is not None
    
    # Test health check
    health = await database_manager.health_check()
    assert health["status"] == "healthy"
    assert health["connected"] is True

async def test_task_queue_operations(task_queue_manager):
    """Test task queue operations and error handling"""
    # Test task submission
    async def test_task():
        await asyncio.sleep(0.1)
        return "success"
    
    task_id = await task_queue_manager.submit_task(
        name="test_task",
        func=test_task
    )
    assert task_id is not None
    
    # Test task status
    status = await task_queue_manager.get_task_status(task_id)
    assert status is not None
    assert status["name"] == "test_task"
    
    # Wait for task completion
    await asyncio.sleep(0.2)
    
    # Verify task completed
    status = await task_queue_manager.get_task_status(task_id)
    assert status["status"] == TaskStatus.COMPLETED.value
    
    # Test error handling
    async def failing_task():
        raise ValueError("Test error")
    
    task_id = await task_queue_manager.submit_task(
        name="failing_task",
        func=failing_task
    )
    
    # Wait for retries
    await asyncio.sleep(0.5)
    
    # Verify task failed after retries
    status = await task_queue_manager.get_task_status(task_id)
    assert status["status"] == TaskStatus.FAILED.value
    assert "Test error" in status["error"]
    
    # Test health check
    health = await task_queue_manager.health_check()
    assert health["status"] == "healthy"
    assert health["running"] is True

def test_provider_registry(provider_registry):
    """Test provider registry functionality"""
    # Test provider registration
    assert provider_registry.get_available_providers() is not None
    
    # Test provider configuration
    providers = provider_registry.get_available_providers()
    assert "ollama" in providers
    assert "groq" in providers
    
    # Test provider capabilities
    ollama_capabilities = provider_registry.get_provider_capabilities("ollama")
    assert ollama_capabilities is not None

async def test_system_health(health_checker):
    """Test comprehensive system health check"""
    # Perform health check
    health = await health_checker.check_health()
    
    # Verify overall status
    assert health["status"] in [
        ComponentStatus.HEALTHY.value,
        ComponentStatus.DEGRADED.value,
        ComponentStatus.UNHEALTHY.value,
        ComponentStatus.UNKNOWN.value
    ]
    
    # Verify components
    assert "database" in health["components"]
    assert "task_queue" in health["components"]
    assert "providers" in health["components"]
    
    # Verify component details
    for component in health["components"].values():
        assert "status" in component
        assert "details" in component
        assert "last_checked" in component

async def test_error_recovery(database_manager, task_queue_manager):
    """Test system recovery from errors"""
    # Simulate database connection loss
    await database_manager.disconnect()
    assert not database_manager._is_connected
    
    # Attempt to reconnect
    await database_manager.connect()
    assert database_manager._is_connected
    
    # Test task queue recovery
    async def intermittent_task():
        if datetime.now().timestamp() % 2 == 0:
            raise ValueError("Intermittent error")
        return "success"
    
    task_id = await task_queue_manager.submit_task(
        name="intermittent_task",
        func=intermittent_task
    )
    
    # Wait for task completion or failure
    await asyncio.sleep(1.0)
    
    # Verify task either completed or failed with retries
    status = await task_queue_manager.get_task_status(task_id)
    assert status["status"] in [
        TaskStatus.COMPLETED.value,
        TaskStatus.FAILED.value
    ] 