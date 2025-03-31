import pytest
import ast
from pathlib import Path
from typing import List, Dict
import numpy as np
from src.refactoring.refactoring_trainer import (
    RefactoringTrainer,
    CodeQualityMetrics,
    RefactoringExample
)

@pytest.fixture
def trainer():
    """Create a RefactoringTrainer instance for testing."""
    return RefactoringTrainer(output_dir="test_data/refactoring")

@pytest.fixture
def sample_code():
    """Create a sample code with code smells."""
    return """
class UserManager:
    def process_user_data(self, user_data):
        if user_data.get('status') == 'active' and user_data.get('age') > 18:
            if user_data.get('subscription') == 'premium':
                user_id = user_data.get('id')
                user_name = user_data.get('name')
                user_email = user_data.get('email')
                
                self.update_user_status(user_id, 'verified')
                self.send_welcome_email(user_email, user_name)
                self.create_user_profile(user_id, user_name, user_email)
                return True
        return False
    
    def update_user_status(self, user_id, status):
        if user_id and status:
            if status in ['active', 'inactive', 'suspended']:
                if self.validate_user_id(user_id):
                    self.db.update('users', {'status': status}, {'id': user_id})
                    return True
        return False
"""

def test_initialization(trainer):
    """Test RefactoringTrainer initialization."""
    assert trainer.output_dir == Path("test_data/refactoring")
    assert trainer.output_dir.exists()
    assert isinstance(trainer.code_smells, dict)
    assert isinstance(trainer.refactoring_patterns, dict)

def test_code_quality_analysis(trainer, sample_code):
    """Test code quality analysis."""
    metrics = trainer._analyze_code_quality(sample_code)
    
    assert isinstance(metrics, CodeQualityMetrics)
    assert metrics.cyclomatic_complexity >= 0
    assert metrics.maintainability_index >= 0
    assert metrics.lines_of_code > 0
    assert 0 <= metrics.comment_ratio <= 1
    assert metrics.function_count > 0
    assert metrics.avg_function_length >= 0
    assert metrics.variable_count > 0
    assert metrics.nesting_depth >= 0
    assert 0 <= metrics.duplication_ratio <= 1
    assert 0 <= metrics.naming_score <= 1

def test_code_smell_detection(trainer, sample_code):
    """Test code smell detection."""
    smells = trainer._identify_code_smells(sample_code)
    
    assert isinstance(smells, list)
    assert "long_method" in smells
    assert "complex_condition" in smells
    assert "duplicate_code" in smells

def test_duplication_ratio_calculation(trainer, sample_code):
    """Test code duplication ratio calculation."""
    ratio = trainer._calculate_duplication_ratio(sample_code)
    
    assert isinstance(ratio, float)
    assert 0 <= ratio <= 1

def test_naming_score_calculation(trainer, sample_code):
    """Test naming score calculation."""
    score = trainer._calculate_naming_score(ast.parse(sample_code))
    
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_nesting_depth_calculation(trainer, sample_code):
    """Test nesting depth calculation."""
    depth = trainer._calculate_nesting_depth(ast.parse(sample_code))
    
    assert isinstance(depth, int)
    assert depth >= 0

def test_primitive_obsession_detection(trainer, sample_code):
    """Test primitive obsession detection."""
    has_obsession = trainer._has_primitive_obsession(ast.parse(sample_code))
    
    assert isinstance(has_obsession, bool)

def test_switch_statement_detection(trainer, sample_code):
    """Test switch statement detection."""
    has_switch = trainer._has_switch_statement(ast.parse(sample_code))
    
    assert isinstance(has_switch, bool)

def test_data_clumps_detection(trainer, sample_code):
    """Test data clumps detection."""
    has_clumps = trainer._has_data_clumps(ast.parse(sample_code))
    
    assert isinstance(has_clumps, bool)

def test_feature_envy_detection(trainer, sample_code):
    """Test feature envy detection."""
    has_envy = trainer._has_feature_envy(ast.parse(sample_code))
    
    assert isinstance(has_envy, bool)

def test_difficulty_calculation(trainer, sample_code):
    """Test refactoring difficulty calculation."""
    # Create a refactored version of the code
    refactored_code = """
class UserManager:
    def process_user_data(self, user_data):
        if not self._is_valid_user(user_data):
            return False
            
        user = self._extract_user_data(user_data)
        self._process_valid_user(user)
        return True
    
    def _is_valid_user(self, user_data):
        return (user_data.get('status') == 'active' and 
                user_data.get('age') > 18 and
                user_data.get('subscription') == 'premium')
    
    def _extract_user_data(self, user_data):
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'email': user_data.get('email')
        }
    
    def _process_valid_user(self, user):
        self.update_user_status(user['id'], 'verified')
        self.send_welcome_email(user['email'], user['name'])
        self.create_user_profile(user['id'], user['name'], user['email'])
"""
    
    difficulty = trainer._calculate_difficulty(sample_code, refactored_code)
    
    assert isinstance(difficulty, float)
    assert 0 <= difficulty <= 1

def test_improvement_metrics_calculation(trainer):
    """Test improvement metrics calculation."""
    before = CodeQualityMetrics(
        cyclomatic_complexity=10,
        maintainability_index=50,
        lines_of_code=100,
        comment_ratio=0.1,
        function_count=5,
        avg_function_length=20,
        variable_count=15,
        nesting_depth=4,
        duplication_ratio=0.3,
        naming_score=0.7
    )
    
    after = CodeQualityMetrics(
        cyclomatic_complexity=5,
        maintainability_index=70,
        lines_of_code=80,
        comment_ratio=0.2,
        function_count=8,
        avg_function_length=10,
        variable_count=12,
        nesting_depth=2,
        duplication_ratio=0.1,
        naming_score=0.9
    )
    
    improvement = trainer._calculate_improvement_metrics(before, after)
    
    assert isinstance(improvement, float)
    assert improvement > 0

def test_correctness_check(trainer, sample_code):
    """Test refactoring correctness check."""
    # Create a refactored version that maintains functionality
    refactored_code = """
class UserManager:
    def process_user_data(self, user_data):
        if not self._is_valid_user(user_data):
            return False
            
        user = self._extract_user_data(user_data)
        self._process_valid_user(user)
        return True
    
    def _is_valid_user(self, user_data):
        return (user_data.get('status') == 'active' and 
                user_data.get('age') > 18 and
                user_data.get('subscription') == 'premium')
    
    def _extract_user_data(self, user_data):
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'email': user_data.get('email')
        }
    
    def _process_valid_user(self, user):
        self.update_user_status(user['id'], 'verified')
        self.send_welcome_email(user['email'], user['name'])
        self.create_user_profile(user['id'], user['name'], user['email'])
"""
    
    correctness = trainer._check_correctness(sample_code, refactored_code)
    
    assert isinstance(correctness, float)
    assert 0 <= correctness <= 1
    assert correctness > 0.5  # Should be high for this refactoring

def test_relevance_evaluation(trainer, sample_code):
    """Test refactoring relevance evaluation."""
    # Create a refactored version
    refactored_code = """
class UserManager:
    def process_user_data(self, user_data):
        if not self._is_valid_user(user_data):
            return False
            
        user = self._extract_user_data(user_data)
        self._process_valid_user(user)
        return True
    
    def _is_valid_user(self, user_data):
        return (user_data.get('status') == 'active' and 
                user_data.get('age') > 18 and
                user_data.get('subscription') == 'premium')
    
    def _extract_user_data(self, user_data):
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'email': user_data.get('email')
        }
    
    def _process_valid_user(self, user):
        self.update_user_status(user['id'], 'verified')
        self.send_welcome_email(user['email'], user['name'])
        self.create_user_profile(user['id'], user['name'], user['email'])
"""
    
    relevance = trainer._evaluate_relevance(
        sample_code, refactored_code,
        trainer._analyze_code_quality(sample_code),
        trainer._analyze_code_quality(refactored_code)
    )
    
    assert isinstance(relevance, float)
    assert 0 <= relevance <= 1
    assert relevance > 0.5  # Should be high for this refactoring

def test_dataset_generation(trainer):
    """Test dataset generation."""
    examples = trainer.generate_dataset(num_examples=5)
    
    assert isinstance(examples, list)
    assert len(examples) == 5
    
    for example in examples:
        assert isinstance(example, RefactoringExample)
        assert isinstance(example.original_code, str)
        assert isinstance(example.refactored_code, str)
        assert isinstance(example.quality_before, CodeQualityMetrics)
        assert isinstance(example.quality_after, CodeQualityMetrics)
        assert isinstance(example.refactoring_steps, list)
        assert isinstance(example.code_smells, list)
        assert isinstance(example.benefits, list)
        assert isinstance(example.difficulty, float)
        assert isinstance(example.category, str)

def test_refactoring_evaluation(trainer, sample_code):
    """Test complete refactoring evaluation."""
    # Create a refactored version
    refactored_code = """
class UserManager:
    def process_user_data(self, user_data):
        if not self._is_valid_user(user_data):
            return False
            
        user = self._extract_user_data(user_data)
        self._process_valid_user(user)
        return True
    
    def _is_valid_user(self, user_data):
        return (user_data.get('status') == 'active' and 
                user_data.get('age') > 18 and
                user_data.get('subscription') == 'premium')
    
    def _extract_user_data(self, user_data):
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'email': user_data.get('email')
        }
    
    def _process_valid_user(self, user):
        self.update_user_status(user['id'], 'verified')
        self.send_welcome_email(user['email'], user['name'])
        self.create_user_profile(user['id'], user['name'], user['email'])
"""
    
    metrics = trainer.evaluate_refactoring(sample_code, refactored_code)
    
    assert isinstance(metrics, dict)
    assert "improvement" in metrics
    assert "correctness" in metrics
    assert "relevance" in metrics
    
    for score in metrics.values():
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for this refactoring

def test_categorization(trainer):
    """Test refactoring categorization."""
    categories = {
        "method_refactoring": ["long_method", "complex_condition"],
        "class_refactoring": ["large_class", "feature_envy"],
        "duplication_refactoring": ["duplicate_code"],
        "data_refactoring": ["primitive_obsession", "data_clumps"],
        "control_refactoring": ["switch_statement"]
    }
    
    for expected_category, smells in categories.items():
        category = trainer._categorize_refactoring(smells)
        assert category == expected_category
    
    # Test general category
    category = trainer._categorize_refactoring(["unknown_smell"])
    assert category == "general_refactoring" 