from typing import Dict, List, Optional, Set
import logging
from pathlib import Path
import json
import yaml
from dataclasses import dataclass
import re
from collections import defaultdict
import ast
import javalang
from typing_extensions import TypedDict

from .template_manager import TemplateManager
from .language_generator import LanguageGenerator
from .suggestion_engine import SuggestionEngine, CodeContext

logger = logging.getLogger(__name__)

class QualityMetrics(TypedDict):
    """Metrics for code quality analysis"""
    complexity: int
    maintainability: float
    reliability: float
    security: float
    performance: float
    testability: float
    reusability: float
    readability: float

class QualityAnalyzer:
    """Analyzes code quality and provides optimization suggestions"""
    
    def __init__(self, template_manager: TemplateManager, 
                 language_generator: LanguageGenerator,
                 suggestion_engine: SuggestionEngine):
        self.template_manager = template_manager
        self.language_generator = language_generator
        self.suggestion_engine = suggestion_engine
        self._load_config()
        self._setup_analyzer()
        
    def _load_config(self) -> None:
        """Load quality analyzer configuration"""
        try:
            config_path = Path("src/core/codegen/config/quality.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Quality configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading quality configuration: {str(e)}")
            self.config = {}
            
    def _setup_analyzer(self) -> None:
        """Setup quality analyzer"""
        try:
            # Load quality rules
            self._load_quality_rules()
            
            # Load optimization patterns
            self._load_optimization_patterns()
            
            # Load security rules
            self._load_security_rules()
            
        except Exception as e:
            logger.error(f"Error setting up quality analyzer: {str(e)}")
            
    def _load_quality_rules(self) -> None:
        """Load quality analysis rules"""
        try:
            rules_dir = Path("src/core/codegen/rules")
            self.quality_rules = defaultdict(list)
            
            for rule_file in rules_dir.glob("*.yaml"):
                with open(rule_file, "r") as f:
                    rules = yaml.safe_load(f)
                    self.quality_rules[rule_file.stem] = rules
                    
        except Exception as e:
            logger.error(f"Error loading quality rules: {str(e)}")
            self.quality_rules = defaultdict(list)
            
    def _load_optimization_patterns(self) -> None:
        """Load code optimization patterns"""
        try:
            patterns_dir = Path("src/core/codegen/optimizations")
            self.optimization_patterns = defaultdict(list)
            
            for pattern_file in patterns_dir.glob("*.json"):
                with open(pattern_file, "r") as f:
                    patterns = json.load(f)
                    self.optimization_patterns[pattern_file.stem] = patterns
                    
        except Exception as e:
            logger.error(f"Error loading optimization patterns: {str(e)}")
            self.optimization_patterns = defaultdict(list)
            
    def _load_security_rules(self) -> None:
        """Load security analysis rules"""
        try:
            rules_dir = Path("src/core/codegen/security")
            self.security_rules = defaultdict(list)
            
            for rule_file in rules_dir.glob("*.yaml"):
                with open(rule_file, "r") as f:
                    rules = yaml.safe_load(f)
                    self.security_rules[rule_file.stem] = rules
                    
        except Exception as e:
            logger.error(f"Error loading security rules: {str(e)}")
            self.security_rules = defaultdict(list)
            
    def analyze_code(self, code: str, language: str, file_path: str) -> Dict:
        """Analyze code quality and provide optimization suggestions"""
        try:
            # Get code context
            context = self.suggestion_engine.analyze_context(code, language, file_path)
            
            # Calculate quality metrics
            metrics = self._calculate_quality_metrics(code, language)
            
            # Get optimization suggestions
            optimizations = self._get_optimization_suggestions(code, language, context)
            
            # Get security issues
            security_issues = self._analyze_security(code, language)
            
            # Get code smells
            code_smells = self._detect_code_smells(code, language)
            
            return {
                "metrics": metrics,
                "optimizations": optimizations,
                "security_issues": security_issues,
                "code_smells": code_smells,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {}
            
    def _calculate_quality_metrics(self, code: str, language: str) -> QualityMetrics:
        """Calculate code quality metrics"""
        try:
            metrics = {
                "complexity": self._calculate_complexity(code, language),
                "maintainability": self._calculate_maintainability(code, language),
                "reliability": self._calculate_reliability(code, language),
                "security": self._calculate_security_score(code, language),
                "performance": self._calculate_performance_score(code, language),
                "testability": self._calculate_testability(code, language),
                "reusability": self._calculate_reusability(code, language),
                "readability": self._calculate_readability(code, language)
            }
            
            return QualityMetrics(**metrics)
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return QualityMetrics(
                complexity=0,
                maintainability=0.0,
                reliability=0.0,
                security=0.0,
                performance=0.0,
                testability=0.0,
                reusability=0.0,
                readability=0.0
            )
            
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate code complexity"""
        try:
            complexity = 0
            
            if language == "python":
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                      ast.AsyncWith, ast.ExceptHandler, ast.BoolOp)):
                        complexity += 1
            elif language == "java":
                tree = javalang.parse.parse(code)
                for node in tree.filter(javalang.tree.IfStatement):
                    complexity += 1
                for node in tree.filter(javalang.tree.WhileStatement):
                    complexity += 1
                for node in tree.filter(javalang.tree.ForStatement):
                    complexity += 1
                for node in tree.filter(javalang.tree.CatchClause):
                    complexity += 1
                    
            return complexity
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {str(e)}")
            return 0
            
    def _calculate_maintainability(self, code: str, language: str) -> float:
        """Calculate code maintainability score"""
        try:
            score = 1.0
            
            # Check code length
            if len(code.splitlines()) > 1000:
                score *= 0.8
                
            # Check function length
            if language == "python":
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.body) > 20:
                            score *= 0.9
            elif language == "java":
                tree = javalang.parse.parse(code)
                for node in tree.filter(javalang.tree.MethodDeclaration):
                    if len(node.body) > 20:
                        score *= 0.9
                        
            # Check comment ratio
            comment_lines = len(re.findall(r'^\s*#|^\s*//|^\s*/\*', code, re.MULTILINE))
            total_lines = len(code.splitlines())
            if total_lines > 0 and comment_lines / total_lines < 0.1:
                score *= 0.9
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating maintainability: {str(e)}")
            return 0.0
            
    def _calculate_reliability(self, code: str, language: str) -> float:
        """Calculate code reliability score"""
        try:
            score = 1.0
            
            # Check error handling
            if not re.search(r'try\s*{|catch\s*\([^)]+\)\s*{', code):
                score *= 0.8
                
            # Check null checks
            if re.search(r'null\.|undefined\.', code):
                score *= 0.9
                
            # Check type safety
            if language == "typescript" and not re.search(r':\s*\w+', code):
                score *= 0.9
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating reliability: {str(e)}")
            return 0.0
            
    def _calculate_security_score(self, code: str, language: str) -> float:
        """Calculate code security score"""
        try:
            score = 1.0
            
            # Check for hardcoded credentials
            if re.search(r'password\s*=\s*["\'].*["\']', code):
                score *= 0.5
                
            # Check for SQL injection
            if re.search(r'execute\s*\(\s*[\w\s]+\s*\+\s*[\w\s]+\s*\)', code):
                score *= 0.7
                
            # Check for XSS vulnerabilities
            if re.search(r'innerHTML\s*=\s*[\w\s]+\s*\+\s*[\w\s]+', code):
                score *= 0.8
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating security score: {str(e)}")
            return 0.0
            
    def _calculate_performance_score(self, code: str, language: str) -> float:
        """Calculate code performance score"""
        try:
            score = 1.0
            
            # Check for nested loops
            if re.search(r'for\s*\([^)]+\)\s*{\s*for\s*\([^)]+\)\s*{', code):
                score *= 0.9
                
            # Check for inefficient data structures
            if re.search(r'ArrayList\s*<\s*String\s*>', code):
                score *= 0.9
                
            # Check for memory leaks
            if re.search(r'new\s+\w+\s*\(\s*\)\s*;', code):
                score *= 0.9
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.0
            
    def _calculate_testability(self, code: str, language: str) -> float:
        """Calculate code testability score"""
        try:
            score = 1.0
            
            # Check for dependencies
            if re.search(r'new\s+\w+\s*\(\s*\)', code):
                score *= 0.9
                
            # Check for static methods
            if re.search(r'static\s+\w+\s+\w+\s*\(', code):
                score *= 0.9
                
            # Check for global state
            if re.search(r'global\s+\w+', code):
                score *= 0.8
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating testability: {str(e)}")
            return 0.0
            
    def _calculate_reusability(self, code: str, language: str) -> float:
        """Calculate code reusability score"""
        try:
            score = 1.0
            
            # Check for inheritance
            if re.search(r'extends\s+\w+', code):
                score *= 1.1
                
            # Check for interfaces
            if re.search(r'implements\s+\w+', code):
                score *= 1.1
                
            # Check for composition
            if re.search(r'private\s+\w+\s+\w+;', code):
                score *= 1.1
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating reusability: {str(e)}")
            return 0.0
            
    def _calculate_readability(self, code: str, language: str) -> float:
        """Calculate code readability score"""
        try:
            score = 1.0
            
            # Check line length
            for line in code.splitlines():
                if len(line) > 100:
                    score *= 0.9
                    
            # Check naming conventions
            if language == "python":
                if not re.search(r'def\s+[a-z_][a-z0-9_]*\s*\(', code):
                    score *= 0.9
            elif language == "java":
                if not re.search(r'public\s+\w+\s+[a-z][a-zA-Z0-9]*\s*\(', code):
                    score *= 0.9
                    
            # Check comment quality
            if re.search(r'# TODO|# FIXME', code):
                score *= 0.9
                
            return score
            
        except Exception as e:
            logger.error(f"Error calculating readability: {str(e)}")
            return 0.0
            
    def _get_optimization_suggestions(self, code: str, language: str, context: CodeContext) -> List[Dict]:
        """Get code optimization suggestions"""
        try:
            suggestions = []
            
            # Get language-specific optimizations
            patterns = self.optimization_patterns.get(language, [])
            
            # Check each pattern
            for pattern in patterns:
                if re.search(pattern["regex"], code):
                    suggestions.append({
                        "type": "optimization",
                        "pattern": pattern["name"],
                        "description": pattern["description"],
                        "code": pattern["suggestion"],
                        "priority": pattern.get("priority", 0)
                    })
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {str(e)}")
            return []
            
    def _analyze_security(self, code: str, language: str) -> List[Dict]:
        """Analyze code for security issues"""
        try:
            issues = []
            
            # Get security rules for language
            rules = self.security_rules.get(language, [])
            
            # Check each rule
            for rule in rules:
                if re.search(rule["pattern"], code):
                    issues.append({
                        "type": "security",
                        "rule": rule["name"],
                        "description": rule["description"],
                        "severity": rule.get("severity", "medium"),
                        "fix": rule.get("fix", "")
                    })
                    
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing security: {str(e)}")
            return []
            
    def _detect_code_smells(self, code: str, language: str) -> List[Dict]:
        """Detect code smells"""
        try:
            smells = []
            
            # Get quality rules for language
            rules = self.quality_rules.get(language, [])
            
            # Check each rule
            for rule in rules:
                if re.search(rule["pattern"], code):
                    smells.append({
                        "type": "code_smell",
                        "name": rule["name"],
                        "description": rule["description"],
                        "severity": rule.get("severity", "medium"),
                        "fix": rule.get("fix", "")
                    })
                    
            return smells
            
        except Exception as e:
            logger.error(f"Error detecting code smells: {str(e)}")
            return [] 