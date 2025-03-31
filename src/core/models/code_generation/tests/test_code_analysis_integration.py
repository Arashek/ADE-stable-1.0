"""
Integration tests for code analysis capabilities and performance tests for large codebases.
"""

import unittest
import time
import tempfile
import os
from typing import Dict, List, Any
from ..code_analysis import (
    SemanticCodeAnalyzer,
    DependencyAnalyzer,
    ImpactAnalyzer,
    CodeQualityAnalyzer,
    CodeMetricType,
    CodeMetric
)

class TestCodeAnalysisIntegration(unittest.TestCase):
    """Test cases for integration between different analyzers."""
    
    def setUp(self):
        self.semantic_analyzer = SemanticCodeAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()
        self.quality_analyzer = CodeQualityAnalyzer()
        
        # Create a sample codebase for integration testing
        self.codebase = {
            "models.py": """
from typing import List, Dict, Any

class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email
        }

class UserManager:
    def __init__(self):
        self.users: List[User] = []
        
    def add_user(self, user: User) -> None:
        self.users.append(user)
        
    def get_user_by_email(self, email: str) -> User:
        for user in self.users:
            if user.email == email:
                return user
        raise ValueError(f"User with email {email} not found")
""",
            "services.py": """
from models import User, UserManager

class UserService:
    def __init__(self):
        self.user_manager = UserManager()
        
    def create_user(self, name: str, email: str) -> User:
        user = User(name, email)
        self.user_manager.add_user(user)
        return user
        
    def find_user(self, email: str) -> User:
        return self.user_manager.get_user_by_email(email)
""",
            "api.py": """
from services import UserService

class UserAPI:
    def __init__(self):
        self.user_service = UserService()
        
    def create_user(self, name: str, email: str) -> dict:
        user = self.user_service.create_user(name, email)
        return user.to_dict()
        
    def get_user(self, email: str) -> dict:
        user = self.user_service.find_user(email)
        return user.to_dict()
"""
        }
        
    def test_semantic_and_dependency_integration(self):
        """Test integration between semantic and dependency analysis."""
        # First, analyze dependencies
        dep_result = self.dependency_analyzer.analyze_dependencies(list(self.codebase.keys()))
        
        # Then, analyze semantics of each file
        semantic_results = {}
        for file_path, content in self.codebase.items():
            semantic_results[file_path] = self.semantic_analyzer.analyze_code_semantics(content)
            
        # Verify integration points
        for file_path in self.codebase:
            # Check that semantic features match dependency relationships
            semantic_features = semantic_results[file_path]["features"]
            dep_features = dep_result["import_dependencies"][file_path]
            
            # Verify that imported modules are present in semantic features
            for dep in dep_features:
                self.assertTrue(
                    any(dep in feature for feature in semantic_features["imports"]),
                    f"Import {dep} not found in semantic features of {file_path}"
                )
                
    def test_impact_and_quality_integration(self):
        """Test integration between impact and quality analysis."""
        # Create a change to test impact
        changes = [{
            "file_path": "models.py",
            "type": "modification",
            "content": self.codebase["models.py"].replace(
                "def to_dict(self) -> Dict[str, Any]:",
                "def to_dict(self) -> Dict[str, Any]:\n        # Added timestamp"
            )
        }]
        
        # Analyze impact
        impact_result = self.impact_analyzer.analyze_impact(changes, self.codebase)
        
        # Analyze quality of affected files
        quality_results = {}
        for file_path in impact_result["direct_impact"]["modified_files"]:
            quality_results[file_path] = self.quality_analyzer.analyze_quality(
                self.codebase[file_path], file_path
            )
            
        # Verify integration points
        for file_path in impact_result["direct_impact"]["modified_files"]:
            # Check that quality metrics reflect the changes
            quality_metrics = quality_results[file_path]
            
            # Verify that documentation metrics are affected
            self.assertGreater(
                quality_metrics["documentation_metrics"]["comment_coverage"],
                0,
                f"Comment coverage should be affected in {file_path}"
            )
            
            # Verify that maintainability metrics reflect the change
            self.assertGreater(
                quality_metrics["maintainability_metrics"]["lines_of_code"],
                0,
                f"Lines of code should be affected in {file_path}"
            )
            
    def test_full_analysis_integration(self):
        """Test full integration of all analyzers."""
        # Create a complex change scenario
        changes = [{
            "file_path": "models.py",
            "type": "modification",
            "content": self.codebase["models.py"].replace(
                "class User:",
                "class User:\n    '''User model with enhanced functionality.'''"
            )
        }]
        
        # Run all analyses
        dep_result = self.dependency_analyzer.analyze_dependencies(list(self.codebase.keys()))
        impact_result = self.impact_analyzer.analyze_impact(changes, self.codebase)
        
        semantic_results = {}
        quality_results = {}
        for file_path, content in self.codebase.items():
            semantic_results[file_path] = self.semantic_analyzer.analyze_code_semantics(content)
            quality_results[file_path] = self.quality_analyzer.analyze_quality(content, file_path)
            
        # Verify cross-analyzer consistency
        for file_path in self.codebase:
            # Check semantic and quality consistency
            semantic_features = semantic_results[file_path]["features"]
            quality_metrics = quality_results[file_path]
            
            # Verify that class documentation is reflected in both analyses
            if any("class" in feature for feature in semantic_features["classes"]):
                self.assertGreater(
                    quality_metrics["documentation_metrics"]["docstring_coverage"],
                    0,
                    f"Class documentation should be reflected in quality metrics for {file_path}"
                )
                
            # Check impact and dependency consistency
            if file_path in impact_result["direct_impact"]["modified_files"]:
                self.assertIn(
                    file_path,
                    dep_result["import_dependencies"],
                    f"Modified file {file_path} should be in dependency analysis"
                )

class TestCodeAnalysisPerformance(unittest.TestCase):
    """Test cases for performance with large codebases."""
    
    def setUp(self):
        self.semantic_analyzer = SemanticCodeAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.impact_analyzer = ImpactAnalyzer()
        self.quality_analyzer = CodeQualityAnalyzer()
        
        # Create a temporary directory for large codebase
        self.temp_dir = tempfile.mkdtemp()
        
        # Generate a large codebase
        self.large_codebase = self._generate_large_codebase()
        
    def tearDown(self):
        # Clean up temporary files
        for file_path in self.large_codebase:
            try:
                os.remove(os.path.join(self.temp_dir, file_path))
            except:
                pass
        os.rmdir(self.temp_dir)
        
    def _generate_large_codebase(self) -> Dict[str, str]:
        """Generate a large codebase for performance testing."""
        codebase = {}
        
        # Generate 100 Python files
        for i in range(100):
            file_name = f"module_{i}.py"
            content = f"""
from typing import List, Dict, Any

class Module{i}:
    def __init__(self):
        self.data = []
        
    def process_data(self, input_data: List[Any]) -> Dict[str, Any]:
        result = {{}}
        for item in input_data:
            if isinstance(item, (int, float)):
                result[str(item)] = item * 2
        return result
        
    def analyze(self, data: Dict[str, Any]) -> List[Any]:
        return [v for v in data.values() if v > 0]
"""
            codebase[file_name] = content
            
            # Write to temporary file
            with open(os.path.join(self.temp_dir, file_name), 'w') as f:
                f.write(content)
                
        return codebase
        
    def test_semantic_analysis_performance(self):
        """Test performance of semantic analysis with large codebase."""
        start_time = time.time()
        
        # Analyze all files
        results = {}
        for file_path, content in self.large_codebase.items():
            results[file_path] = self.semantic_analyzer.analyze_code_semantics(content)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertLess(duration, 10.0, "Semantic analysis should complete within 10 seconds")
        
        # Verify results
        self.assertEqual(len(results), len(self.large_codebase))
        for file_path, result in results.items():
            self.assertIn("features", result)
            self.assertIn("semantic_representation", result)
            
    def test_dependency_analysis_performance(self):
        """Test performance of dependency analysis with large codebase."""
        start_time = time.time()
        
        # Analyze dependencies
        result = self.dependency_analyzer.analyze_dependencies(
            [os.path.join(self.temp_dir, f) for f in self.large_codebase.keys()]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertLess(duration, 5.0, "Dependency analysis should complete within 5 seconds")
        
        # Verify results
        self.assertIn("import_dependencies", result)
        self.assertIn("dependency_metrics", result)
        
    def test_impact_analysis_performance(self):
        """Test performance of impact analysis with large codebase."""
        # Create a change scenario
        changes = [{
            "file_path": "module_0.py",
            "type": "modification",
            "content": self.large_codebase["module_0.py"].replace(
                "def process_data",
                "def process_data\n        # Enhanced processing"
            )
        }]
        
        start_time = time.time()
        
        # Analyze impact
        result = self.impact_analyzer.analyze_impact(changes, self.large_codebase)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertLess(duration, 8.0, "Impact analysis should complete within 8 seconds")
        
        # Verify results
        self.assertIn("direct_impact", result)
        self.assertIn("indirect_impact", result)
        
    def test_quality_analysis_performance(self):
        """Test performance of quality analysis with large codebase."""
        start_time = time.time()
        
        # Analyze quality of all files
        results = {}
        for file_path, content in self.large_codebase.items():
            results[file_path] = self.quality_analyzer.analyze_quality(content, file_path)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertLess(duration, 15.0, "Quality analysis should complete within 15 seconds")
        
        # Verify results
        self.assertEqual(len(results), len(self.large_codebase))
        for file_path, result in results.items():
            self.assertIn("complexity_metrics", result)
            self.assertIn("maintainability_metrics", result)
            self.assertIn("quality_score", result)
            
    def test_full_analysis_performance(self):
        """Test performance of full analysis pipeline with large codebase."""
        start_time = time.time()
        
        # Run all analyses
        dep_result = self.dependency_analyzer.analyze_dependencies(
            [os.path.join(self.temp_dir, f) for f in self.large_codebase.keys()]
        )
        
        semantic_results = {}
        quality_results = {}
        for file_path, content in self.large_codebase.items():
            semantic_results[file_path] = self.semantic_analyzer.analyze_code_semantics(content)
            quality_results[file_path] = self.quality_analyzer.analyze_quality(content, file_path)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance
        self.assertLess(duration, 30.0, "Full analysis should complete within 30 seconds")
        
        # Verify results
        self.assertEqual(len(semantic_results), len(self.large_codebase))
        self.assertEqual(len(quality_results), len(self.large_codebase))
        self.assertIn("import_dependencies", dep_result)

if __name__ == '__main__':
    unittest.main() 