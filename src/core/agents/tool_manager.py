from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import threading
import inspect
import functools
import time
import importlib
import pkg_resources
import hashlib
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class ToolDependency:
    name: str
    version: str
    required_by: str
    is_optional: bool = False

@dataclass
class ToolSecurityPolicy:
    required_permissions: Set[str]
    max_execution_time: float
    allowed_operations: Set[str]
    resource_limits: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]

@dataclass
class ToolPerformanceMetrics:
    execution_times: List[float]
    memory_usage: List[float]
    cpu_usage: List[float]
    success_rate: float
    error_rate: float
    last_optimized: datetime

@dataclass
class ToolCall:
    timestamp: datetime
    tool_name: str
    parameters: Dict[str, Any]
    result: Any
    duration: float
    agent_id: str
    context: Dict[str, Any]
    status: str  # 'success', 'error', 'timeout'
    error: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None

class ToolDiscovery(ABC):
    @abstractmethod
    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools in the system."""
        pass

class PackageToolDiscovery(ToolDiscovery):
    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover tools from installed packages."""
        tools = []
        for entry_point in pkg_resources.iter_entry_points('ade.tools'):
            try:
                tool_module = entry_point.load()
                tools.append({
                    'name': entry_point.name,
                    'module': tool_module,
                    'version': entry_point.dist.version,
                    'description': getattr(tool_module, '__doc__', '')
                })
            except Exception as e:
                logger.error(f"Failed to load tool {entry_point.name}: {str(e)}")
        return tools

class ToolSecurityManager:
    def __init__(self):
        self.security_policies: Dict[str, ToolSecurityPolicy] = {}
        self.permission_cache: Dict[str, Set[str]] = {}
        
    def register_policy(self, tool_name: str, policy: ToolSecurityPolicy) -> None:
        """Register security policy for a tool."""
        self.security_policies[tool_name] = policy
        
    def validate_execution(self, tool_name: str, parameters: Dict[str, Any],
                          agent_permissions: Set[str]) -> bool:
        """Validate tool execution against security policy."""
        if tool_name not in self.security_policies:
            return True  # No policy means no restrictions
            
        policy = self.security_policies[tool_name]
        
        # Check permissions
        if not policy.required_permissions.issubset(agent_permissions):
            return False
            
        # Validate operations
        for operation in parameters.get('operations', []):
            if operation not in policy.allowed_operations:
                return False
                
        # Apply validation rules
        for rule in policy.validation_rules:
            if not self._apply_validation_rule(parameters, rule):
                return False
                
        return True
        
    def _apply_validation_rule(self, parameters: Dict[str, Any],
                             rule: Dict[str, Any]) -> bool:
        """Apply a validation rule to parameters."""
        rule_type = rule.get('type')
        if rule_type == 'regex':
            pattern = rule['pattern']
            field = rule['field']
            return bool(re.match(pattern, str(parameters.get(field, ''))))
        elif rule_type == 'range':
            field = rule['field']
            value = parameters.get(field)
            if value is None:
                return True
            return rule['min'] <= value <= rule['max']
        return True

class ToolPerformanceOptimizer:
    def __init__(self):
        self.metrics: Dict[str, ToolPerformanceMetrics] = {}
        self.optimization_threshold = 0.8  # 80% threshold for optimization
        
    def track_execution(self, tool_name: str, duration: float,
                       memory_usage: float, cpu_usage: float,
                       success: bool) -> None:
        """Track tool execution metrics."""
        if tool_name not in self.metrics:
            self.metrics[tool_name] = ToolPerformanceMetrics(
                execution_times=[],
                memory_usage=[],
                cpu_usage=[],
                success_rate=0.0,
                error_rate=0.0,
                last_optimized=datetime.now()
            )
            
        metrics = self.metrics[tool_name]
        metrics.execution_times.append(duration)
        metrics.memory_usage.append(memory_usage)
        metrics.cpu_usage.append(cpu_usage)
        
        # Update success/error rates
        total_executions = len(metrics.execution_times)
        successful = sum(1 for t in metrics.execution_times if t > 0)
        metrics.success_rate = successful / total_executions
        metrics.error_rate = 1 - metrics.success_rate
        
        # Check if optimization is needed
        if self._should_optimize(metrics):
            self._optimize_tool(tool_name)
            
    def _should_optimize(self, metrics: ToolPerformanceMetrics) -> bool:
        """Determine if tool needs optimization."""
        if not metrics.execution_times:
            return False
            
        avg_execution_time = sum(metrics.execution_times) / len(metrics.execution_times)
        return (avg_execution_time > 1.0 or  # More than 1 second
                metrics.error_rate > 0.2 or  # More than 20% errors
                metrics.success_rate < self.optimization_threshold)
                
    def _optimize_tool(self, tool_name: str) -> None:
        """Optimize tool performance."""
        metrics = self.metrics[tool_name]
        metrics.last_optimized = datetime.now()
        
        # Implement optimization strategies
        # 1. Cache frequently used results
        # 2. Optimize parameter validation
        # 3. Implement batch processing
        # 4. Add result compression
        logger.info(f"Optimizing tool: {tool_name}")

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
        self.call_history: List[ToolCall] = []
        self._lock = threading.Lock()
        self._timeout = 30  # Default timeout in seconds
        
        # Initialize new components
        self.discovery = PackageToolDiscovery()
        self.security_manager = ToolSecurityManager()
        self.performance_optimizer = ToolPerformanceOptimizer()
        self.dependencies: Dict[str, List[ToolDependency]] = {}
        
        # Auto-discover tools
        self._discover_tools()
        
    def _discover_tools(self) -> None:
        """Discover and register available tools."""
        discovered_tools = self.discovery.discover_tools()
        for tool_info in discovered_tools:
            try:
                self.register_tool(
                    name=tool_info['name'],
                    tool=tool_info['module'],
                    metadata={
                        'version': tool_info['version'],
                        'description': tool_info['description']
                    }
                )
            except Exception as e:
                logger.error(f"Failed to register discovered tool {tool_info['name']}: {str(e)}")
                
    def register_tool(self, name: str, tool: Callable, 
                     metadata: Optional[Dict[str, Any]] = None,
                     dependencies: Optional[List[ToolDependency]] = None,
                     security_policy: Optional[ToolSecurityPolicy] = None) -> None:
        """Register a new tool with metadata, dependencies, and security policy."""
        if not callable(tool):
            raise ValueError(f"Tool {name} must be callable")
            
        self.tools[name] = tool
        self.tool_metadata[name] = metadata or {}
        
        # Add parameter validation
        sig = inspect.signature(tool)
        self.tool_metadata[name]['parameters'] = {
            param.name: {
                'type': param.annotation if param.annotation != inspect.Parameter.empty else Any,
                'default': param.default if param.default != inspect.Parameter.empty else None,
                'required': param.default == inspect.Parameter.empty
            }
            for param in sig.parameters.values()
        }
        
        # Register dependencies
        if dependencies:
            self.dependencies[name] = dependencies
            
        # Register security policy
        if security_policy:
            self.security_manager.register_policy(name, security_policy)
            
    def execute_tool(self, name: str, parameters: Dict[str, Any],
                    agent_id: str, context: Dict[str, Any],
                    agent_permissions: Set[str]) -> Any:
        """Execute a registered tool with given parameters."""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
            
        # Validate dependencies
        self._validate_dependencies(name)
        
        # Validate security
        if not self.security_manager.validate_execution(name, parameters, agent_permissions):
            raise PermissionError(f"Security policy violation for tool {name}")
            
        # Validate parameters
        self._validate_parameters(name, parameters)
        
        # Execute tool with timeout and performance tracking
        start_time = time.time()
        try:
            result = self._execute_with_timeout(name, parameters)
            status = 'success'
            error = None
        except TimeoutError:
            status = 'timeout'
            result = None
            error = f"Tool {name} execution timed out after {self._timeout} seconds"
        except Exception as e:
            status = 'error'
            result = None
            error = str(e)
            
        duration = time.time() - start_time
        
        # Track performance metrics
        performance_metrics = self._get_performance_metrics()
        self.performance_optimizer.track_execution(
            name, duration,
            performance_metrics['memory_usage'],
            performance_metrics['cpu_usage'],
            status == 'success'
        )
        
        # Record call with performance metrics
        call = ToolCall(
            timestamp=datetime.now(),
            tool_name=name,
            parameters=parameters,
            result=result,
            duration=duration,
            agent_id=agent_id,
            context=context,
            status=status,
            error=error,
            performance_metrics=performance_metrics
        )
        
        with self._lock:
            self.call_history.append(call)
            
        if status != 'success':
            raise RuntimeError(f"Tool execution failed: {error}")
            
        return result
        
    def _validate_dependencies(self, name: str) -> None:
        """Validate tool dependencies."""
        if name not in self.dependencies:
            return
            
        for dep in self.dependencies[name]:
            try:
                pkg_resources.require(f"{dep.name}=={dep.version}")
            except pkg_resources.VersionConflict:
                raise ValueError(f"Version conflict for dependency {dep.name}")
            except pkg_resources.DistributionNotFound:
                if not dep.is_optional:
                    raise ValueError(f"Required dependency {dep.name} not found")
                    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        import psutil
        process = psutil.Process()
        return {
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'cpu_usage': process.cpu_percent(),
            'thread_count': process.num_threads()
        }
        
    def _execute_with_timeout(self, name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool with timeout."""
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def execute():
            try:
                result = self.tools[name](**parameters)
                result_queue.put(('success', result))
            except Exception as e:
                result_queue.put(('error', e))
                
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()
        
        try:
            status, result = result_queue.get(timeout=self._timeout)
            if status == 'error':
                raise result
            return result
        except queue.Empty:
            raise TimeoutError()
            
    def _validate_parameters(self, name: str, parameters: Dict[str, Any]) -> None:
        """Validate tool parameters against signature."""
        metadata = self.tool_metadata[name]
        param_specs = metadata['parameters']
        
        # Check for missing required parameters
        missing = [
            name for name, spec in param_specs.items()
            if spec['required'] and name not in parameters
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
            
        # Check for unknown parameters
        unknown = [
            name for name in parameters
            if name not in param_specs
        ]
        if unknown:
            raise ValueError(f"Unknown parameters: {', '.join(unknown)}")
            
        # Validate parameter types
        for name, value in parameters.items():
            spec = param_specs[name]
            expected_type = spec['type']
            
            if expected_type != Any and not isinstance(value, expected_type):
                raise TypeError(
                    f"Parameter {name} must be of type {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                
    def get_tool_history(self, agent_id: Optional[str] = None,
                        tool_name: Optional[str] = None,
                        status: Optional[str] = None) -> List[ToolCall]:
        """Get filtered tool call history."""
        with self._lock:
            filtered = self.call_history
            
            if agent_id:
                filtered = [call for call in filtered if call.agent_id == agent_id]
            if tool_name:
                filtered = [call for call in filtered if call.tool_name == tool_name]
            if status:
                filtered = [call for call in filtered if call.status == status]
                
            return filtered
            
    def get_tool_metrics(self) -> Dict[str, Any]:
        """Get metrics about tool usage."""
        with self._lock:
            metrics = {
                'total_calls': len(self.call_history),
                'success_rate': 0,
                'avg_duration': 0,
                'tool_usage': {},
                'error_rates': {}
            }
            
            if not self.call_history:
                return metrics
                
            # Calculate success rate
            successful = sum(1 for call in self.call_history if call.status == 'success')
            metrics['success_rate'] = successful / len(self.call_history)
            
            # Calculate average duration
            total_duration = sum(call.duration for call in self.call_history)
            metrics['avg_duration'] = total_duration / len(self.call_history)
            
            # Calculate tool usage
            for call in self.call_history:
                if call.tool_name not in metrics['tool_usage']:
                    metrics['tool_usage'][call.tool_name] = {
                        'calls': 0,
                        'success_rate': 0,
                        'avg_duration': 0
                    }
                    
                tool_metrics = metrics['tool_usage'][call.tool_name]
                tool_metrics['calls'] += 1
                tool_metrics['success_rate'] = sum(
                    1 for c in self.call_history
                    if c.tool_name == call.tool_name and c.status == 'success'
                ) / tool_metrics['calls']
                tool_metrics['avg_duration'] = sum(
                    c.duration for c in self.call_history
                    if c.tool_name == call.tool_name
                ) / tool_metrics['calls']
                
            # Calculate error rates
            for call in self.call_history:
                if call.status == 'error':
                    if call.tool_name not in metrics['error_rates']:
                        metrics['error_rates'][call.tool_name] = {}
                    error_type = type(call.error).__name__
                    metrics['error_rates'][call.tool_name][error_type] = \
                        metrics['error_rates'][call.tool_name].get(error_type, 0) + 1
                        
            return metrics
            
    def export_data(self, file_path: str) -> None:
        """Export tool call history to file."""
        with self._lock:
            data = {
                'calls': [
                    {
                        'timestamp': call.timestamp.isoformat(),
                        'tool_name': call.tool_name,
                        'parameters': call.parameters,
                        'result': str(call.result) if call.result is not None else None,
                        'duration': call.duration,
                        'agent_id': call.agent_id,
                        'context': call.context,
                        'status': call.status,
                        'error': call.error
                    }
                    for call in self.call_history
                ],
                'tools': {
                    name: {
                        'metadata': metadata,
                        'parameters': self.tool_metadata[name]['parameters']
                    }
                    for name, metadata in self.tool_metadata.items()
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    def import_data(self, file_path: str) -> None:
        """Import tool call history from file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        with self._lock:
            self.call_history = [
                ToolCall(
                    timestamp=datetime.fromisoformat(call['timestamp']),
                    tool_name=call['tool_name'],
                    parameters=call['parameters'],
                    result=call['result'],
                    duration=call['duration'],
                    agent_id=call['agent_id'],
                    context=call['context'],
                    status=call['status'],
                    error=call.get('error')
                )
                for call in data['calls']
            ]
            
            # Note: Tool registration metadata is not imported as it requires
            # the actual tool functions to be available 