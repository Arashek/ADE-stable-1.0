from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
from .error_collector import ErrorEvent, ErrorSeverity
from .anonymous_reporter import AnonymizedError

@dataclass
class ErrorPattern:
    pattern_id: str
    error_type: str
    message_pattern: str
    stack_pattern: str
    frequency: int
    severity_distribution: Dict[str, int]
    component_distribution: Dict[str, int]
    related_patterns: List[str]
    first_seen: datetime
    last_seen: datetime
    confidence_score: float

@dataclass
class WorkflowPattern:
    pattern_id: str
    sequence: List[str]
    success_rate: float
    error_patterns: List[str]
    average_duration: float
    frequency: int
    confidence_score: float

class PatternDetector:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}
        self.error_sequence_buffer: List[AnonymizedError] = []
        self.workflow_sequence_buffer: List[Dict[str, Any]] = []

    def analyze_error_pattern(self, error: AnonymizedError) -> Optional[ErrorPattern]:
        """Analyze an error and identify if it matches existing patterns"""
        # Add to sequence buffer
        self.error_sequence_buffer.append(error)
        if len(self.error_sequence_buffer) > self.window_size:
            self.error_sequence_buffer.pop(0)

        # Find matching patterns
        matching_patterns = self._find_matching_patterns(error)
        if matching_patterns:
            return matching_patterns[0]
        
        # Create new pattern if no match found
        return self._create_new_pattern(error)

    def analyze_workflow_pattern(self, event: Dict[str, Any]) -> Optional[WorkflowPattern]:
        """Analyze a workflow event and identify patterns"""
        # Add to sequence buffer
        self.workflow_sequence_buffer.append(event)
        if len(self.workflow_sequence_buffer) > self.window_size:
            self.workflow_sequence_buffer.pop(0)

        # Find matching patterns
        matching_patterns = self._find_matching_workflow_patterns(event)
        if matching_patterns:
            return matching_patterns[0]
        
        # Create new pattern if no match found
        return self._create_new_workflow_pattern(event)

    def _find_matching_patterns(self, error: AnonymizedError) -> List[ErrorPattern]:
        """Find patterns that match the given error"""
        matching_patterns = []
        for pattern in self.error_patterns.values():
            if (pattern.error_type == error.error_type and
                pattern.message_pattern == error.message_pattern and
                pattern.stack_pattern == error.stack_pattern):
                matching_patterns.append(pattern)
        return matching_patterns

    def _find_matching_workflow_patterns(self, event: Dict[str, Any]) -> List[WorkflowPattern]:
        """Find workflow patterns that match the given event sequence"""
        matching_patterns = []
        current_sequence = [e["type"] for e in self.workflow_sequence_buffer[-5:]]
        
        for pattern in self.workflow_patterns.values():
            if self._sequence_matches_pattern(current_sequence, pattern.sequence):
                matching_patterns.append(pattern)
        return matching_patterns

    def _sequence_matches_pattern(self, sequence: List[str], pattern: List[str]) -> bool:
        """Check if a sequence matches a pattern"""
        if len(sequence) < len(pattern):
            return False
        return sequence[-len(pattern):] == pattern

    def _create_new_pattern(self, error: AnonymizedError) -> ErrorPattern:
        """Create a new error pattern"""
        pattern_id = f"EP_{len(self.error_patterns) + 1}"
        pattern = ErrorPattern(
            pattern_id=pattern_id,
            error_type=error.error_type,
            message_pattern=error.message_pattern,
            stack_pattern=error.stack_pattern,
            frequency=1,
            severity_distribution={error.severity: 1},
            component_distribution={error.component: 1},
            related_patterns=[],
            first_seen=error.timestamp,
            last_seen=error.timestamp,
            confidence_score=0.5
        )
        self.error_patterns[pattern_id] = pattern
        return pattern

    def _create_new_workflow_pattern(self, event: Dict[str, Any]) -> WorkflowPattern:
        """Create a new workflow pattern"""
        pattern_id = f"WP_{len(self.workflow_patterns) + 1}"
        sequence = [e["type"] for e in self.workflow_sequence_buffer[-5:]]
        
        pattern = WorkflowPattern(
            pattern_id=pattern_id,
            sequence=sequence,
            success_rate=1.0 if event.get("success", False) else 0.0,
            error_patterns=[],
            average_duration=event.get("duration", 0.0),
            frequency=1,
            confidence_score=0.5
        )
        self.workflow_patterns[pattern_id] = pattern
        return pattern

    def update_pattern_statistics(self):
        """Update statistics for all patterns"""
        for pattern in self.error_patterns.values():
            self._update_error_pattern_stats(pattern)
        
        for pattern in self.workflow_patterns.values():
            self._update_workflow_pattern_stats(pattern)

    def _update_error_pattern_stats(self, pattern: ErrorPattern):
        """Update statistics for an error pattern"""
        recent_errors = [
            e for e in self.error_sequence_buffer
            if e.error_type == pattern.error_type
            and e.message_pattern == pattern.message_pattern
            and e.stack_pattern == pattern.stack_pattern
        ]

        if recent_errors:
            pattern.frequency = len(recent_errors)
            pattern.last_seen = max(e.timestamp for e in recent_errors)
            
            # Update severity distribution
            pattern.severity_distribution = defaultdict(int)
            for error in recent_errors:
                pattern.severity_distribution[error.severity] += 1
            
            # Update component distribution
            pattern.component_distribution = defaultdict(int)
            for error in recent_errors:
                pattern.component_distribution[error.component] += 1
            
            # Update confidence score
            pattern.confidence_score = self._calculate_pattern_confidence(pattern)

    def _update_workflow_pattern_stats(self, pattern: WorkflowPattern):
        """Update statistics for a workflow pattern"""
        recent_workflows = [
            e for e in self.workflow_sequence_buffer
            if self._sequence_matches_pattern(
                [e["type"] for e in self.workflow_sequence_buffer[-5:]],
                pattern.sequence
            )
        ]

        if recent_workflows:
            pattern.frequency = len(recent_workflows)
            pattern.success_rate = sum(1 for w in recent_workflows if w.get("success", False)) / len(recent_workflows)
            pattern.average_duration = np.mean([w.get("duration", 0.0) for w in recent_workflows])
            pattern.confidence_score = self._calculate_workflow_confidence(pattern)

    def _calculate_pattern_confidence(self, pattern: ErrorPattern) -> float:
        """Calculate confidence score for an error pattern"""
        # Base confidence on frequency and consistency
        frequency_factor = min(pattern.frequency / self.window_size, 1.0)
        consistency_factor = len(pattern.severity_distribution) / len(ErrorSeverity)
        return (frequency_factor + consistency_factor) / 2

    def _calculate_workflow_confidence(self, pattern: WorkflowPattern) -> float:
        """Calculate confidence score for a workflow pattern"""
        # Base confidence on frequency and success rate
        frequency_factor = min(pattern.frequency / self.window_size, 1.0)
        return (frequency_factor + pattern.success_rate) / 2

    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights about detected patterns"""
        return {
            "error_patterns": {
                "total": len(self.error_patterns),
                "by_severity": self._aggregate_patterns_by_severity(),
                "by_component": self._aggregate_patterns_by_component(),
                "trending": self._get_trending_patterns()
            },
            "workflow_patterns": {
                "total": len(self.workflow_patterns),
                "success_rate": self._calculate_overall_success_rate(),
                "common_sequences": self._get_common_sequences(),
                "error_correlations": self._analyze_error_correlations()
            }
        }

    def _aggregate_patterns_by_severity(self) -> Dict[str, int]:
        """Aggregate patterns by severity level"""
        aggregation = defaultdict(int)
        for pattern in self.error_patterns.values():
            for severity, count in pattern.severity_distribution.items():
                aggregation[severity] += count
        return dict(aggregation)

    def _aggregate_patterns_by_component(self) -> Dict[str, int]:
        """Aggregate patterns by component"""
        aggregation = defaultdict(int)
        for pattern in self.error_patterns.values():
            for component, count in pattern.component_distribution.items():
                aggregation[component] += count
        return dict(aggregation)

    def _get_trending_patterns(self) -> List[Dict[str, Any]]:
        """Get trending error patterns"""
        recent_patterns = [
            pattern for pattern in self.error_patterns.values()
            if (datetime.utcnow() - pattern.last_seen) < timedelta(hours=24)
        ]
        return sorted(
            recent_patterns,
            key=lambda p: p.frequency * p.confidence_score,
            reverse=True
        )[:5]

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate for workflow patterns"""
        if not self.workflow_patterns:
            return 0.0
        return np.mean([p.success_rate for p in self.workflow_patterns.values()])

    def _get_common_sequences(self) -> List[Dict[str, Any]]:
        """Get most common workflow sequences"""
        return sorted(
            [
                {
                    "sequence": pattern.sequence,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate
                }
                for pattern in self.workflow_patterns.values()
            ],
            key=lambda x: x["frequency"],
            reverse=True
        )[:5]

    def _analyze_error_correlations(self) -> List[Dict[str, Any]]:
        """Analyze correlations between error patterns"""
        correlations = []
        for pattern1 in self.error_patterns.values():
            for pattern2 in self.error_patterns.values():
                if pattern1.pattern_id < pattern2.pattern_id:
                    correlation = self._calculate_pattern_correlation(pattern1, pattern2)
                    if correlation > 0.5:  # Only include strong correlations
                        correlations.append({
                            "pattern1": pattern1.pattern_id,
                            "pattern2": pattern2.pattern_id,
                            "correlation": correlation
                        })
        return sorted(correlations, key=lambda x: x["correlation"], reverse=True)

    def _calculate_pattern_correlation(self, pattern1: ErrorPattern, pattern2: ErrorPattern) -> float:
        """Calculate correlation between two error patterns"""
        # Simple temporal correlation based on co-occurrence
        cooccurrences = sum(
            1 for e1, e2 in zip(self.error_sequence_buffer[:-1], self.error_sequence_buffer[1:])
            if (e1.error_type == pattern1.error_type and e2.error_type == pattern2.error_type) or
               (e1.error_type == pattern2.error_type and e2.error_type == pattern1.error_type)
        )
        return cooccurrences / len(self.error_sequence_buffer) if self.error_sequence_buffer else 0.0 