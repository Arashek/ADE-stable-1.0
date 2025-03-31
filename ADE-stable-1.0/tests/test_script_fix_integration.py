import pytest
import os
import tempfile
import shutil
from datetime import datetime
from src.core.script.script_manager import ScriptManager
from src.core.code.fix_manager import FixManager, Fix
from src.core.error.retry_policy import RetryManager, RetryPolicy, RetryStrategy
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer, RootCause

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def script_manager():
    """Create a ScriptManager instance"""
    return ScriptManager(
        retry_manager=RetryManager(),
        error_detector=ErrorDetector(),
        root_cause_analyzer=RootCauseAnalyzer(),
        fix_manager=FixManager()
    )

@pytest.fixture
def test_script(temp_dir):
    """Create a test script with intentional errors"""
    script_path = os.path.join(temp_dir, "test_script.py")
    
    # Create a script with a syntax error
    with open(script_path, 'w') as f:
        f.write("""
def calculate_sum(a, b):
    return a + b

# Intentional syntax error
if True
    print("This is wrong")

print(calculate_sum(1, 2))
""")
    
    return script_path

@pytest.fixture
def fix_manager():
    """Create a FixManager instance with test fixes"""
    manager = FixManager()
    
    # Register a fix for syntax errors
    syntax_fix = Fix(
        cause_type="syntax_error",
        description="Fix syntax error in if statement",
        confidence=0.9,
        changes=[
            {
                "type": "replace",
                "old": "if True",
                "new": "if True:"
            }
        ],
        safety_checks=[
            {
                "type": "file_exists"
            },
            {
                "type": "syntax_check"
            }
        ],
        rollback_plan={
            "verification": lambda f: True
        }
    )
    
    manager.register_fix(syntax_fix)
    return manager

def test_script_execution_with_fix(script_manager, test_script):
    """Test script execution with automatic fixing"""
    # Execute script
    success, result = script_manager.execute_script(test_script)
    
    # Verify script was fixed and executed successfully
    assert success
    assert "3" in result  # Result of calculate_sum(1, 2)
    
    # Verify the fix was applied
    with open(test_script, 'r') as f:
        content = f.read()
    assert "if True:" in content  # Fixed syntax

def test_script_execution_without_fix(script_manager, temp_dir):
    """Test script execution without available fix"""
    # Create a script with an error that can't be fixed
    script_path = os.path.join(temp_dir, "unfixable_script.py")
    with open(script_path, 'w') as f:
        f.write("""
def undefined_function():
    return x  # x is not defined
""")
    
    # Execute script
    success, result = script_manager.execute_script(script_path)
    
    # Verify script failed
    assert not success
    assert "NameError" in str(result)

def test_script_execution_with_retry(script_manager, temp_dir):
    """Test script execution with retry logic"""
    # Create a script that fails initially
    script_path = os.path.join(temp_dir, "retry_script.py")
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
    
    # Execute script
    success, result = script_manager.execute_script(script_path)
    
    # Verify script succeeded after retry
    assert success
    assert "Success" in result

def test_script_execution_with_circuit_breaker(script_manager, temp_dir):
    """Test script execution with circuit breaker"""
    # Create a script that always fails
    script_path = os.path.join(temp_dir, "failing_script.py")
    with open(script_path, 'w') as f:
        f.write("""
raise RuntimeError("Always fails")
""")
    
    # Create a policy with circuit breaker
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
    script_manager.retry_manager.add_policy("circuit", policy)
    
    # Execute script multiple times
    for _ in range(4):
        success, result = script_manager.execute_script(
            script_path,
            retry_policy_name="circuit"
        )
        assert not success
    
    # Verify circuit breaker is open
    assert script_manager.get_circuit_breaker_state("circuit") == CircuitBreakerState.OPEN

def test_script_execution_with_context(script_manager, test_script):
    """Test script execution with context"""
    context = {
        "user_id": "test_user",
        "operation": "test_execution",
        "timestamp": datetime.now().isoformat()
    }
    
    # Execute script with context
    success, result = script_manager.execute_script(
        test_script,
        context=context
    )
    
    # Verify context was captured in error history
    error_history = script_manager.get_error_history()
    assert len(error_history) > 0
    assert error_history[-1]["context"] == context

def test_fix_safety_checks(script_manager, temp_dir):
    """Test fix safety checks"""
    # Create a script with a syntax error
    script_path = os.path.join(temp_dir, "safety_test.py")
    with open(script_path, 'w') as f:
        f.write("""
def test_function():
    return 1 + 1

# Syntax error
if True
    print("Wrong")
""")
    
    # Make file read-only
    os.chmod(script_path, 0o444)
    
    # Execute script
    success, result = script_manager.execute_script(script_path)
    
    # Verify script failed due to safety check
    assert not success
    assert "Permission denied" in str(result)

def test_fix_rollback(script_manager, temp_dir):
    """Test fix rollback on failure"""
    # Create a script with multiple issues
    script_path = os.path.join(temp_dir, "rollback_test.py")
    with open(script_path, 'w') as f:
        f.write("""
def test_function():
    return 1 + 1

# Multiple issues
if True
    print("Wrong")
    undefined_variable
""")
    
    # Execute script
    success, result = script_manager.execute_script(script_path)
    
    # Verify script failed and was rolled back
    assert not success
    with open(script_path, 'r') as f:
        content = f.read()
    assert "if True" in content  # Original content restored

def test_script_execution_with_custom_fix(script_manager, temp_dir):
    """Test script execution with custom fix"""
    # Create a script with a custom issue
    script_path = os.path.join(temp_dir, "custom_fix_test.py")
    with open(script_path, 'w') as f:
        f.write("""
def calculate_sum(a, b):
    return a + b

# Custom issue: missing docstring
def process_data(data):
    return data * 2
""")
    
    # Register custom fix
    custom_fix = Fix(
        cause_type="missing_docstring",
        description="Add docstring to function",
        confidence=0.8,
        changes=[
            {
                "type": "insert",
                "position": 5,
                "text": '    """Process input data by doubling it."""\n'
            }
        ],
        safety_checks=[
            {
                "type": "syntax_check"
            }
        ]
    )
    script_manager.fix_manager.register_fix(custom_fix)
    
    # Create root cause
    cause = RootCause(
        cause_type="missing_docstring",
        description="Function missing docstring",
        confidence=0.8,
        evidence=["process_data function has no docstring"],
        suggested_fixes=["Add docstring"],
        related_errors=[]
    )
    
    # Apply fix
    success = script_manager.fix_manager.apply_fix(cause, script_path)
    assert success
    
    # Verify fix was applied
    with open(script_path, 'r') as f:
        content = f.read()
    assert '"""Process input data by doubling it."""' in content 