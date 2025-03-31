from typing import Dict, Any, List, Optional, Tuple
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
import traceback
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """Pattern for error detection"""
    pattern_id: str
    name: str
    description: str
    regex_pattern: str
    severity: str
    category: str
    suggested_fixes: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class ErrorContext:
    """Context of an error occurrence"""
    error_id: str
    timestamp: datetime
    error_type: str
    message: str
    stack_trace: str
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    local_vars: Dict[str, Any] = None
    global_vars: Dict[str, Any] = None
    system_state: Dict[str, Any] = None

@dataclass
class ErrorMatch:
    """Result of error pattern matching"""
    pattern: ErrorPattern
    context: ErrorContext
    match_groups: Dict[str, str]
    confidence: float
    metadata: Dict[str, Any] = None

class ErrorDetector:
    """Detects and analyzes errors using pattern matching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.patterns: Dict[str, ErrorPattern] = {}
        self.error_history: List[ErrorContext] = []
        self._load_patterns()
        
    def _load_patterns(self) -> None:
        """Load error patterns from configuration"""
        try:
            patterns_file = self.config.get("patterns_file", "error_patterns.json")
            if not Path(patterns_file).exists():
                logger.warning(f"Patterns file {patterns_file} not found")
                return
                
            with open(patterns_file, 'r') as f:
                patterns_data = json.load(f)
                
            for pattern_data in patterns_data:
                pattern = ErrorPattern(
                    pattern_id=pattern_data["id"],
                    name=pattern_data["name"],
                    description=pattern_data["description"],
                    regex_pattern=pattern_data["pattern"],
                    severity=pattern_data["severity"],
                    category=pattern_data["category"],
                    suggested_fixes=pattern_data.get("suggested_fixes", []),
                    metadata=pattern_data.get("metadata", {})
                )
                self.patterns[pattern.pattern_id] = pattern
                
            logger.info(f"Loaded {len(self.patterns)} error patterns")
            
        except Exception as e:
            logger.error(f"Failed to load error patterns: {str(e)}")
            
    async def detect_error(self, error: Exception, context: Dict[str, Any]) -> List[ErrorMatch]:
        """Detect errors using pattern matching
        
        Args:
            error: Exception object
            context: Additional context information
            
        Returns:
            List of matched error patterns
        """
        try:
            # Create error context
            error_context = self._create_error_context(error, context)
            self.error_history.append(error_context)
            
            # Match against patterns
            matches = []
            for pattern in self.patterns.values():
                match = self._match_pattern(pattern, error_context)
                if match:
                    matches.append(match)
                    
            # Sort matches by confidence
            matches.sort(key=lambda x: x.confidence, reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Error detection failed: {str(e)}")
            return []
            
    def _create_error_context(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """Create error context from exception
        
        Args:
            error: Exception object
            context: Additional context information
            
        Returns:
            ErrorContext object
        """
        # Get stack trace
        stack_trace = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
        
        # Extract source information
        source_info = self._extract_source_info(error.__traceback__)
        
        return ErrorContext(
            error_id=f"err_{len(self.error_history) + 1}",
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            message=str(error),
            stack_trace=stack_trace,
            source_file=source_info.get("file"),
            line_number=source_info.get("line"),
            function_name=source_info.get("function"),
            local_vars=context.get("local_vars", {}),
            global_vars=context.get("global_vars", {}),
            system_state=context.get("system_state", {})
        )
        
    def _extract_source_info(self, tb) -> Dict[str, Any]:
        """Extract source information from traceback
        
        Args:
            tb: Traceback object
            
        Returns:
            Dictionary containing source information
        """
        if not tb:
            return {}
            
        frame = tb.tb_frame
        return {
            "file": frame.f_code.co_filename,
            "line": tb.tb_lineno,
            "function": frame.f_code.co_name
        }
        
    def _match_pattern(self, pattern: ErrorPattern, context: ErrorContext) -> Optional[ErrorMatch]:
        """Match error context against pattern
        
        Args:
            pattern: Error pattern to match against
            context: Error context to match
            
        Returns:
            ErrorMatch object if pattern matches, None otherwise
        """
        try:
            # Compile regex pattern
            regex = re.compile(pattern.regex_pattern)
            
            # Try to match against error message
            message_match = regex.search(context.message)
            if message_match:
                return ErrorMatch(
                    pattern=pattern,
                    context=context,
                    match_groups=message_match.groupdict(),
                    confidence=1.0,
                    metadata={"match_type": "message"}
                )
                
            # Try to match against stack trace
            stack_match = regex.search(context.stack_trace)
            if stack_match:
                return ErrorMatch(
                    pattern=pattern,
                    context=context,
                    match_groups=stack_match.groupdict(),
                    confidence=0.8,
                    metadata={"match_type": "stack_trace"}
                )
                
            # Try to match against source file
            if context.source_file:
                file_match = regex.search(context.source_file)
                if file_match:
                    return ErrorMatch(
                        pattern=pattern,
                        context=context,
                        match_groups=file_match.groupdict(),
                        confidence=0.6,
                        metadata={"match_type": "source_file"}
                    )
                    
            return None
            
        except Exception as e:
            logger.error(f"Pattern matching failed: {str(e)}")
            return None
            
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected errors
        
        Returns:
            Dictionary containing error statistics
        """
        try:
            stats = {
                "total_errors": len(self.error_history),
                "error_types": {},
                "severities": {},
                "categories": {},
                "patterns_matched": {},
                "time_distribution": {}
            }
            
            for error in self.error_history:
                # Count error types
                stats["error_types"][error.error_type] = \
                    stats["error_types"].get(error.error_type, 0) + 1
                    
                # Count severities
                for pattern in self.patterns.values():
                    if pattern.regex_pattern in error.message:
                        stats["severities"][pattern.severity] = \
                            stats["severities"].get(pattern.severity, 0) + 1
                        stats["categories"][pattern.category] = \
                            stats["categories"].get(pattern.category, 0) + 1
                        stats["patterns_matched"][pattern.pattern_id] = \
                            stats["patterns_matched"].get(pattern.pattern_id, 0) + 1
                        
                # Count time distribution
                hour = error.timestamp.hour
                stats["time_distribution"][hour] = \
                    stats["time_distribution"].get(hour, 0) + 1
                    
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate error statistics: {str(e)}")
            return {}
            
    def analyze_error_trends(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Analyze error trends over a time window
        
        Args:
            time_window: Time window for analysis
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            cutoff_time = datetime.now() - time_window
            recent_errors = [
                error for error in self.error_history
                if error.timestamp >= cutoff_time
            ]
            
            trends = {
                "total_errors": len(recent_errors),
                "error_frequency": defaultdict(int),
                "severity_distribution": defaultdict(int),
                "category_distribution": defaultdict(int),
                "hourly_distribution": defaultdict(int),
                "common_patterns": defaultdict(int),
                "recurring_errors": defaultdict(list)
            }
            
            for error in recent_errors:
                # Count error types
                trends["error_frequency"][error.error_type] += 1
                
                # Count severities
                for pattern in self.patterns.values():
                    if pattern.regex_pattern in error.message:
                        trends["severity_distribution"][pattern.severity] += 1
                        trends["category_distribution"][pattern.category] += 1
                        trends["common_patterns"][pattern.pattern_id] += 1
                        
                # Count hourly distribution
                trends["hourly_distribution"][error.timestamp.hour] += 1
                
                # Track recurring errors
                error_key = f"{error.error_type}:{error.message}"
                trends["recurring_errors"][error_key].append(error.timestamp)
                
            # Calculate recurring error patterns
            for error_key, timestamps in trends["recurring_errors"].items():
                if len(timestamps) > 1:
                    intervals = [
                        (timestamps[i] - timestamps[i-1]).total_seconds()
                        for i in range(1, len(timestamps))
                    ]
                    trends["recurring_errors"][error_key] = {
                        "count": len(timestamps),
                        "avg_interval": sum(intervals) / len(intervals),
                        "min_interval": min(intervals),
                        "max_interval": max(intervals)
                    }
                    
            return trends
            
        except Exception as e:
            logger.error(f"Error trend analysis failed: {str(e)}")
            return {}
            
    def analyze_error_correlations(self) -> List[Dict[str, Any]]:
        """Analyze correlations between different error types
        
        Returns:
            List of correlation patterns
        """
        try:
            correlations = []
            error_sequence = [
                error.error_type for error in self.error_history
            ]
            
            # Look for patterns of length 2
            for i in range(len(error_sequence) - 1):
                pattern = (error_sequence[i], error_sequence[i + 1])
                count = sum(
                    1 for j in range(len(error_sequence) - 1)
                    if (error_sequence[j], error_sequence[j + 1]) == pattern
                )
                
                if count > 1:
                    correlations.append({
                        "pattern": pattern,
                        "count": count,
                        "confidence": count / (len(error_sequence) - 1)
                    })
                    
            # Sort by confidence
            correlations.sort(key=lambda x: x["confidence"], reverse=True)
            return correlations
            
        except Exception as e:
            logger.error(f"Error correlation analysis failed: {str(e)}")
            return []
            
    def analyze_error_context(self, error_id: str) -> Dict[str, Any]:
        """Analyze context of a specific error
        
        Args:
            error_id: ID of the error to analyze
            
        Returns:
            Dictionary containing context analysis
        """
        try:
            error = next(
                (e for e in self.error_history if e.error_id == error_id),
                None
            )
            
            if not error:
                return {}
                
            context = {
                "error_details": {
                    "type": error.error_type,
                    "message": error.message,
                    "timestamp": error.timestamp.isoformat(),
                    "source_file": error.source_file,
                    "line_number": error.line_number,
                    "function_name": error.function_name
                },
                "variable_analysis": self._analyze_variables(error),
                "stack_trace_analysis": self._analyze_stack_trace(error),
                "system_state_analysis": self._analyze_system_state(error)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error context analysis failed: {str(e)}")
            return {}
            
    def _analyze_variables(self, error: ErrorContext) -> Dict[str, Any]:
        """Analyze variables in error context
        
        Args:
            error: Error context to analyze
            
        Returns:
            Dictionary containing variable analysis
        """
        analysis = {
            "local_vars": {},
            "global_vars": {},
            "type_distribution": defaultdict(int),
            "null_values": [],
            "undefined_vars": []
        }
        
        if error.local_vars:
            for name, value in error.local_vars.items():
                analysis["local_vars"][name] = {
                    "type": type(value).__name__,
                    "value": str(value)
                }
                analysis["type_distribution"][type(value).__name__] += 1
                if value is None:
                    analysis["null_values"].append(name)
                    
        if error.global_vars:
            for name, value in error.global_vars.items():
                analysis["global_vars"][name] = {
                    "type": type(value).__name__,
                    "value": str(value)
                }
                
        return analysis
        
    def _analyze_stack_trace(self, error: ErrorContext) -> Dict[str, Any]:
        """Analyze stack trace
        
        Args:
            error: Error context to analyze
            
        Returns:
            Dictionary containing stack trace analysis
        """
        analysis = {
            "depth": 0,
            "function_calls": [],
            "module_sequence": [],
            "common_functions": defaultdict(int)
        }
        
        if error.stack_trace:
            lines = error.stack_trace.split('\n')
            analysis["depth"] = len([l for l in lines if l.strip().startswith('  File')])
            
            for line in lines:
                if line.strip().startswith('  File'):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        module = parts[0].split('"')[1]
                        function = parts[1].strip()
                        analysis["module_sequence"].append(module)
                        analysis["function_calls"].append(function)
                        analysis["common_functions"][function] += 1
                        
        return analysis
        
    def _analyze_system_state(self, error: ErrorContext) -> Dict[str, Any]:
        """Analyze system state at error time
        
        Args:
            error: Error context to analyze
            
        Returns:
            Dictionary containing system state analysis
        """
        analysis = {
            "resource_usage": {},
            "environment_vars": {},
            "system_metrics": {}
        }
        
        if error.system_state:
            if "resource_usage" in error.system_state:
                analysis["resource_usage"] = error.system_state["resource_usage"]
            if "environment_vars" in error.system_state:
                analysis["environment_vars"] = error.system_state["environment_vars"]
            if "system_metrics" in error.system_state:
                analysis["system_metrics"] = error.system_state["system_metrics"]
                
        return analysis 