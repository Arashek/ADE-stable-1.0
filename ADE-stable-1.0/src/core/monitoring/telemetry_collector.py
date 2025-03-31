from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import time
import json
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge, Summary
import opentelemetry
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import elasticsearch
from elasticsearch import AsyncElasticsearch
import asyncio
from contextlib import asynccontextmanager
import uuid

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    type: str = "gauge"  # gauge, counter, histogram

@dataclass
class UserAction:
    """User action data."""
    user_id: str
    action: str
    timestamp: datetime
    metadata: Dict[str, Any]
    session_id: str
    ip_address: str
    user_agent: str

class TelemetryCollector:
    """Telemetry collection and management."""
    
    def __init__(
        self,
        elasticsearch_url: str = "http://localhost:9200",
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831,
        service_name: str = "api_gateway"
    ):
        # Initialize Prometheus metrics
        self.REQUEST_COUNT = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.REQUEST_LATENCY = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.ERROR_COUNT = Counter(
            'http_errors_total',
            'Total number of HTTP errors',
            ['method', 'endpoint', 'error_type']
        )
        
        self.ACTIVE_CONNECTIONS = Gauge(
            'active_connections',
            'Number of active connections',
            ['service']
        )
        
        self.MEMORY_USAGE = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.CPU_USAGE = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )
        
        # Initialize OpenTelemetry
        self._setup_tracing(jaeger_host, jaeger_port, service_name)
        self._setup_metrics()
        
        # Initialize Elasticsearch client
        self.es = AsyncElasticsearch([elasticsearch_url])
        
        # Initialize session tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    def _setup_tracing(self, jaeger_host: str, jaeger_port: int, service_name: str) -> None:
        """Setup distributed tracing."""
        # Create tracer provider
        provider = TracerProvider()
        
        # Add Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
            service_name=service_name
        )
        provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        
        # Create tracer
        self.tracer = trace.get_tracer(__name__)
        
    def _setup_metrics(self) -> None:
        """Setup OpenTelemetry metrics."""
        # Create meter provider
        provider = MeterProvider()
        
        # Add Prometheus exporter
        prometheus_exporter = PrometheusExporter()
        provider.add_metric_reader(prometheus_exporter)
        
        # Set global meter provider
        metrics.set_meter_provider(provider)
        
        # Create meter
        self.meter = metrics.get_meter(__name__)
        
    async def record_performance_metric(self, metric: PerformanceMetric) -> None:
        """Record a performance metric."""
        try:
            # Update Prometheus metric
            if metric.type == "gauge":
                self.METRICS[metric.name].labels(**metric.labels).set(metric.value)
            elif metric.type == "counter":
                self.METRICS[metric.name].labels(**metric.labels).inc(metric.value)
            elif metric.type == "histogram":
                self.METRICS[metric.name].labels(**metric.labels).observe(metric.value)
                
            # Store in Elasticsearch
            await self.es.index(
                index=f"metrics-{datetime.now().strftime('%Y.%m')}",
                document={
                    "name": metric.name,
                    "value": metric.value,
                    "timestamp": metric.timestamp,
                    "labels": metric.labels,
                    "type": metric.type
                }
            )
        except Exception as e:
            logger.error(f"Failed to record performance metric: {str(e)}")
            
    async def record_user_action(self, action: UserAction) -> None:
        """Record a user action."""
        try:
            # Store in Elasticsearch
            await self.es.index(
                index=f"user-actions-{datetime.now().strftime('%Y.%m')}",
                document={
                    "user_id": action.user_id,
                    "action": action.action,
                    "timestamp": action.timestamp,
                    "metadata": action.metadata,
                    "session_id": action.session_id,
                    "ip_address": action.ip_address,
                    "user_agent": action.user_agent
                }
            )
            
            # Update session tracking
            if action.session_id not in self.active_sessions:
                self.active_sessions[action.session_id] = {
                    "user_id": action.user_id,
                    "start_time": action.timestamp,
                    "actions": []
                }
            self.active_sessions[action.session_id]["actions"].append(action)
            
        except Exception as e:
            logger.error(f"Failed to record user action: {str(e)}")
            
    @asynccontextmanager
    async def trace_request(self, name: str, attributes: Optional[Dict[str, str]] = None) -> None:
        """Trace a request with OpenTelemetry."""
        with self.tracer.start_as_current_span(
            name,
            attributes=attributes or {}
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                span.record_exception(e)
                span.set_attribute("error", str(e))
                raise
                
    async def record_error(
        self,
        method: str,
        endpoint: str,
        error_type: str,
        error_message: str
    ) -> None:
        """Record an error occurrence."""
        try:
            # Update Prometheus metric
            self.ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type=error_type
            ).inc()
            
            # Store in Elasticsearch
            await self.es.index(
                index=f"errors-{datetime.now().strftime('%Y.%m')}",
                document={
                    "method": method,
                    "endpoint": endpoint,
                    "error_type": error_type,
                    "error_message": error_message,
                    "timestamp": datetime.now()
                }
            )
        except Exception as e:
            logger.error(f"Failed to record error: {str(e)}")
            
    async def get_session_analytics(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific session."""
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        return {
            "user_id": session["user_id"],
            "duration": (datetime.now() - session["start_time"]).total_seconds(),
            "action_count": len(session["actions"]),
            "actions": [
                {
                    "action": action.action,
                    "timestamp": action.timestamp,
                    "metadata": action.metadata
                }
                for action in session["actions"]
            ]
        }
        
    async def get_performance_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        labels: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Get performance metrics for a time range."""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"name": metric_name}},
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": start_time,
                                        "lte": end_time
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            if labels:
                for key, value in labels.items():
                    query["query"]["bool"]["must"].append(
                        {"term": {f"labels.{key}": value}}
                    )
                    
            result = await self.es.search(
                index=f"metrics-{datetime.now().strftime('%Y.%m')}",
                body=query
            )
            
            return [
                {
                    "value": hit["_source"]["value"],
                    "timestamp": hit["_source"]["timestamp"],
                    "labels": hit["_source"]["labels"]
                }
                for hit in result["hits"]["hits"]
            ]
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            return []
            
    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """Clean up old sessions."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = [
            session_id
            for session_id, session in self.active_sessions.items()
            if session["start_time"] < cutoff
        ]
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            
    async def close(self) -> None:
        """Close connections and cleanup."""
        await self.es.close()
        # Add any other cleanup tasks here 