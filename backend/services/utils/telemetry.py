import logging
import time
import uuid
from typing import Dict, Any, Optional, List
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class TelemetryEvent:
    """Representation of a telemetry event"""
    
    def __init__(
        self,
        event_type: str,
        properties: Dict[str, Any],
        event_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.properties = properties
        self.timestamp = timestamp or time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "properties": self.properties,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TelemetryEvent':
        """Create an event from a dictionary"""
        return cls(
            event_id=data.get("event_id"),
            event_type=data["event_type"],
            properties=data["properties"],
            timestamp=data.get("timestamp")
        )

class TelemetryManager:
    """Manager for collecting and sending telemetry data"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one telemetry manager exists"""
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the telemetry manager if not already initialized"""
        if self.initialized:
            return
            
        self.events: List[TelemetryEvent] = []
        self.batch_size = 50
        self.enabled = True
        self.flush_interval = 60  # seconds
        self.logger = logging.getLogger(__name__)
        self.initialized = True
        self._background_task = None
        
    async def track_event(self, event_type: str, properties: Dict[str, Any]) -> str:
        """Track a new telemetry event"""
        if not self.enabled:
            return ""
            
        event = TelemetryEvent(event_type, properties)
        self.events.append(event)
        
        # If we've reached the batch size, flush events
        if len(self.events) >= self.batch_size:
            await self.flush()
            
        return event.event_id
        
    async def flush(self) -> bool:
        """Flush accumulated events to the telemetry service"""
        if not self.events:
            return True
            
        try:
            # In a real implementation, this would send the events to a telemetry service
            self.logger.info(f"Flushing {len(self.events)} telemetry events")
            
            # For demonstration, just log the events
            events_to_flush = self.events.copy()
            self.events.clear()
            
            # Simulate sending to a service
            await self._send_events(events_to_flush)
            
            return True
        except Exception as e:
            self.logger.error(f"Error flushing telemetry events: {str(e)}")
            return False
            
    async def _send_events(self, events: List[TelemetryEvent]) -> bool:
        """Send events to the telemetry service"""
        # This is a mock implementation
        # In a real system, this would send the events to a real service
        
        # Simulate network latency
        await asyncio.sleep(0.1)
        
        # Log event types for demonstration
        event_types = {}
        for event in events:
            event_type = event.event_type
            if event_type in event_types:
                event_types[event_type] += 1
            else:
                event_types[event_type] = 1
                
        self.logger.debug(f"Sent telemetry events: {event_types}")
        
        return True
        
    async def _periodic_flush(self) -> None:
        """Periodically flush events in the background"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                if self.events:
                    await self.flush()
            except asyncio.CancelledError:
                # Final flush on cancellation
                if self.events:
                    await self.flush()
                break
            except Exception as e:
                self.logger.error(f"Error in periodic flush: {str(e)}")
                
    async def start_background_task(self):
        """Start the background flush task in an async context"""
        if not self._background_task:
            self._background_task = asyncio.create_task(self._periodic_flush())
            self.logger.debug("Started telemetry background task")
                
    async def stop_background_task(self):
        """Stop the background flush task"""
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
            self._background_task = None
            self.logger.debug("Stopped telemetry background task")
                
    def disable(self) -> None:
        """Disable telemetry collection"""
        self.enabled = False
        
    def enable(self) -> None:
        """Enable telemetry collection"""
        self.enabled = True

    def track(self, event: TelemetryEvent) -> None:
        """Track a telemetry event"""
        self.events.append(event)

# Global telemetry handler
_telemetry_handler = None

def initialize_telemetry(handler=None):
    """Initialize the telemetry system with a handler"""
    global _telemetry_handler
    _telemetry_handler = handler or TelemetryManager()
    return _telemetry_handler

def track_event(event_type: str, properties: Dict[str, Any] = None):
    """
    Track an event in the telemetry system
    
    Args:
        event_type: Type of event to track
        properties: Properties to include with the event
    """
    global _telemetry_handler
    
    if _telemetry_handler is None:
        _telemetry_handler = TelemetryManager()
        
    if properties is None:
        properties = {}
        
    event = TelemetryEvent(event_type=event_type, properties=properties)
    _telemetry_handler.track(event)
    return event

# Global function for tracking events
_telemetry_manager = TelemetryManager()

async def track_event_async(event_type: str, properties: Dict[str, Any]) -> str:
    """Track a telemetry event"""
    return await _telemetry_manager.track_event(event_type, properties)

async def flush_telemetry() -> bool:
    """Flush all pending telemetry events"""
    return await _telemetry_manager.flush()

def disable_telemetry() -> None:
    """Disable telemetry collection"""
    _telemetry_manager.disable()

def enable_telemetry() -> None:
    """Enable telemetry collection"""
    _telemetry_manager.enable()

async def start_telemetry_background_task():
    """Start the telemetry background task"""
    await _telemetry_manager.start_background_task()
    
async def stop_telemetry_background_task():
    """Stop the telemetry background task"""
    await _telemetry_manager.stop_background_task()
