import pytest
import asyncio
import time
from production.src.core.time_management import (
    TimeManager, Task, TaskPriority, TaskStatus, TaskMetrics
)

@pytest.fixture
async def time_manager():
    manager = TimeManager()
    yield manager
    # Cleanup if needed

@pytest.fixture
def sample_task():
    return Task(
        task_id="test_task",
        agent_id="test_agent",
        priority=TaskPriority.NORMAL,
        timeout=10.0,
        content={"test": "data"}
    )

@pytest.mark.asyncio
async def test_task_registration(time_manager, sample_task):
    """Test task registration with dependency checking."""
    # Register task successfully
    success = await time_manager.register_task(sample_task)
    assert success is True
    
    # Try to register same task again
    success = await time_manager.register_task(sample_task)
    assert success is False

@pytest.mark.asyncio
async def test_circular_dependency_detection(time_manager):
    """Test detection of circular dependencies."""
    # Create tasks with circular dependency
    task1 = Task(
        task_id="task1",
        agent_id="agent1",
        priority=TaskPriority.NORMAL,
        timeout=10.0,
        dependencies={"task2"},
        content={}
    )
    
    task2 = Task(
        task_id="task2",
        agent_id="agent1",
        priority=TaskPriority.NORMAL,
        timeout=10.0,
        dependencies={"task1"},
        content={}
    )
    
    # Register first task
    success = await time_manager.register_task(task1)
    assert success is True
    
    # Try to register second task (should fail due to circular dependency)
    success = await time_manager.register_task(task2)
    assert success is False

@pytest.mark.asyncio
async def test_resource_management(time_manager):
    """Test resource allocation and deadlock prevention."""
    # Create tasks that share resources
    task1 = Task(
        task_id="task1",
        agent_id="agent1",
        priority=TaskPriority.NORMAL,
        timeout=10.0,
        resources={"resource1", "resource2"},
        content={}
    )
    
    task2 = Task(
        task_id="task2",
        agent_id="agent2",
        priority=TaskPriority.NORMAL,
        timeout=10.0,
        resources={"resource2", "resource3"},
        content={}
    )
    
    # Register tasks
    await time_manager.register_task(task1)
    await time_manager.register_task(task2)
    
    # Try to acquire resources for task1
    success = await time_manager.acquire_resources(task1.task_id)
    assert success is True
    
    # Try to acquire resources for task2 (should fail as resource2 is locked)
    success = await time_manager.acquire_resources(task2.task_id)
    assert success is False
    
    # Release resources
    await time_manager.release_resources(task1.task_id)
    
    # Now task2 should be able to acquire resources
    success = await time_manager.acquire_resources(task2.task_id)
    assert success is True

@pytest.mark.asyncio
async def test_task_progress_tracking(time_manager, sample_task):
    """Test task progress tracking and stall detection."""
    # Register and start task
    await time_manager.register_task(sample_task)
    sample_task.status = TaskStatus.RUNNING
    
    # Update progress
    success = await time_manager.update_task_progress(sample_task.task_id, 0.5)
    assert success is True
    
    # Check metrics
    metrics = await time_manager.get_task_metrics(sample_task.task_id)
    assert metrics is not None
    assert metrics["last_progress_time"] > metrics["start_time"]
    assert metrics["estimated_completion"] is not None
    
    # Simulate stall
    await asyncio.sleep(time_manager.stall_threshold + 1)
    success = await time_manager.update_task_progress(sample_task.task_id, 0.5)
    assert success is True
    
    # Check if task is marked as stalled
    assert sample_task.status == TaskStatus.STALLED

@pytest.mark.asyncio
async def test_heartbeat_monitoring(time_manager):
    """Test agent heartbeat monitoring."""
    agent_id = "test_agent"
    
    # Update heartbeat
    await time_manager.update_heartbeat(agent_id)
    
    # Check agent health
    stalled_agents = await time_manager.check_agent_health()
    assert agent_id not in stalled_agents
    
    # Simulate agent stall
    await asyncio.sleep(time_manager.heartbeat_interval * 3)
    stalled_agents = await time_manager.check_agent_health()
    assert agent_id in stalled_agents

@pytest.mark.asyncio
async def test_task_priority_adjustment(time_manager, sample_task):
    """Test dynamic task priority adjustment."""
    # Register task
    await time_manager.register_task(sample_task)
    
    # Set initial priority
    sample_task.priority = TaskPriority.NORMAL
    
    # Simulate time pressure
    sample_task.metrics.estimated_completion = time.time() + 2
    sample_task.timeout = 10
    
    # Check priority adjustment
    new_priority = await time_manager.adjust_task_priority(sample_task.task_id)
    assert new_priority == TaskPriority.HIGH
    
    # Simulate critical time pressure
    sample_task.metrics.estimated_completion = time.time() + 1
    new_priority = await time_manager.adjust_task_priority(sample_task.task_id)
    assert new_priority == TaskPriority.CRITICAL

@pytest.mark.asyncio
async def test_stall_recovery(time_manager, sample_task):
    """Test stall recovery mechanisms."""
    # Register and start task
    await time_manager.register_task(sample_task)
    sample_task.status = TaskStatus.RUNNING
    
    # Simulate multiple stalls
    for _ in range(3):
        await asyncio.sleep(time_manager.stall_threshold + 1)
        await time_manager.update_task_progress(sample_task.task_id, 0.5)
        assert sample_task.status == TaskStatus.PENDING
    
    # Simulate one more stall
    await asyncio.sleep(time_manager.stall_threshold + 1)
    await time_manager.update_task_progress(sample_task.task_id, 0.5)
    assert sample_task.status == TaskStatus.FAILED

@pytest.mark.asyncio
async def test_concurrent_task_execution(time_manager):
    """Test handling of concurrent task execution."""
    tasks = []
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            agent_id=f"agent_{i}",
            priority=TaskPriority.NORMAL,
            timeout=10.0,
            resources={f"resource_{i}"},
            content={}
        )
        tasks.append(task)
        await time_manager.register_task(task)
    
    # Try to acquire resources for all tasks concurrently
    async def acquire_resources(task_id):
        return await time_manager.acquire_resources(task_id)
    
    results = await asyncio.gather(*[
        acquire_resources(task.task_id) for task in tasks
    ])
    
    # All tasks should be able to acquire their unique resources
    assert all(results) 