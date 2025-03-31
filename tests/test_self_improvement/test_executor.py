import os
import pytest
from pathlib import Path
import json
import ast
from datetime import datetime
import shutil

from src.tools.self_improvement.executor import ImprovementExecutor, ImprovementResult
from src.tools.self_improvement.analyzer import ImprovementSuggestion

@pytest.fixture
def test_project_dir(tmp_path):
    """Create a temporary project directory with test files"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create necessary subdirectories
    (project_dir / "current").mkdir()
    (project_dir / "improvements").mkdir()
    (project_dir / "backups").mkdir()
    (project_dir / "reports").mkdir()
    
    # Create test configuration
    config = {
        "name": "test_project",
        "type": "self_improvement",
        "settings": {
            "isolation_level": "strict",
            "allowed_operations": ["code_analysis", "refactoring", "optimization", "documentation"],
            "backup_frequency": "before_each_improvement",
            "max_improvement_iterations": 5
        }
    }
    
    with open(project_dir / "config.json", 'w') as f:
        json.dump(config, f)
    
    return project_dir

@pytest.fixture
def test_file(test_project_dir):
    """Create a test Python file with various issues"""
    file_path = test_project_dir / "current" / "test_file.py"
    
    content = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
                if result > 100:
                    return result * 2
                else:
                    return result
            else:
                return 0
        else:
            return 0
    else:
        return 0

def performance_issue():
    result = ""
    for i in range(1000):
        result += str(i)
    return result

class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"""
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path

@pytest.fixture
def executor(test_project_dir):
    """Create an improvement executor instance"""
    return ImprovementExecutor(str(test_project_dir))

@pytest.fixture
def test_suggestions():
    """Create test improvement suggestions"""
    return [
        ImprovementSuggestion(
            category="code_quality",
            file_path="test_file.py",
            line_number=1,
            description="High cyclomatic complexity detected",
            priority=2,
            potential_impact="Improved code maintainability",
            suggested_changes=["Break down complex functions"],
            estimated_effort="medium"
        ),
        ImprovementSuggestion(
            category="performance",
            file_path="test_file.py",
            line_number=20,
            description="String concatenation in loop",
            priority=3,
            potential_impact="Improved performance",
            suggested_changes=["Use list join instead"],
            estimated_effort="low"
        ),
        ImprovementSuggestion(
            category="documentation",
            file_path="test_file.py",
            line_number=1,
            description="Missing docstrings",
            priority=1,
            potential_impact="Better code documentation",
            suggested_changes=["Add docstrings"],
            estimated_effort="low"
        )
    ]

def test_executor_initialization(executor, test_project_dir):
    """Test executor initialization"""
    assert executor.project_dir == test_project_dir
    assert executor.current_dir == test_project_dir / "current"
    assert executor.improvements_dir == test_project_dir / "improvements"
    assert executor.backup_dir == test_project_dir / "backups"
    assert executor.reports_dir == test_project_dir / "reports"

def test_find_target_file(executor, test_file):
    """Test finding target files for improvements"""
    # Test with file path
    suggestion = ImprovementSuggestion(
        category="code_quality",
        file_path="test_file.py",
        line_number=1,
        description="Test",
        priority=1,
        potential_impact="Test",
        suggested_changes=["Test"],
        estimated_effort="low"
    )
    assert executor._find_target_file(suggestion) == test_file
    
    # Test finding complex file
    suggestion.description = "High complexity"
    assert executor._find_target_file(suggestion) == test_file
    
    # Test finding performance critical file
    suggestion.description = "Performance issues"
    assert executor._find_target_file(suggestion) == test_file
    
    # Test finding file without docstring
    suggestion.description = "Missing docstrings"
    assert executor._find_target_file(suggestion) == test_file

def test_calculate_complexity(executor, test_file):
    """Test cyclomatic complexity calculation"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Test complex function
    complex_func = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "complex_function")
    assert executor._calculate_complexity(complex_func) > 5
    
    # Test simple function
    simple_func = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "performance_issue")
    assert executor._calculate_complexity(simple_func) == 1

def test_has_performance_issues(executor, test_file):
    """Test performance issue detection"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Test performance issue function
    perf_func = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "performance_issue")
    assert executor._has_performance_issues(perf_func)

def test_has_docstrings(executor, test_file):
    """Test docstring detection"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Test class without docstrings
    test_class = next(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    assert not executor._has_docstrings(test_class)

def test_refactor_complex_functions(executor, test_file):
    """Test complex function refactoring"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Refactor complex function
    new_tree = executor._refactor_complex_functions(tree)
    
    # Check if helper functions were created
    helper_functions = [
        node for node in ast.walk(new_tree)
        if isinstance(node, ast.FunctionDef) and "helper" in node.name
    ]
    assert len(helper_functions) > 0

def test_optimize_loops(executor, test_file):
    """Test loop optimization"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Optimize loops
    new_tree = executor._optimize_loops(tree)
    
    # Check if string concatenation was optimized
    perf_func = next(node for node in ast.walk(new_tree) if isinstance(node, ast.FunctionDef) and node.name == "performance_issue")
    assert not executor._has_performance_issues(perf_func)

def test_add_docstrings(executor, test_file):
    """Test docstring addition"""
    with open(test_file, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Add docstrings
    new_tree = executor._add_docstrings(tree)
    
    # Check if docstrings were added
    test_class = next(node for node in ast.walk(new_tree) if isinstance(node, ast.ClassDef))
    assert executor._has_docstrings(test_class)

def test_backup_and_restore(executor, test_file):
    """Test backup and restore functionality"""
    # Create backup
    executor._create_backup()
    
    # Modify file
    with open(test_file, 'a') as f:
        f.write("\n# Test modification")
    
    # Restore from backup
    executor._restore_from_backup()
    
    # Check if file was restored
    with open(test_file, 'r') as f:
        content = f.read()
    assert "# Test modification" not in content

def test_execute_improvements(executor, test_suggestions):
    """Test executing multiple improvements"""
    results = executor.execute_improvements(test_suggestions)
    
    assert len(results) == len(test_suggestions)
    assert all(isinstance(result, ImprovementResult) for result in results)
    
    # Check if improvements were saved
    improvement_files = list(executor.improvements_dir.glob("improvement_*.json"))
    assert len(improvement_files) > 0
    
    # Check if report was generated
    report_files = list(executor.reports_dir.glob("improvement_report_*.json"))
    assert len(report_files) > 0

def test_error_handling(executor):
    """Test error handling during improvements"""
    # Test with invalid file path
    suggestion = ImprovementSuggestion(
        category="code_quality",
        file_path="nonexistent.py",
        line_number=1,
        description="Test",
        priority=1,
        potential_impact="Test",
        suggested_changes=["Test"],
        estimated_effort="low"
    )
    
    result = executor._execute_single_improvement(suggestion)
    assert not result.success
    assert "Target file not found" in result.errors

def test_metrics_tracking(executor, test_file):
    """Test code metrics tracking"""
    # Get initial metrics
    metrics_before = executor._get_current_metrics()
    assert metrics_before
    
    # Make some changes
    with open(test_file, 'a') as f:
        f.write("\n# Test addition")
    
    # Get metrics after changes
    metrics_after = executor._get_current_metrics()
    assert metrics_after
    
    # Compare metrics
    assert metrics_before != metrics_after

def test_generate_diff(executor, test_file):
    """Test diff generation"""
    # Read original content
    with open(test_file, 'r') as f:
        original = f.read()
    
    # Make changes
    with open(test_file, 'a') as f:
        f.write("\n# Test addition")
    
    # Read new content
    with open(test_file, 'r') as f:
        new = f.read()
    
    # Generate diff
    diff = executor._generate_diff(original, new)
    assert diff
    assert "# Test addition" in diff 