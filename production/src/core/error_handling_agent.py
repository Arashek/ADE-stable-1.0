import logging
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from .agent import Agent
from .agent_communication import Message, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ErrorInfo:
    """Represents information about an error."""
    error_id: str
    error_type: str
    message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"
    status: str = "new"
    resolution: Optional[str] = None
    resolution_time: Optional[datetime] = None

class ErrorHandlingAgent(Agent):
    """Agent specialized in error detection, analysis, and recovery."""
    
    def __init__(self, agent_id: str = "error_handler",
                 name: str = "Error Handling Agent",
                 config_path: Optional[str] = None):
        """Initialize the error handling agent."""
        super().__init__(
            agent_id=agent_id,
            name=name,
            capabilities=[
                "error_detection",
                "error_analysis",
                "error_recovery",
                "error_prevention",
                "error_reporting",
                "pattern_recognition"
            ],
            config_path=config_path
        )
        
        # Initialize error tracking
        self.errors: Dict[str, ErrorInfo] = {}
        self.error_patterns: Dict[str, List[str]] = {}
        self.recovery_strategies: Dict[str, List[Dict[str, Any]]] = {}
        
        # Error handling settings
        self.settings = {
            "auto_recover": True,
            "pattern_analysis": True,
            "max_retries": 3,
            "retry_delay": 5.0,  # seconds
            "pattern_threshold": 3  # Minimum occurrences for pattern recognition
        }

    def _process_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Process an error handling task."""
        try:
            task_type = task_data.get("task_type")
            
            if task_type == "handle_error":
                self._handle_error(task_data.get("error_info"))
            elif task_type == "analyze_patterns":
                self._analyze_error_patterns()
            elif task_type == "suggest_recovery":
                self._suggest_recovery_strategy(task_data.get("error_id"))
            elif task_type == "prevent_errors":
                self._prevent_errors(task_data.get("target_agent"))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.complete_task(task_id, True, {"status": "completed"})
            
        except Exception as e:
            self._handle_error(e, task_id)
            self.complete_task(task_id, False, {"error": str(e)})

    def _handle_error(self, error_info: Dict[str, Any]) -> None:
        """Handle an error and attempt recovery."""
        try:
            # Create error info object
            error = ErrorInfo(
                error_id=error_info.get("error_id", str(time.time())),
                error_type=error_info.get("error_type", "unknown"),
                message=error_info.get("message", "Unknown error"),
                stack_trace=error_info.get("stack_trace"),
                context=error_info.get("context", {}),
                severity=self._determine_severity(error_info)
            )
            
            # Store error
            self.errors[error.error_id] = error
            
            # Analyze error
            analysis = self._analyze_error(error)
            
            # Attempt recovery if enabled
            if self.settings["auto_recover"]:
                self._attempt_recovery(error, analysis)
            
            # Update error patterns
            if self.settings["pattern_analysis"]:
                self._update_error_patterns(error)
            
            # Broadcast error status
            self._broadcast_error_status(error)
            
        except Exception as e:
            self._handle_error(e, "error_handling")

    def _analyze_error_patterns(self) -> None:
        """Analyze patterns in error occurrences."""
        try:
            # Group errors by type
            error_groups = self._group_errors_by_type()
            
            # Identify patterns
            patterns = self._identify_patterns(error_groups)
            
            # Generate prevention recommendations
            recommendations = self._generate_prevention_recommendations(patterns)
            
            # Broadcast pattern analysis
            self._broadcast_pattern_analysis(patterns, recommendations)
            
        except Exception as e:
            self._handle_error(e, "pattern_analysis")

    def _suggest_recovery_strategy(self, error_id: str) -> None:
        """Suggest a recovery strategy for an error."""
        try:
            if error_id not in self.errors:
                raise ValueError(f"Error {error_id} not found")
            
            error = self.errors[error_id]
            
            # Find similar errors
            similar_errors = self._find_similar_errors(error)
            
            # Analyze successful recovery strategies
            strategies = self._analyze_recovery_strategies(similar_errors)
            
            # Generate recommendation
            recommendation = self._generate_recovery_recommendation(
                error, similar_errors, strategies
            )
            
            # Broadcast recommendation
            self._broadcast_recovery_recommendation(error_id, recommendation)
            
        except Exception as e:
            self._handle_error(e, "recovery_strategy")

    def _prevent_errors(self, target_agent: str) -> None:
        """Prevent potential errors based on patterns."""
        try:
            # Analyze potential risks
            risks = self._analyze_potential_risks(target_agent)
            
            # Generate prevention measures
            measures = self._generate_prevention_measures(risks)
            
            # Apply prevention measures
            if measures:
                self._apply_prevention_measures(target_agent, measures)
            
            # Broadcast prevention status
            self._broadcast_prevention_status(target_agent, measures)
            
        except Exception as e:
            self._handle_error(e, "error_prevention")

    def _determine_severity(self, error_info: Dict[str, Any]) -> str:
        """Determine error severity."""
        # Check for critical keywords
        critical_keywords = ["fatal", "critical", "crash", "system failure"]
        message = error_info.get("message", "").lower()
        
        if any(keyword in message for keyword in critical_keywords):
            return "critical"
        
        # Check for error type
        error_type = error_info.get("error_type", "").lower()
        if error_type in ["system_error", "runtime_error", "fatal_error"]:
            return "high"
        
        # Check for impact
        context = error_info.get("context", {})
        if context.get("impact", "").lower() == "high":
            return "high"
        
        return "medium"

    def _analyze_error(self, error: ErrorInfo) -> Dict[str, Any]:
        """Analyze an error for root cause and impact."""
        analysis = {
            "root_cause": self._identify_root_cause(error),
            "impact": self._assess_impact(error),
            "similar_errors": self._find_similar_errors(error),
            "recovery_options": self._identify_recovery_options(error)
        }
        
        return analysis

    def _identify_root_cause(self, error: ErrorInfo) -> str:
        """Identify the root cause of an error."""
        # Analyze stack trace if available
        if error.stack_trace:
            # Look for common error patterns in stack trace
            if "NullPointerException" in error.stack_trace:
                return "null_pointer"
            elif "IndexError" in error.stack_trace:
                return "index_error"
            elif "KeyError" in error.stack_trace:
                return "key_error"
        
        # Analyze error context
        context = error.context
        if context.get("resource_exhaustion"):
            return "resource_exhaustion"
        elif context.get("timeout"):
            return "timeout"
        elif context.get("connection_error"):
            return "connection_error"
        
        return "unknown"

    def _assess_impact(self, error: ErrorInfo) -> Dict[str, Any]:
        """Assess the impact of an error."""
        impact = {
            "severity": error.severity,
            "scope": "local",  # local, system, or global
            "affected_components": [],
            "recovery_time": "unknown",
            "data_loss": False
        }
        
        # Analyze context for impact details
        context = error.context
        if context.get("system_wide"):
            impact["scope"] = "system"
        if context.get("global_effect"):
            impact["scope"] = "global"
        if context.get("data_corruption"):
            impact["data_loss"] = True
        
        return impact

    def _find_similar_errors(self, error: ErrorInfo) -> List[ErrorInfo]:
        """Find similar errors in history."""
        similar_errors = []
        
        for historical_error in self.errors.values():
            if self._calculate_error_similarity(error, historical_error) > 0.7:
                similar_errors.append(historical_error)
        
        return similar_errors

    def _calculate_error_similarity(self, error1: ErrorInfo, 
                                  error2: ErrorInfo) -> float:
        """Calculate similarity between two errors."""
        similarity = 0.0
        
        # Compare error types
        if error1.error_type == error2.error_type:
            similarity += 0.4
        
        # Compare messages
        if error1.message == error2.message:
            similarity += 0.3
        
        # Compare stack traces
        if error1.stack_trace and error2.stack_trace:
            if error1.stack_trace == error2.stack_trace:
                similarity += 0.3
        
        return similarity

    def _identify_recovery_options(self, error: ErrorInfo) -> List[Dict[str, Any]]:
        """Identify possible recovery options."""
        options = []
        
        # Add standard recovery options based on error type
        if error.error_type == "connection_error":
            options.append({
                "type": "retry",
                "description": "Retry the connection",
                "success_rate": 0.7
            })
        elif error.error_type == "resource_exhaustion":
            options.append({
                "type": "cleanup",
                "description": "Clean up unused resources",
                "success_rate": 0.8
            })
        
        # Add options based on similar errors
        similar_errors = self._find_similar_errors(error)
        for similar_error in similar_errors:
            if similar_error.resolution:
                options.append({
                    "type": "historical",
                    "description": f"Apply resolution from similar error: {similar_error.resolution}",
                    "success_rate": 0.9
                })
        
        return options

    def _attempt_recovery(self, error: ErrorInfo, 
                         analysis: Dict[str, Any]) -> None:
        """Attempt to recover from an error."""
        try:
            # Get recovery options
            options = analysis["recovery_options"]
            if not options:
                return
            
            # Try each option in order of success rate
            options.sort(key=lambda x: x["success_rate"], reverse=True)
            
            for option in options:
                if self._try_recovery_option(error, option):
                    # Update error status
                    error.status = "resolved"
                    error.resolution = option["description"]
                    error.resolution_time = datetime.now()
                    return
            
            # If no option succeeded
            error.status = "unresolved"
            
        except Exception as e:
            self._handle_error(e, "recovery_attempt")

    def _try_recovery_option(self, error: ErrorInfo, 
                           option: Dict[str, Any]) -> bool:
        """Try a specific recovery option."""
        try:
            if option["type"] == "retry":
                return self._retry_operation(error)
            elif option["type"] == "cleanup":
                return self._cleanup_resources(error)
            elif option["type"] == "historical":
                return self._apply_historical_solution(error, option)
            
            return False
            
        except Exception as e:
            self._handle_error(e, f"recovery_option_{option['type']}")
            return False

    def _retry_operation(self, error: ErrorInfo) -> bool:
        """Retry the failed operation."""
        # Implementation would depend on the specific operation
        return False

    def _cleanup_resources(self, error: ErrorInfo) -> bool:
        """Clean up resources to resolve the error."""
        # Implementation would depend on the specific resource type
        return False

    def _apply_historical_solution(self, error: ErrorInfo, 
                                 option: Dict[str, Any]) -> bool:
        """Apply a solution from a similar historical error."""
        # Implementation would depend on the specific solution
        return False

    def _update_error_patterns(self, error: ErrorInfo) -> None:
        """Update error pattern tracking."""
        pattern_key = f"{error.error_type}_{error.severity}"
        
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = []
        
        self.error_patterns[pattern_key].append(error.error_id)
        
        # Keep only recent errors for pattern analysis
        if len(self.error_patterns[pattern_key]) > 100:
            self.error_patterns[pattern_key].pop(0)

    def _group_errors_by_type(self) -> Dict[str, List[ErrorInfo]]:
        """Group errors by their type."""
        groups = {}
        
        for error in self.errors.values():
            if error.error_type not in groups:
                groups[error.error_type] = []
            groups[error.error_type].append(error)
        
        return groups

    def _identify_patterns(self, error_groups: Dict[str, List[ErrorInfo]]) -> Dict[str, Any]:
        """Identify patterns in error groups."""
        patterns = {}
        
        for error_type, errors in error_groups.items():
            if len(errors) >= self.settings["pattern_threshold"]:
                patterns[error_type] = {
                    "frequency": len(errors),
                    "common_causes": self._find_common_causes(errors),
                    "successful_recoveries": self._count_successful_recoveries(errors)
                }
        
        return patterns

    def _find_common_causes(self, errors: List[ErrorInfo]) -> List[str]:
        """Find common root causes among errors."""
        causes = {}
        
        for error in errors:
            cause = self._identify_root_cause(error)
            causes[cause] = causes.get(cause, 0) + 1
        
        # Sort by frequency
        return sorted(causes.items(), key=lambda x: x[1], reverse=True)

    def _count_successful_recoveries(self, errors: List[ErrorInfo]) -> int:
        """Count successful recoveries among errors."""
        return sum(1 for error in errors if error.status == "resolved")

    def _generate_prevention_recommendations(self, 
                                          patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations to prevent errors."""
        recommendations = []
        
        for error_type, pattern in patterns.items():
            if pattern["frequency"] > self.settings["pattern_threshold"]:
                recommendations.append({
                    "error_type": error_type,
                    "recommendation": self._generate_recommendation_for_pattern(
                        error_type, pattern
                    ),
                    "priority": "high" if pattern["frequency"] > 10 else "medium"
                })
        
        return recommendations

    def _generate_recommendation_for_pattern(self, error_type: str, 
                                          pattern: Dict[str, Any]) -> str:
        """Generate a specific recommendation for an error pattern."""
        if pattern["successful_recoveries"] / pattern["frequency"] > 0.7:
            return f"Implement automatic recovery for {error_type} errors"
        else:
            return f"Investigate and fix root causes of {error_type} errors"

    def _analyze_potential_risks(self, target_agent: str) -> List[Dict[str, Any]]:
        """Analyze potential risks for an agent."""
        risks = []
        
        # Check error history
        agent_errors = [
            error for error in self.errors.values()
            if error.context.get("agent_id") == target_agent
        ]
        
        if agent_errors:
            # Analyze error patterns
            patterns = self._identify_patterns(
                self._group_errors_by_type()
            )
            
            # Generate risk assessments
            for error_type, pattern in patterns.items():
                if pattern["frequency"] > 0:
                    risks.append({
                        "type": error_type,
                        "probability": pattern["frequency"] / len(agent_errors),
                        "impact": "high" if pattern["frequency"] > 5 else "medium"
                    })
        
        return risks

    def _generate_prevention_measures(self, 
                                   risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate measures to prevent identified risks."""
        measures = []
        
        for risk in risks:
            if risk["probability"] > 0.3:  # 30% threshold
                measures.append({
                    "risk_type": risk["type"],
                    "measure": self._generate_measure_for_risk(risk),
                    "priority": risk["impact"]
                })
        
        return measures

    def _generate_measure_for_risk(self, risk: Dict[str, Any]) -> str:
        """Generate a specific prevention measure for a risk."""
        if risk["type"] == "connection_error":
            return "Implement connection pooling and retry mechanism"
        elif risk["type"] == "resource_exhaustion":
            return "Implement resource monitoring and automatic cleanup"
        else:
            return f"Add error handling and recovery for {risk['type']}"

    def _apply_prevention_measures(self, target_agent: str, 
                                 measures: List[Dict[str, Any]]) -> None:
        """Apply prevention measures for an agent."""
        for measure in measures:
            # Implementation would depend on the specific measure
            pass

    def _broadcast_error_status(self, error: ErrorInfo) -> None:
        """Broadcast error status update."""
        status_data = {
            "error_id": error.error_id,
            "error_type": error.error_type,
            "severity": error.severity,
            "status": error.status,
            "timestamp": error.timestamp.isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "error_status", "data": status_data}
        )

    def _broadcast_pattern_analysis(self, patterns: Dict[str, Any], 
                                  recommendations: List[Dict[str, Any]]) -> None:
        """Broadcast error pattern analysis."""
        analysis_data = {
            "patterns": patterns,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "pattern_analysis", "data": analysis_data}
        )

    def _broadcast_recovery_recommendation(self, error_id: str, 
                                         recommendation: Dict[str, Any]) -> None:
        """Broadcast recovery strategy recommendation."""
        recommendation_data = {
            "error_id": error_id,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "recovery_recommendation", "data": recommendation_data}
        )

    def _broadcast_prevention_status(self, target_agent: str, 
                                   measures: List[Dict[str, Any]]) -> None:
        """Broadcast error prevention status."""
        prevention_data = {
            "target_agent": target_agent,
            "measures": measures,
            "timestamp": datetime.now().isoformat()
        }
        self.comm_system.broadcast_notification(
            self.agent_id,
            {"type": "prevention_status", "data": prevention_data}
        ) 