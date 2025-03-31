from typing import Dict, List, Optional, Any, Set
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict

@dataclass
class ErrorPattern:
    """Represents a known error pattern."""
    pattern_type: str
    regex: str
    description: str
    severity: str
    category: str
    subcategory: str
    common_causes: List[str]
    solutions: List[str]
    examples: List[str]
    related_patterns: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class ErrorSolution:
    """Represents a solution for an error pattern."""
    solution_id: str
    pattern_type: str
    description: str
    steps: List[str]
    prerequisites: List[str]
    success_criteria: List[str]
    created_at: datetime
    updated_at: datetime

class ErrorKnowledgeBase:
    """Manages error patterns, solutions, and their relationships."""
    
    def __init__(self, storage_path: str = "data/error_knowledge"):
        self.logger = logging.getLogger(__name__)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.patterns: Dict[str, ErrorPattern] = {}
        self.solutions: Dict[str, ErrorSolution] = {}
        self.pattern_solutions: Dict[str, List[str]] = defaultdict(list)
        self.category_patterns: Dict[str, List[str]] = defaultdict(list)
        self.severity_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load patterns and solutions from storage."""
        # Load patterns
        patterns_file = self.storage_path / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                patterns_data = json.load(f)
                for pattern_data in patterns_data:
                    pattern = ErrorPattern(
                        pattern_type=pattern_data["pattern_type"],
                        regex=pattern_data["regex"],
                        description=pattern_data["description"],
                        severity=pattern_data["severity"],
                        category=pattern_data["category"],
                        subcategory=pattern_data["subcategory"],
                        common_causes=pattern_data["common_causes"],
                        solutions=pattern_data["solutions"],
                        examples=pattern_data["examples"],
                        related_patterns=pattern_data["related_patterns"],
                        created_at=datetime.fromisoformat(pattern_data["created_at"]),
                        updated_at=datetime.fromisoformat(pattern_data["updated_at"])
                    )
                    self.patterns[pattern.pattern_type] = pattern
                    self.category_patterns[pattern.category].append(pattern.pattern_type)
                    self.severity_patterns[pattern.severity].append(pattern.pattern_type)
        
        # Load solutions
        solutions_file = self.storage_path / "solutions.json"
        if solutions_file.exists():
            with open(solutions_file, 'r') as f:
                solutions_data = json.load(f)
                for solution_data in solutions_data:
                    solution = ErrorSolution(
                        solution_id=solution_data["solution_id"],
                        pattern_type=solution_data["pattern_type"],
                        description=solution_data["description"],
                        steps=solution_data["steps"],
                        prerequisites=solution_data["prerequisites"],
                        success_criteria=solution_data["success_criteria"],
                        created_at=datetime.fromisoformat(solution_data["created_at"]),
                        updated_at=datetime.fromisoformat(solution_data["updated_at"])
                    )
                    self.solutions[solution.solution_id] = solution
                    self.pattern_solutions[solution.pattern_type].append(solution.solution_id)
    
    def _save_data(self):
        """Save patterns and solutions to storage."""
        # Save patterns
        patterns_file = self.storage_path / "patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(
                [asdict(pattern) for pattern in self.patterns.values()],
                f,
                default=str,
                indent=2
            )
        
        # Save solutions
        solutions_file = self.storage_path / "solutions.json"
        with open(solutions_file, 'w') as f:
            json.dump(
                [asdict(solution) for solution in self.solutions.values()],
                f,
                default=str,
                indent=2
            )
    
    def add_pattern(self, pattern: ErrorPattern) -> bool:
        """Add a new error pattern to the knowledge base."""
        try:
            self.patterns[pattern.pattern_type] = pattern
            self.category_patterns[pattern.category].append(pattern.pattern_type)
            self.severity_patterns[pattern.severity].append(pattern.pattern_type)
            self._save_data()
            return True
        except Exception as e:
            self.logger.error(f"Error adding pattern: {str(e)}")
            return False
    
    def add_solution(self, solution: ErrorSolution) -> bool:
        """Add a new solution to the knowledge base."""
        try:
            self.solutions[solution.solution_id] = solution
            self.pattern_solutions[solution.pattern_type].append(solution.solution_id)
            self._save_data()
            return True
        except Exception as e:
            self.logger.error(f"Error adding solution: {str(e)}")
            return False
    
    def get_pattern(self, pattern_type: str) -> Optional[ErrorPattern]:
        """Retrieve a pattern by its type."""
        return self.patterns.get(pattern_type)
    
    def get_solution(self, solution_id: str) -> Optional[ErrorSolution]:
        """Retrieve a solution by its ID."""
        return self.solutions.get(solution_id)
    
    def get_pattern_solutions(self, pattern_type: str) -> List[ErrorSolution]:
        """Get all solutions for a specific pattern."""
        solution_ids = self.pattern_solutions.get(pattern_type, [])
        return [self.solutions[sid] for sid in solution_ids if sid in self.solutions]
    
    def get_category_patterns(self, category: str) -> List[ErrorPattern]:
        """Get all patterns in a specific category."""
        pattern_types = self.category_patterns.get(category, [])
        return [self.patterns[pt] for pt in pattern_types if pt in self.patterns]
    
    def get_severity_patterns(self, severity: str) -> List[ErrorPattern]:
        """Get all patterns with a specific severity level."""
        pattern_types = self.severity_patterns.get(severity, [])
        return [self.patterns[pt] for pt in pattern_types if pt in self.patterns]
    
    def search_patterns(self, query: str) -> List[ErrorPattern]:
        """Search for patterns matching the query."""
        query = query.lower()
        matches = []
        
        for pattern in self.patterns.values():
            # Check pattern type
            if query in pattern.pattern_type.lower():
                matches.append(pattern)
                continue
            
            # Check description
            if query in pattern.description.lower():
                matches.append(pattern)
                continue
            
            # Check examples
            if any(query in example.lower() for example in pattern.examples):
                matches.append(pattern)
                continue
            
            # Check common causes
            if any(query in cause.lower() for cause in pattern.common_causes):
                matches.append(pattern)
                continue
        
        return matches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            "total_patterns": len(self.patterns),
            "total_solutions": len(self.solutions),
            "categories": {
                category: len(patterns)
                for category, patterns in self.category_patterns.items()
            },
            "severity_levels": {
                severity: len(patterns)
                for severity, patterns in self.severity_patterns.items()
            },
            "patterns_per_solution": {
                pattern_type: len(solutions)
                for pattern_type, solutions in self.pattern_solutions.items()
            }
        } 