from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import ast
import re
from datetime import datetime
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
from radon.visitors import ComplexityVisitor
from radon.raw import analyze as raw_analyze

logger = logging.getLogger(__name__)

@dataclass
class CodeQualityMetrics:
    """Metrics for code quality analysis"""
    complexity: float
    maintainability: float
    security_score: float
    performance_score: float
    test_coverage: float
    documentation_score: float
    issues: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]

class CodeQualityAnalyzer:
    """Code quality analysis system"""
    
    def __init__(self):
        # Define quality thresholds
        self.thresholds = {
            "complexity": {
                "low": 5,
                "medium": 10,
                "high": 15
            },
            "maintainability": {
                "low": 0.6,
                "medium": 0.8,
                "high": 0.9
            },
            "security": {
                "low": 0.6,
                "medium": 0.8,
                "high": 0.9
            },
            "performance": {
                "low": 0.6,
                "medium": 0.8,
                "high": 0.9
            },
            "test_coverage": {
                "low": 0.6,
                "medium": 0.8,
                "high": 0.9
            },
            "documentation": {
                "low": 0.6,
                "medium": 0.8,
                "high": 0.9
            }
        }
        
        # Define security patterns
        self.security_patterns = {
            "sql_injection": r"execute\s*\(\s*[\"'].*?\+.*?[\"']",
            "xss": r"innerHTML\s*=\s*[\"'].*?\+.*?[\"']",
            "command_injection": r"os\.system\s*\(\s*[\"'].*?\+.*?[\"']",
            "path_traversal": r"open\s*\(\s*[\"'].*?\+.*?[\"']",
            "hardcoded_secrets": r"(password|secret|key)\s*=\s*[\"'][^\"']+[\"']"
        }
        
        # Define performance patterns
        self.performance_patterns = {
            "n_plus_one": r"for.*?query.*?for",
            "memory_leak": r"new\s+.*?;",
            "inefficient_loop": r"for.*?\+=",
            "redundant_computation": r"for.*?for.*?for",
            "large_object": r"class.*?{.*?}.*?{.*?}"
        }
        
    async def analyze(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> CodeQualityMetrics:
        """Analyze code quality"""
        try:
            # Calculate basic metrics
            complexity = self._calculate_complexity(code)
            maintainability = self._calculate_maintainability(code)
            
            # Analyze security
            security_score, security_issues = self._analyze_security(code)
            
            # Analyze performance
            performance_score, performance_issues = self._analyze_performance(code)
            
            # Analyze test coverage
            test_coverage = self._analyze_test_coverage(code)
            
            # Analyze documentation
            documentation_score = self._analyze_documentation(code)
            
            # Detect patterns
            patterns = self._detect_patterns(code)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(
                code,
                complexity,
                maintainability,
                security_score,
                performance_score,
                test_coverage,
                documentation_score,
                patterns
            )
            
            return CodeQualityMetrics(
                complexity=complexity,
                maintainability=maintainability,
                security_score=security_score,
                performance_score=performance_score,
                test_coverage=test_coverage,
                documentation_score=documentation_score,
                issues=security_issues + performance_issues,
                patterns=patterns,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            return CodeQualityMetrics(
                complexity=0.0,
                maintainability=0.0,
                security_score=0.0,
                performance_score=0.0,
                test_coverage=0.0,
                documentation_score=0.0,
                issues=[],
                patterns=[],
                suggestions=[]
            )
            
    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity"""
        try:
            # Use radon for complexity analysis
            visitor = ComplexityVisitor.from_code(code)
            complexity = sum(item.complexity for item in visitor.functions)
            
            # Normalize complexity score
            max_complexity = self.thresholds["complexity"]["high"]
            normalized_complexity = min(complexity / max_complexity, 1.0)
            
            return normalized_complexity
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {e}")
            return 0.0
            
    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index"""
        try:
            # Use radon for maintainability analysis
            mi = radon_metrics.mi_visit(code, multi=True)
            
            # Normalize maintainability score
            max_mi = 100.0
            normalized_mi = min(mi / max_mi, 1.0)
            
            return normalized_mi
            
        except Exception as e:
            logger.error(f"Error calculating maintainability: {e}")
            return 0.0
            
    def _analyze_security(self, code: str) -> Tuple[float, List[Dict[str, Any]]]:
        """Analyze security issues"""
        issues = []
        total_patterns = len(self.security_patterns)
        matched_patterns = 0
        
        try:
            # Check for security patterns
            for pattern_name, pattern in self.security_patterns.items():
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "type": "security",
                        "pattern": pattern_name,
                        "line": code[:match.start()].count("\n") + 1,
                        "code": match.group(0),
                        "severity": "high"
                    })
                    matched_patterns += 1
                    
            # Calculate security score
            security_score = 1.0 - (matched_patterns / total_patterns)
            
            return security_score, issues
            
        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            return 0.0, []
            
    def _analyze_performance(self, code: str) -> Tuple[float, List[Dict[str, Any]]]:
        """Analyze performance issues"""
        issues = []
        total_patterns = len(self.performance_patterns)
        matched_patterns = 0
        
        try:
            # Check for performance patterns
            for pattern_name, pattern in self.performance_patterns.items():
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "type": "performance",
                        "pattern": pattern_name,
                        "line": code[:match.start()].count("\n") + 1,
                        "code": match.group(0),
                        "severity": "medium"
                    })
                    matched_patterns += 1
                    
            # Calculate performance score
            performance_score = 1.0 - (matched_patterns / total_patterns)
            
            return performance_score, issues
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return 0.0, []
            
    def _analyze_test_coverage(self, code: str) -> float:
        """Analyze test coverage"""
        try:
            # Look for test files and test functions
            test_patterns = [
                r"test_.*?\.py",
                r"def\s+test_.*?\(",
                r"class\s+Test.*?\("
            ]
            
            total_patterns = len(test_patterns)
            matched_patterns = 0
            
            for pattern in test_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    matched_patterns += 1
                    
            # Calculate test coverage score
            test_coverage = matched_patterns / total_patterns
            
            return test_coverage
            
        except Exception as e:
            logger.error(f"Error analyzing test coverage: {e}")
            return 0.0
            
    def _analyze_documentation(self, code: str) -> float:
        """Analyze documentation coverage"""
        try:
            # Look for documentation patterns
            doc_patterns = [
                r"\"\"\".*?\"\"\"",
                r"'''.*?'''",
                r"#.*?$"
            ]
            
            # Count documented elements
            documented_elements = 0
            total_elements = 0
            
            # Parse code
            tree = ast.parse(code)
            
            # Count classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    total_elements += 1
                    if ast.get_docstring(node):
                        documented_elements += 1
                        
            # Calculate documentation score
            if total_elements > 0:
                documentation_score = documented_elements / total_elements
            else:
                documentation_score = 0.0
                
            return documentation_score
            
        except Exception as e:
            logger.error(f"Error analyzing documentation: {e}")
            return 0.0
            
    def _detect_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Detect code patterns"""
        patterns = []
        
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Look for design patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for singleton pattern
                    if self._is_singleton(node):
                        patterns.append({
                            "type": "design_pattern",
                            "name": "singleton",
                            "line": node.lineno,
                            "code": ast.unparse(node)
                        })
                        
                    # Check for factory pattern
                    if self._is_factory(node):
                        patterns.append({
                            "type": "design_pattern",
                            "name": "factory",
                            "line": node.lineno,
                            "code": ast.unparse(node)
                        })
                        
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []
            
    def _is_singleton(self, node: ast.ClassDef) -> bool:
        """Check if class implements singleton pattern"""
        try:
            # Look for private instance variable
            has_instance = False
            for child in node.body:
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and target.id == "_instance":
                            has_instance = True
                            break
                            
            # Look for get_instance method
            has_get_instance = False
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    if child.name == "get_instance":
                        has_get_instance = True
                        break
                        
            return has_instance and has_get_instance
            
        except Exception as e:
            logger.error(f"Error checking singleton pattern: {e}")
            return False
            
    def _is_factory(self, node: ast.ClassDef) -> bool:
        """Check if class implements factory pattern"""
        try:
            # Look for create/build/make methods
            has_factory_method = False
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    if child.name in ["create", "build", "make"]:
                        has_factory_method = True
                        break
                        
            return has_factory_method
            
        except Exception as e:
            logger.error(f"Error checking factory pattern: {e}")
            return False
            
    def _generate_suggestions(
        self,
        code: str,
        complexity: float,
        maintainability: float,
        security_score: float,
        performance_score: float,
        test_coverage: float,
        documentation_score: float,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []
        
        try:
            # Complexity suggestions
            if complexity > self.thresholds["complexity"]["medium"]:
                suggestions.append({
                    "type": "complexity",
                    "description": "High code complexity detected. Consider breaking down into smaller functions.",
                    "priority": "high",
                    "impact": "maintainability"
                })
                
            # Maintainability suggestions
            if maintainability < self.thresholds["maintainability"]["medium"]:
                suggestions.append({
                    "type": "maintainability",
                    "description": "Low maintainability index. Consider improving code organization and documentation.",
                    "priority": "medium",
                    "impact": "maintainability"
                })
                
            # Security suggestions
            if security_score < self.thresholds["security"]["medium"]:
                suggestions.append({
                    "type": "security",
                    "description": "Security issues detected. Review and fix security vulnerabilities.",
                    "priority": "high",
                    "impact": "security"
                })
                
            # Performance suggestions
            if performance_score < self.thresholds["performance"]["medium"]:
                suggestions.append({
                    "type": "performance",
                    "description": "Performance issues detected. Review and optimize code.",
                    "priority": "medium",
                    "impact": "performance"
                })
                
            # Test coverage suggestions
            if test_coverage < self.thresholds["test_coverage"]["medium"]:
                suggestions.append({
                    "type": "test_coverage",
                    "description": "Low test coverage. Add more tests to improve reliability.",
                    "priority": "medium",
                    "impact": "reliability"
                })
                
            # Documentation suggestions
            if documentation_score < self.thresholds["documentation"]["medium"]:
                suggestions.append({
                    "type": "documentation",
                    "description": "Low documentation coverage. Add more documentation.",
                    "priority": "low",
                    "impact": "maintainability"
                })
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return [] 