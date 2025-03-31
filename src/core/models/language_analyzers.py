from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import tree_sitter
from .enhanced_code_analysis import EnhancedCodeAnalyzer

class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific analyzers."""
    
    @abstractmethod
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        """Analyze syntax structure for the specific language."""
        pass
        
    @abstractmethod
    def analyze_semantics(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        """Analyze semantic meaning for the specific language."""
        pass
        
    @abstractmethod
    def infer_types(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        """Infer types for the specific language."""
        pass

class PythonAnalyzer(LanguageAnalyzer):
    """Python-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
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
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def analyze_semantics(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "scope": {},
            "references": {},
            "definitions": {},
            "usage": {},
            "type_inference": {},
            "symbol_table": {}
        }
        
        def traverse(node: tree_sitter.Node, scope: str = "global"):
            if node.type == "identifier":
                identifier = node.text.decode("utf8")
                if identifier not in analysis["references"]:
                    analysis["references"][identifier] = []
                analysis["references"][identifier].append({
                    "node": node,
                    "scope": scope,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            elif node.type == "function_definition":
                new_scope = f"{scope}.{node.child_by_field_name('name').text.decode('utf8')}"
                analysis["scope"][new_scope] = {
                    "parent": scope,
                    "variables": set(),
                    "functions": set(),
                    "classes": set()
                }
                
            for child in node.children:
                traverse(child, scope)
                
        traverse(tree.root_node)
        return analysis
        
    def infer_types(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
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
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                return_type = node.child_by_field_name("return_type").text.decode("utf8") if node.child_by_field_name("return_type") else None
                analysis["functions"][func_name] = {
                    "return_type": return_type,
                    "parameters": self._analyze_function_parameters(node),
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_function_parameters(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        parameters = []
        for param in node.children_by_field_name("parameters"):
            parameters.append({
                "name": param.child_by_field_name("name").text.decode("utf8"),
                "type": param.child_by_field_name("type").text.decode("utf8") if param.child_by_field_name("type") else None,
                "default": param.child_by_field_name("default").text.decode("utf8") if param.child_by_field_name("default") else None
            })
        return parameters

class JavaAnalyzer(LanguageAnalyzer):
    """Java-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "imports": [],
            "classes": [],
            "methods": [],
            "fields": [],
            "annotations": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "import_declaration":
                analysis["imports"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "class_declaration":
                analysis["classes"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "modifiers": [mod.text.decode("utf8") for mod in node.children_by_field_name("modifiers")],
                    "extends": node.child_by_field_name("superclass").text.decode("utf8") if node.child_by_field_name("superclass") else None,
                    "implements": [imp.text.decode("utf8") for imp in node.children_by_field_name("interfaces")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "method_declaration":
                analysis["methods"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "modifiers": [mod.text.decode("utf8") for mod in node.children_by_field_name("modifiers")],
                    "return_type": node.child_by_field_name("return_type").text.decode("utf8"),
                    "parameters": [param.text.decode("utf8") for param in node.children_by_field_name("parameters")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def analyze_semantics(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "scope": {},
            "references": {},
            "definitions": {},
            "usage": {},
            "type_inference": {},
            "symbol_table": {}
        }
        
        def traverse(node: tree_sitter.Node, scope: str = "global"):
            if node.type == "identifier":
                identifier = node.text.decode("utf8")
                if identifier not in analysis["references"]:
                    analysis["references"][identifier] = []
                analysis["references"][identifier].append({
                    "node": node,
                    "scope": scope,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            elif node.type == "method_declaration":
                new_scope = f"{scope}.{node.child_by_field_name('name').text.decode('utf8')}"
                analysis["scope"][new_scope] = {
                    "parent": scope,
                    "variables": set(),
                    "methods": set(),
                    "classes": set()
                }
                
            for child in node.children:
                traverse(child, scope)
                
        traverse(tree.root_node)
        return analysis
        
    def infer_types(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "variables": {},
            "methods": {},
            "classes": {},
            "type_parameters": {},
            "generic_types": {}
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "variable_declaration":
                var_name = node.child_by_field_name("name").text.decode("utf8")
                var_type = node.child_by_field_name("type").text.decode("utf8")
                analysis["variables"][var_name] = {
                    "type": var_type,
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            elif node.type == "method_declaration":
                method_name = node.child_by_field_name("name").text.decode("utf8")
                return_type = node.child_by_field_name("return_type").text.decode("utf8")
                analysis["methods"][method_name] = {
                    "return_type": return_type,
                    "parameters": self._analyze_method_parameters(node),
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_method_parameters(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        parameters = []
        for param in node.children_by_field_name("parameters"):
            parameters.append({
                "name": param.child_by_field_name("name").text.decode("utf8"),
                "type": param.child_by_field_name("type").text.decode("utf8"),
                "modifiers": [mod.text.decode("utf8") for mod in param.children_by_field_name("modifiers")]
            })
        return parameters

class TypeScriptAnalyzer(LanguageAnalyzer):
    """TypeScript-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "imports": [],
            "interfaces": [],
            "classes": [],
            "functions": [],
            "variables": [],
            "type_aliases": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "import_statement":
                analysis["imports"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "interface_declaration":
                analysis["interfaces"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "extends": [ext.text.decode("utf8") for ext in node.children_by_field_name("extends")],
                    "members": [member.text.decode("utf8") for member in node.children_by_field_name("body")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "class_declaration":
                analysis["classes"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "extends": node.child_by_field_name("extends").text.decode("utf8") if node.child_by_field_name("extends") else None,
                    "implements": [imp.text.decode("utf8") for imp in node.children_by_field_name("implements")],
                    "members": [member.text.decode("utf8") for member in node.children_by_field_name("body")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def analyze_semantics(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "scope": {},
            "references": {},
            "definitions": {},
            "usage": {},
            "type_inference": {},
            "symbol_table": {}
        }
        
        def traverse(node: tree_sitter.Node, scope: str = "global"):
            if node.type == "identifier":
                identifier = node.text.decode("utf8")
                if identifier not in analysis["references"]:
                    analysis["references"][identifier] = []
                analysis["references"][identifier].append({
                    "node": node,
                    "scope": scope,
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            elif node.type == "function_declaration":
                new_scope = f"{scope}.{node.child_by_field_name('name').text.decode('utf8')}"
                analysis["scope"][new_scope] = {
                    "parent": scope,
                    "variables": set(),
                    "functions": set(),
                    "classes": set()
                }
                
            for child in node.children:
                traverse(child, scope)
                
        traverse(tree.root_node)
        return analysis
        
    def infer_types(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "variables": {},
            "functions": {},
            "classes": {},
            "interfaces": {},
            "type_aliases": {},
            "generic_types": {}
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "variable_declaration":
                var_name = node.child_by_field_name("name").text.decode("utf8")
                var_type = node.child_by_field_name("type").text.decode("utf8") if node.child_by_field_name("type") else None
                analysis["variables"][var_name] = {
                    "type": var_type,
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            elif node.type == "function_declaration":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                return_type = node.child_by_field_name("return_type").text.decode("utf8") if node.child_by_field_name("return_type") else None
                analysis["functions"][func_name] = {
                    "return_type": return_type,
                    "parameters": self._analyze_function_parameters(node),
                    "location": (node.start_point[0], node.end_point[0])
                }
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_function_parameters(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        parameters = []
        for param in node.children_by_field_name("parameters"):
            parameters.append({
                "name": param.child_by_field_name("name").text.decode("utf8"),
                "type": param.child_by_field_name("type").text.decode("utf8") if param.child_by_field_name("type") else None,
                "optional": bool(param.child_by_field_name("optional")),
                "default": param.child_by_field_name("default").text.decode("utf8") if param.child_by_field_name("default") else None
            })
        return parameters

class CppAnalyzer(LanguageAnalyzer):
    """C++-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "includes": [],
            "namespaces": [],
            "classes": [],
            "structs": [],
            "functions": [],
            "templates": [],
            "variables": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "preproc_include":
                analysis["includes"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "namespace_definition":
                analysis["namespaces"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "class_specifier":
                analysis["classes"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "bases": [base.text.decode("utf8") for base in node.children_by_field_name("base_class")],
                    "access_specifiers": [spec.text.decode("utf8") for spec in node.children_by_field_name("access_specifier")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "struct_specifier":
                analysis["structs"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "function_definition":
                analysis["functions"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "return_type": node.child_by_field_name("return_type").text.decode("utf8"),
                    "parameters": [param.text.decode("utf8") for param in node.children_by_field_name("parameters")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis

class CSharpAnalyzer(LanguageAnalyzer):
    """C#-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "using_directives": [],
            "namespaces": [],
            "classes": [],
            "interfaces": [],
            "methods": [],
            "properties": [],
            "fields": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "using_directive":
                analysis["using_directives"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "namespace_declaration":
                analysis["namespaces"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "class_declaration":
                analysis["classes"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "modifiers": [mod.text.decode("utf8") for mod in node.children_by_field_name("modifier")],
                    "base_types": [base.text.decode("utf8") for base in node.children_by_field_name("base_type")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "interface_declaration":
                analysis["interfaces"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "base_types": [base.text.decode("utf8") for base in node.children_by_field_name("base_type")],
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "method_declaration":
                analysis["methods"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "modifiers": [mod.text.decode("utf8") for mod in node.children_by_field_name("modifier")],
                    "return_type": node.child_by_field_name("return_type").text.decode("utf8"),
                    "parameters": [param.text.decode("utf8") for param in node.children_by_field_name("parameters")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis

class GoAnalyzer(LanguageAnalyzer):
    """Go-specific code analyzer."""
    
    def analyze_syntax(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        analysis = {
            "imports": [],
            "packages": [],
            "structs": [],
            "interfaces": [],
            "functions": [],
            "methods": [],
            "variables": [],
            "errors": []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == "import_spec":
                analysis["imports"].append({
                    "text": node.text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "package_clause":
                analysis["packages"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "location": (node.start_point[0], node.end_point[0])
                })
            elif node.type == "type_spec":
                if node.child_by_field_name("type").type == "struct_type":
                    analysis["structs"].append({
                        "name": node.child_by_field_name("name").text.decode("utf8"),
                        "fields": [field.text.decode("utf8") for field in node.children_by_field_name("field")],
                        "location": (node.start_point[0], node.end_point[0])
                    })
                elif node.child_by_field_name("type").type == "interface_type":
                    analysis["interfaces"].append({
                        "name": node.child_by_field_name("name").text.decode("utf8"),
                        "methods": [method.text.decode("utf8") for method in node.children_by_field_name("method")],
                        "location": (node.start_point[0], node.end_point[0])
                    })
            elif node.type == "function_declaration":
                analysis["functions"].append({
                    "name": node.child_by_field_name("name").text.decode("utf8"),
                    "parameters": [param.text.decode("utf8") for param in node.children_by_field_name("parameters")],
                    "results": [result.text.decode("utf8") for result in node.children_by_field_name("result")],
                    "location": (node.start_point[0], node.end_point[0])
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis

# Language analyzer factory
class LanguageAnalyzerFactory:
    """Factory for creating language-specific analyzers."""
    
    _analyzers = {
        "python": PythonAnalyzer,
        "java": JavaAnalyzer,
        "typescript": TypeScriptAnalyzer,
        "cpp": CppAnalyzer,
        "csharp": CSharpAnalyzer,
        "go": GoAnalyzer
    }
    
    @classmethod
    def create_analyzer(cls, language: str) -> LanguageAnalyzer:
        """Create a language-specific analyzer."""
        if language.lower() not in cls._analyzers:
            raise ValueError(f"Unsupported language: {language}")
        return cls._analyzers[language.lower()]() 