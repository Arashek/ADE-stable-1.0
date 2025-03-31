from typing import Dict, Any, Optional, List, Callable
import logging
import time
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Different retry strategies"""
    LINEAR = "linear"  # Fixed delay between retries
    EXPONENTIAL = "exponential"  # Exponential backoff
    FIBONACCI = "fibonacci"  # Fibonacci backoff
    RANDOM = "random"  # Random delay within bounds
    CUSTOM = "custom"  # Custom retry function

@dataclass
class RetryPolicy:
    """Policy for retrying operations"""
    max_attempts: int
    strategy: RetryStrategy
    initial_delay: float
    max_delay: Optional[float] = None
    jitter: bool = False
    custom_function: Optional[Callable[[int], float]] = None
    error_types: List[type] = None
    error_patterns: List[str] = None
    max_total_time: Optional[float] = None
    metadata: Dict[str, Any] = None

class RetryManager:
    """Manages retry operations with different policies"""
    
    def __init__(self):
        self.policies: Dict[str, RetryPolicy] = {}
        self.attempt_history: Dict[str, List[Dict[str, Any]]] = {}
        
    def add_policy(self, name: str, policy: RetryPolicy) -> None:
        """Add a retry policy
        
        Args:
            name: Name of the policy
            policy: Retry policy to add
        """
        self.policies[name] = policy
        self.attempt_history[name] = []
        
    def get_policy(self, name: str) -> Optional[RetryPolicy]:
        """Get a retry policy by name
        
        Args:
            name: Name of the policy
            
        Returns:
            Retry policy if found, None otherwise
        """
        return self.policies.get(name)
        
    def should_retry(self, policy_name: str, error: Exception) -> bool:
        """Check if operation should be retried
        
        Args:
            policy_name: Name of the policy to use
            error: Exception that occurred
            
        Returns:
            True if should retry, False otherwise
        """
        policy = self.get_policy(policy_name)
        if not policy:
            return False
            
        # Check error type
        if policy.error_types and not any(isinstance(error, t) for t in policy.error_types):
            return False
            
        # Check error pattern
        if policy.error_patterns:
            error_msg = str(error)
            if not any(pattern in error_msg for pattern in policy.error_patterns):
                return False
                
        return True
        
    def get_delay(self, policy_name: str, attempt: int) -> float:
        """Get delay for next retry attempt
        
        Args:
            policy_name: Name of the policy to use
            attempt: Current attempt number
            
        Returns:
            Delay in seconds
        """
        policy = self.get_policy(policy_name)
        if not policy:
            return 0
            
        delay = self._calculate_delay(policy, attempt)
        
        # Apply jitter if enabled
        if policy.jitter:
            delay *= random.uniform(0.8, 1.2)
            
        # Apply max delay if specified
        if policy.max_delay:
            delay = min(delay, policy.max_delay)
            
        return delay
        
    def _calculate_delay(self, policy: RetryPolicy, attempt: int) -> float:
        """Calculate delay based on retry strategy
        
        Args:
            policy: Retry policy to use
            attempt: Current attempt number
            
        Returns:
            Delay in seconds
        """
        if policy.strategy == RetryStrategy.LINEAR:
            return policy.initial_delay * attempt
            
        elif policy.strategy == RetryStrategy.EXPONENTIAL:
            return policy.initial_delay * (2 ** (attempt - 1))
            
        elif policy.strategy == RetryStrategy.FIBONACCI:
            if attempt <= 2:
                return policy.initial_delay
            a, b = policy.initial_delay, policy.initial_delay
            for _ in range(attempt - 2):
                a, b = b, a + b
            return b
            
        elif policy.strategy == RetryStrategy.RANDOM:
            return random.uniform(policy.initial_delay, policy.max_delay or policy.initial_delay * 2)
            
        elif policy.strategy == RetryStrategy.CUSTOM and policy.custom_function:
            return policy.custom_function(attempt)
            
        return policy.initial_delay
        
    def record_attempt(self, policy_name: str, attempt: int, error: Exception, delay: float) -> None:
        """Record retry attempt
        
        Args:
            policy_name: Name of the policy used
            attempt: Attempt number
            error: Exception that occurred
            delay: Delay before next attempt
        """
        if policy_name in self.attempt_history:
            self.attempt_history[policy_name].append({
                "attempt": attempt,
                "timestamp": time.time(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "delay": delay
            })
            
    def get_attempt_history(self, policy_name: str) -> List[Dict[str, Any]]:
        """Get history of retry attempts for a policy
        
        Args:
            policy_name: Name of the policy
            
        Returns:
            List of attempt records
        """
        return self.attempt_history.get(policy_name, [])
        
    def clear_history(self, policy_name: Optional[str] = None) -> None:
        """Clear retry attempt history
        
        Args:
            policy_name: Optional policy name to clear history for
        """
        if policy_name:
            self.attempt_history[policy_name] = []
        else:
            self.attempt_history.clear() 