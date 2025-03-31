import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re
from datetime import datetime
import subprocess
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class CodeMetric:
    name: str
    value: float
    unit: str
    description: str
    impact: str

@dataclass
class ImprovementSuggestion:
    category: str
    file_path: str
    line_number: Optional[int]
    description: str
    priority: int
    potential_impact: str
    suggested_changes: List[str]
    estimated_effort: str

class CodeAnalyzer:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.current_dir = self.project_dir / "current"
        self.analysis_dir = self.project_dir / "analysis"
        self.improvements_dir = self.project_dir / "improvements"
        
        # Load project configuration
        with open(self.project_dir / "config.json") as f:
            self.config = json.load(f)
    
    def analyze_codebase(self) -> Dict[str, List[CodeMetric]]:
        """Perform comprehensive code analysis"""
        metrics = {
            "code_quality": [],
            "performance": [],
            "security": [],
            "documentation": []
        }
        
        # Run static analysis tools
        self._run_static_analysis(metrics)
        
        # Analyze code structure
        self._analyze_code_structure(metrics)
        
        # Check documentation
        self._analyze_documentation(metrics)
        
        # Save analysis results
        self._save_analysis_results(metrics)
        
        return metrics
    
    def _run_static_analysis(self, metrics: Dict[str, List[CodeMetric]]):
        """Run static analysis tools"""
        tools = {
            "pylint": ["pylint", "--output-format=json"],
            "flake8": ["flake8", "--format=json"],
            "mypy": ["mypy", "--json"],
            "black": ["black", "--check", "--diff"]
        }
        
        for tool, command in tools.items():
            try:
                result = subprocess.run(
                    command + [str(self.current_dir)],
                    capture_output=True,
                    text=True
                )
                
                if tool == "pylint":
                    self._process_pylint_results(result.stdout, metrics)
                elif tool == "flake8":
                    self._process_flake8_results(result.stdout, metrics)
                elif tool == "mypy":
                    self._process_mypy_results(result.stdout, metrics)
                elif tool == "black":
                    self._process_black_results(result.stdout, metrics)
            
            except subprocess.CalledProcessError as e:
                print(f"Error running {tool}: {e}")
    
    def _process_pylint_results(self, output: str, metrics: Dict[str, List[CodeMetric]]):
        """Process pylint results"""
        try:
            results = json.loads(output)
            for result in results:
                if result["type"] == "convention":
                    metrics["code_quality"].append(
                        CodeMetric(
                            name="pylint_convention",
                            value=float(result["symbol"]),
                            unit="score",
                            description=f"Convention violation: {result['message']}",
                            impact="low"
                        )
                    )
                elif result["type"] == "refactor":
                    metrics["code_quality"].append(
                        CodeMetric(
                            name="pylint_refactor",
                            value=float(result["symbol"]),
                            unit="score",
                            description=f"Refactoring suggestion: {result['message']}",
                            impact="medium"
                        )
                    )
        except json.JSONDecodeError:
            print("Error parsing pylint results")
    
    def _process_flake8_results(self, output: str, metrics: Dict[str, List[CodeMetric]]):
        """Process flake8 results"""
        try:
            results = json.loads(output)
            for result in results:
                metrics["code_quality"].append(
                    CodeMetric(
                        name="flake8_violation",
                        value=float(result["code"]),
                        unit="score",
                        description=f"Style violation: {result['text']}",
                        impact="low"
                    )
                )
        except json.JSONDecodeError:
            print("Error parsing flake8 results")
    
    def _process_mypy_results(self, output: str, metrics: Dict[str, List[CodeMetric]]):
        """Process mypy results"""
        try:
            results = json.loads(output)
            for result in results:
                metrics["code_quality"].append(
                    CodeMetric(
                        name="mypy_error",
                        value=float(result["severity"]),
                        unit="score",
                        description=f"Type error: {result['message']}",
                        impact="high"
                    )
                )
        except json.JSONDecodeError:
            print("Error parsing mypy results")
    
    def _process_black_results(self, output: str, metrics: Dict[str, List[CodeMetric]]):
        """Process black results"""
        if output:
            metrics["code_quality"].append(
                CodeMetric(
                    name="black_formatting",
                    value=1.0,
                    unit="score",
                    description="Code formatting issues detected",
                    impact="low"
                )
            )
    
    def _analyze_code_structure(self, metrics: Dict[str, List[CodeMetric]]):
        """Analyze code structure and complexity"""
        with ThreadPoolExecutor() as executor:
            futures = []
            for file_path in self.current_dir.rglob("*.py"):
                futures.append(
                    executor.submit(self._analyze_file_structure, file_path)
                )
            
            for future in futures:
                file_metrics = future.result()
                for category, metric in file_metrics.items():
                    metrics[category].append(metric)
    
    def _analyze_file_structure(self, file_path: Path) -> Dict[str, CodeMetric]:
        """Analyze structure of a single file"""
        metrics = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Calculate complexity metrics
            complexity = self._calculate_complexity(tree)
            metrics["code_quality"].append(
                CodeMetric(
                    name="cyclomatic_complexity",
                    value=complexity,
                    unit="score",
                    description=f"Cyclomatic complexity for {file_path.name}",
                    impact="medium"
                )
            )
            
            # Analyze function lengths
            avg_function_length = self._calculate_avg_function_length(tree)
            metrics["code_quality"].append(
                CodeMetric(
                    name="avg_function_length",
                    value=avg_function_length,
                    unit="lines",
                    description=f"Average function length in {file_path.name}",
                    impact="low"
                )
            )
            
            # Check for potential performance issues
            performance_issues = self._check_performance_issues(tree)
            if performance_issues:
                metrics["performance"].append(
                    CodeMetric(
                        name="performance_issues",
                        value=len(performance_issues),
                        unit="count",
                        description=f"Potential performance issues in {file_path.name}",
                        impact="high"
                    )
                )
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return metrics
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of an AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.ExceptHandler, ast.BoolOp)):
                complexity += 1
        
        return complexity
    
    def _calculate_avg_function_length(self, tree: ast.AST) -> float:
        """Calculate average function length"""
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if not functions:
            return 0
        
        total_lines = sum(len(func.body) for func in functions)
        return total_lines / len(functions)
    
    def _check_performance_issues(self, tree: ast.AST) -> List[str]:
        """Check for potential performance issues"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for nested loops
            if isinstance(node, (ast.For, ast.While)):
                parent = getattr(node, 'parent', None)
                if isinstance(parent, (ast.For, ast.While)):
                    issues.append("Nested loops detected")
            
            # Check for large list comprehensions
            if isinstance(node, ast.ListComp):
                if len(node.generators) > 2:
                    issues.append("Complex list comprehension")
            
            # Check for string concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
                        if isinstance(child.left, ast.Str) or isinstance(child.right, ast.Str):
                            issues.append("String concatenation in loop")
        
        return issues
    
    def _analyze_documentation(self, metrics: Dict[str, List[CodeMetric]]):
        """Analyze code documentation"""
        for file_path in self.current_dir.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for docstrings
                tree = ast.parse(content)
                has_docstring = any(
                    ast.get_docstring(node) for node in ast.walk(tree)
                    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
                )
                
                if not has_docstring:
                    metrics["documentation"].append(
                        CodeMetric(
                            name="missing_docstring",
                            value=1.0,
                            unit="count",
                            description=f"Missing docstrings in {file_path.name}",
                            impact="medium"
                        )
                    )
                
                # Check for inline comments
                comment_ratio = self._calculate_comment_ratio(content)
                metrics["documentation"].append(
                    CodeMetric(
                        name="comment_ratio",
                        value=comment_ratio,
                        unit="ratio",
                        description=f"Comment to code ratio in {file_path.name}",
                        impact="low"
                    )
                )
            
            except Exception as e:
                print(f"Error analyzing documentation in {file_path}: {e}")
    
    def _calculate_comment_ratio(self, content: str) -> float:
        """Calculate ratio of comments to code lines"""
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        if not code_lines:
            return 0
        
        return len(comment_lines) / len(code_lines)
    
    def _save_analysis_results(self, metrics: Dict[str, List[CodeMetric]]):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for category, category_metrics in metrics.items():
            results = {
                "timestamp": timestamp,
                "metrics": [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "description": metric.description,
                        "impact": metric.impact
                    }
                    for metric in category_metrics
                ]
            }
            
            output_file = self.analysis_dir / category / f"analysis_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
    
    def generate_improvement_suggestions(self) -> List[ImprovementSuggestion]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Load latest analysis results
        for category in ["code_quality", "performance", "security", "documentation"]:
            analysis_files = list((self.analysis_dir / category).glob("analysis_*.json"))
            if not analysis_files:
                continue
            
            latest_analysis = max(analysis_files, key=lambda x: x.stat().st_mtime)
            with open(latest_analysis) as f:
                results = json.load(f)
            
            for metric in results["metrics"]:
                suggestion = self._create_suggestion_from_metric(category, metric)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Save suggestions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suggestions_file = self.improvements_dir / f"suggestions_{timestamp}.json"
        
        with open(suggestions_file, 'w') as f:
            json.dump(
                [vars(suggestion) for suggestion in suggestions],
                f,
                indent=2
            )
        
        return suggestions
    
    def _create_suggestion_from_metric(
        self,
        category: str,
        metric: Dict[str, Any]
    ) -> Optional[ImprovementSuggestion]:
        """Create improvement suggestion from metric"""
        if metric["name"] == "cyclomatic_complexity" and metric["value"] > 10:
            return ImprovementSuggestion(
                category=category,
                file_path="",  # Would need to be determined from analysis
                line_number=None,
                description=f"High cyclomatic complexity ({metric['value']}) detected",
                priority=2,
                potential_impact="Improved code maintainability and testability",
                suggested_changes=[
                    "Break down complex functions into smaller, more focused ones",
                    "Extract repeated logic into helper functions",
                    "Consider using design patterns to simplify control flow"
                ],
                estimated_effort="medium"
            )
        
        elif metric["name"] == "performance_issues":
            return ImprovementSuggestion(
                category=category,
                file_path="",  # Would need to be determined from analysis
                line_number=None,
                description=f"Found {metric['value']} potential performance issues",
                priority=3,
                potential_impact="Improved application performance and resource usage",
                suggested_changes=[
                    "Optimize nested loops",
                    "Use more efficient data structures",
                    "Implement caching where appropriate"
                ],
                estimated_effort="high"
            )
        
        elif metric["name"] == "missing_docstring":
            return ImprovementSuggestion(
                category=category,
                file_path="",  # Would need to be determined from analysis
                line_number=None,
                description="Missing docstrings in code",
                priority=1,
                potential_impact="Improved code documentation and maintainability",
                suggested_changes=[
                    "Add module-level docstrings",
                    "Document classes and methods",
                    "Include type hints and parameter descriptions"
                ],
                estimated_effort="low"
            )
        
        return None

def main():
    """Main entry point for the analyzer"""
    project_dir = os.getenv("ADE_PROJECT_DIR")
    if not project_dir:
        print("Error: ADE_PROJECT_DIR environment variable not set")
        return
    
    analyzer = CodeAnalyzer(project_dir)
    
    print("Starting code analysis...")
    metrics = analyzer.analyze_codebase()
    print("Analysis complete!")
    
    print("\nGenerating improvement suggestions...")
    suggestions = analyzer.generate_improvement_suggestions()
    print(f"Generated {len(suggestions)} improvement suggestions")
    
    print("\nTop priority suggestions:")
    for suggestion in sorted(suggestions, key=lambda x: x.priority, reverse=True)[:5]:
        print(f"- {suggestion.description} (Priority: {suggestion.priority})")

if __name__ == "__main__":
    main() 