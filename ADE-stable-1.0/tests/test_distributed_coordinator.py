import pytest
import asyncio
import aiohttp
from datetime import datetime, timedelta
from src.core.distributed.coordinator import Coordinator, NodeState
from src.core.distributed.executor import NodeInfo, TaskInfo

@pytest.fixture
async def coordinator():
    """Create a coordinator instance for testing"""
    coordinator = Coordinator(host="localhost", port=8000)
    await coordinator.start()
    yield coordinator
    await coordinator.stop()

@pytest.fixture
async def client():
    """Create an HTTP client for testing"""
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.mark.asyncio
async def test_node_registration(coordinator, client):
    """Test node registration"""
    # Register a node
    node_data = {
        "node_id": "test_node_1",
        "host": "localhost",
        "port": 8001,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
        result = await response.json()
        assert result["status"] == "success"
    
    # Verify node is registered
    assert "test_node_1" in coordinator.nodes
    node_state = coordinator.nodes["test_node_1"]
    assert node_state.info.host == "localhost"
    assert node_state.info.port == 8001
    assert node_state.health_status == "healthy"

@pytest.mark.asyncio
async def test_node_heartbeat(coordinator, client):
    """Test node heartbeat"""
    # Register a node
    node_data = {
        "node_id": "test_node_2",
        "host": "localhost",
        "port": 8002,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
    # Send heartbeat
    heartbeat_data = {
        "node_id": "test_node_2",
        "load": 0.5,
        "available_memory": 2048,
        "status": "running"
    }
    
    async with client.post("http://localhost:8000/nodes/heartbeat", json=heartbeat_data) as response:
        assert response.status == 200
        result = await response.json()
        assert result["status"] == "success"
    
    # Verify heartbeat was processed
    node_state = coordinator.nodes["test_node_2"]
    assert node_state.info.load == 0.5
    assert node_state.info.available_memory == 2048
    assert node_state.info.status == "running"
    assert node_state.last_heartbeat is not None

@pytest.mark.asyncio
async def test_node_health_check(coordinator, client):
    """Test node health check"""
    # Register a node
    node_data = {
        "node_id": "test_node_3",
        "host": "localhost",
        "port": 8003,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
    # Simulate node timeout
    node_state = coordinator.nodes["test_node_3"]
    node_state.last_heartbeat = datetime.now() - timedelta(seconds=31)
    
    # Wait for health check
    await asyncio.sleep(6)  # Health check runs every 5 seconds
    
    # Verify node is marked as unhealthy
    assert node_state.health_status == "unhealthy"

@pytest.mark.asyncio
async def test_task_submission(coordinator, client):
    """Test task submission"""
    # Register a node
    node_data = {
        "node_id": "test_node_4",
        "host": "localhost",
        "port": 8004,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
    # Submit a task
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
        result = await response.json()
        assert result["status"] == "success"
    
    # Verify task is in queue
    assert "test_task_1" in coordinator.tasks
    task = coordinator.tasks["test_task_1"]
    assert task.script_id == "script_1"
    assert task.priority == 1
    assert task.status == "pending"

@pytest.mark.asyncio
async def test_task_scheduling(coordinator, client):
    """Test task scheduling"""
    # Register a node
    node_data = {
        "node_id": "test_node_5",
        "host": "localhost",
        "port": 8005,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
    # Submit a task
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
    
    # Wait for task scheduling
    await asyncio.sleep(0.2)  # Scheduling runs every 0.1 seconds
    
    # Verify task is assigned to node
    task = coordinator.tasks["test_task_2"]
    assert task.node_id == "test_node_5"
    assert "test_task_2" in coordinator.nodes["test_node_5"].tasks

@pytest.mark.asyncio
async def test_task_update(coordinator, client):
    """Test task status update"""
    # Register a node and submit a task
    node_data = {
        "node_id": "test_node_6",
        "host": "localhost",
        "port": 8006,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
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
    
    # Update task status
    update_data = {
        "task_id": "test_task_3",
        "status": "completed",
        "result": {"output": "success"}
    }
    
    async with client.post("http://localhost:8000/tasks/update", json=update_data) as response:
        assert response.status == 200
        result = await response.json()
        assert result["status"] == "success"
    
    # Verify task is updated
    task = coordinator.tasks["test_task_3"]
    assert task.status == "completed"
    assert task.result == {"output": "success"}
    assert task.completed_at is not None

@pytest.mark.asyncio
async def test_task_reassignment(coordinator, client):
    """Test task reassignment on node failure"""
    # Register two nodes
    node1_data = {
        "node_id": "test_node_7",
        "host": "localhost",
        "port": 8007,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    node2_data = {
        "node_id": "test_node_8",
        "host": "localhost",
        "port": 8008,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "docker"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node1_data) as response:
        assert response.status == 200
    
    async with client.post("http://localhost:8000/nodes/register", json=node2_data) as response:
        assert response.status == 200
    
    # Submit a task
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
    
    # Wait for task scheduling
    await asyncio.sleep(0.2)
    
    # Simulate node failure
    node_state = coordinator.nodes["test_node_7"]
    node_state.last_heartbeat = datetime.now() - timedelta(seconds=31)
    
    # Wait for health check
    await asyncio.sleep(6)
    
    # Verify task is reassigned
    task = coordinator.tasks["test_task_4"]
    assert task.node_id == "test_node_8"
    assert "test_task_4" in coordinator.nodes["test_node_8"].tasks

@pytest.mark.asyncio
async def test_node_capabilities(coordinator, client):
    """Test task scheduling based on node capabilities"""
    # Register a node with specific capabilities
    node_data = {
        "node_id": "test_node_9",
        "host": "localhost",
        "port": 8009,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python", "gpu"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node_data) as response:
        assert response.status == 200
    
    # Submit a task requiring GPU
    task_data = {
        "task_id": "test_task_5",
        "script_id": "script_5",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python", "gpu"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task scheduling
    await asyncio.sleep(0.2)
    
    # Verify task is assigned to node with required capabilities
    task = coordinator.tasks["test_task_5"]
    assert task.node_id == "test_node_9"
    assert "test_task_5" in coordinator.nodes["test_node_9"].tasks

@pytest.mark.asyncio
async def test_load_balancing(coordinator, client):
    """Test load balancing across nodes"""
    # Register two nodes
    node1_data = {
        "node_id": "test_node_10",
        "host": "localhost",
        "port": 8010,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python"]
        }
    }
    
    node2_data = {
        "node_id": "test_node_11",
        "host": "localhost",
        "port": 8011,
        "capabilities": {
            "max_load": 10,
            "memory": 4096,
            "features": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/nodes/register", json=node1_data) as response:
        assert response.status == 200
    
    async with client.post("http://localhost:8000/nodes/register", json=node2_data) as response:
        assert response.status == 200
    
    # Set different loads for nodes
    coordinator.nodes["test_node_10"].info.load = 0.8
    coordinator.nodes["test_node_11"].info.load = 0.2
    
    # Submit a task
    task_data = {
        "task_id": "test_task_6",
        "script_id": "script_6",
        "priority": 1,
        "requirements": {
            "memory": 1024,
            "capabilities": ["python"]
        }
    }
    
    async with client.post("http://localhost:8000/tasks/submit", json=task_data) as response:
        assert response.status == 200
    
    # Wait for task scheduling
    await asyncio.sleep(0.2)
    
    # Verify task is assigned to less loaded node
    task = coordinator.tasks["test_task_6"]
    assert task.node_id == "test_node_11"
    assert "test_task_6" in coordinator.nodes["test_node_11"].tasks 