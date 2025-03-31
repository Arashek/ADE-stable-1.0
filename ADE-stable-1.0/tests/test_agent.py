import unittest
import threading
import time
from datetime import datetime
from production.src.core.agent import Agent, AgentState
from production.src.core.agent_communication import Message, MessageType
import pytest
import logging
from src.core.error.retry_policy import RetryManager, RetryPolicy, RetryStrategy
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer

class TestAgent(Agent):
    """Test implementation of Agent class."""
    
    def _process_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Process a test task."""
        # Simulate task processing
        time.sleep(0.1)
        self.complete_task(task_id, True, {"result": "success"})

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.agent = TestAgent(
            agent_id="test_agent",
            name="Test Agent",
            capabilities=["test_capability"],
            config_path=None
        )
        
        # Track received messages
        self.received_messages = []
        
        # Register message handler for testing
        self.agent.comm_system.register_handler(
            "test_agent",
            MessageType.NOTIFICATION,
            self._handle_notification
        )

    def tearDown(self):
        """Clean up test fixtures."""
        if self.agent.is_active:
            self.agent.stop()
        self.agent.comm_system.unregister_agent(self.agent.agent_id)

    def _handle_notification(self, message: Message):
        """Handle notification messages for testing."""
        self.received_messages.append(message)

    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.capabilities, ["test_capability"])
        self.assertFalse(self.agent.is_active)
        self.assertEqual(self.agent.state.status, "initialized")

    def test_agent_start_stop(self):
        """Test agent start and stop functionality."""
        # Test start
        self.assertTrue(self.agent.start())
        self.assertTrue(self.agent.is_active)
        self.assertEqual(self.agent.state.status, "active")
        
        # Test duplicate start
        self.assertFalse(self.agent.start())
        
        # Test stop
        self.assertTrue(self.agent.stop())
        self.assertFalse(self.agent.is_active)
        self.assertEqual(self.agent.state.status, "stopped")
        
        # Test duplicate stop
        self.assertFalse(self.agent.stop())

    def test_task_assignment(self):
        """Test task assignment and processing."""
        # Start agent
        self.agent.start()
        
        # Test valid task
        task_data = {
            "task_id": "test_task",
            "required_capabilities": ["test_capability"]
        }
        self.assertTrue(self.agent.assign_task("test_task", task_data))
        
        # Wait for task completion
        time.sleep(0.2)
        
        # Verify task completion
        self.assertIsNone(self.agent.state.current_task)
        self.assertEqual(self.agent.metrics["tasks_completed"], 1)

    def test_task_rejection(self):
        """Test task rejection for invalid capabilities."""
        # Start agent
        self.agent.start()
        
        # Test task with invalid capabilities
        task_data = {
            "task_id": "test_task",
            "required_capabilities": ["invalid_capability"]
        }
        self.assertFalse(self.agent.assign_task("test_task", task_data))
        
        # Verify no task was assigned
        self.assertIsNone(self.agent.state.current_task)
        self.assertEqual(self.agent.metrics["tasks_completed"], 0)

    def test_capability_update(self):
        """Test capability updates."""
        # Start agent
        self.agent.start()
        
        # Update capabilities
        new_capabilities = ["test_capability", "new_capability"]
        self.assertTrue(self.agent.update_capabilities(new_capabilities))
        
        # Verify update
        self.assertEqual(self.agent.state.capabilities, new_capabilities)
        
        # Check status broadcast
        status_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and "capabilities" in msg.content
        ]
        self.assertTrue(len(status_messages) > 0)
        self.assertEqual(status_messages[-1].content["capabilities"], new_capabilities)

    def test_error_handling(self):
        """Test error handling and broadcasting."""
        # Start agent
        self.agent.start()
        
        # Trigger error
        try:
            raise ValueError("Test error")
        except Exception as e:
            self.agent._handle_error(e, "test_context")
        
        # Verify error metrics
        self.assertEqual(self.agent.state.error_count, 1)
        self.assertIsNotNone(self.agent.metrics["last_error"])
        
        # Check error broadcast
        error_messages = [
            msg for msg in self.received_messages
            if msg.message_type == MessageType.NOTIFICATION
            and "error" in msg.content
        ]
        self.assertTrue(len(error_messages) > 0)
        self.assertEqual(error_messages[-1].content["error"], "Test error")

    def test_state_management(self):
        """Test agent state management."""
        # Start agent
        self.agent.start()
        
        # Get initial state
        initial_state = self.agent.get_state()
        self.assertEqual(initial_state["status"], "active")
        self.assertEqual(initial_state["error_count"], 0)
        self.assertEqual(initial_state["success_count"], 0)
        
        # Complete a task
        self.agent.assign_task("test_task", {"task_id": "test_task"})
        time.sleep(0.2)
        
        # Get updated state
        updated_state = self.agent.get_state()
        self.assertEqual(updated_state["success_count"], 1)
        self.assertEqual(updated_state["total_tasks"], 1)

    def test_metrics_tracking(self):
        """Test metrics tracking."""
        # Start agent
        self.agent.start()
        
        # Complete multiple tasks
        for i in range(3):
            self.agent.assign_task(f"task_{i}", {"task_id": f"task_{i}"})
            time.sleep(0.2)
        
        # Verify metrics
        metrics = self.agent.get_metrics()
        self.assertEqual(metrics["tasks_completed"], 3)
        self.assertEqual(metrics["tasks_failed"], 0)
        self.assertIsNotNone(metrics["last_success"])

    def test_message_handling(self):
        """Test message handling system."""
        # Start agent
        self.agent.start()
        
        # Send test message
        test_message = Message(
            message_id="test_msg",
            sender_id="other_agent",
            receiver_id=self.agent.agent_id,
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        self.agent.comm_system.send_message(test_message)
        
        # Process messages
        self.agent.comm_system.process_messages(self.agent.agent_id)
        
        # Verify message handling
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0].message_id, "test_msg")

@pytest.fixture
def retry_manager():
    return RetryManager()

@pytest.fixture
def error_detector():
    return ErrorDetector()

@pytest.fixture
def root_cause_analyzer():
    return RootCauseAnalyzer()

@pytest.fixture
def agent(retry_manager, error_detector, root_cause_analyzer):
    return Agent(
        name="test_agent",
        retry_manager=retry_manager,
        error_detector=error_detector,
        root_cause_analyzer=root_cause_analyzer
    )

def test_agent_initialization(agent):
    """Test agent initialization"""
    assert agent.name == "test_agent"
    assert isinstance(agent.retry_manager, RetryManager)
    assert isinstance(agent.error_detector, ErrorDetector)
    assert isinstance(agent.root_cause_analyzer, RootCauseAnalyzer)
    assert isinstance(agent.logger, logging.Logger)

def test_default_retry_policy(agent):
    """Test default retry policy setup"""
    policy = agent.retry_manager.get_policy("test_agent_default")
    assert policy is not None
    assert policy.max_attempts == 3
    assert policy.strategy == RetryStrategy.EXPONENTIAL
    assert policy.initial_delay == 1.0
    assert policy.max_delay == 5.0
    assert policy.jitter is True

def test_successful_operation(agent):
    """Test successful operation execution"""
    def operation():
        return "success"
    
    result = agent.execute_with_retry(operation)
    assert result == "success"

def test_failing_operation(agent):
    """Test operation that fails after retries"""
    attempt_count = 0
    def operation():
        nonlocal attempt_count
        attempt_count += 1
        raise ValueError("operation failed")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(operation)
    
    assert attempt_count == 3  # Should try 3 times

def test_successful_retry(agent):
    """Test operation that succeeds after retries"""
    attempt_count = 0
    def operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("operation failed")
        return "success"
    
    result = agent.execute_with_retry(operation)
    assert result == "success"
    assert attempt_count == 3

def test_custom_retry_policy(agent):
    """Test using custom retry policy"""
    custom_policy = RetryPolicy(
        name="custom",
        max_attempts=2,
        strategy=RetryStrategy.LINEAR,
        initial_delay=0.5,
        max_delay=2.0
    )
    agent.retry_manager.add_policy("custom", custom_policy)
    
    attempt_count = 0
    def operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise ValueError("operation failed")
        return "success"
    
    result = agent.execute_with_retry(operation, retry_policy_name="custom")
    assert result == "success"
    assert attempt_count == 2

def test_error_detection(agent):
    """Test error detection during operation"""
    def operation():
        raise ValueError("test error")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(operation)
    
    error_history = agent.get_error_history()
    assert len(error_history) > 0
    assert error_history[-1]["error_type"] == "ValueError"
    assert "test error" in error_history[-1]["error_message"]

def test_root_cause_analysis(agent):
    """Test root cause analysis during operation"""
    def operation():
        raise RuntimeError("database connection timeout")
    
    with pytest.raises(RuntimeError):
        agent.execute_with_retry(operation)
    
    # Verify root cause analysis was performed
    error_history = agent.get_error_history()
    assert len(error_history) > 0
    assert "root_causes" in error_history[-1]

def test_retry_history(agent):
    """Test retry history tracking"""
    attempt_count = 0
    def operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("operation failed")
        return "success"
    
    agent.execute_with_retry(operation)
    
    history = agent.get_retry_history()
    assert len(history) == 2  # Two retries
    assert all(entry["error_type"] == "ValueError" for entry in history)

def test_clear_histories(agent):
    """Test clearing retry and error histories"""
    # Generate some history
    def operation():
        raise ValueError("test error")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(operation)
    
    # Clear histories
    agent.clear_retry_history()
    agent.clear_error_history()
    
    # Verify histories are cleared
    assert len(agent.get_retry_history()) == 0
    assert len(agent.get_error_history()) == 0

def test_circuit_breaker_state(agent):
    """Test circuit breaker state tracking"""
    # Create policy with circuit breaker
    policy = RetryPolicy(
        name="circuit",
        max_attempts=3,
        strategy=RetryStrategy.LINEAR,
        initial_delay=1.0,
        circuit_breaker=CircuitBreaker(
            failure_threshold=3,
            reset_timeout=1,
            half_open_timeout=0.5,
            failure_rate_threshold=0.5,
            min_requests=5
        )
    )
    agent.retry_manager.add_policy("circuit", policy)
    
    # Initial state should be CLOSED
    assert agent.get_circuit_breaker_state("circuit") == CircuitBreakerState.CLOSED
    
    # Trigger circuit breaker
    def operation():
        raise RuntimeError("operation failed")
    
    for _ in range(3):
        with pytest.raises(RuntimeError):
            agent.execute_with_retry(operation, retry_policy_name="circuit")
    
    # State should be OPEN
    assert agent.get_circuit_breaker_state("circuit") == CircuitBreakerState.OPEN

def test_operation_context(agent):
    """Test operation context handling"""
    context = {"user_id": "123", "operation": "test"}
    
    def operation():
        raise ValueError("test error")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(operation, context=context)
    
    error_history = agent.get_error_history()
    assert len(error_history) > 0
    assert error_history[-1]["context"] == context

def test_invalid_policy_name(agent):
    """Test handling of invalid retry policy name"""
    def operation():
        return "success"
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(operation, retry_policy_name="nonexistent")

if __name__ == '__main__':
    unittest.main() 