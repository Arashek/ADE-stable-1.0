import pytest
from ..language_analyzers import (
    LanguageAnalyzerFactory,
    PythonAnalyzer,
    JavaAnalyzer,
    TypeScriptAnalyzer
)

@pytest.fixture
def python_analyzer():
    return PythonAnalyzer()

@pytest.fixture
def java_analyzer():
    return JavaAnalyzer()

@pytest.fixture
def typescript_analyzer():
    return TypeScriptAnalyzer()

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
"""

@pytest.fixture
def sample_java_code():
    return """
import java.util.List;
import java.util.Map;

public class UserManager {
    private String dbConnection;
    private Map<String, User> users;
    
    public UserManager(String dbConnection) {
        this.dbConnection = dbConnection;
        this.users = new HashMap<>();
    }
    
    public Optional<User> getUser(String userId) {
        if (users.containsKey(userId)) {
            return Optional.of(users.get(userId));
        }
        return Optional.empty();
    }
    
    public boolean addUser(User user) {
        if (users.containsKey(user.getId())) {
            return false;
        }
        users.put(user.getId(), user);
        return true;
    }
}
"""

@pytest.fixture
def sample_typescript_code():
    return """
import { User } from './types';

interface IUserManager {
    getUser(userId: string): User | null;
    addUser(user: User): boolean;
}

class UserManager implements IUserManager {
    private dbConnection: string;
    private users: Map<string, User>;
    
    constructor(dbConnection: string) {
        this.dbConnection = dbConnection;
        this.users = new Map();
    }
    
    getUser(userId: string): User | null {
        if (this.users.has(userId)) {
            return this.users.get(userId) || null;
        }
        return null;
    }
    
    addUser(user: User): boolean {
        if (this.users.has(user.id)) {
            return false;
        }
        this.users.set(user.id, user);
        return true;
    }
}
"""

def test_python_syntax_analysis(python_analyzer, sample_python_code):
    """Test Python syntax analysis."""
    tree = python_analyzer._parse_code(sample_python_code)
    analysis = python_analyzer.analyze_syntax(tree)
    
    # Verify imports
    assert len(analysis["imports"]) == 2
    assert any(imp["text"] == "import os" for imp in analysis["imports"])
    assert any("from typing import" in imp["text"] for imp in analysis["imports"])
    
    # Verify class definition
    assert len(analysis["classes"]) == 1
    assert analysis["classes"][0]["name"] == "UserManager"
    
    # Verify methods
    assert len(analysis["functions"]) == 3
    method_names = {func["name"] for func in analysis["functions"]}
    assert "__init__" in method_names
    assert "get_user" in method_names
    assert "add_user" in method_names

def test_java_syntax_analysis(java_analyzer, sample_java_code):
    """Test Java syntax analysis."""
    tree = java_analyzer._parse_code(sample_java_code)
    analysis = java_analyzer.analyze_syntax(tree)
    
    # Verify imports
    assert len(analysis["imports"]) == 2
    assert any("java.util.List" in imp["text"] for imp in analysis["imports"])
    assert any("java.util.Map" in imp["text"] for imp in analysis["imports"])
    
    # Verify class definition
    assert len(analysis["classes"]) == 1
    assert analysis["classes"][0]["name"] == "UserManager"
    assert "public" in analysis["classes"][0]["modifiers"]
    
    # Verify methods
    assert len(analysis["methods"]) == 3
    method_names = {method["name"] for method in analysis["methods"]}
    assert "UserManager" in method_names  # Constructor
    assert "getUser" in method_names
    assert "addUser" in method_names

def test_typescript_syntax_analysis(typescript_analyzer, sample_typescript_code):
    """Test TypeScript syntax analysis."""
    tree = typescript_analyzer._parse_code(sample_typescript_code)
    analysis = typescript_analyzer.analyze_syntax(tree)
    
    # Verify imports
    assert len(analysis["imports"]) == 1
    assert "import { User } from './types'" in analysis["imports"][0]["text"]
    
    # Verify interface
    assert len(analysis["interfaces"]) == 1
    assert analysis["interfaces"][0]["name"] == "IUserManager"
    
    # Verify class definition
    assert len(analysis["classes"]) == 1
    assert analysis["classes"][0]["name"] == "UserManager"
    assert "IUserManager" in analysis["classes"][0]["implements"]

def test_python_semantic_analysis(python_analyzer, sample_python_code):
    """Test Python semantic analysis."""
    tree = python_analyzer._parse_code(sample_python_code)
    analysis = python_analyzer.analyze_semantics(tree)
    
    # Verify scope analysis
    assert "UserManager" in analysis["scope"]
    assert "UserManager.__init__" in analysis["scope"]
    assert "UserManager.get_user" in analysis["scope"]
    assert "UserManager.add_user" in analysis["scope"]
    
    # Verify references
    assert "user_id" in analysis["references"]
    assert "user" in analysis["references"]
    assert "self" in analysis["references"]

def test_java_semantic_analysis(java_analyzer, sample_java_code):
    """Test Java semantic analysis."""
    tree = java_analyzer._parse_code(sample_java_code)
    analysis = java_analyzer.analyze_semantics(tree)
    
    # Verify scope analysis
    assert "UserManager" in analysis["scope"]
    assert "UserManager.UserManager" in analysis["scope"]  # Constructor
    assert "UserManager.getUser" in analysis["scope"]
    assert "UserManager.addUser" in analysis["scope"]
    
    # Verify references
    assert "userId" in analysis["references"]
    assert "user" in analysis["references"]
    assert "this" in analysis["references"]

def test_typescript_semantic_analysis(typescript_analyzer, sample_typescript_code):
    """Test TypeScript semantic analysis."""
    tree = typescript_analyzer._parse_code(sample_typescript_code)
    analysis = typescript_analyzer.analyze_semantics(tree)
    
    # Verify scope analysis
    assert "UserManager" in analysis["scope"]
    assert "UserManager.constructor" in analysis["scope"]
    assert "UserManager.getUser" in analysis["scope"]
    assert "UserManager.addUser" in analysis["scope"]
    
    # Verify references
    assert "userId" in analysis["references"]
    assert "user" in analysis["references"]
    assert "this" in analysis["references"]

def test_python_type_inference(python_analyzer, sample_python_code):
    """Test Python type inference."""
    tree = python_analyzer._parse_code(sample_python_code)
    analysis = python_analyzer.infer_types(tree)
    
    # Verify variable types
    assert "db_connection" in analysis["variables"]
    assert analysis["variables"]["db_connection"]["type"] == "str"
    
    # Verify function return types
    assert "get_user" in analysis["functions"]
    assert analysis["functions"]["get_user"]["return_type"] == "Optional[User]"
    assert "add_user" in analysis["functions"]
    assert analysis["functions"]["add_user"]["return_type"] == "bool"

def test_java_type_inference(java_analyzer, sample_java_code):
    """Test Java type inference."""
    tree = java_analyzer._parse_code(sample_java_code)
    analysis = java_analyzer.infer_types(tree)
    
    # Verify variable types
    assert "dbConnection" in analysis["variables"]
    assert analysis["variables"]["dbConnection"]["type"] == "String"
    
    # Verify method return types
    assert "getUser" in analysis["methods"]
    assert analysis["methods"]["getUser"]["return_type"] == "Optional<User>"
    assert "addUser" in analysis["methods"]
    assert analysis["methods"]["addUser"]["return_type"] == "boolean"

def test_typescript_type_inference(typescript_analyzer, sample_typescript_code):
    """Test TypeScript type inference."""
    tree = typescript_analyzer._parse_code(sample_typescript_code)
    analysis = typescript_analyzer.infer_types(tree)
    
    # Verify variable types
    assert "dbConnection" in analysis["variables"]
    assert analysis["variables"]["dbConnection"]["type"] == "string"
    
    # Verify function return types
    assert "getUser" in analysis["functions"]
    assert analysis["functions"]["getUser"]["return_type"] == "User | null"
    assert "addUser" in analysis["functions"]
    assert analysis["functions"]["addUser"]["return_type"] == "boolean"

def test_language_analyzer_factory():
    """Test language analyzer factory."""
    factory = LanguageAnalyzerFactory()
    
    # Test supported languages
    assert isinstance(factory.create_analyzer("python"), PythonAnalyzer)
    assert isinstance(factory.create_analyzer("java"), JavaAnalyzer)
    assert isinstance(factory.create_analyzer("typescript"), TypeScriptAnalyzer)
    
    # Test case insensitivity
    assert isinstance(factory.create_analyzer("PYTHON"), PythonAnalyzer)
    assert isinstance(factory.create_analyzer("Java"), JavaAnalyzer)
    assert isinstance(factory.create_analyzer("TypeScript"), TypeScriptAnalyzer)
    
    # Test unsupported language
    with pytest.raises(ValueError):
        factory.create_analyzer("unsupported") 