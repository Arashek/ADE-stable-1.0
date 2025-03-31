from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
from pydantic import BaseModel

class EventType(Enum):
    """Types of events that can be emitted."""
    PLAN_CREATED = "plan.created"
    PLAN_UPDATED = "plan.updated"
    PLAN_DELETED = "plan.deleted"
    PLAN_STARTED = "plan.started"
    PLAN_COMPLETED = "plan.completed"
    PLAN_FAILED = "plan.failed"
    PLAN_CANCELLED = "plan.cancelled"
    
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    LOG_MESSAGE = "log.message"
    ERROR_OCCURRED = "error.occurred"
    
    SYSTEM_STATUS = "system.status"
    RESOURCE_UPDATE = "resource.update"

@dataclass
class Event:
    """Event data structure."""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class EventEmitter:
    """Event emitter for handling real-time events."""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._logger = logging.getLogger(__name__)
        
    def on(self, event_type: EventType, callback: Callable[[Event], None]):
        """Register a callback for an event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        
    def off(self, event_type: EventType, callback: Callable[[Event], None]):
        """Remove a callback for an event type.
        
        Args:
            event_type: Type of event to remove listener for
            callback: Function to remove
        """
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
            
    async def emit(self, event_type: EventType, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Emit an event to all registered listeners.
        
        Args:
            event_type: Type of event to emit
            data: Event data
            metadata: Optional event metadata
        """
        event = Event(
            type=event_type,
            timestamp=datetime.now(),
            data=data,
            metadata=metadata
        )
        
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    self._logger.error(f"Error in event listener: {str(e)}")
                    
    def remove_all_listeners(self):
        """Remove all registered event listeners."""
        self._listeners.clear()
        
    def get_listener_count(self, event_type: EventType) -> int:
        """Get number of listeners for an event type.
        
        Args:
            event_type: Type of event to check
            
        Returns:
            Number of listeners
        """
        return len(self._listeners.get(event_type, []))

# Global event emitter instance
event_emitter = EventEmitter() 