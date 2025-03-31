import pytest
import time
from datetime import datetime, timedelta
from src.core.error.retry_policy import (
    RetryManager, RetryPolicy, RetryStrategy,
    CircuitBreaker, CircuitBreakerState
)

@pytest.fixture
def retry_manager():
    return RetryManager()

@pytest.fixture
def basic_policy():
    return RetryPolicy(
        name="basic",
        max_attempts=3,
        strategy=RetryStrategy.LINEAR,
        initial_delay=1.0,
        max_delay=5.0,
        jitter=True,
        error_types=[ValueError],
        error_patterns=["invalid input"],
        max_total_time=10.0,
        circuit_breaker=CircuitBreaker(
            failure_threshold=5,
            reset_timeout=60,
            half_open_timeout=30,
            failure_rate_threshold=0.5,
            min_requests=10
        )
    )

def test_add_and_get_policy(retry_manager, basic_policy):
    """Test adding and retrieving retry policies"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Test getting existing policy
    policy = retry_manager.get_policy("basic")
    assert policy == basic_policy
    
    # Test getting non-existent policy
    policy = retry_manager.get_policy("nonexistent")
    assert policy is None

def test_should_retry(retry_manager, basic_policy):
    """Test retry decision logic"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Test matching error type
    assert retry_manager.should_retry("basic", ValueError("invalid input"))
    
    # Test matching error pattern
    assert retry_manager.should_retry("basic", Exception("invalid input"))
    
    # Test non-matching error
    assert not retry_manager.should_retry("basic", TypeError("type error"))

def test_delay_calculation(retry_manager, basic_policy):
    """Test delay calculation for different strategies"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Test linear delay
    delay = retry_manager.get_delay("basic", 2)
    assert delay == 2.0  # 1.0 * 2
    
    # Test exponential delay
    exp_policy = RetryPolicy(
        name="exponential",
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=10.0
    )
    retry_manager.add_policy("exponential", exp_policy)
    delay = retry_manager.get_delay("exponential", 2)
    assert delay == 2.0  # 1.0 * 2^1
    
    # Test fibonacci delay
    fib_policy = RetryPolicy(
        name="fibonacci",
        max_attempts=3,
        strategy=RetryStrategy.FIBONACCI,
        initial_delay=1.0,
        max_delay=10.0
    )
    retry_manager.add_policy("fibonacci", fib_policy)
    delay = retry_manager.get_delay("fibonacci", 3)
    assert delay == 2.0  # 1.0, 1.0, 2.0
    
    # Test random delay
    rand_policy = RetryPolicy(
        name="random",
        max_attempts=3,
        strategy=RetryStrategy.RANDOM,
        initial_delay=1.0,
        max_delay=5.0
    )
    retry_manager.add_policy("random", rand_policy)
    delay = retry_manager.get_delay("random", 1)
    assert 1.0 <= delay <= 5.0

def test_custom_delay_function(retry_manager):
    """Test custom delay function"""
    def custom_delay(attempt: int) -> float:
        return attempt * 2.0
    
    custom_policy = RetryPolicy(
        name="custom",
        max_attempts=3,
        strategy=RetryStrategy.CUSTOM,
        initial_delay=1.0,
        custom_function=custom_delay
    )
    retry_manager.add_policy("custom", custom_policy)
    
    delay = retry_manager.get_delay("custom", 2)
    assert delay == 4.0  # 2 * 2.0

def test_jitter_application(retry_manager, basic_policy):
    """Test jitter application to delays"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Test multiple delays to verify jitter
    delays = [retry_manager.get_delay("basic", 1) for _ in range(10)]
    assert len(set(delays)) > 1  # Should have some variation
    assert all(0.8 <= delay <= 1.2)  # Within jitter range

def test_max_delay_limit(retry_manager):
    """Test maximum delay limit"""
    policy = RetryPolicy(
        name="max_delay",
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=5.0
    )
    retry_manager.add_policy("max_delay", policy)
    
    delay = retry_manager.get_delay("max_delay", 4)
    assert delay <= 5.0  # Should not exceed max_delay

def test_max_total_time(retry_manager, basic_policy):
    """Test maximum total time limit"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Test within time limit
    assert retry_manager.should_retry("basic", ValueError("invalid input"))
    
    # Test exceeding time limit
    basic_policy.start_time = time.time() - 11.0  # Exceed 10.0 seconds
    assert not retry_manager.should_retry("basic", ValueError("invalid input"))

def test_circuit_breaker(retry_manager):
    """Test circuit breaker functionality"""
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
    retry_manager.add_policy("circuit", policy)
    
    # Test initial state
    assert policy.circuit_breaker.state == CircuitBreakerState.CLOSED
    
    # Test transition to open
    for _ in range(3):
        policy.circuit_breaker.record_failure()
    assert policy.circuit_breaker.state == CircuitBreakerState.OPEN
    
    # Test transition to half-open
    time.sleep(1.1)  # Wait for reset timeout
    assert policy.circuit_breaker.state == CircuitBreakerState.HALF_OPEN
    
    # Test successful recovery
    policy.circuit_breaker.record_success()
    assert policy.circuit_breaker.state == CircuitBreakerState.CLOSED

def test_attempt_history(retry_manager, basic_policy):
    """Test attempt history recording"""
    retry_manager.add_policy("basic", basic_policy)
    
    # Record some attempts
    retry_manager.record_attempt("basic", 1, ValueError("invalid input"), 1.0)
    retry_manager.record_attempt("basic", 2, ValueError("invalid input"), 2.0)
    
    # Check history
    history = retry_manager.get_attempt_history("basic")
    assert len(history) == 2
    assert history[0]["attempt"] == 1
    assert history[1]["attempt"] == 2
    assert history[0]["error_type"] == "ValueError"
    assert history[1]["error_type"] == "ValueError"
    
    # Test clearing history
    retry_manager.clear_history("basic")
    assert len(retry_manager.get_attempt_history("basic")) == 0

def test_clear_all_history(retry_manager, basic_policy):
    """Test clearing all attempt history"""
    retry_manager.add_policy("basic", basic_policy)
    retry_manager.add_policy("other", RetryPolicy(
        name="other",
        max_attempts=3,
        strategy=RetryStrategy.LINEAR,
        initial_delay=1.0
    ))
    
    # Record attempts for both policies
    retry_manager.record_attempt("basic", 1, ValueError("invalid input"), 1.0)
    retry_manager.record_attempt("other", 1, TypeError("type error"), 1.0)
    
    # Clear all history
    retry_manager.clear_history()
    
    # Verify both histories are cleared
    assert len(retry_manager.get_attempt_history("basic")) == 0
    assert len(retry_manager.get_attempt_history("other")) == 0

def test_circuit_breaker_failure_rate(retry_manager):
    """Test circuit breaker failure rate threshold"""
    policy = RetryPolicy(
        name="circuit",
        max_attempts=3,
        strategy=RetryStrategy.LINEAR,
        initial_delay=1.0,
        circuit_breaker=CircuitBreaker(
            failure_threshold=10,
            reset_timeout=1,
            half_open_timeout=0.5,
            failure_rate_threshold=0.5,
            min_requests=10
        )
    )
    retry_manager.add_policy("circuit", policy)
    
    # Record 10 requests with 6 failures (60% failure rate)
    for _ in range(6):
        policy.circuit_breaker.record_failure()
    for _ in range(4):
        policy.circuit_breaker.record_success()
    
    # Should open due to high failure rate
    assert policy.circuit_breaker.state == CircuitBreakerState.OPEN

def test_circuit_breaker_min_requests(retry_manager):
    """Test circuit breaker minimum requests requirement"""
    policy = RetryPolicy(
        name="circuit",
        max_attempts=3,
        strategy=RetryStrategy.LINEAR,
        initial_delay=1.0,
        circuit_breaker=CircuitBreaker(
            failure_threshold=10,
            reset_timeout=1,
            half_open_timeout=0.5,
            failure_rate_threshold=0.5,
            min_requests=10
        )
    )
    retry_manager.add_policy("circuit", policy)
    
    # Record 5 failures (below min_requests)
    for _ in range(5):
        policy.circuit_breaker.record_failure()
    
    # Should not open due to insufficient requests
    assert policy.circuit_breaker.state == CircuitBreakerState.CLOSED 