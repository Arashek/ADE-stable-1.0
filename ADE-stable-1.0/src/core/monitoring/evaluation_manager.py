from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import time
import json
import numpy as np
from datetime import datetime
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge
import wandb
from dataclasses import dataclass
from collections import defaultdict

from ..config import ModelConfig

logger = logging.getLogger(__name__)

@dataclass
class MetricConfig:
    """Configuration for metrics"""
    window_size: int = 1000
    update_interval: int = 60  # seconds
    retention_period: int = 7  # days

class EvaluationManager:
    """Manages monitoring and evaluation of model components"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.metric_config = MetricConfig()
        self._initialize_metrics()
        self._initialize_prometheus()
        self._initialize_wandb()
        
    def _initialize_metrics(self):
        """Initialize metrics tracking"""
        self.metrics = {
            "latency": defaultdict(list),
            "throughput": defaultdict(int),
            "error_rate": defaultdict(int),
            "success_rate": defaultdict(int),
            "resource_usage": defaultdict(list),
            "model_performance": defaultdict(list)
        }
        
    def _initialize_prometheus(self):
        """Initialize Prometheus metrics"""
        # Latency metrics
        self.latency_histogram = Histogram(
            "model_latency_seconds",
            "Model processing latency in seconds",
            ["component", "operation"]
        )
        
        # Throughput metrics
        self.throughput_counter = Counter(
            "model_requests_total",
            "Total number of model requests",
            ["component", "operation"]
        )
        
        # Error metrics
        self.error_counter = Counter(
            "model_errors_total",
            "Total number of model errors",
            ["component", "operation", "error_type"]
        )
        
        # Resource metrics
        self.memory_gauge = Gauge(
            "model_memory_usage_bytes",
            "Model memory usage in bytes",
            ["component"]
        )
        
        self.gpu_gauge = Gauge(
            "model_gpu_usage_percent",
            "Model GPU usage percentage",
            ["component", "device"]
        )
        
    def _initialize_wandb(self):
        """Initialize Weights & Biases for experiment tracking"""
        try:
            wandb.init(
                project="ade-evaluation",
                config=self.config.dict(),
                mode="disabled" if self.config.environment == "production" else "online"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Weights & Biases: {e}")
            
    def record_latency(self, component: str, operation: str, latency: float):
        """Record latency metric"""
        try:
            # Update Prometheus metric
            self.latency_histogram.labels(
                component=component,
                operation=operation
            ).observe(latency)
            
            # Update internal metric
            self.metrics["latency"][f"{component}:{operation}"].append(latency)
            
            # Trim old data
            if len(self.metrics["latency"][f"{component}:{operation}"]) > self.metric_config.window_size:
                self.metrics["latency"][f"{component}:{operation}"].pop(0)
                
        except Exception as e:
            logger.error(f"Failed to record latency: {e}")
            
    def record_throughput(self, component: str, operation: str):
        """Record throughput metric"""
        try:
            # Update Prometheus metric
            self.throughput_counter.labels(
                component=component,
                operation=operation
            ).inc()
            
            # Update internal metric
            self.metrics["throughput"][f"{component}:{operation}"] += 1
            
        except Exception as e:
            logger.error(f"Failed to record throughput: {e}")
            
    def record_error(self, component: str, operation: str, error_type: str):
        """Record error metric"""
        try:
            # Update Prometheus metric
            self.error_counter.labels(
                component=component,
                operation=operation,
                error_type=error_type
            ).inc()
            
            # Update internal metric
            self.metrics["error_rate"][f"{component}:{operation}"] += 1
            
        except Exception as e:
            logger.error(f"Failed to record error: {e}")
            
    def record_success(self, component: str, operation: str):
        """Record success metric"""
        try:
            # Update internal metric
            self.metrics["success_rate"][f"{component}:{operation}"] += 1
            
        except Exception as e:
            logger.error(f"Failed to record success: {e}")
            
    def record_resource_usage(
        self,
        component: str,
        memory_usage: float,
        gpu_usage: Optional[Dict[str, float]] = None
    ):
        """Record resource usage metrics"""
        try:
            # Update Prometheus metrics
            self.memory_gauge.labels(component=component).set(memory_usage)
            
            if gpu_usage:
                for device, usage in gpu_usage.items():
                    self.gpu_gauge.labels(
                        component=component,
                        device=device
                    ).set(usage)
                    
            # Update internal metric
            self.metrics["resource_usage"][component].append({
                "timestamp": time.time(),
                "memory": memory_usage,
                "gpu": gpu_usage
            })
            
            # Trim old data
            if len(self.metrics["resource_usage"][component]) > self.metric_config.window_size:
                self.metrics["resource_usage"][component].pop(0)
                
        except Exception as e:
            logger.error(f"Failed to record resource usage: {e}")
            
    def record_model_performance(
        self,
        component: str,
        metrics: Dict[str, float]
    ):
        """Record model performance metrics"""
        try:
            # Update internal metric
            self.metrics["model_performance"][component].append({
                "timestamp": time.time(),
                **metrics
            })
            
            # Trim old data
            if len(self.metrics["model_performance"][component]) > self.metric_config.window_size:
                self.metrics["model_performance"][component].pop(0)
                
            # Log to Weights & Biases
            wandb.log({
                f"{component}/{k}": v
                for k, v in metrics.items()
            })
            
        except Exception as e:
            logger.error(f"Failed to record model performance: {e}")
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "latency": {
                k: {
                    "mean": np.mean(v) if v else 0,
                    "std": np.std(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                    "p95": np.percentile(v, 95) if v else 0,
                    "p99": np.percentile(v, 99) if v else 0
                }
                for k, v in self.metrics["latency"].items()
            },
            "throughput": dict(self.metrics["throughput"]),
            "error_rate": dict(self.metrics["error_rate"]),
            "success_rate": dict(self.metrics["success_rate"]),
            "resource_usage": {
                k: {
                    "memory": {
                        "mean": np.mean([r["memory"] for r in v]) if v else 0,
                        "max": max([r["memory"] for r in v]) if v else 0
                    },
                    "gpu": {
                        device: {
                            "mean": np.mean([r["gpu"][device] for r in v if r["gpu"]]) if v else 0,
                            "max": max([r["gpu"][device] for r in v if r["gpu"]]) if v else 0
                        }
                        for device in next((r["gpu"].keys() for r in v if r["gpu"]), [])
                    }
                }
                for k, v in self.metrics["resource_usage"].items()
            },
            "model_performance": {
                k: {
                    metric: {
                        "mean": np.mean([r[metric] for r in v]) if v else 0,
                        "std": np.std([r[metric] for r in v]) if v else 0,
                        "min": min([r[metric] for r in v]) if v else 0,
                        "max": max([r[metric] for r in v]) if v else 0
                    }
                    for metric in next((r.keys() for r in v if r), [])
                    if metric != "timestamp"
                }
                for k, v in self.metrics["model_performance"].items()
            }
        }
        
    def export_metrics(self, output_dir: Path):
        """Export metrics to files"""
        try:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export metrics to JSON
            metrics = self.get_performance_metrics()
            with open(output_dir / "metrics.json", "w") as f:
                json.dump(metrics, f, indent=2)
                
            # Export metrics to CSV
            for metric_type, data in metrics.items():
                df = pd.DataFrame(data).T
                df.to_csv(output_dir / f"{metric_type}.csv")
                
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            
    def log_metrics(self):
        """Log performance metrics"""
        metrics = self.get_performance_metrics()
        logger.info("Performance Metrics:")
        logger.info(f"Latency: {metrics['latency']}")
        logger.info(f"Throughput: {metrics['throughput']}")
        logger.info(f"Error Rate: {metrics['error_rate']}")
        logger.info(f"Success Rate: {metrics['success_rate']}")
        logger.info(f"Resource Usage: {metrics['resource_usage']}")
        logger.info(f"Model Performance: {metrics['model_performance']}")
        
    async def run_ab_test(
        self,
        component: str,
        model_a: str,
        model_b: str,
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run A/B test between two model versions"""
        try:
            results = {
                "model_a": {"metrics": {}, "errors": []},
                "model_b": {"metrics": {}, "errors": []}
            }
            
            # Test model A
            for item in test_data:
                start_time = time.time()
                try:
                    # Run model A
                    result_a = await self._run_model(model_a, item)
                    
                    # Record metrics
                    latency = time.time() - start_time
                    self.record_latency(f"{component}_a", "inference", latency)
                    self.record_throughput(f"{component}_a", "inference")
                    self.record_success(f"{component}_a", "inference")
                    
                    # Record performance
                    self.record_model_performance(
                        f"{component}_a",
                        {"accuracy": result_a.get("accuracy", 0)}
                    )
                    
                except Exception as e:
                    self.record_error(f"{component}_a", "inference", str(e))
                    results["model_a"]["errors"].append(str(e))
                    
            # Test model B
            for item in test_data:
                start_time = time.time()
                try:
                    # Run model B
                    result_b = await self._run_model(model_b, item)
                    
                    # Record metrics
                    latency = time.time() - start_time
                    self.record_latency(f"{component}_b", "inference", latency)
                    self.record_throughput(f"{component}_b", "inference")
                    self.record_success(f"{component}_b", "inference")
                    
                    # Record performance
                    self.record_model_performance(
                        f"{component}_b",
                        {"accuracy": result_b.get("accuracy", 0)}
                    )
                    
                except Exception as e:
                    self.record_error(f"{component}_b", "inference", str(e))
                    results["model_b"]["errors"].append(str(e))
                    
            # Compare results
            comparison = self._compare_models(
                f"{component}_a",
                f"{component}_b"
            )
            
            # Log results
            wandb.log({
                f"{component}_ab_test_comparison": comparison
            })
            
            return {
                "status": "success",
                "results": results,
                "comparison": comparison
            }
            
        except Exception as e:
            logger.error(f"Failed to run A/B test: {e}")
            return {"error": str(e)}
            
    async def _run_model(self, model: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run model inference"""
        # Implement model inference logic
        return {"accuracy": 0.0}
        
    def _compare_models(self, model_a: str, model_b: str) -> Dict[str, Any]:
        """Compare performance metrics between two models"""
        metrics = self.get_performance_metrics()
        
        comparison = {
            "latency": {
                "difference": {
                    k: metrics["latency"][model_b][k] - metrics["latency"][model_a][k]
                    for k in ["mean", "std", "min", "max", "p95", "p99"]
                }
            },
            "throughput": {
                "difference": metrics["throughput"][model_b] - metrics["throughput"][model_a]
            },
            "error_rate": {
                "difference": metrics["error_rate"][model_b] - metrics["error_rate"][model_a]
            },
            "success_rate": {
                "difference": metrics["success_rate"][model_b] - metrics["success_rate"][model_a]
            },
            "resource_usage": {
                "memory": {
                    "difference": {
                        k: metrics["resource_usage"][model_b]["memory"][k] - 
                           metrics["resource_usage"][model_a]["memory"][k]
                        for k in ["mean", "max"]
                    }
                },
                "gpu": {
                    device: {
                        k: metrics["resource_usage"][model_b]["gpu"][device][k] - 
                           metrics["resource_usage"][model_a]["gpu"][device][k]
                        for k in ["mean", "max"]
                    }
                    for device in metrics["resource_usage"][model_b]["gpu"]
                }
            },
            "model_performance": {
                metric: {
                    k: metrics["model_performance"][model_b][metric][k] - 
                       metrics["model_performance"][model_a][metric][k]
                    for k in ["mean", "std", "min", "max"]
                }
                for metric in metrics["model_performance"][model_b]
            }
        }
        
        return comparison 