from typing import Dict, List, Any, Optional, Set
import ast
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path

logger = logging.getLogger(__name__)

class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"

@dataclass
class TypeInfo:
    name: str
    base_types: List[str]
    is_primitive: bool
    is_composite: bool
    is_generic: bool
    generic_params: List[str]
    methods: List[str]
    properties: List[str]
    docstring: Optional[str]
    source_location: str

class EnhancedTypeInference:
    """Enhanced type inference system with multi-language support."""
    
    def __init__(self):
        """Initialize the type inference system."""
        self.language_parsers: Dict[Language, Any] = {}
        self.type_registry: Dict[str, TypeInfo] = {}
        self._initialize_parsers()
        
    def _initialize_parsers(self):
        """Initialize language-specific parsers."""
        try:
            # Initialize tree-sitter parsers for each language
            for lang in Language:
                try:
                    parser = tree_sitter.Parser()
                    parser.set_language(tree_sitter.Language(f"build/{lang.value}.so", lang.value))
                    self.language_parsers[lang] = parser
                except Exception as e:
                    logger.warning(f"Failed to initialize parser for {lang.value}: {e}")
                    
        except Exception as e:
            logger.error(f"Error initializing parsers: {e}")
            raise
            
    def detect_language(self, file_path: str) -> Optional[Language]:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".h": Language.CPP,
            ".hpp": Language.CPP,
            ".go": Language.GO,
            ".rs": Language.RUST,
            ".rb": Language.RUBY,
            ".php": Language.PHP,
            ".swift": Language.SWIFT,
            ".kt": Language.KOTLIN
        }
        return language_map.get(ext)
        
    def analyze_types(self, file_path: str, content: str) -> Dict[str, TypeInfo]:
        """Analyze types in a file."""
        language = self.detect_language(file_path)
        if not language:
            raise ValueError(f"Unsupported language for file: {file_path}")
            
        try:
            # Parse the code
            tree = self.language_parsers[language].parse(bytes(content, "utf8"))
            
            # Extract type information
            type_info = self._extract_type_info(tree, language)
            
            # Update type registry
            self.type_registry.update(type_info)
            
            return type_info
            
        except Exception as e:
            logger.error(f"Error analyzing types in {file_path}: {e}")
            raise
            
    def _extract_type_info(self, tree: tree_sitter.Tree, language: Language) -> Dict[str, TypeInfo]:
        """Extract type information from parsed code."""
        type_info = {}
        
        if language == Language.PYTHON:
            type_info = self._extract_python_types(tree)
        elif language == Language.TYPESCRIPT:
            type_info = self._extract_typescript_types(tree)
        elif language == Language.JAVA:
            type_info = self._extract_java_types(tree)
        # Add more language-specific extractors as needed
        
        return type_info
        
    def _extract_python_types(self, tree: tree_sitter.Tree) -> Dict[str, TypeInfo]:
        """Extract type information from Python code."""
        type_info = {}
        
        def traverse(node: tree_sitter.Node):
            if node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                bases = []
                for base in node.child_by_field_name("superclasses").children:
                    if base.type == "identifier":
                        bases.append(base.text.decode("utf8"))
                        
                methods = []
                properties = []
                docstring = None
                
                for child in node.children:
                    if child.type == "function_definition":
                        methods.append(child.child_by_field_name("name").text.decode("utf8"))
                    elif child.type == "expression_statement":
                        # Check for property decorators
                        if child.child_by_field_name("expression").type == "decorator":
                            properties.append(child.child_by_field_name("expression").text.decode("utf8"))
                    elif child.type == "expression" and child.child_by_field_name("expression").type == "string":
                        docstring = child.child_by_field_name("expression").text.decode("utf8")
                        
                type_info[class_name] = TypeInfo(
                    name=class_name,
                    base_types=bases,
                    is_primitive=False,
                    is_composite=True,
                    is_generic=False,
                    generic_params=[],
                    methods=methods,
                    properties=properties,
                    docstring=docstring,
                    source_location=f"{node.start_point[0]}:{node.end_point[0]}"
                )
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return type_info
        
    def _extract_typescript_types(self, tree: tree_sitter.Tree) -> Dict[str, TypeInfo]:
        """Extract type information from TypeScript code."""
        # Implement TypeScript type extraction
        return {}
        
    def _extract_java_types(self, tree: tree_sitter.Tree) -> Dict[str, TypeInfo]:
        """Extract type information from Java code."""
        # Implement Java type extraction
        return {}
        
    def infer_type(self, expression: str, context: Dict[str, Any]) -> Optional[TypeInfo]:
        """Infer the type of an expression in a given context."""
        try:
            # Parse the expression
            tree = ast.parse(expression)
            
            # Analyze the expression
            type_info = self._analyze_expression(tree, context)
            
            return type_info
            
        except Exception as e:
            logger.error(f"Error inferring type for expression: {e}")
            return None
            
    def _analyze_expression(self, tree: ast.AST, context: Dict[str, Any]) -> Optional[TypeInfo]:
        """Analyze an expression to infer its type."""
        if isinstance(tree, ast.Name):
            # Check context for variable type
            if tree.id in context:
                return context[tree.id]
            # Check type registry
            if tree.id in self.type_registry:
                return self.type_registry[tree.id]
                
        elif isinstance(tree, ast.Call):
            # Analyze function call
            if isinstance(tree.func, ast.Name):
                if tree.func.id in self.type_registry:
                    return self.type_registry[tree.func.id]
                    
        elif isinstance(tree, ast.BinOp):
            # Analyze binary operation
            left_type = self._analyze_expression(tree.left, context)
            right_type = self._analyze_expression(tree.right, context)
            if left_type and right_type:
                return self._resolve_binary_op_type(left_type, right_type, tree.op)
                
        return None
        
    def _resolve_binary_op_type(self, left: TypeInfo, right: TypeInfo, op: ast.operator) -> Optional[TypeInfo]:
        """Resolve the type of a binary operation."""
        # Implement type resolution for binary operations
        return None 