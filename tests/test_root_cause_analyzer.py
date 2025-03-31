import pytest
from datetime import datetime
from src.core.error.root_cause_analyzer import RootCauseAnalyzer, RootCause

@pytest.fixture
def analyzer():
    return RootCauseAnalyzer()

def test_analyze_memory_error(analyzer):
    """Test analysis of memory error"""
    error = Exception("Memory limit exceeded: 1024MB")
    context = {
        "system_state": {
            "resource_usage": {
                "memory": 95,
                "cpu": 50
            }
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 1
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    assert memory_cause.description == "System memory limit exceeded"
    assert memory_cause.confidence == 0.9
    assert "Optimize memory usage" in memory_cause.suggested_fixes
    assert memory_cause.metadata["pattern_match"] == ("1024",)
    assert memory_cause.metadata["match_type"] == "exact_match"

def test_analyze_dependency_error(analyzer):
    """Test analysis of dependency error"""
    error = ImportError("No module named 'requests'")
    context = {
        "system_state": {
            "environment_vars": {
                "PYTHONPATH": "/usr/local/lib/python3.8"
            }
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 1
    dep_cause = next(c for c in causes if c.cause_type == "dependency_issues")
    assert dep_cause.description == "Missing Python dependency"
    assert dep_cause.confidence == 0.9
    assert "Install required package" in dep_cause.suggested_fixes
    assert dep_cause.metadata["pattern_match"] == ("requests",)

def test_analyze_validation_error(analyzer):
    """Test analysis of validation error"""
    error = ValueError("invalid literal for int(): 'abc'")
    context = {
        "local_vars": {
            "input_value": "abc",
            "expected_type": "int"
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 1
    val_cause = next(c for c in causes if c.cause_type == "data_validation")
    assert val_cause.description == "Invalid data format"
    assert val_cause.confidence == 0.8
    assert "Validate input data" in val_cause.suggested_fixes
    assert val_cause.metadata["pattern_match"] == ("int", "abc")

def test_analyze_concurrency_error(analyzer):
    """Test analysis of concurrency error"""
    error = RuntimeError("Deadlock detected")
    context = {
        "system_state": {
            "thread_count": 5,
            "lock_count": 3
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 1
    conc_cause = next(c for c in causes if c.cause_type == "concurrency")
    assert conc_cause.description == "Resource deadlock"
    assert conc_cause.confidence == 0.9
    assert "Review locking order" in conc_cause.suggested_fixes

def test_analyze_configuration_error(analyzer):
    """Test analysis of configuration error"""
    error = RuntimeError("Environment variable API_KEY not set")
    context = {
        "system_state": {
            "environment_vars": {
                "PATH": "/usr/bin",
                "HOME": "/home/user"
            }
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 1
    config_cause = next(c for c in causes if c.cause_type == "configuration")
    assert config_cause.description == "Missing environment variable"
    assert config_cause.confidence == 0.8
    assert "Set required environment variable" in config_cause.suggested_fixes
    assert config_cause.metadata["pattern_match"] == ("API_KEY",)

def test_analyze_multiple_causes(analyzer):
    """Test analysis with multiple causes"""
    error = Exception("Memory limit exceeded: 2048MB")
    context = {
        "system_state": {
            "resource_usage": {
                "memory": 98,
                "cpu": 95
            },
            "environment_vars": {}
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    assert len(causes) >= 2
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    cpu_cause = next(c for c in causes if c.cause_type == "resource_exhaustion" and c.metadata["resource"] == "cpu")
    
    assert memory_cause.confidence > cpu_cause.confidence  # Memory error should have higher confidence

def test_error_history(analyzer):
    """Test error history tracking"""
    error1 = Exception("Memory limit exceeded: 1024MB")
    error2 = ImportError("No module named 'requests'")
    
    analyzer.analyze_error(error1, {})
    analyzer.analyze_error(error2, {})
    
    history = analyzer.get_error_history()
    assert len(history) == 2
    assert history[0]["error_type"] == "Exception"
    assert history[1]["error_type"] == "ImportError"
    
    analyzer.clear_history()
    assert len(analyzer.get_error_history()) == 0

def test_related_errors(analyzer):
    """Test related error detection"""
    error1 = Exception("Memory limit exceeded: 1024MB")
    error2 = Exception("Memory limit exceeded: 2048MB")
    
    analyzer.analyze_error(error1, {})
    causes = analyzer.analyze_error(error2, {})
    
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    assert len(memory_cause.related_errors) == 1
    assert "Memory limit exceeded: 1024MB" in memory_cause.related_errors

def test_context_analysis(analyzer):
    """Test context-based analysis"""
    error = Exception("Some error")
    context = {
        "local_vars": {
            "user_input": None,
            "config": None
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    val_cause = next(c for c in causes if c.cause_type == "data_validation")
    assert val_cause.description == "Validation issue: null_variables"
    assert "user_input" in val_cause.metadata["details"]
    assert "config" in val_cause.metadata["details"]

def test_error_handling(analyzer):
    """Test error handling in analyzer"""
    # Test with invalid error object
    causes = analyzer.analyze_error(None, {})
    assert len(causes) == 0
    
    # Test with invalid context
    causes = analyzer.analyze_error(Exception("Test"), None)
    assert len(causes) == 0

def test_pattern_matching_strategies(analyzer):
    """Test different pattern matching strategies"""
    # Test exact match
    error = Exception("Memory limit exceeded: 1024MB")
    causes = analyzer.analyze_error(error, {})
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    assert memory_cause.metadata["match_type"] == "exact_match"
    
    # Test partial match
    error = Exception("Out of memory error occurred")
    causes = analyzer.analyze_error(error, {})
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    assert memory_cause.metadata["match_type"] == "partial_match"
    
    # Test keyword match
    error = Exception("Heap memory allocation failed")
    causes = analyzer.analyze_error(error, {})
    memory_cause = next(c for c in causes if c.cause_type == "resource_exhaustion")
    assert memory_cause.metadata["match_type"] == "keyword_match"

def test_security_analysis(analyzer):
    """Test security-related analysis"""
    error = Exception("Authentication failed: Invalid credentials")
    context = {
        "system_state": {
            "security_context": {
                "ssl_errors": ["Certificate expired"],
                "auth_failures": ["Invalid credentials"]
            }
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    # Check authentication error
    auth_cause = next(c for c in causes if c.cause_type == "security" and c.metadata["issue_type"] == "auth")
    assert auth_cause.description == "Security issue: auth"
    assert "Invalid credentials" in auth_cause.evidence[0]
    
    # Check SSL error
    ssl_cause = next(c for c in causes if c.cause_type == "security" and c.metadata["issue_type"] == "ssl")
    assert ssl_cause.description == "Security issue: ssl"
    assert "Certificate expired" in ssl_cause.evidence[0]

def test_performance_analysis(analyzer):
    """Test performance-related analysis"""
    error = Exception("Query timeout: SELECT * FROM large_table")
    context = {
        "system_state": {
            "performance_metrics": {
                "response_time": 1500,
                "cache_miss_rate": 75
            }
        },
        "db_context": {
            "slow_queries": ["SELECT * FROM large_table"],
            "connection_errors": ["Connection refused"]
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    # Check query timeout
    query_cause = next(c for c in causes if c.cause_type == "performance" and c.metadata["issue_type"] == "slow_queries")
    assert query_cause.description == "Performance issue: slow_queries"
    assert "SELECT * FROM large_table" in str(query_cause.evidence[0])
    
    # Check response time
    response_cause = next(c for c in causes if c.cause_type == "performance" and c.metadata["issue_type"] == "response_time")
    assert response_cause.description == "Performance issue: response_time"
    assert "1500" in response_cause.evidence[0]
    
    # Check cache miss rate
    cache_cause = next(c for c in causes if c.cause_type == "performance" and c.metadata["issue_type"] == "cache_miss")
    assert cache_cause.description == "Performance issue: cache_miss"
    assert "75" in cache_cause.evidence[0]

def test_database_context_analysis(analyzer):
    """Test database context analysis"""
    error = Exception("Database connection failed")
    context = {
        "db_context": {
            "slow_queries": ["SELECT * FROM users WHERE status = 'inactive'"],
            "connection_errors": ["Connection refused: Connection timed out"]
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    # Check slow query
    query_cause = next(c for c in causes if c.cause_type == "performance" and c.metadata["issue_type"] == "slow_queries")
    assert "SELECT * FROM users" in str(query_cause.evidence[0])
    
    # Check connection error
    conn_cause = next(c for c in causes if c.cause_type == "dependency_issues" and c.metadata["issue_type"] == "db_connection")
    assert "Connection refused" in conn_cause.evidence[0]

def test_disk_space_analysis(analyzer):
    """Test disk space analysis"""
    error = Exception("Disk space exceeded: 100GB")
    context = {
        "system_state": {
            "resource_usage": {
                "disk": 95
            }
        }
    }
    
    causes = analyzer.analyze_error(error, context)
    
    # Check disk space error
    disk_cause = next(c for c in causes if c.cause_type == "resource_exhaustion" and c.metadata["resource"] == "disk")
    assert disk_cause.description == "High disk usage: 95%"
    assert "Clean up disk space" in disk_cause.suggested_fixes 