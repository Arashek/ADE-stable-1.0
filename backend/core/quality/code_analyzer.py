from typing import Dict, List, Optional, Any
import ast
from pathlib import Path
import subprocess
import json
from datetime import datetime
from dataclasses import dataclass
from ..monitoring.telemetry import TelemetryManager

@dataclass
class CodeIssue:
    file: str
    line: int
    column: int
    severity: str
    message: str
    rule_id: str
    fix_suggestions: Optional[List[str]] = None

@dataclass
class CodeMetrics:
    complexity: int
    maintainability_index: float
    loc: int
    comment_ratio: float
    test_coverage: float

class CodeAnalyzer:
    def __init__(self, telemetry: TelemetryManager):
        self.telemetry = telemetry
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict[str, Any]:
        """Load code analysis rules from configuration"""
        with open("config/code_rules.json") as f:
            return json.load(f)
            
    async def analyze_file(self, file_path: str) -> List[CodeIssue]:
        """Analyze a single file for code issues"""
        with self.telemetry.create_span(
            "analyze_file",
            {"file": file_path}
        ):
            issues = []
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Parse Python code
                tree = ast.parse(content)
                
                # Analyze AST
                issues.extend(self._analyze_ast(tree, file_path))
                
                # Run static type checking
                issues.extend(await self._run_mypy(file_path))
                
                # Run style checking
                issues.extend(await self._run_flake8(file_path))
                
            except Exception as e:
                self.telemetry.create_span(
                    "analysis_error",
                    {"file": file_path, "error": str(e)}
                )
                
            return issues
            
    def _analyze_ast(self, tree: ast.AST, file_path: str) -> List[CodeIssue]:
        """Analyze Python AST for issues"""
        issues = []
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                
            def visit_FunctionDef(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        
        if complexity_visitor.complexity > self.rules["max_complexity"]:
            issues.append(
                CodeIssue(
                    file=file_path,
                    line=1,
                    column=1,
                    severity="warning",
                    message=f"Function is too complex (complexity: {complexity_visitor.complexity})",
                    rule_id="MAX_COMPLEXITY"
                )
            )
            
        return issues
        
    async def _run_mypy(self, file_path: str) -> List[CodeIssue]:
        """Run mypy for static type checking"""
        try:
            result = subprocess.run(
                ["mypy", file_path],
                capture_output=True,
                text=True
            )
            
            issues = []
            for line in result.stdout.splitlines():
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 4:
                        issues.append(
                            CodeIssue(
                                file=parts[0],
                                line=int(parts[1]),
                                column=1,
                                severity="error" if "error" in parts[3] else "warning",
                                message=parts[3].strip(),
                                rule_id="TYPE_CHECK"
                            )
                        )
                        
            return issues
            
        except Exception as e:
            self.telemetry.create_span(
                "mypy_error",
                {"file": file_path, "error": str(e)}
            )
            return []
            
    async def _run_flake8(self, file_path: str) -> List[CodeIssue]:
        """Run flake8 for style checking"""
        try:
            result = subprocess.run(
                ["flake8", file_path],
                capture_output=True,
                text=True
            )
            
            issues = []
            for line in result.stdout.splitlines():
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 4:
                        issues.append(
                            CodeIssue(
                                file=parts[0],
                                line=int(parts[1]),
                                column=int(parts[2]),
                                severity="warning",
                                message=parts[3].strip(),
                                rule_id="STYLE"
                            )
                        )
                        
            return issues
            
        except Exception as e:
            self.telemetry.create_span(
                "flake8_error",
                {"file": file_path, "error": str(e)}
            )
            return []
            
    async def calculate_metrics(self, file_path: str) -> CodeMetrics:
        """Calculate code metrics for a file"""
        with self.telemetry.create_span(
            "calculate_metrics",
            {"file": file_path}
        ):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                # Calculate metrics
                loc = len(content.splitlines())
                
                # Calculate comment ratio
                comments = 0
                for line in content.splitlines():
                    if line.strip().startswith('#'):
                        comments += 1
                        
                comment_ratio = comments / loc if loc > 0 else 0
                
                # Calculate complexity
                complexity_visitor = ComplexityVisitor()
                complexity_visitor.visit(tree)
                
                # Calculate maintainability index
                # Using a simplified version of the formula
                maintainability = 100 - (complexity_visitor.complexity * 0.5)
                
                # Get test coverage
                coverage = await self._get_test_coverage(file_path)
                
                return CodeMetrics(
                    complexity=complexity_visitor.complexity,
                    maintainability_index=maintainability,
                    loc=loc,
                    comment_ratio=comment_ratio,
                    test_coverage=coverage
                )
                
            except Exception as e:
                self.telemetry.create_span(
                    "metrics_error",
                    {"file": file_path, "error": str(e)}
                )
                return CodeMetrics(0, 0.0, 0, 0.0, 0.0)
                
    async def _get_test_coverage(self, file_path: str) -> float:
        """Get test coverage for a file"""
        try:
            result = subprocess.run(
                ["coverage", "run", "-m", "pytest", file_path],
                capture_output=True,
                text=True
            )
            
            coverage_result = subprocess.run(
                ["coverage", "report"],
                capture_output=True,
                text=True
            )
            
            for line in coverage_result.stdout.splitlines():
                if file_path in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        return float(parts[3].rstrip('%'))
                        
            return 0.0
            
        except Exception as e:
            self.telemetry.create_span(
                "coverage_error",
                {"file": file_path, "error": str(e)}
            )
            return 0.0
