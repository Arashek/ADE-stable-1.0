from typing import Dict, Any, Optional, Union, List
import numpy as np
from enum import Enum
from dataclasses import dataclass
import logging
from datetime import datetime

from ...utils.logging import get_logger
from ...config import Config
from ..models.privacy_settings import PrivacyLevel

logger = get_logger(__name__)

class MetricType(str, Enum):
    """Types of metrics that can be anonymized"""
    RATE = "rate"           # Values between 0 and 1
    COUNT = "count"         # Non-negative integers
    TIME = "time"          # Time measurements in seconds
    SCORE = "score"        # Arbitrary numeric scores
    DISTRIBUTION = "distribution"  # Probability distributions

@dataclass
class MetricConfig:
    """Configuration for metric anonymization"""
    type: MetricType
    sensitivity: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    rounding: Optional[int] = None
    scale_factor: float = 1.0
    description: str = ""

class DifferentialPrivacy:
    """Component for adding differential privacy to numeric data"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the differential privacy component.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self._metric_configs: Dict[str, MetricConfig] = {}
        self._initialize_metric_configs()
        
    def _initialize_metric_configs(self) -> None:
        """Initialize default metric configurations"""
        self._metric_configs = {
            "success_rate": MetricConfig(
                type=MetricType.RATE,
                sensitivity=0.01,  # 1% change in success rate
                min_value=0.0,
                max_value=1.0,
                rounding=4,
                description="Success rate of pattern application"
            ),
            "error_rate": MetricConfig(
                type=MetricType.RATE,
                sensitivity=0.01,
                min_value=0.0,
                max_value=1.0,
                rounding=4,
                description="Error rate during pattern application"
            ),
            "usage_count": MetricConfig(
                type=MetricType.COUNT,
                sensitivity=1.0,
                min_value=0,
                rounding=0,
                description="Number of times a pattern has been used"
            ),
            "average_duration": MetricConfig(
                type=MetricType.TIME,
                sensitivity=0.1,  # 100ms change in duration
                min_value=0,
                rounding=2,
                description="Average duration of pattern application"
            ),
            "confidence_score": MetricConfig(
                type=MetricType.SCORE,
                sensitivity=0.05,
                min_value=0.0,
                max_value=1.0,
                rounding=3,
                description="Confidence in pattern effectiveness"
            )
        }
    
    def add_noise(
        self,
        value: float,
        metric_name: str,
        epsilon: float,
        privacy_level: PrivacyLevel
    ) -> float:
        """
        Add Laplace noise to a value based on metric configuration and privacy settings.
        
        Args:
            value: Original value to anonymize
            metric_name: Name of the metric (must be configured)
            epsilon: Privacy budget parameter
            privacy_level: Privacy protection level
            
        Returns:
            float: Anonymized value
            
        Raises:
            ValueError: If metric is not configured or value is invalid
        """
        if metric_name not in self._metric_configs:
            raise ValueError(f"Metric '{metric_name}' not configured")
            
        metric_config = self._metric_configs[metric_name]
        
        # Validate input value
        if metric_config.min_value is not None and value < metric_config.min_value:
            raise ValueError(f"Value {value} below minimum {metric_config.min_value}")
        if metric_config.max_value is not None and value > metric_config.max_value:
            raise ValueError(f"Value {value} above maximum {metric_config.max_value}")
            
        # Calculate noise scale based on sensitivity and epsilon
        scale = metric_config.sensitivity / epsilon
        
        # Generate Laplace noise
        noise = np.random.laplace(0, scale)
        
        # Apply noise and scale factor
        noisy_value = value + (noise * metric_config.scale_factor)
        
        # Apply bounds
        if metric_config.min_value is not None:
            noisy_value = max(metric_config.min_value, noisy_value)
        if metric_config.max_value is not None:
            noisy_value = min(metric_config.max_value, noisy_value)
            
        # Apply rounding if specified
        if metric_config.rounding is not None:
            noisy_value = round(noisy_value, metric_config.rounding)
            
        # Log anonymization details
        logger.debug(
            f"Anonymized {metric_name}: {value} -> {noisy_value} "
            f"(epsilon={epsilon}, noise={noise:.6f})"
        )
        
        return noisy_value
    
    def anonymize_metrics(
        self,
        metrics: Dict[str, float],
        epsilon: float,
        privacy_level: PrivacyLevel
    ) -> Dict[str, float]:
        """
        Anonymize multiple metrics at once.
        
        Args:
            metrics: Dictionary of metric names and values
            epsilon: Privacy budget parameter
            privacy_level: Privacy protection level
            
        Returns:
            Dict[str, float]: Dictionary of anonymized metrics
        """
        return {
            name: self.add_noise(value, name, epsilon, privacy_level)
            for name, value in metrics.items()
            if name in self._metric_configs
        }
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        sensitivity: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        rounding: Optional[int] = None,
        scale_factor: float = 1.0,
        description: str = ""
    ) -> None:
        """
        Register a new metric configuration.
        
        Args:
            name: Name of the metric
            metric_type: Type of the metric
            sensitivity: Sensitivity of the metric
            min_value: Optional minimum value
            max_value: Optional maximum value
            rounding: Optional number of decimal places
            scale_factor: Optional scaling factor for noise
            description: Description of the metric
        """
        self._metric_configs[name] = MetricConfig(
            type=metric_type,
            sensitivity=sensitivity,
            min_value=min_value,
            max_value=max_value,
            rounding=rounding,
            scale_factor=scale_factor,
            description=description
        )
        logger.info(f"Registered new metric configuration: {name}")
    
    def get_metric_config(self, name: str) -> Optional[MetricConfig]:
        """
        Get the configuration for a metric.
        
        Args:
            name: Name of the metric
            
        Returns:
            Optional[MetricConfig]: Metric configuration if found
        """
        return self._metric_configs.get(name)
    
    def get_configured_metrics(self) -> List[str]:
        """
        Get list of configured metric names.
        
        Returns:
            List[str]: List of metric names
        """
        return list(self._metric_configs.keys())
    
    def calculate_epsilon(
        self,
        privacy_level: PrivacyLevel,
        metric_count: int = 1
    ) -> float:
        """
        Calculate epsilon value based on privacy level and number of metrics.
        
        Args:
            privacy_level: Privacy protection level
            metric_count: Number of metrics being anonymized
            
        Returns:
            float: Calculated epsilon value
        """
        base_epsilon = {
            PrivacyLevel.LOW: 1.0,
            PrivacyLevel.MEDIUM: 0.5,
            PrivacyLevel.HIGH: 0.1
        }[privacy_level]
        
        # Divide epsilon by number of metrics to maintain privacy budget
        return base_epsilon / metric_count
    
    def validate_metrics(
        self,
        metrics: Dict[str, float]
    ) -> Dict[str, str]:
        """
        Validate a set of metrics against their configurations.
        
        Args:
            metrics: Dictionary of metric names and values
            
        Returns:
            Dict[str, str]: Dictionary of validation errors (empty if valid)
        """
        errors = {}
        for name, value in metrics.items():
            if name not in self._metric_configs:
                errors[name] = "Metric not configured"
                continue
                
            config = self._metric_configs[name]
            
            if config.min_value is not None and value < config.min_value:
                errors[name] = f"Value {value} below minimum {config.min_value}"
            if config.max_value is not None and value > config.max_value:
                errors[name] = f"Value {value} above maximum {config.max_value}"
                
        return errors 