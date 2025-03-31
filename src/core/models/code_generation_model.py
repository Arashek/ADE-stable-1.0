from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .model_router import ModelRouter
import ast
import black
import isort
import pylint.lint
from io import StringIO
import re

class CodeQualityMetrics(BaseModel):
    """Metrics for code quality assessment"""
    complexity: float
    maintainability: float
    testability: float
    security: float
    performance: float
    readability: float
    documentation: float
    pylint_score: float
    black_compliance: float
    isort_compliance: float

class CodeGenerationResult(BaseModel):
    """Result of code generation"""
    code: str
    quality_metrics: CodeQualityMetrics
    dependencies: List[str]
    test_cases: List[str]
    documentation: str
    metadata: Dict[str, Any] = {}

class CodeGenerationModel:
    """Specialized model for optimized code generation"""
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        self.generation_metrics: Dict[str, Dict[str, float]] = {}
        self.code_templates: Dict[str, str] = {}
        self.optimization_rules: Dict[str, List[str]] = {}
        
    async def generate_code(
        self,
        requirements: str,
        language: str,
        framework: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CodeGenerationResult:
        """Generate optimized code based on requirements"""
        # Get appropriate model for code generation
        model = await self.model_router.get_model_for_capability("code_generation")
        
        # Generate initial code
        initial_code = await self._generate_initial_code(model, requirements, language, framework, context)
        
        # Optimize code
        optimized_code = await self._optimize_code(initial_code, language)
        
        # Generate tests
        test_cases = await self._generate_tests(optimized_code, requirements)
        
        # Generate documentation
        documentation = await self._generate_documentation(optimized_code, requirements)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(optimized_code)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(optimized_code, language)
        
        # Create result
        result = CodeGenerationResult(
            code=optimized_code,
            quality_metrics=quality_metrics,
            dependencies=dependencies,
            test_cases=test_cases,
            documentation=documentation,
            metadata={
                "language": language,
                "framework": framework,
                "generated_at": datetime.now().isoformat()
            }
        )
        
        # Update generation metrics
        self._update_generation_metrics(result)
        
        return result
        
    async def _generate_initial_code(
        self,
        model: Any,
        requirements: str,
        language: str,
        framework: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate initial code using the model"""
        prompt = f"""Generate high-quality code in {language} based on the following requirements.
        Consider best practices, design patterns, and optimization techniques.

        Requirements: {requirements}

        Additional Context:
        - Language: {language}
        - Framework: {framework or 'None'}
        - Best Practices: Follow SOLID principles, DRY, and KISS
        - Performance: Optimize for speed and memory usage
        - Security: Follow security best practices
        - Maintainability: Write clean, well-documented code
        - Testability: Make code easy to test

        Generate code that is:
        1. Efficient and performant
        2. Secure and robust
        3. Well-documented
        4. Easy to maintain
        5. Easy to test
        6. Following language-specific best practices
        """
        
        response = await model.generate_code(prompt, context)
        return response
        
    async def _optimize_code(self, code: str, language: str) -> str:
        """Optimize generated code"""
        # Apply language-specific optimizations
        if language == "python":
            code = await self._optimize_python_code(code)
        elif language == "javascript":
            code = await self._optimize_javascript_code(code)
        elif language == "java":
            code = await self._optimize_java_code(code)
            
        return code
        
    async def _optimize_python_code(self, code: str) -> str:
        """Optimize Python code"""
        # Format code with black
        try:
            code = black.format_str(code, mode=black.FileMode())
        except Exception:
            pass
            
        # Sort imports with isort
        try:
            code = isort.code(code)
        except Exception:
            pass
            
        # Apply AST-based optimizations
        try:
            tree = ast.parse(code)
            optimized_tree = self._optimize_ast(tree)
            code = ast.unparse(optimized_tree)
        except Exception:
            pass
            
        return code
        
    def _optimize_ast(self, tree: ast.AST) -> ast.AST:
        """Optimize Python AST"""
        # Remove unused imports
        tree = self._remove_unused_imports(tree)
        
        # Optimize loops
        tree = self._optimize_loops(tree)
        
        # Optimize function calls
        tree = self._optimize_function_calls(tree)
        
        return tree
        
    def _remove_unused_imports(self, tree: ast.AST) -> ast.AST:
        """Remove unused imports from AST"""
        # Track used names
        used_names = set()
        
        class NameCollector(ast.NodeVisitor):
            def visit_Name(self, node):
                used_names.add(node.id)
                
        collector = NameCollector()
        collector.visit(tree)
        
        # Remove unused imports
        class ImportCleaner(ast.NodeTransformer):
            def visit_Import(self, node):
                names = [alias.name for alias in node.names]
                if not any(name in used_names for name in names):
                    return None
                return node
                
            def visit_ImportFrom(self, node):
                names = [alias.name for alias in node.names]
                if not any(name in used_names for name in names):
                    return None
                return node
                
        cleaner = ImportCleaner()
        return cleaner.visit(tree)
        
    def _optimize_loops(self, tree: ast.AST) -> ast.AST:
        """Optimize loops in AST"""
        class LoopOptimizer(ast.NodeTransformer):
            def visit_For(self, node):
                # Convert for loops to list comprehensions where possible
                if isinstance(node.body, list) and len(node.body) == 1:
                    if isinstance(node.body[0], ast.Assign):
                        return self._convert_to_list_comprehension(node)
                return node
                
            def _convert_to_list_comprehension(self, node):
                # Implementation of loop to list comprehension conversion
                pass
                
        optimizer = LoopOptimizer()
        return optimizer.visit(tree)
        
    def _optimize_function_calls(self, tree: ast.AST) -> ast.AST:
        """Optimize function calls in AST"""
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
        
    async def _generate_tests(self, code: str, requirements: str) -> List[str]:
        """Generate test cases for the code"""
        prompt = f"""Generate comprehensive test cases for the following code based on the requirements.

        Code:
        {code}

        Requirements: {requirements}

        Generate test cases that cover:
        1. Happy path scenarios
        2. Edge cases
        3. Error cases
        4. Performance tests
        5. Security tests
        """
        
        response = await self.model_router.route_task({
            "task_type": "test_generation",
            "content": prompt
        })
        
        # Parse test cases from response
        test_cases = []
        current_test = []
        
        for line in response.content.split('\n'):
            line = line.strip()
            if not line:
                if current_test:
                    test_cases.append('\n'.join(current_test))
                    current_test = []
                continue
                
            if line.startswith('def test_'):
                if current_test:
                    test_cases.append('\n'.join(current_test))
                current_test = [line]
            else:
                current_test.append(line)
                
        if current_test:
            test_cases.append('\n'.join(current_test))
            
        return test_cases
        
    async def _generate_documentation(self, code: str, requirements: str) -> str:
        """Generate documentation for the code"""
        prompt = f"""Generate comprehensive documentation for the following code based on the requirements.

        Code:
        {code}

        Requirements: {requirements}

        Generate documentation that includes:
        1. Overview and purpose
        2. Installation and setup
        3. Usage examples
        4. API reference
        5. Performance considerations
        6. Security considerations
        7. Contributing guidelines
        """
        
        response = await self.model_router.route_task({
            "task_type": "documentation",
            "content": prompt
        })
        
        return response.content
        
    def _calculate_quality_metrics(self, code: str) -> CodeQualityMetrics:
        """Calculate code quality metrics"""
        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(code)
        
        # Calculate maintainability index
        maintainability = self._calculate_maintainability(code)
        
        # Calculate testability score
        testability = self._calculate_testability(code)
        
        # Calculate security score
        security = self._calculate_security(code)
        
        # Calculate performance score
        performance = self._calculate_performance(code)
        
        # Calculate readability score
        readability = self._calculate_readability(code)
        
        # Calculate documentation score
        documentation = self._calculate_documentation(code)
        
        # Run pylint
        pylint_score = self._run_pylint(code)
        
        # Check black compliance
        black_compliance = self._check_black_compliance(code)
        
        # Check isort compliance
        isort_compliance = self._check_isort_compliance(code)
        
        return CodeQualityMetrics(
            complexity=complexity,
            maintainability=maintainability,
            testability=testability,
            security=security,
            performance=performance,
            readability=readability,
            documentation=documentation,
            pylint_score=pylint_score,
            black_compliance=black_compliance,
            isort_compliance=isort_compliance
        )
        
    def _calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity"""
        try:
            tree = ast.parse(code)
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
            
            return 1 / (complexity + 1)  # Normalize to 0-1 range
        except Exception:
            return 0.5
            
    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index"""
        try:
            # Count lines of code
            loc = len(code.splitlines())
            
            # Count comments
            comments = len(re.findall(r'#.*$', code, re.MULTILINE))
            
            # Count functions
            functions = len(re.findall(r'def\s+\w+', code))
            
            # Calculate maintainability score
            score = (comments / (loc + 1)) * (1 / (functions + 1))
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _calculate_testability(self, code: str) -> float:
        """Calculate testability score"""
        try:
            # Count dependencies
            dependencies = len(self._extract_dependencies(code, "python"))
            
            # Count side effects
            side_effects = len(re.findall(r'global\s+\w+|nonlocal\s+\w+', code))
            
            # Calculate testability score
            score = 1 / (dependencies + side_effects + 1)
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _calculate_security(self, code: str) -> float:
        """Calculate security score"""
        try:
            # Check for common security issues
            security_issues = 0
            
            # Check for hardcoded secrets
            security_issues += len(re.findall(r'password\s*=\s*[\'"][^\'"]+[\'"]', code))
            
            # Check for SQL injection vulnerabilities
            security_issues += len(re.findall(r'\+.*?\+.*?sql', code))
            
            # Check for command injection vulnerabilities
            security_issues += len(re.findall(r'os\.system|subprocess\.call', code))
            
            # Calculate security score
            score = 1 / (security_issues + 1)
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _calculate_performance(self, code: str) -> float:
        """Calculate performance score"""
        try:
            # Check for performance issues
            performance_issues = 0
            
            # Check for nested loops
            performance_issues += len(re.findall(r'for.*?for', code))
            
            # Check for large data structures
            performance_issues += len(re.findall(r'\[.*?\]', code))
            
            # Check for expensive operations
            performance_issues += len(re.findall(r'sort\(|sorted\(', code))
            
            # Calculate performance score
            score = 1 / (performance_issues + 1)
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _calculate_readability(self, code: str) -> float:
        """Calculate readability score"""
        try:
            # Check line length
            long_lines = len([line for line in code.splitlines() if len(line) > 80])
            
            # Check function length
            functions = re.findall(r'def\s+\w+.*?:\n(.*?)(?=def|\Z)', code, re.DOTALL)
            long_functions = len([f for f in functions if len(f.splitlines()) > 20])
            
            # Calculate readability score
            score = 1 / (long_lines + long_functions + 1)
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _calculate_documentation(self, code: str) -> float:
        """Calculate documentation score"""
        try:
            # Count docstrings
            docstrings = len(re.findall(r'""".*?"""', code, re.DOTALL))
            
            # Count comments
            comments = len(re.findall(r'#.*$', code, re.MULTILINE))
            
            # Count functions
            functions = len(re.findall(r'def\s+\w+', code))
            
            # Calculate documentation score
            score = (docstrings + comments) / (functions + 1)
            return min(score, 1.0)
        except Exception:
            return 0.5
            
    def _run_pylint(self, code: str) -> float:
        """Run pylint on the code"""
        try:
            # Capture pylint output
            output = StringIO()
            pylint.lint.Run(['-'], reporter=pylint.reporters.TextReporter(output), do_exit=False)
            
            # Extract score from output
            match = re.search(r'Your code has been rated at (-?\d+\.\d+)/10', output.getvalue())
            if match:
                return float(match.group(1)) / 10
            return 0.5
        except Exception:
            return 0.5
            
    def _check_black_compliance(self, code: str) -> float:
        """Check black formatting compliance"""
        try:
            formatted_code = black.format_str(code, mode=black.FileMode())
            return 1.0 if formatted_code == code else 0.5
        except Exception:
            return 0.5
            
    def _check_isort_compliance(self, code: str) -> float:
        """Check isort import sorting compliance"""
        try:
            sorted_code = isort.code(code)
            return 1.0 if sorted_code == code else 0.5
        except Exception:
            return 0.5
            
    def _extract_dependencies(self, code: str, language: str) -> List[str]:
        """Extract dependencies from code"""
        dependencies = []
        
        if language == "python":
            # Extract import statements
            imports = re.findall(r'import\s+(\w+)|from\s+(\w+)\s+import', code)
            dependencies.extend([imp[0] or imp[1] for imp in imports])
            
        elif language == "javascript":
            # Extract require statements
            requires = re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', code)
            dependencies.extend(requires)
            
        elif language == "java":
            # Extract import statements
            imports = re.findall(r'import\s+([\w.]+);', code)
            dependencies.extend(imports)
            
        return list(set(dependencies))
        
    def _update_generation_metrics(self, result: CodeGenerationResult):
        """Update code generation metrics"""
        metrics = result.quality_metrics
        
        if "code_generation" not in self.generation_metrics:
            self.generation_metrics["code_generation"] = {
                "avg_complexity": 0.0,
                "avg_maintainability": 0.0,
                "avg_testability": 0.0,
                "avg_security": 0.0,
                "avg_performance": 0.0,
                "avg_readability": 0.0,
                "avg_documentation": 0.0,
                "avg_pylint_score": 0.0,
                "avg_black_compliance": 0.0,
                "avg_isort_compliance": 0.0
            }
            
        gen_metrics = self.generation_metrics["code_generation"]
        
        # Update metrics with exponential moving average
        gen_metrics["avg_complexity"] = 0.9 * gen_metrics["avg_complexity"] + 0.1 * metrics.complexity
        gen_metrics["avg_maintainability"] = 0.9 * gen_metrics["avg_maintainability"] + 0.1 * metrics.maintainability
        gen_metrics["avg_testability"] = 0.9 * gen_metrics["avg_testability"] + 0.1 * metrics.testability
        gen_metrics["avg_security"] = 0.9 * gen_metrics["avg_security"] + 0.1 * metrics.security
        gen_metrics["avg_performance"] = 0.9 * gen_metrics["avg_performance"] + 0.1 * metrics.performance
        gen_metrics["avg_readability"] = 0.9 * gen_metrics["avg_readability"] + 0.1 * metrics.readability
        gen_metrics["avg_documentation"] = 0.9 * gen_metrics["avg_documentation"] + 0.1 * metrics.documentation
        gen_metrics["avg_pylint_score"] = 0.9 * gen_metrics["avg_pylint_score"] + 0.1 * metrics.pylint_score
        gen_metrics["avg_black_compliance"] = 0.9 * gen_metrics["avg_black_compliance"] + 0.1 * metrics.black_compliance
        gen_metrics["avg_isort_compliance"] = 0.9 * gen_metrics["avg_isort_compliance"] + 0.1 * metrics.isort_compliance
        
    def get_generation_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get code generation metrics"""
        return self.generation_metrics 