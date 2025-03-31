from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import ast
import logging
from enum import Enum
import tree_sitter
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    TYPE = "type"
    CONTROL_FLOW = "control_flow"
    DATA_FLOW = "data_flow"
    DEPENDENCY = "dependency"
    PATTERN = "pattern"
    INTENT = "intent"

@dataclass
class CodeEntity:
    name: str
    type: str
    location: Tuple[int, int]
    scope: str
    dependencies: Set[str]
    metadata: Dict[str, Any]

@dataclass
class AnalysisContext:
    file_path: str
    language: str
    imports: List[str]
    exports: List[str]
    entities: Dict[str, CodeEntity]
    scope_stack: List[str]
    current_scope: str

class EnhancedCodeAnalyzer:
    """Enhanced code analysis system with comprehensive semantic analysis capabilities."""
    
    def __init__(self):
        self.parsers = {}
        self.vectorizer = TfidfVectorizer()
        self.logger = logging.getLogger(__name__)
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize specialized models for code analysis."""
        try:
            # Initialize tokenizer and model for semantic analysis
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
            self.model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base")
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                
        except Exception as e:
            logger.error(f"Failed to initialize code analysis models: {e}")
            
    def analyze_code(self, code: str, language: str, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive code analysis."""
        try:
            # Parse code into AST
            tree = self._parse_code(code, language)
            
            # Create analysis context
            context = AnalysisContext(
                file_path=file_path,
                language=language,
                imports=[],
                exports=[],
                entities={},
                scope_stack=["global"],
                current_scope="global"
            )
            
            # Perform comprehensive analysis
            analysis = {
                "syntax": self._analyze_syntax(tree, context),
                "semantics": self._analyze_semantics(tree, context),
                "types": self._infer_types(tree, context),
                "control_flow": self._analyze_control_flow(tree, context),
                "data_flow": self._analyze_data_flow(tree, context),
                "dependencies": self._analyze_dependencies(tree, context),
                "patterns": self._identify_patterns(tree, context),
                "intent": self._analyze_code_intent(code, context)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            return {"error": str(e)}
            
    def _parse_code(self, code: str, language: str) -> tree_sitter.Tree:
        """Parse code into AST using tree-sitter."""
        if language not in self.parsers:
            self.parsers[language] = tree_sitter.Language.build_library(
                f"build/{language}.so",
                [f"vendor/tree-sitter-{language}"]
            )
            
        parser = tree_sitter.Parser()
        parser.set_language(self.parsers[language])
        return parser.parse(bytes(code, "utf8"))
        
    def _analyze_syntax(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze syntax structure with enhanced detail."""
        analysis = {
            "imports": [],
            "classes": [],
            "functions": [],
            "variables": [],
            "decorators": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "import_statement":
                analysis["imports"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "class_definition":
                analysis["classes"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "bases": [base.text.decode("utf8") for base in node.children_by_field_name("base_class")],
                    "methods": [method.child_by_field_name("name").text.decode("utf8") 
                              for method in node.children_by_field_name("body") 
                              if method.type == "function_definition"],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "function_definition":
                analysis["functions"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "args": [arg.text.decode("utf8") for arg in node.children_by_field_name("parameters")],
                    "decorators": [decorator.text.decode("utf8") for decorator in node.children_by_field_name("decorator")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "variable_declaration":
                analysis["variables"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "type": node.child_by_field_name("type").text.decode("utf8") if node.child_by_field_name("type") else None,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_semantics(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze semantic meaning with enhanced scope tracking and type inference."""
        analysis = {
            "scope": {},
            "references": {},
            "definitions": {},
            "usage": {},
            "type_inference": {},
            "symbol_table": {},
            "semantic_metrics": {
                "cohesion": 0.0,
                "coupling": 0.0,
                "abstraction": 0.0,
                "encapsulation": 0.0,
                "inheritance": 0.0,
                "polymorphism": 0.0
            }
        }
        
        def traverse(node: tree_sitter.Node, scope: str = "global"):
            if node.type == "identifier":
                identifier = node.text.decode("utf8")
                if identifier not in analysis["references"]:
                    analysis["references"][identifier] = []
                analysis["references"][identifier].append({
                    "node": node,
                    "scope": scope,
                    "location": (node.start_point[0], node.end_point[0]),
                    "type": self._infer_identifier_type(node)
                })
                
            elif node.type == "function_definition":
                new_scope = f"{scope}.{node.child_by_field_name('name').text.decode('utf8')}"
                analysis["scope"][new_scope] = {
                    "parent": scope,
                    "variables": set(),
                    "functions": set(),
                    "classes": set(),
                    "parameters": self._analyze_function_parameters(node),
                    "return_type": self._infer_return_type(node),
                    "semantic_metrics": self._calculate_function_metrics(node)
                }
                
            elif node.type == "class_definition":
                new_scope = f"{scope}.{node.child_by_field_name('name').text.decode('utf8')}"
                class_metrics = self._calculate_class_metrics(node)
                analysis["scope"][new_scope] = {
                    "parent": scope,
                    "variables": set(),
                    "methods": set(),
                    "inheritance": [base.text.decode("utf8") for base in node.children_by_field_name("base_class")],
                    "semantic_metrics": class_metrics
                }
                
                # Update overall semantic metrics
                analysis["semantic_metrics"]["cohesion"] += class_metrics["cohesion"]
                analysis["semantic_metrics"]["coupling"] += class_metrics["coupling"]
                analysis["semantic_metrics"]["abstraction"] += class_metrics["abstraction"]
                analysis["semantic_metrics"]["encapsulation"] += class_metrics["encapsulation"]
                analysis["semantic_metrics"]["inheritance"] += class_metrics["inheritance"]
                analysis["semantic_metrics"]["polymorphism"] += class_metrics["polymorphism"]
                
            for child in node.children:
                traverse(child, scope)
                
        traverse(tree.root_node)
        
        # Normalize semantic metrics
        class_count = sum(1 for scope in analysis["scope"].values() if "semantic_metrics" in scope)
        if class_count > 0:
            for key in analysis["semantic_metrics"]:
                analysis["semantic_metrics"][key] /= class_count
                
        return analysis
        
    def _infer_types(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Infer types with enhanced type tracking and validation."""
        analysis = {
            "variables": {},
            "functions": {},
            "classes": {},
            "type_aliases": {},
            "generic_types": {}
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "variable_declaration":
                var_name = node.child_by_field_name("name").text.decode("utf8")
                var_type = node.child_by_field_name("type").text.decode("utf8") if node.child_by_field_name("type") else None
                analysis["variables"][var_name] = {
                    "type": var_type,
                    "location": (node.start_point[0], node.end_point[0]),
                    "inferred_type": self._infer_variable_type(node)
                }
                
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                return_type = node.child_by_field_name("return_type").text.decode("utf8") if node.child_by_field_name("return_type") else None
                analysis["functions"][func_name] = {
                    "return_type": return_type,
                    "parameters": self._analyze_function_parameters(node),
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            elif node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                analysis["classes"][class_name] = {
                    "bases": [base.text.decode("utf8") for base in node.children_by_field_name("base_class")],
                    "methods": self._analyze_class_methods(node),
                    "attributes": self._analyze_class_attributes(node),
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_control_flow(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze control flow with path analysis and complexity metrics."""
        analysis = {
            "branches": [],
            "loops": [],
            "exceptions": [],
            "returns": [],
            "complexity": {
                "cyclomatic": 0,
                "cognitive": 0,
                "maintainability": 0
            }
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type in ["if_statement", "elif_clause", "else_clause"]:
                analysis["branches"].append({
                    "type": node.type,
                    "condition": node.child_by_field_name("condition").text.decode("utf8") if node.child_by_field_name("condition") else None,
                    "location": (node.start_point[0], node.end_point[0])
                })
                analysis["complexity"]["cyclomatic"] += 1
                
            elif node.type in ["for_statement", "while_statement"]:
                analysis["loops"].append({
                    "type": node.type,
                    "condition": node.child_by_field_name("condition").text.decode("utf8") if node.child_by_field_name("condition") else None,
                    "location": (node.start_point[0], node.end_point[0])
                })
                analysis["complexity"]["cyclomatic"] += 2
                
            elif node.type == "try_statement":
                analysis["exceptions"].append({
                    "handlers": [handler.text.decode("utf8") for handler in node.children_by_field_name("handler")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            elif node.type == "return_statement":
                analysis["returns"].append({
                    "value": node.child_by_field_name("value").text.decode("utf8") if node.child_by_field_name("value") else None,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_data_flow(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze data flow with variable tracking and dependency analysis."""
        analysis = {
            "definitions": {},
            "uses": {},
            "dependencies": {},
            "data_flow_graph": defaultdict(list)
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "assignment":
                var_name = node.child_by_field_name("left").text.decode("utf8")
                if var_name not in analysis["definitions"]:
                    analysis["definitions"][var_name] = []
                analysis["definitions"][var_name].append({
                    "node": node,
                    "location": (node.start_point[0], node.end_point[0]),
                    "value": node.child_by_field_name("right").text.decode("utf8") if node.child_by_field_name("right") else None
                })
                
            elif node.type == "identifier":
                var_name = node.text.decode("utf8")
                if var_name not in analysis["uses"]:
                    analysis["uses"][var_name] = []
                analysis["uses"][var_name].append({
                    "node": node,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_dependencies(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze code dependencies and relationships."""
        analysis = {
            "imports": [],
            "exports": [],
            "dependencies": defaultdict(list),
            "relationships": defaultdict(list)
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "import_statement":
                analysis["imports"].append({
                    "module": node.child_by_field_name("module").text.decode("utf8") if node.child_by_field_name("module") else None,
                    "names": [name.text.decode("utf8") for name in node.children_by_field_name("name")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            elif node.type in ["class_definition", "function_definition"]:
                name = node.child_by_field_name("name").text.decode("utf8")
                analysis["exports"].append({
                    "name": name,
                    "type": node.type,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _identify_patterns(self, tree: tree_sitter.Tree, context: AnalysisContext) -> Dict[str, Any]:
        """Identify common code patterns and anti-patterns."""
        analysis = {
            "design_patterns": [],
            "anti_patterns": [],
            "code_smells": [],
            "best_practices": [],
            "pattern_metrics": {
                "complexity": 0.0,
                "maintainability": 0.0,
                "reusability": 0.0,
                "testability": 0.0
            }
        }
        
        def traverse(node: tree_sitter.Node):
            # Check for design patterns
            patterns = [
                (self._is_singleton_pattern, "singleton"),
                (self._is_factory_pattern, "factory"),
                (self._is_observer_pattern, "observer"),
                (self._is_strategy_pattern, "strategy"),
                (self._is_decorator_pattern, "decorator"),
                (self._is_adapter_pattern, "adapter"),
                (self._is_facade_pattern, "facade"),
                (self._is_command_pattern, "command"),
                (self._is_state_pattern, "state"),
                (self._is_iterator_pattern, "iterator")
            ]
            
            for pattern_check, pattern_name in patterns:
                if pattern_check(node):
                    analysis["design_patterns"].append({
                        "type": pattern_name,
                        "location": (node.start_point[0], node.end_point[0]),
                        "confidence": self._calculate_pattern_confidence(node, pattern_name)
                    })
                    
            # Check for anti-patterns
            anti_patterns = [
                (self._is_god_class, "god_class"),
                (self._is_long_method, "long_method"),
                (self._is_duplicate_code, "duplicate_code"),
                (self._is_feature_envy, "feature_envy"),
                (self._is_data_clumps, "data_clumps"),
                (self._is_primitive_obsession, "primitive_obsession"),
                (self._is_switch_statement, "switch_statement"),
                (self._is_shotgun_surgery, "shotgun_surgery"),
                (self._is_parallel_inheritance, "parallel_inheritance"),
                (self._is_lazy_class, "lazy_class")
            ]
            
            for anti_pattern_check, anti_pattern_name in anti_patterns:
                if anti_pattern_check(node):
                    analysis["anti_patterns"].append({
                        "type": anti_pattern_name,
                        "location": (node.start_point[0], node.end_point[0]),
                        "severity": self._calculate_anti_pattern_severity(node, anti_pattern_name)
                    })
                    
            # Check for code smells
            code_smells = [
                (self._is_magic_number, "magic_number"),
                (self._is_dead_code, "dead_code"),
                (self._is_complex_condition, "complex_condition"),
                (self._is_long_parameter_list, "long_parameter_list"),
                (self._is_switch_statement, "switch_statement"),
                (self._is_duplicate_code, "duplicate_code"),
                (self._is_large_class, "large_class"),
                (self._is_data_class, "data_class"),
                (self._is_refused_bequest, "refused_bequest"),
                (self._is_comments, "comments")
            ]
            
            for smell_check, smell_name in code_smells:
                if smell_check(node):
                    analysis["code_smells"].append({
                        "type": smell_name,
                        "location": (node.start_point[0], node.end_point[0]),
                        "impact": self._calculate_smell_impact(node, smell_name)
                    })
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        
        # Calculate pattern metrics
        analysis["pattern_metrics"] = self._calculate_pattern_metrics(analysis)
        
        return analysis
        
    def _analyze_code_intent(self, code: str, context: AnalysisContext) -> Dict[str, Any]:
        """Analyze code intent using NLP techniques."""
        try:
            # Tokenize code
            tokens = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**tokens)
                predictions = torch.softmax(outputs.logits, dim=1)
                
            # Extract intent features
            intent_features = {
                "purpose": self._extract_code_purpose(code),
                "complexity": self._calculate_code_complexity(code),
                "maintainability": self._assess_maintainability(code),
                "readability": self._assess_readability(code)
            }
            
            return intent_features
            
        except Exception as e:
            logger.error(f"Failed to analyze code intent: {e}")
            return {"error": str(e)}
            
    def _is_singleton_pattern(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the singleton pattern."""
        if node.type != "class_definition":
            return False
            
        class_name = node.child_by_field_name("name").text.decode("utf8")
        has_private_constructor = False
        has_static_instance = False
        has_get_instance = False
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_name = child.child_by_field_name("name").text.decode("utf8")
                
                # Check for private constructor
                if method_name == "__init__" and child.child_by_field_name("parameters"):
                    params = child.child_by_field_name("parameters")
                    if len(params.children) == 1:  # Only self parameter
                        has_private_constructor = True
                        
                # Check for static instance
                elif method_name.startswith("_"):  # Private method
                    if "instance" in method_name.lower():
                        has_static_instance = True
                        
                # Check for get_instance method
                elif method_name.lower() in ["get_instance", "getinstance", "instance"]:
                    has_get_instance = True
                    
        return has_private_constructor and has_static_instance and has_get_instance

    def _is_god_class(self, node: tree_sitter.Node) -> bool:
        """Check if a class is a god class (too many responsibilities)."""
        if node.type != "class_definition":
            return False
            
        # Count methods and attributes
        method_count = 0
        attribute_count = 0
        total_lines = 0
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_count += 1
                # Count lines in method
                total_lines += child.end_point[0] - child.start_point[0]
            elif child.type == "variable_declaration":
                attribute_count += 1
                
        # Check against thresholds
        return (method_count > 10 or  # Too many methods
                attribute_count > 15 or  # Too many attributes
                total_lines > 300)  # Too large

    def _is_long_method(self, node: tree_sitter.Node) -> bool:
        """Check if a method is too long."""
        if node.type != "function_definition":
            return False
            
        # Count lines in method body
        method_lines = node.end_point[0] - node.start_point[0]
        
        # Check against threshold (20 lines is a common threshold)
        return method_lines > 20

    def _infer_variable_type(self, node: tree_sitter.Node) -> str:
        """Infer variable type based on usage and context."""
        if not node:
            return "Any"
            
        # Check for type annotation
        type_node = node.child_by_field_name("type")
        if type_node:
            return type_node.text.decode("utf8")
            
        # Check for assignment
        assignment = node.child_by_field_name("right")
        if assignment:
            if assignment.type == "string":
                return "str"
            elif assignment.type == "integer":
                return "int"
            elif assignment.type == "float":
                return "float"
            elif assignment.type == "true" or assignment.type == "false":
                return "bool"
            elif assignment.type == "list":
                return "List"
            elif assignment.type == "dictionary":
                return "Dict"
            elif assignment.type == "set":
                return "Set"
            elif assignment.type == "tuple":
                return "Tuple"
                
        # Check for usage context
        parent = node.parent
        if parent:
            if parent.type == "call":
                # Try to infer from function call
                func_name = parent.child_by_field_name("function").text.decode("utf8")
                if func_name in ["len", "str", "int", "float", "bool"]:
                    return func_name
                    
        return "Any"

    def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity metrics."""
        complexity = 0.0
        
        # Count control structures
        control_structures = {
            "if": 2,  # Weight for if statements
            "elif": 2,
            "else": 1,
            "for": 3,  # Weight for loops
            "while": 3,
            "try": 2,  # Weight for exception handling
            "except": 2,
            "finally": 1,
            "and": 1,  # Weight for logical operators
            "or": 1,
            "not": 1
        }
        
        # Count occurrences of control structures
        for structure, weight in control_structures.items():
            count = code.count(structure)
            complexity += count * weight
            
        # Normalize complexity score to [0, 1]
        max_complexity = 50  # Threshold for maximum complexity
        return min(complexity / max_complexity, 1.0)

    def _assess_maintainability(self, code: str) -> float:
        """Assess code maintainability."""
        maintainability = 1.0
        
        # Check code length
        lines = code.split("\n")
        if len(lines) > 500:  # Too long file
            maintainability *= 0.8
            
        # Check function length
        for line in lines:
            if line.strip().startswith("def "):
                func_lines = 0
                for func_line in lines[lines.index(line):]:
                    if func_line.strip().startswith("def "):
                        break
                    func_lines += 1
                if func_lines > 20:  # Long function
                    maintainability *= 0.9
                    
        # Check comment ratio
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        if len(lines) > 0:
            comment_ratio = comment_lines / len(lines)
            if comment_ratio < 0.1:  # Low documentation
                maintainability *= 0.9
                
        return maintainability

    def _assess_readability(self, code: str) -> float:
        """Assess code readability."""
        readability = 1.0
        
        # Check line length
        for line in code.split("\n"):
            if len(line) > 80:  # Long lines
                readability *= 0.95
                
        # Check naming conventions
        import re
        snake_case = re.compile(r"^[a-z_][a-z0-9_]*$")
        PascalCase = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
        
        for line in code.split("\n"):
            # Check variable names
            if "=" in line and not line.strip().startswith("#"):
                var_name = line.split("=")[0].strip()
                if not snake_case.match(var_name):
                    readability *= 0.95
                    
            # Check class names
            if line.strip().startswith("class "):
                class_name = line.split("class ")[1].split("(")[0].strip()
                if not PascalCase.match(class_name):
                    readability *= 0.95
                    
        return readability
        
    def _extract_code_purpose(self, code: str) -> str:
        """Extract code purpose using NLP techniques."""
        # Implementation for code purpose extraction
        return "Unknown"  # Placeholder
        
    def _analyze_function_parameters(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        """Analyze function parameters with type information."""
        parameters = []
        for param in node.children_by_field_name("parameters"):
            parameters.append({
                "name": param.child_by_field_name("name").text.decode("utf8"),
                "type": param.child_by_field_name("type").text.decode("utf8") if param.child_by_field_name("type") else None,
                "default": param.child_by_field_name("default").text.decode("utf8") if param.child_by_field_name("default") else None
            })
        return parameters
        
    def _analyze_class_methods(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        """Analyze class methods with visibility and type information."""
        methods = []
        for method in node.children_by_field_name("body"):
            if method.type == "function_definition":
                methods.append({
                    "name": method.child_by_field_name("name").text.decode("utf8"),
                    "visibility": self._determine_method_visibility(method),
                    "return_type": method.child_by_field_name("return_type").text.decode("utf8") if method.child_by_field_name("return_type") else None
                })
        return methods
        
    def _analyze_class_attributes(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        """Analyze class attributes with visibility and type information."""
        attributes = []
        for attr in node.children_by_field_name("body"):
            if attr.type == "variable_declaration":
                attributes.append({
                    "name": attr.child_by_field_name("name").text.decode("utf8"),
                    "type": attr.child_by_field_name("type").text.decode("utf8") if attr.child_by_field_name("type") else None,
                    "visibility": self._determine_attribute_visibility(attr)
                })
        return attributes
        
    def _determine_method_visibility(self, node: tree_sitter.Node) -> str:
        """Determine method visibility based on naming and decorators."""
        name = node.child_by_field_name("name").text.decode("utf8")
        if name.startswith("_"):
            return "private"
        elif name.startswith("__"):
            return "mangled"
        return "public"
        
    def _determine_attribute_visibility(self, node: tree_sitter.Node) -> str:
        """Determine attribute visibility based on naming and decorators."""
        name = node.child_by_field_name("name").text.decode("utf8")
        if name.startswith("_"):
            return "private"
        elif name.startswith("__"):
            return "mangled"
        return "public"

    def _is_factory_pattern(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the factory pattern."""
        if node.type != "class_definition":
            return False
            
        has_factory_method = False
        has_abstract_product = False
        has_concrete_products = False
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_name = child.child_by_field_name("name").text.decode("utf8")
                
                # Check for factory method
                if method_name.lower() in ["create", "make", "build", "get_instance"]:
                    has_factory_method = True
                    
                # Check for abstract product
                if method_name.startswith("_"):  # Abstract method
                    has_abstract_product = True
                    
                # Check for concrete products
                if method_name.lower().endswith("_product"):
                    has_concrete_products = True
                    
        return has_factory_method and (has_abstract_product or has_concrete_products)

    def _is_observer_pattern(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the observer pattern."""
        if node.type != "class_definition":
            return False
            
        has_subject = False
        has_observers = False
        has_notify = False
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_name = child.child_by_field_name("name").text.decode("utf8")
                
                # Check for subject methods
                if method_name.lower() in ["attach", "detach", "notify"]:
                    has_subject = True
                    
                # Check for observer methods
                if method_name.lower() in ["update", "notify"]:
                    has_observers = True
                    
                # Check for notify method
                if method_name.lower() == "notify":
                    has_notify = True
                    
        return has_subject and has_observers and has_notify

    def _is_strategy_pattern(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the strategy pattern."""
        if node.type != "class_definition":
            return False
            
        has_strategy_interface = False
        has_context = False
        has_strategy_method = False
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_name = child.child_by_field_name("name").text.decode("utf8")
                
                # Check for strategy interface
                if method_name.startswith("_"):  # Abstract method
                    has_strategy_interface = True
                    
                # Check for context
                if method_name.lower() in ["execute", "perform", "run"]:
                    has_context = True
                    
                # Check for strategy method
                if method_name.lower().endswith("_strategy"):
                    has_strategy_method = True
                    
        return has_strategy_interface and has_context and has_strategy_method

    def _is_decorator_pattern(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the decorator pattern."""
        if node.type != "class_definition":
            return False
            
        has_component = False
        has_decorator = False
        has_wrapped_component = False
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                method_name = child.child_by_field_name("name").text.decode("utf8")
                
                # Check for component
                if method_name.startswith("_"):  # Abstract method
                    has_component = True
                    
                # Check for decorator
                if method_name.lower() in ["decorate", "wrap"]:
                    has_decorator = True
                    
                # Check for wrapped component
                if "component" in method_name.lower():
                    has_wrapped_component = True
                    
        return has_component and has_decorator and has_wrapped_component

    def _calculate_pattern_confidence(self, node: tree_sitter.Node, pattern_name: str) -> float:
        """Calculate confidence score for pattern detection."""
        confidence = 0.0
        
        # Base confidence on pattern-specific characteristics
        if pattern_name == "singleton":
            confidence = 0.8 if self._is_singleton_pattern(node) else 0.0
        elif pattern_name == "factory":
            confidence = 0.7 if self._is_factory_pattern(node) else 0.0
        elif pattern_name == "observer":
            confidence = 0.75 if self._is_observer_pattern(node) else 0.0
        elif pattern_name == "strategy":
            confidence = 0.7 if self._is_strategy_pattern(node) else 0.0
        elif pattern_name == "decorator":
            confidence = 0.65 if self._is_decorator_pattern(node) else 0.0
        elif pattern_name == "adapter":
            confidence = 0.7 if self._is_adapter_pattern(node) else 0.0
            
        # Adjust confidence based on code quality
        if confidence > 0:
            # Check method naming conventions
            method_names = [child.child_by_field_name("name").text.decode("utf8")
                          for child in node.children_by_field_name("body")
                          if child.type == "function_definition"]
            naming_score = sum(1 for name in method_names if self._follows_naming_convention(name)) / len(method_names)
            confidence *= (0.7 + 0.3 * naming_score)
            
            # Check code organization
            organization_score = self._assess_code_organization(node)
            confidence *= (0.6 + 0.4 * organization_score)
            
        return min(confidence, 1.0)

    def _calculate_anti_pattern_severity(self, node: tree_sitter.Node, anti_pattern_name: str) -> float:
        """Calculate severity score for anti-pattern detection."""
        severity = 0.0
        
        # Base severity on anti-pattern type
        if anti_pattern_name == "god_class":
            severity = 0.9
        elif anti_pattern_name == "long_method":
            severity = 0.7
        elif anti_pattern_name == "duplicate_code":
            severity = 0.8
        elif anti_pattern_name == "feature_envy":
            severity = 0.6
        elif anti_pattern_name == "data_clumps":
            severity = 0.5
        elif anti_pattern_name == "primitive_obsession":
            severity = 0.4
        elif anti_pattern_name == "switch_statement":
            severity = 0.3
        elif anti_pattern_name == "shotgun_surgery":
            severity = 0.8
        elif anti_pattern_name == "parallel_inheritance":
            severity = 0.7
        elif anti_pattern_name == "lazy_class":
            severity = 0.2
            
        # Adjust severity based on impact
        if severity > 0:
            # Check method complexity
            complexity_score = self._calculate_method_complexity(node)
            severity *= (0.7 + 0.3 * complexity_score)
            
            # Check code dependencies
            dependency_score = self._assess_dependencies(node)
            severity *= (0.6 + 0.4 * dependency_score)
            
        return min(severity, 1.0)

    def _calculate_smell_impact(self, node: tree_sitter.Node, smell_name: str) -> float:
        """Calculate impact score for code smell detection."""
        impact = 0.0
        
        # Base impact on smell type
        if smell_name == "magic_number":
            impact = 0.3
        elif smell_name == "dead_code":
            impact = 0.4
        elif smell_name == "complex_condition":
            impact = 0.5
        elif smell_name == "long_parameter_list":
            impact = 0.4
        elif smell_name == "switch_statement":
            impact = 0.3
        elif smell_name == "duplicate_code":
            impact = 0.6
        elif smell_name == "large_class":
            impact = 0.7
        elif smell_name == "data_class":
            impact = 0.2
        elif smell_name == "refused_bequest":
            impact = 0.5
        elif smell_name == "comments":
            impact = 0.3
            
        # Adjust impact based on context
        if impact > 0:
            # Check code maintainability
            maintainability_score = self._assess_maintainability(node)
            impact *= (0.7 + 0.3 * maintainability_score)
            
            # Check code readability
            readability_score = self._assess_readability(node)
            impact *= (0.6 + 0.4 * readability_score)
            
        return min(impact, 1.0)

    def _calculate_pattern_metrics(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate metrics for pattern analysis."""
        metrics = {
            "complexity": 0.0,
            "maintainability": 0.0,
            "reusability": 0.0,
            "testability": 0.0
        }
        
        # Calculate complexity based on pattern types
        pattern_complexity = {
            "singleton": 0.2,
            "factory": 0.4,
            "observer": 0.5,
            "strategy": 0.3,
            "decorator": 0.4,
            "adapter": 0.3
        }
        
        for pattern in analysis["design_patterns"]:
            metrics["complexity"] += pattern_complexity.get(pattern["type"], 0.3)
            
        # Calculate maintainability based on anti-patterns
        anti_pattern_impact = {
            "god_class": 0.8,
            "long_method": 0.6,
            "duplicate_code": 0.5,
            "feature_envy": 0.4,
            "data_clumps": 0.3
        }
        
        for anti_pattern in analysis["anti_patterns"]:
            metrics["maintainability"] += anti_pattern_impact.get(anti_pattern["type"], 0.3)
            
        # Calculate reusability based on pattern types
        pattern_reusability = {
            "singleton": 0.3,
            "factory": 0.7,
            "observer": 0.6,
            "strategy": 0.8,
            "decorator": 0.7,
            "adapter": 0.6
        }
        
        for pattern in analysis["design_patterns"]:
            metrics["reusability"] += pattern_reusability.get(pattern["type"], 0.5)
            
        # Calculate testability based on code smells
        smell_testability = {
            "magic_number": 0.2,
            "dead_code": 0.3,
            "complex_condition": 0.4,
            "long_parameter_list": 0.3,
            "switch_statement": 0.2
        }
        
        for smell in analysis["code_smells"]:
            metrics["testability"] += smell_testability.get(smell["type"], 0.2)
            
        # Normalize metrics to [0, 1]
        for key in metrics:
            metrics[key] = min(metrics[key], 1.0)
            
        return metrics

    def _calculate_function_metrics(self, node: tree_sitter.Node) -> Dict[str, float]:
        """Calculate semantic metrics for a function."""
        metrics = {
            "complexity": 0.0,
            "maintainability": 0.0,
            "readability": 0.0,
            "testability": 0.0,
            "reusability": 0.0
        }
        
        # Calculate complexity
        metrics["complexity"] = self._calculate_method_complexity(node)
        
        # Calculate maintainability
        metrics["maintainability"] = self._assess_maintainability(node)
        
        # Calculate readability
        metrics["readability"] = self._assess_readability(node)
        
        # Calculate testability
        metrics["testability"] = self._assess_testability(node)
        
        # Calculate reusability
        metrics["reusability"] = self._assess_reusability(node)
        
        return metrics

    def _calculate_class_metrics(self, node: tree_sitter.Node) -> Dict[str, float]:
        """Calculate semantic metrics for a class."""
        metrics = {
            "cohesion": 0.0,
            "coupling": 0.0,
            "abstraction": 0.0,
            "encapsulation": 0.0,
            "inheritance": 0.0,
            "polymorphism": 0.0
        }
        
        # Calculate cohesion
        metrics["cohesion"] = self._calculate_class_cohesion(node)
        
        # Calculate coupling
        metrics["coupling"] = self._calculate_class_coupling(node)
        
        # Calculate abstraction
        metrics["abstraction"] = self._calculate_class_abstraction(node)
        
        # Calculate encapsulation
        metrics["encapsulation"] = self._calculate_class_encapsulation(node)
        
        # Calculate inheritance
        metrics["inheritance"] = self._calculate_class_inheritance(node)
        
        # Calculate polymorphism
        metrics["polymorphism"] = self._calculate_class_polymorphism(node)
        
        return metrics

    def _calculate_class_cohesion(self, node: tree_sitter.Node) -> float:
        """Calculate class cohesion using LCOM (Lack of Cohesion of Methods)."""
        if node.type != "class_definition":
            return 0.0
            
        methods = []
        attributes = []
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                methods.append(child)
            elif child.type == "variable_declaration":
                attributes.append(child)
                
        if not methods or not attributes:
            return 1.0
            
        # Calculate method-attribute pairs
        total_pairs = len(methods) * len(attributes)
        if total_pairs == 0:
            return 1.0
            
        shared_pairs = 0
        for method in methods:
            method_attrs = self._get_method_attributes(method)
            for attr in attributes:
                if attr.child_by_field_name("name").text.decode("utf8") in method_attrs:
                    shared_pairs += 1
                    
        return 1.0 - (shared_pairs / total_pairs)

    def _calculate_class_coupling(self, node: tree_sitter.Node) -> float:
        """Calculate class coupling using CBO (Coupling Between Objects)."""
        if node.type != "class_definition":
            return 0.0
            
        coupled_classes = set()
        
        # Check method parameters and return types
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                # Check parameters
                for param in child.children_by_field_name("parameters"):
                    param_type = param.child_by_field_name("type")
                    if param_type:
                        coupled_classes.add(param_type.text.decode("utf8"))
                        
                # Check return type
                return_type = child.child_by_field_name("return_type")
                if return_type:
                    coupled_classes.add(return_type.text.decode("utf8"))
                    
        # Normalize coupling score
        return min(len(coupled_classes) / 10.0, 1.0)  # Cap at 10 coupled classes

    def _calculate_class_abstraction(self, node: tree_sitter.Node) -> float:
        """Calculate class abstraction level."""
        if node.type != "class_definition":
            return 0.0
            
        abstract_methods = 0
        total_methods = 0
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                total_methods += 1
                if self._is_abstract_method(child):
                    abstract_methods += 1
                    
        if total_methods == 0:
            return 0.0
            
        return abstract_methods / total_methods

    def _calculate_class_encapsulation(self, node: tree_sitter.Node) -> float:
        """Calculate class encapsulation level."""
        if node.type != "class_definition":
            return 0.0
            
        private_members = 0
        total_members = 0
        
        for child in node.children_by_field_name("body"):
            if child.type in ["function_definition", "variable_declaration"]:
                total_members += 1
                if self._is_private_member(child):
                    private_members += 1
                    
        if total_members == 0:
            return 0.0
            
        return private_members / total_members

    def _calculate_class_inheritance(self, node: tree_sitter.Node) -> float:
        """Calculate class inheritance level."""
        if node.type != "class_definition":
            return 0.0
            
        base_classes = node.children_by_field_name("base_class")
        return min(len(base_classes) / 3.0, 1.0)  # Cap at 3 base classes

    def _calculate_class_polymorphism(self, node: tree_sitter.Node) -> Dict[str, float]:
        """Calculate class polymorphism level."""
        if node.type != "class_definition":
            return 0.0
            
        overridden_methods = 0
        total_methods = 0
        
        for child in node.children_by_field_name("body"):
            if child.type == "function_definition":
                total_methods += 1
                if self._is_overridden_method(child):
                    overridden_methods += 1
                    
        if total_methods == 0:
            return 0.0
            
        return overridden_methods / total_methods

    def _assess_testability(self, node: tree_sitter.Node) -> float:
        """Assess code testability."""
        testability = 1.0
        
        # Check method complexity
        complexity = self._calculate_method_complexity(node)
        testability *= (1.0 - complexity)
        
        # Check dependencies
        dependencies = self._count_dependencies(node)
        testability *= (1.0 - min(dependencies / 10.0, 1.0))
        
        # Check side effects
        side_effects = self._has_side_effects(node)
        if side_effects:
            testability *= 0.8
            
        return testability

    def _assess_reusability(self, node: tree_sitter.Node) -> float:
        """Assess code reusability."""
        reusability = 1.0
        
        # Check coupling
        coupling = self._calculate_class_coupling(node)
        reusability *= (1.0 - coupling)
        
        # Check dependencies
        dependencies = self._count_dependencies(node)
        reusability *= (1.0 - min(dependencies / 10.0, 1.0))
        
        # Check abstraction
        abstraction = self._calculate_class_abstraction(node)
        reusability *= (0.5 + 0.5 * abstraction)
        
        return reusability

    def _get_method_attributes(self, node: tree_sitter.Node) -> Set[str]:
        """Get set of attributes used in a method."""
        attributes = set()
        
        def traverse(n: tree_sitter.Node):
            if n.type == "identifier":
                attributes.add(n.text.decode("utf8"))
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return attributes

    def _is_abstract_method(self, node: tree_sitter.Node) -> bool:
        """Check if a method is abstract."""
        if node.type != "function_definition":
            return False
            
        # Check for abstract decorator
        decorators = node.children_by_field_name("decorator")
        for decorator in decorators:
            if decorator.text.decode("utf8") == "@abstractmethod":
                return True
                
        # Check for abstract base class
        parent = node.parent
        while parent:
            if parent.type == "class_definition":
                bases = parent.children_by_field_name("base_class")
                for base in bases:
                    if "ABC" in base.text.decode("utf8"):
                        return True
                break
            parent = parent.parent
            
        return False

    def _is_private_member(self, node: tree_sitter.Node) -> bool:
        """Check if a class member is private."""
        if node.type not in ["function_definition", "variable_declaration"]:
            return False
            
        name = node.child_by_field_name("name").text.decode("utf8")
        return name.startswith("_")

    def _is_overridden_method(self, node: tree_sitter.Node) -> bool:
        """Check if a method is overridden from a base class."""
        if node.type != "function_definition":
            return False
            
        method_name = node.child_by_field_name("name").text.decode("utf8")
        parent = node.parent
        
        while parent:
            if parent.type == "class_definition":
                bases = parent.children_by_field_name("base_class")
                for base in bases:
                    base_name = base.text.decode("utf8")
                    if self._method_exists_in_base(base_name, method_name):
                        return True
                break
            parent = parent.parent
            
        return False

    def _method_exists_in_base(self, base_name: str, method_name: str) -> bool:
        """Check if a method exists in a base class."""
        # This is a simplified check - in a real implementation,
        # you would need to analyze the base class definition
        return True  # Placeholder

    def _has_side_effects(self, node: tree_sitter.Node) -> bool:
        """Check if a method has side effects."""
        if node.type != "function_definition":
            return False
            
        # Check for global variable access
        has_global = False
        for child in node.children_by_field_name("body"):
            if child.type == "global_statement":
                has_global = True
                break
                
        # Check for file operations
        has_file_ops = False
        for child in node.children_by_field_name("body"):
            if child.type == "call":
                func_name = child.child_by_field_name("function").text.decode("utf8")
                if func_name in ["open", "write", "read", "close"]:
                    has_file_ops = True
                    break
                    
        return has_global or has_file_ops

    def _count_dependencies(self, node: tree_sitter.Node) -> int:
        """Count number of dependencies in a method or class."""
        dependencies = 0
        
        def traverse(n: tree_sitter.Node):
            nonlocal dependencies
            if n.type == "call":
                dependencies += 1
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return dependencies 