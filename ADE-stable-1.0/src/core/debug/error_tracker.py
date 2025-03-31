from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity level of an error"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ErrorEvent:
    """Represents an error event"""
    timestamp: datetime
    error_id: str
    message: str
    severity: ErrorSeverity
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = None
    resolution: Optional[str] = None
    resolved: bool = False

class ErrorTracker:
    """Tracks and analyzes errors during debug operations"""
    
    def __init__(self):
        self.errors: Dict[str, List[ErrorEvent]] = {}
        self.error_patterns: Dict[str, int] = {}
        self.resolution_patterns: Dict[str, int] = {}
        
    def record_error(self, debug_id: str,
                    message: str,
                    severity: ErrorSeverity,
                    stack_trace: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """Record a new error event
        
        Args:
            debug_id: ID of the debug operation
            message: Error message
            severity: Error severity level
            stack_trace: Optional stack trace
            context: Optional context information
            
        Returns:
            str: Unique error ID
        """
        try:
            error_id = f"err_{len(self.errors.get(debug_id, [])) + 1}"
            
            error_event = ErrorEvent(
                timestamp=datetime.now(),
                error_id=error_id,
                message=message,
                severity=severity,
                stack_trace=stack_trace,
                context=context or {}
            )
            
            if debug_id not in self.errors:
                self.errors[debug_id] = []
            self.errors[debug_id].append(error_event)
            
            # Update error patterns
            pattern = self._extract_error_pattern(message)
            self.error_patterns[pattern] = self.error_patterns.get(pattern, 0) + 1
            
            logger.info(f"Recorded error {error_id} for debug operation {debug_id}")
            return error_id
            
        except Exception as e:
            logger.error(f"Failed to record error: {str(e)}")
            return ""
            
    def resolve_error(self, debug_id: str,
                     error_id: str,
                     resolution: str) -> bool:
        """Mark an error as resolved
        
        Args:
            debug_id: ID of the debug operation
            error_id: ID of the error to resolve
            resolution: Description of how the error was resolved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if debug_id not in self.errors:
                logger.warning(f"Debug operation {debug_id} not found")
                return False
                
            for error in self.errors[debug_id]:
                if error.error_id == error_id:
                    error.resolution = resolution
                    error.resolved = True
                    
                    # Update resolution patterns
                    pattern = self._extract_resolution_pattern(resolution)
                    self.resolution_patterns[pattern] = self.resolution_patterns.get(pattern, 0) + 1
                    
                    logger.info(f"Resolved error {error_id} for debug operation {debug_id}")
                    return True
                    
            logger.warning(f"Error {error_id} not found for debug operation {debug_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve error: {str(e)}")
            return False
            
    def get_errors(self, debug_id: str) -> List[Dict[str, Any]]:
        """Get all errors for a debug operation
        
        Args:
            debug_id: ID of the debug operation
            
        Returns:
            List of error events as dictionaries
        """
        try:
            if debug_id not in self.errors:
                return []
                
            return [
                {
                    "error_id": error.error_id,
                    "timestamp": error.timestamp.isoformat(),
                    "message": error.message,
                    "severity": error.severity.value,
                    "stack_trace": error.stack_trace,
                    "context": error.context,
                    "resolution": error.resolution,
                    "resolved": error.resolved
                }
                for error in self.errors[debug_id]
            ]
            
        except Exception as e:
            logger.error(f"Failed to get errors: {str(e)}")
            return []
            
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about errors and resolutions
        
        Returns:
            Dictionary containing error statistics
        """
        try:
            total_errors = sum(len(errors) for errors in self.errors.values())
            resolved_errors = sum(
                sum(1 for error in errors if error.resolved)
                for errors in self.errors.values()
            )
            
            return {
                "total_errors": total_errors,
                "resolved_errors": resolved_errors,
                "resolution_rate": (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
                "error_patterns": self.error_patterns,
                "resolution_patterns": self.resolution_patterns
            }
            
        except Exception as e:
            logger.error(f"Failed to get error statistics: {str(e)}")
            return {}
            
    def _extract_error_pattern(self, message: str) -> str:
        """Extract a pattern from an error message
        
        Args:
            message: Error message
            
        Returns:
            str: Extracted pattern
        """
        # Simple pattern extraction - can be enhanced with more sophisticated analysis
        words = message.lower().split()
        return " ".join(words[:3])  # Use first 3 words as pattern
        
    def _extract_resolution_pattern(self, resolution: str) -> str:
        """Extract a pattern from a resolution message
        
        Args:
            resolution: Resolution message
            
        Returns:
            str: Extracted pattern
        """
        # Simple pattern extraction - can be enhanced with more sophisticated analysis
        words = resolution.lower().split()
        return " ".join(words[:3])  # Use first 3 words as pattern 