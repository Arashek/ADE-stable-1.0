import pytest
from datetime import datetime
from src.core.cost.cost_estimator import CostEstimator, CostMetrics

@pytest.fixture
def cost_estimator():
    return CostEstimator()

@pytest.fixture
def sample_task():
    return {
        "description": "Analyze code and generate documentation",
        "type": "analysis",
        "complexity": 0.7
    }

def test_estimate_task_cost(cost_estimator, sample_task):
    """Test cost estimation for a task"""
    metrics = cost_estimator.estimate_task_cost(sample_task, "gpt-4-turbo-preview")
    
    assert isinstance(metrics, CostMetrics)
    assert metrics.estimated_tokens > 0
    assert metrics.estimated_cost > 0
    assert 0 <= metrics.confidence <= 1
    assert isinstance(metrics.timestamp, datetime)
    assert metrics.model_name == "gpt-4-turbo-preview"
    assert metrics.task_type == "analysis"
    assert isinstance(metrics.resource_requirements, dict)

def test_estimate_tokens(cost_estimator):
    """Test token estimation"""
    task = {"description": "Test task with five words"}
    tokens = cost_estimator._estimate_tokens(task)
    assert tokens == 6.5  # 5 words * 1.3 tokens per word

def test_calculate_token_cost(cost_estimator):
    """Test token cost calculation"""
    # Test with GPT-4
    cost = cost_estimator._calculate_token_cost(1000, "gpt-4-turbo-preview")
    assert cost > 0
    
    # Test with unknown model
    cost = cost_estimator._calculate_token_cost(1000, "unknown-model")
    assert cost == 0

def test_estimate_resource_requirements(cost_estimator):
    """Test resource requirements estimation"""
    # Test training task
    training_task = {"type": "training"}
    reqs = cost_estimator._estimate_resource_requirements(training_task)
    assert reqs["gpu"] == 60.0
    assert reqs["memory"] == 200.0
    
    # Test inference task
    inference_task = {"type": "inference"}
    reqs = cost_estimator._estimate_resource_requirements(inference_task)
    assert reqs["gpu"] == 5.0
    
    # Test analysis task
    analysis_task = {"type": "analysis"}
    reqs = cost_estimator._estimate_resource_requirements(analysis_task)
    assert reqs["cpu"] == 2.0
    assert reqs["memory"] == 150.0

def test_calculate_resource_cost(cost_estimator):
    """Test resource cost calculation"""
    requirements = {
        "cpu": 10.0,
        "memory": 100.0,
        "gpu": 5.0,
        "storage": 10.0
    }
    cost = cost_estimator._calculate_resource_cost(requirements)
    assert cost > 0

def test_calculate_confidence(cost_estimator):
    """Test confidence calculation"""
    # Test simple task
    simple_task = {"complexity": 0.3, "type": "inference"}
    confidence = cost_estimator._calculate_confidence(simple_task)
    assert confidence > 0.7
    
    # Test complex task
    complex_task = {"complexity": 0.8, "type": "training"}
    confidence = cost_estimator._calculate_confidence(complex_task)
    assert confidence < 0.7

def test_error_handling(cost_estimator):
    """Test error handling"""
    # Test with invalid task
    with pytest.raises(Exception):
        cost_estimator.estimate_task_cost({}, "gpt-4-turbo-preview")
    
    # Test with invalid model
    with pytest.raises(Exception):
        cost_estimator.estimate_task_cost({"description": "test"}, None)

def test_cost_metrics_validation(cost_estimator, sample_task):
    """Test CostMetrics validation"""
    metrics = cost_estimator.estimate_task_cost(sample_task, "gpt-4-turbo-preview")
    
    # Test required fields
    assert hasattr(metrics, "estimated_tokens")
    assert hasattr(metrics, "estimated_cost")
    assert hasattr(metrics, "confidence")
    assert hasattr(metrics, "timestamp")
    assert hasattr(metrics, "model_name")
    assert hasattr(metrics, "task_type")
    assert hasattr(metrics, "resource_requirements")
    
    # Test value ranges
    assert metrics.estimated_tokens >= 0
    assert metrics.estimated_cost >= 0
    assert 0 <= metrics.confidence <= 1
    assert isinstance(metrics.timestamp, datetime)
    assert isinstance(metrics.resource_requirements, dict) 