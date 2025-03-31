import pytest
import time
from datetime import datetime, timedelta
from src.core.agent.agent import Agent
from src.core.error.retry_policy import (
    RetryManager, RetryPolicy, RetryStrategy,
    CircuitBreaker, CircuitBreakerState
)
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer

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

@pytest.fixture
def retry_policy():
    return RetryPolicy(
        name="agent_retry",
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=5.0,
        jitter=True,
        error_types=[ValueError, RuntimeError],
        error_patterns=["invalid input", "operation failed"],
        max_total_time=10.0,
        circuit_breaker=CircuitBreaker(
            failure_threshold=5,
            reset_timeout=60,
            half_open_timeout=30,
            failure_rate_threshold=0.5,
            min_requests=10
        )
    )

def test_agent_retry_integration(agent, retry_manager, retry_policy):
    """Test integration between agent and retry system"""
    # Add retry policy
    retry_manager.add_policy("agent_retry", retry_policy)
    
    # Test successful operation
    def successful_operation():
        return "success"
    
    result = agent.execute_with_retry(
        operation=successful_operation,
        retry_policy_name="agent_retry"
    )
    assert result == "success"
    
    # Test operation with retries
    attempt_count = 0
    def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("invalid input")
        return "success"
    
    result = agent.execute_with_retry(
        operation=failing_operation,
        retry_policy_name="agent_retry"
    )
    assert result == "success"
    assert attempt_count == 3

def test_agent_error_detection(agent, error_detector):
    """Test error detection during agent operations"""
    def failing_operation():
        raise ValueError("invalid input")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(
            operation=failing_operation,
            retry_policy_name="agent_retry"
        )
    
    # Verify error was detected and analyzed
    error_history = error_detector.get_error_history()
    assert len(error_history) > 0
    assert error_history[-1]["error_type"] == "ValueError"
    assert "invalid input" in error_history[-1]["error_message"]

def test_agent_root_cause_analysis(agent, root_cause_analyzer):
    """Test root cause analysis during agent operations"""
    def failing_operation():
        raise RuntimeError("operation failed: database connection timeout")
    
    with pytest.raises(RuntimeError):
        agent.execute_with_retry(
            operation=failing_operation,
            retry_policy_name="agent_retry"
        )
    
    # Verify root cause analysis
    causes = root_cause_analyzer.analyze_error(RuntimeError("operation failed: database connection timeout"))
    assert len(causes) > 0
    assert any(cause.cause_type == "dependency_issues" for cause in causes)

def test_agent_circuit_breaker(agent, retry_manager, retry_policy):
    """Test circuit breaker integration with agent"""
    retry_manager.add_policy("agent_retry", retry_policy)
    
    def failing_operation():
        raise RuntimeError("operation failed")
    
    # Trigger circuit breaker
    for _ in range(6):  # Exceed failure threshold
        with pytest.raises(RuntimeError):
            agent.execute_with_retry(
                operation=failing_operation,
                retry_policy_name="agent_retry"
            )
    
    # Verify circuit breaker state
    assert retry_policy.circuit_breaker.state == CircuitBreakerState.OPEN
    
    # Test operation with open circuit breaker
    with pytest.raises(RuntimeError):
        agent.execute_with_retry(
            operation=failing_operation,
            retry_policy_name="agent_retry"
        )

def test_agent_retry_history(agent, retry_manager, retry_policy):
    """Test retry history tracking during agent operations"""
    retry_manager.add_policy("agent_retry", retry_policy)
    
    attempt_count = 0
    def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("invalid input")
        return "success"
    
    agent.execute_with_retry(
        operation=failing_operation,
        retry_policy_name="agent_retry"
    )
    
    # Verify retry history
    history = retry_manager.get_attempt_history("agent_retry")
    assert len(history) == 2  # Two retries
    assert all(entry["error_type"] == "ValueError" for entry in history)

def test_agent_error_patterns(agent, error_detector):
    """Test error pattern matching during agent operations"""
    def failing_operation():
        raise ValueError("invalid input: missing required field")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(
            operation=failing_operation,
            retry_policy_name="agent_retry"
        )
    
    # Verify error pattern matching
    error_history = error_detector.get_error_history()
    assert len(error_history) > 0
    assert "invalid input" in error_history[-1]["error_message"]

def test_agent_retry_strategies(agent, retry_manager):
    """Test different retry strategies with agent"""
    # Test exponential backoff
    exp_policy = RetryPolicy(
        name="exponential",
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=5.0
    )
    retry_manager.add_policy("exponential", exp_policy)
    
    attempt_count = 0
    def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("invalid input")
        return "success"
    
    start_time = time.time()
    agent.execute_with_retry(
        operation=failing_operation,
        retry_policy_name="exponential"
    )
    duration = time.time() - start_time
    
    # Verify exponential backoff timing
    assert duration >= 3.0  # 1.0 + 2.0 seconds

def test_agent_error_context(agent, error_detector):
    """Test error context capture during agent operations"""
    def failing_operation():
        context = {"user_id": "123", "operation": "test"}
        raise ValueError("invalid input")
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(
            operation=failing_operation,
            retry_policy_name="agent_retry"
        )
    
    # Verify error context
    error_history = error_detector.get_error_history()
    assert len(error_history) > 0
    assert "context" in error_history[-1]

def test_agent_retry_timeout(agent, retry_manager, retry_policy):
    """Test retry timeout handling"""
    retry_manager.add_policy("agent_retry", retry_policy)
    
    def slow_operation():
        time.sleep(2.0)  # Simulate slow operation
        raise ValueError("invalid input")
    
    # Set short timeout
    retry_policy.max_total_time = 1.0
    
    with pytest.raises(ValueError):
        agent.execute_with_retry(
            operation=slow_operation,
            retry_policy_name="agent_retry"
        )
    
    # Verify timeout handling
    history = retry_manager.get_attempt_history("agent_retry")
    assert len(history) > 0
    assert history[-1]["error_type"] == "ValueError" 