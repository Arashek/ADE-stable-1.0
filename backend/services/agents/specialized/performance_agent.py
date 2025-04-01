from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import ast
import re
import logging
from services.core.base_agent import BaseAgent

@dataclass
class PerformanceIssue:
    severity: str
    description: str
    location: str
    impact: str
    fix_suggestion: str
    estimated_improvement: str

class PerformanceAgent(BaseAgent):
    """Specialized agent for performance analysis and optimization"""
    
    def __init__(self):
        super().__init__("performance_agent")
        self.logger = logging.getLogger(__name__)
        self._load_performance_patterns()

    def _load_performance_patterns(self):
        """Load performance anti-patterns and optimization rules"""
        self.patterns = {
            'n_plus_one': {
                'pattern': r'for.*in.*\.filter\(.*\)',
                'impact': 'HIGH',
                'improvement': '50-90%'
            },
            'inefficient_query': {
                'pattern': r'\.filter\(.*\)\.filter\(.*\)',
                'impact': 'MEDIUM',
                'improvement': '20-40%'
            },
            'memory_leak': {
                'pattern': r'addEventListener\(.*\)',
                'impact': 'HIGH',
                'improvement': '30-60%'
            },
            'unoptimized_images': {
                'pattern': r'<img[^>]+src="[^"]+\.(jpg|png|gif)"[^>]*>',
                'impact': 'MEDIUM',
                'improvement': '40-70%'
            }
        }

    async def analyze_code(self, code: str, filename: str) -> List[PerformanceIssue]:
        """Analyze code for performance issues"""
        issues = []
        
        # Static Analysis
        issues.extend(await self._perform_static_analysis(code, filename))
        
        # Pattern Matching
        issues.extend(await self._check_performance_patterns(code, filename))
        
        # Framework-specific Analysis
        if self._is_frontend_file(filename):
            issues.extend(await self._analyze_frontend_performance(code, filename))
        elif self._is_backend_file(filename):
            issues.extend(await self._analyze_backend_performance(code, filename))
        
        return issues

    async def _perform_static_analysis(self, code: str, filename: str) -> List[PerformanceIssue]:
        """Perform static code analysis for performance issues"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for nested loops
            nested_loops = self._find_nested_loops(tree)
            for loop in nested_loops:
                issues.append(
                    PerformanceIssue(
                        severity="HIGH",
                        description="Nested loop detected - potential O(n²) complexity",
                        location=f"{filename}:{loop[0]}",
                        impact="High CPU usage and response time",
                        fix_suggestion="Consider restructuring using more efficient data structures",
                        estimated_improvement="40-80%"
                    )
                )
            
            # Check for large data structures
            large_structures = self._find_large_data_structures(tree)
            for struct in large_structures:
                issues.append(
                    PerformanceIssue(
                        severity="MEDIUM",
                        description=f"Large data structure initialization: {struct[1]}",
                        location=f"{filename}:{struct[0]}",
                        impact="High memory usage",
                        fix_suggestion="Consider lazy loading or pagination",
                        estimated_improvement="30-50%"
                    )
                )
        
        except SyntaxError:
            self.logger.warning(f"Could not parse {filename} for static analysis")
        
        return issues

    def _find_nested_loops(self, tree: ast.AST) -> List[Tuple[int, str]]:
        """Find nested loops in AST"""
        nested_loops = []
        
        class LoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.loops = []
            
            def visit_For(self, node):
                self.loop_depth += 1
                if self.loop_depth > 1:
                    self.loops.append((node.lineno, 'for'))
                self.generic_visit(node)
                self.loop_depth -= 1
            
            def visit_While(self, node):
                self.loop_depth += 1
                if self.loop_depth > 1:
                    self.loops.append((node.lineno, 'while'))
                self.generic_visit(node)
                self.loop_depth -= 1
        
        visitor = LoopVisitor()
        visitor.visit(tree)
        return visitor.loops

    def _find_large_data_structures(self, tree: ast.AST) -> List[Tuple[int, str]]:
        """Find large data structure initializations"""
        structures = []
        
        class StructureVisitor(ast.NodeVisitor):
            def visit_List(self, node):
                if len(node.elts) > 100:
                    structures.append((node.lineno, 'list'))
            
            def visit_Dict(self, node):
                if len(node.keys) > 100:
                    structures.append((node.lineno, 'dict'))
            
            def visit_Set(self, node):
                if len(node.elts) > 100:
                    structures.append((node.lineno, 'set'))
        
        visitor = StructureVisitor()
        visitor.visit(tree)
        return structures

    async def _check_performance_patterns(self, code: str, filename: str) -> List[PerformanceIssue]:
        """Check code against known performance anti-patterns"""
        issues = []
        
        for pattern_name, pattern_info in self.patterns.items():
            matches = re.finditer(pattern_info['pattern'], code)
            for match in matches:
                line_no = code[:match.start()].count('\n') + 1
                issues.append(
                    PerformanceIssue(
                        severity=pattern_info['impact'],
                        description=f"Performance anti-pattern detected: {pattern_name}",
                        location=f"{filename}:{line_no}",
                        impact=f"Performance impact: {pattern_info['impact']}",
                        fix_suggestion=self._get_fix_suggestion(pattern_name),
                        estimated_improvement=pattern_info['improvement']
                    )
                )
        
        return issues

    async def _analyze_frontend_performance(self, code: str, filename: str) -> List[PerformanceIssue]:
        """Analyze frontend-specific performance issues"""
        issues = []
        
        # Check for unoptimized renders
        if 'React' in code:
            issues.extend(await self._analyze_react_performance(code, filename))
        elif 'Vue' in code:
            issues.extend(await self._analyze_vue_performance(code, filename))
        
        # Check for unoptimized assets
        issues.extend(await self._analyze_asset_performance(code, filename))
        
        return issues

    async def _analyze_backend_performance(self, code: str, filename: str) -> List[PerformanceIssue]:
        """Analyze backend-specific performance issues"""
        issues = []
        
        # Check for database query issues
        if 'django' in code.lower():
            issues.extend(await self._analyze_django_performance(code, filename))
        elif 'sqlalchemy' in code.lower():
            issues.extend(await self._analyze_sqlalchemy_performance(code, filename))
        
        # Check for API endpoint performance
        issues.extend(await self._analyze_api_performance(code, filename))
        
        return issues

    def _is_frontend_file(self, filename: str) -> bool:
        """Check if file is a frontend file"""
        return any(ext in filename.lower() for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue'])

    def _is_backend_file(self, filename: str) -> bool:
        """Check if file is a backend file"""
        return any(ext in filename.lower() for ext in ['.py', '.rb', '.php', '.java'])

    def _get_fix_suggestion(self, pattern_name: str) -> str:
        """Get fix suggestion for performance pattern"""
        suggestions = {
            'n_plus_one': "Use select_related() or prefetch_related() for related queries",
            'inefficient_query': "Combine filters into a single query",
            'memory_leak': "Remove event listeners when component unmounts",
            'unoptimized_images': "Use image optimization and lazy loading"
        }
        return suggestions.get(pattern_name, "Review and optimize code")
