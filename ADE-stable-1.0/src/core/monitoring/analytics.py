import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
from src.core.monitoring.metrics import Metrics

@dataclass
class Analytics:
    """Analytics data structure"""
    error_patterns: Dict[str, int] = None
    retry_policies: Dict[str, Dict[str, Any]] = None
    root_causes: Dict[str, int] = None
    fix_effectiveness: Dict[str, Dict[str, float]] = None
    circuit_breakers: Dict[str, Dict[str, Any]] = None
    performance_trends: Dict[str, List[float]] = None
    error_correlations: List[Dict[str, Any]] = None
    timestamp: datetime = None

class AnalyticsEngine:
    """Analyzes metrics and generates insights"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("analytics_engine")
        self.metrics_history: List[Metrics] = []
        self.error_history: List[Dict[str, Any]] = []
        self.fix_history: List[Dict[str, Any]] = []
        self.retry_history: List[Dict[str, Any]] = []
        self.circuit_breaker_history: List[Dict[str, Any]] = []
        
    def add_metrics(self, metrics: Metrics):
        """Add metrics to history"""
        self.metrics_history.append(metrics)
        self._cleanup_old_data()
    
    def add_error(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """Add error to history"""
        self.error_history.append({
            "type": error_type,
            "message": error_message,
            "context": context,
            "timestamp": datetime.now()
        })
    
    def add_fix(self, cause_type: str, success: bool, context: Dict[str, Any]):
        """Add fix attempt to history"""
        self.fix_history.append({
            "cause_type": cause_type,
            "success": success,
            "context": context,
            "timestamp": datetime.now()
        })
    
    def add_retry(self, policy_name: str, attempt: int, delay: float, success: bool):
        """Add retry attempt to history"""
        self.retry_history.append({
            "policy_name": policy_name,
            "attempt": attempt,
            "delay": delay,
            "success": success,
            "timestamp": datetime.now()
        })
    
    def add_circuit_breaker_state(self, policy_name: str, state: str, failure_rate: float):
        """Add circuit breaker state to history"""
        self.circuit_breaker_history.append({
            "policy_name": policy_name,
            "state": state,
            "failure_rate": failure_rate,
            "timestamp": datetime.now()
        })
    
    def get_analytics(self) -> Analytics:
        """Generate analytics from collected data"""
        analytics = Analytics(
            error_patterns=self._analyze_error_patterns(),
            retry_policies=self._analyze_retry_policies(),
            root_causes=self._analyze_root_causes(),
            fix_effectiveness=self._analyze_fix_effectiveness(),
            circuit_breakers=self._analyze_circuit_breakers(),
            performance_trends=self._analyze_performance_trends(),
            error_correlations=self._analyze_error_correlations(),
            timestamp=datetime.now()
        )
        return analytics
    
    def _analyze_error_patterns(self) -> Dict[str, int]:
        """Analyze error patterns"""
        patterns = defaultdict(int)
        for error in self.error_history:
            patterns[error["type"]] += 1
        return dict(patterns)
    
    def _analyze_retry_policies(self) -> Dict[str, Dict[str, Any]]:
        """Analyze retry policy effectiveness"""
        policies = defaultdict(lambda: {
            "total_attempts": 0,
            "successful_attempts": 0,
            "avg_delay": 0.0,
            "success_rate": 0.0
        })
        
        for retry in self.retry_history:
            policy = policies[retry["policy_name"]]
            policy["total_attempts"] += 1
            if retry["success"]:
                policy["successful_attempts"] += 1
            policy["avg_delay"] = (
                (policy["avg_delay"] * (policy["total_attempts"] - 1) + retry["delay"])
                / policy["total_attempts"]
            )
            policy["success_rate"] = policy["successful_attempts"] / policy["total_attempts"]
        
        return dict(policies)
    
    def _analyze_root_causes(self) -> Dict[str, int]:
        """Analyze root causes of errors"""
        causes = defaultdict(int)
        for error in self.error_history:
            if "root_cause" in error["context"]:
                causes[error["context"]["root_cause"]] += 1
        return dict(causes)
    
    def _analyze_fix_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """Analyze fix effectiveness"""
        effectiveness = defaultdict(lambda: {
            "total_attempts": 0,
            "successful_attempts": 0,
            "success_rate": 0.0
        })
        
        for fix in self.fix_history:
            cause = effectiveness[fix["cause_type"]]
            cause["total_attempts"] += 1
            if fix["success"]:
                cause["successful_attempts"] += 1
            cause["success_rate"] = cause["successful_attempts"] / cause["total_attempts"]
        
        return dict(effectiveness)
    
    def _analyze_circuit_breakers(self) -> Dict[str, Dict[str, Any]]:
        """Analyze circuit breaker behavior"""
        breakers = defaultdict(lambda: {
            "state_transitions": 0,
            "failure_rate": 0.0,
            "current_state": "CLOSED"
        })
        
        for state in self.circuit_breaker_history:
            breaker = breakers[state["policy_name"]]
            if breaker["current_state"] != state["state"]:
                breaker["state_transitions"] += 1
            breaker["current_state"] = state["state"]
            breaker["failure_rate"] = state["failure_rate"]
        
        return dict(breakers)
    
    def _analyze_performance_trends(self) -> Dict[str, List[float]]:
        """Analyze performance trends"""
        trends = {
            "execution_time": [],
            "memory_usage": [],
            "cpu_usage": []
        }
        
        for metrics in self.metrics_history:
            trends["execution_time"].append(metrics.execution_time)
            trends["memory_usage"].append(metrics.memory_usage)
            trends["cpu_usage"].append(metrics.cpu_usage)
        
        return trends
    
    def _analyze_error_correlations(self) -> List[Dict[str, Any]]:
        """Analyze error correlations"""
        correlations = []
        error_types = set(error["type"] for error in self.error_history)
        
        for error1 in error_types:
            for error2 in error_types:
                if error1 != error2:
                    correlation = self._calculate_error_correlation(error1, error2)
                    if correlation > 0.5:  # Only include strong correlations
                        correlations.append({
                            "error1": error1,
                            "error2": error2,
                            "correlation": correlation
                        })
        
        return correlations
    
    def _calculate_error_correlation(self, error1: str, error2: str) -> float:
        """Calculate correlation between two error types"""
        # Simple time-based correlation
        error1_times = [
            error["timestamp"]
            for error in self.error_history
            if error["type"] == error1
        ]
        error2_times = [
            error["timestamp"]
            for error in self.error_history
            if error["type"] == error2
        ]
        
        if not error1_times or not error2_times:
            return 0.0
        
        # Count errors that occur within 1 second of each other
        correlated_count = 0
        for t1 in error1_times:
            for t2 in error2_times:
                if abs((t1 - t2).total_seconds()) <= 1.0:
                    correlated_count += 1
        
        return correlated_count / max(len(error1_times), len(error2_times))
    
    def _cleanup_old_data(self):
        """Clean up data older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        self.error_history = [
            error for error in self.error_history
            if error["timestamp"] > cutoff
        ]
        self.fix_history = [
            fix for fix in self.fix_history
            if fix["timestamp"] > cutoff
        ]
        self.retry_history = [
            retry for retry in self.retry_history
            if retry["timestamp"] > cutoff
        ]
        self.circuit_breaker_history = [
            state for state in self.circuit_breaker_history
            if state["timestamp"] > cutoff
        ] 