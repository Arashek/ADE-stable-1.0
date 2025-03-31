import pytest
import os
import tempfile
import shutil
import time
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
from src.core.script.script_manager import ScriptManager, ScriptContext, ExecutionResult
from src.core.code.fix_manager import FixManager, Fix
from src.core.error.retry_policy import RetryManager, RetryPolicy, RetryStrategy, CircuitBreaker, CircuitBreakerState
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer, RootCause
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine

@dataclass
class TestMetrics:
    """Test metrics data structure"""
    execution_time: float
    memory_usage: float
    retry_count: int
    error_count: int
    fix_count: int
    success_rate: float
    avg_delay: float
    circuit_breaker_state: str

@pytest.fixture
def metrics_collector():
    """Create a metrics collector instance"""
    return MetricsCollector()

@pytest.fixture
def analytics_engine():
    """Create an analytics engine instance"""
    return AnalyticsEngine()

@pytest.fixture
def monitored_script_manager(metrics_collector, analytics_engine):
    """Create a ScriptManager instance with monitoring"""
    return ScriptManager(
        retry_manager=RetryManager(),
        error_detector=ErrorDetector(),
        root_cause_analyzer=RootCauseAnalyzer(),
        fix_manager=FixManager(),
        metrics_collector=metrics_collector,
        analytics_engine=analytics_engine
    )

@pytest.fixture
def performance_test_script(temp_dir):
    """Create a script for performance testing"""
    script_path = os.path.join(temp_dir, "performance_test.py")
    with open(script_path, 'w') as f:
        f.write("""
import time
import psutil
import os

def memory_intensive():
    data = [i for i in range(1000000)]
    return sum(data)

def cpu_intensive():
    result = 0
    for i in range(1000000):
        result += i * i
    return result

def io_intensive():
    with open('test_file.txt', 'w') as f:
        for i in range(10000):
            f.write(f"Line {i}\\n")

def main():
    # Test memory usage
    memory_result = memory_intensive()
    
    # Test CPU usage
    cpu_result = cpu_intensive()
    
    # Test I/O operations
    io_intensive()
    
    print(f"Memory test result: {memory_result}")
    print(f"CPU test result: {cpu_result}")
    print("I/O test completed")
""")
    return script_path

def test_execution_metrics(monitored_script_manager, performance_test_script):
    """Test execution metrics collection"""
    # Execute script
    success, result = monitored_script_manager.execute_script(performance_test_script)
    
    # Get metrics
    metrics = monitored_script_manager.metrics_collector.get_metrics()
    
    # Verify metrics
    assert metrics.execution_time > 0
    assert metrics.memory_usage > 0
    assert metrics.retry_count >= 0
    assert metrics.error_count >= 0
    assert metrics.fix_count >= 0
    assert 0 <= metrics.success_rate <= 1
    assert metrics.avg_delay >= 0

def test_error_pattern_analytics(monitored_script_manager, temp_dir):
    """Test error pattern analytics"""
    # Create a script with various error patterns
    script_path = os.path.join(temp_dir, "error_patterns.py")
    with open(script_path, 'w') as f:
        f.write("""
def test_errors():
    # Syntax error
    if True
        print("Wrong")
    
    # Name error
    undefined_variable
    
    # Type error
    "string" + 42
    
    # Index error
    empty_list = []
    empty_list[0]
""")
    
    # Execute script multiple times
    for _ in range(5):
        monitored_script_manager.execute_script(script_path)
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify error pattern analysis
    assert "syntax_error" in analytics.error_patterns
    assert "name_error" in analytics.error_patterns
    assert "type_error" in analytics.error_patterns
    assert "index_error" in analytics.error_patterns

def test_retry_policy_analytics(monitored_script_manager, temp_dir):
    """Test retry policy analytics"""
    # Create a script that fails initially
    script_path = os.path.join(temp_dir, "retry_analytics.py")
    with open(script_path, 'w') as f:
        f.write("""
import os
import time

# Create a file that will be deleted after first attempt
if not os.path.exists('test_file'):
    with open('test_file', 'w') as f:
        f.write('test')
    raise RuntimeError("First attempt failed")

print("Success")
""")
    
    # Create different retry policies
    policies = [
        RetryPolicy(
            name="linear",
            max_attempts=3,
            strategy=RetryStrategy.LINEAR,
            initial_delay=1.0
        ),
        RetryPolicy(
            name="exponential",
            max_attempts=3,
            strategy=RetryStrategy.EXPONENTIAL,
            initial_delay=1.0
        ),
        RetryPolicy(
            name="fibonacci",
            max_attempts=3,
            strategy=RetryStrategy.FIBONACCI,
            initial_delay=1.0
        )
    ]
    
    # Add policies
    for policy in policies:
        monitored_script_manager.retry_manager.add_policy(policy.name, policy)
    
    # Test each policy
    for policy in policies:
        monitored_script_manager.execute_script(
            script_path,
            retry_policy_name=policy.name
        )
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify retry policy analysis
    assert "linear" in analytics.retry_policies
    assert "exponential" in analytics.retry_policies
    assert "fibonacci" in analytics.retry_policies

def test_root_cause_analytics(monitored_script_manager, temp_dir):
    """Test root cause analysis analytics"""
    # Create a script with complex error chain
    script_path = os.path.join(temp_dir, "root_cause.py")
    with open(script_path, 'w') as f:
        f.write("""
def process_data(data):
    try:
        result = data / 0  # Division by zero
    except ZeroDivisionError:
        raise ValueError("Invalid data format")
    return result

def main():
    try:
        process_data("invalid")
    except ValueError as e:
        raise RuntimeError(f"Processing failed: {str(e)}")

main()
""")
    
    # Execute script
    monitored_script_manager.execute_script(script_path)
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify root cause analysis
    assert "runtime_error" in analytics.root_causes
    assert "value_error" in analytics.root_causes
    assert "zero_division_error" in analytics.root_causes

def test_fix_effectiveness_analytics(monitored_script_manager, temp_dir):
    """Test fix effectiveness analytics"""
    # Create a script with fixable issues
    script_path = os.path.join(temp_dir, "fix_effectiveness.py")
    with open(script_path, 'w') as f:
        f.write("""
def calculate_sum(a, b):
    return a + b

# Missing docstring
def process_data(data):
    return data * 2

# Syntax error
if True
    print("Wrong")
""")
    
    # Register fixes
    fixes = [
        Fix(
            cause_type="missing_docstring",
            description="Add docstring",
            confidence=0.9,
            changes=[
                {
                    "type": "insert",
                    "position": 5,
                    "text": '    """Process input data."""\n'
                }
            ],
            safety_checks=[{"type": "syntax_check"}]
        ),
        Fix(
            cause_type="syntax_error",
            description="Fix syntax",
            confidence=0.8,
            changes=[
                {
                    "type": "replace",
                    "old": "if True",
                    "new": "if True:"
                }
            ],
            safety_checks=[{"type": "syntax_check"}]
        )
    ]
    
    for fix in fixes:
        monitored_script_manager.fix_manager.register_fix(fix)
    
    # Execute script
    monitored_script_manager.execute_script(script_path)
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify fix effectiveness analysis
    assert "missing_docstring" in analytics.fix_effectiveness
    assert "syntax_error" in analytics.fix_effectiveness
    assert analytics.fix_effectiveness["missing_docstring"]["success_rate"] > 0
    assert analytics.fix_effectiveness["syntax_error"]["success_rate"] > 0

def test_circuit_breaker_analytics(monitored_script_manager, temp_dir):
    """Test circuit breaker analytics"""
    # Create a script that fails consistently
    script_path = os.path.join(temp_dir, "circuit_breaker.py")
    with open(script_path, 'w') as f:
        f.write("""
raise RuntimeError("Always fails")
""")
    
    # Create policy with circuit breaker
    policy = RetryPolicy(
        name="circuit_test",
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
    monitored_script_manager.retry_manager.add_policy("circuit_test", policy)
    
    # Execute script multiple times
    for _ in range(5):
        monitored_script_manager.execute_script(
            script_path,
            retry_policy_name="circuit_test"
        )
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify circuit breaker analysis
    assert "circuit_test" in analytics.circuit_breakers
    assert analytics.circuit_breakers["circuit_test"]["state_transitions"] > 0
    assert analytics.circuit_breakers["circuit_test"]["failure_rate"] > 0

def test_performance_trends(monitored_script_manager, performance_test_script):
    """Test performance trend analysis"""
    # Execute script multiple times
    for _ in range(5):
        monitored_script_manager.execute_script(performance_test_script)
        time.sleep(0.1)  # Small delay between executions
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify performance trends
    assert len(analytics.performance_trends["execution_time"]) > 0
    assert len(analytics.performance_trends["memory_usage"]) > 0
    assert len(analytics.performance_trends["cpu_usage"]) > 0

def test_error_correlation_analytics(monitored_script_manager, temp_dir):
    """Test error correlation analysis"""
    # Create a script with correlated errors
    script_path = os.path.join(temp_dir, "error_correlation.py")
    with open(script_path, 'w') as f:
        f.write("""
def process_data(data):
    try:
        result = int(data)
        return result / 0  # Division by zero
    except ValueError:
        raise TypeError("Invalid data type")
    except ZeroDivisionError:
        raise RuntimeError("Processing failed")

def main():
    try:
        process_data("invalid")
    except (TypeError, RuntimeError) as e:
        raise Exception(f"Operation failed: {str(e)}")

main()
""")
    
    # Execute script multiple times
    for _ in range(5):
        monitored_script_manager.execute_script(script_path)
    
    # Get analytics
    analytics = monitored_script_manager.analytics_engine.get_analytics()
    
    # Verify error correlation analysis
    assert "error_correlations" in analytics
    assert len(analytics.error_correlations) > 0
    assert any("type_error" in corr for corr in analytics.error_correlations)
    assert any("runtime_error" in corr for corr in analytics.error_correlations)

def test_resource_usage_monitoring(monitored_script_manager, performance_test_script):
    """Test resource usage monitoring"""
    # Execute script
    monitored_script_manager.execute_script(performance_test_script)
    
    # Get metrics
    metrics = monitored_script_manager.metrics_collector.get_metrics()
    
    # Verify resource usage metrics
    assert metrics.memory_usage > 0
    assert metrics.cpu_usage > 0
    assert metrics.io_operations > 0
    assert metrics.network_usage >= 0

def test_alert_thresholds(monitored_script_manager, performance_test_script):
    """Test alert threshold monitoring"""
    # Set alert thresholds
    monitored_script_manager.metrics_collector.set_alert_thresholds({
        "memory_usage": 100,  # MB
        "execution_time": 5.0,  # seconds
        "error_rate": 0.5
    })
    
    # Execute script
    monitored_script_manager.execute_script(performance_test_script)
    
    # Get alerts
    alerts = monitored_script_manager.metrics_collector.get_alerts()
    
    # Verify alert system
    assert isinstance(alerts, list)
    assert all(isinstance(alert, dict) for alert in alerts)
    assert all("threshold" in alert for alert in alerts)
    assert all("value" in alert for alert in alerts) 