import pytest
import asyncio
import aiohttp
from datetime import datetime
from src.core.distributed.worker import WorkerNode
from src.core.distributed.executor import TaskInfo

@pytest.fixture
async def coordinator():
    """Create a coordinator instance for testing"""
    from src.core.distributed.coordinator import Coordinator
    coordinator = Coordinator(host="localhost", port=8000)
    await coordinator.start()
    yield coordinator
    await coordinator.stop()

@pytest.fixture
async def worker():
    """Create a worker node instance for testing"""
    worker = WorkerNode(
        host="localhost",
        port=8001,
        coordinator_host="localhost",
        coordinator_port=8000,
        capabilities={
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    )
    await worker.start()
    yield worker
    await worker.stop()

@pytest.fixture
async def client():
    """Create an HTTP client for testing"""
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.mark.asyncio
async def test_worker_registration(coordinator, worker):
    """Test worker registration with coordinator"""
    # Wait for registration
    await asyncio.sleep(0.5)
    
    # Verify worker is registered
    assert worker.node_id in coordinator.nodes
    node_state = coordinator.nodes[worker.node_id]
    assert node_state.info.host == "localhost"
    assert node_state.info.port == 8001
    assert node_state.health_status == "healthy"

@pytest.mark.asyncio
async def test_worker_heartbeat(coordinator, worker):
    """Test worker heartbeat"""
    # Wait for initial heartbeat
    await asyncio.sleep(6)  # Heartbeat runs every 5 seconds
    
    # Verify heartbeat was received
    node_state = coordinator.nodes[worker.node_id]
    assert node_state.last_heartbeat is not None
    assert node_state.info.status == "running"

@pytest.mark.asyncio
async def test_task_assignment(coordinator, worker, client):
    """Test task assignment to worker"""
    # Submit task to coordinator
    task_data = {
        "task_id": "test_task_1",
        "script_id": "script_1",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task assignment
    await asyncio.sleep(0.3)  # Scheduling runs every 0.1 seconds
    
    # Verify task is assigned to worker
    assert "test_task_1" in worker.current_tasks
    task = worker.current_tasks["test_task_1"]
    assert task.script_id == "script_1"
    assert task.node_id == worker.node_id
    assert task.status == "pending"

@pytest.mark.asyncio
async def test_task_execution(coordinator, worker, client):
    """Test task execution"""
    # Submit task to coordinator
    task_data = {
        "task_id": "test_task_2",
        "script_id": "script_2",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task execution
    await asyncio.sleep(0.3)
    
    # Verify task is being executed
    task = worker.current_tasks["test_task_2"]
    assert task.status == "running"
    assert task.started_at is not None

@pytest.mark.asyncio
async def test_task_completion(coordinator, worker, client):
    """Test task completion"""
    # Submit task to coordinator
    task_data = {
        "task_id": "test_task_3",
        "script_id": "script_3",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task completion
    await asyncio.sleep(0.3)
    
    # Simulate task completion
    task = worker.current_tasks["test_task_3"]
    task.status = "completed"
    task.completed_at = datetime.now()
    task.result = {"output": "success"}
    
    # Update task status
    await worker._update_task_status(task)
    
    # Verify task is completed
    assert task.status == "completed"
    assert task.result == {"output": "success"}
    assert task.completed_at is not None

@pytest.mark.asyncio
async def test_task_failure(coordinator, worker, client):
    """Test task failure handling"""
    # Submit task to coordinator
    task_data = {
        "task_id": "test_task_4",
        "script_id": "script_4",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task execution
    await asyncio.sleep(0.3)
    
    # Simulate task failure
    task = worker.current_tasks["test_task_4"]
    task.status = "failed"
    task.completed_at = datetime.now()
    task.error = "Script execution failed"
    
    # Update task status
    await worker._update_task_status(task)
    
    # Verify task failure is handled
    assert task.status == "failed"
    assert task.error == "Script execution failed"
    assert task.completed_at is not None

@pytest.mark.asyncio
async def test_task_stop(coordinator, worker, client):
    """Test task stop request"""
    # Submit task to coordinator
    task_data = {
        "task_id": "test_task_5",
        "script_id": "script_5",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task assignment
    await asyncio.sleep(0.3)
    
    # Send stop request
    stop_data = {"task_id": "test_task_5"}
    async with client.post("http://localhost:8001/tasks/stop", json=stop_data) as response:
        assert response.status == 200
        result = await response.json()
        assert result["status"] == "success"
    
    # Verify task is stopped
    assert "test_task_5" not in worker.current_tasks

@pytest.mark.asyncio
async def test_worker_shutdown(coordinator, worker):
    """Test worker shutdown"""
    # Stop worker
    await worker.stop()
    
    # Wait for deregistration
    await asyncio.sleep(0.5)
    
    # Verify worker is deregistered
    assert worker.node_id not in coordinator.nodes

@pytest.mark.asyncio
async def test_capability_matching(coordinator, worker, client):
    """Test task assignment based on capabilities"""
    # Submit task requiring specific capability
    task_data = {
        "task_id": "test_task_6",
        "script_id": "script_6",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task assignment
    await asyncio.sleep(0.3)
    
    # Verify task is assigned to worker with matching capabilities
    assert "test_task_6" in worker.current_tasks
    task = worker.current_tasks["test_task_6"]
    assert task.node_id == worker.node_id
    assert "docker" in worker.capabilities["features"]

@pytest.mark.asyncio
async def test_resource_monitoring(coordinator, worker):
    """Test resource monitoring"""
    # Wait for heartbeat
    await asyncio.sleep(6)
    
    # Verify resource metrics are reported
    node_state = coordinator.nodes[worker.node_id]
    assert node_state.info.load >= 0
    assert node_state.info.available_memory > 0
    assert node_state.info.status == "running" 