from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from collections import defaultdict
from .error_collector import ErrorEvent, ErrorSeverity
from .pattern_detector import PatternDetector, ErrorPattern, WorkflowPattern
from .solution_repository import SolutionRepository

@dataclass
class RiskAssessment:
    risk_level: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    potential_errors: List[str]
    recommended_actions: List[str]
    preventive_solutions: List[str]

@dataclass
class UserProfile:
    user_id: str
    expertise_level: float  # 0.0 to 1.0
    error_history: List[str]
    success_patterns: List[str]
    learning_rate: float
    last_activity: datetime

class PreventiveAdvisor:
    def __init__(
        self,
        pattern_detector: PatternDetector,
        solution_repository: SolutionRepository,
        min_confidence: float = 0.7
    ):
        self.pattern_detector = pattern_detector
        self.solution_repository = solution_repository
        self.min_confidence = min_confidence
        self.user_profiles: Dict[str, UserProfile] = {}
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }

    def assess_risk(
        self,
        current_action: Dict[str, Any],
        user_id: str,
        context: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess the risk of potential errors for the current action"""
        # Get user profile
        user_profile = self._get_or_create_user_profile(user_id)
        
        # Analyze current action against known patterns
        error_patterns = self._find_relevant_error_patterns(current_action)
        workflow_patterns = self._find_relevant_workflow_patterns(current_action)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(
            error_patterns,
            workflow_patterns,
            user_profile
        )
        
        # Get preventive solutions
        preventive_solutions = self._find_preventive_solutions(
            error_patterns,
            user_profile
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level,
            error_patterns,
            workflow_patterns,
            user_profile
        )
        
        return RiskAssessment(
            risk_level=risk_level,
            confidence=self._calculate_confidence(
                error_patterns,
                workflow_patterns
            ),
            potential_errors=[p.error_type for p in error_patterns],
            recommended_actions=recommendations,
            preventive_solutions=preventive_solutions
        )

    def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create a user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                expertise_level=0.5,  # Default to medium expertise
                error_history=[],
                success_patterns=[],
                learning_rate=0.1,  # Default learning rate
                last_activity=datetime.utcnow()
            )
        return self.user_profiles[user_id]

    def _find_relevant_error_patterns(
        self,
        current_action: Dict[str, Any]
    ) -> List[ErrorPattern]:
        """Find error patterns relevant to the current action"""
        relevant_patterns = []
        action_type = current_action.get("type", "")
        action_context = current_action.get("context", {})
        
        for pattern in self.pattern_detector.error_patterns.values():
            # Check if pattern is relevant based on action type and context
            if self._is_pattern_relevant(pattern, action_type, action_context):
                relevant_patterns.append(pattern)
        
        return relevant_patterns

    def _find_relevant_workflow_patterns(
        self,
        current_action: Dict[str, Any]
    ) -> List[WorkflowPattern]:
        """Find workflow patterns relevant to the current action"""
        relevant_patterns = []
        action_type = current_action.get("type", "")
        
        for pattern in self.pattern_detector.workflow_patterns.values():
            # Check if pattern is relevant based on action type
            if action_type in pattern.sequence:
                relevant_patterns.append(pattern)
        
        return relevant_patterns

    def _is_pattern_relevant(
        self,
        pattern: ErrorPattern,
        action_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """Check if an error pattern is relevant to the current action"""
        # Check component relevance
        if pattern.component_distribution:
            relevant_components = [
                comp for comp, count in pattern.component_distribution.items()
                if count > 0
            ]
            if action_type in relevant_components:
                return True
        
        # Check context relevance
        if context:
            for key, value in context.items():
                if key in pattern.metadata:
                    return True
        
        return False

    def _calculate_risk_level(
        self,
        error_patterns: List[ErrorPattern],
        workflow_patterns: List[WorkflowPattern],
        user_profile: UserProfile
    ) -> float:
        """Calculate the overall risk level"""
        if not error_patterns and not workflow_patterns:
            return 0.0
        
        # Calculate base risk from error patterns
        error_risk = 0.0
        if error_patterns:
            error_risk = np.mean([
                self._calculate_pattern_risk(pattern)
                for pattern in error_patterns
            ])
        
        # Calculate workflow risk
        workflow_risk = 0.0
        if workflow_patterns:
            workflow_risk = np.mean([
                1.0 - pattern.success_rate
                for pattern in workflow_patterns
            ])
        
        # Adjust risk based on user expertise
        expertise_factor = 1.0 - user_profile.expertise_level
        
        # Combine risks with weights
        return (
            0.6 * error_risk +
            0.4 * workflow_risk
        ) * expertise_factor

    def _calculate_pattern_risk(self, pattern: ErrorPattern) -> float:
        """Calculate risk level for a specific error pattern"""
        # Base risk on severity distribution
        severity_weights = {
            ErrorSeverity.CRITICAL.value: 1.0,
            ErrorSeverity.HIGH.value: 0.8,
            ErrorSeverity.MEDIUM.value: 0.6,
            ErrorSeverity.LOW.value: 0.4,
            ErrorSeverity.INFO.value: 0.2
        }
        
        total_weight = sum(pattern.severity_distribution.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            severity_weights.get(severity, 0.0) * count
            for severity, count in pattern.severity_distribution.items()
        )
        
        return weighted_sum / total_weight

    def _find_preventive_solutions(
        self,
        error_patterns: List[ErrorPattern],
        user_profile: UserProfile
    ) -> List[str]:
        """Find preventive solutions for potential errors"""
        solutions = []
        for pattern in error_patterns:
            # Find solutions for the error pattern
            pattern_solutions = self.solution_repository.find_solutions(
                pattern.pattern_id,
                min_confidence=self.min_confidence
            )
            
            # Filter solutions based on user expertise
            for solution in pattern_solutions:
                if self._is_solution_appropriate(solution, user_profile):
                    solutions.append(solution.solution_id)
        
        return solutions

    def _is_solution_appropriate(
        self,
        solution: Any,
        user_profile: UserProfile
    ) -> bool:
        """Check if a solution is appropriate for the user's expertise level"""
        # Adjust solution complexity based on user expertise
        complexity_threshold = 0.5 + (1.0 - user_profile.expertise_level) * 0.5
        
        # Consider solution confidence and success rate
        solution_score = (
            solution.confidence_score * 0.6 +
            solution.success_rate * 0.4
        )
        
        return solution_score >= complexity_threshold

    def _generate_recommendations(
        self,
        risk_level: float,
        error_patterns: List[ErrorPattern],
        workflow_patterns: List[WorkflowPattern],
        user_profile: UserProfile
    ) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        # Add severity-based recommendations
        if risk_level >= self.risk_thresholds["high"]:
            recommendations.append("Consider reviewing the action with a team member")
            recommendations.append("Take a backup before proceeding")
        elif risk_level >= self.risk_thresholds["medium"]:
            recommendations.append("Double-check all inputs and parameters")
            recommendations.append("Review similar successful workflows")
        
        # Add pattern-specific recommendations
        for pattern in error_patterns:
            recommendations.extend(self._get_pattern_recommendations(pattern))
        
        # Add workflow-based recommendations
        for pattern in workflow_patterns:
            if pattern.success_rate < 0.7:
                recommendations.append(f"Follow the established workflow for {pattern.sequence[-1]}")
        
        # Adjust recommendations based on user expertise
        if user_profile.expertise_level < 0.5:
            recommendations.append("Consider following the step-by-step guide")
        
        return list(set(recommendations))  # Remove duplicates

    def _get_pattern_recommendations(self, pattern: ErrorPattern) -> List[str]:
        """Get specific recommendations for an error pattern"""
        recommendations = []
        
        # Add severity-based recommendations
        if ErrorSeverity.CRITICAL.value in pattern.severity_distribution:
            recommendations.append("Ensure all safety checks are in place")
        if ErrorSeverity.HIGH.value in pattern.severity_distribution:
            recommendations.append("Review error handling procedures")
        
        # Add component-specific recommendations
        for component, count in pattern.component_distribution.items():
            if count > 0:
                recommendations.append(f"Verify {component} configuration")
        
        return recommendations

    def _calculate_confidence(
        self,
        error_patterns: List[ErrorPattern],
        workflow_patterns: List[WorkflowPattern]
    ) -> float:
        """Calculate confidence in the risk assessment"""
        if not error_patterns and not workflow_patterns:
            return 0.0
        
        # Calculate confidence from pattern confidence scores
        pattern_confidence = 0.0
        if error_patterns:
            pattern_confidence = np.mean([
                pattern.confidence_score
                for pattern in error_patterns
            ])
        
        # Calculate confidence from workflow patterns
        workflow_confidence = 0.0
        if workflow_patterns:
            workflow_confidence = np.mean([
                pattern.confidence_score
                for pattern in workflow_patterns
            ])
        
        # Combine confidences with weights
        return (
            0.6 * pattern_confidence +
            0.4 * workflow_confidence
        )

    def update_user_profile(
        self,
        user_id: str,
        action_success: bool,
        error_occurred: bool,
        error_type: Optional[str] = None
    ):
        """Update user profile based on action outcome"""
        if user_id not in self.user_profiles:
            return
        
        profile = self.user_profiles[user_id]
        profile.last_activity = datetime.utcnow()
        
        # Update error history
        if error_occurred and error_type:
            profile.error_history.append(error_type)
            if len(profile.error_history) > 100:  # Keep last 100 errors
                profile.error_history.pop(0)
        
        # Update success patterns
        if action_success:
            profile.success_patterns.append(error_type or "general_success")
            if len(profile.success_patterns) > 100:  # Keep last 100 successes
                profile.success_patterns.pop(0)
        
        # Update expertise level based on success rate
        success_rate = len(profile.success_patterns) / (
            len(profile.success_patterns) + len(profile.error_history)
        ) if (profile.success_patterns or profile.error_history) else 0.5
        
        # Smooth expertise level update
        profile.expertise_level = (
            (1 - profile.learning_rate) * profile.expertise_level +
            profile.learning_rate * success_rate
        ) 