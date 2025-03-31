import pytest
from src.core.error.code_fixer import CodeFixer, CodeFix

@pytest.fixture
def fixer():
    return CodeFixer()

def test_analyze_unused_import(fixer):
    """Test analysis of unused import"""
    code = """
import os
import sys
import json

def process_data():
    return json.loads('{}')
"""
    context = {"error_type": "ImportError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 1
    unused_import = next(f for f in fixes if f.fix_id.startswith("fix_unused_import_"))
    assert unused_import.description == "Remove unused import: os"
    assert unused_import.confidence == 0.9
    assert unused_import.safety_score > 0.8
    assert "os" not in unused_import.fixed_code

def test_analyze_circular_import(fixer):
    """Test analysis of circular import"""
    code = """
from module_a import function_a
from module_b import function_b

def process_data():
    return function_a() + function_b()
"""
    context = {"error_type": "ImportError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 1
    circular_import = next(f for f in fixes if f.fix_id.startswith("fix_circular_import_"))
    assert "Move circular import inside function" in circular_import.description
    assert circular_import.confidence == 0.8
    assert circular_import.safety_score > 0.7

def test_analyze_naming_convention(fixer):
    """Test analysis of naming convention violations"""
    code = """
def ProcessData():
    UserInput = "test"
    return UserInput
"""
    context = {"error_type": "NameError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 2
    function_fix = next(f for f in fixes if f.fix_id.startswith("fix_naming_ProcessData"))
    variable_fix = next(f for f in fixes if f.fix_id.startswith("fix_naming_UserInput"))
    
    assert function_fix.description == "Rename ProcessData to process_data to follow convention"
    assert variable_fix.description == "Rename UserInput to user_input to follow convention"
    assert "def process_data" in function_fix.fixed_code
    assert "user_input" in variable_fix.fixed_code

def test_analyze_missing_docstring(fixer):
    """Test analysis of missing docstrings"""
    code = """
def process_data():
    return "test"

class DataProcessor:
    def process(self):
        return "test"
"""
    context = {"error_type": "NameError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 2
    function_fix = next(f for f in fixes if f.fix_id.startswith("fix_docstring_process_data"))
    class_fix = next(f for f in fixes if f.fix_id.startswith("fix_docstring_DataProcessor"))
    
    assert function_fix.description == "Add docstring to process_data"
    assert class_fix.description == "Add docstring to DataProcessor"
    assert '"""process_data function."""' in function_fix.fixed_code
    assert '"""DataProcessor class."""' in class_fix.fixed_code

def test_analyze_high_complexity(fixer):
    """Test analysis of high complexity function"""
    code = """
def complex_function():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        return "test"
"""
    context = {"error_type": "RuntimeError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 1
    complexity_fix = next(f for f in fixes if f.fix_id.startswith("fix_complexity_complex_function"))
    assert "Split complex function complex_function into smaller functions" in complexity_fix.description
    assert complexity_fix.confidence == 0.6
    assert complexity_fix.safety_score > 0.5

def test_safety_checks(fixer):
    """Test safety checks for fixes"""
    code = """
def process_data():
    return "test"
"""
    context = {"error_type": "NameError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 1
    fix = fixes[0]
    
    # Check safety score components
    assert fix.safety_score > 0
    assert fix.safety_score <= 1
    
    # Check validation results
    assert fix.validation_results["syntax_valid"]
    assert not fix.validation_results["line_lengths"]
    assert fix.validation_results["complexity"] <= fixer.validation_rules["max_complexity"]
    assert not fix.validation_results["naming_conventions"]
    assert not fix.validation_results["docstrings"]

def test_validation_rules(fixer):
    """Test validation rules"""
    # Test line length
    long_line = "x" * (fixer.validation_rules["max_line_length"] + 1)
    code = f"""
def process_data():
    {long_line}
    return "test"
"""
    context = {"error_type": "NameError"}
    
    fixes = fixer.analyze_code(code, context)
    
    assert len(fixes) >= 1
    fix = fixes[0]
    assert len(fix.validation_results["line_lengths"]) > 0
    
    # Test complexity
    complex_code = """
def complex_function():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            if True:
                                if True:
                                    if True:
                                        if True:
                                            return "test"
"""
    fixes = fixer.analyze_code(complex_code, context)
    
    assert len(fixes) >= 1
    fix = fixes[0]
    assert fix.validation_results["complexity"] > fixer.validation_rules["max_complexity"]

def test_error_handling(fixer):
    """Test error handling in code analysis"""
    # Test with invalid code
    invalid_code = "def process_data() return 'test'"
    context = {"error_type": "SyntaxError"}
    
    fixes = fixer.analyze_code(invalid_code, context)
    assert len(fixes) == 0
    
    # Test with empty code
    fixes = fixer.analyze_code("", context)
    assert len(fixes) == 0
    
    # Test with None code
    fixes = fixer.analyze_code(None, context)
    assert len(fixes) == 0

def test_fix_history(fixer):
    """Test fix history tracking"""
    code = """
def ProcessData():
    return "test"
"""
    context = {"error_type": "NameError"}
    
    # Apply fixes
    fixes = fixer.analyze_code(code, context)
    assert len(fixes) >= 1
    
    # Check history
    history = fixer.get_fix_history()
    assert len(history) > 0
    
    # Clear history
    fixer.clear_history()
    assert len(fixer.get_fix_history()) == 0 