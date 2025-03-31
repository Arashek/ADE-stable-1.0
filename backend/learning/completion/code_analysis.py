from typing import Dict, List, Any, Optional, Set
import ast
import re
from pathlib import Path
import logging
from ...config.logging_config import logger

class CodeAnalyzer:
    """Analyzes code for imports and type information"""
    
    def __init__(self):
        self.import_cache: Dict[str, Set[str]] = {}
        self.type_cache: Dict[str, Dict[str, str]] = {}
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file for imports and types"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                
            tree = ast.parse(code)
            
            # Analyze imports
            imports = self._analyze_imports(tree)
            
            # Analyze types
            types = self._analyze_types(tree)
            
            # Analyze references
            references = self._analyze_references(tree)
            
            return {
                'imports': imports,
                'types': types,
                'references': references
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {}
            
    def _analyze_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Analyze import statements in the code"""
        imports = {
            'imports': [],
            'from_imports': [],
            'aliases': {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports['imports'].append(name.name)
                    if name.asname:
                        imports['aliases'][name.asname] = name.name
                        
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    if name.name == '*':
                        # Handle wildcard imports
                        if module in self.import_cache:
                            imports['from_imports'].extend(self.import_cache[module])
                    else:
                        imports['from_imports'].append(f"{module}.{name.name}")
                        if name.asname:
                            imports['aliases'][name.asname] = f"{module}.{name.name}"
                            
        return imports
        
    def _analyze_types(self, tree: ast.AST) -> Dict[str, str]:
        """Analyze type annotations in the code"""
        types = {}
        
        for node in ast.walk(tree):
            # Function arguments
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    if arg.annotation:
                        types[arg.arg] = self._get_type_string(arg.annotation)
                        
                # Return type
                if node.returns:
                    types['return'] = self._get_type_string(node.returns)
                    
            # Variable assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if node.value:
                            types[target.id] = self._infer_type_from_value(node.value)
                            
        return types
        
    def _analyze_references(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Analyze references to variables and functions"""
        references = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id not in references:
                    references[node.id] = []
                references[node.id].append(self._get_node_location(node))
                
        return references
        
    def _get_type_string(self, node: ast.AST) -> str:
        """Convert an AST node to a type string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self._get_type_string(node.value)
            slice_str = self._get_type_string(node.slice)
            return f"{value}[{slice_str}]"
        elif isinstance(node, ast.BinOp):
            left = self._get_type_string(node.left)
            right = self._get_type_string(node.right)
            return f"{left} | {right}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"
        
    def _infer_type_from_value(self, node: ast.AST) -> str:
        """Infer type from an AST value node"""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return "List"
        elif isinstance(node, ast.Dict):
            return "Dict"
        elif isinstance(node, ast.Set):
            return "Set"
        elif isinstance(node, ast.Tuple):
            return "Tuple"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
        return "Any"
        
    def _get_node_location(self, node: ast.AST) -> str:
        """Get the location of an AST node"""
        return f"line {node.lineno}, column {node.col_offset}"
        
    def suggest_imports(self, code: str, cursor_position: int) -> List[str]:
        """Suggest imports based on code context"""
        try:
            # Get context before cursor
            context = code[:cursor_position]
            
            # Parse context
            tree = ast.parse(context)
            
            # Find undefined names
            undefined = self._find_undefined_names(tree)
            
            # Suggest imports for undefined names
            suggestions = []
            for name in undefined:
                if name in self.import_cache:
                    suggestions.extend(self.import_cache[name])
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting imports: {str(e)}")
            return []
            
    def _find_undefined_names(self, tree: ast.AST) -> Set[str]:
        """Find undefined names in the code"""
        defined = set()
        undefined = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):  # Assignment
                    defined.add(node.id)
                elif isinstance(node.ctx, ast.Load):  # Usage
                    if node.id not in defined:
                        undefined.add(node.id)
                        
        return undefined
        
    def infer_type(self, code: str, cursor_position: int) -> str:
        """Infer type for a variable at cursor position"""
        try:
            # Get context before cursor
            context = code[:cursor_position]
            
            # Parse context
            tree = ast.parse(context)
            
            # Find the variable at cursor position
            var_name = self._find_variable_at_position(tree, cursor_position)
            
            if var_name:
                # Look up type in cache
                if var_name in self.type_cache:
                    return self.type_cache[var_name]
                    
                # Infer type from usage
                return self._infer_type_from_usage(tree, var_name)
                
            return "Any"
            
        except Exception as e:
            logger.error(f"Error inferring type: {str(e)}")
            return "Any"
            
    def _find_variable_at_position(self, tree: ast.AST, position: int) -> Optional[str]:
        """Find the variable name at a specific position"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.col_offset <= position <= node.end_col_offset:
                    return node.id
        return None
        
    def _infer_type_from_usage(self, tree: ast.AST, var_name: str) -> str:
        """Infer type from how a variable is used"""
        usages = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == var_name:
                if isinstance(node.ctx, ast.Load):  # Usage
                    parent = self._get_parent_node(tree, node)
                    if parent:
                        usages.append(self._get_usage_type(parent))
                        
        if not usages:
            return "Any"
            
        # Return most common type
        return max(set(usages), key=usages.count)
        
    def _get_parent_node(self, tree: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Get the parent node of a target node"""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is target:
                    return node
        return None
        
    def _get_usage_type(self, node: ast.AST) -> str:
        """Get the type from a node's usage context"""
        if isinstance(node, ast.Call):
            return "Callable"
        elif isinstance(node, ast.BinOp):
            return "Number"
        elif isinstance(node, ast.Compare):
            return "bool"
        elif isinstance(node, ast.Subscript):
            return "Sequence"
        return "Any"
        
    def resolve_reference(self, code: str, cursor_position: int) -> Optional[str]:
        """Resolve a reference to its definition"""
        try:
            # Get context before cursor
            context = code[:cursor_position]
            
            # Parse context
            tree = ast.parse(context)
            
            # Find the reference at cursor position
            ref_name = self._find_variable_at_position(tree, cursor_position)
            
            if ref_name:
                # Look up reference in cache
                if ref_name in self.type_cache:
                    return self.type_cache[ref_name]
                    
                # Find definition
                return self._find_definition(tree, ref_name)
                
            return None
            
        except Exception as e:
            logger.error(f"Error resolving reference: {str(e)}")
            return None
            
    def _find_definition(self, tree: ast.AST, name: str) -> Optional[str]:
        """Find the definition of a name"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return f"function {name}"
            elif isinstance(node, ast.ClassDef) and node.name == name:
                return f"class {name}"
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return f"variable {name}"
        return None 