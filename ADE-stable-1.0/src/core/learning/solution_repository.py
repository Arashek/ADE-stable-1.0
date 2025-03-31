from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import hashlib
from .error_collector import ErrorEvent
from .pattern_detector import ErrorPattern

@dataclass
class Solution:
    solution_id: str
    error_pattern_id: str
    description: str
    steps: List[str]
    success_rate: float
    confidence_score: float
    created_at: datetime
    last_used: datetime
    usage_count: int
    tags: List[str]
    metadata: Dict[str, Any]

class SolutionRepository:
    def __init__(self, storage_path: str = "data/solutions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.solutions: Dict[str, Solution] = {}
        self._load_solutions()

    def _load_solutions(self):
        """Load all solutions from storage"""
        for solution_file in self.storage_path.glob("*.json"):
            with open(solution_file, "r") as f:
                data = json.load(f)
                solution = Solution(
                    solution_id=data["solution_id"],
                    error_pattern_id=data["error_pattern_id"],
                    description=data["description"],
                    steps=data["steps"],
                    success_rate=data["success_rate"],
                    confidence_score=data["confidence_score"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_used=datetime.fromisoformat(data["last_used"]),
                    usage_count=data["usage_count"],
                    tags=data["tags"],
                    metadata=data["metadata"]
                )
                self.solutions[solution.solution_id] = solution

    def add_solution(
        self,
        error_pattern_id: str,
        description: str,
        steps: List[str],
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Solution:
        """Add a new solution to the repository"""
        solution_id = self._generate_solution_id(error_pattern_id, steps)
        
        solution = Solution(
            solution_id=solution_id,
            error_pattern_id=error_pattern_id,
            description=description,
            steps=steps,
            success_rate=1.0,
            confidence_score=0.5,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            usage_count=0,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.solutions[solution_id] = solution
        self._save_solution(solution)
        return solution

    def find_solutions(
        self,
        error_pattern_id: str,
        min_confidence: float = 0.5,
        min_success_rate: float = 0.7
    ) -> List[Solution]:
        """Find solutions for a given error pattern"""
        return [
            solution for solution in self.solutions.values()
            if solution.error_pattern_id == error_pattern_id
            and solution.confidence_score >= min_confidence
            and solution.success_rate >= min_success_rate
        ]

    def update_solution_stats(
        self,
        solution_id: str,
        success: bool,
        feedback: Optional[Dict[str, Any]] = None
    ):
        """Update solution statistics based on usage"""
        if solution_id not in self.solutions:
            return

        solution = self.solutions[solution_id]
        solution.usage_count += 1
        solution.last_used = datetime.utcnow()
        
        # Update success rate using exponential moving average
        alpha = 0.1  # Learning rate
        solution.success_rate = (
            (1 - alpha) * solution.success_rate +
            alpha * (1.0 if success else 0.0)
        )
        
        # Update confidence score based on usage and success rate
        solution.confidence_score = self._calculate_confidence_score(solution)
        
        # Update metadata with feedback if provided
        if feedback:
            solution.metadata.update(feedback)
        
        self._save_solution(solution)

    def _calculate_confidence_score(self, solution: Solution) -> float:
        """Calculate confidence score for a solution"""
        # Base confidence on usage count and success rate
        usage_factor = min(solution.usage_count / 100, 1.0)  # Cap at 100 uses
        return (usage_factor + solution.success_rate) / 2

    def _generate_solution_id(self, error_pattern_id: str, steps: List[str]) -> str:
        """Generate a unique solution ID"""
        # Create a hash of the error pattern and steps
        content = f"{error_pattern_id}:{':'.join(steps)}"
        return f"SOL_{hashlib.sha256(content.encode()).hexdigest()[:8]}"

    def _save_solution(self, solution: Solution):
        """Save a solution to storage"""
        solution_file = self.storage_path / f"{solution.solution_id}.json"
        with open(solution_file, "w") as f:
            json.dump({
                "solution_id": solution.solution_id,
                "error_pattern_id": solution.error_pattern_id,
                "description": solution.description,
                "steps": solution.steps,
                "success_rate": solution.success_rate,
                "confidence_score": solution.confidence_score,
                "created_at": solution.created_at.isoformat(),
                "last_used": solution.last_used.isoformat(),
                "usage_count": solution.usage_count,
                "tags": solution.tags,
                "metadata": solution.metadata
            }, f)

    def get_solution_insights(self) -> Dict[str, Any]:
        """Get insights about the solution repository"""
        return {
            "total_solutions": len(self.solutions),
            "solutions_by_pattern": self._aggregate_solutions_by_pattern(),
            "top_solutions": self._get_top_solutions(),
            "solution_effectiveness": self._calculate_solution_effectiveness()
        }

    def _aggregate_solutions_by_pattern(self) -> Dict[str, int]:
        """Aggregate solutions by error pattern"""
        aggregation = {}
        for solution in self.solutions.values():
            aggregation[solution.error_pattern_id] = aggregation.get(solution.error_pattern_id, 0) + 1
        return aggregation

    def _get_top_solutions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing solutions"""
        return sorted(
            [
                {
                    "solution_id": solution.solution_id,
                    "error_pattern_id": solution.error_pattern_id,
                    "success_rate": solution.success_rate,
                    "confidence_score": solution.confidence_score,
                    "usage_count": solution.usage_count
                }
                for solution in self.solutions.values()
            ],
            key=lambda x: x["success_rate"] * x["confidence_score"],
            reverse=True
        )[:limit]

    def _calculate_solution_effectiveness(self) -> Dict[str, float]:
        """Calculate overall solution effectiveness metrics"""
        if not self.solutions:
            return {
                "average_success_rate": 0.0,
                "average_confidence": 0.0,
                "solution_coverage": 0.0
            }

        return {
            "average_success_rate": sum(s.success_rate for s in self.solutions.values()) / len(self.solutions),
            "average_confidence": sum(s.confidence_score for s in self.solutions.values()) / len(self.solutions),
            "solution_coverage": len(set(s.error_pattern_id for s in self.solutions.values()))
        }

    def validate_solution(self, solution_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a solution against test cases"""
        if solution_id not in self.solutions:
            return {"valid": False, "error": "Solution not found"}

        solution = self.solutions[solution_id]
        results = []

        for test_case in test_cases:
            # Simulate solution application
            success = self._simulate_solution_application(solution, test_case)
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

    def _simulate_solution_application(
        self,
        solution: Solution,
        test_case: Dict[str, Any]
    ) -> bool:
        """Simulate applying a solution to a test case"""
        # This is a placeholder for actual solution application logic
        # In a real implementation, this would execute the solution steps
        # and verify the expected outcomes
        return True  # Placeholder return 