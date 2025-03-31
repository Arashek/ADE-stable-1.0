import pytest
from datetime import datetime, timedelta
from src.core.cost.ml_ensemble import MLEnsemble, EnhancedFeatures

@pytest.fixture
def ml_ensemble(tmp_path):
    return MLEnsemble(data_dir=str(tmp_path))

@pytest.fixture
def sample_task():
    return {
        "id": "task-123",
        "description": "Implement a complex algorithm with multiple functions and classes",
        "type": "development",
        "complexity": 0.8,
        "priority": 0.9,
        "urgency": 0.7,
        "dependencies": ["task-100", "task-101"]
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
        {
            "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
            "model_name": "gpt-4-turbo-preview",
            "task_type": "development",
            "predicted_cost": 0.5,
            "confidence": 0.8,
            "features": {
                "basic": {
                    "task_complexity": 0.8,
                    "task_length": 100,
                    "model_cost_per_1k": 0.03,
                    "cpu_usage": 50.0,
                    "memory_usage": 60.0,
                    "gpu_usage": 30.0
                },
                "derived": {
                    "resource_utilization": 46.67,
                    "task_density": 80.0,
                    "cost_efficiency": 0.024
                },
                "temporal": {
                    "hour_of_day": 12,
                    "day_of_week": 1,
                    "is_weekend": 0,
                    "is_business_hour": 1,
                    "is_peak_hour": 1,
                    "month": 3,
                    "season": 1
                },
                "resource": {
                    "cpu_memory_ratio": 0.833,
                    "gpu_utilization": 0.3,
                    "resource_saturation": 0.6
                },
                "task": {
                    "complexity_score": 0.8,
                    "priority_score": 0.9,
                    "urgency_score": 0.7,
                    "dependency_score": 0.2
                }
            },
            "actual_cost": 0.45
        }
        for i in range(150)  # More than min_samples
    ]

def test_initialize_ensemble(ml_ensemble):
    """Test ensemble initialization"""
    assert ml_ensemble.rf_model is not None
    assert ml_ensemble.gb_model is not None
    assert ml_ensemble.ensemble is not None
    assert ml_ensemble.scaler is not None
    assert ml_ensemble.feature_selector is not None
    assert len(ml_ensemble.predictions) == 0
    assert ml_ensemble.min_samples == 100
    assert ml_ensemble.model_update_interval == 24

def test_extract_enhanced_features(ml_ensemble, sample_task, sample_resource_metrics):
    """Test enhanced feature extraction"""
    features = ml_ensemble._extract_enhanced_features(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    # Test basic features
    assert "task_complexity" in features.basic_features
    assert "task_length" in features.basic_features
    assert "model_cost_per_1k" in features.basic_features
    assert "cpu_usage" in features.basic_features
    assert "memory_usage" in features.basic_features
    assert "gpu_usage" in features.basic_features
    
    # Test derived features
    assert "resource_utilization" in features.derived_features
    assert "task_density" in features.derived_features
    assert "cost_efficiency" in features.derived_features
    
    # Test temporal features
    assert "hour_of_day" in features.temporal_features
    assert "day_of_week" in features.temporal_features
    assert "is_weekend" in features.temporal_features
    assert "is_business_hour" in features.temporal_features
    assert "is_peak_hour" in features.temporal_features
    assert "month" in features.temporal_features
    assert "season" in features.temporal_features
    
    # Test resource features
    assert "cpu_memory_ratio" in features.resource_features
    assert "gpu_utilization" in features.resource_features
    assert "resource_saturation" in features.resource_features
    
    # Test task features
    assert "complexity_score" in features.task_features
    assert "priority_score" in features.task_features
    assert "urgency_score" in features.task_features
    assert "dependency_score" in features.task_features

def test_calculate_complexity_score(ml_ensemble):
    """Test complexity score calculation"""
    # Test with high complexity task
    high_complexity_task = {
        "description": "Implement complex algorithm with multiple functions, classes, and optimization",
        "complexity": 0.9
    }
    score = ml_ensemble._calculate_complexity_score(high_complexity_task)
    assert score > 0.8
    
    # Test with low complexity task
    low_complexity_task = {
        "description": "Simple task",
        "complexity": 0.3
    }
    score = ml_ensemble._calculate_complexity_score(low_complexity_task)
    assert score < 0.5

def test_predict_cost(ml_ensemble, sample_task, sample_resource_metrics):
    """Test cost prediction"""
    prediction = ml_ensemble.predict_cost(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    assert "timestamp" in prediction
    assert "model_name" in prediction
    assert "task_type" in prediction
    assert "predicted_cost" in prediction
    assert "confidence" in prediction
    assert "features" in prediction
    
    assert prediction["model_name"] == "gpt-4-turbo-preview"
    assert prediction["task_type"] == "development"
    assert prediction["predicted_cost"] >= 0
    assert 0 <= prediction["confidence"] <= 1
    assert len(prediction["features"]) == 5  # All feature categories

def test_calculate_confidence(ml_ensemble, sample_task, sample_resource_metrics):
    """Test confidence calculation"""
    features = ml_ensemble._extract_enhanced_features(
        sample_task,
        "gpt-4-turbo-preview",
        sample_resource_metrics
    )
    
    confidence = ml_ensemble._calculate_confidence(features)
    assert 0 <= confidence <= 1
    
    # Test with high variance features
    high_variance_metrics = {
        "cpu_percent": 90.0,
        "memory_percent": 10.0,
        "gpu_percent": 50.0
    }
    high_variance_features = ml_ensemble._extract_enhanced_features(
        sample_task,
        "gpt-4-turbo-preview",
        high_variance_metrics
    )
    high_variance_confidence = ml_ensemble._calculate_confidence(high_variance_features)
    assert high_variance_confidence < confidence

def test_visualize_cost_trends(ml_ensemble, sample_predictions):
    """Test cost trend visualization"""
    ml_ensemble.predictions = sample_predictions
    
    fig = ml_ensemble.visualize_cost_trends(time_window=timedelta(days=7))
    
    assert fig is not None
    assert len(fig.data) > 0
    assert fig.layout.title.text == "Cost Analysis Dashboard"
    
    # Check subplot titles
    subplot_titles = [
        "Cost Over Time",
        "Cost by Model",
        "Cost by Task Type",
        "Resource Usage vs Cost",
        "Prediction Confidence",
        "Feature Importance"
    ]
    for title in subplot_titles:
        assert title in fig.layout.annotations

def test_get_feature_importance(ml_ensemble, sample_predictions):
    """Test feature importance calculation"""
    ml_ensemble.predictions = sample_predictions
    
    importance = ml_ensemble.get_feature_importance()
    assert isinstance(importance, dict)
    assert len(importance) > 0
    
    # Check that all feature categories are represented
    feature_categories = ["basic", "derived", "temporal", "resource", "task"]
    for category in feature_categories:
        assert any(category in feature for feature in importance.keys())

def test_get_model_performance_metrics(ml_ensemble, sample_predictions):
    """Test model performance metrics calculation"""
    ml_ensemble.predictions = sample_predictions
    
    metrics = ml_ensemble.get_model_performance_metrics()
    
    assert "mse" in metrics
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "r2" in metrics
    assert "total_predictions" in metrics
    assert "feature_importance" in metrics
    
    assert metrics["total_predictions"] == len(sample_predictions)
    assert metrics["mse"] >= 0
    assert metrics["rmse"] >= 0
    assert metrics["mae"] >= 0
    assert 0 <= metrics["r2"] <= 1

def test_error_handling(ml_ensemble, sample_task, sample_resource_metrics):
    """Test error handling"""
    # Test with invalid task
    with pytest.raises(Exception):
        ml_ensemble.predict_cost({}, "gpt-4-turbo-preview", sample_resource_metrics)
    
    # Test with invalid model name
    prediction = ml_ensemble.predict_cost(
        sample_task,
        "invalid-model",
        sample_resource_metrics
    )
    assert prediction["predicted_cost"] == 0.0
    assert prediction["confidence"] == 0.0
    
    # Test with invalid resource metrics
    prediction = ml_ensemble.predict_cost(
        sample_task,
        "gpt-4-turbo-preview",
        {}
    )
    assert prediction["predicted_cost"] >= 0
    assert 0 <= prediction["confidence"] <= 1

def test_historical_similarity(ml_ensemble, sample_predictions):
    """Test historical similarity calculation"""
    ml_ensemble.predictions = sample_predictions
    
    # Create similar features
    similar_features = ml_ensemble._extract_enhanced_features(
        {
            "description": "Similar task",
            "type": "development",
            "complexity": 0.8
        },
        "gpt-4-turbo-preview",
        {"cpu_percent": 50.0, "memory_percent": 60.0, "gpu_percent": 30.0}
    )
    
    # Create dissimilar features
    dissimilar_features = ml_ensemble._extract_enhanced_features(
        {
            "description": "Different task",
            "type": "analysis",
            "complexity": 0.3
        },
        "gpt-3.5-turbo",
        {"cpu_percent": 90.0, "memory_percent": 10.0, "gpu_percent": 80.0}
    )
    
    similar_score = ml_ensemble._calculate_historical_similarity(similar_features)
    dissimilar_score = ml_ensemble._calculate_historical_similarity(dissimilar_features)
    
    assert similar_score > dissimilar_score
    assert 0 <= similar_score <= 1
    assert 0 <= dissimilar_score <= 1 