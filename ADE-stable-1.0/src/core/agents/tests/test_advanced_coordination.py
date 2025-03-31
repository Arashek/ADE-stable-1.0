import pytest
import asyncio
from datetime import datetime, timedelta
from ..advanced_coordination import (
    AdvancedAgentCoordinator,
    AgentRole,
    ExpertiseLevel,
    AgentCapability,
    Task
)

@pytest.fixture
def coordinator():
    return AdvancedAgentCoordinator()

@pytest.fixture
def sample_capabilities():
    return [
        AgentCapability(
            name="code_implementation",
            description="Implement code features",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            supported_roles={AgentRole.DEVELOPER}
        ),
        AgentCapability(
            name="code_review",
            description="Review code changes",
            expertise_level=ExpertiseLevel.EXPERT,
            supported_roles={AgentRole.REVIEWER}
        )
    ]

@pytest.mark.asyncio
async def test_agent_registration(coordinator, sample_capabilities):
    """Test agent registration with capabilities."""
    success = await coordinator.register_agent(
        agent_id="agent1",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    assert success
    assert "agent1" in coordinator.agents
    assert coordinator.agents["agent1"].role == AgentRole.DEVELOPER
    assert len(coordinator.agents["agent1"].capabilities) == 2

@pytest.mark.asyncio
async def test_task_creation_and_allocation(coordinator, sample_capabilities):
    """Test task creation and dynamic agent allocation."""
    # Register agents
    await coordinator.register_agent(
        agent_id="agent1",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    await coordinator.register_agent(
        agent_id="agent2",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create a task
    task = Task(
        id="task1",
        title="Implement feature",
        description="Implement new feature X",
        required_capabilities={"code_implementation"},
        priority=1,
        deadline=datetime.now() + timedelta(days=1)
    )
    
    # Create and allocate task
    await coordinator.create_task(task)
    
    # Verify task allocation
    assert task.id in coordinator.tasks
    assert task.assigned_agents is not None
    assert len(task.assigned_agents) > 0
    assert all(agent_id in coordinator.agents for agent_id in task.assigned_agents)

@pytest.mark.asyncio
async def test_agent_specialization(coordinator, sample_capabilities):
    """Test agent specialization optimization."""
    # Register agent
    await coordinator.register_agent(
        agent_id="agent1",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create and complete some tasks
    for i in range(5):
        task = Task(
            id=f"task{i}",
            title=f"Task {i}",
            description=f"Description {i}",
            required_capabilities={"code_implementation"},
            priority=1,
            deadline=datetime.now() + timedelta(days=1),
            metrics={"start_time": datetime.now(), "end_time": datetime.now() + timedelta(hours=1)}
        )
        await coordinator.create_task(task)
        task.status = "completed"
        coordinator.agents["agent1"].current_tasks.append(task)
    
    # Optimize specialization
    await coordinator.optimize_agent_specialization("agent1")
    
    # Verify specialization updates
    agent = coordinator.agents["agent1"]
    assert agent.performance_metrics["task_completion_rate"] > 0
    assert agent.performance_metrics["efficiency"] > 0

@pytest.mark.asyncio
async def test_collaboration_patterns(coordinator, sample_capabilities):
    """Test collaboration pattern tracking and optimization."""
    # Register multiple agents
    for i in range(3):
        await coordinator.register_agent(
            agent_id=f"agent{i}",
            role=AgentRole.DEVELOPER,
            capabilities=sample_capabilities
        )
    
    # Create a task requiring collaboration
    task = Task(
        id="collab_task",
        title="Collaborative task",
        description="Task requiring multiple agents",
        required_capabilities={"code_implementation", "code_review"},
        priority=1,
        deadline=datetime.now() + timedelta(days=1)
    )
    
    # Create and allocate task
    await coordinator.create_task(task)
    
    # Verify collaboration patterns
    metrics = await coordinator.get_coordination_metrics()
    assert "collaboration_patterns" in metrics
    assert len(metrics["collaboration_patterns"]) > 0

@pytest.mark.asyncio
async def test_workload_balancing(coordinator, sample_capabilities):
    """Test workload balancing across agents."""
    # Register agents
    await coordinator.register_agent(
        agent_id="agent1",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    await coordinator.register_agent(
        agent_id="agent2",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create multiple tasks
    for i in range(5):
        task = Task(
            id=f"task{i}",
            title=f"Task {i}",
            description=f"Description {i}",
            required_capabilities={"code_implementation"},
            priority=1,
            deadline=datetime.now() + timedelta(days=1)
        )
        await coordinator.create_task(task)
    
    # Verify workload distribution
    metrics = await coordinator.get_coordination_metrics()
    workloads = metrics["agent_workloads"]
    
    assert len(workloads) == 2
    assert all(0 <= workload["current_workload"] <= 1.0 for workload in workloads.values())
    
    # Check workload balance
    workload_diff = abs(
        workloads["agent1"]["current_workload"] -
        workloads["agent2"]["current_workload"]
    )
    assert workload_diff < 0.3  # Workloads should be relatively balanced

@pytest.mark.asyncio
async def test_performance_metrics(coordinator, sample_capabilities):
    """Test performance metrics tracking and calculation."""
    # Register agent
    await coordinator.register_agent(
        agent_id="agent1",
        role=AgentRole.DEVELOPER,
        capabilities=sample_capabilities
    )
    
    # Create and complete some tasks
    for i in range(3):
        task = Task(
            id=f"task{i}",
            title=f"Task {i}",
            description=f"Description {i}",
            required_capabilities={"code_implementation"},
            priority=1,
            deadline=datetime.now() + timedelta(days=1),
            metrics={
                "start_time": datetime.now(),
                "end_time": datetime.now() + timedelta(hours=1)
            }
        )
        await coordinator.create_task(task)
        task.status = "completed"
        coordinator.agents["agent1"].current_tasks.append(task)
    
    # Get metrics
    metrics = await coordinator.get_coordination_metrics()
    agent_metrics = metrics["performance_metrics"]["agent1"]
    
    # Verify metrics
    assert "task_completion_rate" in agent_metrics
    assert "efficiency" in agent_metrics
    assert "collaboration_score" in agent_metrics
    assert 0 <= agent_metrics["task_completion_rate"] <= 1.0
    assert 0 <= agent_metrics["efficiency"] <= 1.0 