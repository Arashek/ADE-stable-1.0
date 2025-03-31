from typing import Dict, Any, Optional
import logging
import uuid
from datetime import datetime

from .debug_loop_monitor import DebugLoopMonitor, DebugStatus
from .error_tracker import ErrorTracker, ErrorSeverity

logger = logging.getLogger(__name__)

class DebugManager:
    """Manages debug operations, monitoring, and error tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.debug_monitor = DebugLoopMonitor(config)
        self.error_tracker = ErrorTracker()
        
    def start_debug_session(self) -> str:
        """Start a new debug session
        
        Returns:
            str: Unique debug session ID
        """
        try:
            debug_id = f"debug_{uuid.uuid4().hex[:8]}"
            
            if self.debug_monitor.start_monitoring(debug_id):
                logger.info(f"Started debug session {debug_id}")
                return debug_id
            else:
                logger.error("Failed to start debug session")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to start debug session: {str(e)}")
            return ""
            
    def end_debug_session(self, debug_id: str) -> bool:
        """End a debug session
        
        Args:
            debug_id: ID of the debug session
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.debug_monitor.stop_monitoring(debug_id):
                logger.info(f"Ended debug session {debug_id}")
                return True
            else:
                logger.error(f"Failed to end debug session {debug_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to end debug session: {str(e)}")
            return False
            
    def update_debug_progress(self, debug_id: str,
                            step_count: Optional[int] = None,
                            error_count: Optional[int] = None,
                            warning_count: Optional[int] = None,
                            resource_usage: Optional[Dict[str, float]] = None,
                            completion_percentage: Optional[float] = None) -> None:
        """Update progress of a debug session
        
        Args:
            debug_id: ID of the debug session
            step_count: Number of steps completed
            error_count: Number of errors encountered
            warning_count: Number of warnings encountered
            resource_usage: Current resource usage metrics
            completion_percentage: Overall completion percentage
        """
        try:
            self.debug_monitor.update_progress(
                debug_id=debug_id,
                step_count=step_count,
                error_count=error_count,
                warning_count=warning_count,
                resource_usage=resource_usage,
                completion_percentage=completion_percentage
            )
            
        except Exception as e:
            logger.error(f"Failed to update debug progress: {str(e)}")
            
    def record_error(self, debug_id: str,
                    message: str,
                    severity: ErrorSeverity,
                    stack_trace: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """Record a new error in a debug session
        
        Args:
            debug_id: ID of the debug session
            message: Error message
            severity: Error severity level
            stack_trace: Optional stack trace
            context: Optional context information
            
        Returns:
            str: Unique error ID
        """
        try:
            error_id = self.error_tracker.record_error(
                debug_id=debug_id,
                message=message,
                severity=severity,
                stack_trace=stack_trace,
                context=context
            )
            
            # Update debug progress with error count
            if error_id:
                errors = self.error_tracker.get_errors(debug_id)
                self.update_debug_progress(
                    debug_id=debug_id,
                    error_count=len([e for e in errors if e["severity"] == "error"]),
                    warning_count=len([e for e in errors if e["severity"] == "warning"])
                )
                
            return error_id
            
        except Exception as e:
            logger.error(f"Failed to record error: {str(e)}")
            return ""
            
    def resolve_error(self, debug_id: str,
                     error_id: str,
                     resolution: str) -> bool:
        """Mark an error as resolved
        
        Args:
            debug_id: ID of the debug session
            error_id: ID of the error to resolve
            resolution: Description of how the error was resolved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.error_tracker.resolve_error(
                debug_id=debug_id,
                error_id=error_id,
                resolution=resolution
            )
            
        except Exception as e:
            logger.error(f"Failed to resolve error: {str(e)}")
            return False
            
    def get_debug_status(self, debug_id: str) -> Dict[str, Any]:
        """Get current status of a debug session
        
        Args:
            debug_id: ID of the debug session
            
        Returns:
            Dictionary containing debug status and metrics
        """
        try:
            progress = self.debug_monitor.get_progress(debug_id)
            errors = self.error_tracker.get_errors(debug_id)
            
            return {
                "progress": progress,
                "errors": errors,
                "error_statistics": self.error_tracker.get_error_statistics()
            }
            
        except Exception as e:
            logger.error(f"Failed to get debug status: {str(e)}")
            return {} 