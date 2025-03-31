from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import re
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReviewSeverity(Enum):
    """Severity levels for review comments"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ReviewCategory(Enum):
    """Categories for review comments"""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    DOCUMENTATION = "documentation"
    STYLE = "style"
    ARCHITECTURE = "architecture"
    TEST_COVERAGE = "test_coverage"
    OTHER = "other"

class ReviewComment(BaseModel):
    """A single review comment"""
    id: str
    line_number: int
    column: int
    severity: ReviewSeverity
    category: ReviewCategory
    description: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}

class ReviewResult(BaseModel):
    """Result of a code review"""
    file_path: str
    comments: List[ReviewComment]
    metrics: Dict[str, float]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class CodeReviewManager:
    """Manager for code review operations"""
    
    def __init__(self):
        self.review_history: List[ReviewResult] = []
        self.review_patterns: Dict[ReviewCategory, List[Dict[str, Any]]] = {}
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize review patterns"""
        # Bug patterns
        self.review_patterns[ReviewCategory.BUG] = [
            {
                "name": "null_check",
                "description": "Check for potential null reference",
                "pattern": r"if\s+(\w+)\s*==\s*None",
                "severity": ReviewSeverity.HIGH,
                "suggestion": "Use 'is None' instead of '== None'"
            },
            {
                "name": "division_by_zero",
                "description": "Check for potential division by zero",
                "pattern": r"(\w+)\s*/\s*(\w+)",
                "severity": ReviewSeverity.CRITICAL,
                "suggestion": "Add check for zero denominator"
            }
        ]
        
        # Security patterns
        self.review_patterns[ReviewCategory.SECURITY] = [
            {
                "name": "sql_injection",
                "description": "Check for SQL injection vulnerability",
                "pattern": r"execute\s*\(\s*[\"'].*?\+.*?[\"']",
                "severity": ReviewSeverity.CRITICAL,
                "suggestion": "Use parameterized queries"
            },
            {
                "name": "hardcoded_secret",
                "description": "Check for hardcoded secrets",
                "pattern": r"(password|secret|key)\s*=\s*[\"'].*?[\"']",
                "severity": ReviewSeverity.HIGH,
                "suggestion": "Use environment variables or secure configuration"
            }
        ]
        
        # Performance patterns
        self.review_patterns[ReviewCategory.PERFORMANCE] = [
            {
                "name": "inefficient_loop",
                "description": "Check for inefficient loop patterns",
                "pattern": r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\)",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Use enumerate() instead"
            },
            {
                "name": "repeated_string_concat",
                "description": "Check for repeated string concatenation",
                "pattern": r"(\w+)\s*\+\s*(\w+)",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Use string formatting or join()"
            }
        ]
        
        # Maintainability patterns
        self.review_patterns[ReviewCategory.MAINTAINABILITY] = [
            {
                "name": "long_function",
                "description": "Check for long functions",
                "pattern": r"def\s+(\w+)\s*\([^)]*\):",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Break down into smaller functions"
            },
            {
                "name": "magic_number",
                "description": "Check for magic numbers",
                "pattern": r"\b\d{3,}\b",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Define as named constant"
            }
        ]
        
        # Testability patterns
        self.review_patterns[ReviewCategory.TESTABILITY] = [
            {
                "name": "global_state",
                "description": "Check for global state usage",
                "pattern": r"global\s+(\w+)",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Use dependency injection"
            },
            {
                "name": "tight_coupling",
                "description": "Check for tight coupling",
                "pattern": r"from\s+(\w+)\s+import\s+\*",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Import specific items"
            }
        ]
        
        # Documentation patterns
        self.review_patterns[ReviewCategory.DOCUMENTATION] = [
            {
                "name": "missing_docstring",
                "description": "Check for missing docstrings",
                "pattern": r"def\s+(\w+)\s*\([^)]*\):",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Add docstring"
            },
            {
                "name": "unclear_comment",
                "description": "Check for unclear comments",
                "pattern": r"#\s*[a-z]+\s+[a-z]+\s+[a-z]+",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Make comment more descriptive"
            }
        ]
        
        # Style patterns
        self.review_patterns[ReviewCategory.STYLE] = [
            {
                "name": "inconsistent_naming",
                "description": "Check for inconsistent naming",
                "pattern": r"def\s+([A-Z][a-z]+)\s*\([^)]*\):",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Use snake_case for function names"
            },
            {
                "name": "line_length",
                "description": "Check for long lines",
                "pattern": r".{100,}",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Break line into multiple lines"
            }
        ]
        
        # Architecture patterns
        self.review_patterns[ReviewCategory.ARCHITECTURE] = [
            {
                "name": "circular_import",
                "description": "Check for circular imports",
                "pattern": r"from\s+(\w+)\s+import\s+(\w+)\s+import\s+(\w+)",
                "severity": ReviewSeverity.HIGH,
                "suggestion": "Restructure imports"
            },
            {
                "name": "violation_of_single_responsibility",
                "description": "Check for single responsibility violation",
                "pattern": r"class\s+(\w+):\s*def\s+(\w+)\s*\([^)]*\):",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Split class into multiple classes"
            }
        ]
        
        # Test coverage patterns
        self.review_patterns[ReviewCategory.TEST_COVERAGE] = [
            {
                "name": "missing_test",
                "description": "Check for missing tests",
                "pattern": r"def\s+test_(\w+)\s*\([^)]*\):",
                "severity": ReviewSeverity.MEDIUM,
                "suggestion": "Add test case"
            },
            {
                "name": "incomplete_test",
                "description": "Check for incomplete tests",
                "pattern": r"def\s+test_(\w+)\s*\([^)]*\):\s*pass",
                "severity": ReviewSeverity.LOW,
                "suggestion": "Complete test implementation"
            }
        ]
        
    async def review_code(
        self,
        code: str,
        file_path: str,
        categories: Optional[List[ReviewCategory]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ReviewResult:
        """Review code based on specified categories"""
        try:
            # Initialize result
            result = ReviewResult(
                file_path=file_path,
                comments=[],
                metrics={},
                summary={},
                metadata={
                    "reviewed_at": datetime.now().isoformat(),
                    "context": context or {}
                }
            )
            
            # Calculate metrics
            result.metrics = self._calculate_metrics(code)
            
            # Review code
            if categories is None:
                categories = list(ReviewCategory)
                
            for category in categories:
                if category in self.review_patterns:
                    for pattern in self.review_patterns[category]:
                        try:
                            comments = self._find_pattern_matches(
                                code,
                                pattern,
                                category,
                                file_path
                            )
                            result.comments.extend(comments)
                        except Exception as e:
                            logger.error(f"Failed to apply pattern {pattern['name']}: {str(e)}")
                            
            # Generate summary
            result.summary = self._generate_summary(result)
            
            # Store in history
            self.review_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to review code: {str(e)}")
            
    def _calculate_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code metrics"""
        try:
            tree = ast.parse(code)
            return {
                "complexity": self._calculate_complexity(tree),
                "maintainability": self._calculate_maintainability(tree),
                "testability": self._calculate_testability(tree),
                "documentation": self._calculate_documentation(tree),
                "style": self._calculate_style_score(code)
            }
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {str(e)}")
            return {}
            
    def _find_pattern_matches(
        self,
        code: str,
        pattern: Dict[str, Any],
        category: ReviewCategory,
        file_path: str
    ) -> List[ReviewComment]:
        """Find matches for a review pattern"""
        comments = []
        for match in re.finditer(pattern["pattern"], code):
            line_number = code[:match.start()].count('\n') + 1
            column = match.start() - code.rfind('\n', 0, match.start())
            
            comment = ReviewComment(
                id=f"{pattern['name']}_{line_number}_{column}",
                line_number=line_number,
                column=column,
                severity=pattern["severity"],
                category=category,
                description=pattern["description"],
                suggestion=pattern.get("suggestion"),
                code_snippet=code[max(0, match.start()-20):min(len(code), match.end()+20)],
                context={
                    "pattern": pattern["name"],
                    "match": match.group(0)
                }
            )
            comments.append(comment)
            
        return comments
        
    def _generate_summary(self, result: ReviewResult) -> Dict[str, Any]:
        """Generate review summary"""
        summary = {
            "total_comments": len(result.comments),
            "comments_by_severity": {},
            "comments_by_category": {},
            "metrics": result.metrics
        }
        
        # Count comments by severity
        for comment in result.comments:
            if comment.severity not in summary["comments_by_severity"]:
                summary["comments_by_severity"][comment.severity] = 0
            summary["comments_by_severity"][comment.severity] += 1
            
        # Count comments by category
        for comment in result.comments:
            if comment.category not in summary["comments_by_category"]:
                summary["comments_by_category"][comment.category] = 0
            summary["comments_by_category"][comment.category] += 1
            
        return summary
        
    def get_review_history(self) -> List[ReviewResult]:
        """Get review history"""
        return self.review_history
        
    def get_review_patterns(self) -> Dict[ReviewCategory, List[Dict[str, Any]]]:
        """Get review patterns"""
        return self.review_patterns
        
    def add_review_pattern(
        self,
        category: ReviewCategory,
        name: str,
        description: str,
        pattern: str,
        severity: ReviewSeverity,
        suggestion: Optional[str] = None
    ):
        """Add a new review pattern"""
        if category not in self.review_patterns:
            self.review_patterns[category] = []
            
        self.review_patterns[category].append({
            "name": name,
            "description": description,
            "pattern": pattern,
            "severity": severity,
            "suggestion": suggestion
        }) 