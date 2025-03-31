from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from fastapi import FastAPI
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TelemetryManager:
    def __init__(self, service_name: str, jaeger_host: Optional[str] = "localhost"):
        self.service_name = service_name
        self.jaeger_host = jaeger_host
        self.tracer_provider = None
        
    def setup(self):
        """Setup OpenTelemetry with Jaeger exporter"""
        try:
            # Create TracerProvider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # Create Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_host,
                agent_port=6831,
            )
            
            # Add SpanProcessor to the TracerProvider
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            logger.info(f"Telemetry setup completed for service: {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup telemetry: {str(e)}")
            
    def instrument_fastapi(self, app: FastAPI):
        """Instrument FastAPI application"""
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation completed")
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {str(e)}")
            
    def instrument_redis(self, client):
        """Instrument Redis client"""
        try:
            RedisInstrumentor().instrument(client=client)
            logger.info("Redis instrumentation completed")
        except Exception as e:
            logger.error(f"Failed to instrument Redis: {str(e)}")
            
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy engine"""
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumentation completed")
        except Exception as e:
            logger.error(f"Failed to instrument SQLAlchemy: {str(e)}")
            
    def create_span(self, name: str, attributes: dict = None):
        """Create a new trace span"""
        tracer = trace.get_tracer(__name__)
        return tracer.start_span(name, attributes=attributes)
