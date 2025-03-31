import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import ast
import re
from .agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeAnalysisAgent(Agent):
    """Specialized agent for code analysis and understanding."""
    
    def __init__(self, agent_id: str, name: str, config_path: Optional[str] = None):
        """Initialize the code analysis agent."""
        capabilities = [
            "code_parsing",
            "ast_analysis",
            "dependency_analysis",
            "complexity_analysis",
            "code_search",
            "documentation_generation"
        ]
        super().__init__(agent_id, name, capabilities, config_path)
        
        # Initialize code analysis specific metrics
        self.metrics.update({
            "files_analyzed": 0,
            "average_complexity": 0,
            "total_dependencies": 0,
            "documentation_coverage": 0
        })

    def analyze_code(self, code: str, task_id: str) -> Dict[str, Any]:
        """Analyze code and return insights."""
        try:
            # Parse code into AST
            tree = ast.parse(code)
            
            # Perform various analyses
            analysis_results = {
                "ast_analysis": self._analyze_ast(tree),
                "complexity": self._calculate_complexity(tree),
                "dependencies": self._analyze_dependencies(tree),
                "documentation": self._analyze_documentation(code),
                "metrics": self._calculate_metrics(tree)
            }
            
            # Update agent metrics
            self._update_analysis_metrics(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            self._handle_error(e, task_id)
            return {}

    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze the Abstract Syntax Tree."""
        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        return analyzer.get_results()

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code complexity metrics."""
        complexity = ComplexityAnalyzer()
        complexity.visit(tree)
        return complexity.get_results()

    def _analyze_dependencies(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code dependencies."""
        dependency_analyzer = DependencyAnalyzer()
        dependency_analyzer.visit(tree)
        return dependency_analyzer.get_results()

    def _analyze_documentation(self, code: str) -> Dict[str, Any]:
        """Analyze code documentation."""
        doc_analyzer = DocumentationAnalyzer()
        return doc_analyzer.analyze(code)

    def _calculate_metrics(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate various code metrics."""
        metrics = CodeMetricsAnalyzer()
        metrics.visit(tree)
        return metrics.get_results()

    def _update_analysis_metrics(self, results: Dict[str, Any]) -> None:
        """Update agent metrics with analysis results."""
        with self.state_lock:
            self.metrics["files_analyzed"] += 1
            
            # Update average complexity
            current_avg = self.metrics["average_complexity"]
            new_complexity = results["complexity"]["cyclomatic_complexity"]
            self.metrics["average_complexity"] = (
                (current_avg * (self.metrics["files_analyzed"] - 1) + new_complexity) 
                / self.metrics["files_analyzed"]
            )
            
            # Update total dependencies
            self.metrics["total_dependencies"] += len(results["dependencies"]["imports"])
            
            # Update documentation coverage
            doc_coverage = results["documentation"]["coverage"]
            current_coverage = self.metrics["documentation_coverage"]
            self.metrics["documentation_coverage"] = (
                (current_coverage * (self.metrics["files_analyzed"] - 1) + doc_coverage) 
                / self.metrics["files_analyzed"]
            )

class ASTAnalyzer(ast.NodeVisitor):
    """Analyzer for Abstract Syntax Tree."""
    
    def __init__(self):
        self.results = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": []
        }
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.results["classes"].append({
            "name": node.name,
            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
        })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.results["functions"].append({
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "decorators": [decorator.id for decorator in node.decorator_list if isinstance(decorator, ast.Name)]
        })
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        self.results["imports"].extend(alias.name for alias in node.names)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.results["imports"].extend(f"{node.module}.{alias.name}" for alias in node.names)
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.results["variables"].append(target.id)
        self.generic_visit(node)
    
    def get_results(self) -> Dict[str, Any]:
        return self.results

class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyzer for code complexity."""
    
    def __init__(self):
        self.results = {
            "cyclomatic_complexity": 1,  # Base complexity
            "cognitive_complexity": 0,
            "nesting_depth": 0,
            "branch_count": 0
        }
        self.current_depth = 0
    
    def visit_If(self, node: ast.If) -> None:
        self.results["cyclomatic_complexity"] += 1
        self.results["branch_count"] += 1
        self.current_depth += 1
        self.results["nesting_depth"] = max(self.results["nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_For(self, node: ast.For) -> None:
        self.results["cyclomatic_complexity"] += 1
        self.current_depth += 1
        self.results["nesting_depth"] = max(self.results["nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_While(self, node: ast.While) -> None:
        self.results["cyclomatic_complexity"] += 1
        self.current_depth += 1
        self.results["nesting_depth"] = max(self.results["nesting_depth"], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.results["cyclomatic_complexity"] += 1
        self.generic_visit(node)
    
    def get_results(self) -> Dict[str, Any]:
        return self.results

class DependencyAnalyzer(ast.NodeVisitor):
    """Analyzer for code dependencies."""
    
    def __init__(self):
        self.results = {
            "imports": [],
            "external_calls": [],
            "module_dependencies": set()
        }
    
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.results["imports"].append(alias.name)
            self.results["module_dependencies"].add(alias.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.results["imports"].append(f"{node.module}.{alias.name}")
            self.results["module_dependencies"].add(node.module.split('.')[0])
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            self.results["external_calls"].append(node.func.attr)
        self.generic_visit(node)
    
    def get_results(self) -> Dict[str, Any]:
        self.results["module_dependencies"] = list(self.results["module_dependencies"])
        return self.results

class DocumentationAnalyzer:
    """Analyzer for code documentation."""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        results = {
            "docstrings": [],
            "comments": [],
            "coverage": 0,
            "quality_score": 0
        }
        
        # Extract docstrings
        docstring_pattern = r'"""(.*?)"""'
        docstrings = re.finditer(docstring_pattern, code, re.DOTALL)
        for match in docstrings:
            docstring = match.group(1)
            results["docstrings"].append(docstring.strip())
        
        # Extract single-quoted docstrings
        single_quote_pattern = r"'''(.*?)'''"
        single_quote_docstrings = re.finditer(single_quote_pattern, code, re.DOTALL)
        for match in single_quote_docstrings:
            docstring = match.group(1)
            results["docstrings"].append(docstring.strip())
        
        # Extract comments
        comment_pattern = r'#(.*?)$'
        comments = re.finditer(comment_pattern, code, re.MULTILINE)
        for match in comments:
            results["comments"].append(match.group(1).strip())
        
        # Calculate coverage
        total_functions = len(re.findall(r'def\s+\w+', code))
        total_classes = len(re.findall(r'class\s+\w+', code))
        documented_items = len(results["docstrings"])
        total_items = total_functions + total_classes
        
        if total_items > 0:
            results["coverage"] = documented_items / total_items
        
        # Calculate quality score
        quality_score = 0
        for docstring in results["docstrings"]:
            # Check for key components
            if "Args:" in docstring:
                quality_score += 1
            if "Returns:" in docstring:
                quality_score += 1
            if "Raises:" in docstring:
                quality_score += 1
            if "Examples:" in docstring:
                quality_score += 1
        
        if results["docstrings"]:
            results["quality_score"] = quality_score / len(results["docstrings"])
        
        return results

class CodeMetricsAnalyzer(ast.NodeVisitor):
    """Analyzer for code metrics."""
    
    def __init__(self):
        self.results = {
            "lines_of_code": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "function_count": 0,
            "class_count": 0,
            "variable_count": 0
        }
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.results["function_count"] += 1
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.results["class_count"] += 1
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        self.results["variable_count"] += len(node.targets)
        self.generic_visit(node)
    
    def get_results(self) -> Dict[str, Any]:
        return self.results 