from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import ast
import libcst as cst
from libcst.metadata import MetadataWrapper
import radon.complexity as radon
from pylint import epylint as lint

logger = logging.getLogger(__name__)

class ContextAwareFixSystem:
    """System for applying context-aware code fixes"""
    
    def __init__(self):
        self.fix_history: Dict[str, List[Dict[str, Any]]] = {}
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_context(self, file_path: str) -> Dict[str, Any]:
        """Analyze code context for a file"""
        if file_path in self.context_cache:
            return self.context_cache[file_path]
            
        try:
            code = Path(file_path).read_text()
            
            # Parse code
            tree = ast.parse(code)
            cst_tree = cst.parse_module(code)
            wrapper = MetadataWrapper(cst_tree)
            
            # Analyze code structure
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            
            # Calculate metrics
            complexity = radon.cc_visit(code)
            maintainability = radon.mi_visit(code, multi=True)
            
            # Run static analysis
            pylint_stdout, pylint_stderr = lint.py_run(
                f'"{file_path}"',
                return_std=True
            )
            lint_issues = self._parse_lint_output(pylint_stdout.getvalue())
            
            context = {
                'imports': imports,
                'functions': functions,
                'classes': classes,
                'metrics': {
                    'complexity': complexity,
                    'maintainability': maintainability
                },
                'static_analysis': lint_issues,
                'dependencies': self._extract_dependencies(imports)
            }
            
            self.context_cache[file_path] = context
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing context for {file_path}: {str(e)}")
            return {}
            
    async def generate_review(
        self,
        file_path: str,
        context: Dict[str, Any],
        review_type: str = 'full'
    ) -> Dict[str, Any]:
        """Generate a code review with context awareness"""
        code = Path(file_path).read_text()
        
        # Determine review scope
        if review_type == 'quick':
            analyzers = ['syntax', 'style', 'complexity']
        elif review_type == 'security':
            analyzers = ['security', 'input_validation', 'error_handling']
        else:  # full review
            analyzers = ['syntax', 'style', 'complexity', 'security',
                        'maintainability', 'performance']
            
        issues = []
        for analyzer in analyzers:
            analyzer_issues = await self._run_analyzer(
                analyzer,
                code,
                context
            )
            issues.extend(analyzer_issues)
            
        return {
            'file_path': file_path,
            'issues': issues,
            'code': code,
            'review_type': review_type,
            'context_used': context
        }
        
    async def apply_fix(
        self,
        code: str,
        issues: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Apply context-aware fixes to code"""
        if not issues:
            return code
            
        # Sort issues by priority
        issues = sorted(
            issues,
            key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[
                x.get('severity', 'low')
            ]
        )
        
        fixed_code = code
        for issue in issues:
            try:
                if issue['type'] == 'style':
                    fixed_code = await self._apply_style_fix(fixed_code, issue, context)
                elif issue['type'] == 'security':
                    fixed_code = await self._apply_security_fix(fixed_code, issue, context)
                elif issue['type'] == 'performance':
                    fixed_code = await self._apply_performance_fix(fixed_code, issue, context)
                elif issue['type'] == 'maintainability':
                    fixed_code = await self._apply_maintainability_fix(fixed_code, issue, context)
                    
            except Exception as e:
                logger.error(f"Error applying fix for issue {issue['id']}: {str(e)}")
                continue
                
        return fixed_code
        
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import information from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'type': 'import',
                        'name': name.name,
                        'asname': name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    'type': 'importfrom',
                    'module': node.module,
                    'names': [n.name for n in node.names]
                })
        return imports
        
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function information from AST"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': [a.arg for a in node.args.args],
                    'decorators': [d.id for d in node.decorator_list
                                 if isinstance(d, ast.Name)],
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                })
        return functions
        
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class information from AST"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'bases': [b.id for b in node.bases if isinstance(b, ast.Name)],
                    'methods': [m.name for m in node.body
                              if isinstance(m, ast.FunctionDef)]
                })
        return classes
        
    def _extract_dependencies(self, imports: List[Dict[str, Any]]) -> List[str]:
        """Extract external dependencies from imports"""
        deps = set()
        for imp in imports:
            if imp['type'] == 'import':
                deps.add(imp['name'].split('.')[0])
            elif imp['type'] == 'importfrom' and imp['module']:
                deps.add(imp['module'].split('.')[0])
        return list(deps)
        
    def _parse_lint_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse pylint output into structured issues"""
        issues = []
        for line in output.split('\n'):
            if ':' not in line:
                continue
            try:
                parts = line.split(':')
                issues.append({
                    'line': int(parts[1]),
                    'column': int(parts[2]),
                    'type': parts[3].strip(),
                    'message': parts[4].strip(),
                    'symbol': parts[5].strip() if len(parts) > 5 else None
                })
            except (ValueError, IndexError):
                continue
        return issues
        
    async def _run_analyzer(
        self,
        analyzer: str,
        code: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run a specific code analyzer"""
        # Implement different analyzers
        if analyzer == 'syntax':
            return self._analyze_syntax(code)
        elif analyzer == 'style':
            return self._analyze_style(code)
        elif analyzer == 'complexity':
            return self._analyze_complexity(code)
        elif analyzer == 'security':
            return self._analyze_security(code, context)
        elif analyzer == 'maintainability':
            return self._analyze_maintainability(code, context)
        elif analyzer == 'performance':
            return self._analyze_performance(code, context)
        return []
        
    def _analyze_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code syntax"""
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'id': 'syntax_error',
                'type': 'syntax',
                'severity': 'critical',
                'message': str(e),
                'line': e.lineno,
                'offset': e.offset
            })
        return issues
        
    def _analyze_style(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code style"""
        # Use pylint for style checking
        issues = []
        pylint_stdout, _ = lint.py_run(code, return_std=True)
        return self._parse_lint_output(pylint_stdout.getvalue())
        
    def _analyze_complexity(self, code: str) -> List[Dict[str, Any]]:
        """Analyze code complexity"""
        issues = []
        try:
            complexity = radon.cc_visit(code)
            for item in complexity:
                if item.complexity > 10:
                    issues.append({
                        'id': f'high_complexity_{item.name}',
                        'type': 'complexity',
                        'severity': 'high',
                        'message': f'Function {item.name} has high complexity ({item.complexity})',
                        'line': item.lineno
                    })
        except Exception as e:
            logger.error(f"Error analyzing complexity: {str(e)}")
        return issues
        
    def _analyze_security(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze code security"""
        issues = []
        
        # Check for common security issues
        if 'eval(' in code or 'exec(' in code:
            issues.append({
                'id': 'security_eval_exec',
                'type': 'security',
                'severity': 'critical',
                'message': 'Use of eval() or exec() is dangerous'
            })
            
        # Check SQL injection vulnerabilities
        if 'execute' in code and 'sql' in code.lower():
            if '%s' in code or '+' in code:
                issues.append({
                    'id': 'security_sql_injection',
                    'type': 'security',
                    'severity': 'critical',
                    'message': 'Possible SQL injection vulnerability'
                })
                
        return issues
        
    def _analyze_maintainability(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze code maintainability"""
        issues = []
        
        # Check function length
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    issues.append({
                        'id': f'long_function_{node.name}',
                        'type': 'maintainability',
                        'severity': 'medium',
                        'message': f'Function {node.name} is too long',
                        'line': node.lineno
                    })
                    
        return issues
        
    def _analyze_performance(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze code performance"""
        issues = []
        
        # Check for inefficient list operations
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range' and len(node.iter.args) == 1:
                            issues.append({
                                'id': 'performance_range',
                                'type': 'performance',
                                'severity': 'medium',
                                'message': 'Consider using xrange for large iterations',
                                'line': node.lineno
                            })
                            
        return issues
        
    async def _apply_style_fix(
        self,
        code: str,
        issue: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Apply style fixes"""
        # Implement style fixes
        return code
        
    async def _apply_security_fix(
        self,
        code: str,
        issue: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Apply security fixes"""
        # Implement security fixes
        return code
        
    async def _apply_performance_fix(
        self,
        code: str,
        issue: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Apply performance fixes"""
        # Implement performance fixes
        return code
        
    async def _apply_maintainability_fix(
        self,
        code: str,
        issue: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Apply maintainability fixes"""
        # Implement maintainability fixes
        return code
