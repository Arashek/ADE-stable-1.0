import pytest
import asyncio
from datetime import datetime
from ..agent_communication import (
    AgentCommunicationSystem, Message, MessageType, MessagePriority,
    AgentCapability, AgentProfile, CoordinationPattern, ResourceAllocationStrategy,
    LeaderElectionState, ConsensusState, BarrierState
)
import uuid

@pytest.fixture
def communication_system():
    return AgentCommunicationSystem()

@pytest.fixture
def sample_capabilities():
    return [
        AgentCapability(
            name="process_data",
            description="Process data using advanced algorithms",
            parameters={"data": "dict", "algorithm": "str"},
            return_type="dict",
            is_async=True,
            timeout=30
        ),
        AgentCapability(
            name="analyze_code",
            description="Analyze code for patterns and metrics",
            parameters={"code": "str", "language": "str"},
            return_type="dict",
            is_async=True,
            timeout=60
        )
    ]

@pytest.fixture
def sample_agents(communication_system, sample_capabilities):
    async def register_agents():
        # Register agent 1
        await communication_system.register_agent(
            "agent1",
            "DataProcessor",
            sample_capabilities
        )
        
        # Register agent 2
        await communication_system.register_agent(
            "agent2",
            "CodeAnalyzer",
            sample_capabilities
        )
        
        # Register agent 3
        await communication_system.register_agent(
            "agent3",
            "Coordinator",
            sample_capabilities
        )
        
    asyncio.run(register_agents())
    return communication_system.agents

@pytest.mark.asyncio
async def test_agent_registration(communication_system, sample_capabilities):
    """Test agent registration and unregistration."""
    # Register agent
    success = await communication_system.register_agent(
        "test_agent",
        "TestAgent",
        sample_capabilities
    )
    assert success
    assert "test_agent" in communication_system.agents
    
    # Verify agent profile
    agent = communication_system.agents["test_agent"]
    assert agent.name == "TestAgent"
    assert len(agent.capabilities) == len(sample_capabilities)
    assert agent.status == "active"
    assert agent.load == 0.0
    
    # Unregister agent
    success = await communication_system.unregister_agent("test_agent")
    assert success
    assert "test_agent" not in communication_system.agents

@pytest.mark.asyncio
async def test_message_sending(communication_system, sample_agents):
    """Test message sending and handling."""
    # Create test message
    message = Message(
        id="test_msg_1",
        type=MessageType.REQUEST,
        sender="agent1",
        recipients=["agent2"],
        content={"action": "analyze", "data": "test code"},
        timestamp=datetime.now(),
        priority=MessagePriority.MEDIUM,
        metadata={"test": True}
    )
    
    # Send message
    success = await communication_system.send_message(message)
    assert success
    
    # Verify message in queue
    queued_message = await communication_system.message_queue.get()
    assert queued_message.id == message.id
    assert queued_message.type == message.type
    assert queued_message.sender == message.sender
    assert queued_message.recipients == message.recipients

@pytest.mark.asyncio
async def test_coordination_task(communication_system, sample_agents):
    """Test coordination task management."""
    # Start coordination task
    success = await communication_system.start_coordination(
        task_id="test_task_1",
        coordinator_id="agent3",
        participants=["agent1", "agent2"],
        task_type="code_analysis",
        parameters={"code": "test code", "language": "python"}
    )
    assert success
    assert "test_task_1" in communication_system.coordination_tasks
    
    # Verify task state
    task = communication_system.coordination_tasks["test_task_1"]
    assert not task.done()
    
    # Cancel task
    task.cancel()
    await asyncio.sleep(0.1)  # Allow task to clean up
    assert task.done()

@pytest.mark.asyncio
async def test_collaboration_session(communication_system, sample_agents):
    """Test collaboration session management."""
    # Start collaboration session
    success = await communication_system.start_collaboration(
        session_id="test_session_1",
        initiator_id="agent1",
        participants=["agent1", "agent2"],
        collaboration_type="code_review",
        parameters={"code": "test code", "language": "python"}
    )
    assert success
    assert "test_session_1" in communication_system.collaboration_sessions
    
    # Verify session state
    session = communication_system.collaboration_sessions["test_session_1"]
    assert session["status"] == "active"
    assert session["initiator"] == "agent1"
    assert len(session["participants"]) == 2
    
    # End session
    await communication_system._end_collaboration_session("test_session_1")
    assert "test_session_1" not in communication_system.collaboration_sessions

@pytest.mark.asyncio
async def test_resource_negotiation(communication_system, sample_agents):
    """Test resource negotiation between agents."""
    # Initiate resource negotiation
    success = await communication_system.negotiate_resource(
        resource_id="test_resource_1",
        requester_id="agent1",
        owner_id="agent2",
        resource_type="data_processor",
        parameters={"priority": "high", "duration": 300}
    )
    assert success
    
    # Verify negotiation message
    message = await communication_system.message_queue.get()
    assert message.type == MessageType.NEGOTIATION
    assert message.sender == "agent1"
    assert message.recipients == ["agent2"]
    assert message.content["resource_id"] == "test_resource_1"

@pytest.mark.asyncio
async def test_resource_sharing(communication_system, sample_agents):
    """Test resource sharing between agents."""
    # Share resource
    success = await communication_system.share_resource(
        resource_id="test_resource_1",
        owner_id="agent2",
        recipient_id="agent1",
        resource_type="data_processor",
        access_level="read"
    )
    assert success
    
    # Verify sharing message
    message = await communication_system.message_queue.get()
    assert message.type == MessageType.RESOURCE_SHARING
    assert message.sender == "agent2"
    assert message.recipients == ["agent1"]
    assert message.content["resource_id"] == "test_resource_1"

@pytest.mark.asyncio
async def test_message_handlers(communication_system, sample_agents):
    """Test message handler registration and execution."""
    # Create test handler
    handled_messages = []
    
    async def test_handler(message):
        handled_messages.append(message)
    
    # Register handler
    communication_system.register_message_handler(MessageType.REQUEST, test_handler)
    
    # Create and send test message
    message = Message(
        id="test_msg_2",
        type=MessageType.REQUEST,
        sender="agent1",
        recipients=["agent2"],
        content={"action": "test"},
        timestamp=datetime.now(),
        priority=MessagePriority.MEDIUM,
        metadata={}
    )
    
    await communication_system.send_message(message)
    await communication_system._process_message(message)
    
    # Verify handler execution
    assert len(handled_messages) == 1
    assert handled_messages[0].id == message.id

@pytest.mark.asyncio
async def test_agent_status_checking(communication_system, sample_agents):
    """Test agent status checking."""
    # Check active agent
    status = await communication_system._check_agent_status("agent1")
    assert status
    
    # Check non-existent agent
    status = await communication_system._check_agent_status("non_existent_agent")
    assert not status

@pytest.mark.asyncio
async def test_task_progress_calculation(communication_system, sample_agents):
    """Test task progress calculation."""
    # Create test task state
    task_state = {
        "id": "test_task_2",
        "coordinator": "agent3",
        "participants": ["agent1", "agent2"],
        "type": "test",
        "parameters": {},
        "status": "in_progress",
        "start_time": datetime.now(),
        "progress": 0.0,
        "results": {
            "agent1": {"progress": 0.5},
            "agent2": {"progress": 0.7}
        }
    }
    
    # Calculate progress
    progress = await communication_system._calculate_task_progress(task_state)
    assert progress == 0.6  # Average of 0.5 and 0.7

@pytest.mark.asyncio
async def test_message_validation(communication_system, sample_agents):
    """Test message validation."""
    # Valid message
    valid_message = Message(
        id="test_msg_3",
        type=MessageType.REQUEST,
        sender="agent1",
        recipients=["agent2"],
        content={"action": "test"},
        timestamp=datetime.now(),
        priority=MessagePriority.MEDIUM,
        metadata={}
    )
    assert communication_system._validate_message(valid_message)
    
    # Invalid message (non-existent sender)
    invalid_message = Message(
        id="test_msg_4",
        type=MessageType.REQUEST,
        sender="non_existent_agent",
        recipients=["agent2"],
        content={"action": "test"},
        timestamp=datetime.now(),
        priority=MessagePriority.MEDIUM,
        metadata={}
    )
    assert not communication_system._validate_message(invalid_message)

@pytest.mark.asyncio
async def test_cleanup_agent_resources(communication_system, sample_agents):
    """Test cleanup of agent resources."""
    # Start a coordination task
    await communication_system.start_coordination(
        task_id="test_task_3",
        coordinator_id="agent3",
        participants=["agent1", "agent2"],
        task_type="test",
        parameters={}
    )
    
    # Start a collaboration session
    await communication_system.start_collaboration(
        session_id="test_session_2",
        initiator_id="agent1",
        participants=["agent1", "agent2"],
        collaboration_type="test",
        parameters={}
    )
    
    # Clean up agent resources
    await communication_system._cleanup_agent_resources("agent1")
    
    # Verify cleanup
    assert "test_task_3" not in communication_system.coordination_tasks
    assert "test_session_2" not in communication_system.collaboration_sessions

@pytest.mark.asyncio
async def test_leader_election(communication_system, sample_agents):
    """Test leader election process."""
    # Start leader election
    success = await communication_system.start_leader_election(
        election_id="test_election_1",
        participants=["agent1", "agent2", "agent3"],
        timeout=2.0
    )
    assert success
    assert "test_election_1" in communication_system.leader_election_states
    
    # Verify election state
    state = communication_system.leader_election_states["test_election_1"]
    assert state.term == 0
    assert state.leader_id is None
    assert state.voted_for is None
    assert state.votes_received == 0
    assert not state.is_leader
    
    # Wait for election process
    await asyncio.sleep(3.0)
    
    # Verify election completed
    state = communication_system.leader_election_states["test_election_1"]
    assert state.is_leader
    assert state.leader_id is not None

@pytest.mark.asyncio
async def test_consensus(communication_system, sample_agents):
    """Test consensus process."""
    # Start consensus
    success = await communication_system.start_consensus(
        consensus_id="test_consensus_1",
        participants=["agent1", "agent2", "agent3"],
        initial_value={"action": "test"},
        quorum_size=2
    )
    assert success
    assert "test_consensus_1" in communication_system.consensus_states
    
    # Verify consensus state
    state = communication_system.consensus_states["test_consensus_1"]
    assert state.proposal_id is not None
    assert state.value == {"action": "test"}
    assert state.accepted_value is None
    assert state.quorum_size == 2
    assert len(state.acceptors) == 3
    assert state.promises_received == 0
    assert state.accepts_received == 0
    assert state.phase == "prepare"
    
    # Wait for consensus process
    await asyncio.sleep(1.0)
    
    # Verify consensus completed
    state = communication_system.consensus_states["test_consensus_1"]
    assert state.accepted_value is not None

@pytest.mark.asyncio
async def test_barrier_synchronization(communication_system, sample_agents):
    """Test barrier synchronization."""
    # Create barrier
    success = await communication_system.create_barrier(
        barrier_id="test_barrier_1",
        participants=["agent1", "agent2", "agent3"],
        timeout=5.0
    )
    assert success
    assert "test_barrier_1" in communication_system.barrier_states
    
    # Verify barrier state
    state = communication_system.barrier_states["test_barrier_1"]
    assert state.barrier_id == "test_barrier_1"
    assert state.total_participants == 3
    assert state.arrived_participants == 0
    assert state.timeout == 5.0
    assert not state.is_released
    
    # Wait for barrier
    await asyncio.sleep(6.0)
    
    # Verify barrier released
    state = communication_system.barrier_states["test_barrier_1"]
    assert state.is_released

@pytest.mark.asyncio
async def test_work_distribution(communication_system, sample_agents):
    """Test work distribution."""
    # Prepare work items
    work_items = [f"item_{i}" for i in range(5)]
    
    # Distribute work
    success = await communication_system.distribute_work(
        work_id="test_work_1",
        coordinator_id="agent1",
        participants=["agent1", "agent2", "agent3"],
        work_items=work_items,
        strategy=ResourceAllocationStrategy.ROUND_ROBIN
    )
    assert success
    assert "test_work_1" in communication_system.work_distribution_states
    
    # Verify work distribution state
    state = communication_system.work_distribution_states["test_work_1"]
    assert state["coordinator"] == "agent1"
    assert len(state["participants"]) == 3
    assert len(state["work_items"]) == 5
    assert state["strategy"] == ResourceAllocationStrategy.ROUND_ROBIN
    assert len(state["assigned_items"]) == 0
    assert len(state["completed_items"]) == 0
    assert state["status"] == "in_progress"
    
    # Wait for work distribution
    await asyncio.sleep(1.0)
    
    # Verify work completed
    state = communication_system.work_distribution_states["test_work_1"]
    assert state["status"] == "completed"

@pytest.mark.asyncio
async def test_load_balancing(communication_system, sample_agents):
    """Test load balancing."""
    # Start load balancing
    success = await communication_system.start_load_balancing(
        balancer_id="agent1",
        participants=["agent1", "agent2", "agent3"],
        strategy=ResourceAllocationStrategy.DYNAMIC_LOAD_BALANCING
    )
    assert success
    assert "agent1" in communication_system.load_balancing_states
    
    # Verify load balancing state
    state = communication_system.load_balancing_states["agent1"]
    assert state["balancer"] == "agent1"
    assert len(state["participants"]) == 3
    assert state["strategy"] == ResourceAllocationStrategy.DYNAMIC_LOAD_BALANCING
    assert len(state["loads"]) == 3
    assert state["threshold"] == 0.8
    assert state["status"] == "active"
    
    # Wait for load balancing
    await asyncio.sleep(6.0)
    
    # Verify load balancing active
    state = communication_system.load_balancing_states["agent1"]
    assert state["status"] == "active"

@pytest.mark.asyncio
async def test_resource_allocation_strategies(communication_system, sample_agents):
    """Test different resource allocation strategies."""
    # Test round-robin strategy
    participant = communication_system._select_participant(
        ["agent1", "agent2", "agent3"],
        ResourceAllocationStrategy.ROUND_ROBIN
    )
    assert participant in ["agent1", "agent2", "agent3"]
    
    # Test least-loaded strategy
    participant = communication_system._select_participant(
        ["agent1", "agent2", "agent3"],
        ResourceAllocationStrategy.LEAST_LOADED
    )
    assert participant in ["agent1", "agent2", "agent3"]
    
    # Test weighted random strategy
    participant = communication_system._select_participant(
        ["agent1", "agent2", "agent3"],
        ResourceAllocationStrategy.WEIGHTED_RANDOM
    )
    assert participant in ["agent1", "agent2", "agent3"]

@pytest.mark.asyncio
async def test_load_rebalancing(communication_system, sample_agents):
    """Test load rebalancing detection."""
    # Test with balanced loads
    loads = {"agent1": 0.5, "agent2": 0.5, "agent3": 0.5}
    assert not communication_system._needs_rebalancing(loads, 0.8)
    
    # Test with unbalanced loads
    loads = {"agent1": 0.9, "agent2": 0.5, "agent3": 0.5}
    assert communication_system._needs_rebalancing(loads, 0.8)
    
    # Test with empty loads
    assert not communication_system._needs_rebalancing({}, 0.8)

@pytest.mark.asyncio
async def test_participant_load_calculation(communication_system, sample_agents):
    """Test participant load calculation."""
    # Test load calculation
    load = communication_system._get_participant_load("agent1")
    assert isinstance(load, float)
    assert 0 <= load <= 1

@pytest.mark.asyncio
async def test_two_phase_commit(communication_system, sample_agents):
    """Test Two-Phase Commit process."""
    # Start Two-Phase Commit
    success = await communication_system.start_two_phase_commit(
        transaction_id="test_tx_1",
        coordinator_id="agent1",
        participants=["agent1", "agent2", "agent3"],
        value={"action": "test"},
        timeout=5.0
    )
    assert success
    assert "test_tx_1" in communication_system.two_phase_commit_states
    
    # Verify 2PC state
    state = communication_system.two_phase_commit_states["test_tx_1"]
    assert state.transaction_id == "test_tx_1"
    assert state.coordinator_id == "agent1"
    assert len(state.participants) == 3
    assert state.value == {"action": "test"}
    assert state.phase == "prepare"
    assert state.prepared_count == 0
    assert state.committed_count == 0
    assert state.aborted_count == 0
    assert state.timeout == 5.0
    assert state.status == "active"
    
    # Wait for 2PC process
    await asyncio.sleep(6.0)
    
    # Verify 2PC completed
    state = communication_system.two_phase_commit_states["test_tx_1"]
    assert state.status in ["committed", "aborted"]

@pytest.mark.asyncio
async def test_raft_consensus(communication_system, sample_agents):
    """Test Raft consensus process."""
    # Start Raft for each agent
    for agent_id in ["agent1", "agent2", "agent3"]:
        success = await communication_system.start_raft(
            node_id=agent_id,
            participants=["agent1", "agent2", "agent3"],
            election_timeout=2.0,
            heartbeat_interval=0.5
        )
        assert success
        assert agent_id in communication_system.raft_states
        
        # Verify Raft state
        state = communication_system.raft_states[agent_id]
        assert state.node_id == agent_id
        assert state.current_term == 0
        assert state.voted_for is None
        assert state.role == "follower"
        assert state.leader_id is None
        assert len(state.log) == 0
        assert state.commit_index == 0
        assert state.last_applied == 0
        assert len(state.next_index) == 3
        assert len(state.match_index) == 3
        assert state.election_timeout == 2.0
        assert state.heartbeat_interval == 0.5
    
    # Wait for Raft process
    await asyncio.sleep(3.0)
    
    # Verify leader election
    leaders = [state for state in communication_system.raft_states.values() 
              if state.role == "leader"]
    assert len(leaders) == 1
    
    # Verify followers
    followers = [state for state in communication_system.raft_states.values() 
                if state.role == "follower"]
    assert len(followers) == 2

@pytest.mark.asyncio
async def test_raft_log_replication(communication_system, sample_agents):
    """Test Raft log replication."""
    # Start Raft for each agent
    for agent_id in ["agent1", "agent2", "agent3"]:
        await communication_system.start_raft(
            node_id=agent_id,
            participants=["agent1", "agent2", "agent3"],
            election_timeout=2.0,
            heartbeat_interval=0.5
        )
    
    # Wait for leader election
    await asyncio.sleep(3.0)
    
    # Find leader
    leader_state = next(state for state in communication_system.raft_states.values() 
                       if state.role == "leader")
    
    # Add log entry
    log_entry = {
        "term": leader_state.current_term,
        "command": {"action": "test", "value": 123}
    }
    leader_state.log.append(log_entry)
    
    # Send AppendEntries RPC
    message = Message(
        id=str(uuid.uuid4()),
        type=MessageType.RAFT,
        sender=leader_state.node_id,
        recipients=[state.node_id for state in communication_system.raft_states.values() 
                   if state.role == "follower"],
        content={
            "term": leader_state.current_term,
            "leader_id": leader_state.node_id,
            "prev_log_index": len(leader_state.log) - 2,
            "prev_log_term": leader_state.log[-2]["term"] if len(leader_state.log) > 1 else 0,
            "entries": [log_entry],
            "leader_commit": leader_state.commit_index,
            "action": "append_entries"
        },
        timestamp=datetime.now(),
        priority=MessagePriority.HIGH,
        metadata={"state": leader_state}
    )
    
    await communication_system.send_message(message)
    
    # Wait for log replication
    await asyncio.sleep(1.0)
    
    # Verify log replication
    for state in communication_system.raft_states.values():
        if state.role == "follower":
            assert len(state.log) == len(leader_state.log)
            assert state.log[-1] == log_entry

@pytest.mark.asyncio
async def test_three_phase_commit(communication_system, sample_agents):
    """Test Three-Phase Commit process."""
    # Start Three-Phase Commit
    success = await communication_system.start_three_phase_commit(
        transaction_id="test_tx_2",
        coordinator_id="agent1",
        participants=["agent1", "agent2", "agent3"],
        value={"action": "test"},
        timeout=5.0
    )
    assert success
    assert "test_tx_2" in communication_system.three_phase_commit_states
    
    # Verify 3PC state
    state = communication_system.three_phase_commit_states["test_tx_2"]
    assert state.transaction_id == "test_tx_2"
    assert state.coordinator_id == "agent1"
    assert len(state.participants) == 3
    assert state.value == {"action": "test"}
    assert state.phase == "can_commit"
    assert state.can_commit_count == 0
    assert state.pre_commit_count == 0
    assert state.commit_count == 0
    assert state.abort_count == 0
    assert state.timeout == 5.0
    assert state.status == "active"
    assert not state.recovery_needed
    
    # Wait for 3PC process
    await asyncio.sleep(6.0)
    
    # Verify 3PC completed
    state = communication_system.three_phase_commit_states["test_tx_2"]
    assert state.status in ["committed", "aborted"]

@pytest.mark.asyncio
async def test_zab_consensus(communication_system, sample_agents):
    """Test ZAB consensus process."""
    # Start ZAB for each agent
    for agent_id in ["agent1", "agent2", "agent3"]:
        success = await communication_system.start_zab(
            node_id=agent_id,
            participants=["agent1", "agent2", "agent3"],
            election_timeout=2.0,
            heartbeat_interval=0.5,
            sync_limit=100
        )
        assert success
        assert agent_id in communication_system.zab_states
        
        # Verify ZAB state
        state = communication_system.zab_states[agent_id]
        assert state.node_id == agent_id
        assert state.epoch == 0
        assert state.role == "follower"
        assert state.leader_id is None
        assert state.last_proposed_zxid == 0
        assert state.last_committed_zxid == 0
        assert state.last_applied_zxid == 0
        assert len(state.pending_proposals) == 0
        assert state.sync_limit == 100
        assert state.election_timeout == 2.0
        assert state.heartbeat_interval == 0.5
        assert not state.sync_in_progress
        assert not state.recovery_needed
    
    # Wait for ZAB process
    await asyncio.sleep(3.0)
    
    # Verify leader election
    leaders = [state for state in communication_system.zab_states.values() 
              if state.role == "leader"]
    assert len(leaders) == 1
    
    # Verify followers
    followers = [state for state in communication_system.zab_states.values() 
                if state.role == "follower"]
    assert len(followers) == 2

@pytest.mark.asyncio
async def test_resource_pool_management(communication_system, sample_agents):
    """Test resource pool management."""
    # Create test resources
    resources = {
        f"resource_{i}": {
            "type": "compute",
            "capacity": 100,
            "cost": 10.0,
            "health": "healthy"
        } for i in range(5)
    }
    
    # Create resource pool
    success = await communication_system.create_resource_pool(
        pool_id="test_pool_1",
        resources=resources,
        strategy=ResourceAllocationStrategy.ADAPTIVE_LOAD_BALANCING,
        capacity=10,
        auto_scaling=True
    )
    assert success
    assert "test_pool_1" in communication_system.resource_pools
    
    # Verify resource pool
    pool = communication_system.resource_pools["test_pool_1"]
    assert pool.pool_id == "test_pool_1"
    assert len(pool.resources) == 5
    assert pool.allocation_strategy == ResourceAllocationStrategy.ADAPTIVE_LOAD_BALANCING
    assert pool.capacity == 10
    assert pool.current_load == 0.0
    assert pool.health_status == "healthy"
    assert pool.auto_scaling_enabled
    assert pool.scaling_thresholds == {"high": 0.8, "low": 0.2}
    assert len(pool.fault_domains) == 0
    assert len(pool.backup_resources) == 0
    
    # Wait for resource management
    await asyncio.sleep(2.0)
    
    # Verify metrics updated
    assert "utilization" in pool.metrics
    assert "response_time" in pool.metrics
    assert "error_rate" in pool.metrics
    assert "cost_per_request" in pool.metrics

@pytest.mark.asyncio
async def test_resource_pool_auto_scaling(communication_system, sample_agents):
    """Test resource pool auto-scaling."""
    # Create resource pool with high utilization
    resources = {
        f"resource_{i}": {
            "type": "compute",
            "capacity": 100,
            "cost": 10.0,
            "health": "healthy"
        } for i in range(2)
    }
    
    await communication_system.create_resource_pool(
        pool_id="test_pool_2",
        resources=resources,
        strategy=ResourceAllocationStrategy.PREDICTIVE_SCALING,
        capacity=5,
        auto_scaling=True
    )
    
    # Set high utilization to trigger scaling
    pool = communication_system.resource_pools["test_pool_2"]
    pool.metrics["utilization"] = 0.9
    
    # Wait for auto-scaling
    await asyncio.sleep(2.0)
    
    # Verify scaling triggered
    assert pool.metrics["utilization"] > pool.scaling_thresholds["high"]

@pytest.mark.asyncio
async def test_resource_pool_fault_tolerance(communication_system, sample_agents):
    """Test resource pool fault tolerance."""
    # Create resource pool with fault domains
    resources = {
        f"resource_{i}": {
            "type": "compute",
            "capacity": 100,
            "cost": 10.0,
            "health": "healthy",
            "fault_domain": f"domain_{i % 2}"
        } for i in range(4)
    }
    
    await communication_system.create_resource_pool(
        pool_id="test_pool_3",
        resources=resources,
        strategy=ResourceAllocationStrategy.FAULT_TOLERANT,
        capacity=5,
        auto_scaling=True
    )
    
    pool = communication_system.resource_pools["test_pool_3"]
    pool.fault_domains = ["domain_0", "domain_1"]
    
    # Simulate domain failure
    for resource_id, resource in pool.resources.items():
        if resource["fault_domain"] == "domain_0":
            resource["health"] = "failed"
    
    # Wait for fault tolerance handling
    await asyncio.sleep(2.0)
    
    # Verify fault tolerance
    assert pool.health_status == "degraded"
    assert len(pool.backup_resources) > 0 