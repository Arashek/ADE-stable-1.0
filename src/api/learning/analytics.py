from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.core.learning.error_collector import ErrorCollector
from src.core.learning.pattern_detector import PatternDetector
from src.core.learning.solution_repository import SolutionRepository
from src.core.learning.fleet_learner import FleetLearner

router = APIRouter()

@router.get("/analytics")
async def get_learning_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    instance_id: Optional[str] = None
) -> Dict:
    """
    Get comprehensive learning analytics data for visualization.
    
    Args:
        start_date: Optional start date for filtering data (ISO format)
        end_date: Optional end date for filtering data (ISO format)
        instance_id: Optional instance ID for filtering data
        
    Returns:
        Dictionary containing analytics data for visualization
    """
    try:
        # Initialize components
        error_collector = ErrorCollector()
        pattern_detector = PatternDetector()
        solution_repository = SolutionRepository()
        fleet_learner = FleetLearner()

        # Parse date filters
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()

        # Get error patterns
        error_patterns = pattern_detector.get_pattern_insights()
        filtered_error_patterns = [
            pattern for pattern in error_patterns
            if start <= pattern.created_at <= end
        ]

        # Get workflow patterns
        workflow_patterns = pattern_detector.get_workflow_pattern_insights()
        filtered_workflow_patterns = [
            pattern for pattern in workflow_patterns
            if start <= pattern.created_at <= end
        ]

        # Get solutions
        solutions = solution_repository.get_solution_insights()
        filtered_solutions = [
            solution for solution in solutions
            if start <= solution.created_at <= end
        ]

        # Get fleet metrics
        fleet_metrics = fleet_learner.get_fleet_insights()
        if instance_id:
            fleet_metrics = {
                k: v for k, v in fleet_metrics.items()
                if k == "instance_metrics" or k == "learning_distribution"
            }

        # Prepare response data
        response_data = {
            "errorPatterns": [
                {
                    "error_type": pattern.error_type,
                    "frequency": pattern.frequency,
                    "severity": pattern.severity_distribution,
                    "component": pattern.component,
                    "timestamp": pattern.created_at.isoformat(),
                    "component_count": pattern.component_count
                }
                for pattern in filtered_error_patterns
            ],
            "workflowPatterns": [
                {
                    "sequence": pattern.sequence,
                    "success_rate": pattern.success_rate,
                    "error_rate": pattern.error_rate,
                    "average_duration": pattern.average_duration,
                    "frequency": pattern.frequency,
                    "timestamp": pattern.created_at.isoformat()
                }
                for pattern in filtered_workflow_patterns
            ],
            "solutions": [
                {
                    "solution_id": solution.solution_id,
                    "success_rate": solution.success_rate,
                    "confidence_score": solution.confidence_score,
                    "usage_count": solution.usage_count,
                    "type": solution.type,
                    "timestamp": solution.created_at.isoformat(),
                    "count": 1  # For pie chart aggregation
                }
                for solution in filtered_solutions
            ],
            "fleetMetrics": {
                "learning_history": [
                    {
                        "timestamp": entry["timestamp"].isoformat(),
                        "average_confidence": entry["average_confidence"],
                        "insight_diversity": entry["insight_diversity"],
                        "learning_rate": entry["learning_rate"]
                    }
                    for entry in fleet_metrics.get("learning_history", [])
                    if start <= entry["timestamp"] <= end
                ],
                "instance_metrics": [
                    {
                        "instance_id": instance["instance_id"],
                        "insight_count": instance["insight_count"],
                        "contribution_count": instance["contribution_count"]
                    }
                    for instance in fleet_metrics.get("instance_metrics", [])
                ],
                "learning_distribution": [
                    {
                        "type": dist["type"],
                        "count": dist["count"]
                    }
                    for dist in fleet_metrics.get("learning_distribution", [])
                ]
            }
        }

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics data: {str(e)}"
        )

@router.get("/analytics/error-patterns")
async def get_error_pattern_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Get detailed analytics for error patterns.
    
    Args:
        start_date: Optional start date for filtering data (ISO format)
        end_date: Optional end date for filtering data (ISO format)
        
    Returns:
        List of error pattern analytics data
    """
    try:
        error_collector = ErrorCollector()
        pattern_detector = PatternDetector()

        # Parse date filters
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()

        # Get error patterns
        error_patterns = pattern_detector.get_pattern_insights()
        filtered_patterns = [
            pattern for pattern in error_patterns
            if start <= pattern.created_at <= end
        ]

        return [
            {
                "error_type": pattern.error_type,
                "frequency": pattern.frequency,
                "severity": pattern.severity_distribution,
                "component": pattern.component,
                "timestamp": pattern.created_at.isoformat(),
                "component_count": pattern.component_count
            }
            for pattern in filtered_patterns
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate error pattern analytics: {str(e)}"
        )

@router.get("/analytics/workflow-patterns")
async def get_workflow_pattern_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Get detailed analytics for workflow patterns.
    
    Args:
        start_date: Optional start date for filtering data (ISO format)
        end_date: Optional end date for filtering data (ISO format)
        
    Returns:
        List of workflow pattern analytics data
    """
    try:
        pattern_detector = PatternDetector()

        # Parse date filters
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()

        # Get workflow patterns
        workflow_patterns = pattern_detector.get_workflow_pattern_insights()
        filtered_patterns = [
            pattern for pattern in workflow_patterns
            if start <= pattern.created_at <= end
        ]

        return [
            {
                "sequence": pattern.sequence,
                "success_rate": pattern.success_rate,
                "error_rate": pattern.error_rate,
                "average_duration": pattern.average_duration,
                "frequency": pattern.frequency,
                "timestamp": pattern.created_at.isoformat()
            }
            for pattern in filtered_patterns
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workflow pattern analytics: {str(e)}"
        )

@router.get("/analytics/solutions")
async def get_solution_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Get detailed analytics for solutions.
    
    Args:
        start_date: Optional start date for filtering data (ISO format)
        end_date: Optional end date for filtering data (ISO format)
        
    Returns:
        List of solution analytics data
    """
    try:
        solution_repository = SolutionRepository()

        # Parse date filters
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()

        # Get solutions
        solutions = solution_repository.get_solution_insights()
        filtered_solutions = [
            solution for solution in solutions
            if start <= solution.created_at <= end
        ]

        return [
            {
                "solution_id": solution.solution_id,
                "success_rate": solution.success_rate,
                "confidence_score": solution.confidence_score,
                "usage_count": solution.usage_count,
                "type": solution.type,
                "timestamp": solution.created_at.isoformat(),
                "count": 1  # For pie chart aggregation
            }
            for solution in filtered_solutions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate solution analytics: {str(e)}"
        )

@router.get("/analytics/fleet")
async def get_fleet_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    instance_id: Optional[str] = None
) -> Dict:
    """
    Get detailed analytics for fleet learning.
    
    Args:
        start_date: Optional start date for filtering data (ISO format)
        end_date: Optional end date for filtering data (ISO format)
        instance_id: Optional instance ID for filtering data
        
    Returns:
        Dictionary containing fleet learning analytics data
    """
    try:
        fleet_learner = FleetLearner()

        # Parse date filters
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()

        # Get fleet metrics
        fleet_metrics = fleet_learner.get_fleet_insights()
        if instance_id:
            fleet_metrics = {
                k: v for k, v in fleet_metrics.items()
                if k == "instance_metrics" or k == "learning_distribution"
            }

        return {
            "learning_history": [
                {
                    "timestamp": entry["timestamp"].isoformat(),
                    "average_confidence": entry["average_confidence"],
                    "insight_diversity": entry["insight_diversity"],
                    "learning_rate": entry["learning_rate"]
                }
                for entry in fleet_metrics.get("learning_history", [])
                if start <= entry["timestamp"] <= end
            ],
            "instance_metrics": [
                {
                    "instance_id": instance["instance_id"],
                    "insight_count": instance["insight_count"],
                    "contribution_count": instance["contribution_count"]
                }
                for instance in fleet_metrics.get("instance_metrics", [])
            ],
            "learning_distribution": [
                {
                    "type": dist["type"],
                    "count": dist["count"]
                }
                for dist in fleet_metrics.get("learning_distribution", [])
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fleet analytics: {str(e)}"
        ) 