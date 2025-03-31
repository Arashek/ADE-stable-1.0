import pytest
import os
import tempfile
from ..project_analysis import ProjectAnalyzer, ProjectMetrics, ProjectPattern

@pytest.fixture
def project_analyzer():
    return ProjectAnalyzer()

@pytest.fixture
def sample_project():
    """Create a sample project structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample Python files
        os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "tests"), exist_ok=True)
        
        # Create a sample class with singleton pattern
        with open(os.path.join(temp_dir, "src", "singleton.py"), "w") as f:
            f.write("""
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connection = None
            self.initialized = True
            
    def connect(self):
        if not self.connection:
            self.connection = "Connected to database"
        return self.connection
""")
            
        # Create a sample class with factory pattern
        with open(os.path.join(temp_dir, "src", "factory.py"), "w") as f:
            f.write("""
from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def create(self):
        pass
        
class PDFDocument(Document):
    def create(self):
        return "Created PDF document"
        
class WordDocument(Document):
    def create(self):
        return "Created Word document"
        
class DocumentFactory:
    @staticmethod
    def create_document(doc_type):
        if doc_type == "pdf":
            return PDFDocument()
        elif doc_type == "word":
            return WordDocument()
        raise ValueError("Invalid document type")
""")
            
        # Create a sample class with observer pattern
        with open(os.path.join(temp_dir, "src", "observer.py"), "w") as f:
            f.write("""
class Subject:
    def __init__(self):
        self.observers = []
        
    def attach(self, observer):
        self.observers.append(observer)
        
    def detach(self, observer):
        self.observers.remove(observer)
        
    def notify(self):
        for observer in self.observers:
            observer.update()
            
class Observer:
    def __init__(self, subject):
        self.subject = subject
        self.subject.attach(self)
        
    def update(self):
        print("Observer updated")
""")
            
        # Create a sample test file
        with open(os.path.join(temp_dir, "tests", "test_singleton.py"), "w") as f:
            f.write("""
import pytest
from src.singleton import DatabaseConnection

def test_singleton():
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    assert db1 is db2
    assert db1.connect() == "Connected to database"
""")
            
        yield temp_dir

def test_project_analysis(project_analyzer, sample_project):
    """Test project-level analysis."""
    analysis = project_analyzer.analyze_project(sample_project)
    
    # Check analysis structure
    assert "metrics" in analysis
    assert "patterns" in analysis
    assert "dependencies" in analysis
    assert "architecture" in analysis
    assert "code_quality" in analysis
    assert "recommendations" in analysis
    
    # Check metrics
    metrics = analysis["metrics"]
    assert isinstance(metrics, ProjectMetrics)
    assert metrics.total_files > 0
    assert metrics.total_lines > 0
    assert metrics.total_classes > 0
    assert metrics.total_functions > 0
    assert 0 <= metrics.complexity_score <= 1
    assert 0 <= metrics.maintainability_score <= 1
    assert 0 <= metrics.testability_score <= 1
    assert 0 <= metrics.reusability_score <= 1
    assert 0 <= metrics.pattern_coverage <= 1
    assert 0 <= metrics.code_quality_score <= 1
    
    # Check patterns
    patterns = analysis["patterns"]
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    
    # Check for specific patterns
    pattern_types = {pattern.type for pattern in patterns}
    assert "design" in pattern_types
    assert "architectural" in pattern_types
    
    # Check architecture
    architecture = analysis["architecture"]
    assert "components" in architecture
    assert "relationships" in architecture
    assert "layers" in architecture
    assert "metrics" in architecture
    
    # Check architecture metrics
    arch_metrics = architecture["metrics"]
    assert "component_count" in arch_metrics
    assert "relationship_count" in arch_metrics
    assert "layer_count" in arch_metrics
    assert "coupling" in arch_metrics
    assert "cohesion" in arch_metrics
    assert 0 <= arch_metrics["coupling"] <= 1
    assert 0 <= arch_metrics["cohesion"] <= 1

def test_pattern_detection(project_analyzer, sample_project):
    """Test pattern detection capabilities."""
    analysis = project_analyzer.analyze_project(sample_project)
    patterns = analysis["patterns"]
    
    # Check for singleton pattern
    singleton_patterns = [p for p in patterns if p.name == "Singleton Pattern Cluster"]
    assert len(singleton_patterns) > 0
    singleton = singleton_patterns[0]
    assert singleton.type == "design"
    assert singleton.confidence > 0.5
    assert "src/singleton.py" in singleton.files
    
    # Check for factory pattern
    factory_patterns = [p for p in patterns if p.name == "Creational Pattern Cluster"]
    assert len(factory_patterns) > 0
    factory = factory_patterns[0]
    assert factory.type == "design"
    assert factory.confidence > 0.5
    assert "src/factory.py" in factory.files
    
    # Check for observer pattern
    observer_patterns = [p for p in patterns if p.name == "Behavioral Pattern Cluster"]
    assert len(observer_patterns) > 0
    observer = observer_patterns[0]
    assert observer.type == "design"
    assert observer.confidence > 0.5
    assert "src/observer.py" in observer.files

def test_architecture_analysis(project_analyzer, sample_project):
    """Test architecture analysis capabilities."""
    analysis = project_analyzer.analyze_project(sample_project)
    architecture = analysis["architecture"]
    
    # Check components
    components = architecture["components"]
    assert len(components) > 0
    for component in components:
        assert "name" in component
        assert "files" in component
        assert "size" in component
        assert "cohesion" in component
        assert 0 <= component["cohesion"] <= 1
        
    # Check relationships
    relationships = architecture["relationships"]
    assert len(relationships) > 0
    for relationship in relationships:
        assert "source" in relationship
        assert "target" in relationship
        assert "type" in relationship
        assert relationship["type"] in ["internal", "external", "implementation"]
        
    # Check layers
    layers = architecture["layers"]
    assert len(layers) > 0
    for layer in layers:
        assert "name" in layer
        assert "files" in layer
        assert "dependencies" in layer

def test_metrics_calculation(project_analyzer, sample_project):
    """Test project metrics calculation."""
    analysis = project_analyzer.analyze_project(sample_project)
    metrics = analysis["metrics"]
    
    # Check basic metrics
    assert metrics.total_files >= 4  # At least 4 files in sample project
    assert metrics.total_lines > 0
    assert metrics.total_classes >= 3  # At least 3 classes in sample project
    assert metrics.total_functions >= 5  # At least 5 functions in sample project
    
    # Check quality metrics
    assert 0 <= metrics.complexity_score <= 1
    assert 0 <= metrics.maintainability_score <= 1
    assert 0 <= metrics.testability_score <= 1
    assert 0 <= metrics.reusability_score <= 1
    
    # Check pattern coverage
    assert 0 <= metrics.pattern_coverage <= 1
    
    # Check overall code quality
    assert 0 <= metrics.code_quality_score <= 1

def test_recommendations(project_analyzer, sample_project):
    """Test recommendation generation."""
    analysis = project_analyzer.analyze_project(sample_project)
    recommendations = analysis["recommendations"]
    
    # Check recommendations structure
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    # Check recommendation content
    for recommendation in recommendations:
        assert isinstance(recommendation, str)
        assert len(recommendation) > 0
        assert recommendation.endswith(".")  # Should be a complete sentence

def test_language_detection(project_analyzer):
    """Test programming language detection."""
    assert project_analyzer._detect_language("test.py") == "python"
    assert project_analyzer._detect_language("test.java") == "java"
    assert project_analyzer._detect_language("test.ts") == "typescript"
    assert project_analyzer._detect_language("test.cpp") == "cpp"
    assert project_analyzer._detect_language("test.h") == "cpp"
    assert project_analyzer._detect_language("test.cs") == "csharp"
    assert project_analyzer._detect_language("test.go") == "go"
    assert project_analyzer._detect_language("test.rs") == "rust"
    assert project_analyzer._detect_language("test.rb") == "ruby"
    assert project_analyzer._detect_language("test.php") == "php"
    assert project_analyzer._detect_language("test.swift") == "swift"
    assert project_analyzer._detect_language("test.kt") == "kotlin"
    assert project_analyzer._detect_language("test.unknown") == "unknown"

def test_code_file_detection(project_analyzer):
    """Test code file detection."""
    assert project_analyzer._is_code_file("test.py")
    assert project_analyzer._is_code_file("test.java")
    assert project_analyzer._is_code_file("test.ts")
    assert project_analyzer._is_code_file("test.cpp")
    assert project_analyzer._is_code_file("test.h")
    assert project_analyzer._is_code_file("test.cs")
    assert project_analyzer._is_code_file("test.go")
    assert project_analyzer._is_code_file("test.rs")
    assert project_analyzer._is_code_file("test.rb")
    assert project_analyzer._is_code_file("test.php")
    assert project_analyzer._is_code_file("test.swift")
    assert project_analyzer._is_code_file("test.kt")
    assert not project_analyzer._is_code_file("test.txt")
    assert not project_analyzer._is_code_file("test.md")
    assert not project_analyzer._is_code_file("test.json") 