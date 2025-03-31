import pytest
from pathlib import Path
import shutil
import json
from src.tools.self_improvement.analyzer import CodeAnalyzer
from src.tools.self_improvement.executor import ImprovementExecutor
from src.tools.self_improvement.reporter import ImprovementReporter

@pytest.fixture
def test_project_dir(tmp_path):
    """Create a temporary project directory with test files"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create test files
    (project_dir / "src").mkdir()
    (project_dir / "src" / "test_module.py").write_text("""
def complex_function(x, y):
    result = 0
    for i in range(x):
        for j in range(y):
            if i > j:
                result += i * j
            else:
                result += j - i
    return result

def duplicate_function(x, y):
    result = 0
    for i in range(x):
        for j in range(y):
            if i > j:
                result += i * j
            else:
                result += j - i
    return result

def expensive_function(data):
    return sum([x * x for x in data])

def undocumented_function(x):
    return x * 2

def poorly_named_function(x):
    return x * 3
""")
    
    return project_dir

@pytest.fixture
def analyzer(test_project_dir):
    """Create a CodeAnalyzer instance"""
    return CodeAnalyzer(test_project_dir)

@pytest.fixture
def executor(test_project_dir):
    """Create an ImprovementExecutor instance"""
    return ImprovementExecutor(test_project_dir)

@pytest.fixture
def reporter(test_project_dir):
    """Create an ImprovementReporter instance"""
    return ImprovementReporter(test_project_dir)

def test_full_improvement_cycle(test_project_dir, analyzer, executor, reporter):
    """Test the complete improvement cycle"""
    # 1. Analyze codebase
    analysis_results = analyzer.analyze_codebase()
    
    # Verify analysis results
    assert 'files' in analysis_results
    assert 'complexity' in analysis_results
    assert 'documentation' in analysis_results
    assert 'performance' in analysis_results
    
    # 2. Generate improvement suggestions
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    
    # Verify suggestions
    assert len(suggestions) > 0
    assert all(hasattr(s, 'description') for s in suggestions)
    assert all(hasattr(s, 'priority') for s in suggestions)
    
    # 3. Execute improvements
    improvement_results = executor.execute_improvements(suggestions)
    
    # Verify improvement results
    assert 'improved_files' in improvement_results
    assert 'changes' in improvement_results
    assert len(improvement_results['improved_files']) > 0
    
    # 4. Generate report
    report = reporter.generate_report(analysis_results, improvement_results)
    
    # Verify report
    assert report.total_files_analyzed > 0
    assert report.total_files_improved > 0
    assert report.total_changes_made > 0
    assert len(report.metrics) > 0
    assert len(report.recommendations) > 0
    
    # 5. Verify visualizations
    viz_dir = test_project_dir / "reports" / "visualizations"
    assert viz_dir.exists()
    assert (viz_dir / "changes_by_category.png").exists()
    assert (viz_dir / "improvement_metrics.png").exists()
    assert (viz_dir / "impact_analysis.png").exists()

def test_improvement_validation(test_project_dir, analyzer, executor):
    """Test that improvements maintain code functionality"""
    # 1. Analyze original code
    analysis_results = analyzer.analyze_codebase()
    
    # 2. Execute improvements
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    improvement_results = executor.execute_improvements(suggestions)
    
    # 3. Verify code still works
    import sys
    sys.path.append(str(test_project_dir))
    from src.test_module import complex_function, expensive_function
    
    # Test complex function
    assert complex_function(3, 4) == complex_function(3, 4)
    
    # Test expensive function
    test_data = [1, 2, 3, 4, 5]
    assert expensive_function(test_data) == expensive_function(test_data)

def test_improvement_metrics(test_project_dir, analyzer, executor, reporter):
    """Test that improvements are measurable"""
    # 1. Get initial metrics
    initial_analysis = analyzer.analyze_codebase()
    initial_metrics = {
        'complexity': initial_analysis['complexity']['average'],
        'documentation': initial_analysis['documentation']['coverage'],
        'performance': initial_analysis['performance']['avg_execution_time']
    }
    
    # 2. Execute improvements
    suggestions = analyzer.generate_improvement_suggestions(initial_analysis)
    improvement_results = executor.execute_improvements(suggestions)
    
    # 3. Get final metrics
    final_analysis = analyzer.analyze_codebase()
    final_metrics = {
        'complexity': final_analysis['complexity']['average'],
        'documentation': final_analysis['documentation']['coverage'],
        'performance': final_analysis['performance']['avg_execution_time']
    }
    
    # 4. Verify improvements
    assert final_metrics['complexity'] <= initial_metrics['complexity']
    assert final_metrics['documentation'] >= initial_metrics['documentation']
    assert final_metrics['performance'] <= initial_metrics['performance']

def test_error_handling(test_project_dir, analyzer, executor):
    """Test error handling during improvement process"""
    # 1. Create invalid code
    invalid_file = test_project_dir / "src" / "invalid.py"
    invalid_file.write_text("def invalid_function():\n    return 1/0")
    
    # 2. Try to analyze and improve
    analysis_results = analyzer.analyze_codebase()
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    improvement_results = executor.execute_improvements(suggestions)
    
    # 3. Verify error handling
    assert 'errors' in improvement_results
    assert len(improvement_results['errors']) > 0
    assert all('error' in error for error in improvement_results['errors'])

def test_backup_and_restore(test_project_dir, executor):
    """Test backup and restore functionality"""
    # 1. Create test file
    test_file = test_project_dir / "src" / "test_backup.py"
    test_file.write_text("def test_function():\n    return 42")
    
    # 2. Create backup
    backup_path = executor._create_backup(test_file)
    assert backup_path.exists()
    
    # 3. Modify file
    test_file.write_text("def test_function():\n    return 43")
    
    # 4. Restore from backup
    executor._restore_from_backup(test_file, backup_path)
    assert test_file.read_text() == "def test_function():\n    return 42"

def test_concurrent_improvements(test_project_dir, analyzer, executor):
    """Test handling of concurrent improvements"""
    import concurrent.futures
    
    # 1. Generate multiple suggestions
    analysis_results = analyzer.analyze_codebase()
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    
    # 2. Execute improvements concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for suggestion in suggestions:
            future = executor.submit(
                executor._execute_single_improvement,
                suggestion
            )
            futures.append(future)
        
        # Wait for all improvements to complete
        results = [f.result() for f in futures]
    
    # 3. Verify results
    assert len(results) == len(suggestions)
    assert all(isinstance(result, dict) for result in results)
    assert all('changes_made' in result for result in results)
    assert all('errors' in result for result in results)

def test_report_generation(test_project_dir, analyzer, executor, reporter):
    """Test report generation with various improvement types"""
    # 1. Analyze and improve
    analysis_results = analyzer.analyze_codebase()
    suggestions = analyzer.generate_improvement_suggestions(analysis_results)
    improvement_results = executor.execute_improvements(suggestions)
    
    # 2. Generate report
    report = reporter.generate_report(analysis_results, improvement_results)
    
    # 3. Verify report contents
    assert report.timestamp
    assert report.total_files_analyzed > 0
    assert report.total_files_improved > 0
    assert report.total_changes_made > 0
    
    # 4. Verify metrics
    assert len(report.metrics) > 0
    for metric in report.metrics:
        assert metric.metric_name
        assert metric.before_value is not None
        assert metric.after_value is not None
        assert metric.unit
        assert metric.improvement_percentage is not None
    
    # 5. Verify impacts
    assert report.performance_impact
    assert report.code_quality_impact
    assert report.documentation_impact
    
    # 6. Verify recommendations
    assert len(report.recommendations) > 0
    assert all(isinstance(rec, str) for rec in report.recommendations) 