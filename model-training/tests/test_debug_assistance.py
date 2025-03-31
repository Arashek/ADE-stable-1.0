import pytest
from pathlib import Path
import json
import ast
from typing import Dict, List

from ade_model_training.data.debug_dataset_generator import DebugDatasetGenerator
from ade_model_training.data.bug_introducer import BugIntroducer
from ade_model_training.evaluation.debug_evaluator import DebugEvaluator

@pytest.fixture
def dataset_generator():
    """Create a DebugDatasetGenerator instance."""
    return DebugDatasetGenerator(output_dir="test_data/debug_dataset")

@pytest.fixture
def bug_introducer():
    """Create a BugIntroducer instance."""
    return BugIntroducer()

@pytest.fixture
def evaluator():
    """Create a DebugEvaluator instance."""
    return DebugEvaluator(output_dir="test_data/evaluation")

@pytest.fixture
def sample_working_code():
    """Create a sample working code snippet."""
    return """
def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total += num
        count += 1
    return total / count

result = calculate_average([1, 2, 3, 4, 5])
print(result)
"""

def test_dataset_generator_initialization(dataset_generator):
    """Test initialization of DebugDatasetGenerator."""
    assert dataset_generator.output_dir.exists()
    assert isinstance(dataset_generator.error_patterns, dict)
    assert "type_error" in dataset_generator.error_patterns
    assert "name_error" in dataset_generator.error_patterns

def test_dataset_generation(dataset_generator):
    """Test dataset generation."""
    dataset = dataset_generator.generate_dataset(num_examples=5)
    assert len(dataset) == 5
    assert all(isinstance(item, dict) for item in dataset)
    assert all("error_type" in item for item in dataset)
    assert all("buggy_code" in item for item in dataset)
    assert all("error_message" in item for item in dataset)
    assert all("fixed_code" in item for item in dataset)
    assert all("debugging_steps" in item for item in dataset)

def test_dataset_save_load(dataset_generator, tmp_path):
    """Test saving and loading datasets."""
    dataset = dataset_generator.generate_dataset(num_examples=3)
    filename = "test_dataset.json"
    
    # Save dataset
    dataset_generator.save_dataset(dataset, filename)
    assert (dataset_generator.output_dir / filename).exists()
    
    # Load dataset
    loaded_dataset = dataset_generator.load_dataset(filename)
    assert len(loaded_dataset) == len(dataset)
    assert loaded_dataset[0]["error_type"] == dataset[0]["error_type"]

def test_bug_introducer_initialization(bug_introducer):
    """Test initialization of BugIntroducer."""
    assert isinstance(bug_introducer.bug_patterns, dict)
    assert "type_error" in bug_introducer.bug_patterns
    assert "name_error" in bug_introducer.bug_patterns

def test_bug_introduction(bug_introducer, sample_working_code):
    """Test introducing bugs into working code."""
    error_types = ["type_error", "name_error", "index_error", "key_error", "syntax_error"]
    
    for error_type in error_types:
        buggy_code, error_message, fixed_code, steps = bug_introducer.introduce_bug(
            sample_working_code, error_type)
        
        assert isinstance(buggy_code, str)
        assert isinstance(error_message, str)
        assert isinstance(fixed_code, str)
        assert isinstance(steps, list)
        assert all(isinstance(step, str) for step in steps)

def test_bug_introduction_invalid_error_type(bug_introducer, sample_working_code):
    """Test introducing bugs with invalid error type."""
    with pytest.raises(ValueError):
        bug_introducer.introduce_bug(sample_working_code, "invalid_error_type")

def test_bug_introduction_invalid_code(bug_introducer):
    """Test introducing bugs into invalid code."""
    invalid_code = "if True\n    print('Invalid')"  # Missing colon
    with pytest.raises(ValueError):
        bug_introducer.introduce_bug(invalid_code, "type_error")

def test_evaluator_initialization(evaluator):
    """Test initialization of DebugEvaluator."""
    assert evaluator.output_dir.exists()
    assert isinstance(evaluator.metrics, dict)
    assert "error_identification" in evaluator.metrics
    assert "debugging_steps" in evaluator.metrics
    assert "fix_proposals" in evaluator.metrics

def test_error_identification_evaluation(evaluator):
    """Test evaluation of error identification."""
    true_errors = ["type_error", "name_error", "type_error"]
    predicted_errors = ["type_error", "name_error", "index_error"]
    
    metrics = evaluator.evaluate_error_identification(true_errors, predicted_errors)
    
    assert isinstance(metrics, dict)
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert all(0 <= value <= 1 for value in metrics.values())

def test_debugging_steps_evaluation(evaluator):
    """Test evaluation of debugging steps."""
    true_steps = [
        ["Identify the issue", "Fix the problem"],
        ["Check the code", "Apply the fix"]
    ]
    predicted_steps = [
        ["Find the bug", "Fix the issue"],
        ["Check the code", "Apply the fix"]
    ]
    
    metrics = evaluator.evaluate_debugging_steps(true_steps, predicted_steps)
    
    assert isinstance(metrics, dict)
    assert "completeness" in metrics
    assert "correctness" in metrics
    assert "clarity" in metrics
    assert all(0 <= value <= 1 for value in metrics.values())

def test_fix_proposals_evaluation(evaluator):
    """Test evaluation of fix proposals."""
    true_fixes = [
        "result = int('5') + 3",
        "my_list.append(4)"
    ]
    predicted_fixes = [
        "result = int('5') + 3",
        "my_list.append(4)"
    ]
    
    metrics = evaluator.evaluate_fix_proposals(true_fixes, predicted_fixes)
    
    assert isinstance(metrics, dict)
    assert "correctness" in metrics
    assert "efficiency" in metrics
    assert "readability" in metrics
    assert all(0 <= value <= 1 for value in metrics.values())

def test_full_evaluation(evaluator):
    """Test full evaluation process."""
    test_data = [
        {
            "error_type": "type_error",
            "predicted_error": "type_error",
            "debugging_steps": ["Identify issue", "Fix problem"],
            "predicted_steps": ["Find bug", "Fix issue"],
            "fixed_code": "result = int('5') + 3",
            "predicted_fix": "result = int('5') + 3"
        }
    ]
    
    metrics = evaluator.evaluate(test_data)
    
    assert isinstance(metrics, dict)
    assert all(isinstance(category_metrics, dict) for category_metrics in metrics.values())
    assert all(0 <= value <= 1 for category_metrics in metrics.values() 
              for value in category_metrics.values())

def test_evaluation_save_load(evaluator, tmp_path):
    """Test saving and loading evaluation results."""
    test_data = [
        {
            "error_type": "type_error",
            "predicted_error": "type_error",
            "debugging_steps": ["Identify issue", "Fix problem"],
            "predicted_steps": ["Find bug", "Fix issue"],
            "fixed_code": "result = int('5') + 3",
            "predicted_fix": "result = int('5') + 3"
        }
    ]
    
    metrics = evaluator.evaluate(test_data)
    filename = "test_evaluation.json"
    
    # Save evaluation
    evaluator.save_evaluation(metrics, filename)
    assert (evaluator.output_dir / filename).exists()
    
    # Load evaluation
    loaded_metrics = evaluator.load_evaluation(filename)
    assert loaded_metrics == metrics

def test_similar_step():
    """Test step similarity calculation."""
    from ade_model_training.evaluation.debug_evaluator import similar_step
    
    step1 = "Identify the type mismatch"
    step2 = "Find the type mismatch"
    assert similar_step(step1, step2) is True
    
    step1 = "Check the code"
    step2 = "Run the tests"
    assert similar_step(step1, step2) is False

def test_similar_code():
    """Test code similarity calculation."""
    from ade_model_training.evaluation.debug_evaluator import similar_code
    
    code1 = "result = int('5') + 3"
    code2 = "result = int('5') + 3"
    assert similar_code(code1, code2) is True
    
    code1 = "result = int('5') + 3"
    code2 = "result = float('5.0') + 3"
    assert similar_code(code1, code2) is False

def test_calculate_readability():
    """Test code readability calculation."""
    from ade_model_training.evaluation.debug_evaluator import calculate_readability
    
    code = "result = int('5') + 3"
    readability = calculate_readability(code)
    assert 0 <= readability <= 1
    
    code = "x = 1\ny = 2\nz = x + y\nprint(z)"
    readability = calculate_readability(code)
    assert 0 <= readability <= 1 