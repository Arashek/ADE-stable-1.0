from typing import Dict, List, Optional, Any, Set
import ast
import logging
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class ModuleInfo:
    """Information about a Python module."""
    name: str
    path: str
    imports: List[str]
    classes: List[str]
    functions: List[str]
    dependencies: Set[str]
    complexity: float
    lines_of_code: int
    docstring: Optional[str]

@dataclass
class CodeStructureAnalysis:
    """Results of code structure analysis."""
    modules: Dict[str, ModuleInfo]
    circular_dependencies: List[List[str]]
    unused_imports: Dict[str, List[str]]
    complex_functions: Dict[str, List[str]]
    missing_docstrings: List[str]
    dependency_graph: Dict[str, Set[str]]
    metrics: Dict[str, Any]

class CodeStructureAnalyzer:
    """Analyzes code structure, dependencies, and potential issues."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.complexity_threshold = 10
        self.max_function_length = 50
    
    def analyze_directory(self, directory: str) -> CodeStructureAnalysis:
        """Analyze all Python files in a directory."""
        modules = {}
        circular_deps = []
        unused_imports = {}
        complex_funcs = {}
        missing_docs = []
        dep_graph = {}
        
        # Find all Python files
        python_files = list(Path(directory).rglob("*.py"))
        
        # First pass: collect module information
        for file_path in python_files:
            try:
                module_info = self._analyze_module(file_path)
                modules[module_info.name] = module_info
                dep_graph[module_info.name] = module_info.dependencies
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {str(e)}")
        
        # Second pass: analyze dependencies and issues
        for module_name, module_info in modules.items():
            # Check for unused imports
            unused = self._find_unused_imports(module_info)
            if unused:
                unused_imports[module_name] = unused
            
            # Check for complex functions
            complex_funcs[module_name] = self._find_complex_functions(module_info)
            
            # Check for missing docstrings
            if not module_info.docstring:
                missing_docs.append(module_name)
        
        # Find circular dependencies
        circular_deps = self._find_circular_dependencies(dep_graph)
        
        # Calculate metrics
        metrics = self._calculate_metrics(modules)
        
        return CodeStructureAnalysis(
            modules=modules,
            circular_dependencies=circular_deps,
            unused_imports=unused_imports,
            complex_functions=complex_funcs,
            missing_docstrings=missing_docs,
            dependency_graph=dep_graph,
            metrics=metrics
        )
    
    def _analyze_module(self, file_path: Path) -> ModuleInfo:
        """Analyze a single Python module."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                else:
                    imports.append(node.module or '')
        
        # Extract classes and functions
        classes = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        # Extract docstring
        docstring = ast.get_docstring(tree)
        
        # Calculate complexity
        complexity = self._calculate_complexity(tree)
        
        # Get dependencies
        dependencies = self._extract_dependencies(tree)
        
        return ModuleInfo(
            name=str(file_path.relative_to(file_path.parent.parent)),
            path=str(file_path),
            imports=imports,
            classes=classes,
            functions=functions,
            dependencies=dependencies,
            complexity=complexity,
            lines_of_code=len(content.splitlines()),
            docstring=docstring
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _extract_dependencies(self, tree: ast.AST) -> Set[str]:
        """Extract module dependencies from the AST."""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    dependencies.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.add(node.module.split('.')[0])
        
        return dependencies
    
    def _find_unused_imports(self, module_info: ModuleInfo) -> List[str]:
        """Find unused imports in a module."""
        used_names = set()
        
        # Add all defined names
        used_names.update(module_info.classes)
        used_names.update(module_info.functions)
        
        # Check each import
        unused = []
        for imp in module_info.imports:
            name = imp.split('.')[0]
            if name not in used_names:
                unused.append(imp)
        
        return unused
    
    def _find_complex_functions(self, module_info: ModuleInfo) -> List[str]:
        """Find functions with high complexity."""
        complex_funcs = []
        
        for func_name in module_info.functions:
            # Get function AST
            tree = ast.parse(Path(module_info.path).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    complexity = self._calculate_complexity(node)
                    if complexity > self.complexity_threshold:
                        complex_funcs.append(func_name)
                    break
        
        return complex_funcs
    
    def _find_circular_dependencies(self, dep_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find circular dependencies in the dependency graph."""
        circular = []
        visited = set()
        
        def dfs(node: str, path: List[str], visited_in_path: Set[str]):
            if node in visited_in_path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if cycle not in circular:
                    circular.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            visited_in_path.add(node)
            path.append(node)
            
            for dep in dep_graph.get(node, set()):
                dfs(dep, path, visited_in_path)
            
            path.pop()
            visited_in_path.remove(node)
        
        for node in dep_graph:
            if node not in visited:
                dfs(node, [], set())
        
        return circular
    
    def _calculate_metrics(self, modules: Dict[str, ModuleInfo]) -> Dict[str, Any]:
        """Calculate code metrics."""
        total_lines = sum(m.lines_of_code for m in modules.values())
        total_complexity = sum(m.complexity for m in modules.values())
        total_classes = sum(len(m.classes) for m in modules.values())
        total_functions = sum(len(m.functions) for m in modules.values())
        
        # Calculate additional metrics
        total_imports = sum(len(m.imports) for m in modules.values())
        total_dependencies = sum(len(m.dependencies) for m in modules.values())
        
        # Calculate complexity distribution
        complexity_distribution = {
            "low": 0,    # 1-5
            "medium": 0, # 6-15
            "high": 0,   # 16-30
            "very_high": 0  # >30
        }
        
        for module in modules.values():
            if module.complexity <= 5:
                complexity_distribution["low"] += 1
            elif module.complexity <= 15:
                complexity_distribution["medium"] += 1
            elif module.complexity <= 30:
                complexity_distribution["high"] += 1
            else:
                complexity_distribution["very_high"] += 1
        
        # Calculate dependency metrics
        dependency_metrics = {
            "most_dependent": max(modules.items(), key=lambda x: len(x[1].dependencies))[0] if modules else None,
            "least_dependent": min(modules.items(), key=lambda x: len(x[1].dependencies))[0] if modules else None,
            "average_dependencies": total_dependencies / len(modules) if modules else 0,
            "dependency_distribution": {
                "low": sum(1 for m in modules.values() if len(m.dependencies) <= 2),
                "medium": sum(1 for m in modules.values() if 2 < len(m.dependencies) <= 5),
                "high": sum(1 for m in modules.values() if len(m.dependencies) > 5)
            }
        }
        
        # Calculate code quality metrics
        code_quality = {
            "docstring_coverage": sum(1 for m in modules.values() if m.docstring) / len(modules) if modules else 0,
            "complex_functions_ratio": sum(len(m.complex_functions) for m in modules.values()) / total_functions if total_functions > 0 else 0,
            "unused_imports_ratio": sum(len(m.unused_imports) for m in modules.values()) / total_imports if total_imports > 0 else 0,
            "circular_dependencies_count": len(self._find_circular_dependencies({m.name: m.dependencies for m in modules.values()}))
        }
        
        # Calculate maintainability metrics
        maintainability = {
            "average_function_length": total_lines / total_functions if total_functions > 0 else 0,
            "average_class_size": total_functions / total_classes if total_classes > 0 else 0,
            "module_size_distribution": {
                "small": sum(1 for m in modules.values() if m.lines_of_code <= 100),
                "medium": sum(1 for m in modules.values() if 100 < m.lines_of_code <= 500),
                "large": sum(1 for m in modules.values() if m.lines_of_code > 500)
            }
        }
        
        return {
            "total_modules": len(modules),
            "total_lines_of_code": total_lines,
            "average_complexity": total_complexity / len(modules) if modules else 0,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "average_functions_per_module": total_functions / len(modules) if modules else 0,
            "average_classes_per_module": total_classes / len(modules) if modules else 0,
            "average_lines_per_module": total_lines / len(modules) if modules else 0,
            "complexity_distribution": complexity_distribution,
            "dependency_metrics": dependency_metrics,
            "code_quality": code_quality,
            "maintainability": maintainability
        }
    
    def get_analysis_report(self, analysis: CodeStructureAnalysis) -> str:
        """Generate a human-readable analysis report."""
        report = []
        
        # Summary
        report.append("Code Structure Analysis Report")
        report.append("=" * 50)
        report.append(f"\nTotal Modules: {analysis.metrics['total_modules']}")
        report.append(f"Total Lines of Code: {analysis.metrics['total_lines_of_code']}")
        report.append(f"Average Complexity: {analysis.metrics['average_complexity']:.2f}")
        
        # Issues
        if analysis.circular_dependencies:
            report.append("\nCircular Dependencies:")
            for cycle in analysis.circular_dependencies:
                report.append(f"  {' -> '.join(cycle)}")
        
        if analysis.unused_imports:
            report.append("\nUnused Imports:")
            for module, imports in analysis.unused_imports.items():
                report.append(f"  {module}:")
                for imp in imports:
                    report.append(f"    - {imp}")
        
        if analysis.complex_functions:
            report.append("\nComplex Functions:")
            for module, functions in analysis.complex_functions.items():
                report.append(f"  {module}:")
                for func in functions:
                    report.append(f"    - {func}")
        
        if analysis.missing_docstrings:
            report.append("\nMissing Docstrings:")
            for module in analysis.missing_docstrings:
                report.append(f"  - {module}")
        
        return "\n".join(report) 