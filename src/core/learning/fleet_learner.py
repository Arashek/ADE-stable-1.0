from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
from pathlib import Path
import numpy as np
from .error_collector import ErrorEvent
from .pattern_detector import PatternDetector, ErrorPattern, WorkflowPattern
from .solution_repository import SolutionRepository
from .preventive_advisor import PreventiveAdvisor

@dataclass
class FleetInsight:
    insight_id: str
    type: str  # "error_pattern", "workflow_pattern", "solution"
    content: Dict[str, Any]
    confidence: float
    source_instances: List[str]
    created_at: datetime
    last_updated: datetime
    usage_count: int

class FleetLearner:
    def __init__(
        self,
        instance_id: str,
        pattern_detector: PatternDetector,
        solution_repository: SolutionRepository,
        preventive_advisor: PreventiveAdvisor,
        storage_path: str = "data/fleet"
    ):
        self.instance_id = instance_id
        self.pattern_detector = pattern_detector
        self.solution_repository = solution_repository
        self.preventive_advisor = preventive_advisor
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.insights: Dict[str, FleetInsight] = {}
        self.known_instances: Set[str] = {instance_id}
        self._load_insights()

    def _load_insights(self):
        """Load all fleet insights from storage"""
        for insight_file in self.storage_path.glob("*.json"):
            with open(insight_file, "r") as f:
                data = json.load(f)
                insight = FleetInsight(
                    insight_id=data["insight_id"],
                    type=data["type"],
                    content=data["content"],
                    confidence=data["confidence"],
                    source_instances=data["source_instances"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_updated=datetime.fromisoformat(data["last_updated"]),
                    usage_count=data["usage_count"]
                )
                self.insights[insight.insight_id] = insight

    def share_insights(self) -> List[Dict[str, Any]]:
        """Share local insights with the fleet"""
        insights_to_share = []
        
        # Share error patterns
        for pattern in self.pattern_detector.error_patterns.values():
            if pattern.confidence_score >= 0.7:  # Only share high-confidence patterns
                insights_to_share.append(self._create_pattern_insight(pattern))
        
        # Share workflow patterns
        for pattern in self.pattern_detector.workflow_patterns.values():
            if pattern.confidence_score >= 0.7:  # Only share high-confidence patterns
                insights_to_share.append(self._create_workflow_insight(pattern))
        
        # Share solutions
        for solution in self.solution_repository.solutions.values():
            if solution.confidence_score >= 0.7:  # Only share high-confidence solutions
                insights_to_share.append(self._create_solution_insight(solution))
        
        return insights_to_share

    def receive_insights(self, insights: List[Dict[str, Any]], source_instance: str):
        """Receive and process insights from other instances"""
        self.known_instances.add(source_instance)
        
        for insight_data in insights:
            insight = FleetInsight(
                insight_id=insight_data["insight_id"],
                type=insight_data["type"],
                content=insight_data["content"],
                confidence=insight_data["confidence"],
                source_instances=[source_instance],
                created_at=datetime.fromisoformat(insight_data["created_at"]),
                last_updated=datetime.fromisoformat(insight_data["last_updated"]),
                usage_count=insight_data["usage_count"]
            )
            
            # Merge with existing insight if it exists
            if insight.insight_id in self.insights:
                self._merge_insights(self.insights[insight.insight_id], insight)
            else:
                self.insights[insight.insight_id] = insight
            
            self._save_insight(self.insights[insight.insight_id])

    def _create_pattern_insight(self, pattern: ErrorPattern) -> Dict[str, Any]:
        """Create a fleet insight from an error pattern"""
        return {
            "insight_id": f"EP_{hashlib.sha256(str(pattern).encode()).hexdigest()[:8]}",
            "type": "error_pattern",
            "content": {
                "error_type": pattern.error_type,
                "message_pattern": pattern.message_pattern,
                "stack_pattern": pattern.stack_pattern,
                "severity_distribution": pattern.severity_distribution,
                "component_distribution": pattern.component_distribution,
                "frequency": pattern.frequency,
                "first_seen": pattern.first_seen.isoformat(),
                "last_seen": pattern.last_seen.isoformat()
            },
            "confidence": pattern.confidence_score,
            "source_instances": [self.instance_id],
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "usage_count": pattern.frequency
        }

    def _create_workflow_insight(self, pattern: WorkflowPattern) -> Dict[str, Any]:
        """Create a fleet insight from a workflow pattern"""
        return {
            "insight_id": f"WP_{hashlib.sha256(str(pattern).encode()).hexdigest()[:8]}",
            "type": "workflow_pattern",
            "content": {
                "sequence": pattern.sequence,
                "success_rate": pattern.success_rate,
                "error_patterns": pattern.error_patterns,
                "average_duration": pattern.average_duration,
                "frequency": pattern.frequency
            },
            "confidence": pattern.confidence_score,
            "source_instances": [self.instance_id],
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "usage_count": pattern.frequency
        }

    def _create_solution_insight(self, solution: Any) -> Dict[str, Any]:
        """Create a fleet insight from a solution"""
        return {
            "insight_id": solution.solution_id,
            "type": "solution",
            "content": {
                "error_pattern_id": solution.error_pattern_id,
                "description": solution.description,
                "steps": solution.steps,
                "success_rate": solution.success_rate,
                "tags": solution.tags,
                "metadata": solution.metadata
            },
            "confidence": solution.confidence_score,
            "source_instances": [self.instance_id],
            "created_at": solution.created_at.isoformat(),
            "last_updated": solution.last_used.isoformat(),
            "usage_count": solution.usage_count
        }

    def _merge_insights(self, existing: FleetInsight, new: FleetInsight):
        """Merge a new insight with an existing one"""
        # Update source instances
        existing.source_instances.extend(new.source_instances)
        existing.source_instances = list(set(existing.source_instances))
        
        # Update confidence using weighted average
        total_usage = existing.usage_count + new.usage_count
        existing.confidence = (
            (existing.confidence * existing.usage_count +
             new.confidence * new.usage_count) /
            total_usage
        )
        
        # Update usage count
        existing.usage_count = total_usage
        
        # Update last updated timestamp
        existing.last_updated = datetime.utcnow()
        
        # Merge content based on type
        if existing.type == "error_pattern":
            self._merge_pattern_content(existing, new)
        elif existing.type == "workflow_pattern":
            self._merge_workflow_content(existing, new)
        elif existing.type == "solution":
            self._merge_solution_content(existing, new)

    def _merge_pattern_content(self, existing: FleetInsight, new: FleetInsight):
        """Merge content for error pattern insights"""
        # Merge severity distribution
        for severity, count in new.content["severity_distribution"].items():
            existing.content["severity_distribution"][severity] = (
                existing.content["severity_distribution"].get(severity, 0) + count
            )
        
        # Merge component distribution
        for component, count in new.content["component_distribution"].items():
            existing.content["component_distribution"][component] = (
                existing.content["component_distribution"].get(component, 0) + count
            )
        
        # Update frequency
        existing.content["frequency"] += new.content["frequency"]
        
        # Update timestamps
        existing.content["first_seen"] = min(
            existing.content["first_seen"],
            new.content["first_seen"]
        )
        existing.content["last_seen"] = max(
            existing.content["last_seen"],
            new.content["last_seen"]
        )

    def _merge_workflow_content(self, existing: FleetInsight, new: FleetInsight):
        """Merge content for workflow pattern insights"""
        # Update success rate using weighted average
        total_frequency = existing.content["frequency"] + new.content["frequency"]
        existing.content["success_rate"] = (
            (existing.content["success_rate"] * existing.content["frequency"] +
             new.content["success_rate"] * new.content["frequency"]) /
            total_frequency
        )
        
        # Update average duration
        existing.content["average_duration"] = (
            (existing.content["average_duration"] * existing.content["frequency"] +
             new.content["average_duration"] * new.content["frequency"]) /
            total_frequency
        )
        
        # Update frequency
        existing.content["frequency"] = total_frequency
        
        # Merge error patterns
        existing.content["error_patterns"].extend(new.content["error_patterns"])
        existing.content["error_patterns"] = list(set(existing.content["error_patterns"]))

    def _merge_solution_content(self, existing: FleetInsight, new: FleetInsight):
        """Merge content for solution insights"""
        # Update success rate using weighted average
        total_usage = existing.usage_count + new.usage_count
        existing.content["success_rate"] = (
            (existing.content["success_rate"] * existing.usage_count +
             new.content["success_rate"] * new.usage_count) /
            total_usage
        )
        
        # Merge tags
        existing.content["tags"].extend(new.content["tags"])
        existing.content["tags"] = list(set(existing.content["tags"]))
        
        # Merge metadata
        existing.content["metadata"].update(new.content["metadata"])

    def _save_insight(self, insight: FleetInsight):
        """Save a fleet insight to storage"""
        insight_file = self.storage_path / f"{insight.insight_id}.json"
        with open(insight_file, "w") as f:
            json.dump({
                "insight_id": insight.insight_id,
                "type": insight.type,
                "content": insight.content,
                "confidence": insight.confidence,
                "source_instances": insight.source_instances,
                "created_at": insight.created_at.isoformat(),
                "last_updated": insight.last_updated.isoformat(),
                "usage_count": insight.usage_count
            }, f)

    def get_fleet_insights(self) -> Dict[str, Any]:
        """Get insights about the fleet's learning"""
        return {
            "total_insights": len(self.insights),
            "insights_by_type": self._aggregate_insights_by_type(),
            "top_insights": self._get_top_insights(),
            "instance_coverage": len(self.known_instances),
            "learning_metrics": self._calculate_learning_metrics()
        }

    def _aggregate_insights_by_type(self) -> Dict[str, int]:
        """Aggregate insights by type"""
        aggregation = {}
        for insight in self.insights.values():
            aggregation[insight.type] = aggregation.get(insight.type, 0) + 1
        return aggregation

    def _get_top_insights(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing insights"""
        return sorted(
            [
                {
                    "insight_id": insight.insight_id,
                    "type": insight.type,
                    "confidence": insight.confidence,
                    "usage_count": insight.usage_count,
                    "source_instances": len(insight.source_instances)
                }
                for insight in self.insights.values()
            ],
            key=lambda x: x["confidence"] * x["usage_count"],
            reverse=True
        )[:limit]

    def _calculate_learning_metrics(self) -> Dict[str, float]:
        """Calculate learning metrics for the fleet"""
        if not self.insights:
            return {
                "average_confidence": 0.0,
                "insight_diversity": 0.0,
                "learning_rate": 0.0
            }
        
        # Calculate average confidence
        average_confidence = np.mean([i.confidence for i in self.insights.values()])
        
        # Calculate insight diversity (ratio of unique types)
        unique_types = len(set(i.type for i in self.insights.values()))
        insight_diversity = unique_types / len(self.insights)
        
        # Calculate learning rate (ratio of recent insights)
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_insights = sum(
            1 for i in self.insights.values()
            if i.last_updated > recent_cutoff
        )
        learning_rate = recent_insights / len(self.insights)
        
        return {
            "average_confidence": average_confidence,
            "insight_diversity": insight_diversity,
            "learning_rate": learning_rate
        }

    def validate_insight(self, insight_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a fleet insight against test cases"""
        if insight_id not in self.insights:
            return {"valid": False, "error": "Insight not found"}
        
        insight = self.insights[insight_id]
        results = []
        
        for test_case in test_cases:
            # Simulate insight application
            success = self._simulate_insight_application(insight, test_case)
            results.append({
                "test_case": test_case,
                "success": success
            })
        
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        return {
            "valid": success_rate >= 0.8,  # Require 80% success rate
            "success_rate": success_rate,
            "results": results
        }

    def _simulate_insight_application(
        self,
        insight: FleetInsight,
        test_case: Dict[str, Any]
    ) -> bool:
        """Simulate applying an insight to a test case"""
        # This is a placeholder for actual insight application logic
        # In a real implementation, this would apply the insight
        # and verify the expected outcomes
        return True  # Placeholder return 