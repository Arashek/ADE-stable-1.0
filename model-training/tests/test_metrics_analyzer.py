import pytest
import ast
from pathlib import Path
from src.refactoring.metrics_analyzer import MetricsAnalyzer, CodeMetrics

@pytest.fixture
def analyzer():
    """Create a MetricsAnalyzer instance for testing."""
    return MetricsAnalyzer()

@pytest.fixture
def sample_code():
    """Create a sample code snippet for testing."""
    return """
def calculate_sum(numbers):
    # Calculate the sum of numbers
    total = 0
    for num in numbers:
        if num > 0:
            total += num
    return total

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        result = []
        for item in self.data:
            if isinstance(item, dict):
                if 'value' in item:
                    result.append(item['value'])
        return result

def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            else:
                return a + b
        else:
            return a
    return 0
"""

@pytest.fixture
def sample_file(tmp_path, sample_code):
    """Create a temporary file with sample code."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(sample_code)
    return file_path

def test_initialization(analyzer):
    """Test MetricsAnalyzer initialization."""
    assert isinstance(analyzer, MetricsAnalyzer)
    assert hasattr(analyzer, 'metrics')

def test_analyze_file(analyzer, sample_file):
    """Test analyzing a single file."""
    metrics = analyzer.analyze_file(str(sample_file))
    assert isinstance(metrics, CodeMetrics)
    
    # Check basic metrics
    assert metrics.lines_of_code > 0
    assert metrics.comment_ratio >= 0
    assert metrics.function_count == 3
    assert metrics.variable_count > 0
    
    # Check complexity metrics
    assert metrics.complexity > 0
    assert metrics.cyclomatic_complexity > 0
    assert metrics.cognitive_complexity > 0
    
    # Check maintainability metrics
    assert 0 <= metrics.maintainability <= 100
    assert 0 <= metrics.maintainability_index <= 100
    
    # Check other metrics
    assert 0 <= metrics.duplication_ratio <= 1
    assert 0 <= metrics.naming_score <= 100
    assert metrics.halstead_metrics is not None

def test_analyze_directory(analyzer, tmp_path):
    """Test analyzing a directory of Python files."""
    # Create multiple Python files
    files = {
        "file1.py": "def func1(): pass",
        "file2.py": "class Class1: pass",
        "file3.py": "x = 1"
    }
    
    for name, content in files.items():
        (tmp_path / name).write_text(content)
    
    metrics = analyzer.analyze_directory(str(tmp_path))
    assert len(metrics) == 3
    assert all(isinstance(m, CodeMetrics) for m in metrics.values())

def test_complexity_calculation(analyzer, sample_code):
    """Test complexity calculation."""
    tree = ast.parse(sample_code)
    complexity = analyzer._calculate_complexity(tree)
    assert complexity > 0
    
    # Complex function should have higher complexity
    complex_tree = ast.parse("""
def complex():
    if a:
        if b:
            if c:
                if d:
                    pass
    return
    """)
    complex_complexity = analyzer._calculate_complexity(complex_tree)
    assert complex_complexity > complexity

def test_maintainability_calculation(analyzer, sample_code):
    """Test maintainability calculation."""
    tree = ast.parse(sample_code)
    maintainability = analyzer._calculate_maintainability(tree)
    assert 0 <= maintainability <= 100
    
    # Complex code should have lower maintainability
    complex_code = """
def complex():
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            pass
    return
    """
    complex_tree = ast.parse(complex_code)
    complex_maintainability = analyzer._calculate_maintainability(complex_tree)
    assert complex_maintainability < maintainability

def test_comment_ratio_calculation(analyzer):
    """Test comment ratio calculation."""
    # Code with comments
    code_with_comments = """
# This is a comment
def func():
    # Another comment
    pass
    """
    ratio = analyzer._calculate_comment_ratio(code_with_comments)
    assert ratio > 0
    
    # Code without comments
    code_without_comments = """
def func():
    pass
    """
    ratio = analyzer._calculate_comment_ratio(code_without_comments)
    assert ratio == 0

def test_function_length_calculation(analyzer):
    """Test average function length calculation."""
    # Code with functions of different lengths
    code = """
def short():
    pass

def medium():
    x = 1
    y = 2
    return x + y

def long():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    return a + b + c + d + e
    """
    tree = ast.parse(code)
    avg_length = analyzer._calculate_avg_function_length(tree)
    assert avg_length > 0

def test_nesting_depth_calculation(analyzer):
    """Test nesting depth calculation."""
    # Code with different nesting levels
    code = """
def nested():
    if a:
        if b:
            if c:
                pass
    return
    """
    tree = ast.parse(code)
    depth = analyzer._calculate_nesting_depth(tree)
    assert depth == 3

def test_duplication_ratio_calculation(analyzer):
    """Test code duplication ratio calculation."""
    # Code with duplicated lines
    code = """
def func1():
    x = 1
    y = 2
    return x + y

def func2():
    x = 1
    y = 2
    return x + y
    """
    ratio = analyzer._calculate_duplication_ratio(code)
    assert 0 <= ratio <= 1
    assert ratio > 0  # Should detect duplicated lines

def test_naming_score_calculation(analyzer):
    """Test naming convention compliance score calculation."""
    # Code with good naming
    good_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
    """
    tree = ast.parse(good_code)
    good_score = analyzer._calculate_naming_score(tree)
    
    # Code with bad naming
    bad_code = """
def calc_sum(nums):
    tot = 0
    for n in nums:
        tot += n
    return tot
    """
    tree = ast.parse(bad_code)
    bad_score = analyzer._calculate_naming_score(tree)
    
    assert good_score > bad_score

def test_cyclomatic_complexity_calculation(analyzer):
    """Test cyclomatic complexity calculation."""
    # Simple function
    simple_code = """
def simple():
    return 1
    """
    tree = ast.parse(simple_code)
    simple_complexity = analyzer._calculate_cyclomatic_complexity(tree)
    
    # Complex function
    complex_code = """
def complex():
    if a:
        if b:
            if c:
                if d:
                    return 1
    return 0
    """
    tree = ast.parse(complex_code)
    complex_complexity = analyzer._calculate_cyclomatic_complexity(tree)
    
    assert complex_complexity > simple_complexity

def test_cognitive_complexity_calculation(analyzer):
    """Test cognitive complexity calculation."""
    # Simple function
    simple_code = """
def simple():
    return 1
    """
    tree = ast.parse(simple_code)
    simple_complexity = analyzer._calculate_cognitive_complexity(tree)
    
    # Complex function with nesting
    complex_code = """
def complex():
    if a:
        if b:
            if c:
                if d:
                    return 1
    return 0
    """
    tree = ast.parse(complex_code)
    complex_complexity = analyzer._calculate_cognitive_complexity(tree)
    
    assert complex_complexity > simple_complexity

def test_halstead_metrics_calculation(analyzer):
    """Test Halstead metrics calculation."""
    code = """
def calculate(a, b):
    result = a + b
    return result
    """
    metrics = analyzer._calculate_halstead_metrics(code)
    
    assert 'program_length' in metrics
    assert 'vocabulary' in metrics
    assert 'volume' in metrics
    assert 'difficulty' in metrics
    assert 'effort' in metrics
    assert 'time' in metrics
    assert 'bugs' in metrics
    
    assert all(isinstance(v, float) for v in metrics.values())
    assert all(v >= 0 for v in metrics.values())

def test_maintainability_index_calculation(analyzer):
    """Test maintainability index calculation."""
    # Simple function
    simple_code = """
def simple():
    return 1
    """
    tree = ast.parse(simple_code)
    simple_index = analyzer._calculate_maintainability_index(tree)
    
    # Complex function
    complex_code = """
def complex():
    if a:
        if b:
            if c:
                if d:
                    return 1
    return 0
    """
    tree = ast.parse(complex_code)
    complex_index = analyzer._calculate_maintainability_index(tree)
    
    assert 0 <= simple_index <= 100
    assert 0 <= complex_index <= 100
    assert simple_index > complex_index

def test_name_validation(analyzer):
    """Test name validation functions."""
    # Test variable names
    assert analyzer._is_valid_name('valid_name')
    assert analyzer._is_valid_name('valid_name_123')
    assert not analyzer._is_valid_name('123invalid')
    assert not analyzer._is_valid_name('Invalid')
    
    # Test function names
    assert analyzer._is_valid_function_name('valid_function')
    assert analyzer._is_valid_function_name('valid_function_123')
    assert not analyzer._is_valid_function_name('InvalidFunction')
    
    # Test class names
    assert analyzer._is_valid_class_name('ValidClass')
    assert analyzer._is_valid_class_name('ValidClass123')
    assert not analyzer._is_valid_class_name('invalid_class')
    assert not analyzer._is_valid_class_name('123Invalid')

def test_similarity_ratio(analyzer):
    """Test string similarity ratio calculation."""
    # Identical strings
    assert analyzer._similarity_ratio('hello', 'hello') == 1.0
    
    # Similar strings
    ratio = analyzer._similarity_ratio('hello', 'helo')
    assert 0 < ratio < 1
    
    # Different strings
    ratio = analyzer._similarity_ratio('hello', 'world')
    assert 0 < ratio < 1
    assert ratio < analyzer._similarity_ratio('hello', 'helo') 