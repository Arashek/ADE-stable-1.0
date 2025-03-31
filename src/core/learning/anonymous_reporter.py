from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass
from .error_collector import ErrorEvent, ErrorContext

@dataclass
class AnonymizedError:
    error_hash: str
    error_type: str
    message_pattern: str
    stack_pattern: str
    severity: str
    component: str
    anonymized_context: Dict[str, Any]
    tags: list[str]
    timestamp: datetime

class AnonymousReporter:
    def __init__(self):
        self.sensitive_fields = {
            "user_id", "email", "ip_address", "hostname", "file_paths",
            "database_names", "api_keys", "tokens", "passwords"
        }
        self.pattern_masks = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            "file_path": r"(?:/[^/]+)*/[^/]+",
            "api_key": r"[a-zA-Z0-9_-]{32,}",
            "token": r"[a-zA-Z0-9_-]{32,}"
        }

    def anonymize_error(self, error_event: ErrorEvent) -> AnonymizedError:
        """Convert an error event into an anonymized version"""
        # Create a hash of the error for deduplication
        error_hash = self._generate_error_hash(error_event)
        
        # Anonymize the message and stack trace
        message_pattern = self._anonymize_text(error_event.message)
        stack_pattern = self._anonymize_text(error_event.stack_trace) if error_event.stack_trace else None
        
        # Anonymize the context
        anonymized_context = self._anonymize_context(error_event.context)
        
        return AnonymizedError(
            error_hash=error_hash,
            error_type=error_event.error_type,
            message_pattern=message_pattern,
            stack_pattern=stack_pattern,
            severity=error_event.severity.value,
            component=error_event.context.component,
            anonymized_context=anonymized_context,
            tags=error_event.tags,
            timestamp=error_event.context.timestamp
        )

    def _generate_error_hash(self, error_event: ErrorEvent) -> str:
        """Generate a unique hash for the error event"""
        # Create a string representation of the error without sensitive data
        error_str = f"{error_event.error_type}:{error_event.message}:{error_event.stack_trace}"
        return hashlib.sha256(error_str.encode()).hexdigest()

    def _anonymize_text(self, text: Optional[str]) -> str:
        """Anonymize sensitive information in text"""
        if not text:
            return ""
            
        import re
        anonymized = text
        
        # Replace sensitive patterns with placeholders
        for pattern_name, pattern in self.pattern_masks.items():
            anonymized = re.sub(pattern, f"[{pattern_name}]", anonymized)
            
        return anonymized

    def _anonymize_context(self, context: ErrorContext) -> Dict[str, Any]:
        """Anonymize sensitive information in the context"""
        anonymized = {
            "timestamp": context.timestamp,
            "environment": context.environment,
            "component": context.component
        }
        
        # Anonymize metadata
        if context.metadata:
            anonymized["metadata"] = self._anonymize_dict(context.metadata)
            
        return anonymized

    def _anonymize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively anonymize sensitive information in a dictionary"""
        anonymized = {}
        for key, value in data.items():
            if key in self.sensitive_fields:
                anonymized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_dict(value)
            elif isinstance(value, list):
                anonymized[key] = [
                    self._anonymize_dict(item) if isinstance(item, dict)
                    else self._anonymize_text(str(item))
                    for item in value
                ]
            else:
                anonymized[key] = self._anonymize_text(str(value))
        return anonymized

    def to_json(self, anonymized_error: AnonymizedError) -> str:
        """Convert an anonymized error to JSON format"""
        return json.dumps({
            "error_hash": anonymized_error.error_hash,
            "error_type": anonymized_error.error_type,
            "message_pattern": anonymized_error.message_pattern,
            "stack_pattern": anonymized_error.stack_pattern,
            "severity": anonymized_error.severity,
            "component": anonymized_error.component,
            "anonymized_context": anonymized_error.anonymized_context,
            "tags": anonymized_error.tags,
            "timestamp": anonymized_error.timestamp.isoformat()
        })

    def from_json(self, json_str: str) -> AnonymizedError:
        """Create an anonymized error from JSON format"""
        data = json.loads(json_str)
        return AnonymizedError(
            error_hash=data["error_hash"],
            error_type=data["error_type"],
            message_pattern=data["message_pattern"],
            stack_pattern=data["stack_pattern"],
            severity=data["severity"],
            component=data["component"],
            anonymized_context=data["anonymized_context"],
            tags=data["tags"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        ) 