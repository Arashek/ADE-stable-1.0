from typing import Any, Callable, Dict, List, Optional, Type, Union
import logging
from datetime import datetime
from src.core.error.retry_policy import RetryManager, RetryPolicy
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer

class Agent:
    """Base agent class with retry and error handling capabilities"""
    
    def __init__(
        self,
        name: str,
        retry_manager: Optional[RetryManager] = None,
        error_detector: Optional[ErrorDetector] = None,
        root_cause_analyzer: Optional[RootCauseAnalyzer] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.name = name
        self.retry_manager = retry_manager or RetryManager()
        self.error_detector = error_detector or ErrorDetector()
        self.root_cause_analyzer = root_cause_analyzer or RootCauseAnalyzer()
        self.logger = logger or logging.getLogger(f"agent.{name}")
        
        # Initialize default retry policy
        self._setup_default_retry_policy()
    
    def _setup_default_retry_policy(self):
        """Set up default retry policy for the agent"""
        default_policy = RetryPolicy(
            name=f"{self.name}_default",
            max_attempts=3,
            strategy=RetryStrategy.EXPONENTIAL,
            initial_delay=1.0,
            max_delay=5.0,
            jitter=True,
            error_types=[Exception],
            error_patterns=[".*"],
            max_total_time=30.0
        )
        self.retry_manager.add_policy(default_policy.name, default_policy)
    
    def execute_with_retry(
        self,
        operation: Callable[[], Any],
        retry_policy_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute an operation with retry logic
        
        Args:
            operation: The operation to execute
            retry_policy_name: Name of the retry policy to use
            context: Additional context for error analysis
            
        Returns:
            The result of the operation
            
        Raises:
            Exception: If the operation fails after all retries
        """
        policy_name = retry_policy_name or f"{self.name}_default"
        policy = self.retry_manager.get_policy(policy_name)
        if not policy:
            raise ValueError(f"Retry policy '{policy_name}' not found")
        
        attempt = 1
        last_error = None
        
        while attempt <= policy.max_attempts:
            try:
                # Check circuit breaker
                if policy.circuit_breaker and policy.circuit_breaker.state == CircuitBreakerState.OPEN:
                    self.logger.warning(f"Circuit breaker is open for policy '{policy_name}'")
                    raise last_error or RuntimeError("Circuit breaker is open")
                
                # Execute operation
                result = operation()
                
                # Record success
                if policy.circuit_breaker:
                    policy.circuit_breaker.record_success()
                
                return result
                
            except Exception as e:
                last_error = e
                
                # Record failure
                if policy.circuit_breaker:
                    policy.circuit_breaker.record_failure()
                
                # Detect and analyze error
                self.error_detector.detect_error(e, context)
                
                # Analyze root cause
                causes = self.root_cause_analyzer.analyze_error(e)
                if causes:
                    self.logger.warning(f"Root causes detected: {[cause.cause_type for cause in causes]}")
                
                # Check if we should retry
                if not self.retry_manager.should_retry(policy_name, e):
                    self.logger.error(f"Operation failed and will not be retried: {str(e)}")
                    raise
                
                # Calculate delay
                delay = self.retry_manager.get_delay(policy_name, attempt)
                
                # Log retry attempt
                self.logger.warning(
                    f"Operation failed (attempt {attempt}/{policy.max_attempts}). "
                    f"Retrying in {delay:.2f} seconds. Error: {str(e)}"
                )
                
                # Record attempt
                self.retry_manager.record_attempt(
                    policy_name,
                    attempt,
                    e,
                    delay
                )
                
                # Wait before retry
                time.sleep(delay)
                attempt += 1
        
        # If we get here, all retries failed
        self.logger.error(f"Operation failed after {policy.max_attempts} attempts")
        raise last_error
    
    def get_retry_history(self, policy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get retry attempt history for a policy"""
        policy_name = policy_name or f"{self.name}_default"
        return self.retry_manager.get_attempt_history(policy_name)
    
    def clear_retry_history(self, policy_name: Optional[str] = None):
        """Clear retry attempt history for a policy"""
        policy_name = policy_name or f"{self.name}_default"
        self.retry_manager.clear_history(policy_name)
    
    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get error detection history"""
        return self.error_detector.get_error_history()
    
    def clear_error_history(self):
        """Clear error detection history"""
        self.error_detector.clear_history()
    
    def get_circuit_breaker_state(self, policy_name: Optional[str] = None) -> CircuitBreakerState:
        """Get circuit breaker state for a policy"""
        policy_name = policy_name or f"{self.name}_default"
        policy = self.retry_manager.get_policy(policy_name)
        if not policy or not policy.circuit_breaker:
            return None
        return policy.circuit_breaker.state 