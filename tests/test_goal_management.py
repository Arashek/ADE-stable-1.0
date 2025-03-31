import pytest
import asyncio
from datetime import datetime, timedelta
from production.src.core.goal_management import (
    GoalManager, Goal, GoalType, GoalStatus, GoalMetrics
)

@pytest.fixture
async def goal_manager():
    manager = GoalManager()
    yield manager

@pytest.fixture
def sample_project_goal():
    return Goal(
        goal_id="project_1",
        type=GoalType.PROJECT,
        description="Build a multi-agent system",
        metadata={
            "objectives": [
                "Create scalable agent architecture",
                "Implement robust communication",
                "Ensure system reliability"
            ]
        }
    )

@pytest.mark.asyncio
async def test_goal_creation(goal_manager):
    """Test goal creation and hierarchy."""
    # Create project goal
    project = await goal_manager.create_goal(
        description="Build a multi-agent system",
        goal_type=GoalType.PROJECT,
        user_intentions=["Create scalable system", "Ensure reliability"]
    )
    
    assert project is not None
    assert project.type == GoalType.PROJECT
    assert len(project.subgoals) > 0  # Should have generated milestones
    
    # Create milestone goal
    milestone = await goal_manager.create_goal(
        description="Development Phase",
        goal_type=GoalType.MILESTONE,
        parent_id=project.goal_id
    )
    
    assert milestone is not None
    assert milestone.type == GoalType.MILESTONE
    assert milestone.parent_id == project.goal_id
    assert len(milestone.subgoals) > 0  # Should have generated tasks

@pytest.mark.asyncio
async def test_goal_progress_tracking(goal_manager, sample_project_goal):
    """Test goal progress tracking and updates."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create and add a milestone
    milestone = await goal_manager.create_goal(
        description="Development Phase",
        goal_type=GoalType.MILESTONE,
        parent_id=sample_project_goal.goal_id
    )
    
    # Update milestone progress
    success = await goal_manager.update_goal_progress(
        goal_id=milestone.goal_id,
        progress=0.5,
        agent_id="agent_1",
        context={"phase": "development"}
    )
    
    assert success is True
    assert milestone.metrics.progress == 0.5
    assert milestone.status == GoalStatus.IN_PROGRESS
    
    # Update to completion
    success = await goal_manager.update_goal_progress(
        goal_id=milestone.goal_id,
        progress=1.0,
        agent_id="agent_1",
        context={"phase": "development"}
    )
    
    assert success is True
    assert milestone.metrics.progress == 1.0
    assert milestone.status == GoalStatus.COMPLETED
    assert milestone.metrics.completion_time is not None

@pytest.mark.asyncio
async def test_goal_alignment(goal_manager, sample_project_goal):
    """Test goal alignment checking."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create a task goal
    task = await goal_manager.create_goal(
        description="Implement agent communication",
        goal_type=GoalType.TASK,
        parent_id=sample_project_goal.goal_id,
        user_intentions=["Create robust communication", "Ensure reliability"]
    )
    
    # Update progress to trigger alignment check
    await goal_manager.update_goal_progress(
        goal_id=task.goal_id,
        progress=0.5,
        agent_id="agent_1",
        context={"phase": "development"}
    )
    
    # Check alignment results
    assert len(task.alignment_checks) > 0
    latest_check = task.alignment_checks[-1]
    assert "alignment_score" in latest_check
    assert "issues" in latest_check
    assert "suggestions" in latest_check

@pytest.mark.asyncio
async def test_goal_adaptation(goal_manager, sample_project_goal):
    """Test goal adaptation capabilities."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Adapt goal with new requirements
    adapted_goal = await goal_manager.adapt_goal(
        goal_id=sample_project_goal.goal_id,
        changes={
            "description": "Build a scalable multi-agent system",
            "metadata": {
                "objectives": [
                    "Create scalable agent architecture",
                    "Implement robust communication",
                    "Ensure system reliability",
                    "Optimize performance"
                ]
            },
            "reason": "Added performance optimization requirement"
        }
    )
    
    assert adapted_goal is not None
    assert adapted_goal.status == GoalStatus.ADAPTED
    assert adapted_goal.metrics.adaptation_count == 1
    assert "Optimize performance" in adapted_goal.metadata["objectives"]
    
    # Check learning data
    assert sample_project_goal.goal_id in goal_manager.learning_data
    assert len(goal_manager.learning_data[sample_project_goal.goal_id]) > 0

@pytest.mark.asyncio
async def test_unachievable_goals_detection(goal_manager, sample_project_goal):
    """Test detection of unachievable goals."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create a task with dependencies
    task = await goal_manager.create_goal(
        description="Implement advanced features",
        goal_type=GoalType.TASK,
        parent_id=sample_project_goal.goal_id,
        dependencies={"non_existent_goal"},
        required_capabilities={"advanced_implementation"}
    )
    
    # Set time constraints
    task.metrics.start_time = datetime.now() - timedelta(days=10)
    task.metrics.estimated_duration = 5 * 24 * 3600  # 5 days in seconds
    
    # Detect unachievable goals
    unachievable = await goal_manager.detect_unachievable_goals()
    
    assert len(unachievable) > 0
    assert any(
        u["goal_id"] == task.goal_id and
        (u["reason"] == "Blocked dependencies" or
         u["reason"] == "Missing capabilities")
        for u in unachievable
    )

@pytest.mark.asyncio
async def test_alternative_suggestions(goal_manager, sample_project_goal):
    """Test alternative approach suggestions."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create a completed similar goal
    completed_goal = await goal_manager.create_goal(
        description="Build agent system",
        goal_type=GoalType.PROJECT,
        metadata={"approach": "microservices"}
    )
    completed_goal.status = GoalStatus.COMPLETED
    
    # Get alternative suggestions
    alternatives = await goal_manager.suggest_alternatives(sample_project_goal.goal_id)
    
    assert len(alternatives) > 0
    assert all(
        "goal_id" in alt and
        "description" in alt and
        "success_rate" in alt and
        "approach" in alt
        for alt in alternatives
    )

@pytest.mark.asyncio
async def test_clarification_requests(goal_manager, sample_project_goal):
    """Test generation of clarification requests."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create a task with missing information
    task = await goal_manager.create_goal(
        description="Implement feature X",
        goal_type=GoalType.TASK,
        parent_id=sample_project_goal.goal_id,
        required_capabilities={"special_skill"},
        dependencies={"unknown_dependency"}
    )
    
    # Get clarification requests
    requests = await goal_manager.request_clarification(task.goal_id)
    
    assert len(requests) > 0
    assert any("user intentions" in req.lower() for req in requests)
    assert any("dependencies" in req.lower() for req in requests)
    assert any("capabilities" in req.lower() for req in requests)

@pytest.mark.asyncio
async def test_goal_hierarchy_progress(goal_manager, sample_project_goal):
    """Test progress propagation through goal hierarchy."""
    # Add project goal to manager
    goal_manager.goals[sample_project_goal.goal_id] = sample_project_goal
    
    # Create milestone
    milestone = await goal_manager.create_goal(
        description="Development Phase",
        goal_type=GoalType.MILESTONE,
        parent_id=sample_project_goal.goal_id
    )
    
    # Create and complete tasks
    tasks = []
    for i in range(3):
        task = await goal_manager.create_goal(
            description=f"Task {i}",
            goal_type=GoalType.TASK,
            parent_id=milestone.goal_id
        )
        tasks.append(task)
        
        # Update task progress
        await goal_manager.update_goal_progress(
            goal_id=task.goal_id,
            progress=1.0,
            agent_id=f"agent_{i}",
            context={"phase": "development"}
        )
    
    # Check milestone progress
    assert milestone.metrics.progress == 1.0
    assert milestone.status == GoalStatus.COMPLETED
    
    # Check project progress
    assert sample_project_goal.metrics.progress > 0
    assert sample_project_goal.status == GoalStatus.IN_PROGRESS 