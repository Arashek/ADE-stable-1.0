from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import json
from pathlib import Path

class ErrorSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ErrorContext:
    timestamp: datetime
    instance_id: str
    environment: str
    component: str
    user_id: Optional[str]
    session_id: str
    metadata: Dict[str, Any]

@dataclass
class ErrorEvent:
    id: str
    error_type: str
    message: str
    stack_trace: Optional[str]
    severity: ErrorSeverity
    context: ErrorContext
    related_events: List[str]
    resolution_status: str
    tags: List[str]

class ErrorCollector:
    def __init__(self, instance_id: str, environment: str):
        self.instance_id = instance_id
        self.environment = environment
        self.batch_size = 100
        self.error_buffer: List[ErrorEvent] = []
        self._setup_storage()

    def _setup_storage(self):
        """Initialize storage for error events"""
        storage_path = Path("data/errors")
        storage_path.mkdir(parents=True, exist_ok=True)
        self.storage_path = storage_path

    def capture_error(
        self,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        component: str = "unknown",
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Capture a new error event"""
        error_id = str(uuid.uuid4())
        context = ErrorContext(
            timestamp=datetime.utcnow(),
            instance_id=self.instance_id,
            environment=self.environment,
            component=component,
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            metadata=metadata or {}
        )

        error_event = ErrorEvent(
            id=error_id,
            error_type=error_type,
            message=message,
            stack_trace=stack_trace,
            severity=severity,
            context=context,
            related_events=[],
            resolution_status="open",
            tags=tags or []
        )

        self.error_buffer.append(error_event)
        self._process_buffer_if_full()
        return error_id

    def _process_buffer_if_full(self):
        """Process the error buffer if it reaches the batch size"""
        if len(self.error_buffer) >= self.batch_size:
            self._process_error_batch()

    def _process_error_batch(self):
        """Process a batch of error events"""
        if not self.error_buffer:
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        batch_file = self.storage_path / f"error_batch_{timestamp}.json"
        
        with open(batch_file, "w") as f:
            json.dump(
                [self._error_event_to_dict(event) for event in self.error_buffer],
                f,
                default=str
            )
        
        self.error_buffer.clear()

    def _error_event_to_dict(self, event: ErrorEvent) -> Dict[str, Any]:
        """Convert an ErrorEvent to a dictionary for storage"""
        return {
            "id": event.id,
            "error_type": event.error_type,
            "message": event.message,
            "stack_trace": event.stack_trace,
            "severity": event.severity.value,
            "context": {
                "timestamp": event.context.timestamp,
                "instance_id": event.context.instance_id,
                "environment": event.context.environment,
                "component": event.context.component,
                "user_id": event.context.user_id,
                "session_id": event.context.session_id,
                "metadata": event.context.metadata
            },
            "related_events": event.related_events,
            "resolution_status": event.resolution_status,
            "tags": event.tags
        }

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected errors"""
        stats = {
            "total_errors": 0,
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "errors_by_component": {},
            "errors_by_type": {},
            "recent_errors": []
        }

        for batch_file in self.storage_path.glob("error_batch_*.json"):
            with open(batch_file, "r") as f:
                errors = json.load(f)
                for error in errors:
                    stats["total_errors"] += 1
                    stats["errors_by_severity"][error["severity"]] += 1
                    
                    component = error["context"]["component"]
                    stats["errors_by_component"][component] = stats["errors_by_component"].get(component, 0) + 1
                    
                    error_type = error["error_type"]
                    stats["errors_by_type"][error_type] = stats["errors_by_type"].get(error_type, 0) + 1

        return stats

    def cleanup_old_errors(self, days: int = 30):
        """Clean up error files older than specified days"""
        cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        for batch_file in self.storage_path.glob("error_batch_*.json"):
            if batch_file.stat().st_mtime < cutoff_date:
                batch_file.unlink() 