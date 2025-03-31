from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RootCause:
    """Container for root cause analysis results."""
    cause: str
    description: str
    confidence: float
    contributing_factors: List[str]
    evidence: List[str]
    suggested_fixes: List[str]
    timestamp: datetime = datetime.utcnow()

class RootCauseAnalyzer:
    """System for analyzing root causes of errors."""
    
    def __init__(self):
        """Initialize root cause analyzer."""
        self.cause_patterns = self._initialize_cause_patterns()
        self.cause_history = defaultdict(list)
        
    def _initialize_cause_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined root cause patterns."""
        return {
            "configuration_error": {
                "indicators": [
                    "config", "settings", "environment", "env",
                    "missing", "invalid", "not found"
                ],
                "description": "Configuration or environment setup issue",
                "severity": "high",
                "fix_suggestions": [
                    "Check configuration files",
                    "Verify environment variables",
                    "Review deployment settings"
                ]
            },
            "dependency_issue": {
                "indicators": [
                    "import", "module", "package", "dependency",
                    "version", "compatibility", "missing"
                ],
                "description": "Dependency or package management issue",
                "severity": "medium",
                "fix_suggestions": [
                    "Update dependencies",
                    "Check version compatibility",
                    "Verify package installation"
                ]
            },
            "resource_exhaustion": {
                "indicators": [
                    "memory", "cpu", "disk", "connection",
                    "timeout", "exhausted", "limit"
                ],
                "description": "System resource exhaustion",
                "severity": "high",
                "fix_suggestions": [
                    "Monitor resource usage",
                    "Implement resource limits",
                    "Optimize resource allocation"
                ]
            },
            "concurrency_issue": {
                "indicators": [
                    "thread", "lock", "deadlock", "race",
                    "concurrent", "synchronization"
                ],
                "description": "Concurrency or threading issue",
                "severity": "high",
                "fix_suggestions": [
                    "Review thread safety",
                    "Check lock ordering",
                    "Implement proper synchronization"
                ]
            },
            "data_integrity": {
                "indicators": [
                    "data", "corrupt", "invalid", "format",
                    "validation", "integrity"
                ],
                "description": "Data integrity or validation issue",
                "severity": "medium",
                "fix_suggestions": [
                    "Validate input data",
                    "Check data format",
                    "Implement data validation"
                ]
            },
            "network_issue": {
                "indicators": [
                    "network", "connection", "timeout", "socket",
                    "http", "dns", "proxy"
                ],
                "description": "Network or connectivity issue",
                "severity": "medium",
                "fix_suggestions": [
                    "Check network connectivity",
                    "Verify service availability",
                    "Review network configuration"
                ]
            },
            "security_issue": {
                "indicators": [
                    "security", "permission", "access", "auth",
                    "unauthorized", "forbidden"
                ],
                "description": "Security or authorization issue",
                "severity": "high",
                "fix_suggestions": [
                    "Review access permissions",
                    "Check authentication",
                    "Verify security settings"
                ]
            }
        }
    
    def analyze_root_cause(
        self,
        error_message: str,
        stack_trace: Optional[List[str]] = None,
        patterns: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RootCause:
        """
        Analyze root cause of an error.
        
        Args:
            error_message: The error message
            stack_trace: Optional stack trace
            patterns: Optional list of detected patterns
            context: Optional error context
            
        Returns:
            RootCause: Analysis results
        """
        try:
            # Collect evidence from different sources
            evidence = self._collect_evidence(
                error_message,
                stack_trace,
                patterns,
                context
            )
            
            # Identify potential causes
            causes = self._identify_causes(evidence)
            
            # Select most likely cause
            primary_cause = self._select_primary_cause(causes)
            
            # Generate analysis
            analysis = self._generate_analysis(
                primary_cause,
                evidence,
                patterns,
                context
            )
            
            # Update cause history
            self._update_history(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error during root cause analysis: {e}")
            raise
    
    def _collect_evidence(
        self,
        error_message: str,
        stack_trace: Optional[List[str]],
        patterns: Optional[List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Collect evidence from various sources."""
        evidence = []
        
        # Add error message
        evidence.append(f"Error message: {error_message}")
        
        # Add stack trace
        if stack_trace:
            evidence.extend(stack_trace)
        
        # Add pattern information
        if patterns:
            for pattern in patterns:
                evidence.append(f"Pattern: {pattern.get('type')} - {pattern.get('description')}")
        
        # Add context information
        if context:
            for key, value in context.items():
                evidence.append(f"Context: {key} = {value}")
        
        return evidence
    
    def _identify_causes(self, evidence: List[str]) -> List[Tuple[str, float]]:
        """Identify potential causes from evidence."""
        causes = []
        
        # Check evidence against cause patterns
        for cause_type, pattern_info in self.cause_patterns.items():
            score = 0
            indicators = pattern_info["indicators"]
            
            # Count matching indicators
            for indicator in indicators:
                for line in evidence:
                    if indicator.lower() in line.lower():
                        score += 1
            
            # Calculate confidence score
            if score > 0:
                confidence = min(score / len(indicators), 1.0)
                causes.append((cause_type, confidence))
        
        return sorted(causes, key=lambda x: x[1], reverse=True)
    
    def _select_primary_cause(self, causes: List[Tuple[str, float]]) -> str:
        """Select the most likely primary cause."""
        if not causes:
            return "unknown"
        
        # Return cause with highest confidence
        return causes[0][0]
    
    def _generate_analysis(
        self,
        cause_type: str,
        evidence: List[str],
        patterns: Optional[List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]]
    ) -> RootCause:
        """Generate detailed analysis for the root cause."""
        pattern_info = self.cause_patterns.get(cause_type, {})
        
        # Collect contributing factors
        contributing_factors = []
        if patterns:
            for pattern in patterns:
                if pattern.get("type") != cause_type:
                    contributing_factors.append(
                        f"{pattern.get('type')}: {pattern.get('description')}"
                    )
        
        # Generate suggested fixes
        suggested_fixes = pattern_info.get("fix_suggestions", [])
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            cause_type,
            evidence,
            patterns,
            context
        )
        
        return RootCause(
            cause=cause_type,
            description=pattern_info.get("description", "Unknown cause"),
            confidence=confidence,
            contributing_factors=contributing_factors,
            evidence=evidence,
            suggested_fixes=suggested_fixes
        )
    
    def _calculate_confidence(
        self,
        cause_type: str,
        evidence: List[str],
        patterns: Optional[List[Dict[str, Any]]],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the analysis."""
        # Initialize confidence components
        components = []
        weights = []
        
        # 1. Pattern matching confidence (weight: 0.4)
        pattern_info = self.cause_patterns.get(cause_type, {})
        indicators = pattern_info.get("indicators", [])
        matches = sum(
            1 for indicator in indicators
            for line in evidence
            if indicator.lower() in line.lower()
        )
        pattern_confidence = matches / len(indicators) if indicators else 0.5
        components.append(pattern_confidence)
        weights.append(0.4)
        
        # 2. Pattern-based confidence (weight: 0.3)
        if patterns:
            pattern_confidence = sum(
                p.get("confidence", 0.5)
                for p in patterns
                if p.get("type") == cause_type
            ) / len(patterns)
            components.append(pattern_confidence)
            weights.append(0.3)
        
        # 3. Context-based confidence (weight: 0.2)
        if context:
            context_confidence = self._calculate_context_confidence(
                cause_type,
                context
            )
            components.append(context_confidence)
            weights.append(0.2)
        
        # 4. Historical confidence (weight: 0.1)
        historical_confidence = self._calculate_historical_confidence(cause_type)
        components.append(historical_confidence)
        weights.append(0.1)
        
        # Calculate weighted average
        if not components:
            return 0.5
        
        # Normalize weights if they don't sum to 1
        total_weight = sum(weights)
        if total_weight != 1:
            weights = [w / total_weight for w in weights]
        
        confidence = sum(c * w for c, w in zip(components, weights))
        
        # Apply confidence adjustments
        confidence = self._adjust_confidence(confidence, cause_type, evidence, context)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_context_confidence(
        self,
        cause_type: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence based on context information."""
        confidence = 0.5  # Base confidence
        
        # Resource-related causes
        if cause_type == "resource_exhaustion":
            if "memory_usage" in context and context["memory_usage"] > 0.9:
                confidence += 0.3
            if "cpu_usage" in context and context["cpu_usage"] > 0.9:
                confidence += 0.3
            if "disk_usage" in context and context["disk_usage"] > 0.9:
                confidence += 0.2
        
        # Network-related causes
        elif cause_type == "network_issue":
            if "network_status" in context and not context["network_status"]:
                confidence += 0.4
            if "response_time" in context and context["response_time"] > 5:
                confidence += 0.3
            if "connection_errors" in context and context["connection_errors"] > 0:
                confidence += 0.2
        
        # Security-related causes
        elif cause_type == "security_issue":
            if "auth_status" in context and not context["auth_status"]:
                confidence += 0.4
            if "permission_level" in context and context["permission_level"] == "none":
                confidence += 0.3
            if "security_events" in context and context["security_events"] > 0:
                confidence += 0.2
        
        # Database-related causes
        elif cause_type == "database_error":
            if "db_connection" in context and not context["db_connection"]:
                confidence += 0.4
            if "query_time" in context and context["query_time"] > 2:
                confidence += 0.3
            if "db_errors" in context and context["db_errors"] > 0:
                confidence += 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_historical_confidence(self, cause_type: str) -> float:
        """Calculate confidence based on historical data."""
        if cause_type not in self.cause_history:
            return 0.5
        
        analyses = self.cause_history[cause_type]
        if not analyses:
            return 0.5
        
        # Calculate average historical confidence
        avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        
        # Consider recency of similar causes
        recent_analyses = [
            a for a in analyses
            if (datetime.utcnow() - a.timestamp).days <= 7
        ]
        
        if recent_analyses:
            recent_confidence = sum(a.confidence for a in recent_analyses) / len(recent_analyses)
            # Weight recent confidence more heavily
            return (avg_confidence * 0.4) + (recent_confidence * 0.6)
        
        return avg_confidence
    
    def _adjust_confidence(
        self,
        base_confidence: float,
        cause_type: str,
        evidence: List[str],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Apply additional adjustments to confidence score."""
        confidence = base_confidence
        
        # Adjust based on evidence quality
        if len(evidence) > 5:  # More evidence points
            confidence += 0.1
        if any("error" in e.lower() for e in evidence):  # Explicit error mentions
            confidence += 0.05
        
        # Adjust based on context quality
        if context:
            if len(context) > 3:  # More context information
                confidence += 0.05
            if any(isinstance(v, (int, float)) for v in context.values()):  # Quantitative data
                confidence += 0.05
        
        # Adjust based on cause type
        if cause_type in ["security_issue", "resource_exhaustion"]:
            # These causes typically have higher confidence when detected
            confidence += 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def _update_history(self, analysis: RootCause) -> None:
        """Update cause history with new analysis."""
        self.cause_history[analysis.cause].append(analysis)
        
        # Keep only recent history (e.g., last 100 entries per cause)
        max_history = 100
        if len(self.cause_history[analysis.cause]) > max_history:
            self.cause_history[analysis.cause] = \
                self.cause_history[analysis.cause][-max_history:]
    
    def get_cause_statistics(self) -> Dict[str, Any]:
        """Get statistics about root cause analysis."""
        stats = {
            "total_analyses": sum(len(analyses) for analyses in self.cause_history.values()),
            "cause_distribution": {
                cause: len(analyses)
                for cause, analyses in self.cause_history.items()
            },
            "average_confidence": {
                cause: sum(a.confidence for a in analyses) / len(analyses)
                for cause, analyses in self.cause_history.items()
                if analyses
            }
        }
        
        return stats
    
    def get_cause_history(
        self,
        cause_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[RootCause]:
        """
        Get historical root cause analyses.
        
        Args:
            cause_type: Optional specific cause type to filter
            limit: Optional maximum number of results
            
        Returns:
            List[RootCause]: Historical analyses
        """
        if cause_type:
            history = self.cause_history.get(cause_type, [])
        else:
            history = [
                analysis
                for analyses in self.cause_history.values()
                for analysis in analyses
            ]
        
        if limit:
            history = history[-limit:]
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True) 