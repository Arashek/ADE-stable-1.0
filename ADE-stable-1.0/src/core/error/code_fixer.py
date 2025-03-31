from typing import Dict, Any, List, Optional, Tuple
import logging
import ast
import difflib
from dataclasses import dataclass
from datetime import datetime
import re
import os
import tempfile
import subprocess
import shutil

logger = logging.getLogger(__name__)

@dataclass
class CodeFix:
    """Represents a proposed code fix"""
    fix_id: str
    description: str
    original_code: str
    fixed_code: str
    confidence: float
    safety_score: float
    validation_results: Dict[str, Any]
    metadata: Dict[str, Any] = None

class CodeFixer:
    """System for analyzing and fixing code issues"""
    
    def __init__(self):
        self.safety_checks = self._load_safety_checks()
        self.validation_rules = self._load_validation_rules()
        self.fix_history: List[Dict[str, Any]] = []
        
    def _load_safety_checks(self) -> Dict[str, Any]:
        """Load safety check rules"""
        return {
            "syntax_check": {
                "enabled": True,
                "weight": 0.3,
                "description": "Validates Python syntax"
            },
            "import_check": {
                "enabled": True,
                "weight": 0.2,
                "description": "Validates imports"
            },
            "type_check": {
                "enabled": True,
                "weight": 0.2,
                "description": "Validates type hints"
            },
            "test_check": {
                "enabled": True,
                "weight": 0.3,
                "description": "Runs unit tests"
            }
        }
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load code validation rules"""
        return {
            "max_line_length": 100,
            "max_complexity": 10,
            "required_docstrings": True,
            "naming_conventions": {
                "functions": "^[a-z_][a-z0-9_]*$",
                "classes": "^[A-Z][a-zA-Z0-9]*$",
                "variables": "^[a-z_][a-z0-9_]*$"
            }
        }
        
    def analyze_code(self, code: str, error_context: Dict[str, Any]) -> List[CodeFix]:
        """Analyze code and generate potential fixes
        
        Args:
            code: Source code to analyze
            error_context: Context about the error
            
        Returns:
            List of proposed fixes
        """
        try:
            fixes = []
            
            # Parse code into AST
            tree = ast.parse(code)
            
            # Analyze AST for potential issues
            issues = self._analyze_ast(tree, error_context)
            
            # Generate fixes for each issue
            for issue in issues:
                fix = self._generate_fix(code, issue, error_context)
                if fix:
                    fixes.append(fix)
                    
            # Sort fixes by confidence and safety score
            fixes.sort(key=lambda x: (x.confidence * x.safety_score), reverse=True)
            return fixes
            
        except Exception as e:
            logger.error(f"Code analysis failed: {str(e)}")
            return []
            
    def _analyze_ast(self, tree: ast.AST, error_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze AST for potential issues
        
        Args:
            tree: AST to analyze
            error_context: Error context
            
        Returns:
            List of identified issues
        """
        issues = []
        
        # Analyze imports
        import_issues = self._analyze_imports(tree)
        issues.extend(import_issues)
        
        # Analyze function definitions
        function_issues = self._analyze_functions(tree)
        issues.extend(function_issues)
        
        # Analyze class definitions
        class_issues = self._analyze_classes(tree)
        issues.extend(class_issues)
        
        # Analyze variable usage
        variable_issues = self._analyze_variables(tree)
        issues.extend(variable_issues)
        
        return issues
        
    def _analyze_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze import statements
        
        Args:
            tree: AST to analyze
            
        Returns:
            List of import issues
        """
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Check for unused imports
                if not self._is_import_used(node, tree):
                    issues.append({
                        "type": "unused_import",
                        "node": node,
                        "description": f"Unused import: {self._get_import_name(node)}",
                        "severity": "warning"
                    })
                    
                # Check for circular imports
                if self._is_circular_import(node):
                    issues.append({
                        "type": "circular_import",
                        "node": node,
                        "description": f"Circular import detected: {self._get_import_name(node)}",
                        "severity": "error"
                    })
                    
        return issues
        
    def _analyze_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze function definitions
        
        Args:
            tree: AST to analyze
            
        Returns:
            List of function issues
        """
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function name
                if not re.match(self.validation_rules["naming_conventions"]["functions"], node.name):
                    issues.append({
                        "type": "naming_convention",
                        "node": node,
                        "description": f"Function name '{node.name}' does not follow convention",
                        "severity": "warning"
                    })
                    
                # Check docstring
                if self.validation_rules["required_docstrings"] and not ast.get_docstring(node):
                    issues.append({
                        "type": "missing_docstring",
                        "node": node,
                        "description": f"Function '{node.name}' is missing docstring",
                        "severity": "warning"
                    })
                    
                # Check complexity
                complexity = self._calculate_complexity(node)
                if complexity > self.validation_rules["max_complexity"]:
                    issues.append({
                        "type": "high_complexity",
                        "node": node,
                        "description": f"Function '{node.name}' has high complexity ({complexity})",
                        "severity": "warning"
                    })
                    
        return issues
        
    def _analyze_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze class definitions
        
        Args:
            tree: AST to analyze
            
        Returns:
            List of class issues
        """
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check class name
                if not re.match(self.validation_rules["naming_conventions"]["classes"], node.name):
                    issues.append({
                        "type": "naming_convention",
                        "node": node,
                        "description": f"Class name '{node.name}' does not follow convention",
                        "severity": "warning"
                    })
                    
                # Check docstring
                if self.validation_rules["required_docstrings"] and not ast.get_docstring(node):
                    issues.append({
                        "type": "missing_docstring",
                        "node": node,
                        "description": f"Class '{node.name}' is missing docstring",
                        "severity": "warning"
                    })
                    
        return issues
        
    def _analyze_variables(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze variable usage
        
        Args:
            tree: AST to analyze
            
        Returns:
            List of variable issues
        """
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                # Check variable name
                if not re.match(self.validation_rules["naming_conventions"]["variables"], node.id):
                    issues.append({
                        "type": "naming_convention",
                        "node": node,
                        "description": f"Variable name '{node.id}' does not follow convention",
                        "severity": "warning"
                    })
                    
        return issues
        
    def _generate_fix(self, code: str, issue: Dict[str, Any], error_context: Dict[str, Any]) -> Optional[CodeFix]:
        """Generate a fix for an issue
        
        Args:
            code: Original code
            issue: Issue to fix
            error_context: Error context
            
        Returns:
            Proposed fix if possible, None otherwise
        """
        try:
            # Generate fix based on issue type
            if issue["type"] == "unused_import":
                return self._fix_unused_import(code, issue)
            elif issue["type"] == "circular_import":
                return self._fix_circular_import(code, issue)
            elif issue["type"] == "naming_convention":
                return self._fix_naming_convention(code, issue)
            elif issue["type"] == "missing_docstring":
                return self._fix_missing_docstring(code, issue)
            elif issue["type"] == "high_complexity":
                return self._fix_high_complexity(code, issue)
                
            return None
            
        except Exception as e:
            logger.error(f"Fix generation failed: {str(e)}")
            return None
            
    def _fix_unused_import(self, code: str, issue: Dict[str, Any]) -> Optional[CodeFix]:
        """Fix unused import
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Proposed fix
        """
        node = issue["node"]
        import_name = self._get_import_name(node)
        
        # Remove the import line
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if import_name in line:
                lines[i] = ""
                
        fixed_code = "\n".join(line for line in lines if line)
        
        return CodeFix(
            fix_id=f"fix_unused_import_{import_name}",
            description=f"Remove unused import: {import_name}",
            original_code=code,
            fixed_code=fixed_code,
            confidence=0.9,
            safety_score=self._calculate_safety_score(fixed_code),
            validation_results=self._validate_fix(fixed_code),
            metadata={"import_name": import_name}
        )
        
    def _fix_circular_import(self, code: str, issue: Dict[str, Any]) -> Optional[CodeFix]:
        """Fix circular import
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Proposed fix
        """
        node = issue["node"]
        import_name = self._get_import_name(node)
        
        # Move import inside function or method
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if import_name in line:
                # Find the next function or class definition
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith(("def ", "class ")):
                        # Move import before function/class
                        import_line = lines[i]
                        lines[i] = ""
                        lines.insert(j, import_line)
                        break
                        
        fixed_code = "\n".join(line for line in lines if line)
        
        return CodeFix(
            fix_id=f"fix_circular_import_{import_name}",
            description=f"Move circular import inside function: {import_name}",
            original_code=code,
            fixed_code=fixed_code,
            confidence=0.8,
            safety_score=self._calculate_safety_score(fixed_code),
            validation_results=self._validate_fix(fixed_code),
            metadata={"import_name": import_name}
        )
        
    def _fix_naming_convention(self, code: str, issue: Dict[str, Any]) -> Optional[CodeFix]:
        """Fix naming convention violation
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Proposed fix
        """
        node = issue["node"]
        old_name = node.id if isinstance(node, ast.Name) else node.name
        
        # Generate new name following convention
        if isinstance(node, ast.FunctionDef):
            new_name = self._convert_to_snake_case(old_name)
        elif isinstance(node, ast.ClassDef):
            new_name = self._convert_to_pascal_case(old_name)
        else:
            new_name = self._convert_to_snake_case(old_name)
            
        # Replace all occurrences
        fixed_code = code.replace(old_name, new_name)
        
        return CodeFix(
            fix_id=f"fix_naming_{old_name}",
            description=f"Rename {old_name} to {new_name} to follow convention",
            original_code=code,
            fixed_code=fixed_code,
            confidence=0.7,
            safety_score=self._calculate_safety_score(fixed_code),
            validation_results=self._validate_fix(fixed_code),
            metadata={"old_name": old_name, "new_name": new_name}
        )
        
    def _fix_missing_docstring(self, code: str, issue: Dict[str, Any]) -> Optional[CodeFix]:
        """Fix missing docstring
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Proposed fix
        """
        node = issue["node"]
        lines = code.splitlines()
        
        # Find the line number of the definition
        for i, line in enumerate(lines):
            if isinstance(node, ast.FunctionDef) and f"def {node.name}" in line:
                # Add docstring
                docstring = f'    """{node.name} function."""'
                lines.insert(i + 1, docstring)
                break
            elif isinstance(node, ast.ClassDef) and f"class {node.name}" in line:
                # Add docstring
                docstring = f'    """{node.name} class."""'
                lines.insert(i + 1, docstring)
                break
                
        fixed_code = "\n".join(lines)
        
        return CodeFix(
            fix_id=f"fix_docstring_{node.name}",
            description=f"Add docstring to {node.name}",
            original_code=code,
            fixed_code=fixed_code,
            confidence=0.8,
            safety_score=self._calculate_safety_score(fixed_code),
            validation_results=self._validate_fix(fixed_code),
            metadata={"node_name": node.name}
        )
        
    def _fix_high_complexity(self, code: str, issue: Dict[str, Any]) -> Optional[CodeFix]:
        """Fix high complexity function
        
        Args:
            code: Original code
            issue: Issue to fix
            
        Returns:
            Proposed fix
        """
        node = issue["node"]
        
        # Extract function body
        lines = code.splitlines()
        start_line = node.lineno - 1
        end_line = node.end_lineno
        
        # Split function into smaller functions
        new_functions = self._split_complex_function(lines[start_line:end_line])
        
        # Replace original function with new functions
        fixed_lines = lines[:start_line] + new_functions + lines[end_line:]
        fixed_code = "\n".join(fixed_lines)
        
        return CodeFix(
            fix_id=f"fix_complexity_{node.name}",
            description=f"Split complex function {node.name} into smaller functions",
            original_code=code,
            fixed_code=fixed_code,
            confidence=0.6,
            safety_score=self._calculate_safety_score(fixed_code),
            validation_results=self._validate_fix(fixed_code),
            metadata={"function_name": node.name}
        )
        
    def _calculate_safety_score(self, code: str) -> float:
        """Calculate safety score for a fix
        
        Args:
            code: Code to evaluate
            
        Returns:
            Safety score between 0 and 1
        """
        scores = []
        
        # Syntax check
        if self.safety_checks["syntax_check"]["enabled"]:
            try:
                ast.parse(code)
                scores.append(1.0)
            except SyntaxError:
                scores.append(0.0)
                
        # Import check
        if self.safety_checks["import_check"]["enabled"]:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if not self._is_import_used(node, tree):
                            scores.append(0.8)
                        else:
                            scores.append(1.0)
            except Exception:
                scores.append(0.0)
                
        # Type check
        if self.safety_checks["type_check"]["enabled"]:
            try:
                # Run mypy in a temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                    
                result = subprocess.run(['mypy', temp_file], capture_output=True, text=True)
                os.unlink(temp_file)
                
                if result.returncode == 0:
                    scores.append(1.0)
                else:
                    scores.append(0.7)
            except Exception:
                scores.append(0.0)
                
        # Test check
        if self.safety_checks["test_check"]["enabled"]:
            try:
                # Run pytest in a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Write code to file
                    with open(os.path.join(temp_dir, 'test_code.py'), 'w') as f:
                        f.write(code)
                        
                    # Write test file
                    with open(os.path.join(temp_dir, 'test_test_code.py'), 'w') as f:
                        f.write(self._generate_test_file(code))
                        
                    # Run tests
                    result = subprocess.run(['pytest', temp_dir], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        scores.append(1.0)
                    else:
                        scores.append(0.6)
            except Exception:
                scores.append(0.0)
                
        # Calculate weighted average
        if not scores:
            return 0.0
            
        weights = [check["weight"] for check in self.safety_checks.values() if check["enabled"]]
        return sum(score * weight for score, weight in zip(scores, weights)) / sum(weights)
        
    def _validate_fix(self, code: str) -> Dict[str, Any]:
        """Validate a code fix
        
        Args:
            code: Code to validate
            
        Returns:
            Validation results
        """
        results = {
            "syntax_valid": True,
            "line_lengths": [],
            "complexity": 0,
            "naming_conventions": [],
            "docstrings": []
        }
        
        try:
            tree = ast.parse(code)
            
            # Check line lengths
            for i, line in enumerate(code.splitlines(), 1):
                if len(line) > self.validation_rules["max_line_length"]:
                    results["line_lengths"].append(i)
                    
            # Check complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.validation_rules["max_complexity"]:
                        results["complexity"] = max(results["complexity"], complexity)
                        
            # Check naming conventions
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if not re.match(self.validation_rules["naming_conventions"]["variables"], node.id):
                        results["naming_conventions"].append(node.id)
                elif isinstance(node, ast.FunctionDef):
                    if not re.match(self.validation_rules["naming_conventions"]["functions"], node.name):
                        results["naming_conventions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if not re.match(self.validation_rules["naming_conventions"]["classes"], node.name):
                        results["naming_conventions"].append(node.name)
                        
            # Check docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        results["docstrings"].append(node.name)
                        
        except SyntaxError:
            results["syntax_valid"] = False
            
        return results
        
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node
        
        Args:
            node: AST node to analyze
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def _is_import_used(self, node: ast.AST, tree: ast.AST) -> bool:
        """Check if an import is used in the code
        
        Args:
            node: Import node to check
            tree: AST to search in
            
        Returns:
            True if import is used
        """
        import_name = self._get_import_name(node)
        
        for child in ast.walk(tree):
            if isinstance(child, ast.Name) and child.id == import_name:
                return True
                
        return False
        
    def _is_circular_import(self, node: ast.AST) -> bool:
        """Check if an import is circular
        
        Args:
            node: Import node to check
            
        Returns:
            True if import is circular
        """
        # This is a simplified check - in practice, you'd need to analyze the full module graph
        import_name = self._get_import_name(node)
        return import_name in self._get_current_module_name()
        
    def _get_import_name(self, node: ast.AST) -> str:
        """Get the name of an import
        
        Args:
            node: Import node
            
        Returns:
            Import name
        """
        if isinstance(node, ast.Import):
            return node.names[0].name
        elif isinstance(node, ast.ImportFrom):
            return node.module or node.names[0].name
        return ""
        
    def _get_current_module_name(self) -> str:
        """Get the name of the current module
        
        Returns:
            Module name
        """
        # This is a placeholder - in practice, you'd need to get the actual module name
        return "current_module"
        
    def _convert_to_snake_case(self, name: str) -> str:
        """Convert a name to snake case
        
        Args:
            name: Name to convert
            
        Returns:
            Snake case name
        """
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return re.sub('[A-Z]', lambda m: m.group().lower(), name)
        
    def _convert_to_pascal_case(self, name: str) -> str:
        """Convert a name to Pascal case
        
        Args:
            name: Name to convert
            
        Returns:
            Pascal case name
        """
        return ''.join(word.capitalize() for word in name.split('_'))
        
    def _split_complex_function(self, lines: List[str]) -> List[str]:
        """Split a complex function into smaller functions
        
        Args:
            lines: Function lines
            
        Returns:
            New function lines
        """
        # This is a simplified implementation - in practice, you'd need more sophisticated analysis
        new_lines = []
        current_function = []
        
        for line in lines:
            if line.strip().startswith('def '):
                if current_function:
                    new_lines.extend(current_function)
                current_function = [line]
            else:
                current_function.append(line)
                
        if current_function:
            new_lines.extend(current_function)
            
        return new_lines
        
    def _generate_test_file(self, code: str) -> str:
        """Generate a test file for the code
        
        Args:
            code: Code to test
            
        Returns:
            Test file content
        """
        # This is a simplified implementation - in practice, you'd need more sophisticated test generation
        return """
import pytest
from test_code import *

def test_basic_functionality():
    # Add basic tests here
    pass
"""
        
    def get_fix_history(self) -> List[Dict[str, Any]]:
        """Get history of applied fixes
        
        Returns:
            List of fix records
        """
        return self.fix_history
        
    def clear_history(self) -> None:
        """Clear fix history"""
        self.fix_history.clear() 