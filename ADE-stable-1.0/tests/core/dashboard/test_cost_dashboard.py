import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.core.dashboard.cost_dashboard import CostDashboard, CostMetrics

@pytest.fixture
def cost_dashboard(tmp_path):
    return CostDashboard(data_dir=str(tmp_path))

@pytest.fixture
def sample_metrics():
    return CostMetrics(
        timestamp=datetime.now(),
        model_name="gpt-4-turbo-preview",
        task_type="analysis",
        token_usage={"input": 100, "output": 50},
        resource_usage={"cpu": 0.7, "memory": 0.6},
        cost=0.01,
        confidence=0.9
    )

def test_initialize_dashboard(cost_dashboard):
    """Test dashboard initialization"""
    assert hasattr(cost_dashboard, "metrics_history")
    assert hasattr(cost_dashboard, "current_metrics")
    assert hasattr(cost_dashboard, "budgets")
    assert isinstance(cost_dashboard.metrics_history, dict)
    assert isinstance(cost_dashboard.current_metrics, dict)
    assert isinstance(cost_dashboard.budgets, dict)

def test_record_metrics(cost_dashboard, sample_metrics):
    """Test recording metrics"""
    cost_dashboard.record_metrics(sample_metrics)
    
    assert sample_metrics.model_name in cost_dashboard.current_metrics
    assert sample_metrics.model_name in cost_dashboard.metrics_history
    assert len(cost_dashboard.metrics_history[sample_metrics.model_name]) == 1

def test_set_budget(cost_dashboard):
    """Test setting budget"""
    model_name = "gpt-4-turbo-preview"
    budget = 100.0
    
    cost_dashboard.set_budget(model_name, budget)
    assert cost_dashboard.budgets[model_name] == budget

def test_get_cost_summary(cost_dashboard, sample_metrics):
    """Test getting cost summary"""
    cost_dashboard.record_metrics(sample_metrics)
    summary = cost_dashboard.get_cost_summary(timedelta(hours=1))
    
    assert sample_metrics.model_name in summary
    model_summary = summary[sample_metrics.model_name]
    
    assert model_summary["total_cost"] == 0.01
    assert model_summary["avg_cost"] == 0.01
    assert model_summary["total_tokens"] == 150
    assert model_summary["cost_per_token"] == 0.01 / 150
    assert model_summary["budget"] == 0
    assert model_summary["budget_remaining"] == 0
    assert model_summary["num_requests"] == 1

def test_get_cost_alerts(cost_dashboard, sample_metrics):
    """Test getting cost alerts"""
    # Test with normal metrics
    cost_dashboard.record_metrics(sample_metrics)
    alerts = cost_dashboard.get_cost_alerts()
    assert len(alerts) == 0
    
    # Test with high cost per token
    high_cost_metrics = CostMetrics(
        timestamp=datetime.now(),
        model_name=sample_metrics.model_name,
        task_type="analysis",
        token_usage={"input": 100, "output": 50},
        resource_usage={"cpu": 0.7, "memory": 0.6},
        cost=2.0,  # High cost
        confidence=0.9
    )
    cost_dashboard.record_metrics(high_cost_metrics)
    alerts = cost_dashboard.get_cost_alerts()
    assert len(alerts) > 0
    assert any(a["type"] == "high_cost_per_token" for a in alerts)
    
    # Test with budget exceeded
    cost_dashboard.set_budget(sample_metrics.model_name, 1.0)
    alerts = cost_dashboard.get_cost_alerts()
    assert any(a["type"] == "budget_exceeded" for a in alerts)

def test_get_cost_trends(cost_dashboard, sample_metrics):
    """Test getting cost trends"""
    cost_dashboard.record_metrics(sample_metrics)
    trends = cost_dashboard.get_cost_trends(sample_metrics.model_name, timedelta(hours=1))
    
    assert "costs" in trends
    assert "timestamps" in trends
    assert "total_cost" in trends
    assert "avg_cost" in trends
    assert "cost_trend" in trends
    assert "num_requests" in trends
    
    assert len(trends["costs"]) == 1
    assert len(trends["timestamps"]) == 1
    assert trends["total_cost"] == 0.01
    assert trends["avg_cost"] == 0.01
    assert trends["num_requests"] == 1

def test_data_persistence(cost_dashboard, sample_metrics):
    """Test data persistence"""
    # Record metrics and set budget
    cost_dashboard.record_metrics(sample_metrics)
    cost_dashboard.set_budget(sample_metrics.model_name, 100.0)
    
    # Create new dashboard instance
    new_dashboard = CostDashboard(data_dir=cost_dashboard.data_dir)
    
    # Check that data was persisted
    assert sample_metrics.model_name in new_dashboard.metrics_history
    assert len(new_dashboard.metrics_history[sample_metrics.model_name]) == 1
    assert new_dashboard.budgets[sample_metrics.model_name] == 100.0

def test_error_handling(cost_dashboard):
    """Test error handling"""
    # Test with invalid metrics
    with pytest.raises(Exception):
        cost_dashboard.record_metrics(None)
    
    # Test with invalid model name
    trends = cost_dashboard.get_cost_trends("nonexistent_model")
    assert trends == {}

def test_data_validation(cost_dashboard, sample_metrics):
    """Test data validation"""
    # Test with invalid timestamp
    invalid_metrics = CostMetrics(
        timestamp=None,  # Invalid timestamp
        model_name=sample_metrics.model_name,
        task_type=sample_metrics.task_type,
        token_usage=sample_metrics.token_usage,
        resource_usage=sample_metrics.resource_usage,
        cost=sample_metrics.cost,
        confidence=sample_metrics.confidence
    )
    with pytest.raises(Exception):
        cost_dashboard.record_metrics(invalid_metrics)
    
    # Test with invalid cost
    invalid_metrics = CostMetrics(
        timestamp=sample_metrics.timestamp,
        model_name=sample_metrics.model_name,
        task_type=sample_metrics.task_type,
        token_usage=sample_metrics.token_usage,
        resource_usage=sample_metrics.resource_usage,
        cost=-1.0,  # Invalid cost
        confidence=sample_metrics.confidence
    )
    with pytest.raises(Exception):
        cost_dashboard.record_metrics(invalid_metrics) 