import pytest
import asyncio
from datetime import datetime, timedelta
from src.core.error.error_detector import ErrorDetector, ErrorContext, ErrorMatch

@pytest.fixture
def error_detector():
    """Create an ErrorDetector instance for testing"""
    config = {
        "patterns_file": "error_patterns.json"
    }
    return ErrorDetector(config)

def test_load_patterns(error_detector):
    """Test loading of error patterns"""
    assert len(error_detector.patterns) > 0
    assert "name_error" in error_detector.patterns
    assert "type_error" in error_detector.patterns

@pytest.mark.asyncio
async def test_detect_name_error(error_detector):
    """Test detection of NameError"""
    try:
        undefined_variable
    except NameError as e:
        context = {
            "local_vars": {},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        name_error_match = next(m for m in matches if m.pattern.pattern_id == "name_error")
        assert name_error_match is not None
        assert name_error_match.confidence == 1.0
        assert name_error_match.match_groups["name"] == "undefined_variable"

@pytest.mark.asyncio
async def test_detect_type_error(error_detector):
    """Test detection of TypeError"""
    try:
        "string" + 42
    except TypeError as e:
        context = {
            "local_vars": {},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        type_error_match = next(m for m in matches if m.pattern.pattern_id == "type_error")
        assert type_error_match is not None
        assert type_error_match.confidence == 1.0
        assert "str" in type_error_match.match_groups["type1"]
        assert "int" in type_error_match.match_groups["type2"]

@pytest.mark.asyncio
async def test_detect_index_error(error_detector):
    """Test detection of IndexError"""
    try:
        empty_list = []
        empty_list[0]
    except IndexError as e:
        context = {
            "local_vars": {"empty_list": []},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        index_error_match = next(m for m in matches if m.pattern.pattern_id == "index_error")
        assert index_error_match is not None
        assert index_error_match.confidence == 1.0

@pytest.mark.asyncio
async def test_detect_key_error(error_detector):
    """Test detection of KeyError"""
    try:
        d = {}
        d["missing_key"]
    except KeyError as e:
        context = {
            "local_vars": {"d": {}},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        key_error_match = next(m for m in matches if m.pattern.pattern_id == "key_error")
        assert key_error_match is not None
        assert key_error_match.confidence == 1.0
        assert key_error_match.match_groups["key"] == "missing_key"

@pytest.mark.asyncio
async def test_detect_attribute_error(error_detector):
    """Test detection of AttributeError"""
    try:
        x = 42
        x.nonexistent_method()
    except AttributeError as e:
        context = {
            "local_vars": {"x": 42},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        attr_error_match = next(m for m in matches if m.pattern.pattern_id == "attribute_error")
        assert attr_error_match is not None
        assert attr_error_match.confidence == 1.0
        assert "int" in attr_error_match.match_groups["type"]
        assert "nonexistent_method" in attr_error_match.match_groups["attribute"]

def test_error_statistics(error_detector):
    """Test error statistics generation"""
    # Create some test errors
    error_contexts = [
        ErrorContext(
            error_id="err_1",
            timestamp=datetime.now(),
            error_type="NameError",
            message="name 'x' is not defined",
            stack_trace="",
            source_file="test.py",
            line_number=1
        ),
        ErrorContext(
            error_id="err_2",
            timestamp=datetime.now(),
            error_type="TypeError",
            message="unsupported operand type(s) for +: 'str' and 'int'",
            stack_trace="",
            source_file="test.py",
            line_number=2
        )
    ]
    
    error_detector.error_history = error_contexts
    
    stats = error_detector.get_error_statistics()
    
    assert stats["total_errors"] == 2
    assert stats["error_types"]["NameError"] == 1
    assert stats["error_types"]["TypeError"] == 1
    assert len(stats["time_distribution"]) > 0

@pytest.mark.asyncio
async def test_multiple_matches(error_detector):
    """Test detection of multiple matching patterns"""
    try:
        # This will raise both TypeError and AttributeError
        x = "string"
        x.nonexistent_method() + 42
    except (TypeError, AttributeError) as e:
        context = {
            "local_vars": {"x": "string"},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 1
        # Verify matches are sorted by confidence
        assert matches[0].confidence >= matches[1].confidence

@pytest.mark.asyncio
async def test_no_matches(error_detector):
    """Test handling of unknown error types"""
    class CustomError(Exception):
        pass
    
    try:
        raise CustomError("Custom error message")
    except CustomError as e:
        context = {
            "local_vars": {},
            "global_vars": {},
            "system_state": {}
        }
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) == 0

def test_analyze_error_trends(error_detector):
    """Test error trend analysis"""
    # Create test errors over time
    now = datetime.now()
    test_errors = [
        ErrorContext(
            error_id=f"err_{i}",
            timestamp=now - timedelta(hours=i),
            error_type="NameError" if i % 2 == 0 else "TypeError",
            message=f"Test error {i}",
            stack_trace="",
            source_file="test.py",
            line_number=i
        )
        for i in range(10)
    ]
    
    error_detector.error_history = test_errors
    
    # Analyze trends
    trends = error_detector.analyze_error_trends(timedelta(hours=24))
    
    assert trends["total_errors"] == 10
    assert trends["error_frequency"]["NameError"] == 5
    assert trends["error_frequency"]["TypeError"] == 5
    assert len(trends["hourly_distribution"]) > 0
    assert len(trends["recurring_errors"]) > 0

def test_analyze_error_correlations(error_detector):
    """Test error correlation analysis"""
    # Create test error sequence
    test_errors = [
        ErrorContext(
            error_id=f"err_{i}",
            timestamp=datetime.now(),
            error_type=["NameError", "TypeError", "IndexError"][i % 3],
            message=f"Test error {i}",
            stack_trace="",
            source_file="test.py",
            line_number=i
        )
        for i in range(9)
    ]
    
    error_detector.error_history = test_errors
    
    # Analyze correlations
    correlations = error_detector.analyze_error_correlations()
    
    assert len(correlations) > 0
    assert all(c["count"] > 1 for c in correlations)
    assert all(0 <= c["confidence"] <= 1 for c in correlations)
    
    # Verify pattern detection
    patterns = [c["pattern"] for c in correlations]
    assert ("NameError", "TypeError") in patterns
    assert ("TypeError", "IndexError") in patterns

def test_analyze_error_context(error_detector):
    """Test error context analysis"""
    # Create test error with context
    test_error = ErrorContext(
        error_id="test_err",
        timestamp=datetime.now(),
        error_type="NameError",
        message="name 'x' is not defined",
        stack_trace="""  File "test.py", line 1, in <module>
    x = undefined_variable
  File "helper.py", line 2, in process_data
    result = calculate(x)""",
        source_file="test.py",
        line_number=1,
        function_name="process_data",
        local_vars={"x": None, "y": 42},
        global_vars={"config": {"debug": True}},
        system_state={
            "resource_usage": {"memory": 100, "cpu": 50},
            "environment_vars": {"PYTHONPATH": "/test"},
            "system_metrics": {"load": 1.5}
        }
    )
    
    error_detector.error_history = [test_error]
    
    # Analyze context
    context = error_detector.analyze_error_context("test_err")
    
    assert context["error_details"]["type"] == "NameError"
    assert context["error_details"]["line_number"] == 1
    
    # Check variable analysis
    var_analysis = context["variable_analysis"]
    assert len(var_analysis["local_vars"]) == 2
    assert var_analysis["type_distribution"]["int"] == 1
    assert "x" in var_analysis["null_values"]
    
    # Check stack trace analysis
    stack_analysis = context["stack_trace_analysis"]
    assert stack_analysis["depth"] == 2
    assert len(stack_analysis["function_calls"]) == 2
    assert "process_data" in stack_analysis["function_calls"]
    
    # Check system state analysis
    state_analysis = context["system_state_analysis"]
    assert state_analysis["resource_usage"]["memory"] == 100
    assert state_analysis["environment_vars"]["PYTHONPATH"] == "/test"
    assert state_analysis["system_metrics"]["load"] == 1.5

def test_analyze_error_context_not_found(error_detector):
    """Test error context analysis for non-existent error"""
    context = error_detector.analyze_error_context("non_existent")
    assert context == {}

@pytest.mark.asyncio
async def test_error_detection_with_context(error_detector):
    """Test error detection with full context"""
    try:
        # Create a complex error scenario
        def process_data(data):
            x = None
            y = 42
            result = data[x] + y
            return result
            
        process_data([])
    except (TypeError, IndexError) as e:
        context = {
            "local_vars": locals(),
            "global_vars": globals(),
            "system_state": {
                "resource_usage": {"memory": 100, "cpu": 50},
                "environment_vars": {"PYTHONPATH": "/test"},
                "system_metrics": {"load": 1.5}
            }
        }
        
        matches = await error_detector.detect_error(e, context)
        
        assert len(matches) > 0
        error_context = matches[0].context
        
        # Verify context analysis
        analysis = error_detector.analyze_error_context(error_context.error_id)
        
        assert analysis["error_details"]["type"] in ["TypeError", "IndexError"]
        assert "x" in analysis["variable_analysis"]["local_vars"]
        assert "y" in analysis["variable_analysis"]["local_vars"]
        assert analysis["system_state_analysis"]["resource_usage"]["memory"] == 100 