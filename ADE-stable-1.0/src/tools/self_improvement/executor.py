import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import shutil
import difflib
from dataclasses import dataclass
import ast
import astor
from concurrent.futures import ThreadPoolExecutor
import logging
from enum import Enum
import hashlib
import tempfile
import subprocess
from typing import Set, Union
import git
from git.exc import GitCommandError

from .analyzer import ImprovementSuggestion
from ..core.models.llm_integration import LLMIntegration, LLMConfig
from ..core.models.code_context_manager import CodeContextManager
from ..core.analysis.impact_analysis import ImpactAnalyzer
from ..core.models.security_analyzer import SecurityAnalyzer, Vulnerability, VulnerabilityType, VulnerabilitySeverity

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Raised when code validation fails"""
    pass

class VerificationError(Exception):
    """Raised when code verification fails"""
    pass

@dataclass
class SafetyCheckResult:
    is_safe: bool
    validation_errors: List[str]
    impact_analysis: Dict[str, Any]
    security_analysis: Dict[str, Any]
    test_results: Dict[str, Any]
    backup_info: Dict[str, Any]

class SafetyManager:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.code_modifier = SafeCodeModifier(project_dir)
        self.version_control = VersionControlManager(project_dir)
        self.security_analyzer = SecurityAnalyzer()
        self.impact_analyzer = ImpactAnalyzer(project_dir)
        
    async def validate_changes(self, changes: List[CodeChange]) -> SafetyCheckResult:
        """Validate changes through multiple safety layers"""
        try:
            # 1. Code Validation
            validation_results = await self.code_modifier._validate_changes(changes)
            validation_errors = []
            for result in validation_results:
                validation_errors.extend(result.errors)
            
            # 2. Impact Analysis
            impact_analysis = await self._analyze_impact(changes)
            
            # 3. Security Analysis
            security_analysis = await self._analyze_security(changes)
            
            # 4. Test Results
            test_results = await self._run_tests(changes)
            
            # 5. Backup Information
            backup_info = await self._create_backup(changes)
            
            # Determine overall safety
            is_safe = (
                len(validation_errors) == 0 and
                impact_analysis.get("risk_level", "HIGH") != "HIGH" and
                len(security_analysis.get("vulnerabilities", [])) == 0 and
                test_results.get("passed", False)
            )
            
            return SafetyCheckResult(
                is_safe=is_safe,
                validation_errors=validation_errors,
                impact_analysis=impact_analysis,
                security_analysis=security_analysis,
                test_results=test_results,
                backup_info=backup_info
            )
            
        except Exception as e:
            logger.error(f"Error in safety validation: {e}")
            return SafetyCheckResult(
                is_safe=False,
                validation_errors=[str(e)],
                impact_analysis={},
                security_analysis={},
                test_results={},
                backup_info={}
            )
            
    async def _analyze_impact(self, changes: List[CodeChange]) -> Dict[str, Any]:
        """Analyze the impact of changes"""
        impact_analysis = {
            "affected_files": set(),
            "risk_level": "LOW",
            "dependencies": set(),
            "breaking_changes": []
        }
        
        for change in changes:
            # Get affected files
            affected = await self.impact_analyzer.get_affected_files(change.file_path)
            impact_analysis["affected_files"].update(affected)
            
            # Analyze dependencies
            deps = await self.code_modifier._analyze_dependencies(Path(change.file_path))
            impact_analysis["dependencies"].update(deps)
            
            # Check for breaking changes
            breaking = await self.impact_analyzer.check_breaking_changes(change)
            if breaking:
                impact_analysis["breaking_changes"].extend(breaking)
                
        # Determine risk level
        if impact_analysis["breaking_changes"]:
            impact_analysis["risk_level"] = "HIGH"
        elif len(impact_analysis["affected_files"]) > 5:
            impact_analysis["risk_level"] = "MEDIUM"
            
        return impact_analysis
        
    async def _analyze_security(self, changes: List[CodeChange]) -> Dict[str, Any]:
        """Analyze security implications of changes"""
        security_analysis = {
            "vulnerabilities": [],
            "security_improvements": [],
            "risk_level": "LOW"
        }
        
        for change in changes:
            # Analyze code for vulnerabilities
            vulnerabilities = self.security_analyzer._find_ast_vulnerabilities(
                ast.parse(change.new_content),
                change.new_content
            )
            security_analysis["vulnerabilities"].extend(vulnerabilities)
            
            # Check for security improvements
            improvements = await self._check_security_improvements(change)
            security_analysis["security_improvements"].extend(improvements)
            
        # Determine security risk level
        if any(v.severity == VulnerabilitySeverity.CRITICAL for v in security_analysis["vulnerabilities"]):
            security_analysis["risk_level"] = "HIGH"
        elif any(v.severity == VulnerabilitySeverity.HIGH for v in security_analysis["vulnerabilities"]):
            security_analysis["risk_level"] = "MEDIUM"
            
        return security_analysis
        
    async def _run_tests(self, changes: List[CodeChange]) -> Dict[str, Any]:
        """Run tests for changes"""
        test_results = {
            "passed": True,
            "failed_tests": [],
            "coverage": 0.0
        }
        
        for change in changes:
            if self.code_modifier._has_tests(Path(change.file_path)):
                # Run tests
                passed = await self.code_modifier._run_tests(Path(change.file_path))
                if not passed:
                    test_results["passed"] = False
                    test_results["failed_tests"].append(change.file_path)
                    
                # Get coverage
                coverage = await self._get_test_coverage(change.file_path)
                test_results["coverage"] = max(test_results["coverage"], coverage)
                
        return test_results
        
    async def _create_backup(self, changes: List[CodeChange]) -> Dict[str, Any]:
        """Create backup of changes"""
        backup_info = {
            "backup_path": None,
            "timestamp": None,
            "files_backed_up": []
        }
        
        try:
            # Create backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.project_dir / "backups" / f"backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup each changed file
            for change in changes:
                file_path = Path(change.file_path)
                if file_path.exists():
                    backup_file = backup_path / file_path.name
                    shutil.copy2(file_path, backup_file)
                    backup_info["files_backed_up"].append(str(file_path))
                    
            backup_info["backup_path"] = str(backup_path)
            backup_info["timestamp"] = timestamp
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            
        return backup_info
        
    async def _check_security_improvements(self, change: CodeChange) -> List[str]:
        """Check for security improvements in changes"""
        improvements = []
        
        # Check for added input validation
        if "validate" in change.new_content.lower():
            improvements.append("Added input validation")
            
        # Check for added output sanitization
        if "sanitize" in change.new_content.lower():
            improvements.append("Added output sanitization")
            
        # Check for added error handling
        if "try" in change.new_content.lower() and "except" in change.new_content.lower():
            improvements.append("Added error handling")
            
        # Check for added logging
        if "logging" in change.new_content.lower():
            improvements.append("Added logging")
            
        return improvements
        
    async def _get_test_coverage(self, file_path: str) -> float:
        """Get test coverage for a file"""
        try:
            result = await self.code_modifier._run_command(f"coverage run -m pytest {file_path}")
            if result.returncode == 0:
                report = await self.code_modifier._run_command(f"coverage report {file_path}")
                # Parse coverage percentage from report
                for line in report.stdout.decode().splitlines():
                    if "TOTAL" in line:
                        return float(line.split()[-1].strip("%"))
            return 0.0
        except Exception:
            return 0.0

@dataclass
class CodeChange:
    file_path: str
    original_content: str
    new_content: str
    line_numbers: List[int]
    description: str
    metadata: Dict[str, Any] = None
    created_at: datetime = datetime.now()
    change_hash: str = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, float]
    dependencies: Set[str]

class SafeCodeModifier:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.safety_manager = SafetyManager(project_dir)
        self.validation_tools = self._initialize_validation_tools()
        self.backup_dir = self.project_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    async def apply_changes(self, changes: List[CodeChange]) -> bool:
        """Apply code changes with comprehensive safety checks"""
        try:
            # 1. Validate changes through safety manager
            safety_result = await self.safety_manager.validate_changes(changes)
            if not safety_result.is_safe:
                logger.error(f"Safety validation failed: {safety_result.validation_errors}")
                return False
                
            # 2. Create backup
            backup_path = await self._create_backup(changes)
            if not backup_path:
                logger.error("Failed to create backup")
                return False
                
            # 3. Apply changes
            for change in changes:
                try:
                    # Apply change
                    await self._apply_single_change(change)
                    
                    # Verify change
                    if not await self._verify_change(change):
                        raise VerificationError(f"Change verification failed for {change.file_path}")
                        
                except Exception as e:
                    logger.error(f"Error applying change to {change.file_path}: {e}")
                    # Restore from backup
                    await self._restore_from_backup(backup_path)
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error in apply_changes: {e}")
            return False
            
    async def _apply_single_change(self, change: CodeChange) -> None:
        """Apply a single code change"""
        try:
            file_path = Path(change.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {change.file_path}")
                
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
                
            # Apply change
            new_content = self._apply_diff(current_content, change)
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            logger.error(f"Error applying change: {e}")
            raise
            
    async def _verify_change(self, change: CodeChange) -> bool:
        """Verify a code change"""
        try:
            # 1. Check file exists
            file_path = Path(change.file_path)
            if not file_path.exists():
                return False
                
            # 2. Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
                
            # 3. Validate syntax
            try:
                ast.parse(current_content)
            except SyntaxError:
                return False
                
            # 4. Run validation tools
            validation_results = await self._validate_changes([change])
            for result in validation_results:
                if result.errors:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error verifying change: {e}")
            return False
            
    async def _validate_changes(self, changes: List[CodeChange]) -> List[ValidationResult]:
        """Validate code changes using multiple tools"""
        results = []
        
        for change in changes:
            try:
                # 1. Syntax validation
                try:
                    ast.parse(change.new_content)
                except SyntaxError as e:
                    results.append(ValidationResult(
                        file_path=change.file_path,
                        errors=[f"Syntax error: {str(e)}"]
                    ))
                    continue
                    
                # 2. Style validation
                style_errors = await self._run_pylint(change)
                if style_errors:
                    results.append(ValidationResult(
                        file_path=change.file_path,
                        errors=style_errors
                    ))
                    
                # 3. Type checking
                type_errors = await self._run_mypy(change)
                if type_errors:
                    results.append(ValidationResult(
                        file_path=change.file_path,
                        errors=type_errors
                    ))
                    
                # 4. Security validation
                security_errors = await self._run_security_check(change)
                if security_errors:
                    results.append(ValidationResult(
                        file_path=change.file_path,
                        errors=security_errors
                    ))
                    
            except Exception as e:
                logger.error(f"Error validating change: {e}")
                results.append(ValidationResult(
                    file_path=change.file_path,
                    errors=[str(e)]
                ))
                
        return results
        
    async def _run_pylint(self, change: CodeChange) -> List[str]:
        """Run pylint on code changes"""
        try:
            result = await self._run_command(f"pylint {change.file_path}")
            if result.returncode != 0:
                return [line for line in result.stderr.decode().splitlines() if line.strip()]
            return []
        except Exception as e:
            logger.error(f"Error running pylint: {e}")
            return []
            
    async def _run_mypy(self, change: CodeChange) -> List[str]:
        """Run mypy on code changes"""
        try:
            result = await self._run_command(f"mypy {change.file_path}")
            if result.returncode != 0:
                return [line for line in result.stderr.decode().splitlines() if line.strip()]
            return []
        except Exception as e:
            logger.error(f"Error running mypy: {e}")
            return []
            
    async def _run_security_check(self, change: CodeChange) -> List[str]:
        """Run security checks on code changes"""
        try:
            # Use safety manager's security analysis
            security_analysis = await self.safety_manager._analyze_security([change])
            return [str(v) for v in security_analysis.get("vulnerabilities", [])]
        except Exception as e:
            logger.error(f"Error running security check: {e}")
            return []
            
    async def _run_command(self, command: str) -> subprocess.CompletedProcess:
        """Run a shell command"""
        try:
            return await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_dir)
            )
        except Exception as e:
            logger.error(f"Error running command: {e}")
            raise
            
    def _apply_diff(self, current_content: str, change: CodeChange) -> str:
        """Apply a diff to current content"""
        try:
            diff = difflib.unified_diff(
                current_content.splitlines(keepends=True),
                change.new_content.splitlines(keepends=True),
                fromfile=change.file_path,
                tofile=change.file_path
            )
            
            # Apply diff
            new_content = []
            for line in diff:
                if line.startswith('+'):
                    new_content.append(line[1:])
                elif not line.startswith('-'):
                    new_content.append(line)
                    
            return ''.join(new_content)
            
        except Exception as e:
            logger.error(f"Error applying diff: {e}")
            raise
            
    async def _create_backup(self, changes: List[CodeChange]) -> Optional[str]:
        """Create a backup of changes"""
        try:
            # Use safety manager's backup functionality
            backup_info = await self.safety_manager._create_backup(changes)
            return backup_info.get("backup_path")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
            
    async def _restore_from_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False
                
            # Restore each backed up file
            for backup_file in backup_dir.glob("*"):
                target_file = self.project_dir / backup_file.name
                shutil.copy2(backup_file, target_file)
                
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
            
    def _initialize_validation_tools(self) -> Dict[str, Any]:
        """Initialize validation tools"""
        return {
            "pylint": self._check_pylint_installed(),
            "mypy": self._check_mypy_installed(),
            "coverage": self._check_coverage_installed()
        }
        
    def _check_pylint_installed(self) -> bool:
        """Check if pylint is installed"""
        try:
            subprocess.run(["pylint", "--version"], capture_output=True)
            return True
        except FileNotFoundError:
            return False
            
    def _check_mypy_installed(self) -> bool:
        """Check if mypy is installed"""
        try:
            subprocess.run(["mypy", "--version"], capture_output=True)
            return True
        except FileNotFoundError:
            return False
            
    def _check_coverage_installed(self) -> bool:
        """Check if coverage is installed"""
        try:
            subprocess.run(["coverage", "--version"], capture_output=True)
            return True
        except FileNotFoundError:
            return False

class FixCategory(Enum):
    BUG = "bug"
    PERFORMANCE = "performance"
    SECURITY = "security"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"

@dataclass
class CodeFix:
    category: FixCategory
    file_path: str
    line_numbers: List[int]
    description: str
    fix_code: str
    impact: str
    effort: str
    confidence: float
    context: Dict[str, Any]
    created_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None

@dataclass
class ImprovementResult:
    suggestion: ImprovementSuggestion
    success: bool
    changes_made: List[str]
    errors: List[str]
    diff: Optional[str]
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    fixes_applied: List[CodeFix] = None

@dataclass
class CodeContext:
    file_path: str
    content: str
    imports: List[str]
    dependencies: Set[str]
    related_files: List[str]
    patterns: Dict[str, List[str]]
    style_guide: Dict[str, Any]
    test_coverage: Dict[str, float]
    metrics: Dict[str, float]

class ContextAwareFixSystem:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.context_cache: Dict[str, CodeContext] = {}
        self.pattern_analyzer = PatternAnalyzer()
        self.style_analyzer = StyleAnalyzer()
        self.test_analyzer = TestAnalyzer()
        
    async def get_context(self, file_path: str) -> CodeContext:
        """Get or create context for a file"""
        if file_path in self.context_cache:
            return self.context_cache[file_path]
            
        # Analyze file and its context
        content = self._read_file(file_path)
        imports = self._analyze_imports(content)
        dependencies = self._analyze_dependencies(file_path)
        related_files = self._find_related_files(file_path)
        patterns = await self.pattern_analyzer.analyze_patterns(file_path)
        style_guide = await self.style_analyzer.analyze_style(file_path)
        test_coverage = await self.test_analyzer.get_coverage(file_path)
        metrics = self._calculate_metrics(content)
        
        context = CodeContext(
            file_path=file_path,
            content=content,
            imports=imports,
            dependencies=dependencies,
            related_files=related_files,
            patterns=patterns,
            style_guide=style_guide,
            test_coverage=test_coverage,
            metrics=metrics
        )
        
        self.context_cache[file_path] = context
        return context
        
    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        with open(file_path, 'r') as f:
            return f.read()
            
    def _analyze_imports(self, content: str) -> List[str]:
        """Analyze imports in file"""
        imports = []
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend(name.name for name in node.names)
                else:
                    imports.append(node.module)
                    
        return imports
        
    def _analyze_dependencies(self, file_path: str) -> Set[str]:
        """Analyze file dependencies"""
        dependencies = set()
        
        # Get imports
        with open(file_path, 'r') as f:
            content = f.read()
        imports = self._analyze_imports(content)
        
        # Find imported files in project
        for imp in imports:
            module_path = self._find_module_path(imp)
            if module_path:
                dependencies.add(module_path)
                
        return dependencies
        
    def _find_module_path(self, module_name: str) -> Optional[str]:
        """Find module path in project"""
        for path in self.project_dir.rglob("*.py"):
            if path.stem == module_name:
                return str(path)
        return None
        
    def _find_related_files(self, file_path: str) -> List[str]:
        """Find related files based on imports and dependencies"""
        related = set()
        
        # Get direct dependencies
        dependencies = self._analyze_dependencies(file_path)
        related.update(dependencies)
        
        # Get files that import this file
        for path in self.project_dir.rglob("*.py"):
            if str(path) != file_path:
                deps = self._analyze_dependencies(str(path))
                if file_path in deps:
                    related.add(str(path))
                    
        return list(related)
        
    def _calculate_metrics(self, content: str) -> Dict[str, float]:
        """Calculate code metrics"""
        tree = ast.parse(content)
        
        return {
            "complexity": self._calculate_complexity(tree),
            "loc": len(content.splitlines()),
            "functions": len([
                node for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]),
            "classes": len([
                node for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ])
        }
        
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.BoolOp)):
                complexity += 1
                
        return complexity

class PatternAnalyzer:
    async def analyze_patterns(self, file_path: str) -> Dict[str, List[str]]:
        """Analyze code patterns in file"""
        patterns = {
            "naming": [],
            "structure": [],
            "error_handling": [],
            "logging": [],
            "testing": []
        }
        
        with open(file_path, 'r') as f:
            content = f.read()
        tree = ast.parse(content)
        
        # Analyze naming patterns
        patterns["naming"] = self._analyze_naming_patterns(tree)
        
        # Analyze structural patterns
        patterns["structure"] = self._analyze_structural_patterns(tree)
        
        # Analyze error handling patterns
        patterns["error_handling"] = self._analyze_error_handling_patterns(tree)
        
        # Analyze logging patterns
        patterns["logging"] = self._analyze_logging_patterns(tree)
        
        # Analyze testing patterns
        patterns["testing"] = self._analyze_testing_patterns(tree)
        
        return patterns
        
    def _analyze_naming_patterns(self, tree: ast.AST) -> List[str]:
        """Analyze naming patterns"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._is_descriptive_name(node.name):
                    patterns.append(f"descriptive_function_name:{node.name}")
                    
            elif isinstance(node, ast.Name):
                if self._is_descriptive_name(node.id):
                    patterns.append(f"descriptive_variable_name:{node.id}")
                    
        return patterns
        
    def _analyze_structural_patterns(self, tree: ast.AST) -> List[str]:
        """Analyze structural patterns"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._has_private_methods(node):
                    patterns.append("private_methods")
                if self._has_property_decorators(node):
                    patterns.append("property_decorators")
                    
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._has_type_hints(node):
                    patterns.append("type_hints")
                if self._has_docstring(node):
                    patterns.append("docstrings")
                    
        return patterns
        
    def _analyze_error_handling_patterns(self, tree: ast.AST) -> List[str]:
        """Analyze error handling patterns"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                if self._has_specific_exceptions(node):
                    patterns.append("specific_exceptions")
                if self._has_finally_block(node):
                    patterns.append("finally_blocks")
                    
        return patterns
        
    def _analyze_logging_patterns(self, tree: ast.AST) -> List[str]:
        """Analyze logging patterns"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "logging":
                    patterns.append("logging_usage")
                    
        return patterns
        
    def _analyze_testing_patterns(self, tree: ast.AST) -> List[str]:
        """Analyze testing patterns"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id.startswith("assert"):
                    patterns.append("assertions")
                    
        return patterns

class StyleAnalyzer:
    async def analyze_style(self, file_path: str) -> Dict[str, Any]:
        """Analyze code style"""
        style = {
            "indentation": 4,
            "max_line_length": 79,
            "quote_style": "single",
            "naming_conventions": {
                "functions": "snake_case",
                "classes": "PascalCase",
                "variables": "snake_case",
                "constants": "UPPER_CASE"
            }
        }
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Analyze indentation
        style["indentation"] = self._analyze_indentation(content)
        
        # Analyze quote style
        style["quote_style"] = self._analyze_quote_style(content)
        
        # Analyze naming conventions
        style["naming_conventions"] = self._analyze_naming_conventions(content)
        
        return style
        
    def _analyze_indentation(self, content: str) -> int:
        """Analyze indentation style"""
        lines = content.splitlines()
        indents = []
        
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)
                    
        if not indents:
            return 4
            
        return min(indents)
        
    def _analyze_quote_style(self, content: str) -> str:
        """Analyze quote style preference"""
        single_quotes = content.count("'")
        double_quotes = content.count('"')
        
        return "single" if single_quotes > double_quotes else "double"
        
    def _analyze_naming_conventions(self, content: str) -> Dict[str, str]:
        """Analyze naming conventions"""
        conventions = {
            "functions": "snake_case",
            "classes": "PascalCase",
            "variables": "snake_case",
            "constants": "UPPER_CASE"
        }
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    conventions["functions"] = "mixed"
                    
            elif isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    conventions["classes"] = "mixed"
                    
            elif isinstance(node, ast.Name):
                if self._is_constant(node):
                    if not self._is_upper_case(node.id):
                        conventions["constants"] = "mixed"
                else:
                    if not self._is_snake_case(node.id):
                        conventions["variables"] = "mixed"
                        
        return conventions

class TestAnalyzer:
    async def get_coverage(self, file_path: str) -> Dict[str, float]:
        """Get test coverage information"""
        coverage = {
            "overall": 0.0,
            "functions": {},
            "classes": {},
            "lines": {}
        }
        
        try:
            # Run coverage tool
            result = await self._run_coverage(file_path)
            
            # Parse coverage data
            coverage_data = self._parse_coverage_data(result)
            
            # Update coverage information
            coverage.update(coverage_data)
            
        except Exception as e:
            logger.error(f"Error getting coverage: {e}")
            
        return coverage
        
    async def _run_coverage(self, file_path: str) -> str:
        """Run coverage tool on file"""
        try:
            result = await asyncio.create_subprocess_shell(
                f"coverage run -m pytest {file_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            # Get coverage report
            report = await asyncio.create_subprocess_shell(
                f"coverage report {file_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await report.communicate()
            
            return stdout.decode()
            
        except Exception as e:
            logger.error(f"Error running coverage: {e}")
            return ""
            
    def _parse_coverage_data(self, coverage_output: str) -> Dict[str, float]:
        """Parse coverage tool output"""
        coverage = {
            "overall": 0.0,
            "functions": {},
            "classes": {},
            "lines": {}
        }
        
        try:
            lines = coverage_output.splitlines()
            
            # Parse overall coverage
            for line in lines:
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage["overall"] = float(parts[3].strip("%"))
                        
            # Parse function coverage
            for line in lines:
                if "def " in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        func_name = parts[0]
                        coverage["functions"][func_name] = float(parts[3].strip("%"))
                        
            # Parse class coverage
            for line in lines:
                if "class " in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        class_name = parts[0]
                        coverage["classes"][class_name] = float(parts[3].strip("%"))
                        
        except Exception as e:
            logger.error(f"Error parsing coverage data: {e}")
            
        return coverage

@dataclass
class SolutionVariant:
    fix: CodeFix
    effectiveness_score: float
    impact_score: float
    complexity_score: float
    maintainability_score: float
    confidence: float
    metadata: Dict[str, Any] = None

class MultiSolutionGenerator:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.context_aware_fix = ContextAwareFixSystem(project_dir)
        self.impact_analyzer = ImpactAnalyzer(project_dir)
        
    async def generate_solutions(self, error: str, file_path: str) -> List[SolutionVariant]:
        """Generate multiple solution variants for a given error"""
        try:
            # Get code context
            context = await self.context_aware_fix.get_context(file_path)
            
            # Generate base fixes
            base_fixes = await self._generate_base_fixes(error, context)
            
            # Generate variants for each base fix
            solution_variants = []
            for base_fix in base_fixes:
                variants = await self._generate_variants(base_fix, context)
                solution_variants.extend(variants)
            
            # Score and rank solutions
            scored_solutions = await self._score_solutions(solution_variants, context)
            
            # Sort by overall score
            scored_solutions.sort(key=lambda x: self._calculate_overall_score(x), reverse=True)
            
            return scored_solutions
            
        except Exception as e:
            logger.error(f"Error generating solutions: {e}")
            return []
            
    async def _generate_base_fixes(self, error: str, context: CodeContext) -> List[CodeFix]:
        """Generate base fixes using different approaches"""
        base_fixes = []
        
        # Generate fix using different strategies
        strategies = [
            self._generate_minimal_fix,
            self._generate_comprehensive_fix,
            self._generate_pattern_based_fix,
            self._generate_refactoring_fix
        ]
        
        for strategy in strategies:
            try:
                fix = await strategy(error, context)
                if fix:
                    base_fixes.append(fix)
            except Exception as e:
                logger.error(f"Error in strategy {strategy.__name__}: {e}")
                
        return base_fixes
        
    async def _generate_minimal_fix(self, error: str, context: CodeContext) -> Optional[CodeFix]:
        """Generate a minimal fix that addresses the core issue"""
        try:
            # Analyze error to identify core issue
            core_issue = self._identify_core_issue(error)
            
            # Generate minimal fix
            fix_code = await self._generate_minimal_solution(core_issue, context)
            
            return CodeFix(
                category=FixCategory.BUG,
                file_path=context.file_path,
                line_numbers=self._identify_affected_lines(error, context),
                description=f"Minimal fix for {core_issue}",
                fix_code=fix_code,
                impact="Low",
                effort="Low",
                confidence=0.8,
                context=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"Error generating minimal fix: {e}")
            return None
            
    async def _generate_comprehensive_fix(self, error: str, context: CodeContext) -> Optional[CodeFix]:
        """Generate a comprehensive fix that addresses the issue and related concerns"""
        try:
            # Analyze error and related issues
            issues = await self._analyze_related_issues(error, context)
            
            # Generate comprehensive fix
            fix_code = await self._generate_comprehensive_solution(issues, context)
            
            return CodeFix(
                category=FixCategory.BUG,
                file_path=context.file_path,
                line_numbers=self._identify_affected_lines(error, context),
                description=f"Comprehensive fix addressing {len(issues)} issues",
                fix_code=fix_code,
                impact="High",
                effort="High",
                confidence=0.7,
                context=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"Error generating comprehensive fix: {e}")
            return None
            
    async def _generate_pattern_based_fix(self, error: str, context: CodeContext) -> Optional[CodeFix]:
        """Generate a fix based on project patterns"""
        try:
            # Analyze project patterns
            patterns = context.patterns
            
            # Generate pattern-based fix
            fix_code = await self._generate_pattern_solution(error, patterns, context)
            
            return CodeFix(
                category=FixCategory.BUG,
                file_path=context.file_path,
                line_numbers=self._identify_affected_lines(error, context),
                description="Pattern-based fix following project conventions",
                fix_code=fix_code,
                impact="Medium",
                effort="Medium",
                confidence=0.85,
                context=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"Error generating pattern-based fix: {e}")
            return None
            
    async def _generate_refactoring_fix(self, error: str, context: CodeContext) -> Optional[CodeFix]:
        """Generate a fix that includes refactoring"""
        try:
            # Analyze code structure
            structure = self._analyze_code_structure(context)
            
            # Generate refactoring fix
            fix_code = await self._generate_refactoring_solution(error, structure, context)
            
            return CodeFix(
                category=FixCategory.REFACTORING,
                file_path=context.file_path,
                line_numbers=self._identify_affected_lines(error, context),
                description="Refactoring fix improving code structure",
                fix_code=fix_code,
                impact="High",
                effort="High",
                confidence=0.75,
                context=context.__dict__
            )
            
        except Exception as e:
            logger.error(f"Error generating refactoring fix: {e}")
            return None
        
    async def _generate_variants(self, base_fix: CodeFix, context: CodeContext) -> List[SolutionVariant]:
        """Generate variants of a base fix"""
        variants = []
        
        # Generate different implementation approaches
        approaches = [
            self._generate_simple_variant,
            self._generate_optimized_variant,
            self._generate_robust_variant,
            self._generate_maintainable_variant
        ]
        
        for approach in approaches:
            try:
                variant = await approach(base_fix, context)
                if variant:
                    variants.append(variant)
            except Exception as e:
                logger.error(f"Error in approach {approach.__name__}: {e}")
                
        return variants
        
    async def _generate_simple_variant(self, base_fix: CodeFix, context: CodeContext) -> Optional[SolutionVariant]:
        """Generate a simple variant of the base fix"""
        try:
            # Create simplified version
            simplified_fix = await self._simplify_fix(base_fix, context)
            
            return SolutionVariant(
                fix=simplified_fix,
                effectiveness_score=0.8,
                impact_score=0.6,
                complexity_score=0.9,
                maintainability_score=0.8,
                confidence=0.85,
                metadata={"approach": "simple"}
            )
            
        except Exception as e:
            logger.error(f"Error generating simple variant: {e}")
            return None
            
    async def _generate_optimized_variant(self, base_fix: CodeFix, context: CodeContext) -> Optional[SolutionVariant]:
        """Generate an optimized variant of the base fix"""
        try:
            # Create optimized version
            optimized_fix = await self._optimize_fix(base_fix, context)
            
            return SolutionVariant(
                fix=optimized_fix,
                effectiveness_score=0.9,
                impact_score=0.8,
                complexity_score=0.7,
                maintainability_score=0.7,
                confidence=0.8,
                metadata={"approach": "optimized"}
            )
            
        except Exception as e:
            logger.error(f"Error generating optimized variant: {e}")
            return None
            
    async def _generate_robust_variant(self, base_fix: CodeFix, context: CodeContext) -> Optional[SolutionVariant]:
        """Generate a robust variant of the base fix"""
        try:
            # Create robust version
            robust_fix = await self._make_fix_robust(base_fix, context)
            
            return SolutionVariant(
                fix=robust_fix,
                effectiveness_score=0.95,
                impact_score=0.9,
                complexity_score=0.6,
                maintainability_score=0.6,
                confidence=0.9,
                metadata={"approach": "robust"}
            )
            
        except Exception as e:
            logger.error(f"Error generating robust variant: {e}")
            return None
            
    async def _generate_maintainable_variant(self, base_fix: CodeFix, context: CodeContext) -> Optional[SolutionVariant]:
        """Generate a maintainable variant of the base fix"""
        try:
            # Create maintainable version
            maintainable_fix = await self._make_fix_maintainable(base_fix, context)
            
            return SolutionVariant(
                fix=maintainable_fix,
                effectiveness_score=0.85,
                impact_score=0.7,
                complexity_score=0.8,
                maintainability_score=0.9,
                confidence=0.85,
                metadata={"approach": "maintainable"}
            )
            
        except Exception as e:
            logger.error(f"Error generating maintainable variant: {e}")
            return None
            
    async def _score_solutions(self, solutions: List[SolutionVariant], context: CodeContext) -> List[SolutionVariant]:
        """Score solution variants based on multiple criteria"""
        scored_solutions = []
        
        for solution in solutions:
            # Calculate effectiveness score
            effectiveness = await self._calculate_effectiveness(solution, context)
            
            # Calculate impact score
            impact = await self._calculate_impact(solution, context)
            
            # Calculate complexity score
            complexity = self._calculate_complexity(solution)
            
            # Calculate maintainability score
            maintainability = self._calculate_maintainability(solution, context)
            
            # Update solution scores
            solution.effectiveness_score = effectiveness
            solution.impact_score = impact
            solution.complexity_score = complexity
            solution.maintainability_score = maintainability
            
            scored_solutions.append(solution)
            
        return scored_solutions
        
    async def _calculate_effectiveness(self, solution: SolutionVariant, context: CodeContext) -> float:
        """Calculate effectiveness score for a solution"""
        # Analyze solution's ability to fix the issue
        fix_effectiveness = self._analyze_fix_effectiveness(solution.fix)
        
        # Check for potential side effects
        side_effects = self._analyze_side_effects(solution.fix, context)
        
        # Calculate final score
        return fix_effectiveness * (1 - side_effects)
        
    async def _calculate_impact(self, solution: SolutionVariant, context: CodeContext) -> float:
        """Calculate impact score for a solution"""
        # Analyze code changes
        changes = self._analyze_code_changes(solution.fix)
        
        # Check dependencies
        dependencies = self._analyze_dependencies(solution.fix, context)
        
        # Calculate final score
        return min(1.0, changes * (1 + len(dependencies) * 0.1))
        
    def _calculate_complexity(self, solution: SolutionVariant) -> float:
        """Calculate complexity score for a solution"""
        # Analyze code complexity
        complexity = self._analyze_code_complexity(solution.fix.fix_code)
        
        # Calculate score (lower complexity = higher score)
        return max(0.0, 1.0 - complexity / 10.0)
        
    def _calculate_maintainability(self, solution: SolutionVariant, context: CodeContext) -> float:
        """Calculate maintainability score for a solution"""
        # Analyze code maintainability
        maintainability = self._analyze_maintainability(solution.fix.fix_code)
        
        # Check consistency with project patterns
        pattern_consistency = self._check_pattern_consistency(solution.fix, context)
        
        # Calculate final score
        return maintainability * pattern_consistency
        
    def _calculate_overall_score(self, solution: SolutionVariant) -> float:
        """Calculate overall score for a solution"""
        weights = {
            'effectiveness': 0.4,
            'impact': 0.3,
            'complexity': 0.15,
            'maintainability': 0.15
        }
        
        return (
            solution.effectiveness_score * weights['effectiveness'] +
            solution.impact_score * weights['impact'] +
            solution.complexity_score * weights['complexity'] +
            solution.maintainability_score * weights['maintainability']
        )

class VersionControlManager:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.repo = self._initialize_repo()
        
    def _initialize_repo(self) -> git.Repo:
        """Initialize or get Git repository"""
        try:
            return git.Repo(self.project_dir)
        except git.InvalidGitRepositoryError:
            # Initialize new repository if none exists
            repo = git.Repo.init(self.project_dir)
            self._create_initial_commit(repo)
            return repo
            
    def _create_initial_commit(self, repo: git.Repo):
        """Create initial commit with existing files"""
        try:
            # Add all files
            repo.index.add("*")
            # Create initial commit
            repo.index.commit("Initial commit")
        except GitCommandError as e:
            logger.error(f"Error creating initial commit: {e}")
            
    async def create_branch(self, branch_name: str) -> bool:
        """Create a new branch for improvements"""
        try:
            # Create and checkout new branch
            current = self.repo.active_branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            logger.info(f"Created and switched to branch: {branch_name}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error creating branch: {e}")
            return False
            
    async def commit_changes(self, message: str, files: List[str]) -> bool:
        """Commit changes to the current branch"""
        try:
            # Add modified files
            self.repo.index.add(files)
            
            # Create commit
            self.repo.index.commit(message)
            
            logger.info(f"Committed changes: {message}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error committing changes: {e}")
            return False
            
    async def merge_changes(self, source_branch: str, target_branch: str = "main") -> bool:
        """Merge changes from source branch to target branch"""
        try:
            # Switch to target branch
            target = self.repo.heads[target_branch]
            target.checkout()
            
            # Merge source branch
            self.repo.git.merge(source_branch)
            
            logger.info(f"Merged {source_branch} into {target_branch}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error merging changes: {e}")
            return False
            
    async def revert_changes(self, commit_hash: str) -> bool:
        """Revert changes to a specific commit"""
        try:
            # Reset to commit
            self.repo.git.reset(commit_hash, hard=True)
            
            logger.info(f"Reverted to commit: {commit_hash}")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error reverting changes: {e}")
            return False
            
    async def get_changes(self, file_path: str) -> List[Dict[str, Any]]:
        """Get change history for a file"""
        try:
            # Get file history
            history = self.repo.git.log(
                "--follow",  # Follow file renames
                "--patch",   # Include changes
                "--format=%H|%an|%ad|%s",  # Format: hash|author|date|message
                file_path
            ).split("\n")
            
            changes = []
            for entry in history:
                if not entry:
                    continue
                    
                hash_id, author, date, message = entry.split("|")
                changes.append({
                    "hash": hash_id,
                    "author": author,
                    "date": date,
                    "message": message
                })
                
            return changes
            
        except GitCommandError as e:
            logger.error(f"Error getting file history: {e}")
            return []
            
    async def get_diff(self, file_path: str, old_hash: str, new_hash: str) -> str:
        """Get diff between two commits for a file"""
        try:
            diff = self.repo.git.diff(
                old_hash,
                new_hash,
                "--",
                file_path
            )
            return diff
            
        except GitCommandError as e:
            logger.error(f"Error getting diff: {e}")
            return ""
            
    async def stash_changes(self) -> bool:
        """Stash current changes"""
        try:
            self.repo.git.stash()
            logger.info("Stashed current changes")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error stashing changes: {e}")
            return False
            
    async def pop_stash(self) -> bool:
        """Pop the most recent stash"""
        try:
            self.repo.git.stash("pop")
            logger.info("Popped most recent stash")
            return True
            
        except GitCommandError as e:
            logger.error(f"Error popping stash: {e}")
            return False

class ImprovementExecutor:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.current_dir = self.project_dir / "current"
        self.improvements_dir = self.project_dir / "improvements"
        self.backup_dir = self.project_dir / "backups"
        self.reports_dir = self.project_dir / "reports"
        
        # Create necessary directories
        self.reports_dir.mkdir(exist_ok=True)
        
        # Load project configuration
        with open(self.project_dir / "config.json") as f:
            self.config = json.load(f)
            
        # Initialize components
        self.llm = LLMIntegration(LLMConfig(**self.config.get("llm", {})))
        self.context_manager = CodeContextManager(self.project_dir)
        self.impact_analyzer = ImpactAnalyzer(self.project_dir)
        self.code_modifier = SafeCodeModifier(self.project_dir)
        self.context_aware_fix = ContextAwareFixSystem(self.project_dir)
        self.solution_generator = MultiSolutionGenerator(self.project_dir)
        self.version_control = VersionControlManager(self.project_dir)
        
        # Initialize fix tracking
        self.fix_history: Dict[str, List[CodeFix]] = {}
        
    async def generate_code_fixes(self, error: str, file_path: str) -> List[CodeFix]:
        """Generate code fixes for a given error using all available systems"""
        try:
            # Get code context
            context = await self.context_aware_fix.get_context(file_path)
            
            # Generate multiple solution variants
            solution_variants = await self.solution_generator.generate_solutions(error, file_path)
            
            # Convert variants to fixes
            fixes = [variant.fix for variant in solution_variants]
            
            # Track fixes
            self._track_fixes(file_path, fixes)
            
            return fixes
            
        except Exception as e:
            logger.error(f"Error generating code fixes: {e}")
            return []
            
    async def _apply_fix(self, file_path: Path, fix: CodeFix) -> bool:
        """Apply a code fix safely using the SafeCodeModifier"""
        try:
            # Read current content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Create code change
            change = CodeChange(
                file_path=str(file_path),
                original_content=content,
                new_content=fix.fix_code,
                line_numbers=fix.line_numbers,
                description=fix.description,
                metadata=fix.metadata
            )
            
            # Apply change safely
            results = await self.code_modifier.apply_changes([change])
            
            # Check results
            if not results or not results[0].is_valid:
                logger.error(f"Failed to apply fix: {results[0].errors if results else 'No results'}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error applying fix: {e}")
            return False
            
    async def _execute_single_improvement(self, suggestion: ImprovementSuggestion) -> ImprovementResult:
        """Execute a single improvement suggestion using all available systems"""
        try:
            # Record metrics before changes
            metrics_before = self._get_current_metrics()
            
            # Create a copy of the file to modify
            file_path = self._find_target_file(suggestion)
            if not file_path:
                return ImprovementResult(
                    suggestion=suggestion,
                    success=False,
                    changes_made=[],
                    errors=["Target file not found"],
                    diff=None,
                    metrics_before=metrics_before,
                    metrics_after={}
                )
            
            # Read original content
            with open(file_path, 'r') as f:
                original_content = f.read()
            
            # Generate code fixes using context-aware system
            fixes = await self.generate_code_fixes(suggestion.description, str(file_path))
            if not fixes:
                return ImprovementResult(
                    suggestion=suggestion,
                    success=False,
                    changes_made=[],
                    errors=["No valid fixes generated"],
                    diff=None,
                    metrics_before=metrics_before,
                    metrics_after={}
                )
            
            # Apply fixes safely
            changes_made = []
            errors = []
            applied_fixes = []
            
            try:
                for fix in fixes:
                    # Apply fix using safe code modifier
                    success = await self._apply_fix(file_path, fix)
                    if success:
                        changes_made.append(fix.description)
                        applied_fixes.append(fix)
                    else:
                        errors.append(f"Failed to apply fix: {fix.description}")
                
                # Generate diff
                with open(file_path, 'r') as f:
                    new_content = f.read()
                diff = self._generate_diff(original_content, new_content)
                
                # Record metrics after changes
                metrics_after = self._get_current_metrics()
                
                return ImprovementResult(
                    suggestion=suggestion,
                    success=len(errors) == 0,
                    changes_made=changes_made,
                    errors=errors,
                    diff=diff,
                    metrics_before=metrics_before,
                    metrics_after=metrics_after,
                    fixes_applied=applied_fixes
                )
            
            except Exception as e:
                return ImprovementResult(
                    suggestion=suggestion,
                    success=False,
                    changes_made=changes_made,
                    errors=[str(e)] + errors,
                    diff=None,
                    metrics_before=metrics_before,
                    metrics_after={},
                    fixes_applied=applied_fixes
                )
                
        except Exception as e:
            return ImprovementResult(
                suggestion=suggestion,
                success=False,
                changes_made=[],
                errors=[str(e)],
                diff=None,
                metrics_before={},
                metrics_after={}
            )
            
    async def execute_improvements(self, suggestions: List[ImprovementSuggestion]) -> List[ImprovementResult]:
        """Execute a list of improvement suggestions with version control"""
        results = []
        
        # Sort suggestions by priority
        sorted_suggestions = sorted(suggestions, key=lambda x: x.priority, reverse=True)
        
        for suggestion in sorted_suggestions:
            try:
                # Create branch for improvement
                branch_name = f"improvement/{suggestion.category}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if not await self.version_control.create_branch(branch_name):
                    results.append(
                        ImprovementResult(
                            suggestion=suggestion,
                            success=False,
                            changes_made=[],
                            errors=["Failed to create version control branch"],
                            diff=None,
                            metrics_before={},
                            metrics_after={}
                        )
                    )
                    continue
                
                try:
                    # Execute improvement
                    result = await self._execute_single_improvement(suggestion)
                    results.append(result)
                    
                    # Save improvement result
                    self._save_improvement_result(result)
                    
                    # If improvement failed, revert changes
                    if not result.success:
                        await self.version_control.revert_changes("HEAD")
                    else:
                        # Commit successful changes
                        commit_message = f"Applied improvements: {', '.join(result.changes_made)}"
                        await self.version_control.commit_changes(commit_message, [str(result.suggestion.file_path)])
                        
                        # Merge changes to main branch
                        await self.version_control.merge_changes(branch_name)
                
                except Exception as e:
                    # Revert changes on error
                    await self.version_control.revert_changes("HEAD")
                    results.append(
                        ImprovementResult(
                            suggestion=suggestion,
                            success=False,
                            changes_made=[],
                            errors=[str(e)],
                            diff=None,
                            metrics_before={},
                            metrics_after={}
                        )
                    )
            
            except Exception as e:
                print(f"Error executing improvement: {e}")
                results.append(
                    ImprovementResult(
                        suggestion=suggestion,
                        success=False,
                        changes_made=[],
                        errors=[str(e)],
                        diff=None,
                        metrics_before={},
                        metrics_after={}
                    )
                )
        
        # Generate improvement report
        self._generate_improvement_report(results)
        
        return results
    
    def _track_fixes(self, file_path: str, fixes: List[CodeFix]):
        """Track applied fixes"""
        if file_path not in self.fix_history:
            self.fix_history[file_path] = []
        self.fix_history[file_path].extend(fixes)
        
    def _create_temp_file(self, fix: CodeFix) -> Path:
        """Create a temporary file with the fix"""
        temp_dir = self.project_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(temp_file, 'w') as f:
            f.write(fix.fix_code)
            
        return temp_file
        
    async def _run_tests(self, file_path: Path) -> bool:
        """Run tests for a file"""
        try:
            # Use pytest or other test runner
            result = await self._run_command(f"pytest {file_path}")
            return result.returncode == 0
        except Exception:
            return False
            
    def _check_compilation(self, file_path: Path) -> bool:
        """Check if code compiles"""
        try:
            with open(file_path, 'r') as f:
                ast.parse(f.read())
            return True
        except Exception:
            return False
            
    async def _get_related_files(self, file_path: str) -> List[str]:
        """Get files related to the fix"""
        try:
            # Use dependency analysis
            dependencies = await self.impact_analyzer.get_dependencies(file_path)
            return [dep for dep in dependencies if dep != file_path]
        except Exception:
            return []
            
    def _has_tests(self, file_path: str) -> bool:
        """Check if file has associated tests"""
        test_file = Path(file_path).parent / f"test_{Path(file_path).name}"
        return test_file.exists()
        
    async def _run_command(self, command: str) -> Any:
        """Run a shell command"""
        import asyncio
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await process.communicate()
    
    def _find_target_file(self, suggestion: ImprovementSuggestion) -> Optional[Path]:
        """Find the target file for the improvement"""
        if suggestion.file_path:
            return self.current_dir / suggestion.file_path
        
        # If file path not specified, try to find it based on the suggestion
        if "complexity" in suggestion.description.lower():
            return self._find_complex_file()
        elif "performance" in suggestion.description.lower():
            return self._find_performance_critical_file()
        elif "docstring" in suggestion.description.lower():
            return self._find_file_without_docstring()
        
        return None
    
    def _find_complex_file(self) -> Optional[Path]:
        """Find the most complex file in the codebase"""
        max_complexity = 0
        complex_file = None
        
        for file_path in self.current_dir.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                complexity = self._calculate_complexity(tree)
                
                if complexity > max_complexity:
                    max_complexity = complexity
                    complex_file = file_path
            
            except Exception:
                continue
        
        return complex_file
    
    def _find_performance_critical_file(self) -> Optional[Path]:
        """Find a file with potential performance issues"""
        for file_path in self.current_dir.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                if self._has_performance_issues(tree):
                    return file_path
            
            except Exception:
                continue
        
        return None
    
    def _find_file_without_docstring(self) -> Optional[Path]:
        """Find a file without proper docstrings"""
        for file_path in self.current_dir.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                if not self._has_docstrings(tree):
                    return file_path
            
            except Exception:
                continue
        
        return None
    
    def _improve_code_quality(self, file_path: Path, suggestion: ImprovementSuggestion) -> tuple[List[str], List[str]]:
        """Improve code quality based on suggestion"""
        changes_made = []
        errors = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            if "complexity" in suggestion.description.lower():
                # Break down complex functions
                new_tree = self._refactor_complex_functions(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Refactored complex functions")
            
            elif "style" in suggestion.description.lower():
                # Apply code style improvements
                new_content = self._apply_style_improvements(content)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Applied style improvements")
            
            elif "duplicate" in suggestion.description.lower():
                # Remove duplicate code
                new_tree = self._remove_duplicate_code(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Removed duplicate code")
            
            elif "naming" in suggestion.description.lower():
                # Improve variable and function naming
                new_tree = self._improve_naming(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Improved naming conventions")
        
        except Exception as e:
            errors.append(f"Error improving code quality: {e}")
        
        return changes_made, errors
    
    def _improve_performance(self, file_path: Path, suggestion: ImprovementSuggestion) -> tuple[List[str], List[str]]:
        """Improve performance based on suggestion"""
        changes_made = []
        errors = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            if "loop" in suggestion.description.lower():
                # Optimize loops
                new_tree = self._optimize_loops(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Optimized loops and data structures")
            
            elif "cache" in suggestion.description.lower():
                # Add caching for expensive operations
                new_tree = self._add_caching(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Added caching for expensive operations")
            
            elif "memory" in suggestion.description.lower():
                # Optimize memory usage
                new_tree = self._optimize_memory(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Optimized memory usage")
        
        except Exception as e:
            errors.append(f"Error improving performance: {e}")
        
        return changes_made, errors
    
    def _improve_documentation(self, file_path: Path, suggestion: ImprovementSuggestion) -> tuple[List[str], List[str]]:
        """Improve documentation based on suggestion"""
        changes_made = []
        errors = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            if "docstring" in suggestion.description.lower():
                # Add missing docstrings
                new_tree = self._add_docstrings(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Added missing docstrings")
            
            elif "type" in suggestion.description.lower():
                # Add type hints
                new_tree = self._add_type_hints(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Added type hints")
            
            elif "example" in suggestion.description.lower():
                # Add usage examples
                new_tree = self._add_usage_examples(tree)
                new_content = astor.to_source(new_tree)
                
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                changes_made.append("Added usage examples")
        
        except Exception as e:
            errors.append(f"Error improving documentation: {e}")
        
        return changes_made, errors
    
    def _refactor_complex_functions(self, tree: ast.AST) -> ast.AST:
        """Refactor complex functions into smaller ones"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._calculate_complexity(node) > 10:
                    # Extract complex logic into helper functions
                    new_functions = self._extract_helper_functions(node)
                    for new_func in new_functions:
                        tree.body.append(new_func)
        
        return tree
    
    def _extract_helper_functions(self, node: ast.FunctionDef) -> List[ast.FunctionDef]:
        """Extract complex logic into helper functions"""
        helper_functions = []
        
        # Find complex blocks in the function
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, (ast.If, ast.While, ast.For)):
                if self._calculate_complexity(stmt) > 5:
                    # Create helper function
                    helper_name = f"{node.name}_helper_{i}"
                    helper_func = ast.FunctionDef(
                        name=helper_name,
                        args=node.args,
                        body=[stmt],
                        decorator_list=[],
                        returns=None
                    )
                    helper_functions.append(helper_func)
                    
                    # Replace complex block with function call
                    node.body[i] = ast.Expr(
                        value=ast.Call(
                            func=ast.Name(id=helper_name, ctx=ast.Load()),
                            args=[],
                            keywords=[]
                        )
                    )
        
        return helper_functions
    
    def _optimize_loops(self, tree: ast.AST) -> ast.AST:
        """Optimize loops and data structures"""
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Convert list comprehension to generator expression
                if isinstance(node.iter, ast.ListComp):
                    node.iter = ast.GeneratorExp(
                        elt=node.iter.elt,
                        generators=node.iter.generators
                    )
            
            elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                # Optimize string concatenation
                if isinstance(node.left, ast.Str) or isinstance(node.right, ast.Str):
                    parent = getattr(node, 'parent', None)
                    if isinstance(parent, ast.For):
                        # Use list join instead of string concatenation
                        new_node = ast.Call(
                            func=ast.Attribute(
                                value=ast.List(
                                    elts=[node.left, node.right],
                                    ctx=ast.Load()
                                ),
                                attr="join",
                                ctx=ast.Load()
                            ),
                            args=[ast.Str(s="")],
                            keywords=[]
                        )
                        node = new_node
        
        return tree
    
    def _add_docstrings(self, tree: ast.AST) -> ast.AST:
        """Add missing docstrings to modules, classes, and functions"""
        if isinstance(tree, ast.Module) and not ast.get_docstring(tree):
            tree.body.insert(0, ast.Expr(
                value=ast.Str(s="Module docstring")
            ))
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    docstring = self._generate_docstring(node)
                    node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        
        return tree
    
    def _generate_docstring(self, node: ast.AST) -> str:
        """Generate a docstring for a node"""
        if isinstance(node, ast.ClassDef):
            return f"Class {node.name} documentation"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return f"Function {node.name} documentation"
        return "Documentation"
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of an AST node"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.BoolOp)):
                complexity += 1
        
        return complexity
    
    def _has_performance_issues(self, tree: ast.AST) -> bool:
        """Check if a file has potential performance issues"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                parent = getattr(node, 'parent', None)
                if isinstance(parent, (ast.For, ast.While)):
                    return True
            
            if isinstance(node, ast.ListComp) and len(node.generators) > 2:
                return True
        
        return False
    
    def _has_docstrings(self, tree: ast.AST) -> bool:
        """Check if a file has proper docstrings"""
        has_module_docstring = bool(ast.get_docstring(tree))
        
        has_class_docstrings = all(
            bool(ast.get_docstring(node))
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        )
        
        has_function_docstrings = all(
            bool(ast.get_docstring(node))
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        
        return has_module_docstring and has_class_docstrings and has_function_docstrings
    
    def _generate_diff(self, original: str, new: str) -> str:
        """Generate a diff between original and new content"""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile="original",
            tofile="new"
        )
        return "".join(diff)
    
    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current code metrics"""
        metrics = {}
        
        for file_path in self.current_dir.rglob("*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                metrics[f"{file_path.name}_complexity"] = self._calculate_complexity(tree)
                metrics[f"{file_path.name}_functions"] = len([
                    node for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                ])
            
            except Exception:
                continue
        
        return metrics
    
    def _create_backup(self):
        """Create a backup of the current codebase"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        if self.current_dir.exists():
            shutil.copytree(self.current_dir, backup_path)
    
    def _restore_from_backup(self):
        """Restore the codebase from the latest backup"""
        backup_files = list(self.backup_dir.glob("backup_*"))
        if not backup_files:
            return
        
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        if self.current_dir.exists():
            shutil.rmtree(self.current_dir)
        
        shutil.copytree(latest_backup, self.current_dir)
    
    def _save_improvement_result(self, result: ImprovementResult):
        """Save the result of an improvement"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.improvements_dir / f"improvement_{timestamp}.json"
        
        result_dict = {
            "suggestion": vars(result.suggestion),
            "success": result.success,
            "changes_made": result.changes_made,
            "errors": result.errors,
            "diff": result.diff,
            "metrics_before": result.metrics_before,
            "metrics_after": result.metrics_after,
            "timestamp": timestamp
        }
        
        with open(result_file, 'w') as f:
            json.dump(result_dict, f, indent=2)
    
    def _generate_improvement_report(self, results: List[ImprovementResult]):
        """Generate a report of all improvements"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"improvement_report_{timestamp}.json"
        
        report = {
            "timestamp": timestamp,
            "total_improvements": len(results),
            "successful_improvements": len([r for r in results if r.success]),
            "failed_improvements": len([r for r in results if not r.success]),
            "improvements": [
                {
                    "category": r.suggestion.category,
                    "description": r.suggestion.description,
                    "success": r.success,
                    "changes_made": r.changes_made,
                    "errors": r.errors,
                    "metrics_before": r.metrics_before,
                    "metrics_after": r.metrics_after
                }
                for r in results
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _remove_duplicate_code(self, tree: ast.AST) -> ast.AST:
        """Remove duplicate code by extracting common patterns"""
        # Find similar function bodies
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                if self._are_functions_similar(func1, func2):
                    # Extract common code into a helper function
                    helper_name = f"common_{func1.name}_{func2.name}"
                    helper_func = self._create_helper_function(func1, func2)
                    
                    # Add helper function to module
                    tree.body.append(helper_func)
                    
                    # Update original functions to use helper
                    self._update_functions_to_use_helper(func1, func2, helper_name)
        
        return tree
    
    def _are_functions_similar(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> bool:
        """Check if two functions have similar bodies"""
        # Convert function bodies to strings for comparison
        body1 = astor.to_source(func1.body)
        body2 = astor.to_source(func2.body)
        
        # Calculate similarity ratio
        ratio = difflib.SequenceMatcher(None, body1, body2).ratio()
        return ratio > 0.8  # 80% similarity threshold
    
    def _create_helper_function(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> ast.FunctionDef:
        """Create a helper function from similar code"""
        # Find common parameters
        common_params = self._find_common_parameters(func1, func2)
        
        # Create helper function
        helper_func = ast.FunctionDef(
            name=f"common_{func1.name}_{func2.name}",
            args=ast.arguments(
                args=[ast.arg(arg=param, annotation=None) for param in common_params],
                defaults=[],
                kwonlyargs=[],
                kw_defaults=[],
                posonlyargs=[]
            ),
            body=self._extract_common_code(func1, func2),
            decorator_list=[],
            returns=None
        )
        
        return helper_func
    
    def _find_common_parameters(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> List[str]:
        """Find common parameters between two functions"""
        params1 = [arg.arg for arg in func1.args.args]
        params2 = [arg.arg for arg in func2.args.args]
        return list(set(params1) & set(params2))
    
    def _extract_common_code(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> List[ast.AST]:
        """Extract common code between two functions"""
        # Convert function bodies to strings
        body1 = astor.to_source(func1.body)
        body2 = astor.to_source(func2.body)
        
        # Find common subsequences
        matcher = difflib.SequenceMatcher(None, body1, body2)
        common_blocks = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                common_blocks.append(body1[i1:i2])
        
        # Parse common blocks back to AST
        common_ast = []
        for block in common_blocks:
            try:
                block_ast = ast.parse(block)
                common_ast.extend(block_ast.body)
            except Exception:
                continue
        
        return common_ast
    
    def _update_functions_to_use_helper(self, func1: ast.FunctionDef, func2: ast.FunctionDef, helper_name: str):
        """Update functions to use the helper function"""
        # Create call to helper function
        helper_call = ast.Expr(
            value=ast.Call(
                func=ast.Name(id=helper_name, ctx=ast.Load()),
                args=[ast.Name(id=arg.arg, ctx=ast.Load()) for arg in func1.args.args],
                keywords=[]
            )
        )
        
        # Update function bodies
        func1.body = [helper_call]
        func2.body = [helper_call]
    
    def _improve_naming(self, tree: ast.AST) -> ast.AST:
        """Improve variable and function naming"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Improve function names
                if not self._is_descriptive_name(node.name):
                    node.name = self._generate_descriptive_name(node)
            
            elif isinstance(node, ast.Name):
                # Improve variable names
                if not self._is_descriptive_name(node.id):
                    node.id = self._generate_variable_name(node)
        
        return tree
    
    def _is_descriptive_name(self, name: str) -> bool:
        """Check if a name is descriptive enough"""
        # Check if name contains multiple words
        if not any(c.isupper() for c in name) and '_' not in name:
            return False
        
        # Check if name is too short
        if len(name) < 4:
            return False
        
        # Check if name is too generic
        generic_names = {'data', 'value', 'result', 'temp', 'var', 'x', 'y', 'z'}
        if name.lower() in generic_names:
            return False
        
        return True
    
    def _generate_descriptive_name(self, node: ast.FunctionDef) -> str:
        """Generate a descriptive name for a function"""
        # Analyze function body to understand its purpose
        purpose = self._analyze_function_purpose(node)
        
        # Generate name based on purpose
        if purpose == "get":
            return f"get_{self._get_primary_object(node)}"
        elif purpose == "set":
            return f"set_{self._get_primary_object(node)}"
        elif purpose == "process":
            return f"process_{self._get_primary_object(node)}"
        else:
            return f"handle_{self._get_primary_object(node)}"
    
    def _generate_variable_name(self, node: ast.Name) -> str:
        """Generate a descriptive name for a variable"""
        # Analyze variable usage context
        context = self._analyze_variable_context(node)
        
        # Generate name based on context
        if context == "counter":
            return "item_count"
        elif context == "result":
            return "processed_result"
        elif context == "flag":
            return "is_valid"
        else:
            return f"processed_{node.id}"
    
    def _analyze_function_purpose(self, node: ast.FunctionDef) -> str:
        """Analyze the purpose of a function"""
        # Check for common patterns
        if any(isinstance(stmt, ast.Return) for stmt in ast.walk(node)):
            return "get"
        elif any(isinstance(stmt, ast.Assign) for stmt in ast.walk(node)):
            return "set"
        elif any(isinstance(stmt, (ast.For, ast.While)) for stmt in ast.walk(node)):
            return "process"
        else:
            return "handle"
    
    def _get_primary_object(self, node: ast.FunctionDef) -> str:
        """Get the primary object a function operates on"""
        # Look for object references in function body
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                return child.id
        return "object"
    
    def _analyze_variable_context(self, node: ast.Name) -> str:
        """Analyze the context of a variable"""
        # Look for common patterns in variable usage
        parent = getattr(node, 'parent', None)
        if isinstance(parent, ast.For):
            return "counter"
        elif isinstance(parent, ast.Assign):
            return "result"
        elif isinstance(parent, ast.If):
            return "flag"
        else:
            return "unknown"
    
    def _add_caching(self, tree: ast.AST) -> ast.AST:
        """Add caching for expensive operations"""
        # Find expensive operations (loops, function calls)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._is_expensive_operation(node):
                    # Add caching decorator
                    node.decorator_list.append(
                        ast.Name(id='lru_cache', ctx=ast.Load())
                    )
        
        return tree
    
    def _is_expensive_operation(self, node: ast.FunctionDef) -> bool:
        """Check if a function performs expensive operations"""
        # Look for expensive patterns
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                return True
            elif isinstance(child, ast.Call):
                # Check for known expensive functions
                if isinstance(child.func, ast.Name):
                    if child.func.id in {'sum', 'max', 'min', 'sorted', 'filter', 'map'}:
                        return True
        
        return False
    
    def _optimize_memory(self, tree: ast.AST) -> ast.AST:
        """Optimize memory usage"""
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                # Convert large lists to generators
                if len(node.elts) > 100:
                    node = ast.GeneratorExp(
                        elt=node.elts[0],
                        generators=[
                            ast.comprehension(
                                target=ast.Name(id='item', ctx=ast.Store()),
                                iter=ast.Call(
                                    func=ast.Name(id='range', ctx=ast.Load()),
                                    args=[ast.Num(n=len(node.elts))],
                                    keywords=[]
                                ),
                                ifs=[],
                                is_async=0
                            )
                        ]
                    )
            
            elif isinstance(node, ast.Dict):
                # Use dict comprehension for large dictionaries
                if len(node.keys) > 100:
                    node = ast.DictComp(
                        key=node.keys[0],
                        value=node.values[0],
                        generators=[
                            ast.comprehension(
                                target=ast.Name(id='key', ctx=ast.Store()),
                                iter=ast.Call(
                                    func=ast.Name(id='range', ctx=ast.Load()),
                                    args=[ast.Num(n=len(node.keys))],
                                    keywords=[]
                                ),
                                ifs=[],
                                is_async=0
                            )
                        ]
                    )
        
        return tree
    
    def _add_type_hints(self, tree: ast.AST) -> ast.AST:
        """Add type hints to functions and variables"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Add return type annotation
                if not node.returns:
                    node.returns = ast.Name(id='Any', ctx=ast.Load())
                
                # Add parameter type annotations
                for arg in node.args.args:
                    if not arg.annotation:
                        arg.annotation = self._infer_type(arg)
            
            elif isinstance(node, ast.AnnAssign):
                # Add type annotation to variable assignments
                if not node.annotation:
                    node.annotation = self._infer_type(node.target)
        
        return tree
    
    def _infer_type(self, node: ast.AST) -> ast.AST:
        """Infer type for a node"""
        if isinstance(node, ast.Name):
            # Infer type based on variable name
            if node.id.startswith('is_'):
                return ast.Name(id='bool', ctx=ast.Load())
            elif node.id.endswith('_list'):
                return ast.Subscript(
                    value=ast.Name(id='List', ctx=ast.Load()),
                    slice=ast.Name(id='Any', ctx=ast.Load()),
                    ctx=ast.Load()
                )
            elif node.id.endswith('_dict'):
                return ast.Subscript(
                    value=ast.Name(id='Dict', ctx=ast.Load()),
                    slice=ast.Tuple(
                        elts=[
                            ast.Name(id='str', ctx=ast.Load()),
                            ast.Name(id='Any', ctx=ast.Load())
                        ],
                        ctx=ast.Load()
                    ),
                    ctx=ast.Load()
                )
        
        return ast.Name(id='Any', ctx=ast.Load())
    
    def _add_usage_examples(self, tree: ast.AST) -> ast.AST:
        """Add usage examples to docstrings"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    # Create docstring with example
                    example = self._generate_usage_example(node)
                    docstring = f'"""\n{node.name} function.\n\nExample:\n{example}\n"""'
                    node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        
        return tree
    
    def _generate_usage_example(self, node: ast.FunctionDef) -> str:
        """Generate a usage example for a function"""
        # Get parameter names
        params = [arg.arg for arg in node.args.args]
        
        # Generate example values
        example_values = {
            'str': '"example"',
            'int': '42',
            'float': '3.14',
            'bool': 'True',
            'list': '[1, 2, 3]',
            'dict': '{"key": "value"}'
        }
        
        # Create example call
        example_params = []
        for param in params:
            param_type = self._infer_type(ast.Name(id=param, ctx=ast.Store()))
            if isinstance(param_type, ast.Name):
                example_params.append(example_values.get(param_type.id, 'None'))
            else:
                example_params.append('None')
        
        return f"{node.name}({', '.join(example_params)})"

def main():
    """Main entry point for the executor"""
    import asyncio
    
    project_dir = os.getenv("ADE_PROJECT_DIR")
    if not project_dir:
        print("Error: ADE_PROJECT_DIR environment variable not set")
        return
    
    executor = ImprovementExecutor(project_dir)
    
    # Load latest suggestions
    suggestions_dir = Path(project_dir) / "improvements"
    suggestion_files = list(suggestions_dir.glob("suggestions_*.json"))
    if not suggestion_files:
        print("No improvement suggestions found")
        return
    
    latest_suggestions = max(suggestion_files, key=lambda x: x.stat().st_mtime)
    with open(latest_suggestions) as f:
        suggestions_data = json.load(f)
    
    suggestions = [
        ImprovementSuggestion(**data)
        for data in suggestions_data
    ]
    
    print(f"Executing {len(suggestions)} improvements...")
    
    async def run_improvements():
        results = []
        for suggestion in suggestions:
            result = await executor._execute_single_improvement(suggestion)
            results.append(result)
        return results
    
    results = asyncio.run(run_improvements())
    
    print("\nImprovement Results:")
    for result in results:
        status = "Success" if result.success else "Failed"
        print(f"- {result.suggestion.description}: {status}")
        if result.errors:
            print(f"  Errors: {', '.join(result.errors)}")
        if result.fixes_applied:
            print(f"  Applied Fixes: {len(result.fixes_applied)}")
            for fix in result.fixes_applied:
                print(f"    - {fix.description} (Confidence: {fix.confidence:.2f})")

if __name__ == "__main__":
    main() 