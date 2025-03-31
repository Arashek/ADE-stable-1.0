from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import psutil
import time
from datetime import datetime
import ast
import re
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PerformanceType(Enum):
    """Types of performance analysis"""
    CPU = "cpu"
    MEMORY = "memory"
    I_O = "io"
    NETWORK = "network"
    CONCURRENCY = "concurrency"
    CACHING = "caching"
    ALGORITHM = "algorithm"
    DATABASE = "database"

class PerformanceMetric(BaseModel):
    """Performance metric"""
    name: str
    value: float
    threshold: float
    status: str
    details: Dict[str, Any] = {}
    recommendations: List[str] = []

class PerformanceResult(BaseModel):
    """Result of performance analysis"""
    performance_type: PerformanceType
    metrics: Dict[str, PerformanceMetric]
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

@dataclass
class PerformanceIssue:
    """Information about a performance issue"""
    type: str
    severity: str
    description: str
    line_number: int
    column: int
    code_snippet: str
    recommendation: str
    impact: str
    metadata: Dict[str, Any] = None

class PerformanceAnalysisResult(BaseModel):
    """Result of performance analysis"""
    issues: List[PerformanceIssue]
    performance_score: float
    metrics: Dict[str, float]
    recommendations: List[str]
    metadata: Dict[str, Any] = {}

class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    thread_count: int
    response_time: float
    throughput: float
    error_rate: float
    timestamp: datetime

class PerformanceThreshold(BaseModel):
    """Performance threshold configuration"""
    metric: str
    warning_threshold: float
    critical_threshold: float
    duration: int  # seconds
    action: str

class PerformanceAnalyzer:
    """Analyzer for monitoring and optimizing system performance"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.thresholds: List[PerformanceThreshold] = []
        self.alerts: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        self.analysis_history: List[PerformanceResult] = []
        self._initialize_patterns()
        self._initialize_performance_rules()
        
    def _initialize_patterns(self):
        """Initialize performance detection patterns"""
        # CPU-intensive patterns
        self.performance_patterns["cpu"] = [
            {
                "pattern": r"for\s+.*?in\s+range\(.*?\):",
                "severity": "warning",
                "description": "Potential CPU-intensive loop detected",
                "recommendation": "Consider using list comprehension or vectorized operations"
            },
            {
                "pattern": r"while\s+True:",
                "severity": "warning",
                "description": "Infinite loop pattern detected",
                "recommendation": "Add proper termination conditions"
            }
        ]
        
        # Memory-intensive patterns
        self.performance_patterns["memory"] = [
            {
                "pattern": r"list\(.*?\)\s*\*",
                "severity": "warning",
                "description": "Large list multiplication detected",
                "recommendation": "Use numpy arrays or generators for large data"
            },
            {
                "pattern": r"\.append\(.*?\)\s*in\s+loop",
                "severity": "warning",
                "description": "List append in loop detected",
                "recommendation": "Use list comprehension or pre-allocate list"
            }
        ]
        
        # I/O patterns
        self.performance_patterns["io"] = [
            {
                "pattern": r"open\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "File open in loop detected",
                "recommendation": "Open files outside loops and use context managers"
            },
            {
                "pattern": r"\.readlines\(\)",
                "severity": "warning",
                "description": "readlines() usage detected",
                "recommendation": "Use file iteration for large files"
            }
        ]
        
        # Network patterns
        self.performance_patterns["network"] = [
            {
                "pattern": r"requests\.get\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "HTTP request in loop detected",
                "recommendation": "Use async/await or connection pooling"
            },
            {
                "pattern": r"socket\.connect\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "Socket connection in loop detected",
                "recommendation": "Use connection pooling or async sockets"
            }
        ]
        
        # Concurrency patterns
        self.performance_patterns["concurrency"] = [
            {
                "pattern": r"threading\.Thread\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "Thread creation in loop detected",
                "recommendation": "Use thread pool or asyncio"
            },
            {
                "pattern": r"\.join\(\)\s+in\s+loop",
                "severity": "warning",
                "description": "Thread join in loop detected",
                "recommendation": "Collect threads and join after loop"
            }
        ]
        
        # Caching patterns
        self.performance_patterns["caching"] = [
            {
                "pattern": r"@lru_cache",
                "severity": "info",
                "description": "LRU cache decorator detected",
                "recommendation": "Consider cache size and memory usage"
            },
            {
                "pattern": r"cache\.get\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "Cache access in loop detected",
                "recommendation": "Batch cache operations"
            }
        ]
        
        # Algorithm patterns
        self.performance_patterns["algorithm"] = [
            {
                "pattern": r"for\s+.*?in\s+.*?:.*?for\s+.*?in\s+.*?:",
                "severity": "warning",
                "description": "Nested loops detected",
                "recommendation": "Consider using more efficient algorithms"
            },
            {
                "pattern": r"\.sort\(\)\s+in\s+loop",
                "severity": "warning",
                "description": "Sort operation in loop detected",
                "recommendation": "Sort outside loop or use heap"
            }
        ]
        
        # Database patterns
        self.performance_patterns["database"] = [
            {
                "pattern": r"SELECT\s+\*",
                "severity": "warning",
                "description": "SELECT * query detected",
                "recommendation": "Select specific columns"
            },
            {
                "pattern": r"\.execute\(.*?\)\s+in\s+loop",
                "severity": "warning",
                "description": "Database query in loop detected",
                "recommendation": "Use batch operations or prepared statements"
            }
        ]
        
    def _initialize_performance_rules(self):
        """Initialize performance rules"""
        self.performance_rules = {
            PerformanceType.CPU: [
                {
                    "name": "cpu_usage",
                    "threshold": 0.7,
                    "description": "CPU usage score"
                },
                {
                    "name": "loop_efficiency",
                    "threshold": 0.8,
                    "description": "Loop efficiency score"
                },
                {
                    "name": "algorithm_complexity",
                    "threshold": 0.8,
                    "description": "Algorithm complexity score"
                }
            ],
            PerformanceType.MEMORY: [
                {
                    "name": "memory_usage",
                    "threshold": 0.7,
                    "description": "Memory usage score"
                },
                {
                    "name": "memory_leaks",
                    "threshold": 0.9,
                    "description": "Memory leak detection score"
                },
                {
                    "name": "garbage_collection",
                    "threshold": 0.8,
                    "description": "Garbage collection efficiency score"
                }
            ],
            PerformanceType.I_O: [
                {
                    "name": "io_efficiency",
                    "threshold": 0.8,
                    "description": "I/O operation efficiency score"
                },
                {
                    "name": "file_handling",
                    "threshold": 0.8,
                    "description": "File handling efficiency score"
                },
                {
                    "name": "buffer_usage",
                    "threshold": 0.7,
                    "description": "Buffer usage efficiency score"
                }
            ],
            PerformanceType.NETWORK: [
                {
                    "name": "network_efficiency",
                    "threshold": 0.8,
                    "description": "Network operation efficiency score"
                },
                {
                    "name": "connection_pooling",
                    "threshold": 0.8,
                    "description": "Connection pooling efficiency score"
                },
                {
                    "name": "request_batching",
                    "threshold": 0.7,
                    "description": "Request batching efficiency score"
                }
            ],
            PerformanceType.CONCURRENCY: [
                {
                    "name": "thread_efficiency",
                    "threshold": 0.8,
                    "description": "Thread usage efficiency score"
                },
                {
                    "name": "async_efficiency",
                    "threshold": 0.8,
                    "description": "Async operation efficiency score"
                },
                {
                    "name": "resource_contention",
                    "threshold": 0.7,
                    "description": "Resource contention score"
                }
            ],
            PerformanceType.CACHING: [
                {
                    "name": "cache_efficiency",
                    "threshold": 0.8,
                    "description": "Cache usage efficiency score"
                },
                {
                    "name": "cache_hit_rate",
                    "threshold": 0.7,
                    "description": "Cache hit rate score"
                },
                {
                    "name": "cache_invalidation",
                    "threshold": 0.8,
                    "description": "Cache invalidation efficiency score"
                }
            ],
            PerformanceType.ALGORITHM: [
                {
                    "name": "time_complexity",
                    "threshold": 0.8,
                    "description": "Time complexity score"
                },
                {
                    "name": "space_complexity",
                    "threshold": 0.8,
                    "description": "Space complexity score"
                },
                {
                    "name": "algorithm_efficiency",
                    "threshold": 0.8,
                    "description": "Overall algorithm efficiency score"
                }
            ],
            PerformanceType.DATABASE: [
                {
                    "name": "query_efficiency",
                    "threshold": 0.8,
                    "description": "Database query efficiency score"
                },
                {
                    "name": "index_usage",
                    "threshold": 0.8,
                    "description": "Index usage efficiency score"
                },
                {
                    "name": "connection_efficiency",
                    "threshold": 0.7,
                    "description": "Database connection efficiency score"
                }
            ]
        }
        
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
            
            # Process metrics
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
            
            # Calculate response time and throughput
            response_time = self._calculate_response_time()
            throughput = self._calculate_throughput()
            
            # Calculate error rate
            error_rate = self._calculate_error_rate()
            
            metrics = PerformanceMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                disk_usage=disk_percent,
                network_io=network_io,
                process_count=process_count,
                thread_count=thread_count,
                response_time=response_time,
                throughput=throughput,
                error_rate=error_rate,
                timestamp=datetime.now()
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Check thresholds
            self._check_thresholds(metrics)
            
            return metrics
            
        except Exception as e:
            raise ValueError(f"Failed to collect performance metrics: {str(e)}")
            
    def add_threshold(self, threshold: PerformanceThreshold):
        """Add a performance threshold"""
        self.thresholds.append(threshold)
        
    def remove_threshold(self, metric: str):
        """Remove a performance threshold"""
        self.thresholds = [t for t in self.thresholds if t.metric != metric]
        
    def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[PerformanceMetrics]:
        """Get metrics history within a time range"""
        if not start_time and not end_time:
            return self.metrics_history
            
        filtered_metrics = self.metrics_history
        if start_time:
            filtered_metrics = [
                m for m in filtered_metrics
                if m.timestamp >= start_time
            ]
        if end_time:
            filtered_metrics = [
                m for m in filtered_metrics
                if m.timestamp <= end_time
            ]
            
        return filtered_metrics
        
    def get_performance_stats(
        self,
        window: int = 3600  # 1 hour in seconds
    ) -> Dict[str, float]:
        """Get performance statistics for a time window"""
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=window)
        
        metrics = self.get_metrics_history(start_time, end_time)
        if not metrics:
            return {}
            
        return {
            "avg_cpu_usage": sum(m.cpu_usage for m in metrics) / len(metrics),
            "avg_memory_usage": sum(m.memory_usage for m in metrics) / len(metrics),
            "avg_disk_usage": sum(m.disk_usage for m in metrics) / len(metrics),
            "avg_response_time": sum(m.response_time for m in metrics) / len(metrics),
            "avg_throughput": sum(m.throughput for m in metrics) / len(metrics),
            "avg_error_rate": sum(m.error_rate for m in metrics) / len(metrics),
            "max_cpu_usage": max(m.cpu_usage for m in metrics),
            "max_memory_usage": max(m.memory_usage for m in metrics),
            "max_disk_usage": max(m.disk_usage for m in metrics),
            "max_response_time": max(m.response_time for m in metrics),
            "max_throughput": max(m.throughput for m in metrics),
            "max_error_rate": max(m.error_rate for m in metrics)
        }
        
    def get_alerts(
        self,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get performance alerts"""
        filtered_alerts = self.alerts
        if severity:
            filtered_alerts = [
                a for a in filtered_alerts
                if a["severity"] == severity
            ]
        if start_time:
            filtered_alerts = [
                a for a in filtered_alerts
                if a["timestamp"] >= start_time
            ]
        if end_time:
            filtered_alerts = [
                a for a in filtered_alerts
                if a["timestamp"] <= end_time
            ]
            
        return filtered_alerts
        
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history"""
        return self.optimization_history
        
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and generate alerts"""
        for threshold in self.thresholds:
            metric_value = getattr(metrics, threshold.metric, None)
            if metric_value is None:
                continue
                
            if metric_value >= threshold.critical_threshold:
                self._generate_alert(
                    threshold.metric,
                    "CRITICAL",
                    metric_value,
                    threshold.critical_threshold
                )
                self._apply_optimization(threshold)
            elif metric_value >= threshold.warning_threshold:
                self._generate_alert(
                    threshold.metric,
                    "WARNING",
                    metric_value,
                    threshold.warning_threshold
                )
                
    def _generate_alert(
        self,
        metric: str,
        severity: str,
        value: float,
        threshold: float
    ):
        """Generate a performance alert"""
        alert = {
            "metric": metric,
            "severity": severity,
            "value": value,
            "threshold": threshold,
            "timestamp": datetime.now(),
            "action": self._get_action_for_severity(severity)
        }
        self.alerts.append(alert)
        
    def _get_action_for_severity(self, severity: str) -> str:
        """Get optimization action for severity level"""
        if severity == "CRITICAL":
            return "IMMEDIATE_OPTIMIZATION"
        elif severity == "WARNING":
            return "SCHEDULED_OPTIMIZATION"
        return "MONITOR"
        
    def _apply_optimization(self, threshold: PerformanceThreshold):
        """Apply performance optimization"""
        optimization = {
            "metric": threshold.metric,
            "action": threshold.action,
            "timestamp": datetime.now(),
            "threshold": threshold,
            "status": "PENDING"
        }
        
        try:
            if threshold.action == "IMMEDIATE_OPTIMIZATION":
                self._execute_optimization(threshold)
                optimization["status"] = "COMPLETED"
            elif threshold.action == "SCHEDULED_OPTIMIZATION":
                self._schedule_optimization(threshold)
                optimization["status"] = "SCHEDULED"
                
            self.optimization_history.append(optimization)
            
        except Exception as e:
            optimization["status"] = "FAILED"
            optimization["error"] = str(e)
            self.optimization_history.append(optimization)
            
    def _execute_optimization(self, threshold: PerformanceThreshold):
        """Execute performance optimization"""
        if threshold.metric == "cpu_usage":
            self._optimize_cpu_usage()
        elif threshold.metric == "memory_usage":
            self._optimize_memory_usage()
        elif threshold.metric == "disk_usage":
            self._optimize_disk_usage()
        elif threshold.metric == "response_time":
            self._optimize_response_time()
        elif threshold.metric == "error_rate":
            self._optimize_error_rate()
            
    def _schedule_optimization(self, threshold: PerformanceThreshold):
        """Schedule performance optimization"""
        # Implementation depends on the scheduling system
        pass
        
    def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        # Implementation depends on the system
        pass
        
    def _optimize_memory_usage(self):
        """Optimize memory usage"""
        # Implementation depends on the system
        pass
        
    def _optimize_disk_usage(self):
        """Optimize disk usage"""
        # Implementation depends on the system
        pass
        
    def _optimize_response_time(self):
        """Optimize response time"""
        # Implementation depends on the system
        pass
        
    def _optimize_error_rate(self):
        """Optimize error rate"""
        # Implementation depends on the system
        pass
        
    def _calculate_response_time(self) -> float:
        """Calculate average response time"""
        # Implementation depends on the system
        return 0.0
        
    def _calculate_throughput(self) -> float:
        """Calculate system throughput"""
        # Implementation depends on the system
        return 0.0
        
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        # Implementation depends on the system
        return 0.0
        
    def analyze_performance(
        self,
        code: str,
        file_path: str,
        performance_type: PerformanceType,
        context: Optional[Dict[str, Any]] = None
    ) -> PerformanceResult:
        """Analyze code performance based on specified type"""
        try:
            # Initialize result
            result = PerformanceResult(
                performance_type=performance_type,
                metrics={},
                issues=[],
                recommendations=[],
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "context": context or {}
                }
            )
            
            # Get performance rules for type
            rules = self.performance_rules.get(performance_type, [])
            
            # Parse code
            tree = ast.parse(code)
            
            # Perform analysis
            for rule in rules:
                metric = self._analyze_performance_metric(
                    rule["name"],
                    code,
                    tree,
                    rule["threshold"],
                    context
                )
                result.metrics[rule["name"]] = metric
                
                # Check for issues
                if metric.status != "good":
                    result.issues.append({
                        "metric": rule["name"],
                        "value": metric.value,
                        "threshold": rule["threshold"],
                        "status": metric.status,
                        "description": rule["description"]
                    })
                    
                # Add recommendations
                result.recommendations.extend(metric.recommendations)
                
            # Generate cross-metric recommendations
            result.recommendations.extend(
                self._generate_cross_metric_recommendations(result.metrics)
            )
            
            # Store in history
            self.analysis_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to analyze performance: {str(e)}")
            
    def _analyze_performance_metric(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        threshold: float,
        context: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetric:
        """Analyze specific performance metric"""
        try:
            # Calculate metric value
            value = self._calculate_metric_value(
                metric_name,
                code,
                tree,
                context
            )
            
            # Determine status
            status = self._determine_metric_status(value, threshold)
            
            # Generate recommendations
            recommendations = self._generate_metric_recommendations(
                metric_name,
                value,
                threshold,
                status
            )
            
            return PerformanceMetric(
                name=metric_name,
                value=value,
                threshold=threshold,
                status=status,
                details={
                    "code": code,
                    "context": context
                },
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze performance metric {metric_name}: {str(e)}")
            return PerformanceMetric(
                name=metric_name,
                value=0.0,
                threshold=threshold,
                status="error",
                details={"error": str(e)},
                recommendations=["Fix performance analysis error"]
            )
            
    def _calculate_metric_value(
        self,
        metric_name: str,
        code: str,
        tree: ast.AST,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate metric value"""
        if metric_name == "cpu_usage":
            return self._calculate_cpu_usage(code, tree)
        elif metric_name == "loop_efficiency":
            return self._calculate_loop_efficiency(code, tree)
        elif metric_name == "algorithm_complexity":
            return self._calculate_algorithm_complexity(code, tree)
        elif metric_name == "memory_usage":
            return self._calculate_memory_usage(code, tree)
        elif metric_name == "memory_leaks":
            return self._calculate_memory_leaks(code, tree)
        elif metric_name == "garbage_collection":
            return self._calculate_garbage_collection(code, tree)
        elif metric_name == "io_efficiency":
            return self._calculate_io_efficiency(code, tree)
        elif metric_name == "file_handling":
            return self._calculate_file_handling(code, tree)
        elif metric_name == "buffer_usage":
            return self._calculate_buffer_usage(code, tree)
        elif metric_name == "network_efficiency":
            return self._calculate_network_efficiency(code, tree)
        elif metric_name == "connection_pooling":
            return self._calculate_connection_pooling(code, tree)
        elif metric_name == "request_batching":
            return self._calculate_request_batching(code, tree)
        elif metric_name == "thread_efficiency":
            return self._calculate_thread_efficiency(code, tree)
        elif metric_name == "async_efficiency":
            return self._calculate_async_efficiency(code, tree)
        elif metric_name == "resource_contention":
            return self._calculate_resource_contention(code, tree)
        elif metric_name == "cache_efficiency":
            return self._calculate_cache_efficiency(code, tree)
        elif metric_name == "cache_hit_rate":
            return self._calculate_cache_hit_rate(code, tree)
        elif metric_name == "cache_invalidation":
            return self._calculate_cache_invalidation(code, tree)
        elif metric_name == "time_complexity":
            return self._calculate_time_complexity(code, tree)
        elif metric_name == "space_complexity":
            return self._calculate_space_complexity(code, tree)
        elif metric_name == "algorithm_efficiency":
            return self._calculate_algorithm_efficiency(code, tree)
        elif metric_name == "query_efficiency":
            return self._calculate_query_efficiency(code, tree)
        elif metric_name == "index_usage":
            return self._calculate_index_usage(code, tree)
        elif metric_name == "connection_efficiency":
            return self._calculate_connection_efficiency(code, tree)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")
            
    def _determine_metric_status(self, value: float, threshold: float) -> str:
        """Determine metric status based on value and threshold"""
        if value >= threshold:
            return "good"
        elif value >= threshold * 0.8:
            return "warning"
        else:
            return "critical"
            
    def _generate_metric_recommendations(
        self,
        metric_name: str,
        value: float,
        threshold: float,
        status: str
    ) -> List[str]:
        """Generate recommendations for metric"""
        recommendations = []
        
        if status == "warning":
            recommendations.append(
                f"{metric_name} is slightly below threshold. Consider optimizing "
                f"performance."
            )
        elif status == "critical":
            recommendations.append(
                f"{metric_name} is significantly below threshold. Immediate "
                f"performance improvements are recommended."
            )
            
        # Add specific recommendations based on metric
        if "cpu" in metric_name and value < threshold:
            recommendations.append(
                "High CPU usage detected. Consider optimizing algorithms and "
                "reducing computational complexity."
            )
        elif "memory" in metric_name and value < threshold:
            recommendations.append(
                "Memory usage issues detected. Consider implementing memory "
                "management optimizations."
            )
        elif "io" in metric_name and value < threshold:
            recommendations.append(
                "I/O efficiency issues detected. Consider using buffered operations "
                "and reducing I/O calls."
            )
        elif "network" in metric_name and value < threshold:
            recommendations.append(
                "Network efficiency issues detected. Consider implementing "
                "connection pooling and request batching."
            )
        elif "concurrency" in metric_name and value < threshold:
            recommendations.append(
                "Concurrency issues detected. Consider using async/await or "
                "thread pools for better resource utilization."
            )
        elif "cache" in metric_name and value < threshold:
            recommendations.append(
                "Cache efficiency issues detected. Consider optimizing cache "
                "strategies and invalidation policies."
            )
        elif "algorithm" in metric_name and value < threshold:
            recommendations.append(
                "Algorithm efficiency issues detected. Consider using more "
                "efficient algorithms and data structures."
            )
        elif "database" in metric_name and value < threshold:
            recommendations.append(
                "Database efficiency issues detected. Consider optimizing queries "
                "and implementing proper indexing."
            )
            
        return recommendations
        
    def _generate_cross_metric_recommendations(
        self,
        metrics: Dict[str, PerformanceMetric]
    ) -> List[str]:
        """Generate recommendations based on multiple metrics"""
        recommendations = []
        
        # Check for multiple performance issues
        performance_metrics = [
            m for n, m in metrics.items()
            if any(p in n for p in ["cpu", "memory", "io", "network"])
        ]
        if len(performance_metrics) > 1 and all(m.status == "critical" for m in performance_metrics):
            recommendations.append(
                "Multiple critical performance issues detected. Consider comprehensive "
                "performance optimization."
            )
            
        # Check for resource contention
        if ("thread_efficiency" in metrics and "resource_contention" in metrics and
            metrics["thread_efficiency"].status == "critical" and
            metrics["resource_contention"].status == "critical"):
            recommendations.append(
                "Critical thread and resource contention issues detected. Consider "
                "implementing better concurrency patterns."
            )
            
        # Check for I/O and network issues
        if ("io_efficiency" in metrics and "network_efficiency" in metrics and
            metrics["io_efficiency"].status == "critical" and
            metrics["network_efficiency"].status == "critical"):
            recommendations.append(
                "Critical I/O and network efficiency issues detected. Consider "
                "implementing better I/O and network patterns."
            )
            
        return recommendations
        
    def get_analysis_history(self) -> List[PerformanceResult]:
        """Get analysis history"""
        return self.analysis_history
        
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.analysis_history:
            return {}
            
        latest = self.analysis_history[-1]
        return {
            "performance_type": latest.performance_type.value,
            "metrics": {
                name: {
                    "value": metric.value,
                    "status": metric.status
                }
                for name, metric in latest.metrics.items()
            },
            "issue_count": len(latest.issues),
            "recommendation_count": len(latest.recommendations)
        }
        
    def analyze_code(self, code: str) -> PerformanceAnalysisResult:
        """Analyze code for performance issues"""
        try:
            # Parse code into AST
            tree = ast.parse(code)
            
            # Find performance issues
            issues = self._find_performance_issues(tree, code)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(issues)
            
            # Calculate metrics
            metrics = self._calculate_metrics(issues)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues)
            
            return PerformanceAnalysisResult(
                issues=issues,
                performance_score=performance_score,
                metrics=metrics,
                recommendations=recommendations,
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "total_issues": len(issues)
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to analyze code: {str(e)}")
            
    def _find_performance_issues(self, tree: ast.AST, code: str) -> List[PerformanceIssue]:
        """Find performance issues in code"""
        issues = []
        
        # Check for pattern-based issues
        for issue_type, patterns in self.performance_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern["pattern"], code)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    column = match.start() - code.rfind('\n', 0, match.start())
                    code_snippet = self._get_code_snippet(code, line_number)
                    
                    issue = PerformanceIssue(
                        type=issue_type,
                        severity=pattern["severity"],
                        description=pattern["description"],
                        line_number=line_number,
                        column=column,
                        code_snippet=code_snippet,
                        recommendation=pattern["recommendation"],
                        impact="High" if pattern["severity"] == "critical" else "Medium"
                    )
                    issues.append(issue)
                    
        # Check for AST-based issues
        issues.extend(self._find_ast_issues(tree, code))
        
        return issues
        
    def _find_ast_issues(self, tree: ast.AST, code: str) -> List[PerformanceIssue]:
        """Find performance issues using AST analysis"""
        issues = []
        
        class PerformanceVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # Check for inefficient loops
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            issues.append(PerformanceIssue(
                                type="loop",
                                severity="warning",
                                description="Potential inefficient loop detected",
                                line_number=node.lineno,
                                column=node.col_offset,
                                code_snippet=self._get_code_snippet(code, node.lineno),
                                recommendation="Consider using list comprehension or vectorized operations",
                                impact="Medium"
                            ))
                            
            def visit_While(self, node):
                # Check for potential infinite loops
                if isinstance(node.test, ast.Constant) and node.test.value:
                    issues.append(PerformanceIssue(
                        type="loop",
                        severity="warning",
                        description="Potential infinite loop detected",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=self._get_code_snippet(code, node.lineno),
                        recommendation="Add proper termination conditions",
                        impact="High"
                    ))
                    
            def visit_Call(self, node):
                # Check for inefficient function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['append', 'extend']:
                        issues.append(PerformanceIssue(
                            type="list",
                            severity="warning",
                            description="List operation in loop detected",
                            line_number=node.lineno,
                            column=node.col_offset,
                            code_snippet=self._get_code_snippet(code, node.lineno),
                            recommendation="Use list comprehension or pre-allocate list",
                            impact="Medium"
                        ))
                        
        visitor = PerformanceVisitor()
        visitor.visit(tree)
        return issues
        
    def _get_code_snippet(self, code: str, line_number: int, context_lines: int = 2) -> str:
        """Get code snippet around a specific line"""
        lines = code.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        return '\n'.join(lines[start:end])
        
    def _calculate_performance_score(self, issues: List[PerformanceIssue]) -> float:
        """Calculate overall performance score"""
        if not issues:
            return 1.0
            
        severity_weights = {
            "critical": 0.0,
            "warning": 0.5,
            "info": 0.8
        }
        
        total_weight = sum(severity_weights[i.severity] for i in issues)
        return max(0.0, 1.0 - (total_weight / len(issues)))
        
    def _calculate_metrics(self, issues: List[PerformanceIssue]) -> Dict[str, float]:
        """Calculate performance metrics"""
        metrics = {
            'issue_count': len(issues),
            'critical_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'loop_count': 0,
            'memory_count': 0,
            'io_count': 0,
            'network_count': 0,
            'concurrency_count': 0,
            'cache_count': 0,
            'algorithm_count': 0,
            'database_count': 0
        }
        
        for issue in issues:
            metrics[f'{issue.severity}_count'] += 1
            metrics[f'{issue.type}_count'] += 1
            
        return metrics
        
    def _generate_recommendations(self, issues: List[PerformanceIssue]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = set()
        
        # Add specific recommendations for each issue
        for issue in issues:
            recommendations.add(issue.recommendation)
            
        # Add general recommendations based on issue types
        issue_types = {i.type for i in issues}
        
        if "loop" in issue_types:
            recommendations.add("Optimize loops and consider using vectorized operations")
            
        if "memory" in issue_types:
            recommendations.add("Implement memory management optimizations")
            
        if "io" in issue_types:
            recommendations.add("Use buffered operations and reduce I/O calls")
            
        if "network" in issue_types:
            recommendations.add("Implement connection pooling and request batching")
            
        if "concurrency" in issue_types:
            recommendations.add("Use async/await or thread pools for better resource utilization")
            
        if "cache" in issue_types:
            recommendations.add("Optimize cache strategies and invalidation policies")
            
        if "algorithm" in issue_types:
            recommendations.add("Use more efficient algorithms and data structures")
            
        if "database" in issue_types:
            recommendations.add("Optimize queries and implement proper indexing")
            
        return list(recommendations)
        
    def register_performance_pattern(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        description: str,
        recommendation: str
    ):
        """Register a new performance pattern"""
        if issue_type not in self.performance_patterns:
            self.performance_patterns[issue_type] = []
            
        self.performance_patterns[issue_type].append({
            "pattern": pattern,
            "severity": severity,
            "description": description,
            "recommendation": recommendation
        })
        
    def get_performance_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get registered performance patterns"""
        return self.performance_patterns
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance analysis metrics"""
        return self.analysis_metrics 