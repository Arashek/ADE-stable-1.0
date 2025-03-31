from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

class EvaluationCriteria(Enum):
    # Code Quality
    CODE_QUALITY = "code_quality"
    CODE_STYLE = "code_style"
    CODE_COMPLEXITY = "code_complexity"
    CODE_MAINTAINABILITY = "code_maintainability"
    DOCUMENTATION = "documentation"
    
    # Performance
    TIME_COMPLEXITY = "time_complexity"
    SPACE_COMPLEXITY = "space_complexity"
    RESOURCE_USAGE = "resource_usage"
    SCALABILITY = "scalability"
    CONCURRENCY = "concurrency"
    
    # Security
    SECURITY_VULNERABILITIES = "security_vulnerabilities"
    INPUT_VALIDATION = "input_validation"
    AUTH_HANDLING = "auth_handling"
    DATA_PROTECTION = "data_protection"
    SECURE_DEFAULTS = "secure_defaults"
    
    # Architecture
    DESIGN_PATTERNS = "design_patterns"
    MODULARITY = "modularity"
    EXTENSIBILITY = "extensibility"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    API_DESIGN = "api_design"
    
    # Testing
    TEST_COVERAGE = "test_coverage"
    TEST_QUALITY = "test_quality"
    EDGE_CASES = "edge_cases"
    INTEGRATION_TESTS = "integration_tests"
    ERROR_HANDLING = "error_handling"
    
    # Business Value
    REQUIREMENT_FULFILLMENT = "requirement_fulfillment"
    USER_EXPERIENCE = "user_experience"
    BUSINESS_IMPACT = "business_impact"
    INNOVATION = "innovation"
    TIME_TO_MARKET = "time_to_market"

@dataclass
class WeightConfig:
    base_weight: float
    expertise_multiplier: float
    confidence_multiplier: float
    historical_performance_multiplier: float
    consensus_alignment_multiplier: float

class EvaluationManager:
    def __init__(self):
        self.criteria_weights = self._initialize_criteria_weights()
        self.historical_performance = {}
        self.consensus_history = {}
        
    def _initialize_criteria_weights(self) -> Dict[EvaluationCriteria, float]:
        """Initialize default weights for each criterion"""
        weights = {}
        # Code Quality Group (30%)
        weights.update({
            EvaluationCriteria.CODE_QUALITY: 0.08,
            EvaluationCriteria.CODE_STYLE: 0.05,
            EvaluationCriteria.CODE_COMPLEXITY: 0.07,
            EvaluationCriteria.CODE_MAINTAINABILITY: 0.06,
            EvaluationCriteria.DOCUMENTATION: 0.04
        })
        
        # Performance Group (20%)
        weights.update({
            EvaluationCriteria.TIME_COMPLEXITY: 0.05,
            EvaluationCriteria.SPACE_COMPLEXITY: 0.04,
            EvaluationCriteria.RESOURCE_USAGE: 0.04,
            EvaluationCriteria.SCALABILITY: 0.04,
            EvaluationCriteria.CONCURRENCY: 0.03
        })
        
        # Security Group (20%)
        weights.update({
            EvaluationCriteria.SECURITY_VULNERABILITIES: 0.05,
            EvaluationCriteria.INPUT_VALIDATION: 0.04,
            EvaluationCriteria.AUTH_HANDLING: 0.04,
            EvaluationCriteria.DATA_PROTECTION: 0.04,
            EvaluationCriteria.SECURE_DEFAULTS: 0.03
        })
        
        # Architecture Group (15%)
        weights.update({
            EvaluationCriteria.DESIGN_PATTERNS: 0.03,
            EvaluationCriteria.MODULARITY: 0.03,
            EvaluationCriteria.EXTENSIBILITY: 0.03,
            EvaluationCriteria.DEPENDENCY_MANAGEMENT: 0.03,
            EvaluationCriteria.API_DESIGN: 0.03
        })
        
        # Testing Group (10%)
        weights.update({
            EvaluationCriteria.TEST_COVERAGE: 0.02,
            EvaluationCriteria.TEST_QUALITY: 0.02,
            EvaluationCriteria.EDGE_CASES: 0.02,
            EvaluationCriteria.INTEGRATION_TESTS: 0.02,
            EvaluationCriteria.ERROR_HANDLING: 0.02
        })
        
        # Business Value Group (5%)
        weights.update({
            EvaluationCriteria.REQUIREMENT_FULFILLMENT: 0.01,
            EvaluationCriteria.USER_EXPERIENCE: 0.01,
            EvaluationCriteria.BUSINESS_IMPACT: 0.01,
            EvaluationCriteria.INNOVATION: 0.01,
            EvaluationCriteria.TIME_TO_MARKET: 0.01
        })
        
        return weights
        
    def evaluate_solution(self, 
                         solution: Dict[str, Any],
                         agent_expertise: Dict[str, float],
                         context: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a solution using weighted criteria"""
        scores = {}
        
        # Evaluate each criterion
        for criterion in EvaluationCriteria:
            score = self._evaluate_criterion(criterion, solution, context)
            weight = self._calculate_criterion_weight(
                criterion,
                agent_expertise.get(criterion.value, 0.5),
                solution.get('confidence', 0.5),
                self._get_historical_performance(solution['agent'], criterion)
            )
            scores[criterion.value] = score * weight
            
        return {
            'individual_scores': scores,
            'overall_score': sum(scores.values()),
            'weighted_confidence': self._calculate_weighted_confidence(solution, scores)
        }
        
    def _evaluate_criterion(self, 
                          criterion: EvaluationCriteria, 
                          solution: Dict[str, Any],
                          context: Dict[str, Any]) -> float:
        """Evaluate a specific criterion"""
        # Implement specific evaluation logic for each criterion
        if criterion == EvaluationCriteria.CODE_QUALITY:
            return self._evaluate_code_quality(solution['response'])
        elif criterion == EvaluationCriteria.SECURITY_VULNERABILITIES:
            return self._evaluate_security(solution['response'])
        # ... implement other criteria
        return 0.5  # Default score
        
    def _calculate_criterion_weight(self,
                                  criterion: EvaluationCriteria,
                                  expertise: float,
                                  confidence: float,
                                  historical_performance: float) -> float:
        """Calculate dynamic weight for a criterion"""
        base_weight = self.criteria_weights[criterion]
        weight_config = WeightConfig(
            base_weight=base_weight,
            expertise_multiplier=1.2,
            confidence_multiplier=1.1,
            historical_performance_multiplier=1.15,
            consensus_alignment_multiplier=1.1
        )
        
        # Apply multipliers
        dynamic_weight = base_weight
        dynamic_weight *= (1 + (expertise - 0.5) * weight_config.expertise_multiplier)
        dynamic_weight *= (1 + (confidence - 0.5) * weight_config.confidence_multiplier)
        dynamic_weight *= (1 + (historical_performance - 0.5) * 
                         weight_config.historical_performance_multiplier)
        
        return dynamic_weight
        
    def _get_historical_performance(self, 
                                  agent: str, 
                                  criterion: EvaluationCriteria) -> float:
        """Get agent's historical performance for a criterion"""
        if agent not in self.historical_performance:
            return 0.5
        return self.historical_performance[agent].get(criterion.value, 0.5)
        
    def _calculate_weighted_confidence(self,
                                    solution: Dict[str, Any],
                                    scores: Dict[str, float]) -> float:
        """Calculate weighted confidence score"""
        base_confidence = solution.get('confidence', 0.5)
        score_impact = sum(scores.values()) / len(scores)
        historical_impact = self._get_historical_performance(
            solution['agent'],
            EvaluationCriteria.CODE_QUALITY  # Use as general performance indicator
        )
        
        return (base_confidence * 0.4 + score_impact * 0.4 + historical_impact * 0.2)
        
    def update_historical_performance(self,
                                   agent: str,
                                   criterion: EvaluationCriteria,
                                   score: float):
        """Update agent's historical performance"""
        if agent not in self.historical_performance:
            self.historical_performance[agent] = {}
        
        current = self.historical_performance[agent].get(criterion.value, 0.5)
        # Exponential moving average
        alpha = 0.3  # Learning rate
        self.historical_performance[agent][criterion.value] = (
            alpha * score + (1 - alpha) * current
        )
        
    def _evaluate_code_quality(self, code: str) -> float:
        """Evaluate code quality using static analysis"""
        # Implement code quality metrics
        return 0.8
        
    def _evaluate_security(self, code: str) -> float:
        """Evaluate security aspects"""
        # Implement security analysis
        return 0.8
