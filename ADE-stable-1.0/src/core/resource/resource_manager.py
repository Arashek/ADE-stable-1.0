from typing import Dict, Any, Optional, List, Tuple
import logging
import psutil
import resource
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from src.core.monitoring.metrics import MetricsCollector
from src.core.monitoring.analytics import AnalyticsEngine
from src.core.resource.visualization import ResourceVisualizer

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types of resources that can be monitored"""
    MEMORY = "memory"
    CPU = "cpu"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    OPEN_FILES = "open_files"
    THREADS = "threads"
    GPU = "gpu"
    SWAP = "swap"
    IOPS = "iops"

class ResourceViolationType(Enum):
    """Types of resource violations"""
    MEMORY_EXCEEDED = "memory_exceeded"
    CPU_EXCEEDED = "cpu_exceeded"
    DISK_IO_EXCEEDED = "disk_io_exceeded"
    NETWORK_IO_EXCEEDED = "network_io_exceeded"
    OPEN_FILES_EXCEEDED = "open_files_exceeded"
    THREADS_EXCEEDED = "threads_exceeded"
    GPU_EXCEEDED = "gpu_exceeded"
    SWAP_EXCEEDED = "swap_exceeded"
    IOPS_EXCEEDED = "iops_exceeded"
    SOFT_LIMIT = "soft_limit"
    HARD_LIMIT = "hard_limit"

@dataclass
class ResourceQuota:
    """Resource quota configuration"""
    memory_limit: int  # MB
    cpu_percent: float
    disk_io: int  # MB/s
    network_io: int  # MB/s
    open_files: int
    max_threads: int
    timeout: float  # seconds
    swap_limit: int = 1024  # MB
    iops_limit: int = 1000  # IOPS
    gpu_memory_limit: Optional[int] = None  # MB
    soft_limit_percent: float = 80.0  # Percentage of hard limit to trigger warnings

@dataclass
class ResourceUsage:
    """Current resource usage"""
    memory_used: float  # MB
    cpu_percent: float
    disk_read: float  # MB/s
    disk_write: float  # MB/s
    network_sent: float  # MB/s
    network_recv: float  # MB/s
    open_files: int
    thread_count: int
    swap_used: float  # MB
    iops: int
    gpu_memory_used: Optional[float] = None  # MB
    timestamp: datetime = None

@dataclass
class ResourceViolation:
    """Resource violation information"""
    type: ResourceViolationType
    resource_type: ResourceType
    current_value: float
    limit: float
    timestamp: datetime
    severity: str  # "warning" or "error"
    details: Dict[str, Any]

class ResourceManager:
    """Manages resource quotas and monitoring for script execution"""
    
    def __init__(
        self,
        quota: Optional[ResourceQuota] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        analytics_engine: Optional[AnalyticsEngine] = None,
        logger: Optional[logging.Logger] = None,
        enable_realtime_visualization: bool = False
    ):
        self.quota = quota or ResourceQuota(
            memory_limit=512,  # 512MB
            cpu_percent=80.0,
            disk_io=100,  # 100MB/s
            network_io=100,  # 100MB/s
            open_files=100,
            max_threads=4,
            timeout=30.0
        )
        
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.analytics_engine = analytics_engine or AnalyticsEngine()
        self.logger = logger or logging.getLogger("resource_manager")
        self.visualizer = ResourceVisualizer()
        
        # Resource monitoring
        self.process: Optional[psutil.Process] = None
        self.monitor_task: Optional[asyncio.Task] = None
        self.usage_history: List[ResourceUsage] = []
        self.violation_history: List[ResourceViolation] = []
        self._last_disk_io = None
        self._last_network_io = None
        self._last_io_time = None
        self._last_iops_count = 0
        self._last_iops_time = None
        
        # Resource trends
        self._trend_window = timedelta(minutes=5)
        self._trend_data: Dict[ResourceType, List[Tuple[datetime, float]]] = {
            rt: [] for rt in ResourceType
        }
        
        # Real-time visualization
        self.realtime_visualizer = None
        if enable_realtime_visualization:
            from src.core.resource.realtime_visualization import RealTimeResourceVisualizer
            self.realtime_visualizer = RealTimeResourceVisualizer(self)
    
    async def start_monitoring(self, pid: int):
        """Start monitoring resources for a process"""
        try:
            self.process = psutil.Process(pid)
            
            # Set resource limits
            self._set_resource_limits()
            
            # Start monitoring task
            self.monitor_task = asyncio.create_task(self._monitor_resources())
            
            # Start real-time visualization if enabled
            if self.realtime_visualizer:
                self.realtime_visualizer.start()
            
            self.logger.info(f"Started resource monitoring for process {pid}")
            
        except Exception as e:
            self.logger.error(f"Failed to start resource monitoring: {str(e)}")
            raise
    
    async def stop_monitoring(self):
        """Stop resource monitoring"""
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop real-time visualization if enabled
        if self.realtime_visualizer:
            self.realtime_visualizer.stop()
        
        self.process = None
        self._last_disk_io = None
        self._last_network_io = None
        self._last_io_time = None
        self._last_iops_count = 0
        self._last_iops_time = None
    
    def _set_resource_limits(self):
        """Set system resource limits"""
        try:
            # Set memory limit
            memory_bytes = self.quota.memory_limit * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # Set file descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (self.quota.open_files, self.quota.open_files))
            
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (int(self.quota.timeout), int(self.quota.timeout)))
            
            # Set swap limit if supported
            try:
                swap_bytes = self.quota.swap_limit * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_SWAP, (swap_bytes, swap_bytes))
            except (ValueError, AttributeError):
                self.logger.warning("Swap limit not supported on this system")
            
        except Exception as e:
            self.logger.warning(f"Failed to set resource limits: {str(e)}")
    
    async def _monitor_resources(self):
        """Monitor resource usage in background"""
        while True:
            try:
                if not self.process:
                    break
                
                # Get current resource usage
                usage = self._get_resource_usage()
                
                # Check resource limits and record violations
                violations = self._check_resource_limits(usage)
                for violation in violations:
                    self._record_violation(violation)
                
                # Update resource trends
                self._update_trends(usage)
                
                # Record usage
                self.usage_history.append(usage)
                
                # Clean up old history
                self._cleanup_history()
                
                # Record metrics
                self._record_metrics(usage)
                
                # Analyze resource patterns
                self._analyze_resource_patterns()
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(0.1)
    
    def _get_resource_usage(self) -> ResourceUsage:
        """Get current resource usage"""
        if not self.process:
            raise RuntimeError("No process being monitored")
        
        # Get memory usage
        memory_info = self.process.memory_info()
        memory_used = memory_info.rss / (1024 * 1024)  # Convert to MB
        
        # Get CPU usage
        cpu_percent = self.process.cpu_percent()
        
        # Get disk I/O
        current_time = datetime.now()
        disk_io = self.process.io_counters()
        
        if self._last_disk_io and self._last_io_time:
            time_diff = (current_time - self._last_io_time).total_seconds()
            disk_read = (disk_io.read_bytes - self._last_disk_io.read_bytes) / (1024 * 1024 * time_diff)
            disk_write = (disk_io.write_bytes - self._last_disk_io.write_bytes) / (1024 * 1024 * time_diff)
        else:
            disk_read = 0.0
            disk_write = 0.0
        
        self._last_disk_io = disk_io
        self._last_io_time = current_time
        
        # Get network I/O
        net_io = self.process.io_counters()
        
        if self._last_network_io and self._last_io_time:
            time_diff = (current_time - self._last_io_time).total_seconds()
            network_sent = (net_io.write_bytes - self._last_network_io.write_bytes) / (1024 * 1024 * time_diff)
            network_recv = (net_io.read_bytes - self._last_network_io.read_bytes) / (1024 * 1024 * time_diff)
        else:
            network_sent = 0.0
            network_recv = 0.0
        
        self._last_network_io = net_io
        
        # Get open files and threads
        open_files = len(self.process.open_files())
        thread_count = self.process.num_threads()
        
        # Get swap usage
        swap_used = self.process.memory_info().vms / (1024 * 1024) - memory_used
        
        # Calculate IOPS
        if self._last_io_time:
            time_diff = (current_time - self._last_io_time).total_seconds()
            iops = int((disk_io.read_count + disk_io.write_count - self._last_iops_count) / time_diff)
        else:
            iops = 0
        
        self._last_iops_count = disk_io.read_count + disk_io.write_count
        self._last_iops_time = current_time
        
        # Get GPU memory usage if available
        gpu_memory_used = None
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_used = info.used / (1024 * 1024)  # Convert to MB
        except Exception:
            pass
        
        return ResourceUsage(
            memory_used=memory_used,
            cpu_percent=cpu_percent,
            disk_read=disk_read,
            disk_write=disk_write,
            network_sent=network_sent,
            network_recv=network_recv,
            open_files=open_files,
            thread_count=thread_count,
            swap_used=swap_used,
            iops=iops,
            gpu_memory_used=gpu_memory_used,
            timestamp=current_time
        )
    
    def _check_resource_limits(self, usage: ResourceUsage) -> List[ResourceViolation]:
        """Check if resource usage exceeds limits"""
        violations = []
        
        # Check memory
        if usage.memory_used > self.quota.memory_limit:
            violations.append(ResourceViolation(
                type=ResourceViolationType.MEMORY_EXCEEDED,
                resource_type=ResourceType.MEMORY,
                current_value=usage.memory_used,
                limit=self.quota.memory_limit,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        elif usage.memory_used > self.quota.memory_limit * (self.quota.soft_limit_percent / 100):
            violations.append(ResourceViolation(
                type=ResourceViolationType.MEMORY_EXCEEDED,
                resource_type=ResourceType.MEMORY,
                current_value=usage.memory_used,
                limit=self.quota.memory_limit,
                timestamp=usage.timestamp,
                severity="warning",
                details={"process_id": self.process.pid}
            ))
        
        # Check CPU
        if usage.cpu_percent > self.quota.cpu_percent:
            violations.append(ResourceViolation(
                type=ResourceViolationType.CPU_EXCEEDED,
                resource_type=ResourceType.CPU,
                current_value=usage.cpu_percent,
                limit=self.quota.cpu_percent,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        
        # Check disk I/O
        total_disk_io = usage.disk_read + usage.disk_write
        if total_disk_io > self.quota.disk_io:
            violations.append(ResourceViolation(
                type=ResourceViolationType.DISK_IO_EXCEEDED,
                resource_type=ResourceType.DISK_IO,
                current_value=total_disk_io,
                limit=self.quota.disk_io,
                timestamp=usage.timestamp,
                severity="error",
                details={"read": usage.disk_read, "write": usage.disk_write}
            ))
        
        # Check network I/O
        total_network_io = usage.network_sent + usage.network_recv
        if total_network_io > self.quota.network_io:
            violations.append(ResourceViolation(
                type=ResourceViolationType.NETWORK_IO_EXCEEDED,
                resource_type=ResourceType.NETWORK_IO,
                current_value=total_network_io,
                limit=self.quota.network_io,
                timestamp=usage.timestamp,
                severity="error",
                details={"sent": usage.network_sent, "recv": usage.network_recv}
            ))
        
        # Check open files
        if usage.open_files > self.quota.open_files:
            violations.append(ResourceViolation(
                type=ResourceViolationType.OPEN_FILES_EXCEEDED,
                resource_type=ResourceType.OPEN_FILES,
                current_value=usage.open_files,
                limit=self.quota.open_files,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        
        # Check thread count
        if usage.thread_count > self.quota.max_threads:
            violations.append(ResourceViolation(
                type=ResourceViolationType.THREADS_EXCEEDED,
                resource_type=ResourceType.THREADS,
                current_value=usage.thread_count,
                limit=self.quota.max_threads,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        
        # Check swap usage
        if usage.swap_used > self.quota.swap_limit:
            violations.append(ResourceViolation(
                type=ResourceViolationType.SWAP_EXCEEDED,
                resource_type=ResourceType.SWAP,
                current_value=usage.swap_used,
                limit=self.quota.swap_limit,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        
        # Check IOPS
        if usage.iops > self.quota.iops_limit:
            violations.append(ResourceViolation(
                type=ResourceViolationType.IOPS_EXCEEDED,
                resource_type=ResourceType.IOPS,
                current_value=usage.iops,
                limit=self.quota.iops_limit,
                timestamp=usage.timestamp,
                severity="error",
                details={"process_id": self.process.pid}
            ))
        
        # Check GPU memory if available
        if usage.gpu_memory_used is not None and self.quota.gpu_memory_limit is not None:
            if usage.gpu_memory_used > self.quota.gpu_memory_limit:
                violations.append(ResourceViolation(
                    type=ResourceViolationType.GPU_EXCEEDED,
                    resource_type=ResourceType.GPU,
                    current_value=usage.gpu_memory_used,
                    limit=self.quota.gpu_memory_limit,
                    timestamp=usage.timestamp,
                    severity="error",
                    details={"process_id": self.process.pid}
                ))
        
        return violations
    
    def _record_violation(self, violation: ResourceViolation):
        """Record a resource violation"""
        self.violation_history.append(violation)
        
        # Log violation
        if violation.severity == "error":
            self.logger.error(
                f"Resource violation: {violation.type.value} - "
                f"Current: {violation.current_value:.1f}, Limit: {violation.limit:.1f}"
            )
        else:
            self.logger.warning(
                f"Resource warning: {violation.type.value} - "
                f"Current: {violation.current_value:.1f}, Limit: {violation.limit:.1f}"
            )
        
        # Record in analytics
        self.analytics_engine.add_resource_violation(
            violation.type.value,
            violation.resource_type.value,
            violation.current_value,
            violation.limit,
            violation.severity,
            violation.details
        )
    
    def _update_trends(self, usage: ResourceUsage):
        """Update resource usage trends"""
        current_time = usage.timestamp
        
        # Update trends for each resource type
        self._trend_data[ResourceType.MEMORY].append((current_time, usage.memory_used))
        self._trend_data[ResourceType.CPU].append((current_time, usage.cpu_percent))
        self._trend_data[ResourceType.DISK_IO].append((current_time, usage.disk_read + usage.disk_write))
        self._trend_data[ResourceType.NETWORK_IO].append((current_time, usage.network_sent + usage.network_recv))
        self._trend_data[ResourceType.OPEN_FILES].append((current_time, usage.open_files))
        self._trend_data[ResourceType.THREADS].append((current_time, usage.thread_count))
        self._trend_data[ResourceType.SWAP].append((current_time, usage.swap_used))
        self._trend_data[ResourceType.IOPS].append((current_time, usage.iops))
        if usage.gpu_memory_used is not None:
            self._trend_data[ResourceType.GPU].append((current_time, usage.gpu_memory_used))
        
        # Clean up old trend data
        cutoff_time = current_time - self._trend_window
        for resource_type in self._trend_data:
            self._trend_data[resource_type] = [
                (t, v) for t, v in self._trend_data[resource_type]
                if t > cutoff_time
            ]
    
    def _analyze_resource_patterns(self):
        """Analyze resource usage patterns"""
        current_time = datetime.now()
        
        for resource_type, trend_data in self._trend_data.items():
            if not trend_data:
                continue
            
            # Calculate basic statistics
            values = [v for _, v in trend_data]
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            
            # Detect spikes
            threshold = avg_value * 2
            spikes = [(t, v) for t, v in trend_data if v > threshold]
            
            if spikes:
                self.analytics_engine.add_resource_pattern(
                    resource_type.value,
                    "spike",
                    {
                        "average": avg_value,
                        "max": max_value,
                        "min": min_value,
                        "spikes": len(spikes),
                        "last_spike": spikes[-1][1]
                    }
                )
            
            # Detect sustained high usage
            sustained_threshold = avg_value * 1.5
            sustained_periods = []
            current_period = None
            
            for t, v in trend_data:
                if v > sustained_threshold:
                    if current_period is None:
                        current_period = {"start": t, "max": v}
                    else:
                        current_period["max"] = max(current_period["max"], v)
                elif current_period is not None:
                    current_period["end"] = t
                    sustained_periods.append(current_period)
                    current_period = None
            
            if current_period is not None:
                current_period["end"] = current_time
                sustained_periods.append(current_period)
            
            if sustained_periods:
                self.analytics_engine.add_resource_pattern(
                    resource_type.value,
                    "sustained_high_usage",
                    {
                        "average": avg_value,
                        "max": max_value,
                        "min": min_value,
                        "sustained_periods": len(sustained_periods),
                        "longest_period": max(
                            (p["end"] - p["start"]).total_seconds()
                            for p in sustained_periods
                        )
                    }
                )
    
    def _cleanup_history(self):
        """Clean up old usage history"""
        current_time = datetime.now()
        
        # Clean up usage history
        self.usage_history = [
            usage for usage in self.usage_history
            if (current_time - usage.timestamp).total_seconds() < 3600  # Keep last hour
        ]
        
        # Clean up violation history
        self.violation_history = [
            violation for violation in self.violation_history
            if (current_time - violation.timestamp).total_seconds() < 3600  # Keep last hour
        ]
    
    def _record_metrics(self, usage: ResourceUsage):
        """Record resource usage metrics"""
        # Record basic metrics
        self.metrics_collector.record_metric("memory_usage", usage.memory_used)
        self.metrics_collector.record_metric("cpu_usage", usage.cpu_percent)
        self.metrics_collector.record_metric("disk_read", usage.disk_read)
        self.metrics_collector.record_metric("disk_write", usage.disk_write)
        self.metrics_collector.record_metric("network_sent", usage.network_sent)
        self.metrics_collector.record_metric("network_recv", usage.network_recv)
        self.metrics_collector.record_metric("open_files", usage.open_files)
        self.metrics_collector.record_metric("thread_count", usage.thread_count)
        self.metrics_collector.record_metric("swap_usage", usage.swap_used)
        self.metrics_collector.record_metric("iops", usage.iops)
        
        if usage.gpu_memory_used is not None:
            self.metrics_collector.record_metric("gpu_memory_usage", usage.gpu_memory_used)
        
        # Record derived metrics
        self.metrics_collector.record_metric("total_disk_io", usage.disk_read + usage.disk_write)
        self.metrics_collector.record_metric("total_network_io", usage.network_sent + usage.network_recv)
        self.metrics_collector.record_metric("memory_utilization", usage.memory_used / self.quota.memory_limit)
        self.metrics_collector.record_metric("cpu_utilization", usage.cpu_percent / self.quota.cpu_percent)
    
    def get_usage_history(self) -> List[Dict[str, Any]]:
        """Get resource usage history"""
        return [
            {
                "timestamp": usage.timestamp.isoformat(),
                "memory_used": usage.memory_used,
                "cpu_percent": usage.cpu_percent,
                "disk_read": usage.disk_read,
                "disk_write": usage.disk_write,
                "network_sent": usage.network_sent,
                "network_recv": usage.network_recv,
                "open_files": usage.open_files,
                "thread_count": usage.thread_count,
                "swap_used": usage.swap_used,
                "iops": usage.iops,
                "gpu_memory_used": usage.gpu_memory_used
            }
            for usage in self.usage_history
        ]
    
    def get_violation_history(self) -> List[Dict[str, Any]]:
        """Get resource violation history"""
        return [
            {
                "timestamp": violation.timestamp.isoformat(),
                "type": violation.type.value,
                "resource_type": violation.resource_type.value,
                "current_value": violation.current_value,
                "limit": violation.limit,
                "severity": violation.severity,
                "details": violation.details
            }
            for violation in self.violation_history
        ]
    
    def get_resource_trends(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get resource usage trends"""
        return {
            resource_type.value: [
                {
                    "timestamp": t.isoformat(),
                    "value": v
                }
                for t, v in trend_data
            ]
            for resource_type, trend_data in self._trend_data.items()
        }
    
    def get_current_usage(self) -> Optional[Dict[str, Any]]:
        """Get current resource usage"""
        if not self.process:
            return None
            
        try:
            usage = self._get_resource_usage()
            return {
                "timestamp": usage.timestamp.isoformat(),
                "memory_used": usage.memory_used,
                "cpu_percent": usage.cpu_percent,
                "disk_read": usage.disk_read,
                "disk_write": usage.disk_write,
                "network_sent": usage.network_sent,
                "network_recv": usage.network_recv,
                "open_files": usage.open_files,
                "thread_count": usage.thread_count,
                "swap_used": usage.swap_used,
                "iops": usage.iops,
                "gpu_memory_used": usage.gpu_memory_used,
                "utilization": {
                    "memory": usage.memory_used / self.quota.memory_limit,
                    "cpu": usage.cpu_percent / self.quota.cpu_percent,
                    "disk_io": (usage.disk_read + usage.disk_write) / self.quota.disk_io,
                    "network_io": (usage.network_sent + usage.network_recv) / self.quota.network_io,
                    "open_files": usage.open_files / self.quota.open_files,
                    "threads": usage.thread_count / self.quota.max_threads,
                    "swap": usage.swap_used / self.quota.swap_limit,
                    "iops": usage.iops / self.quota.iops_limit
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get current usage: {str(e)}")
            return None
    
    def create_usage_timeline(self, resource_types: Optional[List[ResourceType]] = None) -> go.Figure:
        """Create an interactive timeline of resource usage"""
        return self.visualizer.create_usage_timeline(self.usage_history, resource_types)
    
    def create_resource_distribution(self) -> go.Figure:
        """Create a distribution plot of resource usage"""
        return self.visualizer.create_resource_distribution(self.usage_history)
    
    def create_heatmap(self) -> go.Figure:
        """Create a heatmap of resource usage patterns"""
        return self.visualizer.create_heatmap(self.usage_history)
    
    def create_violation_timeline(self) -> go.Figure:
        """Create a timeline of resource violations"""
        return self.visualizer.create_violation_timeline(self.get_violation_history())
    
    def create_utilization_gauge(self) -> go.Figure:
        """Create a gauge chart showing current resource utilization"""
        current_usage = self.get_current_usage()
        if current_usage is None:
            raise RuntimeError("No current usage data available")
        return self.visualizer.create_utilization_gauge(current_usage)
    
    def save_visualization(self, fig: go.Figure, filename: str):
        """Save a visualization to a file"""
        self.visualizer.save_visualization(fig, filename)
    
    def show_visualization(self, fig: go.Figure):
        """Display a visualization in the browser"""
        self.visualizer.show_visualization(fig) 