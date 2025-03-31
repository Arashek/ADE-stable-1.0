"""
Tests for the metrics visualizer.
"""

import pytest
import os
import shutil
import json
from pathlib import Path
from src.refactoring.metrics_visualizer import MetricsVisualizer

@pytest.fixture
def visualizer(tmp_path):
    """Create a MetricsVisualizer instance with a temporary output directory."""
    return MetricsVisualizer(str(tmp_path))

@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing."""
    return {
        'complexity': 5,
        'maintainability': 85.5,
        'lines_of_code': 100,
        'comment_ratio': 0.2,
        'function_count': 3,
        'avg_function_length': 15.5,
        'variable_count': 10,
        'nesting_depth': 2,
        'duplication_ratio': 0.1,
        'naming_score': 90.0,
        'cyclomatic_complexity': 6,
        'cognitive_complexity': 4,
        'halstead_metrics': {
            'program_length': 150,
            'vocabulary': 50,
            'volume': 750,
            'difficulty': 15,
            'effort': 11250,
            'time': 625,
            'bugs': 0.25
        },
        'maintainability_index': 80.0
    }

@pytest.fixture
def sample_directory_metrics():
    """Create sample directory metrics for testing."""
    return {
        'file1.py': {
            'complexity': 5,
            'maintainability': 85.5,
            'lines_of_code': 100,
            'comment_ratio': 0.2,
            'function_count': 3,
            'avg_function_length': 15.5,
            'variable_count': 10,
            'nesting_depth': 2,
            'duplication_ratio': 0.1,
            'naming_score': 90.0,
            'cyclomatic_complexity': 6,
            'cognitive_complexity': 4,
            'halstead_metrics': {
                'program_length': 150,
                'vocabulary': 50,
                'volume': 750,
                'difficulty': 15,
                'effort': 11250,
                'time': 625,
                'bugs': 0.25
            },
            'maintainability_index': 80.0
        },
        'file2.py': {
            'complexity': 8,
            'maintainability': 75.0,
            'lines_of_code': 150,
            'comment_ratio': 0.15,
            'function_count': 5,
            'avg_function_length': 20.0,
            'variable_count': 15,
            'nesting_depth': 3,
            'duplication_ratio': 0.2,
            'naming_score': 85.0,
            'cyclomatic_complexity': 9,
            'cognitive_complexity': 7,
            'halstead_metrics': {
                'program_length': 200,
                'vocabulary': 60,
                'volume': 1000,
                'difficulty': 20,
                'effort': 20000,
                'time': 1111,
                'bugs': 0.33
            },
            'maintainability_index': 70.0
        }
    }

def test_initialization(visualizer):
    """Test MetricsVisualizer initialization."""
    assert isinstance(visualizer, MetricsVisualizer)
    assert visualizer.output_dir.exists()
    assert visualizer.output_dir.is_dir()

def test_visualize_file_metrics(visualizer, sample_metrics):
    """Test visualization of single file metrics."""
    visualizer.visualize_file_metrics(sample_metrics, "test_file")
    
    # Check if output files were created
    output_file = visualizer.output_dir / "test_file_metrics.html"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_visualize_directory_metrics(visualizer, sample_directory_metrics):
    """Test visualization of directory metrics."""
    visualizer.visualize_directory_metrics(sample_directory_metrics)
    
    # Check if output files were created
    expected_files = [
        "directory_summary.html",
        "metric_correlations.html",
        "metric_comparisons.html",
        "metric_distributions.html"
    ]
    
    for file in expected_files:
        output_file = visualizer.output_dir / file
        assert output_file.exists()
        assert output_file.stat().st_size > 0

def test_create_radar_chart_single_file(visualizer, sample_metrics):
    """Test radar chart creation for a single file."""
    visualizer.create_radar_chart(sample_metrics, "test_file")
    
    # Check if output file was created
    output_file = visualizer.output_dir / "test_file_radar.html"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_create_radar_chart_directory(visualizer, sample_directory_metrics):
    """Test radar chart creation for directory metrics."""
    visualizer.create_radar_chart(sample_directory_metrics)
    
    # Check if output file was created
    output_file = visualizer.output_dir / "radar_chart.html"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_create_summary_plots(visualizer, sample_directory_metrics):
    """Test creation of summary plots."""
    visualizer._create_summary_plots(sample_directory_metrics)
    
    # Check if output file was created
    output_file = visualizer.output_dir / "directory_summary.html"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_create_comparison_plots(visualizer, sample_directory_metrics):
    """Test creation of comparison plots."""
    visualizer._create_comparison_plots(sample_directory_metrics)
    
    # Check if output files were created
    expected_files = [
        "metric_correlations.html",
        "metric_comparisons.html"
    ]
    
    for file in expected_files:
        output_file = visualizer.output_dir / file
        assert output_file.exists()
        assert output_file.stat().st_size > 0

def test_create_distribution_plots(visualizer, sample_directory_metrics):
    """Test creation of distribution plots."""
    visualizer._create_distribution_plots(sample_directory_metrics)
    
    # Check if output file was created
    output_file = visualizer.output_dir / "metric_distributions.html"
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_main_function(tmp_path):
    """Test the main function with sample metrics."""
    # Create sample metrics file
    metrics_file = tmp_path / "metrics.json"
    sample_metrics = {
        'complexity': 5,
        'maintainability': 85.5,
        'lines_of_code': 100,
        'comment_ratio': 0.2,
        'function_count': 3,
        'avg_function_length': 15.5,
        'variable_count': 10,
        'nesting_depth': 2,
        'duplication_ratio': 0.1,
        'naming_score': 90.0,
        'cyclomatic_complexity': 6,
        'cognitive_complexity': 4,
        'halstead_metrics': {
            'program_length': 150,
            'vocabulary': 50,
            'volume': 750,
            'difficulty': 15,
            'effort': 11250,
            'time': 625,
            'bugs': 0.25
        },
        'maintainability_index': 80.0
    }
    
    with open(metrics_file, 'w') as f:
        json.dump(sample_metrics, f)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Import and run main function
    from src.refactoring.metrics_visualizer import main
    import sys
    sys.argv = ['metrics_visualizer.py', str(metrics_file), '-o', str(output_dir)]
    main()
    
    # Check if output files were created
    assert (output_dir / "file_metrics.html").exists()
    assert (output_dir / "file_radar.html").exists()

def test_main_function_directory(tmp_path):
    """Test the main function with directory metrics."""
    # Create sample directory metrics file
    metrics_file = tmp_path / "metrics.json"
    sample_directory_metrics = {
        'file1.py': {
            'complexity': 5,
            'maintainability': 85.5,
            'lines_of_code': 100,
            'comment_ratio': 0.2,
            'function_count': 3,
            'avg_function_length': 15.5,
            'variable_count': 10,
            'nesting_depth': 2,
            'duplication_ratio': 0.1,
            'naming_score': 90.0,
            'cyclomatic_complexity': 6,
            'cognitive_complexity': 4,
            'halstead_metrics': {
                'program_length': 150,
                'vocabulary': 50,
                'volume': 750,
                'difficulty': 15,
                'effort': 11250,
                'time': 625,
                'bugs': 0.25
            },
            'maintainability_index': 80.0
        },
        'file2.py': {
            'complexity': 8,
            'maintainability': 75.0,
            'lines_of_code': 150,
            'comment_ratio': 0.15,
            'function_count': 5,
            'avg_function_length': 20.0,
            'variable_count': 15,
            'nesting_depth': 3,
            'duplication_ratio': 0.2,
            'naming_score': 85.0,
            'cyclomatic_complexity': 9,
            'cognitive_complexity': 7,
            'halstead_metrics': {
                'program_length': 200,
                'vocabulary': 60,
                'volume': 1000,
                'difficulty': 20,
                'effort': 20000,
                'time': 1111,
                'bugs': 0.33
            },
            'maintainability_index': 70.0
        }
    }
    
    with open(metrics_file, 'w') as f:
        json.dump(sample_directory_metrics, f)
    
    # Create output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Import and run main function
    from src.refactoring.metrics_visualizer import main
    import sys
    sys.argv = ['metrics_visualizer.py', str(metrics_file), '-o', str(output_dir)]
    main()
    
    # Check if output files were created
    expected_files = [
        "directory_summary.html",
        "metric_correlations.html",
        "metric_comparisons.html",
        "metric_distributions.html",
        "radar_chart.html"
    ]
    
    for file in expected_files:
        assert (output_dir / file).exists()

def test_plot_radar_chart(visualizer, sample_metrics):
    """Test radar chart plotting."""
    visualizer.plot_radar_chart(sample_metrics, "Test Radar Chart", "radar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "radar.png"))

def test_plot_bar_chart(visualizer, sample_metrics):
    """Test bar chart plotting."""
    visualizer.plot_bar_chart(sample_metrics, "Test Bar Chart", "bar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "bar.png"))

def test_plot_heatmap(visualizer):
    """Test heatmap plotting."""
    metrics = {
        'Category1': {'Metric1': 0.8, 'Metric2': 0.7},
        'Category2': {'Metric1': 0.9, 'Metric2': 0.8}
    }
    visualizer.plot_heatmap(metrics, "Test Heatmap", "heatmap.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "heatmap.png"))

def test_plot_trend(visualizer, sample_metrics_history):
    """Test trend plotting."""
    visualizer.plot_trend(sample_metrics_history, "Test Trend", "trend.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "trend.png"))

def test_plot_comparison(visualizer, sample_comparison_metrics):
    """Test comparison plotting."""
    visualizer.plot_comparison(
        sample_comparison_metrics['before'],
        sample_comparison_metrics['after'],
        "Test Comparison",
        "comparison.png"
    )
    assert os.path.exists(os.path.join(visualizer.output_dir, "comparison.png"))

def test_plot_distribution(visualizer, sample_metrics):
    """Test distribution plotting."""
    visualizer.plot_distribution(sample_metrics, "Test Distribution", "distribution.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "distribution.png"))

def test_generate_report(visualizer):
    """Test report generation."""
    metrics = {
        'complexity': {
            'cyclomatic_complexity': 0.7,
            'cognitive_complexity': 0.8
        },
        'maintainability': {
            'size': 0.9,
            'documentation': 0.85
        }
    }
    visualizer.generate_report(metrics, "report.html")
    assert os.path.exists(os.path.join(visualizer.output_dir, "report.html"))

def test_metric_descriptions(visualizer):
    """Test metric descriptions."""
    # Test known metric description
    desc = visualizer._get_metric_description('complexity', 'cyclomatic_complexity')
    assert desc == 'Measures the number of linearly independent paths through a program'
    
    # Test unknown category
    desc = visualizer._get_metric_description('unknown', 'metric')
    assert desc == 'No description available'
    
    # Test unknown metric in known category
    desc = visualizer._get_metric_description('complexity', 'unknown')
    assert desc == 'No description available'

def test_output_directory_creation(visualizer):
    """Test output directory creation."""
    # Remove output directory
    shutil.rmtree(visualizer.output_dir)
    
    # Create new visualizer instance
    new_visualizer = MetricsVisualizer(visualizer.output_dir)
    
    # Check if directory was created
    assert os.path.exists(new_visualizer.output_dir)

def test_plot_with_empty_metrics(visualizer):
    """Test plotting with empty metrics."""
    empty_metrics = {}
    
    # Test radar chart
    visualizer.plot_radar_chart(empty_metrics, "Empty Radar", "empty_radar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "empty_radar.png"))
    
    # Test bar chart
    visualizer.plot_bar_chart(empty_metrics, "Empty Bar", "empty_bar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "empty_bar.png"))
    
    # Test heatmap
    empty_heatmap = {}
    visualizer.plot_heatmap(empty_heatmap, "Empty Heatmap", "empty_heatmap.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "empty_heatmap.png"))

def test_plot_with_single_value(visualizer):
    """Test plotting with single value metrics."""
    single_metric = {'single': 0.5}
    
    # Test radar chart
    visualizer.plot_radar_chart(single_metric, "Single Radar", "single_radar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "single_radar.png"))
    
    # Test bar chart
    visualizer.plot_bar_chart(single_metric, "Single Bar", "single_bar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "single_bar.png"))
    
    # Test heatmap
    single_heatmap = {'Category': {'Metric': 0.5}}
    visualizer.plot_heatmap(single_heatmap, "Single Heatmap", "single_heatmap.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "single_heatmap.png"))

def test_plot_with_extreme_values(visualizer):
    """Test plotting with extreme values."""
    extreme_metrics = {
        'very_low': 0.0,
        'very_high': 1.0,
        'negative': -0.5,
        'large': 100.0
    }
    
    # Test radar chart
    visualizer.plot_radar_chart(extreme_metrics, "Extreme Radar", "extreme_radar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "extreme_radar.png"))
    
    # Test bar chart
    visualizer.plot_bar_chart(extreme_metrics, "Extreme Bar", "extreme_bar.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "extreme_bar.png"))
    
    # Test heatmap
    extreme_heatmap = {
        'Category1': {'Metric1': 0.0, 'Metric2': 1.0},
        'Category2': {'Metric1': -0.5, 'Metric2': 100.0}
    }
    visualizer.plot_heatmap(extreme_heatmap, "Extreme Heatmap", "extreme_heatmap.png")
    assert os.path.exists(os.path.join(visualizer.output_dir, "extreme_heatmap.png")) 