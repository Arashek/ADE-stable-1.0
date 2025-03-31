from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import os
import json
import yaml
from pathlib import Path
import ast
from jinja2 import Environment, FileSystemLoader
import re
from concurrent.futures import ThreadPoolExecutor

from ..llm_integration import LLMIntegration, LLMConfig
from ..code_context_manager import CodeContextManager
from .template_manager import TemplateManager
from .pattern_analyzer import PatternAnalyzer
from .context_aware_suggester import ContextAwareSuggester
from .code_quality_analyzer import CodeQualityAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class GenerationContext:
    """Context for code generation"""
    language: str
    framework: Optional[str] = None
    project_type: Optional[str] = None
    architecture: Optional[str] = None
    style: Optional[str] = None
    dependencies: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    constraints: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class GenerationResult:
    """Result of code generation"""
    code: str
    documentation: str
    quality_score: float
    suggestions: List[str]
    patterns_used: List[str]
    metadata: Dict[str, Any]
    generation_time: datetime

@dataclass
class CodeQualityMetrics:
    """Metrics for code quality analysis"""
    complexity: float
    maintainability: float
    security_score: float
    performance_score: float
    test_coverage: float
    documentation_score: float

class EnhancedCodeGenerator:
    """Enhanced code generation system with advanced capabilities"""
    
    def __init__(
        self,
        llm_config: LLMConfig,
        templates_dir: str = "templates",
        patterns_dir: str = "patterns",
        cache_dir: str = "cache"
    ):
        self.llm = LLMIntegration(llm_config)
        self.context_manager = CodeContextManager()
        self.template_manager = TemplateManager(templates_dir)
        self.pattern_analyzer = PatternAnalyzer(patterns_dir)
        self.context_aware_suggester = ContextAwareSuggester()
        self.code_quality_analyzer = CodeQualityAnalyzer()
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template environment
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Supported languages and frameworks
        self.supported_languages = {
            "frontend": ["javascript", "typescript", "html", "css", "react", "vue", "angular"],
            "backend": ["python", "java", "csharp", "go", "nodejs", "php"],
            "mobile": ["swift", "kotlin", "react-native", "flutter"],
            "data": ["sql", "nosql", "graphql", "rest"]
        }
        
        # Initialize thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    async def generate_code(
        self,
        requirements: str,
        context: GenerationContext,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate code based on requirements and context"""
        try:
            # Validate language support
            if not self._is_language_supported(context.language):
                raise ValueError(f"Unsupported language: {context.language}")
            
            # Analyze requirements and context
            analysis = await self._analyze_requirements(requirements, context)
            
            # Generate code using multiple approaches
            solutions = await self._generate_solutions(requirements, context, analysis)
            
            # Select best solution
            best_solution = await self._select_best_solution(solutions)
            
            # Apply code quality improvements
            improved_code = await self._improve_code_quality(best_solution["code"], context)
            
            # Generate documentation
            documentation = await self._generate_documentation(improved_code, context)
            
            return {
                "code": improved_code,
                "documentation": documentation,
                "quality_metrics": best_solution["quality_metrics"],
                "generation_time": datetime.now(),
                "context": context,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
            
    def _is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        for category in self.supported_languages.values():
            if language.lower() in category:
                return True
        return False
        
    async def _analyze_requirements(
        self,
        requirements: str,
        context: GenerationContext
    ) -> Dict[str, Any]:
        """Analyze requirements and context"""
        # Use LLM to analyze requirements
        analysis_prompt = f"""
        Analyze the following requirements and context:
        
        Requirements: {requirements}
        Language: {context.language}
        Framework: {context.framework}
        Project Type: {context.project_type}
        Architecture: {context.architecture}
        
        Generate a detailed analysis focusing on:
        1. Required components and their relationships
        2. Design patterns to apply
        3. Security considerations
        4. Performance requirements
        5. Testing requirements
        """
        
        analysis = await self.llm.generate(analysis_prompt)
        return json.loads(analysis)
        
    async def _generate_solutions(
        self,
        requirements: str,
        context: GenerationContext,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate solutions using multiple approaches"""
        solutions = []
        
        # Generate template-based solution
        template_solution = await self._generate_template_solution(
            requirements, context, analysis
        )
        solutions.append(template_solution)
        
        # Generate pattern-based solution
        pattern_solution = await self._generate_pattern_solution(
            requirements, context, analysis
        )
        solutions.append(pattern_solution)
        
        # Generate AI-based solution
        ai_solution = await self._generate_ai_solution(
            requirements, context, analysis
        )
        solutions.append(ai_solution)
        
        return solutions
        
    async def _select_best_solution(
        self,
        solutions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Select the best solution based on quality metrics"""
        best_solution = max(
            solutions,
            key=lambda x: x["quality_metrics"].maintainability
        )
        return best_solution
        
    async def _improve_code_quality(
        self,
        code: str,
        context: GenerationContext
    ) -> str:
        """Apply code quality improvements"""
        # Analyze code quality
        quality_metrics = await self.code_quality_analyzer.analyze(code, context)
        
        # Generate improvements
        improvements = await self._generate_improvements(code, quality_metrics, context)
        
        # Apply improvements
        improved_code = await self._apply_improvements(code, improvements)
        
        return improved_code
        
    async def _generate_documentation(
        self,
        code: str,
        context: GenerationContext
    ) -> str:
        """Generate documentation for the code"""
        # Analyze code structure
        structure = await self._analyze_code_structure(code)
        
        # Generate documentation
        doc_prompt = f"""
        Generate comprehensive documentation for the following code:
        
        Code: {code}
        Language: {context.language}
        Framework: {context.framework}
        Structure: {json.dumps(structure)}
        
        Include:
        1. Overview
        2. Components
        3. Usage examples
        4. API documentation
        5. Best practices
        """
        
        documentation = await self.llm.generate(doc_prompt)
        return documentation
        
    async def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyze code structure"""
        try:
            tree = ast.parse(code)
            return self._extract_structure(tree)
        except:
            # Fallback to regex-based analysis for non-Python code
            return self._extract_structure_regex(code)
            
    def _extract_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract structure from AST"""
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure["classes"].append({
                    "name": node.name,
                    "bases": [base.id for base in node.bases],
                    "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                })
            elif isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "returns": self._get_return_type(node)
                })
            elif isinstance(node, ast.Import):
                structure["imports"].extend(alias.name for alias in node.names)
            elif isinstance(node, ast.Assign):
                structure["variables"].extend(target.id for target in node.targets)
                
        return structure
        
    def _extract_structure_regex(self, code: str) -> Dict[str, Any]:
        """Extract structure using regex for non-Python code"""
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "variables": []
        }
        
        # Extract classes
        class_pattern = r"class\s+(\w+)(?:\s*\([^)]*\))?:"
        structure["classes"] = re.findall(class_pattern, code)
        
        # Extract functions
        function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        structure["functions"] = re.findall(function_pattern, code)
        
        # Extract imports
        import_pattern = r"import\s+(\w+(?:\.\w+)*)"
        structure["imports"] = re.findall(import_pattern, code)
        
        # Extract variables
        variable_pattern = r"(\w+)\s*=\s*[^=]"
        structure["variables"] = re.findall(variable_pattern, code)
        
        return structure
        
    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Get function return type annotation"""
        if node.returns:
            return ast.unparse(node.returns)
        return None
        
    async def _generate_template_solution(
        self,
        requirements: str,
        context: GenerationContext,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate template-based solution"""
        # Select appropriate template
        template = await self.template_manager.select_template(
            requirements,
            analysis,
            context
        )
        
        # Generate code using template
        code = await self.template_manager.generate_code(
            template,
            {
                "requirements": requirements,
                "analysis": analysis,
                "context": context
            }
        )
        
        # Apply patterns
        code = await self.pattern_analyzer.apply_patterns(
            code,
            analysis["patterns"],
            context
        )
        
        # Analyze code quality
        quality_metrics = await self.code_quality_analyzer.analyze_code(code)
        
        return {
            "code": code,
            "quality_metrics": quality_metrics
        }
        
    async def _generate_pattern_solution(
        self,
        requirements: str,
        context: GenerationContext,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate pattern-based solution"""
        # Generate code using patterns
        code = await self.pattern_analyzer.generate_code(
            requirements,
            context
        )
        
        # Analyze code quality
        quality_metrics = await self.code_quality_analyzer.analyze_code(code)
        
        return {
            "code": code,
            "quality_metrics": quality_metrics
        }
        
    async def _generate_ai_solution(
        self,
        requirements: str,
        context: GenerationContext,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-based solution"""
        # Use LLM to generate code
        code = await self.llm.generate_code(
            requirements,
            context
        )
        
        # Analyze code quality
        quality_metrics = await self.code_quality_analyzer.analyze_code(code)
        
        return {
            "code": code,
            "quality_metrics": quality_metrics
        }
        
    async def _generate_improvements(
        self,
        code: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate code improvements"""
        improvements = []
        
        # Generate improvements based on analysis
        if analysis["issues"]:
            improvements.extend(
                await self._generate_issue_fixes(code, analysis["issues"])
            )
            
        if analysis["suggestions"]:
            improvements.extend(
                await self._generate_suggestion_improvements(
                    code,
                    analysis["suggestions"]
                )
            )
            
        # Generate optimizations
        improvements.extend(
            await self._generate_optimizations(code, analysis["metrics"])
        )
        
        return improvements
        
    async def _apply_improvements(
        self,
        code: str,
        improvements: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Apply improvements to code"""
        # Use LLM to apply improvements
        improved_code = await self.llm.improve_code(
            code,
            improvements,
            context
        )
        
        # Validate improved code
        if not await self._validate_code(improved_code, context):
            return code
            
        return improved_code
        
    async def _validate_code(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> bool:
        """Validate generated code"""
        try:
            # Parse code
            if context["language"] == "python":
                ast.parse(code)
            # Add validation for other languages
            
            # Run static analysis
            analysis = await self.code_quality_analyzer.analyze_code(code)
            if analysis["score"] < 0.7:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Code validation failed: {e}")
            return False
            
    async def _cache_result(self, result: GenerationResult) -> None:
        """Cache generation result"""
        cache_file = self.cache_dir / f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(
                {
                    "code": result.code,
                    "documentation": result.documentation,
                    "quality_score": result.quality_score,
                    "suggestions": result.suggestions,
                    "patterns_used": result.patterns_used,
                    "metadata": result.metadata,
                    "generation_time": result.generation_time.isoformat()
                },
                f,
                indent=2
            ) 