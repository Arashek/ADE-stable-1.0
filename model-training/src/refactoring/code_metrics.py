"""
Enhanced code quality metrics for refactoring analysis.
"""

import ast
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
import re
from collections import defaultdict

@dataclass
class EnhancedMetrics:
    """Enhanced code quality metrics."""
    # Basic metrics
    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float
    function_count: int
    avg_function_length: float
    variable_count: int
    nesting_depth: int
    duplication_ratio: float
    naming_score: float
    
    # Advanced metrics
    cognitive_complexity: float
    halstead_metrics: Dict[str, float]
    cohesion_metrics: Dict[str, float]
    coupling_metrics: Dict[str, float]
    inheritance_metrics: Dict[str, float]
    dependency_metrics: Dict[str, float]
    testability_metrics: Dict[str, float]
    security_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    maintainability_metrics: Dict[str, float]
    readability_metrics: Dict[str, float]

class CodeMetricsAnalyzer:
    """Analyzes code quality metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze(self, code: str) -> EnhancedMetrics:
        """Analyze code and return enhanced metrics."""
        tree = ast.parse(code)
        
        # Basic metrics
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        maintainability_index = self._calculate_maintainability_index(tree)
        lines_of_code = len(code.splitlines())
        comment_ratio = self._calculate_comment_ratio(code)
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        avg_function_length = self._calculate_avg_function_length(tree)
        variable_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Name)])
        nesting_depth = self._calculate_nesting_depth(tree)
        duplication_ratio = self._calculate_duplication_ratio(code)
        naming_score = self._calculate_naming_score(tree)
        
        # Advanced metrics
        cognitive_complexity = self._calculate_cognitive_complexity(tree)
        halstead_metrics = self._calculate_halstead_metrics(code)
        cohesion_metrics = self._calculate_cohesion_metrics(tree)
        coupling_metrics = self._calculate_coupling_metrics(tree)
        inheritance_metrics = self._calculate_inheritance_metrics(tree)
        dependency_metrics = self._calculate_dependency_metrics(tree)
        testability_metrics = self._calculate_testability_metrics(tree)
        security_metrics = self._calculate_security_metrics(tree)
        performance_metrics = self._calculate_performance_metrics(tree)
        maintainability_metrics = self._calculate_maintainability_metrics(tree)
        readability_metrics = self._calculate_readability_metrics(code)
        
        return EnhancedMetrics(
            cyclomatic_complexity=cyclomatic_complexity,
            maintainability_index=maintainability_index,
            lines_of_code=lines_of_code,
            comment_ratio=comment_ratio,
            function_count=function_count,
            avg_function_length=avg_function_length,
            variable_count=variable_count,
            nesting_depth=nesting_depth,
            duplication_ratio=duplication_ratio,
            naming_score=naming_score,
            cognitive_complexity=cognitive_complexity,
            halstead_metrics=halstead_metrics,
            cohesion_metrics=cohesion_metrics,
            coupling_metrics=coupling_metrics,
            inheritance_metrics=inheritance_metrics,
            dependency_metrics=dependency_metrics,
            testability_metrics=testability_metrics,
            security_metrics=security_metrics,
            performance_metrics=performance_metrics,
            maintainability_metrics=maintainability_metrics,
            readability_metrics=readability_metrics
        )
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> float:
        """Calculate cognitive complexity."""
        complexity = 0.0
        
        for node in ast.walk(tree):
            # Basic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 2
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            
            # Nesting complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try)):
                complexity += self._get_nesting_level(node) * 0.5
            
            # Control flow complexity
            if isinstance(node, ast.Break):
                complexity += 1
            elif isinstance(node, ast.Continue):
                complexity += 1
            elif isinstance(node, ast.Raise):
                complexity += 1
        
        return complexity
    
    def _calculate_halstead_metrics(self, code: str) -> Dict[str, float]:
        """Calculate Halstead metrics."""
        # Tokenize code
        tokens = re.findall(r'\b\w+\b', code)
        
        # Count unique operators and operands
        operators = set()
        operands = set()
        
        for token in tokens:
            if token in ['+', '-', '*', '/', '=', '==', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not']:
                operators.add(token)
            else:
                operands.add(token)
        
        n1 = len(operators)  # unique operators
        n2 = len(operands)   # unique operands
        N1 = sum(1 for t in tokens if t in operators)  # total operators
        N2 = sum(1 for t in tokens if t in operands)   # total operands
        
        # Calculate metrics
        program_length = N1 + N2
        vocabulary = n1 + n2
        volume = program_length * math.log2(vocabulary)
        difficulty = (n1 * N2) / (2 * n2)
        effort = difficulty * volume
        time = effort / 18
        bugs = volume / 3000
        
        return {
            'program_length': program_length,
            'vocabulary': vocabulary,
            'volume': volume,
            'difficulty': difficulty,
            'effort': effort,
            'time': time,
            'bugs': bugs
        }
    
    def _calculate_cohesion_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate cohesion metrics."""
        metrics = {
            'lcom': 0.0,  # Lack of Cohesion of Methods
            'tcc': 0.0,   # Tight Class Cohesion
            'lcc': 0.0,   # Loose Class Cohesion
            'cam': 0.0,   # Cohesion Among Methods
            'cbm': 0.0,   # Coupling Between Methods
            'amc': 0.0    # Average Method Cohesion
        }
        
        # Find all classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        for cls in classes:
            # Get methods and their attributes
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            method_attrs = defaultdict(set)
            
            for method in methods:
                for node in ast.walk(method):
                    if isinstance(node, ast.Name):
                        method_attrs[method.name].add(node.id)
            
            # Calculate LCOM
            if len(methods) > 1:
                shared_attrs = set.intersection(*method_attrs.values())
                metrics['lcom'] += len(methods) - len(shared_attrs)
            
            # Calculate TCC and LCC
            method_pairs = list(combinations(methods, 2))
            connected_pairs = 0
            
            for m1, m2 in method_pairs:
                if method_attrs[m1.name] & method_attrs[m2.name]:
                    connected_pairs += 1
            
            if method_pairs:
                metrics['tcc'] += connected_pairs / len(method_pairs)
                metrics['lcc'] += connected_pairs / (len(methods) * (len(methods) - 1) / 2)
        
        return metrics
    
    def _calculate_coupling_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate coupling metrics."""
        metrics = {
            'cbo': 0.0,   # Coupling Between Objects
            'rfc': 0.0,   # Response For Class
            'cf': 0.0,    # Coupling Factor
            'ic': 0.0,    # Inheritance Coupling
            'cbm': 0.0,   # Coupling Between Methods
            'acbm': 0.0,  # Average Coupling Between Methods
            'ncbm': 0.0,  # Normalized Coupling Between Methods
            'cam': 0.0,   # Cohesion Among Methods
            'mfa': 0.0,   # Message Fan Out
            'mif': 0.0    # Method Inheritance Factor
        }
        
        # Find all classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        for cls in classes:
            # Get methods and their calls
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            method_calls = defaultdict(set)
            
            for method in methods:
                for node in ast.walk(method):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            method_calls[method.name].add(node.func.id)
            
            # Calculate CBO
            external_calls = sum(1 for calls in method_calls.values() 
                               for call in calls if call not in [m.name for m in methods])
            metrics['cbo'] += external_calls
            
            # Calculate RFC
            metrics['rfc'] += len(methods) + external_calls
            
            # Calculate CF
            total_possible_couplings = len(methods) * (len(methods) - 1)
            if total_possible_couplings > 0:
                metrics['cf'] += len(method_calls) / total_possible_couplings
        
        return metrics
    
    def _calculate_inheritance_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate inheritance metrics."""
        metrics = {
            'dit': 0.0,   # Depth of Inheritance Tree
            'noc': 0.0,   # Number of Children
            'nop': 0.0,   # Number of Parents
            'moa': 0.0,   # Measure of Aggregation
            'mfa': 0.0,   # Method Inheritance Factor
            'ahf': 0.0,   # Attribute Hiding Factor
            'mhf': 0.0,   # Method Hiding Factor
            'aif': 0.0,   # Attribute Inheritance Factor
            'mif': 0.0    # Method Inheritance Factor
        }
        
        # Build inheritance graph
        inheritance_graph = defaultdict(list)
        class_methods = defaultdict(set)
        class_attrs = defaultdict(set)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        inheritance_graph[base.id].append(node.name)
                
                # Collect methods and attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_methods[node.name].add(item.name)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_attrs[node.name].add(target.id)
        
        # Calculate metrics
        for cls_name, children in inheritance_graph.items():
            metrics['noc'] += len(children)
            metrics['dit'] = max(metrics['dit'], self._calculate_dit(cls_name, inheritance_graph))
            
            # Calculate inheritance factors
            inherited_methods = set()
            inherited_attrs = set()
            
            for child in children:
                inherited_methods.update(class_methods[child])
                inherited_attrs.update(class_attrs[child])
            
            if class_methods[cls_name]:
                metrics['mif'] = len(inherited_methods) / len(class_methods[cls_name])
            if class_attrs[cls_name]:
                metrics['aif'] = len(inherited_attrs) / len(class_attrs[cls_name])
        
        return metrics
    
    def _calculate_dependency_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate dependency metrics."""
        metrics = {
            'fan_in': 0.0,    # Fan In
            'fan_out': 0.0,   # Fan Out
            'instability': 0.0,  # Instability
            'abstractness': 0.0, # Abstractness
            'distance': 0.0,     # Distance from main sequence
            'normalized_distance': 0.0  # Normalized distance
        }
        
        # Find all modules and their dependencies
        modules = defaultdict(set)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    modules['current'].add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules['current'].add(node.module.split('.')[0])
        
        # Calculate fan in/out
        metrics['fan_out'] = len(modules['current'])
        
        # Calculate instability
        total_deps = metrics['fan_in'] + metrics['fan_out']
        if total_deps > 0:
            metrics['instability'] = metrics['fan_out'] / total_deps
        
        return metrics
    
    def _calculate_testability_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate testability metrics."""
        metrics = {
            'complexity': 0.0,      # Overall complexity
            'dependencies': 0.0,     # Number of dependencies
            'coupling': 0.0,         # Coupling level
            'cohesion': 0.0,         # Cohesion level
            'encapsulation': 0.0,    # Encapsulation level
            'inheritance': 0.0,      # Inheritance complexity
            'polymorphism': 0.0,     # Polymorphism level
            'test_coverage': 0.0,    # Estimated test coverage
            'maintainability': 0.0,  # Maintainability score
            'readability': 0.0       # Readability score
        }
        
        # Calculate complexity
        metrics['complexity'] = self._calculate_cognitive_complexity(tree)
        
        # Calculate dependencies
        metrics['dependencies'] = len([node for node in ast.walk(tree) 
                                     if isinstance(node, (ast.Import, ast.ImportFrom))])
        
        # Calculate coupling and cohesion
        coupling_metrics = self._calculate_coupling_metrics(tree)
        cohesion_metrics = self._calculate_cohesion_metrics(tree)
        
        metrics['coupling'] = coupling_metrics['cbo']
        metrics['cohesion'] = 1 - cohesion_metrics['lcom']
        
        # Calculate encapsulation
        private_members = len([node for node in ast.walk(tree) 
                             if isinstance(node, ast.Name) and node.id.startswith('_')])
        total_members = len([node for node in ast.walk(tree) 
                           if isinstance(node, ast.Name)])
        
        if total_members > 0:
            metrics['encapsulation'] = private_members / total_members
        
        # Calculate inheritance complexity
        inheritance_metrics = self._calculate_inheritance_metrics(tree)
        metrics['inheritance'] = inheritance_metrics['dit']
        
        # Calculate overall testability score
        metrics['testability'] = (
            (1 - metrics['complexity'] / 100) * 0.3 +
            (1 - metrics['dependencies'] / 50) * 0.2 +
            (1 - metrics['coupling'] / 20) * 0.2 +
            metrics['cohesion'] * 0.2 +
            metrics['encapsulation'] * 0.1
        )
        
        return metrics
    
    def _calculate_security_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate security metrics."""
        metrics = {
            'vulnerabilities': 0.0,  # Number of potential vulnerabilities
            'risk_level': 0.0,       # Overall risk level
            'input_validation': 0.0, # Input validation score
            'authentication': 0.0,    # Authentication score
            'authorization': 0.0,     # Authorization score
            'data_protection': 0.0,   # Data protection score
            'error_handling': 0.0,    # Error handling score
            'logging': 0.0,          # Logging score
            'crypto_usage': 0.0,     # Cryptography usage score
            'secure_config': 0.0     # Secure configuration score
        }
        
        # Check for common security issues
        for node in ast.walk(tree):
            # SQL injection
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'execute':
                    metrics['vulnerabilities'] += 1
            
            # Hardcoded credentials
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in ['password', 'secret', 'key']:
                        metrics['vulnerabilities'] += 1
            
            # Unsafe eval
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    metrics['vulnerabilities'] += 1
        
        # Calculate risk level
        metrics['risk_level'] = min(1.0, metrics['vulnerabilities'] / 10)
        
        return metrics
    
    def _calculate_performance_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate performance metrics."""
        metrics = {
            'complexity': 0.0,       # Algorithmic complexity
            'memory_usage': 0.0,     # Memory usage score
            'cpu_usage': 0.0,        # CPU usage score
            'io_operations': 0.0,    # I/O operations score
            'concurrency': 0.0,      # Concurrency score
            'caching': 0.0,          # Caching score
            'optimization': 0.0,     # Optimization score
            'resource_usage': 0.0,   # Resource usage score
            'scalability': 0.0,      # Scalability score
            'efficiency': 0.0        # Overall efficiency score
        }
        
        # Calculate algorithmic complexity
        metrics['complexity'] = self._calculate_cognitive_complexity(tree)
        
        # Check for performance issues
        for node in ast.walk(tree):
            # Nested loops
            if isinstance(node, (ast.For, ast.While)):
                if self._get_nesting_level(node) > 2:
                    metrics['complexity'] += 1
            
            # Large data structures
            if isinstance(node, ast.List):
                if len(node.elts) > 1000:
                    metrics['memory_usage'] += 1
            
            # File operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ['open', 'read', 'write']:
                    metrics['io_operations'] += 1
        
        # Calculate efficiency score
        metrics['efficiency'] = (
            (1 - metrics['complexity'] / 100) * 0.4 +
            (1 - metrics['memory_usage'] / 10) * 0.3 +
            (1 - metrics['io_operations'] / 10) * 0.3
        )
        
        return metrics
    
    def _calculate_maintainability_metrics(self, tree: ast.AST) -> Dict[str, float]:
        """Calculate maintainability metrics."""
        metrics = {
            'complexity': 0.0,       # Code complexity
            'size': 0.0,             # Code size
            'duplication': 0.0,      # Code duplication
            'documentation': 0.0,    # Documentation quality
            'modularity': 0.0,       # Modularity
            'testability': 0.0,      # Testability
            'readability': 0.0,      # Readability
            'consistency': 0.0,      # Code consistency
            'dependencies': 0.0,     # Dependencies
            'maintainability': 0.0   # Overall maintainability
        }
        
        # Calculate basic metrics
        metrics['complexity'] = self._calculate_cognitive_complexity(tree)
        metrics['size'] = len(ast.unparse(tree).splitlines())
        metrics['duplication'] = self._calculate_duplication_ratio(ast.unparse(tree))
        
        # Calculate documentation quality
        docstrings = len([node for node in ast.walk(tree) 
                         if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)])
        metrics['documentation'] = min(1.0, docstrings / 10)
        
        # Calculate modularity
        functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        metrics['modularity'] = min(1.0, (functions + classes) / 20)
        
        # Calculate overall maintainability score
        metrics['maintainability'] = (
            (1 - metrics['complexity'] / 100) * 0.3 +
            (1 - metrics['size'] / 1000) * 0.2 +
            (1 - metrics['duplication']) * 0.2 +
            metrics['documentation'] * 0.15 +
            metrics['modularity'] * 0.15
        )
        
        return metrics
    
    def _calculate_readability_metrics(self, code: str) -> Dict[str, float]:
        """Calculate readability metrics."""
        metrics = {
            'lines_per_function': 0.0,    # Average lines per function
            'complexity': 0.0,             # Code complexity
            'comment_ratio': 0.0,          # Comment ratio
            'naming': 0.0,                 # Naming quality
            'formatting': 0.0,             # Code formatting
            'documentation': 0.0,          # Documentation quality
            'structure': 0.0,              # Code structure
            'consistency': 0.0,            # Code consistency
            'clarity': 0.0,                # Code clarity
            'readability': 0.0             # Overall readability
        }
        
        # Calculate basic metrics
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        metrics['lines_per_function'] = len(code.splitlines()) / max(1, len(functions))
        metrics['complexity'] = self._calculate_cognitive_complexity(tree)
        metrics['comment_ratio'] = self._calculate_comment_ratio(code)
        metrics['naming'] = self._calculate_naming_score(tree)
        
        # Calculate formatting score
        indentation_errors = len(re.findall(r'^\s*[^\s]', code, re.MULTILINE))
        metrics['formatting'] = 1 - min(1.0, indentation_errors / 10)
        
        # Calculate documentation quality
        docstrings = len([node for node in ast.walk(tree) 
                         if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)])
        metrics['documentation'] = min(1.0, docstrings / 10)
        
        # Calculate structure score
        metrics['structure'] = min(1.0, len(functions) / 20)
        
        # Calculate overall readability score
        metrics['readability'] = (
            (1 - metrics['lines_per_function'] / 50) * 0.2 +
            (1 - metrics['complexity'] / 100) * 0.2 +
            metrics['comment_ratio'] * 0.15 +
            metrics['naming'] * 0.15 +
            metrics['formatting'] * 0.15 +
            metrics['documentation'] * 0.15
        )
        
        return metrics
    
    def _get_nesting_level(self, node: ast.AST) -> int:
        """Get the nesting level of a node."""
        level = 0
        current = node
        while hasattr(current, 'parent'):
            current = current.parent
            level += 1
        return level
    
    def _calculate_comment_ratio(self, code: str) -> float:
        """Calculate the ratio of comments to code."""
        lines = code.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        return comment_lines / max(1, len(lines))
    
    def _calculate_naming_score(self, tree: ast.AST) -> float:
        """Calculate naming convention score."""
        score = 0.0
        total = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                total += 1
                # Check for snake_case in variables and functions
                if isinstance(node.parent, (ast.FunctionDef, ast.ClassDef)):
                    if re.match(r'^[a-z][a-z0-9_]*$', node.id):
                        score += 1
                # Check for PascalCase in classes
                elif isinstance(node.parent, ast.ClassDef):
                    if re.match(r'^[A-Z][a-zA-Z0-9]*$', node.id):
                        score += 1
        
        return score / max(1, total)
    
    def _calculate_duplication_ratio(self, code: str) -> float:
        """Calculate code duplication ratio."""
        lines = code.splitlines()
        unique_lines = set(lines)
        return 1 - len(unique_lines) / max(1, len(lines)) 