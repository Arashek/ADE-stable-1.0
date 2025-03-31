import pytest
import asyncio
from datetime import datetime, timedelta
from production.src.core.reasoning import (
    AdvancedReasoning, ReasoningType, ReasoningOutput,
    Plan, Subgoal, PlanStatus
)
from production.src.core.collaboration import (
    CollaborativePlanning, Collaboration, AgentRole,
    CollaborationStatus
)

@pytest.fixture
async def reasoning():
    reasoning = AdvancedReasoning()
    yield reasoning

@pytest.fixture
async def collaboration():
    collaboration = CollaborativePlanning()
    yield collaboration

@pytest.fixture
def sample_plan():
    return Plan(
        plan_id="test_plan",
        goal="Test goal",
        subgoals=[
            Subgoal(
                goal_id="subgoal_1",
                description="Initial analysis",
                required_capabilities={"analysis", "planning"},
                estimated_duration=30.0,
                priority=1
            ),
            Subgoal(
                goal_id="subgoal_2",
                description="Implementation",
                required_capabilities={"implementation", "coding"},
                estimated_duration=60.0,
                priority=2
            )
        ],
        dependencies={
            "subgoal_1": set(),
            "subgoal_2": {"subgoal_1"}
        },
        created_by="test_agent"
    )

@pytest.mark.asyncio
async def test_reasoning(reasoning):
    """Test basic reasoning capabilities."""
    # Test analytical reasoning
    output = await reasoning.perform_reasoning(
        query="Should we implement feature X?",
        reasoning_type=ReasoningType.ANALYTICAL,
        context={"feature": "X", "complexity": "high"}
    )
    
    assert output is not None
    assert isinstance(output, ReasoningOutput)
    assert output.confidence > 0
    assert len(output.steps) > 0
    assert len(output.alternatives) > 0

    # Test creative reasoning
    output = await reasoning.perform_reasoning(
        query="Generate innovative solution for problem Y",
        reasoning_type=ReasoningType.CREATIVE,
        context={"problem": "Y", "constraints": ["time", "resources"]}
    )
    
    assert output is not None
    assert output.confidence > 0
    assert len(output.alternatives) > 0

@pytest.mark.asyncio
async def test_plan_creation(reasoning):
    """Test plan creation and validation."""
    # Create plan
    plan = await reasoning.create_plan(
        goal="Implement new feature",
        agent_id="test_agent",
        capabilities={"planning", "implementation", "testing"},
        context={"priority": "high", "deadline": "2 days"}
    )
    
    assert plan is not None
    assert plan.plan_id is not None
    assert len(plan.subgoals) > 0
    assert plan.status == PlanStatus.DRAFT

    # Validate plan
    success = await reasoning.validate_plan(plan.plan_id)
    assert success is True
    assert plan.status == PlanStatus.VALIDATED

@pytest.mark.asyncio
async def test_plan_adaptation(reasoning, sample_plan):
    """Test plan adaptation capabilities."""
    # Add plan to active plans
    reasoning.active_plans[sample_plan.plan_id] = sample_plan
    
    # Adapt plan
    adapted_plan = await reasoning.adapt_plan(
        plan_id=sample_plan.plan_id,
        changes={
            "new_requirement": "Add security checks",
            "modified_subgoal": "subgoal_2"
        }
    )
    
    assert adapted_plan is not None
    assert adapted_plan.status == PlanStatus.ADAPTED
    assert "adaptations" in adapted_plan.metadata

@pytest.mark.asyncio
async def test_recovery_plan(reasoning, sample_plan):
    """Test recovery plan creation."""
    # Add plan to active plans
    reasoning.active_plans[sample_plan.plan_id] = sample_plan
    
    # Create recovery plan
    recovery_subgoals = await reasoning.create_recovery_plan(
        plan_id=sample_plan.plan_id,
        failed_subgoal_id="subgoal_2"
    )
    
    assert recovery_subgoals is not None
    assert len(recovery_subgoals) > 0
    assert all(sg.description.startswith("Analyze") or sg.description.startswith("Implement")
              for sg in recovery_subgoals)

@pytest.mark.asyncio
async def test_performance_evaluation(reasoning, sample_plan):
    """Test agent performance evaluation."""
    # Add plan to history
    reasoning.plan_history["test_agent"] = [sample_plan]
    
    # Evaluate performance
    metrics = await reasoning.evaluate_performance(
        agent_id="test_agent",
        time_period=datetime.now() - timedelta(days=1)
    )
    
    assert metrics is not None
    assert "total_plans" in metrics
    assert "success_rate" in metrics
    assert "failure_patterns" in metrics

@pytest.mark.asyncio
async def test_collaboration_initiation(collaboration, sample_plan):
    """Test collaboration initiation and role assignment."""
    # Initiate collaboration
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "coordination"},
            "agent2": {"implementation", "testing"}
        }
    )
    
    assert collab is not None
    assert collab.collaboration_id is not None
    assert len(collab.agents) == 2
    
    # Assign roles
    success = await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    assert success is True
    
    # Verify role assignments
    assert collab.agents["agent1"].role in ["coordinator", "planner"]
    assert collab.agents["agent2"].role in ["implementer", "reviewer"]

@pytest.mark.asyncio
async def test_collaboration_progress(collaboration, sample_plan):
    """Test collaboration progress tracking."""
    # Initiate collaboration
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={"agent1": {"planning", "implementation"}}
    )
    
    # Update progress
    success = await collaboration.update_progress(
        collaboration_id=collab.collaboration_id,
        agent_id="agent1",
        subgoal_id="subgoal_1",
        progress=0.5
    )
    
    assert success is True
    assert collab.progress["subgoal_1"] == 0.5
    assert collab.agents["agent1"].last_update is not None

@pytest.mark.asyncio
async def test_conflict_detection(collaboration, sample_plan):
    """Test conflict detection in collaboration."""
    # Initiate collaboration with multiple agents
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "implementation"},
            "agent2": {"planning", "implementation"}
        }
    )
    
    # Assign roles
    await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    
    # Update progress for same subgoal by different agents
    await collaboration.update_progress(
        collaboration_id=collab.collaboration_id,
        agent_id="agent1",
        subgoal_id="subgoal_1",
        progress=0.5
    )
    
    await collaboration.update_progress(
        collaboration_id=collab.collaboration_id,
        agent_id="agent2",
        subgoal_id="subgoal_1",
        progress=0.7
    )
    
    # Check for conflicts
    assert len(collab.conflicts) > 0
    assert any(c["type"] == "resource_conflict" for c in collab.conflicts)

@pytest.mark.asyncio
async def test_conflict_resolution(collaboration, sample_plan):
    """Test conflict resolution in collaboration."""
    # Initiate collaboration and create conflict
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "implementation"},
            "agent2": {"planning", "implementation"}
        }
    )
    
    await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    
    # Create a conflict
    conflict = {
        "id": "conflict_1",
        "type": "resource_conflict",
        "subgoal_id": "subgoal_1",
        "agents": ["agent1", "agent2"],
        "timestamp": datetime.now().isoformat()
    }
    collab.conflicts.append(conflict)
    
    # Resolve conflict
    success = await collaboration.resolve_conflict(
        collaboration_id=collab.collaboration_id,
        conflict_id="conflict_1",
        resolution={"decision": "agent1_handles", "reason": "primary_assignee"}
    )
    
    assert success is True
    assert "resolution" in collab.conflicts[0]
    assert "resolved_at" in collab.conflicts[0]

@pytest.mark.asyncio
async def test_progress_synchronization(collaboration, sample_plan):
    """Test progress synchronization across agents."""
    # Initiate collaboration
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "implementation"},
            "agent2": {"planning", "implementation"}
        }
    )
    
    await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    
    # Update progress for different subgoals
    await collaboration.update_progress(
        collaboration_id=collab.collaboration_id,
        agent_id="agent1",
        subgoal_id="subgoal_1",
        progress=0.5
    )
    
    await collaboration.update_progress(
        collaboration_id=collab.collaboration_id,
        agent_id="agent2",
        subgoal_id="subgoal_2",
        progress=0.3
    )
    
    # Synchronize progress
    sync_data = await collaboration.synchronize_progress(collab.collaboration_id)
    
    assert sync_data is not None
    assert "overall_progress" in sync_data
    assert "active_agents" in sync_data
    assert "conflicts" in sync_data 

@pytest.mark.asyncio
async def test_complex_reasoning(reasoning):
    """Test complex reasoning scenarios with multiple steps and dependencies."""
    # Test critical reasoning with multiple factors
    output = await reasoning.perform_reasoning(
        query="Evaluate system architecture for scalability",
        reasoning_type=ReasoningType.CRITICAL,
        context={
            "current_architecture": "monolithic",
            "expected_load": "high",
            "constraints": ["budget", "time", "maintenance"],
            "requirements": ["scalability", "reliability", "security"]
        }
    )
    
    assert output is not None
    assert len(output.steps) >= 3  # Should have multiple reasoning steps
    assert all(step.confidence > 0.5 for step in output.steps)
    assert len(output.verification_results) > 0

    # Test metacognitive reasoning
    output = await reasoning.perform_reasoning(
        query="Evaluate my decision-making process",
        reasoning_type=ReasoningType.METACOGNITIVE,
        context={
            "previous_decisions": ["decision1", "decision2"],
            "success_rate": 0.8,
            "areas_for_improvement": ["speed", "accuracy"]
        }
    )
    
    assert output is not None
    assert output.confidence > 0
    assert "self_evaluation" in output.metadata

@pytest.mark.asyncio
async def test_plan_validation_edge_cases(reasoning):
    """Test plan validation with various edge cases."""
    # Test plan with circular dependencies
    circular_plan = Plan(
        plan_id="circular_plan",
        goal="Test circular dependencies",
        subgoals=[
            Subgoal(
                goal_id="subgoal_1",
                description="First step",
                required_capabilities={"analysis"},
                estimated_duration=30.0,
                priority=1
            ),
            Subgoal(
                goal_id="subgoal_2",
                description="Second step",
                required_capabilities={"implementation"},
                estimated_duration=60.0,
                priority=2
            )
        ],
        dependencies={
            "subgoal_1": {"subgoal_2"},
            "subgoal_2": {"subgoal_1"}
        },
        created_by="test_agent"
    )
    
    reasoning.active_plans[circular_plan.plan_id] = circular_plan
    success = await reasoning.validate_plan(circular_plan.plan_id)
    assert success is False  # Should fail due to circular dependencies

    # Test plan with missing capabilities
    missing_cap_plan = Plan(
        plan_id="missing_cap_plan",
        goal="Test missing capabilities",
        subgoals=[
            Subgoal(
                goal_id="subgoal_1",
                description="Specialized task",
                required_capabilities={"special_skill"},
                estimated_duration=30.0,
                priority=1
            )
        ],
        dependencies={"subgoal_1": set()},
        created_by="test_agent"
    )
    
    reasoning.active_plans[missing_cap_plan.plan_id] = missing_cap_plan
    success = await reasoning.validate_plan(missing_cap_plan.plan_id)
    assert success is False  # Should fail due to missing capabilities

@pytest.mark.asyncio
async def test_advanced_collaboration_scenarios(collaboration, sample_plan):
    """Test advanced collaboration scenarios."""
    # Test multi-agent collaboration with role transitions
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "coordination", "implementation"},
            "agent2": {"implementation", "testing", "review"},
            "agent3": {"planning", "review", "coordination"}
        }
    )
    
    # Assign initial roles
    await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    
    # Simulate role transition
    collab.agents["agent1"].role = "reviewer"
    collab.agents["agent2"].role = "coordinator"
    collab.agents["agent3"].role = "implementer"
    
    # Update progress for all agents
    for agent_id in collab.agents:
        await collaboration.update_progress(
            collaboration_id=collab.collaboration_id,
            agent_id=agent_id,
            subgoal_id="subgoal_1",
            progress=0.5
        )
    
    # Verify role transitions and progress
    assert collab.agents["agent1"].role == "reviewer"
    assert collab.agents["agent2"].role == "coordinator"
    assert collab.agents["agent3"].role == "implementer"
    assert all(progress == 0.5 for progress in collab.progress.values())

@pytest.mark.asyncio
async def test_error_handling_and_recovery(reasoning, sample_plan):
    """Test error handling and recovery mechanisms."""
    # Test recovery plan creation for multiple failures
    reasoning.active_plans[sample_plan.plan_id] = sample_plan
    
    # Create recovery plans for multiple subgoals
    recovery_plans = {}
    for subgoal_id in ["subgoal_1", "subgoal_2"]:
        recovery_subgoals = await reasoning.create_recovery_plan(
            plan_id=sample_plan.plan_id,
            failed_subgoal_id=subgoal_id
        )
        recovery_plans[subgoal_id] = recovery_subgoals
    
    assert len(recovery_plans) == 2
    assert all(len(subgoals) > 0 for subgoals in recovery_plans.values())
    
    # Test plan adaptation after multiple failures
    adapted_plan = await reasoning.adapt_plan(
        plan_id=sample_plan.plan_id,
        changes={
            "failed_subgoals": ["subgoal_1", "subgoal_2"],
            "recovery_strategy": "parallel_execution",
            "resource_allocation": "increased"
        }
    )
    
    assert adapted_plan is not None
    assert adapted_plan.status == PlanStatus.ADAPTED
    assert "recovery_strategy" in adapted_plan.metadata

@pytest.mark.asyncio
async def test_performance_monitoring(reasoning, sample_plan):
    """Test performance monitoring and metrics collection."""
    # Add multiple plans to history with different statuses
    reasoning.plan_history["test_agent"] = [
        Plan(
            plan_id=f"plan_{i}",
            goal=f"Test goal {i}",
            subgoals=[sample_plan.subgoals[0]],
            dependencies={},
            created_by="test_agent",
            status=status
        )
        for i, status in enumerate([
            PlanStatus.COMPLETED,
            PlanStatus.FAILED,
            PlanStatus.ADAPTED,
            PlanStatus.ACTIVE
        ])
    ]
    
    # Evaluate performance over different time periods
    metrics = await reasoning.evaluate_performance(
        agent_id="test_agent",
        time_period=datetime.now() - timedelta(days=7)
    )
    
    assert metrics is not None
    assert metrics["total_plans"] == 4
    assert metrics["completed_plans"] == 1
    assert metrics["failed_plans"] == 1
    assert metrics["adapted_plans"] == 1
    assert metrics["success_rate"] == 0.25
    
    # Test performance evaluation with no plans
    empty_metrics = await reasoning.evaluate_performance(
        agent_id="empty_agent",
        time_period=datetime.now() - timedelta(days=1)
    )
    
    assert empty_metrics == {}

@pytest.mark.asyncio
async def test_collaboration_conflict_resolution_strategies(collaboration, sample_plan):
    """Test different conflict resolution strategies in collaboration."""
    # Initiate collaboration with potential conflicts
    collab = await collaboration.initiate_collaboration(
        plan_id=sample_plan.plan_id,
        agents={
            "agent1": {"planning", "implementation"},
            "agent2": {"implementation", "testing"},
            "agent3": {"planning", "testing"}
        }
    )
    
    await collaboration.assign_roles(collab.collaboration_id, sample_plan)
    
    # Create multiple types of conflicts
    conflicts = [
        {
            "id": "conflict_1",
            "type": "resource_conflict",
            "subgoal_id": "subgoal_1",
            "agents": ["agent1", "agent2"],
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "conflict_2",
            "type": "dependency_conflict",
            "subgoal_id": "subgoal_2",
            "dependency_id": "subgoal_1",
            "agent_id": "agent3",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    collab.conflicts = conflicts
    
    # Test different resolution strategies
    resolutions = [
        {"decision": "agent1_handles", "reason": "primary_assignee"},
        {"decision": "split_task", "reason": "parallel_execution"},
        {"decision": "reassign", "reason": "capability_match"}
    ]
    
    for conflict, resolution in zip(conflicts, resolutions):
        success = await collaboration.resolve_conflict(
            collaboration_id=collab.collaboration_id,
            conflict_id=conflict["id"],
            resolution=resolution
        )
        assert success is True
        assert "resolution" in conflict
        assert "resolved_at" in conflict

@pytest.mark.asyncio
async def test_plan_execution_monitoring(reasoning, sample_plan):
    """Test plan execution monitoring and progress tracking."""
    # Add plan to active plans
    reasoning.active_plans[sample_plan.plan_id] = sample_plan
    
    # Simulate subgoal execution
    for subgoal in sample_plan.subgoals:
        subgoal.start_time = datetime.now()
        subgoal.progress = 0.5
        subgoal.status = "in_progress"
    
    # Test plan status updates
    assert all(sg.status == "in_progress" for sg in sample_plan.subgoals)
    assert all(sg.progress == 0.5 for sg in sample_plan.subgoals)
    
    # Simulate subgoal completion
    for subgoal in sample_plan.subgoals:
        subgoal.progress = 1.0
        subgoal.status = "completed"
        subgoal.completion_time = datetime.now()
    
    # Verify completion status
    assert all(sg.status == "completed" for sg in sample_plan.subgoals)
    assert all(sg.progress == 1.0 for sg in sample_plan.subgoals)
    assert all(sg.completion_time is not None for sg in sample_plan.subgoals) 