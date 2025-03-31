from typing import Dict, Any, List, Optional, Tuple, Set
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
import ast
import importlib
import sys
from pathlib import Path
import os
import time
import psutil
import resource
import concurrent.futures
from functools import lru_cache
from src.core.error.retry_policy import RetryManager, RetryPolicy, RetryStrategy, CircuitBreaker, CircuitBreakerState
from src.core.error.error_detector import ErrorDetector
from src.core.error.root_cause_analyzer import RootCauseAnalyzer
from src.core.code.fix_manager import FixManager
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine
from src.core.resource.resource_manager import ResourceManager, ResourceQuota

logger = logging.getLogger(__name__)

# Default resource limits
DEFAULT_MEMORY_LIMIT = 512  # MB
DEFAULT_CPU_PERCENT = 80
DEFAULT_DISK_IO = 100  # MB/s
DEFAULT_NETWORK_IO = 100  # MB/s
DEFAULT_OPEN_FILES = 100
DEFAULT_MAX_THREADS = 4
DEFAULT_TIMEOUT = 30.0

@dataclass
class ResourceLimits:
    """Resource limits for script execution"""
    memory_limit: int = DEFAULT_MEMORY_LIMIT
    cpu_percent: int = DEFAULT_CPU_PERCENT
    open_files: int = DEFAULT_OPEN_FILES
    max_threads: int = DEFAULT_MAX_THREADS
    timeout: float = DEFAULT_TIMEOUT

@dataclass
class ScriptContext:
    """Context for script execution"""
    script_id: str
    original_code: str
    parsed_ast: Optional[ast.AST] = None
    dependencies: List[str] = None
    environment_vars: Dict[str, str] = None
    working_directory: str = None
    timeout: float = DEFAULT_TIMEOUT
    max_memory: int = DEFAULT_MEMORY_LIMIT

@dataclass
class ExecutionResult:
    """Result of script execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0
    return_value: Any = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    resource_usage: Optional[Dict[str, Any]] = None

class ScriptManager:
    """Manages script execution with error handling, retries, and code fixing"""
    
    def __init__(
        self,
        retry_manager: Optional[RetryManager] = None,
        error_detector: Optional[ErrorDetector] = None,
        root_cause_analyzer: Optional[RootCauseAnalyzer] = None,
        fix_manager: Optional[FixManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        analytics_engine: Optional[AnalyticsEngine] = None,
        logger: Optional[logging.Logger] = None,
        resource_limits: Optional[ResourceLimits] = None
    ):
        self.retry_manager = retry_manager or RetryManager()
        self.error_detector = error_detector or ErrorDetector()
        self.root_cause_analyzer = root_cause_analyzer or RootCauseAnalyzer()
        self.fix_manager = fix_manager or FixManager()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.analytics_engine = analytics_engine or AnalyticsEngine()
        self.logger = logger or logging.getLogger("script_manager")
        self.resource_limits = resource_limits or ResourceLimits()
        
        # Initialize resource manager
        self.resource_manager = ResourceManager(
            quota=ResourceQuota(
                memory_limit=self.resource_limits.memory_limit,
                cpu_percent=self.resource_limits.cpu_percent,
                disk_io=DEFAULT_DISK_IO,
                network_io=DEFAULT_NETWORK_IO,
                open_files=self.resource_limits.open_files,
                max_threads=self.resource_limits.max_threads,
                timeout=self.resource_limits.timeout
            ),
            metrics_collector=self.metrics_collector,
            analytics_engine=self.analytics_engine
        )
        
        # Initialize thread pool for parallel execution
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.resource_limits.max_threads
        )
        
        # Initialize script cache
        self.script_cache: Dict[str, ScriptContext] = {}
        self.dependency_cache: Dict[str, Set[str]] = {}
        
        # Initialize default retry policy
        self._setup_default_retry_policy()
    
    async def execute_script(self, script_id: str) -> ExecutionResult:
        """Execute a parsed script with resource monitoring"""
        if script_id not in self.script_cache:
            raise ValueError(f"Script {script_id} not found")
            
        context = self.script_cache[script_id]
        start_time = datetime.now()
        
        # Start metrics collection
        self.metrics_collector.start_collection()
        
        try:
            # Create execution environment
            env = self._create_execution_environment(context)
            
            # Start resource monitoring
            await self.resource_manager.start_monitoring(psutil.Process().pid)
            
            # Execute script with resource monitoring
            result = await self._execute_with_monitoring(
                context.original_code,
                env,
                context.timeout,
                context.max_memory
            )
            
            # Get final resource usage
            resource_usage = self.resource_manager.get_current_usage()
            
            # Stop resource monitoring
            await self.resource_manager.stop_monitoring()
            
            # Record metrics
            metrics = self.metrics_collector.stop_collection()
            self.analytics_engine.add_metrics(metrics)
            
            return ExecutionResult(
                success=True,
                output=result.get("output"),
                execution_time=(datetime.now() - start_time).total_seconds(),
                memory_usage=result.get("memory_usage", 0.0),
                return_value=result.get("return_value"),
                stdout=result.get("stdout"),
                stderr=result.get("stderr"),
                resource_usage=resource_usage
            )
            
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            
            # Stop resource monitoring
            await self.resource_manager.stop_monitoring()
            
            # Record error metrics and analytics
            metrics = self.metrics_collector.stop_collection()
            self.analytics_engine.add_metrics(metrics)
            self.analytics_engine.add_error(
                type(e).__name__,
                str(e),
                {"script_id": script_id, "context": context}
            )
            
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _execute_with_monitoring(self,
                                    code: str,
                                    env: Dict[str, Any],
                                    timeout: float,
                                    max_memory: int) -> Dict[str, Any]:
        """Execute code with comprehensive resource monitoring"""
        import io
        import sys
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        try:
            # Execute code with timeout and resource monitoring
            async with asyncio.timeout(timeout):
                # Execute code in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self._execute_code,
                    code,
                    env
                )
                
                # Get final resource usage
                usage = self.resource_manager.get_current_usage()
                
                return {
                    "output": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                    "memory_usage": usage["memory_used"] if usage else 0.0,
                    "cpu_usage": usage["cpu_percent"] if usage else 0.0,
                    "disk_io": {
                        "read": usage["disk_read"] if usage else 0.0,
                        "write": usage["disk_write"] if usage else 0.0
                    } if usage else {"read": 0.0, "write": 0.0},
                    "network_io": {
                        "sent": usage["network_sent"] if usage else 0.0,
                        "recv": usage["network_recv"] if usage else 0.0
                    } if usage else {"sent": 0.0, "recv": 0.0},
                    "return_value": result
                }
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"Execution timed out after {timeout} seconds")
        finally:
            # Restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
    
    def _execute_code(self, code: str, env: Dict[str, Any]) -> Any:
        """Execute code in isolated environment"""
        # Create isolated namespace
        namespace = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if not name.startswith('_')
            },
            **env
        }
        
        # Execute code
        exec(code, namespace)
        return namespace.get("__result__")
    
    def clear_cache(self):
        """Clear script and dependency caches"""
        self.script_cache.clear()
        self.dependency_cache.clear()
        self._parse_script.cache_clear()
        self._extract_dependencies.cache_clear()
    
    def __del__(self):
        """Cleanup resources"""
        self.thread_pool.shutdown(wait=True)
        self.clear_cache()
    
    def _setup_default_retry_policy(self):
        """Set up default retry policy for script execution"""
        default_policy = RetryPolicy(
            name="script_execution",
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
    
    def execute_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        retry_policy_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Any]:
        """
        Execute a script with error handling, retries, and code fixing
        
        Args:
            script_path: Path to the script to execute
            args: Command line arguments for the script
            env: Environment variables for script execution
            retry_policy_name: Name of the retry policy to use
            context: Additional context for error analysis
            
        Returns:
            Tuple of (success, result)
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        policy_name = retry_policy_name or "script_execution"
        policy = self.retry_manager.get_policy(policy_name)
        if not policy:
            raise ValueError(f"Retry policy '{policy_name}' not found")
        
        attempt = 1
        last_error = None
        
        # Start metrics collection
        self.metrics_collector.start_collection()
        
        while attempt <= policy.max_attempts:
            try:
                # Check circuit breaker
                if policy.circuit_breaker and policy.circuit_breaker.state == CircuitBreakerState.OPEN:
                    self.logger.warning(f"Circuit breaker is open for policy '{policy_name}'")
                    raise last_error or RuntimeError("Circuit breaker is open")
                
                # Start resource monitoring
                asyncio.create_task(self.resource_manager.start_monitoring(psutil.Process().pid))
                
                # Execute script
                result = self._run_script(script_path, args, env)
                
                # Stop resource monitoring
                asyncio.create_task(self.resource_manager.stop_monitoring())
                
                # Record success
                if policy.circuit_breaker:
                    policy.circuit_breaker.record_success()
                    self.analytics_engine.add_circuit_breaker_state(
                        policy_name,
                        policy.circuit_breaker.state,
                        policy.circuit_breaker.failure_rate
                    )
                
                # Record metrics and analytics
                metrics = self.metrics_collector.stop_collection()
                self.analytics_engine.add_metrics(metrics)
                self.analytics_engine.add_retry(policy_name, attempt, 0.0, True)
                
                return True, result
                
            except Exception as e:
                last_error = e
                
                # Stop resource monitoring
                asyncio.create_task(self.resource_manager.stop_monitoring())
                
                # Record failure
                if policy.circuit_breaker:
                    policy.circuit_breaker.record_failure()
                    self.analytics_engine.add_circuit_breaker_state(
                        policy_name,
                        policy.circuit_breaker.state,
                        policy.circuit_breaker.failure_rate
                    )
                
                # Detect and analyze error
                error_info = self.error_detector.detect_error(e, context)
                self.analytics_engine.add_error(
                    error_info["type"],
                    str(e),
                    error_info.get("context", {})
                )
                
                # Analyze root cause
                causes = self.root_cause_analyzer.analyze_error(e)
                if causes:
                    self.logger.warning(f"Root causes detected: {[cause.cause_type for cause in causes]}")
                    
                    # Attempt to fix code based on root causes
                    for cause in causes:
                        if self.fix_manager.can_fix(cause):
                            try:
                                success = self.fix_manager.apply_fix(cause, script_path)
                                self.analytics_engine.add_fix(
                                    cause.cause_type,
                                    success,
                                    {"cause": cause, "file": script_path}
                                )
                                if success:
                                    self.logger.info(f"Applied fix for cause: {cause.cause_type}")
                            except Exception as fix_error:
                                self.logger.error(f"Failed to apply fix: {str(fix_error)}")
                
                # Check if we should retry
                if not self.retry_manager.should_retry(policy_name, e):
                    self.logger.error(f"Script execution failed and will not be retried: {str(e)}")
                    
                    # Record final metrics and analytics
                    metrics = self.metrics_collector.stop_collection()
                    self.analytics_engine.add_metrics(metrics)
                    self.analytics_engine.add_retry(policy_name, attempt, 0.0, False)
                    
                    return False, e
                
                # Calculate delay
                delay = self.retry_manager.get_delay(policy_name, attempt)
                
                # Log retry attempt
                self.logger.warning(
                    f"Script execution failed (attempt {attempt}/{policy.max_attempts}). "
                    f"Retrying in {delay:.2f} seconds. Error: {str(e)}"
                )
                
                # Record attempt
                self.retry_manager.record_attempt(
                    policy_name,
                    attempt,
                    e,
                    delay
                )
                
                # Record metrics and analytics
                metrics = self.metrics_collector.stop_collection()
                self.analytics_engine.add_metrics(metrics)
                self.analytics_engine.add_retry(policy_name, attempt, delay, False)
                
                # Wait before retry
                time.sleep(delay)
                attempt += 1
        
        # If we get here, all retries failed
        self.logger.error(f"Script execution failed after {policy.max_attempts} attempts")
        
        # Record final metrics and analytics
        metrics = self.metrics_collector.stop_collection()
        self.analytics_engine.add_metrics(metrics)
        self.analytics_engine.add_retry(policy_name, attempt, 0.0, False)
        
        return False, last_error
    
    def _run_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Any:
        """Execute a script and return its result"""
        # Prepare command
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        # Prepare environment
        script_env = os.environ.copy()
        if env:
            script_env.update(env)
        
        # Execute script
        try:
            import subprocess
            result = subprocess.run(
                cmd,
                env=script_env,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Script execution failed: {e.stderr}")
    
    def get_retry_history(self, policy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get retry attempt history for a policy"""
        policy_name = policy_name or "script_execution"
        return self.retry_manager.get_attempt_history(policy_name)
    
    def get_error_history(self) -> List[Dict[str, Any]]:
        """Get error detection history"""
        return self.error_detector.get_error_history()
    
    def clear_histories(self):
        """Clear all histories"""
        self.retry_manager.clear_history()
        self.error_detector.clear_history()
        self.metrics_collector.clear_alerts()
    
    def get_circuit_breaker_state(self, policy_name: Optional[str] = None) -> CircuitBreakerState:
        """Get circuit breaker state for a policy"""
        policy_name = policy_name or "script_execution"
        policy = self.retry_manager.get_policy(policy_name)
        if not policy or not policy.circuit_breaker:
            return None
        return policy.circuit_breaker.state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics_collector.get_metrics()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get current analytics"""
        return self.analytics_engine.get_analytics()
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts"""
        return self.metrics_collector.get_alerts()
    
    def get_resource_usage(self) -> Optional[Dict[str, Any]]:
        """Get current resource usage"""
        return self.resource_manager.get_current_usage()
    
    def get_resource_history(self) -> List[Dict[str, Any]]:
        """Get resource usage history"""
        return self.resource_manager.get_usage_history()
    
    def _create_execution_environment(self, context: ScriptContext) -> Dict[str, Any]:
        """Create isolated execution environment
        
        Args:
            context: Script execution context
            
        Returns:
            Dictionary containing execution environment
        """
        env = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if not name.startswith('_')
            },
            **context.environment_vars
        }
        
        # Add common modules
        common_modules = [
            "os", "sys", "math", "random", "datetime",
            "json", "re", "collections", "itertools"
        ]
        
        for module_name in common_modules:
            try:
                module = importlib.import_module(module_name)
                env[module_name] = module
            except ImportError:
                logger.warning(f"Failed to import common module {module_name}")
                
        return env 