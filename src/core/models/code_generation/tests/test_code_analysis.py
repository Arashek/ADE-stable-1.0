"""
Tests for code analysis capabilities including semantic understanding,
dependency analysis, impact analysis, and quality metrics.
"""

import unittest
import ast
from typing import Dict, List, Any
from ..code_analysis import (
    SemanticCodeAnalyzer,
    DependencyAnalyzer,
    ImpactAnalyzer,
    CodeQualityAnalyzer,
    CodeMetricType,
    CodeMetric
)

class TestSemanticCodeAnalyzer(unittest.TestCase):
    """Test cases for semantic code analysis."""
    
    def setUp(self):
        self.analyzer = SemanticCodeAnalyzer()
        
    def test_code_semantics_analysis(self):
        """Test analysis of code semantics."""
        code = """
def calculate_sum(a: int, b: int) -> int:
    '''Calculate the sum of two numbers.'''
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
        
    def add(self, x: int, y: int) -> int:
        self.result = x + y
        return self.result
"""
        result = self.analyzer.analyze_code_semantics(code)
        
        # Check features extraction
        self.assertIn("functions", result["features"])
        self.assertIn("classes", result["features"])
        self.assertEqual(len(result["features"]["functions"]), 2)
        self.assertEqual(len(result["features"]["classes"]), 1)
        
        # Check semantic representation
        self.assertIn("text_representation", result["semantic_representation"])
        self.assertIn("vector_representation", result["semantic_representation"])
        
        # Check pattern identification
        self.assertIsInstance(result["patterns"], list)
        
        # Check intent analysis
        self.assertIn("primary_purpose", result["intent"])
        self.assertIn("complexity_level", result["intent"])
        
    def test_feature_extraction(self):
        """Test extraction of code features."""
        code = """
import os
import sys

def process_data(data: List[int]) -> Dict[str, Any]:
    result = {}
    for item in data:
        if item > 0:
            result[str(item)] = item * 2
    return result
"""
        tree = ast.parse(code)
        features = self.analyzer._extract_code_features(tree)
        
        # Check imports
        self.assertIn("os", features["imports"])
        self.assertIn("sys", features["imports"])
        
        # Check functions
        self.assertEqual(len(features["functions"]), 1)
        self.assertEqual(features["functions"][0]["name"], "process_data")
        
        # Check variables
        self.assertIn("result", features["variables"])
        
        # Check control structures
        self.assertIn("If", features["control_structures"])
        self.assertIn("For", features["control_structures"])

class TestDependencyAnalyzer(unittest.TestCase):
    """Test cases for dependency analysis."""
    
    def setUp(self):
        self.analyzer = DependencyAnalyzer()
        
    def test_dependency_analysis(self):
        """Test analysis of file dependencies."""
        files = {
            "main.py": """
from utils import helper
from models import User

def process_user(user: User):
    return helper.format_user(user)
""",
            "utils.py": """
def format_user(user):
    return f"{user.name} ({user.email})"
""",
            "models.py": """
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
"""
        }
        
        result = self.analyzer.analyze_dependencies(list(files.keys()))
        
        # Check import dependencies
        self.assertIn("import_dependencies", result)
        self.assertIn("main.py", result["import_dependencies"])
        self.assertEqual(len(result["import_dependencies"]["main.py"]), 2)
        
        # Check function dependencies
        self.assertIn("function_dependencies", result)
        self.assertIn("main.py", result["function_dependencies"])
        self.assertEqual(len(result["function_dependencies"]["main.py"]), 1)
        
        # Check dependency metrics
        self.assertIn("dependency_metrics", result)
        metrics = result["dependency_metrics"]
        self.assertGreater(metrics["average_dependencies"], 0)
        self.assertGreaterEqual(metrics["max_dependencies"], 0)
        
    def test_dependency_graph(self):
        """Test building dependency graph."""
        files = {
            "a.py": "from b import func",
            "b.py": "from c import Class",
            "c.py": "class Class: pass"
        }
        
        self.analyzer._build_dependency_graph(list(files.keys()))
        
        # Check graph structure
        self.assertIn("a.py", self.analyzer.dependency_graph)
        self.assertIn("b.py", self.analyzer.dependency_graph)
        self.assertIn("c.py", self.analyzer.dependency_graph)
        
        # Check edges
        self.assertTrue(self.analyzer.dependency_graph.has_edge("a.py", "b.py"))
        self.assertTrue(self.analyzer.dependency_graph.has_edge("b.py", "c.py"))

class TestImpactAnalyzer(unittest.TestCase):
    """Test cases for impact analysis."""
    
    def setUp(self):
        self.analyzer = ImpactAnalyzer()
        
    def test_impact_analysis(self):
        """Test analysis of code changes impact."""
        changes = [{
            "file_path": "main.py",
            "type": "modification",
            "content": """
def process_data(data: List[int]) -> Dict[str, Any]:
    result = {}
    for item in data:
        if item > 0:
            result[str(item)] = item * 2
    return result
"""
        }]
        
        codebase = {
            "main.py": """
def process_data(data: List[int]) -> Dict[str, Any]:
    result = {}
    for item in data:
        result[str(item)] = item
    return result
""",
            "test_main.py": """
def test_process_data():
    data = [1, 2, 3]
    result = process_data(data)
    assert result == {"1": 1, "2": 2, "3": 3}
"""
        }
        
        result = self.analyzer.analyze_impact(changes, codebase)
        
        # Check direct impact
        self.assertIn("direct_impact", result)
        self.assertIn("modified_files", result["direct_impact"])
        self.assertIn("main.py", result["direct_impact"]["modified_files"])
        
        # Check indirect impact
        self.assertIn("indirect_impact", result)
        self.assertIn("dependent_files", result["indirect_impact"])
        self.assertIn("test_main.py", result["indirect_impact"]["dependent_files"])
        
        # Check test impact
        self.assertIn("test_impact", result)
        self.assertIn("affected_tests", result["test_impact"])
        self.assertIn("test_main.py", result["test_impact"]["affected_tests"])
        
        # Check risk assessment
        self.assertIn("risk_assessment", result)
        self.assertIn("risk_level", result["risk_assessment"])
        self.assertIn("risk_factors", result["risk_assessment"])
        
    def test_risk_assessment(self):
        """Test risk assessment of changes."""
        direct_impact = {
            "modified_files": ["main.py"],
            "affected_functions": ["process_data"],
            "affected_classes": [],
            "breaking_changes": []
        }
        
        indirect_impact = {
            "dependent_files": ["test_main.py"],
            "affected_tests": ["test_main.py"],
            "performance_impact": [],
            "security_impact": []
        }
        
        test_impact = {
            "affected_tests": ["test_main.py"],
            "coverage_changes": {
                "test_main.py": {"decrease": 0.05}
            },
            "test_quality_impact": {},
            "regression_risk": {}
        }
        
        risk_assessment = self.analyzer._assess_risk(
            direct_impact, indirect_impact, test_impact
        )
        
        # Check risk assessment structure
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("risk_factors", risk_assessment)
        self.assertIn("mitigation_suggestions", risk_assessment)
        self.assertIn("confidence_score", risk_assessment)
        
        # Check risk level
        self.assertIn(risk_assessment["risk_level"], ["low", "medium", "high"])

class TestCodeQualityAnalyzer(unittest.TestCase):
    """Test cases for code quality analysis."""
    
    def setUp(self):
        self.analyzer = CodeQualityAnalyzer()
        
    def test_quality_analysis(self):
        """Test analysis of code quality."""
        code = """
def calculate_factorial(n: int) -> int:
    '''Calculate the factorial of a number.
    
    Args:
        n: The number to calculate factorial for.
        
    Returns:
        The factorial of n.
        
    Raises:
        ValueError: If n is negative.
    '''
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
"""
        result = self.analyzer.analyze_quality(code, "factorial.py")
        
        # Check complexity metrics
        self.assertIn("complexity_metrics", result)
        self.assertIn("cyclomatic_complexity", result["complexity_metrics"])
        self.assertIn("cognitive_complexity", result["complexity_metrics"])
        
        # Check maintainability metrics
        self.assertIn("maintainability_metrics", result)
        self.assertIn("lines_of_code", result["maintainability_metrics"])
        self.assertIn("comment_ratio", result["maintainability_metrics"])
        
        # Check documentation metrics
        self.assertIn("documentation_metrics", result)
        self.assertIn("docstring_coverage", result["documentation_metrics"])
        self.assertIn("comment_coverage", result["documentation_metrics"])
        
        # Check security metrics
        self.assertIn("security_metrics", result)
        self.assertIn("security_score", result["security_metrics"])
        self.assertIn("vulnerability_count", result["security_metrics"])
        
        # Check performance metrics
        self.assertIn("performance_metrics", result)
        self.assertIn("performance_score", result["performance_metrics"])
        self.assertIn("algorithmic_complexity", result["performance_metrics"])
        
        # Check quality score
        self.assertIn("quality_score", result)
        self.assertIsInstance(result["quality_score"], float)
        self.assertGreaterEqual(result["quality_score"], 0)
        self.assertLessEqual(result["quality_score"], 1)
        
    def test_complexity_metrics(self):
        """Test calculation of complexity metrics."""
        code = """
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
"""
        metrics = self.analyzer._calculate_complexity_metrics(code)
        
        # Check cyclomatic complexity
        self.assertGreater(metrics["cyclomatic_complexity"], 0)
        
        # Check cognitive complexity
        self.assertGreater(metrics["cognitive_complexity"], 0)
        
        # Check Halstead complexity
        self.assertGreater(metrics["halstead_complexity"], 0)
        
        # Check maintainability index
        self.assertGreater(metrics["maintainability_index"], 0)
        
    def test_maintainability_metrics(self):
        """Test calculation of maintainability metrics."""
        code = """
# This is a comment
def long_function():
    # Another comment
    result = 0
    for i in range(100):
        if i % 2 == 0:
            result += i
    return result
"""
        metrics = self.analyzer._calculate_maintainability_metrics(code)
        
        # Check lines of code
        self.assertGreater(metrics["lines_of_code"], 0)
        
        # Check comment ratio
        self.assertGreater(metrics["comment_ratio"], 0)
        self.assertLessEqual(metrics["comment_ratio"], 1)
        
        # Check function length
        self.assertGreater(metrics["function_length"], 0)
        
        # Check nesting depth
        self.assertGreater(metrics["nesting_depth"], 0)

if __name__ == '__main__':
    unittest.main() 