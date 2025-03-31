import ast
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CodeMetrics:
    """Container for code quality metrics."""
    complexity: int
    maintainability: float
    lines_of_code: int
    comment_ratio: float
    function_count: int
    avg_function_length: float
    variable_count: int
    nesting_depth: int
    duplication_ratio: float
    naming_score: float
    cyclomatic_complexity: int
    cognitive_complexity: int
    halstead_metrics: Dict[str, float]
    maintainability_index: float

class MetricsAnalyzer:
    """Analyzes code quality metrics for Python code."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def analyze_file(self, file_path: str) -> CodeMetrics:
        """Analyze a single Python file and return its metrics."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Calculate basic metrics
        complexity = self._calculate_complexity(tree)
        maintainability = self._calculate_maintainability(tree)
        lines_of_code = len(content.splitlines())
        comment_ratio = self._calculate_comment_ratio(content)
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        avg_function_length = self._calculate_avg_function_length(tree)
        variable_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Name)])
        nesting_depth = self._calculate_nesting_depth(tree)
        duplication_ratio = self._calculate_duplication_ratio(content)
        naming_score = self._calculate_naming_score(tree)
        
        # Calculate advanced metrics
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        cognitive_complexity = self._calculate_cognitive_complexity(tree)
        halstead_metrics = self._calculate_halstead_metrics(content)
        maintainability_index = self._calculate_maintainability_index(tree)
        
        return CodeMetrics(
            complexity=complexity,
            maintainability=maintainability,
            lines_of_code=lines_of_code,
            comment_ratio=comment_ratio,
            function_count=function_count,
            avg_function_length=avg_function_length,
            variable_count=variable_count,
            nesting_depth=nesting_depth,
            duplication_ratio=duplication_ratio,
            naming_score=naming_score,
            cyclomatic_complexity=cyclomatic_complexity,
            cognitive_complexity=cognitive_complexity,
            halstead_metrics=halstead_metrics,
            maintainability_index=maintainability_index
        )
    
    def analyze_directory(self, directory: str) -> Dict[str, CodeMetrics]:
        """Analyze all Python files in a directory and return their metrics."""
        import os
        from pathlib import Path
        
        metrics = {}
        for file_path in Path(directory).rglob('*.py'):
            try:
                metrics[str(file_path)] = self.analyze_file(str(file_path))
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return metrics
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate code complexity based on control structures."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_maintainability(self, tree: ast.AST) -> float:
        """Calculate maintainability score based on various factors."""
        # Factors that affect maintainability
        complexity_factor = 1.0 / (1 + self._calculate_complexity(tree))
        length_factor = 1.0 / (1 + len(ast.dump(tree)) / 1000)
        nesting_factor = 1.0 / (1 + self._calculate_nesting_depth(tree))
        
        # Weighted average of factors
        return (complexity_factor * 0.4 + length_factor * 0.3 + nesting_factor * 0.3) * 100
    
    def _calculate_comment_ratio(self, content: str) -> float:
        """Calculate the ratio of comments to code lines."""
        lines = content.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        return comment_lines / code_lines if code_lines > 0 else 0
    
    def _calculate_avg_function_length(self, tree: ast.AST) -> float:
        """Calculate average function length in lines."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if not functions:
            return 0
        
        lengths = []
        for func in functions:
            # Get the line numbers from the function definition
            start_line = func.lineno
            end_line = max(node.lineno for node in ast.walk(func))
            lengths.append(end_line - start_line + 1)
        
        return sum(lengths) / len(lengths)
    
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth of control structures."""
        def visit(node: ast.AST, depth: int) -> int:
            max_depth = depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                    max_depth = max(max_depth, visit(child, depth + 1))
                else:
                    max_depth = max(max_depth, visit(child, depth))
            return max_depth
        
        return visit(tree, 0)
    
    def _calculate_duplication_ratio(self, content: str) -> float:
        """Calculate code duplication ratio using string similarity."""
        lines = content.splitlines()
        if not lines:
            return 0
        
        # Group similar lines
        similar_groups = defaultdict(list)
        for i, line in enumerate(lines):
            for group in similar_groups.values():
                if self._similarity_ratio(line, group[0]) > 0.8:
                    group.append(i)
                    break
            else:
                similar_groups[i] = [i]
        
        # Calculate ratio of duplicated lines
        duplicated_lines = sum(len(group) for group in similar_groups.values() if len(group) > 1)
        return duplicated_lines / len(lines)
    
    def _calculate_naming_score(self, tree: ast.AST) -> float:
        """Calculate naming convention compliance score."""
        score = 0
        total = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                total += 1
                if self._is_valid_name(node.id):
                    score += 1
            elif isinstance(node, ast.FunctionDef):
                total += 1
                if self._is_valid_function_name(node.name):
                    score += 1
            elif isinstance(node, ast.ClassDef):
                total += 1
                if self._is_valid_class_name(node.name):
                    score += 1
        
        return (score / total * 100) if total > 0 else 0
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Compare):
                complexity += len(node.ops)
        
        return complexity
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity."""
        complexity = 0
        nesting = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1 + nesting
                nesting += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 2 + nesting
                nesting += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.Compare):
                complexity += len(node.ops)
        
        return complexity
    
    def _calculate_halstead_metrics(self, content: str) -> Dict[str, float]:
        """Calculate Halstead metrics."""
        # Tokenize the code
        tokens = re.findall(r'\b\w+\b|[^\w\s]', content)
        
        # Count operators and operands
        operators = set('+-*/=<>!&|^~%')
        operands = set()
        
        for token in tokens:
            if token in operators:
                self.metrics['operators'].append(token)
            elif token.isidentifier():
                operands.add(token)
                self.metrics['operands'].append(token)
        
        n1 = len(set(self.metrics['operators']))  # Unique operators
        n2 = len(operands)  # Unique operands
        N1 = len(self.metrics['operators'])  # Total operators
        N2 = len(self.metrics['operands'])  # Total operands
        
        # Calculate Halstead metrics
        program_length = N1 + N2
        vocabulary = n1 + n2
        volume = program_length * (math.log2(vocabulary) if vocabulary > 0 else 0)
        difficulty = (n1 * N2) / (2 * n2) if n2 > 0 else 0
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
    
    def _calculate_maintainability_index(self, tree: ast.AST) -> float:
        """Calculate maintainability index."""
        halstead_metrics = self._calculate_halstead_metrics(ast.unparse(tree))
        complexity = self._calculate_complexity(tree)
        lines = len(ast.unparse(tree).splitlines())
        
        # Calculate maintainability index using the formula
        mi = 171 - 5.2 * math.log(halstead_metrics['volume']) - 0.23 * complexity - 16.2 * math.log(lines)
        return max(0, min(100, mi))  # Clamp between 0 and 100
    
    def _similarity_ratio(self, s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if a variable name follows Python naming conventions."""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))
    
    def _is_valid_function_name(self, name: str) -> bool:
        """Check if a function name follows Python naming conventions."""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))
    
    def _is_valid_class_name(self, name: str) -> bool:
        """Check if a class name follows Python naming conventions."""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))

def main():
    """Main function to analyze code metrics."""
    import argparse
    import json
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description='Analyze code quality metrics')
    parser.add_argument('path', help='Path to Python file or directory')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    args = parser.parse_args()
    
    analyzer = MetricsAnalyzer()
    path = Path(args.path)
    
    if path.is_file():
        metrics = analyzer.analyze_file(str(path))
    else:
        metrics = analyzer.analyze_directory(str(path))
    
    # Convert metrics to JSON-serializable format
    if isinstance(metrics, CodeMetrics):
        metrics_dict = {
            'complexity': metrics.complexity,
            'maintainability': metrics.maintainability,
            'lines_of_code': metrics.lines_of_code,
            'comment_ratio': metrics.comment_ratio,
            'function_count': metrics.function_count,
            'avg_function_length': metrics.avg_function_length,
            'variable_count': metrics.variable_count,
            'nesting_depth': metrics.nesting_depth,
            'duplication_ratio': metrics.duplication_ratio,
            'naming_score': metrics.naming_score,
            'cyclomatic_complexity': metrics.cyclomatic_complexity,
            'cognitive_complexity': metrics.cognitive_complexity,
            'halstead_metrics': metrics.halstead_metrics,
            'maintainability_index': metrics.maintainability_index
        }
    else:
        metrics_dict = {
            str(k): {
                'complexity': v.complexity,
                'maintainability': v.maintainability,
                'lines_of_code': v.lines_of_code,
                'comment_ratio': v.comment_ratio,
                'function_count': v.function_count,
                'avg_function_length': v.avg_function_length,
                'variable_count': v.variable_count,
                'nesting_depth': v.nesting_depth,
                'duplication_ratio': v.duplication_ratio,
                'naming_score': v.naming_score,
                'cyclomatic_complexity': v.cyclomatic_complexity,
                'cognitive_complexity': v.cognitive_complexity,
                'halstead_metrics': v.halstead_metrics,
                'maintainability_index': v.maintainability_index
            }
            for k, v in metrics.items()
        }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
    else:
        print(json.dumps(metrics_dict, indent=2))

if __name__ == '__main__':
    main() 