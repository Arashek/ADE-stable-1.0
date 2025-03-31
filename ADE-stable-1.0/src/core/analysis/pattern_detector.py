from typing import Dict, List, Any, Optional, Set
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import re
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

logger = logging.getLogger(__name__)

class PatternType(Enum):
    DESIGN_PATTERN = "design_pattern"
    ANTI_PATTERN = "anti_pattern"
    CODE_SMELL = "code_smell"
    ARCHITECTURAL_PATTERN = "architectural_pattern"
    PERFORMANCE_PATTERN = "performance_pattern"
    SECURITY_PATTERN = "security_pattern"
    TESTING_PATTERN = "testing_pattern"

@dataclass
class Pattern:
    type: PatternType
    name: str
    description: str
    severity: int  # 1-5
    confidence: float  # 0-1
    location: str
    context: Dict[str, Any]
    suggestions: List[str]

@dataclass
class PatternMatch:
    """Container for pattern match results."""
    pattern_type: str
    description: str
    confidence: float
    location: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class PatternDetector:
    """System for detecting error patterns and code issues."""
    
    def __init__(self):
        """Initialize pattern detector with predefined patterns."""
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined error patterns."""
        return {
            "null_pointer": {
                "regex": r"NoneType.*not.*subscriptable|NoneType.*has.*no.*attribute",
                "description": "Attempting to access properties or methods of None value",
                "severity": "high",
                "category": "runtime"
            },
            "index_error": {
                "regex": r"list.*index.*out.*of.*range|string.*index.*out.*of.*range",
                "description": "Accessing invalid index in sequence",
                "severity": "medium",
                "category": "runtime"
            },
            "type_error": {
                "regex": r"TypeError:.*",
                "description": "Invalid type operation or argument",
                "severity": "medium",
                "category": "runtime"
            },
            "value_error": {
                "regex": r"ValueError:.*",
                "description": "Invalid value or argument",
                "severity": "medium",
                "category": "runtime"
            },
            "syntax_error": {
                "regex": r"SyntaxError:.*",
                "description": "Invalid Python syntax",
                "severity": "high",
                "category": "syntax"
            },
            "import_error": {
                "regex": r"ImportError:.*|ModuleNotFoundError:.*",
                "description": "Failed to import module or package",
                "severity": "medium",
                "category": "import"
            },
            "recursion_error": {
                "regex": r"RecursionError:.*|maximum.*recursion.*depth.*exceeded",
                "description": "Excessive recursion depth",
                "severity": "high",
                "category": "runtime"
            },
            "memory_error": {
                "regex": r"MemoryError:.*",
                "description": "Out of memory error",
                "severity": "high",
                "category": "runtime"
            },
            "timeout_error": {
                "regex": r"TimeoutError:.*",
                "description": "Operation timed out",
                "severity": "medium",
                "category": "runtime"
            },
            "permission_error": {
                "regex": r"PermissionError:.*",
                "description": "Permission denied for operation",
                "severity": "high",
                "category": "system"
            },
            "database_error": {
                "regex": r"DatabaseError|SQL.*error|connection.*refused|duplicate.*key",
                "description": "Database operation error",
                "severity": "high",
                "category": "database"
            },
            "api_error": {
                "regex": r"API.*error|HTTP.*error|endpoint.*not.*found|rate.*limit",
                "description": "API or HTTP request error",
                "severity": "medium",
                "category": "network"
            },
            "validation_error": {
                "regex": r"ValidationError|invalid.*input|required.*field|format.*error",
                "description": "Data validation error",
                "severity": "medium",
                "category": "data"
            },
            "authentication_error": {
                "regex": r"AuthenticationError|unauthorized|invalid.*credentials|token.*expired",
                "description": "Authentication or authorization error",
                "severity": "high",
                "category": "security"
            },
            "serialization_error": {
                "regex": r"SerializationError|JSON.*error|pickle.*error|encode.*error",
                "description": "Data serialization or deserialization error",
                "severity": "medium",
                "category": "data"
            },
            "file_error": {
                "regex": r"FileNotFoundError|IOError|permission.*denied|disk.*full",
                "description": "File system operation error",
                "severity": "medium",
                "category": "system"
            },
            "cache_error": {
                "regex": r"CacheError|redis.*error|memcached.*error|cache.*miss",
                "description": "Cache operation error",
                "severity": "low",
                "category": "performance"
            },
            "queue_error": {
                "regex": r"QueueError|rabbitmq.*error|kafka.*error|message.*failed",
                "description": "Message queue operation error",
                "severity": "medium",
                "category": "messaging"
            },
            "logging_error": {
                "regex": r"LoggingError|log.*failed|write.*error|rotate.*error",
                "description": "Logging system error",
                "severity": "low",
                "category": "system"
            },
            "configuration_error": {
                "regex": r"ConfigError|settings.*error|env.*not.*set|invalid.*config",
                "description": "Configuration or environment error",
                "severity": "high",
                "category": "system"
            },
            "dependency_error": {
                "regex": r"DependencyError|version.*conflict|incompatible.*package|missing.*dependency",
                "description": "Dependency or package error",
                "severity": "medium",
                "category": "dependency"
            },
            "resource_error": {
                "regex": r"ResourceError|pool.*exhausted|connection.*limit|resource.*busy",
                "description": "Resource management error",
                "severity": "high",
                "category": "system"
            },
            "concurrency_error": {
                "regex": r"ConcurrencyError|race.*condition|deadlock|lock.*timeout",
                "description": "Concurrency or threading error",
                "severity": "high",
                "category": "runtime"
            },
            "compilation_error": {
                "regex": r"CompilationError|syntax.*error|compile.*failed|invalid.*syntax",
                "description": "Code compilation error",
                "severity": "high",
                "category": "syntax"
            },
            "test_error": {
                "regex": r"TestError|assertion.*failed|test.*failed|coverage.*error",
                "description": "Test execution error",
                "severity": "medium",
                "category": "testing"
            }
        }
    
    def detect_patterns(
        self,
        error_message: str,
        stack_trace: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[PatternMatch]:
        """
        Detect patterns in error message and stack trace.
        
        Args:
            error_message: The error message to analyze
            stack_trace: Optional stack trace
            context: Optional error context
            
        Returns:
            List[PatternMatch]: List of detected patterns
        """
        matches = []
        
        # Check error message against patterns
        for pattern_type, pattern_info in self.patterns.items():
            if re.search(pattern_info["regex"], error_message, re.IGNORECASE):
                match = PatternMatch(
                    pattern_type=pattern_type,
                    description=pattern_info["description"],
                    confidence=0.8,  # High confidence for direct matches
                    context=context
                )
                matches.append(match)
        
        # Analyze stack trace if provided
        if stack_trace:
            stack_patterns = self._analyze_stack_trace(stack_trace)
            matches.extend(stack_patterns)
        
        # Add context-based patterns
        if context:
            context_patterns = self._analyze_context(context)
            matches.extend(context_patterns)
        
        return matches
    
    def _analyze_stack_trace(self, stack_trace: List[str]) -> List[PatternMatch]:
        """Analyze stack trace for additional patterns."""
        matches = []
        
        # Look for common stack trace patterns
        for line in stack_trace:
            # Check for recursion
            if "recursion" in line.lower():
                matches.append(PatternMatch(
                    pattern_type="recursion",
                    description="Recursive function call detected",
                    confidence=0.6,
                    location=line
                ))
            
            # Check for circular imports
            if "circular import" in line.lower():
                matches.append(PatternMatch(
                    pattern_type="circular_import",
                    description="Circular import detected",
                    confidence=0.7,
                    location=line
                ))
            
            # Check for resource leaks
            if any(resource in line.lower() for resource in ["file", "socket", "connection"]):
                matches.append(PatternMatch(
                    pattern_type="resource_leak",
                    description="Potential resource leak detected",
                    confidence=0.5,
                    location=line
                ))
        
        return matches
    
    def _analyze_context(self, context: Dict[str, Any]) -> List[PatternMatch]:
        """Analyze error context for additional patterns."""
        matches = []
        
        # Check for common context patterns
        if "memory_usage" in context and context["memory_usage"] > 0.9:
            matches.append(PatternMatch(
                pattern_type="high_memory",
                description="High memory usage detected",
                confidence=0.7,
                context=context
            ))
        
        if "cpu_usage" in context and context["cpu_usage"] > 0.9:
            matches.append(PatternMatch(
                pattern_type="high_cpu",
                description="High CPU usage detected",
                confidence=0.7,
                context=context
            ))
        
        if "thread_count" in context and context["thread_count"] > 100:
            matches.append(PatternMatch(
                pattern_type="thread_explosion",
                description="Excessive thread count detected",
                confidence=0.6,
                context=context
            ))
        
        return matches
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about available patterns."""
        stats = {
            "total_patterns": len(self.patterns),
            "categories": {},
            "severity_levels": {}
        }
        
        # Count patterns by category and severity
        for pattern_info in self.patterns.values():
            category = pattern_info["category"]
            severity = pattern_info["severity"]
            
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            stats["severity_levels"][severity] = stats["severity_levels"].get(severity, 0) + 1
        
        return stats
    
    def add_custom_pattern(
        self,
        pattern_type: str,
        regex: str,
        description: str,
        severity: str,
        category: str
    ) -> None:
        """
        Add a custom pattern to the detector.
        
        Args:
            pattern_type: Unique identifier for the pattern
            regex: Regular expression to match
            description: Pattern description
            severity: Error severity level
            category: Pattern category
        """
        self.patterns[pattern_type] = {
            "regex": regex,
            "description": description,
            "severity": severity,
            "category": category
        }
    
    def get_pattern_info(self, pattern_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific pattern.
        
        Args:
            pattern_type: Pattern identifier
            
        Returns:
            Dict containing pattern information if found, None otherwise
        """
        return self.patterns.get(pattern_type)

    def analyze_code(self, file_path: str, content: str) -> List[Pattern]:
        """Analyze code for patterns."""
        try:
            # Parse the code
            tree = self._parse_code(file_path, content)
            
            # Detect patterns
            patterns = []
            
            # Design pattern detection
            patterns.extend(self._detect_design_patterns(tree))
            
            # Anti-pattern detection
            patterns.extend(self._detect_anti_patterns(tree))
            
            # Code smell detection
            patterns.extend(self._detect_code_smells(tree))
            
            # Architectural pattern detection
            patterns.extend(self._detect_architectural_patterns(tree))
            
            # Performance pattern detection
            patterns.extend(self._detect_performance_patterns(tree))
            
            # Security pattern detection
            patterns.extend(self._detect_security_patterns(tree))
            
            # Testing pattern detection
            patterns.extend(self._detect_testing_patterns(tree))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns in {file_path}: {e}")
            raise
            
    def _parse_code(self, file_path: str, content: str) -> tree_sitter.Tree:
        """Parse code using tree-sitter."""
        language = self._detect_language(file_path)
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter.Language(f"build/{language}.so", language))
        return parser.parse(bytes(content, "utf8"))
        
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".go": "go",
            ".rs": "rust"
        }
        return language_map.get(ext, "python")
        
    def _detect_design_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect design patterns in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # Singleton pattern detection
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                has_private_constructor = False
                has_static_instance = False
                
                for child in node.children:
                    if child.type == "function_definition":
                        func_name = child.child_by_field_name("name").text.decode("utf8")
                        if func_name == "__new__" or func_name == "__init__":
                            # Check if constructor is private
                            if any(decorator.text.decode("utf8") == "@private" 
                                  for decorator in child.children_by_field_name("decorator")):
                                has_private_constructor = True
                        elif func_name == "get_instance":
                            has_static_instance = True
                            
                if has_private_constructor and has_static_instance:
                    patterns.append(Pattern(
                        type=PatternType.DESIGN_PATTERN,
                        name="Singleton",
                        description=f"Singleton pattern detected in class {class_name}",
                        severity=3,
                        confidence=0.9,
                        location=f"{node.start_point[0]}:{node.end_point[0]}",
                        context={"class_name": class_name},
                        suggestions=["Consider if singleton is really needed", "Ensure thread safety"]
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_anti_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect anti-patterns in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # God class detection
            if node.type == "class_definition":
                method_count = 0
                property_count = 0
                
                for child in node.children:
                    if child.type == "function_definition":
                        method_count += 1
                    elif child.type == "expression_statement":
                        property_count += 1
                        
                if method_count > 20 or property_count > 10:
                    patterns.append(Pattern(
                        type=PatternType.ANTI_PATTERN,
                        name="God Class",
                        description=f"Class {node.child_by_field_name('name').text.decode('utf8')} has too many methods/properties",
                        severity=4,
                        confidence=0.85,
                        location=f"{node.start_point[0]}:{node.end_point[0]}",
                        context={"method_count": method_count, "property_count": property_count},
                        suggestions=["Split into smaller classes", "Apply Single Responsibility Principle"]
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_code_smells(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect code smells in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # Long method detection
            if node.type == "function_definition":
                method_name = node.child_by_field_name("name").text.decode("utf8")
                method_length = node.end_point[0] - node.start_point[0]
                
                if method_length > 50:  # Arbitrary threshold
                    patterns.append(Pattern(
                        type=PatternType.CODE_SMELL,
                        name="Long Method",
                        description=f"Method {method_name} is too long",
                        severity=3,
                        confidence=0.8,
                        location=f"{node.start_point[0]}:{node.end_point[0]}",
                        context={"method_length": method_length},
                        suggestions=["Extract methods", "Apply Single Responsibility Principle"]
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_architectural_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect architectural patterns in the code."""
        # Implement architectural pattern detection
        return []
        
    def _detect_performance_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect performance patterns in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # N+1 query detection
            if node.type == "for_statement":
                # Look for database queries inside loops
                for child in node.children:
                    if child.type == "call":
                        if any(query in child.text.decode("utf8").lower() 
                              for query in ["select", "insert", "update", "delete"]):
                            patterns.append(Pattern(
                                type=PatternType.PERFORMANCE_PATTERN,
                                name="N+1 Query",
                                description="Database query inside loop detected",
                                severity=4,
                                confidence=0.9,
                                location=f"{node.start_point[0]}:{node.end_point[0]}",
                                context={"query": child.text.decode("utf8")},
                                suggestions=["Use bulk operations", "Implement caching"]
                            ))
                            
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_security_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect security patterns in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # SQL injection detection
            if node.type == "call":
                call_text = node.text.decode("utf8")
                if "execute" in call_text.lower() and "sql" in call_text.lower():
                    if any(param in call_text for param in ["%s", "{}", "?"]):
                        patterns.append(Pattern(
                            type=PatternType.SECURITY_PATTERN,
                            name="SQL Injection Risk",
                            description="Potential SQL injection vulnerability detected",
                            severity=5,
                            confidence=0.9,
                            location=f"{node.start_point[0]}:{node.end_point[0]}",
                            context={"query": call_text},
                            suggestions=["Use parameterized queries", "Implement input validation"]
                        ))
                        
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_testing_patterns(self, tree: tree_sitter.Tree) -> List[Pattern]:
        """Detect testing patterns in the code."""
        patterns = []
        
        def traverse(node: tree_sitter.Node):
            # Test method naming convention
            if node.type == "function_definition":
                method_name = node.child_by_field_name("name").text.decode("utf8")
                if method_name.startswith("test_"):
                    if not any(assertion in node.text.decode("utf8").lower() 
                             for assertion in ["assert", "expect", "should"]):
                        patterns.append(Pattern(
                            type=PatternType.TESTING_PATTERN,
                            name="Missing Assertions",
                            description=f"Test method {method_name} has no assertions",
                            severity=2,
                            confidence=0.8,
                            location=f"{node.start_point[0]}:{node.end_point[0]}",
                            context={"method_name": method_name},
                            suggestions=["Add assertions", "Verify test coverage"]
                        ))
                        
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns 