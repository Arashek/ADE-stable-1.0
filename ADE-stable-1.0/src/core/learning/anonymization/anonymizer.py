from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
import re
import hashlib
from dataclasses import dataclass
import logging

from ...utils.logging import get_logger
from ...config import Config
from ..models.pattern import BasePattern, SolutionPattern, ErrorRecoveryPattern, WorkflowPattern, ToolUsagePattern
from ..models.privacy_settings import PrivacySettings, PrivacyLevel
from .differential_privacy import DifferentialPrivacy, MetricType

logger = get_logger(__name__)

@dataclass
class AnonymizationContext:
    """Context for anonymization operations"""
    privacy_settings: PrivacySettings
    timestamp: datetime
    instance_id: str
    anonymization_version: str = "1.0"

class Anonymizer:
    """Component for anonymizing learning patterns"""
    
    # Fields that should be removed or anonymized
    SENSITIVE_FIELDS = {
        "user_id",
        "email",
        "ip_address",
        "hostname",
        "file_path",
        "command_line",
        "session_id",
        "token",
        "password",
        "api_key",
        "secret",
        "private_key",
        "certificate"
    }
    
    # Patterns for identifying sensitive information
    SENSITIVE_PATTERNS = {
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "hostname": r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
        "file_path": r'(?:/[^/]+)+',
        "token": r'[a-zA-Z0-9-_]{32,}'
    }
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the anonymizer component.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.dp = DifferentialPrivacy(config)
        self._initialize_compiled_patterns()
        
    def _initialize_compiled_patterns(self) -> None:
        """Initialize compiled regex patterns for sensitive information"""
        self.compiled_patterns = {
            key: re.compile(pattern)
            for key, pattern in self.SENSITIVE_PATTERNS.items()
        }
    
    def anonymize_pattern(
        self,
        pattern: BasePattern,
        context: AnonymizationContext
    ) -> BasePattern:
        """
        Anonymize a single pattern.
        
        Args:
            pattern: Pattern to anonymize
            context: Anonymization context
            
        Returns:
            BasePattern: Anonymized pattern
        """
        try:
            # Create a copy of the pattern
            anonymized = pattern.copy()
            
            # Anonymize context
            anonymized.context = self._anonymize_context(pattern.context)
            
            # Anonymize metadata
            anonymized.metadata = self._anonymize_metadata(pattern.metadata)
            
            # Apply differential privacy to metrics
            if hasattr(pattern, 'effectiveness'):
                anonymized.effectiveness = self._anonymize_effectiveness(
                    pattern.effectiveness,
                    context
                )
            
            # Update privacy metadata
            anonymized.privacy = self._update_privacy_metadata(
                pattern.privacy,
                context
            )
            
            # Anonymize type-specific fields
            if isinstance(pattern, SolutionPattern):
                anonymized = self._anonymize_solution_pattern(pattern, context)
            elif isinstance(pattern, ErrorRecoveryPattern):
                anonymized = self._anonymize_error_pattern(pattern, context)
            elif isinstance(pattern, WorkflowPattern):
                anonymized = self._anonymize_workflow_pattern(pattern, context)
            elif isinstance(pattern, ToolUsagePattern):
                anonymized = self._anonymize_tool_pattern(pattern, context)
            
            logger.debug(f"Anonymized pattern {pattern.pattern_id}")
            return anonymized
            
        except Exception as e:
            logger.error(f"Error anonymizing pattern {pattern.pattern_id}: {str(e)}")
            raise
    
    def anonymize_patterns(
        self,
        patterns: List[BasePattern],
        context: AnonymizationContext
    ) -> List[BasePattern]:
        """
        Anonymize multiple patterns.
        
        Args:
            patterns: List of patterns to anonymize
            context: Anonymization context
            
        Returns:
            List[BasePattern]: List of anonymized patterns
        """
        return [self.anonymize_pattern(pattern, context) for pattern in patterns]
    
    def _anonymize_context(self, context: Any) -> Any:
        """
        Anonymize context information.
        
        Args:
            context: Context to anonymize
            
        Returns:
            Any: Anonymized context
        """
        if not hasattr(context, '__dict__'):
            return context
            
        anonymized = context.copy()
        
        # Remove or hash sensitive fields
        for field in self.SENSITIVE_FIELDS:
            if hasattr(anonymized, field):
                value = getattr(anonymized, field)
                if value:
                    setattr(anonymized, field, self._hash_value(value))
        
        # Generalize instance information
        if hasattr(anonymized, 'instance_id'):
            anonymized.instance_id = self._generalize_instance_id(anonymized.instance_id)
        
        return anonymized
    
    def _anonymize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize metadata dictionary.
        
        Args:
            metadata: Metadata to anonymize
            
        Returns:
            Dict[str, Any]: Anonymized metadata
        """
        anonymized = metadata.copy()
        
        # Remove sensitive fields
        for field in self.SENSITIVE_FIELDS:
            anonymized.pop(field, None)
        
        # Anonymize sensitive values in remaining fields
        for key, value in anonymized.items():
            if isinstance(value, str):
                anonymized[key] = self._anonymize_text(value)
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_metadata(value)
            elif isinstance(value, list):
                anonymized[key] = [
                    self._anonymize_text(item) if isinstance(item, str)
                    else self._anonymize_metadata(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
        
        return anonymized
    
    def _anonymize_effectiveness(
        self,
        effectiveness: Any,
        context: AnonymizationContext
    ) -> Any:
        """
        Apply differential privacy to effectiveness metrics.
        
        Args:
            effectiveness: Effectiveness metrics to anonymize
            context: Anonymization context
            
        Returns:
            Any: Anonymized effectiveness metrics
        """
        if not hasattr(effectiveness, '__dict__'):
            return effectiveness
            
        anonymized = effectiveness.copy()
        
        # Calculate epsilon based on privacy level
        epsilon = self.dp.calculate_epsilon(
            context.privacy_settings.privacy_level,
            metric_count=4  # success_rate, error_rate, usage_count, confidence_score
        )
        
        # Anonymize numeric metrics
        metrics = {
            "success_rate": getattr(anonymized, 'success_rate', 0.0),
            "error_rate": getattr(anonymized, 'error_rate', 0.0),
            "usage_count": getattr(anonymized, 'usage_count', 0),
            "confidence_score": getattr(anonymized, 'confidence_score', 0.0)
        }
        
        anonymized_metrics = self.dp.anonymize_metrics(
            metrics,
            epsilon,
            context.privacy_settings.privacy_level
        )
        
        # Update effectiveness metrics
        for key, value in anonymized_metrics.items():
            setattr(anonymized, key, value)
        
        return anonymized
    
    def _update_privacy_metadata(
        self,
        privacy: Any,
        context: AnonymizationContext
    ) -> Any:
        """
        Update privacy metadata after anonymization.
        
        Args:
            privacy: Privacy metadata to update
            context: Anonymization context
            
        Returns:
            Any: Updated privacy metadata
        """
        if not hasattr(privacy, '__dict__'):
            return privacy
            
        updated = privacy.copy()
        
        # Update privacy level if needed
        if context.privacy_settings.privacy_level != updated.privacy_level:
            updated.privacy_level = context.privacy_settings.privacy_level
        
        # Update anonymization timestamp
        updated.last_anonymized = context.timestamp
        
        # Update contributor count
        updated.contributor_count += 1
        
        return updated
    
    def _anonymize_text(self, text: str) -> str:
        """
        Anonymize sensitive information in text.
        
        Args:
            text: Text to anonymize
            
        Returns:
            str: Anonymized text
        """
        if not isinstance(text, str):
            return text
            
        anonymized = text
        
        # Replace sensitive patterns with hashed values
        for pattern_type, pattern in self.compiled_patterns.items():
            anonymized = pattern.sub(
                lambda m: self._hash_value(m.group(0)),
                anonymized
            )
        
        return anonymized
    
    def _hash_value(self, value: str) -> str:
        """
        Create a deterministic hash of a value.
        
        Args:
            value: Value to hash
            
        Returns:
            str: Hash of the value
        """
        return hashlib.sha256(value.encode()).hexdigest()[:8]
    
    def _generalize_instance_id(self, instance_id: str) -> str:
        """
        Generalize instance identifier.
        
        Args:
            instance_id: Instance ID to generalize
            
        Returns:
            str: Generalized instance ID
        """
        # Keep only the first part of the instance ID
        parts = instance_id.split('-')
        if len(parts) > 1:
            return f"{parts[0]}-{self._hash_value('-'.join(parts[1:]))}"
        return self._hash_value(instance_id)
    
    def _anonymize_solution_pattern(
        self,
        pattern: SolutionPattern,
        context: AnonymizationContext
    ) -> SolutionPattern:
        """Anonymize solution pattern specific fields"""
        anonymized = pattern.copy()
        
        # Anonymize steps and alternatives
        anonymized.steps = [self._anonymize_text(step) for step in pattern.steps]
        anonymized.alternatives = [self._anonymize_text(alt) for alt in pattern.alternatives]
        
        return anonymized
    
    def _anonymize_error_pattern(
        self,
        pattern: ErrorRecoveryPattern,
        context: AnonymizationContext
    ) -> ErrorRecoveryPattern:
        """Anonymize error pattern specific fields"""
        anonymized = pattern.copy()
        
        # Anonymize error context
        anonymized.error_context = self._anonymize_metadata(pattern.error_context)
        
        # Anonymize recovery steps
        anonymized.recovery_steps = [
            self._anonymize_text(step) for step in pattern.recovery_steps
        ]
        
        return anonymized
    
    def _anonymize_workflow_pattern(
        self,
        pattern: WorkflowPattern,
        context: AnonymizationContext
    ) -> WorkflowPattern:
        """Anonymize workflow pattern specific fields"""
        anonymized = pattern.copy()
        
        # Anonymize sequence and dependencies
        anonymized.sequence = [self._anonymize_text(step) for step in pattern.sequence]
        anonymized.dependencies = {
            self._anonymize_text(k): [self._anonymize_text(v) for v in vs]
            for k, vs in pattern.dependencies.items()
        }
        
        return anonymized
    
    def _anonymize_tool_pattern(
        self,
        pattern: ToolUsagePattern,
        context: AnonymizationContext
    ) -> ToolUsagePattern:
        """Anonymize tool pattern specific fields"""
        anonymized = pattern.copy()
        
        # Anonymize command sequence and parameters
        anonymized.command_sequence = [
            self._anonymize_text(cmd) for cmd in pattern.command_sequence
        ]
        anonymized.parameters = self._anonymize_metadata(pattern.parameters)
        
        return anonymized 