import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import logging
from dataclasses import dataclass
import json
import hashlib
import re
from datetime import datetime

@dataclass
class PrivacyConfig:
    epsilon: float = 1.0  # Privacy budget
    delta: float = 1e-5   # Failure probability
    sensitivity: float = 1.0  # Global sensitivity
    noise_scale: float = 1.0  # Noise scaling factor
    min_value: Optional[float] = None  # Minimum allowed value
    max_value: Optional[float] = None  # Maximum allowed value
    anonymization_level: str = "medium"  # low, medium, high
    retention_days: int = 90  # Data retention period
    allow_aggregation: bool = True  # Allow aggregation of anonymized data
    allow_learning: bool = True  # Allow use in ML training
    allow_sharing: bool = False  # Allow sharing with third parties

class PrivacyEngine:
    def __init__(self, config: Optional[PrivacyConfig] = None):
        self.config = config or PrivacyConfig()
        self.logger = logging.getLogger(__name__)
        self._init_noise_distribution()

    def _init_noise_distribution(self):
        """Initialize the noise distribution based on privacy parameters."""
        self.noise_scale = self.config.sensitivity / self.config.epsilon
        self.noise_distribution = np.random.normal(0, self.noise_scale)

    def add_noise(self, value: float) -> float:
        """Add Laplace noise to a value for differential privacy."""
        noise = np.random.laplace(0, self.config.sensitivity / self.config.epsilon)
        noisy_value = value + noise

        # Clip values if min/max are specified
        if self.config.min_value is not None:
            noisy_value = max(noisy_value, self.config.min_value)
        if self.config.max_value is not None:
            noisy_value = min(noisy_value, self.config.max_value)

        return noisy_value

    def anonymize_text(self, text: str) -> str:
        """Anonymize text by replacing sensitive information."""
        # Email addresses
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)
        
        # Phone numbers
        text = re.sub(r'\+?[\d\s-()]{10,}', '[PHONE]', text)
        
        # IP addresses
        text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
        
        # Credit card numbers
        text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CC]', text)
        
        # Social security numbers
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        return text

    def anonymize_metadata(self, metadata: Dict) -> Dict:
        """Anonymize metadata by removing or hashing sensitive fields."""
        anonymized = metadata.copy()
        
        # Fields to hash
        hash_fields = ['user_id', 'session_id', 'device_id']
        for field in hash_fields:
            if field in anonymized:
                anonymized[field] = self._hash_value(anonymized[field])
        
        # Fields to remove
        remove_fields = ['ip_address', 'user_agent', 'location']
        for field in remove_fields:
            anonymized.pop(field, None)
        
        # Fields to generalize
        if 'timestamp' in anonymized:
            anonymized['timestamp'] = self._generalize_timestamp(anonymized['timestamp'])
        
        return anonymized

    def _hash_value(self, value: str) -> str:
        """Hash a value using SHA-256."""
        return hashlib.sha256(value.encode()).hexdigest()

    def _generalize_timestamp(self, timestamp: Union[str, datetime]) -> str:
        """Generalize timestamp to a less specific format."""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # Round to nearest hour
        return timestamp.replace(minute=0, second=0, microsecond=0).isoformat()

    def aggregate_with_privacy(
        self,
        values: List[float],
        aggregation_type: str = 'mean'
    ) -> Tuple[float, float]:
        """Aggregate values with differential privacy guarantees."""
        if not values:
            return 0.0, 0.0

        # Calculate the true aggregate
        if aggregation_type == 'mean':
            true_value = np.mean(values)
        elif aggregation_type == 'sum':
            true_value = sum(values)
        elif aggregation_type == 'median':
            true_value = np.median(values)
        else:
            raise ValueError(f"Unsupported aggregation type: {aggregation_type}")

        # Add noise to the aggregate
        noisy_value = self.add_noise(true_value)
        
        # Calculate confidence interval
        confidence = self._calculate_confidence_interval(len(values))
        
        return noisy_value, confidence

    def _calculate_confidence_interval(self, n: int) -> float:
        """Calculate the confidence interval for the noisy estimate."""
        # Using Hoeffding's inequality for bounded random variables
        confidence = np.sqrt(2 * np.log(2 / self.config.delta) / n)
        return confidence

    def check_privacy_budget(self, operation_cost: float) -> bool:
        """Check if there's enough privacy budget for an operation."""
        return operation_cost <= self.config.epsilon

    def update_privacy_budget(self, operation_cost: float):
        """Update the privacy budget after an operation."""
        if not self.check_privacy_budget(operation_cost):
            raise ValueError("Operation would exceed privacy budget")
        self.config.epsilon -= operation_cost
        self._init_noise_distribution()

    def generate_privacy_report(self) -> Dict:
        """Generate a report on privacy settings and usage."""
        return {
            "privacy_budget": {
                "epsilon": self.config.epsilon,
                "delta": self.config.delta,
                "sensitivity": self.config.sensitivity
            },
            "anonymization": {
                "level": self.config.anonymization_level,
                "noise_scale": self.noise_scale
            },
            "data_retention": {
                "days": self.config.retention_days
            },
            "permissions": {
                "allow_aggregation": self.config.allow_aggregation,
                "allow_learning": self.config.allow_learning,
                "allow_sharing": self.config.allow_sharing
            }
        }

    def validate_privacy_compliance(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate if data handling complies with privacy settings."""
        violations = []
        
        # Check data retention
        if 'timestamp' in data:
            age = (datetime.utcnow() - datetime.fromisoformat(data['timestamp'])).days
            if age > self.config.retention_days:
                violations.append(f"Data exceeds retention period of {self.config.retention_days} days")
        
        # Check anonymization level
        if 'text' in data and self.config.anonymization_level == 'high':
            if not self._is_fully_anonymized(data['text']):
                violations.append("Text contains potentially sensitive information")
        
        # Check metadata anonymization
        if 'metadata' in data:
            sensitive_fields = ['ip_address', 'user_agent', 'location']
            for field in sensitive_fields:
                if field in data['metadata']:
                    violations.append(f"Metadata contains sensitive field: {field}")
        
        return len(violations) == 0, violations

    def _is_fully_anonymized(self, text: str) -> bool:
        """Check if text is fully anonymized."""
        sensitive_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
            r'\+?[\d\s-()]{10,}',  # Phone
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # CC
            r'\b\d{3}-\d{2}-\d{4}\b'  # SSN
        ]
        
        return not any(re.search(pattern, text) for pattern in sensitive_patterns)

    def get_privacy_impact_assessment(self, operation: str) -> Dict:
        """Generate a privacy impact assessment for an operation."""
        impact_levels = {
            'low': {'risk': 'minimal', 'mitigation': 'standard controls'},
            'medium': {'risk': 'moderate', 'mitigation': 'enhanced controls'},
            'high': {'risk': 'significant', 'mitigation': 'strict controls'}
        }
        
        # Define operation impacts
        operation_impacts = {
            'aggregation': 'low',
            'learning': 'medium',
            'sharing': 'high',
            'storage': 'low',
            'deletion': 'medium'
        }
        
        impact_level = operation_impacts.get(operation, 'medium')
        impact = impact_levels[impact_level]
        
        return {
            "operation": operation,
            "risk_level": impact['risk'],
            "mitigation_strategy": impact['mitigation'],
            "privacy_budget_impact": self._calculate_budget_impact(operation),
            "recommendations": self._get_privacy_recommendations(operation)
        }

    def _calculate_budget_impact(self, operation: str) -> float:
        """Calculate the privacy budget impact of an operation."""
        impacts = {
            'aggregation': 0.1,
            'learning': 0.3,
            'sharing': 0.5,
            'storage': 0.05,
            'deletion': 0.2
        }
        return impacts.get(operation, 0.2)

    def _get_privacy_recommendations(self, operation: str) -> List[str]:
        """Get privacy recommendations for an operation."""
        recommendations = {
            'aggregation': [
                "Use minimum required precision",
                "Implement data minimization",
                "Regular privacy budget review"
            ],
            'learning': [
                "Implement model privacy guarantees",
                "Use federated learning where possible",
                "Regular model privacy audits"
            ],
            'sharing': [
                "Implement strict access controls",
                "Use data sharing agreements",
                "Regular third-party audits"
            ],
            'storage': [
                "Implement encryption at rest",
                "Regular security audits",
                "Access logging"
            ],
            'deletion': [
                "Implement secure deletion",
                "Verification of deletion",
                "Audit trail maintenance"
            ]
        }
        return recommendations.get(operation, ["Review privacy impact", "Implement standard controls"]) 