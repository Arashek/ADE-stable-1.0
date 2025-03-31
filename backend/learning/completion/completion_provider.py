from typing import List, Dict, Any, Optional
import ast
from pathlib import Path
import logging
from ...config.logging_config import logger
from .code_analysis import CodeAnalyzer

class CompletionProvider:
    """Provides intelligent code completions based on context"""
    
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.completion_cache: Dict[str, List[str]] = {}
        
    def get_completions(self, code: str, cursor_position: int) -> List[Dict[str, Any]]:
        """Get completions at the cursor position"""
        try:
            # Get context before cursor
            context = code[:cursor_position]
            
            # Parse context
            tree = ast.parse(context)
            
            # Get the current line and indentation
            lines = context.split('\n')
            current_line = lines[-1] if lines else ''
            indentation = self._get_indentation(current_line)
            
            # Determine completion type
            completion_type = self._determine_completion_type(current_line)
            
            # Generate completions based on type
            if completion_type == 'import':
                return self._get_import_completions(current_line)
            elif completion_type == 'type':
                return self._get_type_completions(current_line, tree)
            elif completion_type == 'function':
                return self._get_function_completions(current_line, tree)
            elif completion_type == 'line':
                return self._get_line_completions(current_line, tree)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting completions: {str(e)}")
            return []
            
    def _determine_completion_type(self, line: str) -> str:
        """Determine the type of completion needed"""
        line = line.strip()
        
        if line.startswith('import ') or line.startswith('from '):
            return 'import'
        elif line.endswith(':') or line.endswith(' ->'):
            return 'type'
        elif line.endswith('(') or line.endswith(','):
            return 'function'
        else:
            return 'line'
            
    def _get_import_completions(self, line: str) -> List[Dict[str, Any]]:
        """Get import statement completions"""
        completions = []
        
        # Common Python modules
        common_modules = [
            'os', 'sys', 'json', 'datetime', 'random', 'math',
            're', 'collections', 'typing', 'pathlib', 'logging'
        ]
        
        if line.startswith('import '):
            for module in common_modules:
                completions.append({
                    'text': module,
                    'type': 'module',
                    'description': f'Import {module} module'
                })
        elif line.startswith('from '):
            for module in common_modules:
                completions.append({
                    'text': f'{module} import ',
                    'type': 'module',
                    'description': f'Import from {module} module'
                })
                
        return completions
        
    def _get_type_completions(self, line: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Get type annotation completions"""
        completions = []
        
        # Common Python types
        common_types = [
            'int', 'float', 'str', 'bool', 'list', 'dict',
            'set', 'tuple', 'Optional', 'List', 'Dict', 'Any'
        ]
        
        for type_name in common_types:
            completions.append({
                'text': type_name,
                'type': 'type',
                'description': f'Use {type_name} type'
            })
            
        return completions
        
    def _get_function_completions(self, line: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Get function argument completions"""
        completions = []
        
        # Find the current function call
        current_call = self._find_current_call(tree)
        if current_call:
            # Get function name
            if isinstance(current_call.func, ast.Name):
                func_name = current_call.func.id
                
                # Get function definition
                func_def = self._find_function_definition(tree, func_name)
                if func_def:
                    # Get argument names
                    for arg in func_def.args.args:
                        completions.append({
                            'text': f'{arg.arg}=',
                            'type': 'argument',
                            'description': f'Add {arg.arg} argument'
                        })
                        
        return completions
        
    def _get_line_completions(self, line: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Get line completions based on context"""
        completions = []
        
        # Get variable names in scope
        variables = self._get_variables_in_scope(tree)
        
        # Add variable completions
        for var_name in variables:
            completions.append({
                'text': var_name,
                'type': 'variable',
                'description': f'Use {var_name} variable'
            })
            
        # Add method completions for objects
        if '.' in line:
            obj_name = line.split('.')[0].strip()
            if obj_name in variables:
                # Common Python methods
                common_methods = [
                    'append', 'extend', 'pop', 'remove', 'clear',
                    'keys', 'values', 'items', 'get', 'update'
                ]
                
                for method in common_methods:
                    completions.append({
                        'text': method,
                        'type': 'method',
                        'description': f'Call {method} method'
                    })
                    
        return completions
        
    def _find_current_call(self, tree: ast.AST) -> Optional[ast.Call]:
        """Find the current function call in the AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node, 'end_col_offset'):
                    return node
        return None
        
    def _find_function_definition(self, tree: ast.AST, name: str) -> Optional[ast.FunctionDef]:
        """Find a function definition by name"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        return None
        
    def _get_variables_in_scope(self, tree: ast.AST) -> List[str]:
        """Get variables defined in the current scope"""
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
            elif isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    variables.append(arg.arg)
                    
        return variables
        
    def _get_indentation(self, line: str) -> str:
        """Get the indentation of a line"""
        return line[:len(line) - len(line.lstrip())]
        
    def update_cache(self, file_path: str, completions: List[Dict[str, Any]]):
        """Update the completion cache for a file"""
        self.completion_cache[file_path] = completions
        
    def get_cached_completions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get cached completions for a file"""
        return self.completion_cache.get(file_path, []) 