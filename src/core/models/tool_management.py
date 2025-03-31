"""Intelligent tool discovery and management system."""

import os
import sys
import importlib
import inspect
import pkg_resources
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
import time
import psutil
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import lru_cache

@dataclass
class ToolMetadata:
    """Metadata for a discovered tool."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    entry_points: List[str]
    security_level: str
    performance_metrics: Dict[str, float]
    last_used: float
    usage_count: int

@dataclass
class ToolSecurityProfile:
    """Security profile for a tool."""
    tool_name: str
    permissions_required: Set[str]
    network_access: bool
    file_system_access: bool
    system_access: bool
    security_risks: List[str]
    mitigation_strategies: List[str]
    audit_logging: bool
    sandbox_enabled: bool

@dataclass
class ToolPerformanceProfile:
    """Performance profile for a tool."""
    tool_name: str
    avg_execution_time: float
    memory_usage: float
    cpu_usage: float
    io_operations: int
    cache_hit_rate: float
    concurrent_usage: int
    resource_limits: Dict[str, float]

class ToolManager:
    """Manages tool discovery, dependencies, performance, and security."""
    
    def __init__(self, base_path: str):
        """Initialize the tool manager.
        
        Args:
            base_path: Base path for tool discovery
        """
        self.base_path = Path(base_path)
        self.tools: Dict[str, ToolMetadata] = {}
        self.security_profiles: Dict[str, ToolSecurityProfile] = {}
        self.performance_profiles: Dict[str, ToolPerformanceProfile] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.tool_cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def discover_tools(self) -> List[str]:
        """Discover available tools in the project.
        
        Returns:
            List of discovered tool names
        """
        discovered_tools = []
        
        # Scan for Python modules
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.py'):
                    module_path = Path(root) / file
                    try:
                        tool_name = self._extract_tool_name(module_path)
                        if tool_name:
                            discovered_tools.append(tool_name)
                            self._analyze_tool(module_path)
                    except Exception as e:
                        self.logger.error(f"Error analyzing tool {module_path}: {e}")
                        
        # Scan for entry points
        for entry_point in pkg_resources.iter_entry_points('ade.tools'):
            try:
                tool_name = entry_point.name
                discovered_tools.append(tool_name)
                self._analyze_entry_point(entry_point)
            except Exception as e:
                self.logger.error(f"Error analyzing entry point {entry_point.name}: {e}")
                
        return discovered_tools
        
    def _extract_tool_name(self, file_path: Path) -> Optional[str]:
        """Extract tool name from file path.
        
        Args:
            file_path: Path to the tool file
            
        Returns:
            Tool name if found, None otherwise
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for tool decorator or class
            if '@tool' in content or 'class Tool' in content:
                return file_path.stem
                
            # Look for entry point
            if 'entry_points' in content:
                for line in content.split('\n'):
                    if 'ade.tools' in line:
                        return line.split('=')[0].strip()
                        
        except Exception as e:
            self.logger.error(f"Error extracting tool name from {file_path}: {e}")
            
        return None
        
    def _analyze_tool(self, file_path: Path):
        """Analyze a tool file for metadata and dependencies.
        
        Args:
            file_path: Path to the tool file
        """
        try:
            # Import the module
            module_name = str(file_path.relative_to(self.base_path)).replace('/', '.')
            module = importlib.import_module(module_name)
            
            # Extract metadata
            metadata = self._extract_metadata(module)
            self.tools[metadata.name] = metadata
            
            # Analyze dependencies
            self._analyze_dependencies(module)
            
            # Create security profile
            self._create_security_profile(metadata.name, module)
            
            # Create performance profile
            self._create_performance_profile(metadata.name, module)
            
        except Exception as e:
            self.logger.error(f"Error analyzing tool {file_path}: {e}")
            
    def _extract_metadata(self, module: Any) -> ToolMetadata:
        """Extract metadata from a module.
        
        Args:
            module: The module to analyze
            
        Returns:
            ToolMetadata object
        """
        return ToolMetadata(
            name=module.__name__,
            version=getattr(module, '__version__', 'unknown'),
            description=getattr(module, '__doc__', ''),
            author=getattr(module, '__author__', 'unknown'),
            dependencies=self._get_dependencies(module),
            entry_points=self._get_entry_points(module),
            security_level=self._determine_security_level(module),
            performance_metrics=self._get_performance_metrics(module),
            last_used=time.time(),
            usage_count=0
        )
        
    def _get_dependencies(self, module: Any) -> List[str]:
        """Get module dependencies.
        
        Args:
            module: The module to analyze
            
        Returns:
            List of dependency names
        """
        dependencies = []
        
        # Check imports
        for name, obj in inspect.getmembers(module):
            if inspect.ismodule(obj):
                dependencies.append(obj.__name__)
                
        # Check requirements
        if hasattr(module, 'requirements'):
            dependencies.extend(module.requirements)
            
        return list(set(dependencies))
        
    def _get_entry_points(self, module: Any) -> List[str]:
        """Get module entry points.
        
        Args:
            module: The module to analyze
            
        Returns:
            List of entry point names
        """
        entry_points = []
        
        # Check for entry point decorators
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '_is_entry_point'):
                entry_points.append(name)
                
        return entry_points
        
    def _determine_security_level(self, module: Any) -> str:
        """Determine module security level.
        
        Args:
            module: The module to analyze
            
        Returns:
            Security level string
        """
        # Check for security annotations
        if hasattr(module, 'security_level'):
            return module.security_level
            
        # Analyze code for security implications
        security_indicators = {
            'high': ['subprocess', 'os.system', 'eval', 'exec'],
            'medium': ['open', 'socket', 'requests'],
            'low': ['json', 'datetime', 'math']
        }
        
        module_source = inspect.getsource(module)
        for level, indicators in security_indicators.items():
            if any(indicator in module_source for indicator in indicators):
                return level
                
        return 'low'
        
    def _get_performance_metrics(self, module: Any) -> Dict[str, float]:
        """Get module performance metrics.
        
        Args:
            module: The module to analyze
            
        Returns:
            Dictionary of performance metrics
        """
        metrics = {
            'execution_time': 0.0,
            'memory_usage': 0.0,
            'cpu_usage': 0.0
        }
        
        # Run performance tests if available
        if hasattr(module, 'performance_test'):
            try:
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                start_cpu = psutil.cpu_percent()
                
                module.performance_test()
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                end_cpu = psutil.cpu_percent()
                
                metrics.update({
                    'execution_time': end_time - start_time,
                    'memory_usage': (end_memory - start_memory) / 1024 / 1024,
                    'cpu_usage': (end_cpu + start_cpu) / 2
                })
            except Exception as e:
                self.logger.error(f"Error running performance test for {module.__name__}: {e}")
                
        return metrics
        
    def _create_security_profile(self, tool_name: str, module: Any):
        """Create security profile for a tool.
        
        Args:
            tool_name: Name of the tool
            module: The tool's module
        """
        profile = ToolSecurityProfile(
            tool_name=tool_name,
            permissions_required=self._analyze_permissions(module),
            network_access=self._has_network_access(module),
            file_system_access=self._has_fs_access(module),
            system_access=self._has_system_access(module),
            security_risks=self._identify_security_risks(module),
            mitigation_strategies=self._get_mitigation_strategies(module),
            audit_logging=self._has_audit_logging(module),
            sandbox_enabled=self._is_sandboxed(module)
        )
        
        self.security_profiles[tool_name] = profile
        
    def _analyze_permissions(self, module: Any) -> Set[str]:
        """Analyze required permissions.
        
        Args:
            module: The module to analyze
            
        Returns:
            Set of required permissions
        """
        permissions = set()
        
        # Check for permission decorators
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '_required_permissions'):
                permissions.update(obj._required_permissions)
                
        # Analyze code for permission indicators
        source = inspect.getsource(module)
        permission_indicators = {
            'file_read': ['open(', 'read(', 'readline('],
            'file_write': ['write(', 'writelines('],
            'network': ['socket', 'requests', 'http'],
            'system': ['subprocess', 'os.system', 'shell=True']
        }
        
        for permission, indicators in permission_indicators.items():
            if any(indicator in source for indicator in indicators):
                permissions.add(permission)
                
        return permissions
        
    def _has_network_access(self, module: Any) -> bool:
        """Check if module has network access.
        
        Args:
            module: The module to analyze
            
        Returns:
            True if module has network access
        """
        source = inspect.getsource(module)
        network_indicators = ['socket', 'requests', 'http', 'urllib', 'ftplib']
        return any(indicator in source for indicator in network_indicators)
        
    def _has_fs_access(self, module: Any) -> bool:
        """Check if module has filesystem access.
        
        Args:
            module: The module to analyze
            
        Returns:
            True if module has filesystem access
        """
        source = inspect.getsource(module)
        fs_indicators = ['open(', 'os.path', 'shutil', 'file']
        return any(indicator in source for indicator in fs_indicators)
        
    def _has_system_access(self, module: Any) -> bool:
        """Check if module has system access.
        
        Args:
            module: The module to analyze
            
        Returns:
            True if module has system access
        """
        source = inspect.getsource(module)
        system_indicators = ['subprocess', 'os.system', 'shell=True', 'commands']
        return any(indicator in source for indicator in system_indicators)
        
    def _identify_security_risks(self, module: Any) -> List[str]:
        """Identify security risks in module.
        
        Args:
            module: The module to analyze
            
        Returns:
            List of security risks
        """
        risks = []
        source = inspect.getsource(module)
        
        # Check for common security issues
        risk_patterns = {
            'SQL Injection': ['execute(', 'executemany(', 'format(', 'f"'],
            'XSS': ['innerHTML', 'document.write', 'eval('],
            'Command Injection': ['subprocess', 'os.system', 'shell=True'],
            'File Inclusion': ['open(', 'include(', 'require('],
            'Hardcoded Secrets': ['password', 'secret', 'key', 'token']
        }
        
        for risk, patterns in risk_patterns.items():
            if any(pattern in source for pattern in patterns):
                risks.append(risk)
                
        return risks
        
    def _get_mitigation_strategies(self, module: Any) -> List[str]:
        """Get security mitigation strategies.
        
        Args:
            module: The module to analyze
            
        Returns:
            List of mitigation strategies
        """
        strategies = []
        source = inspect.getsource(module)
        
        # Check for security best practices
        if 'parametrize' in source:
            strategies.append('Use parameterized queries')
        if 'escape' in source:
            strategies.append('Escape user input')
        if 'validate' in source:
            strategies.append('Validate input data')
        if 'sanitize' in source:
            strategies.append('Sanitize output')
        if 'encrypt' in source:
            strategies.append('Encrypt sensitive data')
            
        return strategies
        
    def _has_audit_logging(self, module: Any) -> bool:
        """Check if module has audit logging.
        
        Args:
            module: The module to analyze
            
        Returns:
            True if module has audit logging
        """
        source = inspect.getsource(module)
        logging_indicators = ['logging', 'audit', 'log_event', 'track']
        return any(indicator in source for indicator in logging_indicators)
        
    def _is_sandboxed(self, module: Any) -> bool:
        """Check if module is sandboxed.
        
        Args:
            module: The module to analyze
            
        Returns:
            True if module is sandboxed
        """
        source = inspect.getsource(module)
        sandbox_indicators = ['sandbox', 'isolate', 'restricted', 'secure']
        return any(indicator in source for indicator in sandbox_indicators)
        
    def _create_performance_profile(self, tool_name: str, module: Any):
        """Create performance profile for a tool.
        
        Args:
            tool_name: Name of the tool
            module: The tool's module
        """
        profile = ToolPerformanceProfile(
            tool_name=tool_name,
            avg_execution_time=self._measure_execution_time(module),
            memory_usage=self._measure_memory_usage(module),
            cpu_usage=self._measure_cpu_usage(module),
            io_operations=self._count_io_operations(module),
            cache_hit_rate=self._calculate_cache_hit_rate(module),
            concurrent_usage=self._get_concurrent_usage(module),
            resource_limits=self._get_resource_limits(module)
        )
        
        self.performance_profiles[tool_name] = profile
        
    def _measure_execution_time(self, module: Any) -> float:
        """Measure average execution time.
        
        Args:
            module: The module to analyze
            
        Returns:
            Average execution time in seconds
        """
        if hasattr(module, 'performance_test'):
            try:
                times = []
                for _ in range(5):  # Run 5 times for average
                    start_time = time.time()
                    module.performance_test()
                    times.append(time.time() - start_time)
                return sum(times) / len(times)
            except Exception as e:
                self.logger.error(f"Error measuring execution time for {module.__name__}: {e}")
        return 0.0
        
    def _measure_memory_usage(self, module: Any) -> float:
        """Measure memory usage.
        
        Args:
            module: The module to analyze
            
        Returns:
            Memory usage in MB
        """
        if hasattr(module, 'performance_test'):
            try:
                process = psutil.Process()
                start_memory = process.memory_info().rss
                module.performance_test()
                end_memory = process.memory_info().rss
                return (end_memory - start_memory) / 1024 / 1024
            except Exception as e:
                self.logger.error(f"Error measuring memory usage for {module.__name__}: {e}")
        return 0.0
        
    def _measure_cpu_usage(self, module: Any) -> float:
        """Measure CPU usage.
        
        Args:
            module: The module to analyze
            
        Returns:
            CPU usage percentage
        """
        if hasattr(module, 'performance_test'):
            try:
                start_cpu = psutil.cpu_percent()
                module.performance_test()
                end_cpu = psutil.cpu_percent()
                return (start_cpu + end_cpu) / 2
            except Exception as e:
                self.logger.error(f"Error measuring CPU usage for {module.__name__}: {e}")
        return 0.0
        
    def _count_io_operations(self, module: Any) -> int:
        """Count I/O operations.
        
        Args:
            module: The module to analyze
            
        Returns:
            Number of I/O operations
        """
        source = inspect.getsource(module)
        io_indicators = ['open(', 'read(', 'write(', 'close(', 'flush(']
        return sum(source.count(indicator) for indicator in io_indicators)
        
    def _calculate_cache_hit_rate(self, module: Any) -> float:
        """Calculate cache hit rate.
        
        Args:
            module: The module to analyze
            
        Returns:
            Cache hit rate as percentage
        """
        if hasattr(module, 'cache_stats'):
            try:
                stats = module.cache_stats()
                hits = stats.get('hits', 0)
                misses = stats.get('misses', 0)
                total = hits + misses
                return (hits / total * 100) if total > 0 else 0.0
            except Exception as e:
                self.logger.error(f"Error calculating cache hit rate for {module.__name__}: {e}")
        return 0.0
        
    def _get_concurrent_usage(self, module: Any) -> int:
        """Get concurrent usage limit.
        
        Args:
            module: The module to analyze
            
        Returns:
            Maximum concurrent usage
        """
        if hasattr(module, 'max_concurrent'):
            return module.max_concurrent
        return 1  # Default to single usage
        
    def _get_resource_limits(self, module: Any) -> Dict[str, float]:
        """Get resource limits.
        
        Args:
            module: The module to analyze
            
        Returns:
            Dictionary of resource limits
        """
        limits = {
            'memory': 1024,  # Default 1GB
            'cpu': 100,      # Default 100%
            'io': 1000,      # Default 1000 ops
            'time': 60       # Default 60 seconds
        }
        
        if hasattr(module, 'resource_limits'):
            try:
                module_limits = module.resource_limits()
                limits.update(module_limits)
            except Exception as e:
                self.logger.error(f"Error getting resource limits for {module.__name__}: {e}")
                
        return limits
        
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing tool information
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        return {
            'metadata': self.tools[tool_name],
            'security': self.security_profiles.get(tool_name),
            'performance': self.performance_profiles.get(tool_name),
            'dependencies': self.dependency_graph.get(tool_name, set())
        }
        
    def optimize_tool(self, tool_name: str) -> Dict[str, Any]:
        """Optimize a tool's performance.
        
        Args:
            tool_name: Name of the tool to optimize
            
        Returns:
            Dictionary containing optimization results
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        results = {
            'original_metrics': self.performance_profiles[tool_name],
            'optimizations_applied': [],
            'new_metrics': None
        }
        
        # Apply optimizations
        self._apply_performance_optimizations(tool_name, results)
        self._apply_memory_optimizations(tool_name, results)
        self._apply_concurrency_optimizations(tool_name, results)
        
        # Measure new metrics
        results['new_metrics'] = self._create_performance_profile(
            tool_name,
            importlib.import_module(self.tools[tool_name].name)
        )
        
        return results
        
    def _apply_performance_optimizations(self, tool_name: str, results: Dict[str, Any]):
        """Apply performance optimizations.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store optimization results
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Apply caching
        if not hasattr(module, '_cached'):
            self._add_caching(module)
            results['optimizations_applied'].append('Added result caching')
            
        # Apply async/await
        if self._can_be_async(module):
            self._make_async(module)
            results['optimizations_applied'].append('Converted to async/await')
            
        # Apply batch processing
        if self._can_batch(module):
            self._add_batching(module)
            results['optimizations_applied'].append('Added batch processing')
            
    def _apply_memory_optimizations(self, tool_name: str, results: Dict[str, Any]):
        """Apply memory optimizations.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store optimization results
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Apply memory pooling
        if self._can_pool_memory(module):
            self._add_memory_pooling(module)
            results['optimizations_applied'].append('Added memory pooling')
            
        # Apply lazy loading
        if self._can_lazy_load(module):
            self._add_lazy_loading(module)
            results['optimizations_applied'].append('Added lazy loading')
            
        # Apply cleanup
        if self._needs_cleanup(module):
            self._add_cleanup(module)
            results['optimizations_applied'].append('Added resource cleanup')
            
    def _apply_concurrency_optimizations(self, tool_name: str, results: Dict[str, Any]):
        """Apply concurrency optimizations.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store optimization results
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Apply thread pooling
        if self._can_use_threads(module):
            self._add_thread_pooling(module)
            results['optimizations_applied'].append('Added thread pooling')
            
        # Apply process pooling
        if self._can_use_processes(module):
            self._add_process_pooling(module)
            results['optimizations_applied'].append('Added process pooling')
            
        # Apply async pooling
        if self._can_use_async_pool(module):
            self._add_async_pooling(module)
            results['optimizations_applied'].append('Added async pooling')
            
    def secure_tool(self, tool_name: str) -> Dict[str, Any]:
        """Apply security measures to a tool.
        
        Args:
            tool_name: Name of the tool to secure
            
        Returns:
            Dictionary containing security measures applied
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        results = {
            'original_profile': self.security_profiles[tool_name],
            'security_measures_applied': [],
            'new_profile': None
        }
        
        # Apply security measures
        self._apply_input_validation(tool_name, results)
        self._apply_output_sanitization(tool_name, results)
        self._apply_access_control(tool_name, results)
        self._apply_audit_logging(tool_name, results)
        
        # Create new security profile
        results['new_profile'] = self._create_security_profile(
            tool_name,
            importlib.import_module(self.tools[tool_name].name)
        )
        
        return results
        
    def _apply_input_validation(self, tool_name: str, results: Dict[str, Any]):
        """Apply input validation.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store security measures
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Add input validation decorator
        if not hasattr(module, '_validated'):
            self._add_input_validation(module)
            results['security_measures_applied'].append('Added input validation')
            
        # Add type checking
        if not hasattr(module, '_type_checked'):
            self._add_type_checking(module)
            results['security_measures_applied'].append('Added type checking')
            
        # Add length limits
        if not hasattr(module, '_length_limited'):
            self._add_length_limits(module)
            results['security_measures_applied'].append('Added length limits')
            
    def _apply_output_sanitization(self, tool_name: str, results: Dict[str, Any]):
        """Apply output sanitization.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store security measures
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Add output sanitization
        if not hasattr(module, '_sanitized'):
            self._add_output_sanitization(module)
            results['security_measures_applied'].append('Added output sanitization')
            
        # Add encoding
        if not hasattr(module, '_encoded'):
            self._add_encoding(module)
            results['security_measures_applied'].append('Added output encoding')
            
        # Add escaping
        if not hasattr(module, '_escaped'):
            self._add_escaping(module)
            results['security_measures_applied'].append('Added output escaping')
            
    def _apply_access_control(self, tool_name: str, results: Dict[str, Any]):
        """Apply access control.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store security measures
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Add permission checking
        if not hasattr(module, '_permission_checked'):
            self._add_permission_checking(module)
            results['security_measures_applied'].append('Added permission checking')
            
        # Add role-based access
        if not hasattr(module, '_role_based'):
            self._add_role_based_access(module)
            results['security_measures_applied'].append('Added role-based access')
            
        # Add rate limiting
        if not hasattr(module, '_rate_limited'):
            self._add_rate_limiting(module)
            results['security_measures_applied'].append('Added rate limiting')
            
    def _apply_audit_logging(self, tool_name: str, results: Dict[str, Any]):
        """Apply audit logging.
        
        Args:
            tool_name: Name of the tool
            results: Dictionary to store security measures
        """
        module = importlib.import_module(self.tools[tool_name].name)
        
        # Add audit logging
        if not hasattr(module, '_audited'):
            self._add_audit_logging(module)
            results['security_measures_applied'].append('Added audit logging')
            
        # Add event tracking
        if not hasattr(module, '_tracked'):
            self._add_event_tracking(module)
            results['security_measures_applied'].append('Added event tracking')
            
        # Add error logging
        if not hasattr(module, '_error_logged'):
            self._add_error_logging(module)
            results['security_measures_applied'].append('Added error logging')
            
    def get_tool_dependencies(self, tool_name: str) -> Dict[str, Any]:
        """Get tool dependencies and their status.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing dependency information
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        dependencies = self.dependency_graph.get(tool_name, set())
        status = {}
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                status[dep] = {
                    'installed': True,
                    'version': pkg_resources.get_distribution(dep).version,
                    'compatible': True
                }
            except ImportError:
                status[dep] = {
                    'installed': False,
                    'version': None,
                    'compatible': False
                }
            except pkg_resources.DistributionNotFound:
                status[dep] = {
                    'installed': True,
                    'version': 'unknown',
                    'compatible': True
                }
                
        return {
            'dependencies': list(dependencies),
            'status': status,
            'missing': [dep for dep, info in status.items() if not info['installed']],
            'incompatible': [dep for dep, info in status.items() if not info['compatible']]
        }
        
    def install_dependencies(self, tool_name: str) -> Dict[str, Any]:
        """Install missing dependencies for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing installation results
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        results = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        deps = self.get_tool_dependencies(tool_name)
        for dep, info in deps['status'].items():
            if not info['installed']:
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                    results['successful'].append(dep)
                except subprocess.CalledProcessError:
                    results['failed'].append(dep)
            else:
                results['skipped'].append(dep)
                
        return results
        
    def update_dependencies(self, tool_name: str) -> Dict[str, Any]:
        """Update dependencies for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing update results
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        results = {
            'updated': [],
            'failed': [],
            'skipped': []
        }
        
        deps = self.get_tool_dependencies(tool_name)
        for dep, info in deps['status'].items():
            if info['installed']:
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', dep])
                    results['updated'].append(dep)
                except subprocess.CalledProcessError:
                    results['failed'].append(dep)
            else:
                results['skipped'].append(dep)
                
        return results
        
    def check_dependency_conflicts(self, tool_name: str) -> Dict[str, Any]:
        """Check for dependency conflicts.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing conflict information
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        results = {
            'conflicts': [],
            'warnings': [],
            'suggestions': []
        }
        
        deps = self.get_tool_dependencies(tool_name)
        for dep, info in deps['status'].items():
            if info['installed']:
                try:
                    # Check version conflicts
                    dist = pkg_resources.get_distribution(dep)
                    for other_dep in deps['status']:
                        if other_dep != dep and deps['status'][other_dep]['installed']:
                            other_dist = pkg_resources.get_distribution(other_dep)
                            if dist.version != other_dist.version:
                                results['conflicts'].append({
                                    'dependency': dep,
                                    'version': dist.version,
                                    'conflicts_with': other_dep,
                                    'other_version': other_dist.version
                                })
                                
                    # Check compatibility
                    if not self._check_compatibility(dep, dist.version):
                        results['warnings'].append({
                            'dependency': dep,
                            'version': dist.version,
                            'message': 'Version may not be compatible'
                        })
                        
                except pkg_resources.DistributionNotFound:
                    results['warnings'].append({
                        'dependency': dep,
                        'message': 'Distribution not found'
                    })
                    
        return results
        
    def _check_compatibility(self, dep: str, version: str) -> bool:
        """Check dependency compatibility.
        
        Args:
            dep: Dependency name
            version: Version to check
            
        Returns:
            True if compatible
        """
        try:
            # Check against known compatible versions
            compatible_versions = {
                'requests': ['2.25.0', '2.26.0', '2.27.0'],
                'numpy': ['1.21.0', '1.22.0', '1.23.0'],
                'pandas': ['1.3.0', '1.4.0', '1.5.0']
            }
            
            if dep in compatible_versions:
                return version in compatible_versions[dep]
                
            return True  # Assume compatible if not in known list
            
        except Exception:
            return False
            
    def get_tool_metrics(self, tool_name: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing tool metrics
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        return {
            'performance': self.performance_profiles[tool_name],
            'security': self.security_profiles[tool_name],
            'dependencies': self.get_tool_dependencies(tool_name),
            'usage': {
                'last_used': self.tools[tool_name].last_used,
                'usage_count': self.tools[tool_name].usage_count
            }
        }
        
    def export_tool_report(self, tool_name: str, format: str = 'json') -> str:
        """Export comprehensive report for a tool.
        
        Args:
            tool_name: Name of the tool
            format: Export format ('json' or 'markdown')
            
        Returns:
            Report in specified format
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        data = self.get_tool_metrics(tool_name)
        
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'markdown':
            return self._generate_markdown_report(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate markdown report.
        
        Args:
            data: Tool metrics data
            
        Returns:
            Markdown formatted report
        """
        report = []
        
        # Performance section
        report.append("## Performance Metrics")
        perf = data['performance']
        report.append(f"- Average Execution Time: {perf.avg_execution_time:.2f}s")
        report.append(f"- Memory Usage: {perf.memory_usage:.2f}MB")
        report.append(f"- CPU Usage: {perf.cpu_usage:.2f}%")
        report.append(f"- I/O Operations: {perf.io_operations}")
        report.append(f"- Cache Hit Rate: {perf.cache_hit_rate:.2f}%")
        report.append(f"- Concurrent Usage: {perf.concurrent_usage}")
        
        # Security section
        report.append("\n## Security Profile")
        sec = data['security']
        report.append(f"- Security Level: {sec.security_level}")
        report.append(f"- Network Access: {'Yes' if sec.network_access else 'No'}")
        report.append(f"- File System Access: {'Yes' if sec.file_system_access else 'No'}")
        report.append(f"- System Access: {'Yes' if sec.system_access else 'No'}")
        report.append("\nSecurity Risks:")
        for risk in sec.security_risks:
            report.append(f"- {risk}")
        report.append("\nMitigation Strategies:")
        for strategy in sec.mitigation_strategies:
            report.append(f"- {strategy}")
            
        # Dependencies section
        report.append("\n## Dependencies")
        deps = data['dependencies']
        report.append("\nInstalled Dependencies:")
        for dep, info in deps['status'].items():
            if info['installed']:
                report.append(f"- {dep} (v{info['version']})")
        report.append("\nMissing Dependencies:")
        for dep in deps['missing']:
            report.append(f"- {dep}")
            
        # Usage section
        report.append("\n## Usage Statistics")
        usage = data['usage']
        report.append(f"- Last Used: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usage['last_used']))}")
        report.append(f"- Usage Count: {usage['usage_count']}")
        
        return "\n".join(report) 