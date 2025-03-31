from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging
import json
import yaml
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import ast
import re
from collections import defaultdict

from ..models.code_generation.pattern_analyzer import PatternAnalyzer
from ..learning.pattern_learner import PatternLearner
from ..resource.resource_optimizer import ResourceOptimizer

logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """Pattern associated with potential errors"""
    pattern_type: str
    description: str
    severity: str  # low, medium, high, critical
    confidence: float
    affected_components: List[str]
    prevention_strategies: List[str]
    last_occurrence: Optional[datetime] = None
    occurrence_count: int = 0

@dataclass
class PreventionMetrics:
    """Metrics for error prevention effectiveness"""
    patterns_detected: int
    patterns_prevented: int
    false_positives: int
    prevention_rate: float
    timestamp: datetime

class ErrorPrevention:
    """Enhanced error prevention with pattern recognition and proactive measures"""
    
    def __init__(self, 
                 pattern_learner: PatternLearner,
                 resource_optimizer: ResourceOptimizer):
        self.pattern_learner = pattern_learner
        self.resource_optimizer = resource_optimizer
        self.pattern_analyzer = PatternAnalyzer()
        
        # Initialize error patterns
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.pattern_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize metrics
        self.metrics: List[PreventionMetrics] = []
        
        # Initialize anomaly detection
        self.isolation_forest = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        
        # Load known error patterns
        self._load_error_patterns()
        
    def _load_error_patterns(self) -> None:
        """Load known error patterns from configuration"""
        try:
            patterns_path = Path("src/core/models/error_prevention/patterns.yaml")
            if patterns_path.exists():
                with open(patterns_path, 'r') as f:
                    patterns = yaml.safe_load(f)
                    
                for pattern in patterns:
                    self.error_patterns[pattern["type"]] = ErrorPattern(
                        pattern_type=pattern["type"],
                        description=pattern["description"],
                        severity=pattern["severity"],
                        confidence=pattern["confidence"],
                        affected_components=pattern["affected_components"],
                        prevention_strategies=pattern["prevention_strategies"]
                    )
                    
        except Exception as e:
            logger.error(f"Error loading error patterns: {e}")
            
    def analyze_code(self, code: str) -> List[ErrorPattern]:
        """Analyze code for potential error patterns"""
        try:
            # Analyze code structure
            analysis = self.pattern_analyzer.analyze_code(code)
            
            # Extract potential error patterns
            patterns = self._extract_error_patterns(analysis)
            
            # Check resource usage patterns
            resource_patterns = self._check_resource_patterns(analysis)
            patterns.extend(resource_patterns)
            
            # Update pattern history
            self._update_pattern_history(patterns)
            
            # Update metrics
            self._update_metrics(patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return []
            
    def _extract_error_patterns(self, analysis: Dict[str, Any]) -> List[ErrorPattern]:
        """Extract error patterns from code analysis"""
        patterns = []
        
        # Check for common error patterns
        for pattern_type, pattern in self.error_patterns.items():
            if self._matches_pattern(analysis, pattern):
                patterns.append(pattern)
                
        # Check for resource-related patterns
        resource_metrics = self.resource_optimizer.get_resource_metrics()
        if resource_metrics:
            resource_patterns = self._analyze_resource_patterns(resource_metrics)
            patterns.extend(resource_patterns)
            
        return patterns
        
    def _matches_pattern(self, analysis: Dict[str, Any], pattern: ErrorPattern) -> bool:
        """Check if code matches an error pattern"""
        # Check complexity
        if analysis.get("complexity", 0) > 10 and pattern.severity == "high":
            return True
            
        # Check dependencies
        if any(dep in analysis.get("dependencies", []) 
               for dep in pattern.affected_components):
            return True
            
        # Check method patterns
        if any(self._matches_method_pattern(method, pattern)
               for method in analysis.get("methods", [])):
            return True
            
        # Check property patterns
        if any(self._matches_property_pattern(prop, pattern)
               for prop in analysis.get("properties", [])):
            return True
            
        return False
        
    def _matches_method_pattern(self, method: Dict[str, Any], pattern: ErrorPattern) -> bool:
        """Check if a method matches an error pattern"""
        # Check method complexity
        if method.get("complexity", 0) > 5 and pattern.severity == "medium":
            return True
            
        # Check method dependencies
        if any(dep in method.get("dependencies", [])
               for dep in pattern.affected_components):
            return True
            
        # Check method parameters
        if len(method.get("parameters", [])) > 5 and pattern.severity == "medium":
            return True
            
        return False
        
    def _matches_property_pattern(self, prop: Dict[str, Any], pattern: ErrorPattern) -> bool:
        """Check if a property matches an error pattern"""
        # Check property complexity
        if prop.get("complexity", 0) > 3 and pattern.severity == "low":
            return True
            
        # Check property dependencies
        if any(dep in prop.get("dependencies", [])
               for dep in pattern.affected_components):
            return True
            
        return False
        
    def _check_resource_patterns(self, analysis: Dict[str, Any]) -> List[ErrorPattern]:
        """Check for resource-related error patterns"""
        patterns = []
        
        # Get resource predictions
        predictions = self.resource_optimizer.get_prediction_metrics()
        
        # Check for resource exhaustion patterns
        if predictions:
            if predictions["cpu"]["predicted"] > 90:
                patterns.append(ErrorPattern(
                    pattern_type="resource_exhaustion",
                    description="High CPU usage predicted",
                    severity="high",
                    confidence=predictions["cpu"]["confidence"],
                    affected_components=["system"],
                    prevention_strategies=["optimize_cpu_usage", "scale_resources"]
                ))
                
            if predictions["memory"]["predicted"] > 90:
                patterns.append(ErrorPattern(
                    pattern_type="resource_exhaustion",
                    description="High memory usage predicted",
                    severity="high",
                    confidence=predictions["memory"]["confidence"],
                    affected_components=["system"],
                    prevention_strategies=["optimize_memory_usage", "scale_resources"]
                ))
                
        return patterns
        
    def _analyze_resource_patterns(self, metrics: Dict[str, Any]) -> List[ErrorPattern]:
        """Analyze resource metrics for error patterns"""
        patterns = []
        
        # Check for resource spikes
        for resource, data in metrics.items():
            if "history" in data and len(data["history"]) > 10:
                history = data["history"]
                if self._detect_resource_spike(history):
                    patterns.append(ErrorPattern(
                        pattern_type="resource_spike",
                        description=f"Resource spike detected in {resource}",
                        severity="medium",
                        confidence=0.8,
                        affected_components=["system"],
                        prevention_strategies=["monitor_resource_usage", "implement_rate_limiting"]
                    ))
                    
        return patterns
        
    def _detect_resource_spike(self, history: List[float]) -> bool:
        """Detect sudden spikes in resource usage"""
        if len(history) < 10:
            return False
            
        # Calculate moving average
        window_size = 5
        moving_avg = np.convolve(history, np.ones(window_size)/window_size, mode='valid')
        
        # Check for spikes
        if len(moving_avg) > 0:
            last_value = history[-1]
            avg_value = moving_avg[-1]
            return last_value > avg_value * 1.5  # 50% spike threshold
            
        return False
        
    def _update_pattern_history(self, patterns: List[ErrorPattern]) -> None:
        """Update pattern history"""
        for pattern in patterns:
            if pattern.pattern_type not in self.pattern_history:
                self.pattern_history[pattern.pattern_type] = []
                
            self.pattern_history[pattern.pattern_type].append({
                "timestamp": datetime.now(),
                "severity": pattern.severity,
                "confidence": pattern.confidence,
                "affected_components": pattern.affected_components
            })
            
            # Keep only recent history
            if len(self.pattern_history[pattern.pattern_type]) > 100:
                self.pattern_history[pattern.pattern_type].pop(0)
                
    def _update_metrics(self, patterns: List[ErrorPattern]) -> None:
        """Update prevention metrics"""
        metrics = PreventionMetrics(
            patterns_detected=len(patterns),
            patterns_prevented=sum(1 for p in patterns if p.severity != "critical"),
            false_positives=0,  # Would need feedback loop to track
            prevention_rate=self._calculate_prevention_rate(),
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics) > 100:
            self.metrics.pop(0)
            
    def _calculate_prevention_rate(self) -> float:
        """Calculate error prevention rate"""
        if not self.metrics:
            return 0.0
            
        total_patterns = sum(m.patterns_detected for m in self.metrics)
        prevented_patterns = sum(m.patterns_prevented for m in self.metrics)
        
        if total_patterns == 0:
            return 0.0
            
        return prevented_patterns / total_patterns
        
    def get_prevention_metrics(self) -> Dict[str, Any]:
        """Get current prevention metrics"""
        if not self.metrics:
            return {}
            
        latest_metrics = self.metrics[-1]
        return {
            "patterns_detected": latest_metrics.patterns_detected,
            "patterns_prevented": latest_metrics.patterns_prevented,
            "false_positives": latest_metrics.false_positives,
            "prevention_rate": latest_metrics.prevention_rate,
            "timestamp": latest_metrics.timestamp.isoformat()
        }
        
    def get_pattern_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get pattern history"""
        return self.pattern_history
        
    def get_error_patterns(self) -> Dict[str, ErrorPattern]:
        """Get known error patterns"""
        return self.error_patterns 