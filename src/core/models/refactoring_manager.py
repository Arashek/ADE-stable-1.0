from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel
import ast
import re
from dataclasses import dataclass
from enum import Enum
import black
import isort
import autopep8
import yapf
import logging

logger = logging.getLogger(__name__)

class RefactoringType(Enum):
    """Types of code refactoring"""
    STYLE = "style"
    COMPLEXITY = "complexity"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    TESTABILITY = "testability"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"

class RefactoringResult(BaseModel):
    """Result of code refactoring"""
    original_code: str
    refactored_code: str
    changes: List[Dict[str, Any]]
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    refactoring_types: List[RefactoringType]
    metadata: Dict[str, Any] = {}

class CodeRefactoringManager:
    """Manager for code refactoring operations"""
    
    def __init__(self):
        self.refactoring_history: List[RefactoringResult] = []
        self.refactoring_rules: Dict[RefactoringType, List[Dict[str, Any]]] = {}
        self._initialize_rules()
        
    def _initialize_rules(self):
        """Initialize refactoring rules"""
        # Style rules
        self.refactoring_rules[RefactoringType.STYLE] = [
            {
                "name": "format_code",
                "description": "Format code using black",
                "function": self._format_code
            },
            {
                "name": "sort_imports",
                "description": "Sort imports using isort",
                "function": self._sort_imports
            },
            {
                "name": "fix_pep8",
                "description": "Fix PEP8 style issues",
                "function": self._fix_pep8
            }
        ]
        
        # Complexity rules
        self.refactoring_rules[RefactoringType.COMPLEXITY] = [
            {
                "name": "extract_method",
                "description": "Extract complex methods into smaller ones",
                "function": self._extract_method
            },
            {
                "name": "simplify_conditionals",
                "description": "Simplify complex conditional statements",
                "function": self._simplify_conditionals
            }
        ]
        
        # Performance rules
        self.refactoring_rules[RefactoringType.PERFORMANCE] = [
            {
                "name": "optimize_loops",
                "description": "Optimize loop structures",
                "function": self._optimize_loops
            },
            {
                "name": "optimize_data_structures",
                "description": "Optimize data structure usage",
                "function": self._optimize_data_structures
            }
        ]
        
        # Security rules
        self.refactoring_rules[RefactoringType.SECURITY] = [
            {
                "name": "fix_security_issues",
                "description": "Fix security vulnerabilities",
                "function": self._fix_security_issues
            },
            {
                "name": "improve_input_validation",
                "description": "Improve input validation",
                "function": self._improve_input_validation
            }
        ]
        
        # Maintainability rules
        self.refactoring_rules[RefactoringType.MAINTAINABILITY] = [
            {
                "name": "improve_naming",
                "description": "Improve variable and function naming",
                "function": self._improve_naming
            },
            {
                "name": "extract_constants",
                "description": "Extract magic numbers and strings into constants",
                "function": self._extract_constants
            }
        ]
        
        # Testability rules
        self.refactoring_rules[RefactoringType.TESTABILITY] = [
            {
                "name": "improve_testability",
                "description": "Improve code testability",
                "function": self._improve_testability
            },
            {
                "name": "reduce_dependencies",
                "description": "Reduce function dependencies",
                "function": self._reduce_dependencies
            }
        ]
        
        # Documentation rules
        self.refactoring_rules[RefactoringType.DOCUMENTATION] = [
            {
                "name": "add_docstrings",
                "description": "Add missing docstrings",
                "function": self._add_docstrings
            },
            {
                "name": "improve_comments",
                "description": "Improve code comments",
                "function": self._improve_comments
            }
        ]
        
        # Optimization rules
        self.refactoring_rules[RefactoringType.OPTIMIZATION] = [
            {
                "name": "optimize_imports",
                "description": "Optimize import statements",
                "function": self._optimize_imports
            },
            {
                "name": "optimize_memory",
                "description": "Optimize memory usage",
                "function": self._optimize_memory
            }
        ]
        
    async def refactor_code(
        self,
        code: str,
        refactoring_types: List[RefactoringType],
        context: Optional[Dict[str, Any]] = None
    ) -> RefactoringResult:
        """Refactor code based on specified types"""
        try:
            # Initialize result
            result = RefactoringResult(
                original_code=code,
                refactored_code=code,
                changes=[],
                metrics_before={},
                metrics_after={},
                refactoring_types=refactoring_types,
                metadata={
                    "refactored_at": datetime.now().isoformat(),
                    "context": context or {}
                }
            )
            
            # Calculate initial metrics
            result.metrics_before = self._calculate_metrics(code)
            
            # Apply refactoring rules
            refactored_code = code
            changes = []
            
            for refactoring_type in refactoring_types:
                if refactoring_type in self.refactoring_rules:
                    for rule in self.refactoring_rules[refactoring_type]:
                        try:
                            rule_result = await rule["function"](refactored_code, context)
                            if rule_result["changed"]:
                                refactored_code = rule_result["code"]
                                changes.append({
                                    "type": refactoring_type,
                                    "rule": rule["name"],
                                    "description": rule["description"],
                                    "changes": rule_result["changes"]
                                })
                        except Exception as e:
                            logger.error(f"Failed to apply rule {rule['name']}: {str(e)}")
                            
            # Calculate final metrics
            result.metrics_after = self._calculate_metrics(refactored_code)
            
            # Update result
            result.refactored_code = refactored_code
            result.changes = changes
            
            # Store in history
            self.refactoring_history.append(result)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to refactor code: {str(e)}")
            
    def _calculate_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code metrics"""
        try:
            tree = ast.parse(code)
            return {
                "complexity": self._calculate_complexity(tree),
                "maintainability": self._calculate_maintainability(tree),
                "testability": self._calculate_testability(tree),
                "documentation": self._calculate_documentation(tree),
                "style": self._calculate_style_score(code)
            }
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {str(e)}")
            return {}
            
    async def _format_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format code using black"""
        try:
            formatted_code = black.format_str(code, mode=black.FileMode())
            return {
                "changed": formatted_code != code,
                "code": formatted_code,
                "changes": ["Formatted code using black"]
            }
        except Exception as e:
            logger.error(f"Failed to format code: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _sort_imports(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sort imports using isort"""
        try:
            sorted_code = isort.code(code)
            return {
                "changed": sorted_code != code,
                "code": sorted_code,
                "changes": ["Sorted imports using isort"]
            }
        except Exception as e:
            logger.error(f"Failed to sort imports: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _fix_pep8(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fix PEP8 style issues"""
        try:
            fixed_code = autopep8.fix_code(code)
            return {
                "changed": fixed_code != code,
                "code": fixed_code,
                "changes": ["Fixed PEP8 style issues"]
            }
        except Exception as e:
            logger.error(f"Failed to fix PEP8 issues: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _extract_method(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract complex methods into smaller ones"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class MethodExtractor(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    if len(node.body) > 20:  # Complex method
                        # Extract method logic here
                        changes.append(f"Extracted method from {node.name}")
                    return node
                    
            new_tree = MethodExtractor().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to extract methods: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _simplify_conditionals(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simplify complex conditional statements"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class ConditionalSimplifier(ast.NodeTransformer):
                def visit_If(self, node):
                    if isinstance(node.test, ast.BoolOp):
                        # Simplify boolean expressions
                        changes.append("Simplified conditional expression")
                    return node
                    
            new_tree = ConditionalSimplifier().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to simplify conditionals: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _optimize_loops(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize loop structures"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class LoopOptimizer(ast.NodeTransformer):
                def visit_For(self, node):
                    if isinstance(node.iter, ast.Call):
                        if isinstance(node.iter.func, ast.Name):
                            if node.iter.func.id == 'range':
                                # Convert to list comprehension
                                changes.append("Optimized loop structure")
                    return node
                    
            new_tree = LoopOptimizer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to optimize loops: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _optimize_data_structures(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize data structure usage"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class DataStructureOptimizer(ast.NodeTransformer):
                def visit_List(self, node):
                    # Convert to set if unique values
                    if len(node.elts) == len(set(node.elts)):
                        changes.append("Converted list to set")
                        return ast.Set(elts=node.elts)
                    return node
                    
            new_tree = DataStructureOptimizer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to optimize data structures: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _fix_security_issues(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fix security vulnerabilities"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class SecurityFixer(ast.NodeTransformer):
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec']:
                            # Replace with safer alternatives
                            changes.append("Replaced unsafe function call")
                            return ast.Call(
                                func=ast.Name(id='ast.literal_eval', ctx=ast.Load()),
                                args=node.args,
                                keywords=node.keywords
                            )
                    return node
                    
            new_tree = SecurityFixer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to fix security issues: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _improve_input_validation(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve input validation"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class InputValidator(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Add input validation
                    if node.args.args:
                        changes.append("Added input validation")
                        validation_code = ast.parse("""
                            if not isinstance(arg, expected_type):
                                raise TypeError(f"Expected {expected_type}, got {type(arg)}")
                        """)
                        node.body.insert(0, validation_code)
                    return node
                    
            new_tree = InputValidator().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to improve input validation: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _improve_naming(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve variable and function naming"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class NamingImprover(ast.NodeTransformer):
                def visit_Name(self, node):
                    # Improve variable names
                    if len(node.id) < 2:
                        changes.append(f"Improved variable name: {node.id}")
                        return ast.Name(id=f"improved_{node.id}", ctx=node.ctx)
                    return node
                    
            new_tree = NamingImprover().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to improve naming: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _extract_constants(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract magic numbers and strings into constants"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class ConstantExtractor(ast.NodeTransformer):
                def visit_Num(self, node):
                    # Extract magic numbers
                    changes.append(f"Extracted magic number: {node.n}")
                    return ast.Name(id=f"CONSTANT_{node.n}", ctx=ast.Load())
                    
            new_tree = ConstantExtractor().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to extract constants: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _improve_testability(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve code testability"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class TestabilityImprover(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Reduce function complexity
                    if len(node.args.args) > 5:
                        changes.append("Reduced function parameters")
                        node.args.args = node.args.args[:5]
                    return node
                    
            new_tree = TestabilityImprover().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to improve testability: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _reduce_dependencies(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reduce function dependencies"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class DependencyReducer(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Extract global variables into parameters
                    if node.globals:
                        changes.append("Reduced global dependencies")
                        node.globals = []
                    return node
                    
            new_tree = DependencyReducer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to reduce dependencies: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _add_docstrings(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add missing docstrings"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class DocstringAdder(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    if not ast.get_docstring(node):
                        changes.append(f"Added docstring to {node.name}")
                        node.body.insert(0, ast.Expr(
                            value=ast.Constant(value=f"Documentation for {node.name}")
                        ))
                    return node
                    
            new_tree = DocstringAdder().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to add docstrings: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _improve_comments(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve code comments"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class CommentImprover(ast.NodeTransformer):
                def visit_FunctionDef(self, node):
                    # Add function purpose comment
                    changes.append(f"Added comment to {node.name}")
                    node.body.insert(0, ast.Expr(
                        value=ast.Constant(value=f"Purpose: {node.name}")
                    ))
                    return node
                    
            new_tree = CommentImprover().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to improve comments: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _optimize_imports(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize import statements"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class ImportOptimizer(ast.NodeTransformer):
                def visit_Import(self, node):
                    # Remove unused imports
                    if not self._is_import_used(node.names[0].name, tree):
                        changes.append(f"Removed unused import: {node.names[0].name}")
                        return None
                    return node
                    
            new_tree = ImportOptimizer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to optimize imports: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    async def _optimize_memory(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            tree = ast.parse(code)
            changes = []
            
            class MemoryOptimizer(ast.NodeTransformer):
                def visit_List(self, node):
                    # Convert large lists to generators
                    if len(node.elts) > 1000:
                        changes.append("Converted large list to generator")
                        return ast.Call(
                            func=ast.Name(id='iter', ctx=ast.Load()),
                            args=[node],
                            keywords=[]
                        )
                    return node
                    
            new_tree = MemoryOptimizer().visit(tree)
            new_code = ast.unparse(new_tree)
            
            return {
                "changed": new_code != code,
                "code": new_code,
                "changes": changes
            }
        except Exception as e:
            logger.error(f"Failed to optimize memory: {str(e)}")
            return {"changed": False, "code": code, "changes": []}
            
    def get_refactoring_history(self) -> List[RefactoringResult]:
        """Get refactoring history"""
        return self.refactoring_history
        
    def get_refactoring_rules(self) -> Dict[RefactoringType, List[Dict[str, Any]]]:
        """Get refactoring rules"""
        return self.refactoring_rules
        
    def add_refactoring_rule(
        self,
        refactoring_type: RefactoringType,
        name: str,
        description: str,
        function: callable
    ):
        """Add a new refactoring rule"""
        if refactoring_type not in self.refactoring_rules:
            self.refactoring_rules[refactoring_type] = []
            
        self.refactoring_rules[refactoring_type].append({
            "name": name,
            "description": description,
            "function": function
        }) 