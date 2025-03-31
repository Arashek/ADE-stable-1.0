from typing import Dict, Any, List, Optional, Union, Tuple, Set
import ast
import logging
from pathlib import Path
import tree_sitter
from tree_sitter import Language, Parser
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pydantic import BaseModel
import re

logger = logging.getLogger(__name__)

class ASTNodeInfo(BaseModel):
    """Information about an AST node"""
    node_type: str
    line_number: int
    column: int
    parent_type: Optional[str]
    children: List[str]
    metadata: Dict[str, Any] = {}

class ASTAnalysisResult(BaseModel):
    """Result of AST analysis"""
    nodes: List[ASTNodeInfo]
    imports: List[str]
    functions: List[str]
    classes: List[str]
    variables: List[str]
    dependencies: List[str]
    complexity: int
    metrics: Dict[str, float]
    suggestions: List[str]

class ASTParser:
    """Specialized parser for code analysis and transformation"""
    
    def __init__(self):
        self.optimization_rules: Dict[str, List[str]] = {}
        self.analysis_metrics: Dict[str, Dict[str, float]] = {}
        
    def parse_code(self, code: str) -> ASTAnalysisResult:
        """Parse code and return detailed AST analysis"""
        try:
            tree = ast.parse(code)
            nodes = self._collect_node_info(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            variables = self._extract_variables(tree)
            dependencies = self._extract_dependencies(tree)
            complexity = self._calculate_complexity(tree)
            metrics = self._calculate_metrics(tree)
            suggestions = self._generate_suggestions(tree, metrics)
            
            return ASTAnalysisResult(
                nodes=nodes,
                imports=imports,
                functions=functions,
                classes=classes,
                variables=variables,
                dependencies=dependencies,
                complexity=complexity,
                metrics=metrics,
                suggestions=suggestions
            )
        except Exception as e:
            raise ValueError(f"Failed to parse code: {str(e)}")
            
    def _collect_node_info(self, tree: ast.AST, parent: Optional[ast.AST] = None) -> List[ASTNodeInfo]:
        """Collect information about all nodes in the AST"""
        nodes = []
        
        class NodeCollector(ast.NodeVisitor):
            def visit(self, node):
                node_info = ASTNodeInfo(
                    node_type=type(node).__name__,
                    line_number=getattr(node, 'lineno', 0),
                    column=getattr(node, 'col_offset', 0),
                    parent_type=type(parent).__name__ if parent else None,
                    children=[type(child).__name__ for child in ast.iter_child_nodes(node)],
                    metadata=self._collect_node_metadata(node)
                )
                nodes.append(node_info)
                return super().visit(node)
                
            def _collect_node_metadata(self, node: ast.AST) -> Dict[str, Any]:
                metadata = {}
                
                if isinstance(node, ast.FunctionDef):
                    metadata['args'] = [arg.arg for arg in node.args.args]
                    metadata['decorators'] = [decorator.id for decorator in node.decorator_list]
                elif isinstance(node, ast.ClassDef):
                    metadata['bases'] = [base.id for base in node.bases]
                    metadata['decorators'] = [decorator.id for decorator in node.decorator_list]
                elif isinstance(node, ast.Call):
                    metadata['func'] = self._get_func_name(node.func)
                    metadata['args'] = len(node.args)
                    metadata['keywords'] = [kw.arg for kw in node.keywords]
                    
                return metadata
                
            def _get_func_name(self, node: ast.AST) -> str:
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self._get_func_name(node.value)}.{node.attr}"
                return "unknown"
                
        collector = NodeCollector()
        collector.visit(tree)
        return nodes
        
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        
        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    imports.append(alias.name)
                    
            def visit_ImportFrom(self, node):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
                    
        visitor = ImportVisitor()
        visitor.visit(tree)
        return imports
        
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function definitions from AST"""
        functions = []
        
        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                functions.append(node.name)
                
        visitor = FunctionVisitor()
        visitor.visit(tree)
        return functions
        
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extract class definitions from AST"""
        classes = []
        
        class ClassVisitor(ast.NodeVisitor):
            def visit_ClassDef(self, node):
                classes.append(node.name)
                
        visitor = ClassVisitor()
        visitor.visit(tree)
        return classes
        
    def _extract_variables(self, tree: ast.AST) -> List[str]:
        """Extract variable assignments from AST"""
        variables = []
        
        class VariableVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
                        
        visitor = VariableVisitor()
        visitor.visit(tree)
        return variables
        
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract dependencies from AST"""
        dependencies = set()
        
        class DependencyVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if node.id not in ['True', 'False', 'None']:
                    dependencies.add(node.id)
                    
            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name):
                    dependencies.add(node.value.id)
                    
        visitor = DependencyVisitor()
        visitor.visit(tree)
        return list(dependencies)
        
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        class ComplexityVisitor(ast.NodeVisitor):
            def visit_If(self, node):
                nonlocal complexity
                complexity += 1
                
            def visit_For(self, node):
                nonlocal complexity
                complexity += 1
                
            def visit_While(self, node):
                nonlocal complexity
                complexity += 1
                
            def visit_ExceptHandler(self, node):
                nonlocal complexity
                complexity += 1
                
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return complexity
        
    def _calculate_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate various code metrics"""
        metrics = {
            'function_count': 0,
            'class_count': 0,
            'variable_count': 0,
            'import_count': 0,
            'line_count': 0,
            'comment_count': 0,
            'complexity': 0,
            'nesting_depth': 0
        }
        
        class MetricsVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                metrics['function_count'] += 1
                
            def visit_ClassDef(self, node):
                metrics['class_count'] += 1
                
            def visit_Assign(self, node):
                metrics['variable_count'] += 1
                
            def visit_Import(self, node):
                metrics['import_count'] += 1
                
            def visit_ImportFrom(self, node):
                metrics['import_count'] += 1
                
        visitor = MetricsVisitor()
        visitor.visit(tree)
        
        # Calculate additional metrics
        metrics['complexity'] = self._calculate_complexity(tree)
        metrics['nesting_depth'] = self._calculate_nesting_depth(tree)
        
        return metrics
        
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        class NestingVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal current_depth, max_depth
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                self.generic_visit(node)
                current_depth -= 1
                
            def visit_ClassDef(self, node):
                nonlocal current_depth, max_depth
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                self.generic_visit(node)
                current_depth -= 1
                
        visitor = NestingVisitor()
        visitor.visit(tree)
        return max_depth
        
    def _generate_suggestions(self, tree: ast.AST, metrics: Dict[str, float]) -> List[str]:
        """Generate code improvement suggestions"""
        suggestions = []
        
        # Check complexity
        if metrics['complexity'] > 10:
            suggestions.append("Consider breaking down complex functions into smaller ones")
            
        # Check nesting depth
        if metrics['nesting_depth'] > 4:
            suggestions.append("Reduce nesting depth by extracting nested functions")
            
        # Check function count
        if metrics['function_count'] > 20:
            suggestions.append("Consider splitting the module into multiple files")
            
        # Check import count
        if metrics['import_count'] > 10:
            suggestions.append("Consider organizing imports and removing unused ones")
            
        return suggestions
        
    def optimize_code(self, code: str, rules: Optional[List[str]] = None) -> str:
        """Optimize code based on AST analysis and rules"""
        try:
            tree = ast.parse(code)
            
            # Apply optimization rules
            if rules:
                for rule in rules:
                    if rule in self.optimization_rules:
                        tree = self._apply_optimization_rule(tree, rule)
                        
            # Apply general optimizations
            tree = self._optimize_imports(tree)
            tree = self._optimize_loops(tree)
            tree = self._optimize_function_calls(tree)
            
            return ast.unparse(tree)
        except Exception as e:
            raise ValueError(f"Failed to optimize code: {str(e)}")
            
    def _apply_optimization_rule(self, tree: ast.AST, rule: str) -> ast.AST:
        """Apply a specific optimization rule"""
        if rule == "remove_unused_imports":
            return self._remove_unused_imports(tree)
        elif rule == "convert_loops":
            return self._optimize_loops(tree)
        elif rule == "simplify_expressions":
            return self._simplify_expressions(tree)
        return tree
        
    def _optimize_imports(self, tree: ast.AST) -> ast.AST:
        """Optimize import statements"""
        class ImportOptimizer(ast.NodeTransformer):
            def visit_Import(self, node):
                # Remove unused imports
                used_names = self._get_used_names(tree)
                node.names = [alias for alias in node.names if alias.name in used_names]
                return node if node.names else None
                
            def visit_ImportFrom(self, node):
                # Remove unused imports
                used_names = self._get_used_names(tree)
                node.names = [alias for alias in node.names if alias.name in used_names]
                return node if node.names else None
                
            def _get_used_names(self, tree: ast.AST) -> Set[str]:
                used_names = set()
                
                class NameCollector(ast.NodeVisitor):
                    def visit_Name(self, node):
                        used_names.add(node.id)
                        
                collector = NameCollector()
                collector.visit(tree)
                return used_names
                
        optimizer = ImportOptimizer()
        return optimizer.visit(tree)
        
    def _optimize_loops(self, tree: ast.AST) -> ast.AST:
        """Optimize loop structures"""
        class LoopOptimizer(ast.NodeTransformer):
            def visit_For(self, node):
                # Convert simple for loops to list comprehensions
                if isinstance(node.body, list) and len(node.body) == 1:
                    if isinstance(node.body[0], ast.Assign):
                        return self._convert_to_list_comprehension(node)
                return node
                
            def _convert_to_list_comprehension(self, node: ast.For) -> ast.ListComp:
                # Implementation of loop to list comprehension conversion
                pass
                
        optimizer = LoopOptimizer()
        return optimizer.visit(tree)
        
    def _optimize_function_calls(self, tree: ast.AST) -> ast.AST:
        """Optimize function calls"""
        class CallOptimizer(ast.NodeTransformer):
            def visit_Call(self, node):
                # Optimize built-in function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'list' and isinstance(node.args[0], ast.List):
                        return node.args[0]
                    elif node.func.id == 'dict' and isinstance(node.args[0], ast.Dict):
                        return node.args[0]
                return node
                
        optimizer = CallOptimizer()
        return optimizer.visit(tree)
        
    def _simplify_expressions(self, tree: ast.AST) -> ast.AST:
        """Simplify expressions"""
        class ExpressionSimplifier(ast.NodeTransformer):
            def visit_BinOp(self, node):
                # Simplify arithmetic expressions
                if isinstance(node.op, ast.Add):
                    if isinstance(node.right, ast.Num) and node.right.n == 0:
                        return node.left
                    if isinstance(node.left, ast.Num) and node.left.n == 0:
                        return node.right
                elif isinstance(node.op, ast.Mult):
                    if isinstance(node.right, ast.Num) and node.right.n == 1:
                        return node.left
                    if isinstance(node.left, ast.Num) and node.left.n == 1:
                        return node.right
                return node
                
        simplifier = ExpressionSimplifier()
        return simplifier.visit(tree)
        
    def register_optimization_rule(self, name: str, rule: str):
        """Register a new optimization rule"""
        self.optimization_rules[name] = rule
        
    def get_optimization_rules(self) -> Dict[str, List[str]]:
        """Get registered optimization rules"""
        return self.optimization_rules
        
    def get_analysis_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get code analysis metrics"""
        return self.analysis_metrics 