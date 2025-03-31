"""Tests for the Orchestrator class."""
import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from src.core.orchestrator import (
    Orchestrator,
    OrchestratorError,
    Plan,
    Task,
    PlanStatus,
    TaskStatus
)
from src.core.providers import (
    ProviderRegistry,
    ModelRouter,
    ProviderConfig,
    Capability
)

class MockProviderRegistry:
    def __init__(self):
        self.providers = {
            "mock_provider": ProviderConfig(
                enabled=True,
                capabilities={
                    Capability.TEXT_GENERATION: 0.9,
                    Capability.PLANNING: 0.8
                }
            )
        }
    
    def get_providers_for_capability(self, capability):
        return [("mock_provider", 0.9)]

class MockMongoClient:
    def __init__(self, *args, **kwargs):
        self.db = MagicMock()
        self.admin = MagicMock()
        self.admin.command.return_value = True
    
    def __getitem__(self, key):
        return self.db
    
    def close(self):
        pass

@pytest.fixture
def mock_provider_registry():
    return MockProviderRegistry()

@pytest.fixture
def mock_mongodb():
    with patch('pymongo.MongoClient', MockMongoClient):
        yield

@pytest.fixture
def orchestrator(mock_provider_registry, mock_mongodb):
    # Create an orchestrator with mocked dependencies
    return Orchestrator(
        provider_registry=mock_provider_registry,
        mongodb_uri="mongodb://localhost:27017",
        database_name="ade_test"
    )

def test_orchestrator_initialization(orchestrator):
    """Test that the orchestrator initializes correctly"""
    assert orchestrator is not None
    assert orchestrator.provider_registry is not None
    assert orchestrator.model_router is not None
    assert orchestrator.state_manager is not None
    assert orchestrator.task_executor is not None
    assert orchestrator.plan_manager is not None

def test_create_plan(orchestrator):
    """Test creating a plan"""
    # Mock the plan_manager.create_plan method
    orchestrator.plan_manager.create_plan = MagicMock(return_value=Plan(
        id="test-plan-id",
        goal="Test goal",
        status=PlanStatus.PLANNING
    ))
    
    # Test create_plan
    plan = orchestrator.create_plan("Test goal", user_id="test-user")
    
    # Verify the result
    assert plan is not None
    assert plan.id == "test-plan-id"
    assert plan.goal == "Test goal"
    assert plan.status == PlanStatus.PLANNING
    
    # Verify the plan_manager was called
    orchestrator.plan_manager.create_plan.assert_called_once_with("Test goal", "test-user")

def test_execute_plan(orchestrator):
    """Test executing a plan"""
    # Mock the plan_manager.execute_plan method
    orchestrator.plan_manager.execute_plan = MagicMock(return_value=Plan(
        id="test-plan-id",
        goal="Test goal",
        status=PlanStatus.EXECUTING
    ))
    
    # Test execute_plan
    plan = orchestrator.execute_plan("test-plan-id", user_id="test-user")
    
    # Verify the result
    assert plan is not None
    assert plan.id == "test-plan-id"
    assert plan.status == PlanStatus.EXECUTING
    
    # Verify the plan_manager was called
    orchestrator.plan_manager.execute_plan.assert_called_once_with("test-plan-id", "test-user")

def test_create_task(orchestrator):
    """Test creating a task"""
    # Mock the state_manager.save_task method
    orchestrator.state_manager.save_task = MagicMock(return_value=True)
    
    # Test create_task
    task = orchestrator.create_task(
        description="Test task",
        plan_id="test-plan-id",
        user_id="test-user"
    )
    
    # Verify the result
    assert task is not None
    assert task.description == "Test task"
    assert task.plan_id == "test-plan-id"
    assert task.status == TaskStatus.CREATED
    assert "user_id" in task.metadata
    assert task.metadata["user_id"] == "test-user"
    
    # Verify the state_manager was called
    orchestrator.state_manager.save_task.assert_called_once()

def test_shutdown(orchestrator):
    """Test orchestrator shutdown"""
    # Mock the task_executor.stop and state_manager.close methods
    orchestrator.task_executor.stop = MagicMock()
    orchestrator.state_manager.close = MagicMock()
    
    # Test shutdown
    orchestrator.shutdown()
    
    # Verify the methods were called
    orchestrator.task_executor.stop.assert_called_once()
    orchestrator.state_manager.close.assert_called_once()

# Additional test cases for better coverage

def test_get_plan(orchestrator):
    """Test getting a plan by ID"""
    # Mock the plan_manager.get_plan method
    test_plan = Plan(
        id="test-plan-id",
        goal="Test goal",
        status=PlanStatus.COMPLETED
    )
    orchestrator.plan_manager.get_plan = MagicMock(return_value=test_plan)
    
    # Test get_plan
    plan = orchestrator.get_plan("test-plan-id")
    
    # Verify the result
    assert plan is not None
    assert plan.id == "test-plan-id"
    assert plan.status == PlanStatus.COMPLETED
    
    # Verify the plan_manager was called
    orchestrator.plan_manager.get_plan.assert_called_once_with("test-plan-id")

def test_get_plans(orchestrator):
    """Test getting plans with status filter"""
    # Mock the plan_manager.get_plans method
    test_plans = [
        Plan(id="plan-1", goal="Goal 1", status=PlanStatus.EXECUTING),
        Plan(id="plan-2", goal="Goal 2", status=PlanStatus.EXECUTING)
    ]
    orchestrator.plan_manager.get_plans = MagicMock(return_value=test_plans)
    
    # Test get_plans with status filter
    plans = orchestrator.get_plans(status=PlanStatus.EXECUTING)
    
    # Verify the result
    assert len(plans) == 2
    assert all(plan.status == PlanStatus.EXECUTING for plan in plans)
    
    # Verify the plan_manager was called
    orchestrator.plan_manager.get_plans.assert_called_once_with(
        PlanStatus.EXECUTING, 100, 0
    )

def test_execute_task(orchestrator):
    """Test executing a task"""
    # Mock the state_manager methods
    test_task = Task(
        id="test-task-id",
        description="Test task",
        status=TaskStatus.CREATED
    )
    orchestrator.state_manager.get_task = MagicMock(return_value=test_task)
    orchestrator.state_manager.save_task = MagicMock(return_value=True)
    
    # Test execute_task
    task = orchestrator.execute_task("test-task-id", user_id="test-user")
    
    # Verify the result
    assert task is not None
    assert task.id == "test-task-id"
    assert task.status == TaskStatus.SUCCEEDED
    assert "executed_by" in task.metadata
    assert task.metadata["executed_by"] == "test-user"
    
    # Verify the state_manager methods were called
    orchestrator.state_manager.get_task.assert_called_once_with("test-task-id")
    assert orchestrator.state_manager.save_task.call_count == 2

def test_get_tasks(orchestrator):
    """Test getting tasks with filters"""
    # Mock the state_manager.get_tasks method
    test_tasks = [
        Task(id="task-1", description="Task 1", status=TaskStatus.RUNNING),
        Task(id="task-2", description="Task 2", status=TaskStatus.RUNNING)
    ]
    orchestrator.state_manager.get_tasks = MagicMock(return_value=test_tasks)
    
    # Test get_tasks with filters
    tasks = orchestrator.get_tasks(
        plan_id="test-plan-id",
        status=TaskStatus.RUNNING
    )
    
    # Verify the result
    assert len(tasks) == 2
    assert all(task.status == TaskStatus.RUNNING for task in tasks)
    
    # Verify the state_manager was called
    orchestrator.state_manager.get_tasks.assert_called_once_with(
        "test-plan-id", TaskStatus.RUNNING, 100, 0
    )

def test_get_history(orchestrator):
    """Test getting history entries"""
    # Mock the state_manager.get_history method
    test_history = [
        {
            "entity_type": "plan",
            "entity_id": "test-plan-id",
            "action": "create",
            "details": "Created plan"
        }
    ]
    orchestrator.state_manager.get_history = MagicMock(return_value=test_history)
    
    # Test get_history
    history = orchestrator.get_history(
        entity_type="plan",
        entity_id="test-plan-id"
    )
    
    # Verify the result
    assert len(history) == 1
    assert history[0]["entity_type"] == "plan"
    assert history[0]["entity_id"] == "test-plan-id"
    
    # Verify the state_manager was called
    orchestrator.state_manager.get_history.assert_called_once_with(
        "plan", "test-plan-id", 100, 0
    )

def test_error_handling(orchestrator):
    """Test error handling in orchestrator methods"""
    # Test create_plan error
    orchestrator.plan_manager.create_plan = MagicMock(side_effect=Exception("Test error"))
    
    with pytest.raises(OrchestratorError) as exc_info:
        orchestrator.create_plan("Test goal")
    assert "Failed to create plan" in str(exc_info.value)
    
    # Test execute_plan error
    orchestrator.plan_manager.execute_plan = MagicMock(side_effect=Exception("Test error"))
    
    with pytest.raises(OrchestratorError) as exc_info:
        orchestrator.execute_plan("test-plan-id")
    assert "Failed to execute plan" in str(exc_info.value)
    
    # Test get_plan error
    orchestrator.plan_manager.get_plan = MagicMock(side_effect=Exception("Test error"))
    
    with pytest.raises(OrchestratorError) as exc_info:
        orchestrator.get_plan("test-plan-id")
    assert "Failed to get plan" in str(exc_info.value) 