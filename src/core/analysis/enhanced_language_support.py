from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import re
import json

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
    SCALA = "scala"
    DART = "dart"
    LUA = "lua"
    R = "r"
    MATLAB = "matlab"
    FORTRAN = "fortran"
    COBOL = "cobol"
    HASKELL = "haskell"
    OCAML = "ocaml"
    FSHARP = "fsharp"
    ELIXIR = "elixir"
    CLOSURE = "closure"
    ERLANG = "erlang"
    PROLOG = "prolog"
    SCHEME = "scheme"
    LISP = "lisp"
    SMALLTALK = "smalltalk"
    ADA = "ada"
    PASCAL = "pascal"
    BASIC = "basic"
    ASSEMBLY = "assembly"

@dataclass
class Scope:
    name: str
    type: str
    start_line: int
    end_line: int
    parent: Optional[str]
    variables: Dict[str, Dict[str, Any]]
    functions: Dict[str, Dict[str, Any]]
    classes: Dict[str, Dict[str, Any]]
    imports: List[str]
    exports: List[str]

class EnhancedLanguageSupport:
    """Enhanced language support and scope analysis system."""
    
    def __init__(self):
        """Initialize the enhanced language support system."""
        self.language_parsers = {}
        self.scope_analyzers = {}
        self._initialize_parsers()
        self._initialize_analyzers()
        
    def _initialize_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        try:
            for language in Language:
                try:
                    parser = tree_sitter.Parser()
                    parser.set_language(tree_sitter.Language(f"build/{language.value}.so", language.value))
                    self.language_parsers[language] = parser
                except Exception as e:
                    logger.warning(f"Failed to initialize parser for {language.value}: {e}")
        except Exception as e:
            logger.error(f"Error initializing parsers: {e}")
            raise
            
    def _initialize_analyzers(self):
        """Initialize language-specific scope analyzers."""
        self.scope_analyzers = {
            Language.PYTHON: self._analyze_python_scope,
            Language.JAVASCRIPT: self._analyze_javascript_scope,
            Language.TYPESCRIPT: self._analyze_typescript_scope,
            Language.JAVA: self._analyze_java_scope,
            Language.CPP: self._analyze_cpp_scope,
            Language.GO: self._analyze_go_scope,
            Language.RUST: self._analyze_rust_scope,
            # Add more language-specific analyzers as needed
        }
        
    def detect_language(self, file_path: str) -> Optional[Language]:
        """Detect programming language from file extension and content."""
        try:
            # First try extension-based detection
            ext = Path(file_path).suffix.lower()
            language_map = {
                ".py": Language.PYTHON,
                ".js": Language.JAVASCRIPT,
                ".ts": Language.TYPESCRIPT,
                ".jsx": Language.JAVASCRIPT,
                ".tsx": Language.TYPESCRIPT,
                ".java": Language.JAVA,
                ".cpp": Language.CPP,
                ".cc": Language.CPP,
                ".cxx": Language.CPP,
                ".h": Language.CPP,
                ".hpp": Language.CPP,
                ".go": Language.GO,
                ".rs": Language.RUST,
                ".rb": Language.RUBY,
                ".php": Language.PHP,
                ".swift": Language.SWIFT,
                ".kt": Language.KOTLIN,
                ".scala": Language.SCALA,
                ".dart": Language.DART,
                ".lua": Language.LUA,
                ".r": Language.R,
                ".m": Language.MATLAB,
                ".f": Language.FORTRAN,
                ".f90": Language.FORTRAN,
                ".cbl": Language.COBOL,
                ".hs": Language.HASKELL,
                ".ml": Language.OCAML,
                ".fs": Language.FSHARP,
                ".ex": Language.ELIXIR,
                ".clj": Language.CLOSURE,
                ".erl": Language.ERLANG,
                ".pl": Language.PROLOG,
                ".scm": Language.SCHEME,
                ".lisp": Language.LISP,
                ".st": Language.SMALLTALK,
                ".ada": Language.ADA,
                ".pas": Language.PASCAL,
                ".bas": Language.BASIC,
                ".asm": Language.ASSEMBLY
            }
            
            if ext in language_map:
                return language_map[ext]
                
            # If extension detection fails, try content-based detection
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for language-specific patterns
            patterns = {
                Language.PYTHON: [
                    r'^#!/usr/bin/env python',
                    r'^import\s+',
                    r'^from\s+',
                    r'^def\s+',
                    r'^class\s+'
                ],
                Language.JAVASCRIPT: [
                    r'^import\s+',
                    r'^export\s+',
                    r'^const\s+',
                    r'^let\s+',
                    r'^var\s+'
                ],
                Language.JAVA: [
                    r'^package\s+',
                    r'^import\s+',
                    r'^public\s+class\s+',
                    r'^private\s+'
                ],
                # Add more language patterns as needed
            }
            
            for language, language_patterns in patterns.items():
                if any(re.search(pattern, content, re.MULTILINE) for pattern in language_patterns):
                    return language
                    
            return None
            
        except Exception as e:
            logger.error(f"Error detecting language for {file_path}: {e}")
            return None
            
    def analyze_scope(self, file_path: str, content: str) -> Dict[str, Scope]:
        """Analyze scopes in the code."""
        try:
            # Detect language
            language = self.detect_language(file_path)
            if not language:
                raise ValueError(f"Could not detect language for {file_path}")
                
            # Get parser
            parser = self.language_parsers.get(language)
            if not parser:
                raise ValueError(f"No parser available for {language.value}")
                
            # Parse code
            tree = parser.parse(bytes(content, "utf8"))
            
            # Get language-specific analyzer
            analyzer = self.scope_analyzers.get(language)
            if not analyzer:
                raise ValueError(f"No scope analyzer available for {language.value}")
                
            # Analyze scopes
            scopes = analyzer(tree.root_node)
            
            return scopes
            
        except Exception as e:
            logger.error(f"Error analyzing scope for {file_path}: {e}")
            return {}
            
    def _analyze_python_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze Python scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "module":
                current_scope = "module"
                scopes[current_scope] = Scope(
                    name="module",
                    type="module",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[class_name] = Scope(
                    name=class_name,
                    type="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = class_name
                
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "import_statement":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "assignment":
                if current_scope:
                    var_name = self._extract_variable_name(node)
                    if var_name:
                        scopes[current_scope].variables[var_name] = {
                            "type": self._extract_variable_type(node),
                            "line": node.start_point[0] + 1
                        }
                        
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["class_definition", "function_definition"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_javascript_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze JavaScript scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "program":
                current_scope = "module"
                scopes[current_scope] = Scope(
                    name="module",
                    type="module",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[class_name] = Scope(
                    name=class_name,
                    type="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = class_name
                
            elif node.type == "function_declaration":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "import_statement":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "export_statement":
                if current_scope:
                    scopes[current_scope].exports.append(node.text.decode("utf8"))
                    
            elif node.type == "variable_declaration":
                if current_scope:
                    for declarator in node.children:
                        if declarator.type == "variable_declarator":
                            var_name = declarator.child_by_field_name("name").text.decode("utf8")
                            scopes[current_scope].variables[var_name] = {
                                "type": self._extract_variable_type(declarator),
                                "line": declarator.start_point[0] + 1
                            }
                            
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["class_declaration", "function_declaration"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_typescript_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze TypeScript scopes."""
        # Similar to JavaScript but with additional type information
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "program":
                current_scope = "module"
                scopes[current_scope] = Scope(
                    name="module",
                    type="module",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[class_name] = Scope(
                    name=class_name,
                    type="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = class_name
                
            elif node.type == "function_declaration":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "import_statement":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "export_statement":
                if current_scope:
                    scopes[current_scope].exports.append(node.text.decode("utf8"))
                    
            elif node.type == "variable_declaration":
                if current_scope:
                    for declarator in node.children:
                        if declarator.type == "variable_declarator":
                            var_name = declarator.child_by_field_name("name").text.decode("utf8")
                            type_node = declarator.child_by_field_name("type")
                            scopes[current_scope].variables[var_name] = {
                                "type": type_node.text.decode("utf8") if type_node else None,
                                "line": declarator.start_point[0] + 1
                            }
                            
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["class_declaration", "function_declaration"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_java_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze Java scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "program":
                current_scope = "module"
                scopes[current_scope] = Scope(
                    name="module",
                    type="module",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[class_name] = Scope(
                    name=class_name,
                    type="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = class_name
                
            elif node.type == "method_declaration":
                method_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[method_name] = Scope(
                    name=method_name,
                    type="method",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = method_name
                
            elif node.type == "import_declaration":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "field_declaration":
                if current_scope:
                    for declarator in node.children:
                        if declarator.type == "variable_declarator":
                            var_name = declarator.child_by_field_name("name").text.decode("utf8")
                            scopes[current_scope].variables[var_name] = {
                                "type": self._extract_variable_type(declarator),
                                "line": declarator.start_point[0] + 1
                            }
                            
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["class_declaration", "method_declaration"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_cpp_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze C++ scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "translation_unit":
                current_scope = "global"
                scopes[current_scope] = Scope(
                    name="global",
                    type="global",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "class_specifier":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[class_name] = Scope(
                    name=class_name,
                    type="class",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = class_name
                
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("declarator").child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "declaration":
                if current_scope:
                    for declarator in node.children:
                        if declarator.type == "init_declarator":
                            var_name = declarator.child_by_field_name("declarator").child_by_field_name("name").text.decode("utf8")
                            scopes[current_scope].variables[var_name] = {
                                "type": self._extract_variable_type(declarator),
                                "line": declarator.start_point[0] + 1
                            }
                            
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["class_specifier", "function_definition"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_go_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze Go scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "source_file":
                current_scope = "package"
                scopes[current_scope] = Scope(
                    name="package",
                    type="package",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "type_declaration":
                type_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[type_name] = Scope(
                    name=type_name,
                    type="type",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = type_name
                
            elif node.type == "function_declaration":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "import_declaration":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "var_declaration":
                if current_scope:
                    for declarator in node.children:
                        if declarator.type == "var_spec":
                            var_name = declarator.child_by_field_name("name").text.decode("utf8")
                            scopes[current_scope].variables[var_name] = {
                                "type": self._extract_variable_type(declarator),
                                "line": declarator.start_point[0] + 1
                            }
                            
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["type_declaration", "function_declaration"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _analyze_rust_scope(self, node: tree_sitter.Node) -> Dict[str, Scope]:
        """Analyze Rust scopes."""
        scopes = {}
        current_scope = None
        
        def traverse(node: tree_sitter.Node, parent_scope: Optional[str] = None):
            nonlocal current_scope
            
            if node.type == "source_file":
                current_scope = "module"
                scopes[current_scope] = Scope(
                    name="module",
                    type="module",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=None,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                
            elif node.type == "struct_item":
                struct_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[struct_name] = Scope(
                    name=struct_name,
                    type="struct",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = struct_name
                
            elif node.type == "impl_item":
                impl_name = node.child_by_field_name("type").text.decode("utf8")
                scopes[impl_name] = Scope(
                    name=impl_name,
                    type="impl",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = impl_name
                
            elif node.type == "function_item":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                scopes[func_name] = Scope(
                    name=func_name,
                    type="function",
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=current_scope,
                    variables={},
                    functions={},
                    classes={},
                    imports=[],
                    exports=[]
                )
                current_scope = func_name
                
            elif node.type == "use_declaration":
                if current_scope:
                    scopes[current_scope].imports.append(node.text.decode("utf8"))
                    
            elif node.type == "let_declaration":
                if current_scope:
                    var_name = node.child_by_field_name("pattern").text.decode("utf8")
                    scopes[current_scope].variables[var_name] = {
                        "type": self._extract_variable_type(node),
                        "line": node.start_point[0] + 1
                    }
                    
            for child in node.children:
                traverse(child, current_scope)
                
            if node.type in ["struct_item", "impl_item", "function_item"]:
                current_scope = parent_scope
                
        traverse(node)
        return scopes
        
    def _extract_variable_name(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract variable name from a node."""
        if node.type == "variable_declaration":
            name_node = node.child_by_field_name("name")
        elif node.type == "assignment":
            name_node = node.child_by_field_name("left")
        elif node.type == "variable_declarator":
            name_node = node.child_by_field_name("name")
        elif node.type == "init_declarator":
            name_node = node.child_by_field_name("declarator").child_by_field_name("name")
        elif node.type == "var_spec":
            name_node = node.child_by_field_name("name")
        elif node.type == "let_declaration":
            name_node = node.child_by_field_name("pattern")
        else:
            return None
            
        if name_node and name_node.type == "identifier":
            return name_node.text.decode("utf8")
        return None
        
    def _extract_variable_type(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract variable type from a node."""
        if node.type == "variable_declaration":
            type_node = node.child_by_field_name("type")
        elif node.type == "variable_declarator":
            type_node = node.child_by_field_name("type")
        elif node.type == "init_declarator":
            type_node = node.child_by_field_name("declarator").child_by_field_name("type")
        elif node.type == "var_spec":
            type_node = node.child_by_field_name("type")
        elif node.type == "let_declaration":
            type_node = node.child_by_field_name("type")
        else:
            return None
            
        if type_node:
            return type_node.text.decode("utf8")
        return None 