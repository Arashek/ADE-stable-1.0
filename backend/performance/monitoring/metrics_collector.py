from typing import Dict, Any, List
import psutil
import time
from datetime import datetime
import socket
import threading
import queue
import asyncio
from ...config.logging_config import logger

class MetricsCollector:
    """Collector for detailed performance metrics"""
    
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.collection_interval = 60  # seconds
        self.is_collecting = False
        self.hostname = socket.gethostname()
        
    async def start_collection(self):
        """Start metrics collection"""
        self.is_collecting = True
        asyncio.create_task(self._collect_metrics())
        
    async def stop_collection(self):
        """Stop metrics collection"""
        self.is_collecting = False
        
    async def _collect_metrics(self):
        """Background task for metrics collection"""
        while self.is_collecting:
            try:
                metrics = await self._gather_metrics()
                self.metrics_queue.put(metrics)
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _gather_metrics(self) -> Dict[str, Any]:
        """Gather comprehensive system and application metrics"""
        try:
            # System metrics
            cpu_times = psutil.cpu_times_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_threads = process.num_threads()
            process_connections = len(process.connections())
            
            # Network metrics
            net_connections = psutil.net_connections()
            net_if_stats = psutil.net_if_stats()
            net_if_addrs = psutil.net_if_addrs()
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "hostname": self.hostname,
                "system": {
                    "cpu": {
                        "percent": psutil.cpu_percent(interval=1),
                        "count": cpu_count,
                        "frequency": {
                            "current": cpu_freq.current if cpu_freq else None,
                            "min": cpu_freq.min if cpu_freq else None,
                            "max": cpu_freq.max if cpu_freq else None
                        },
                        "times": {
                            "user": cpu_times.user,
                            "system": cpu_times.system,
                            "idle": cpu_times.idle,
                            "iowait": cpu_times.iowait
                        }
                    },
                    "memory": {
                        "total": memory.total / 1024 / 1024,  # MB
                        "available": memory.available / 1024 / 1024,  # MB
                        "used": memory.used / 1024 / 1024,  # MB
                        "percent": memory.percent
                    },
                    "swap": {
                        "total": swap.total / 1024 / 1024,  # MB
                        "used": swap.used / 1024 / 1024,  # MB
                        "free": swap.free / 1024 / 1024,  # MB
                        "percent": swap.percent
                    },
                    "disk": {
                        "total": disk.total / 1024 / 1024 / 1024,  # GB
                        "used": disk.used / 1024 / 1024 / 1024,  # GB
                        "free": disk.free / 1024 / 1024 / 1024,  # GB
                        "percent": disk.percent
                    }
                },
                "process": {
                    "pid": process.pid,
                    "name": process.name(),
                    "status": process.status(),
                    "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
                    "cpu_percent": process.cpu_percent(),
                    "memory": {
                        "rss": process_memory.rss / 1024 / 1024,  # MB
                        "vms": process_memory.vms / 1024 / 1024,  # MB
                        "percent": process.memory_percent()
                    },
                    "threads": process_threads,
                    "connections": process_connections
                },
                "network": {
                    "io": {
                        "bytes_sent": net_io.bytes_sent / 1024 / 1024,  # MB
                        "bytes_recv": net_io.bytes_recv / 1024 / 1024,  # MB
                        "packets_sent": net_io.packets_sent,
                        "packets_recv": net_io.packets_recv
                    },
                    "connections": {
                        "total": len(net_connections),
                        "tcp": len([c for c in net_connections if c.type == socket.SOCK_STREAM]),
                        "udp": len([c for c in net_connections if c.type == socket.SOCK_DGRAM])
                    },
                    "interfaces": {
                        name: {
                            "stats": {
                                "isup": stats.isup,
                                "speed": stats.speed,
                                "mtu": stats.mtu
                            },
                            "addresses": [
                                {
                                    "family": addr.family.name,
                                    "address": addr.address,
                                    "netmask": addr.netmask
                                }
                                for addr in addrs
                            ]
                        }
                        for name, (stats, addrs) in zip(net_if_stats.keys(), zip(net_if_stats.values(), net_if_addrs.values()))
                    }
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error gathering metrics: {str(e)}")
            return {}
            
    def get_metrics(self) -> List[Dict[str, Any]]:
        """Get collected metrics"""
        metrics = []
        while not self.metrics_queue.empty():
            metrics.append(self.metrics_queue.get())
        return metrics
        
    def clear_metrics(self):
        """Clear collected metrics"""
        while not self.metrics_queue.empty():
            self.metrics_queue.get() 