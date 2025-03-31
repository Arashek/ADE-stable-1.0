import pytest
from datetime import datetime, timedelta
from src.core.cost.ml_cost_optimizer import MLCostOptimizer, CostPrediction

@pytest.fixture
def ml_optimizer(tmp_path):
    return MLCostOptimizer(data_dir=str(tmp_path))

@pytest.fixture
def sample_task():
    return {
        "id": "task-123",
        "description": "Analyze code and generate documentation",
        "type": "analysis",
        "complexity": 0.7
    }

@pytest.fixture
def sample_resource_metrics():
    return {
        "cpu_percent": 50.0,
        "memory_percent": 60.0,
        "gpu_percent": 30.0
    }

@pytest.fixture
def sample_predictions():
    return [
        CostPrediction(
            timestamp=datetime.now() - timedelta(hours=i),
            model_name="gpt-4-turbo-preview",
            task_type="analysis",
            predicted_cost=0.5,
            confidence=0.8,
            features={
                "task_complexity": 0.7,
                "task_length": 100,
                "model_cost_per_1k": 0.03,
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "gpu_usage": 30.0,
                "hour_of_day": 12,
                "day_of_week": 1,
                "is_weekend": 0
            },
            actual_cost=0.45
        )
        for i in range(150)  # More than min_samples
    ]

def test_initialize_optimizer(ml_optimizer):
    """Test optimizer initialization"""
    assert ml_optimizer.model is not None
    assert ml_optimizer.scaler is not None
    assert len(ml_optimizer.predictions) == 0
    assert ml_optimizer.min_samples == 100
    assert ml_optimizer.model_update_interval == 24

def test_extract_features(ml_optimizer, sample_task, sample_resource_metrics):
    """Test feature extraction"""
    features = ml_optimizer._extract_features(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    assert "task_complexity" in features
    assert "task_length" in features
    assert "model_cost_per_1k" in features
    assert "cpu_usage" in features
    assert "memory_usage" in features
    assert "gpu_usage" in features
    assert "hour_of_day" in features
    assert "day_of_week" in features
    assert "is_weekend" in features
    
    assert features["task_complexity"] == 0.7
    assert features["task_length"] == len(sample_task["description"])
    assert features["model_cost_per_1k"] == 0.03

def test_get_model_cost_per_1k(ml_optimizer):
    """Test model cost per 1k tokens retrieval"""
    assert ml_optimizer._get_model_cost_per_1k("gpt-4-turbo-preview") == 0.03
    assert ml_optimizer._get_model_cost_per_1k("gpt-3.5-turbo") == 0.002
    assert ml_optimizer._get_model_cost_per_1k("codellama/CodeLlama-13b") == 0.0
    assert ml_optimizer._get_model_cost_per_1k("unknown-model") == 0.01

def test_predict_cost(ml_optimizer, sample_task, sample_resource_metrics):
    """Test cost prediction"""
    prediction = ml_optimizer.predict_cost(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    assert isinstance(prediction, CostPrediction)
    assert prediction.model_name == "gpt-4-turbo-preview"
    assert prediction.task_type == "analysis"
    assert prediction.predicted_cost >= 0
    assert 0 <= prediction.confidence <= 1
    assert prediction.actual_cost is None
    assert len(prediction.features) > 0

def test_record_actual_cost(ml_optimizer, sample_task, sample_resource_metrics):
    """Test recording actual cost"""
    prediction = ml_optimizer.predict_cost(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    actual_cost = 0.45
    ml_optimizer.record_actual_cost(prediction, actual_cost)
    
    assert prediction.actual_cost == actual_cost
    assert len(ml_optimizer.predictions) == 1
    assert ml_optimizer.predictions[0].actual_cost == actual_cost

def test_get_cost_optimization_suggestions(ml_optimizer, sample_task):
    """Test cost optimization suggestions"""
    # Test with high resource usage
    high_resource_metrics = {
        "cpu_percent": 85.0,
        "memory_percent": 90.0,
        "gpu_percent": 30.0
    }
    
    suggestions = ml_optimizer.get_cost_optimization_suggestions(
        sample_task,
        current_cost=1.0,
        resource_metrics=high_resource_metrics
    )
    
    assert len(suggestions) > 0
    assert any(s["type"] == "resource_optimization" for s in suggestions)
    
    # Test with historical data
    ml_optimizer.predictions = [
        CostPrediction(
            timestamp=datetime.now() - timedelta(hours=i),
            model_name="gpt-4-turbo-preview",
            task_type="analysis",
            predicted_cost=0.5,
            confidence=0.8,
            features={},
            actual_cost=0.5
        )
        for i in range(10)
    ]
    
    suggestions = ml_optimizer.get_cost_optimization_suggestions(
        sample_task,
        current_cost=1.0,
        resource_metrics=sample_resource_metrics
    )
    
    assert len(suggestions) > 0
    assert any(s["type"] == "cost_reduction" for s in suggestions)

def test_get_cost_trends(ml_optimizer, sample_predictions):
    """Test cost trend analysis"""
    ml_optimizer.predictions = sample_predictions
    
    trends = ml_optimizer.get_cost_trends(time_window=timedelta(days=7))
    
    assert "total_cost" in trends
    assert "average_cost" in trends
    assert "cost_trend" in trends
    assert "model_costs" in trends
    assert "task_type_costs" in trends
    
    assert trends["total_cost"] > 0
    assert trends["average_cost"] > 0
    assert "gpt-4-turbo-preview" in trends["model_costs"]
    assert "analysis" in trends["task_type_costs"]

def test_model_update_interval(ml_optimizer, sample_predictions):
    """Test model update interval checking"""
    ml_optimizer.predictions = sample_predictions
    
    # Test with recent predictions
    assert not ml_optimizer._should_update_model()
    
    # Test with old predictions
    old_predictions = [
        CostPrediction(
            timestamp=datetime.now() - timedelta(hours=25),
            model_name="gpt-4-turbo-preview",
            task_type="analysis",
            predicted_cost=0.5,
            confidence=0.8,
            features={},
            actual_cost=0.5
        )
    ]
    ml_optimizer.predictions = old_predictions
    assert ml_optimizer._should_update_model()

def test_calculate_confidence(ml_optimizer):
    """Test confidence calculation"""
    # Test with low variance features
    low_variance_features = {
        "task_complexity": 0.7,
        "task_length": 100,
        "model_cost_per_1k": 0.03,
        "cpu_usage": 50.0,
        "memory_usage": 50.0,
        "gpu_usage": 50.0,
        "hour_of_day": 12,
        "day_of_week": 1,
        "is_weekend": 0
    }
    confidence = ml_optimizer._calculate_confidence(low_variance_features)
    assert confidence > 0.8
    
    # Test with high variance features
    high_variance_features = {
        "task_complexity": 0.7,
        "task_length": 1000,
        "model_cost_per_1k": 0.03,
        "cpu_usage": 90.0,
        "memory_usage": 10.0,
        "gpu_usage": 50.0,
        "hour_of_day": 12,
        "day_of_week": 1,
        "is_weekend": 0
    }
    confidence = ml_optimizer._calculate_confidence(high_variance_features)
    assert confidence < 0.8

def test_error_handling(ml_optimizer, sample_task, sample_resource_metrics):
    """Test error handling"""
    # Test with invalid task
    with pytest.raises(Exception):
        ml_optimizer.predict_cost({}, "gpt-4-turbo-preview", sample_resource_metrics)
    
    # Test with invalid model name
    prediction = ml_optimizer.predict_cost(
        sample_task,
        "invalid-model",
        sample_resource_metrics
    )
    assert prediction.predicted_cost == 0.0
    assert prediction.confidence == 0.0
    
    # Test with invalid resource metrics
    prediction = ml_optimizer.predict_cost(
        sample_task,
        "gpt-4-turbo-preview",
        {}
    )
    assert prediction.predicted_cost >= 0
    assert 0 <= prediction.confidence <= 1 