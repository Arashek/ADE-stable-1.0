import pytest
from ..enhanced_code_analysis import EnhancedCodeAnalyzer

@pytest.fixture
def analyzer():
    return EnhancedCodeAnalyzer()

@pytest.fixture
def sample_python_code():
    return """
import os
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, db_connection: str):
        self._db = db_connection
        self._users: Dict[str, User] = {}
        
    def get_user(self, user_id: str) -> Optional[User]:
        if user_id in self._users:
            return self._users[user_id]
        return None
        
    def add_user(self, user: User) -> bool:
        if user.id in self._users:
            return False
        self._users[user.id] = user
        return True
        
    def _validate_user(self, user: User) -> bool:
        return user.id is not None and user.name is not None

class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self._created_at = None
"""

@pytest.mark.asyncio
async def test_syntax_analysis(analyzer, sample_python_code):
    """Test syntax analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify imports
    assert len(analysis["syntax"]["imports"]) == 2
    assert any(imp["text"] == "import os" for imp in analysis["syntax"]["imports"])
    assert any("from typing import" in imp["text"] for imp in analysis["syntax"]["imports"])
    
    # Verify classes
    assert len(analysis["syntax"]["classes"]) == 2
    class_names = {cls["name"] for cls in analysis["syntax"]["classes"]}
    assert "UserManager" in class_names
    assert "User" in class_names
    
    # Verify functions
    assert len(analysis["syntax"]["functions"]) == 6  # 3 methods in UserManager + 1 in User
    function_names = {func["name"] for func in analysis["syntax"]["functions"]}
    assert "get_user" in function_names
    assert "add_user" in function_names
    assert "_validate_user" in function_names

@pytest.mark.asyncio
async def test_semantic_analysis(analyzer, sample_python_code):
    """Test semantic analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify scope analysis
    assert "scope" in analysis["semantics"]
    assert "UserManager" in analysis["semantics"]["scope"]
    assert "User" in analysis["semantics"]["scope"]
    
    # Verify references
    assert "references" in analysis["semantics"]
    assert "user_id" in analysis["semantics"]["references"]
    assert "user" in analysis["semantics"]["references"]
    
    # Verify definitions
    assert "definitions" in analysis["semantics"]
    assert "self" in analysis["semantics"]["definitions"]

@pytest.mark.asyncio
async def test_type_analysis(analyzer, sample_python_code):
    """Test type analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify variable types
    assert "variables" in analysis["types"]
    assert "db_connection" in analysis["types"]["variables"]
    assert analysis["types"]["variables"]["db_connection"]["type"] == "str"
    
    # Verify function return types
    assert "functions" in analysis["types"]
    assert "get_user" in analysis["types"]["functions"]
    assert analysis["types"]["functions"]["get_user"]["return_type"] == "Optional[User]"
    
    # Verify class attributes
    assert "classes" in analysis["types"]
    assert "User" in analysis["types"]["classes"]
    assert "id" in {attr["name"] for attr in analysis["types"]["classes"]["User"]["attributes"]}
    assert "name" in {attr["name"] for attr in analysis["types"]["classes"]["User"]["attributes"]}

@pytest.mark.asyncio
async def test_control_flow_analysis(analyzer, sample_python_code):
    """Test control flow analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify branches
    assert "branches" in analysis["control_flow"]
    assert len(analysis["control_flow"]["branches"]) == 2  # Two if statements
    
    # Verify complexity metrics
    assert "complexity" in analysis["control_flow"]
    assert "cyclomatic" in analysis["control_flow"]["complexity"]
    assert analysis["control_flow"]["complexity"]["cyclomatic"] > 0

@pytest.mark.asyncio
async def test_data_flow_analysis(analyzer, sample_python_code):
    """Test data flow analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify variable definitions
    assert "definitions" in analysis["data_flow"]
    assert "self._users" in analysis["data_flow"]["definitions"]
    
    # Verify variable uses
    assert "uses" in analysis["data_flow"]
    assert "user_id" in analysis["data_flow"]["uses"]
    assert "user" in analysis["data_flow"]["uses"]
    
    # Verify data flow graph
    assert "data_flow_graph" in analysis["data_flow"]

@pytest.mark.asyncio
async def test_dependency_analysis(analyzer, sample_python_code):
    """Test dependency analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify imports
    assert "imports" in analysis["dependencies"]
    assert len(analysis["dependencies"]["imports"]) == 2
    
    # Verify exports
    assert "exports" in analysis["dependencies"]
    assert len(analysis["dependencies"]["exports"]) == 2  # Two classes
    
    # Verify relationships
    assert "relationships" in analysis["dependencies"]

@pytest.mark.asyncio
async def test_pattern_analysis(analyzer, sample_python_code):
    """Test pattern analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify pattern detection
    assert "design_patterns" in analysis["patterns"]
    assert "anti_patterns" in analysis["patterns"]
    assert "code_smells" in analysis["patterns"]
    assert "best_practices" in analysis["patterns"]

@pytest.mark.asyncio
async def test_intent_analysis(analyzer, sample_python_code):
    """Test code intent analysis capabilities."""
    analysis = analyzer.analyze_code(sample_python_code, "python", "test.py")
    
    # Verify intent features
    assert "purpose" in analysis["intent"]
    assert "complexity" in analysis["intent"]
    assert "maintainability" in analysis["intent"]
    assert "readability" in analysis["intent"]
    
    # Verify metrics are within expected ranges
    assert 0 <= analysis["intent"]["complexity"] <= 1.0
    assert 0 <= analysis["intent"]["maintainability"] <= 1.0
    assert 0 <= analysis["intent"]["readability"] <= 1.0 