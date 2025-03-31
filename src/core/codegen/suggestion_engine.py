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

logger = logging.getLogger(__name__)

class CodeContext(TypedDict):
    """Context information for code analysis"""
    file_path: str
    language: str
    framework: Optional[str]
    imports: List[str]
    classes: List[str]
    functions: List[str]
    variables: List[str]
    dependencies: List[str]
    patterns: List[str]
    style: Dict[str, str]

class SuggestionEngine:
    """Engine for generating context-aware code suggestions"""
    
    def __init__(self, template_manager: TemplateManager, language_generator: LanguageGenerator):
        self.template_manager = template_manager
        self.language_generator = language_generator
        self._load_config()
        self._setup_engine()
        self._context_cache = {}
        
    def _load_config(self) -> None:
        """Load suggestion engine configuration"""
        try:
            config_path = Path("src/core/codegen/config/suggestions.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.warning("Suggestion configuration not found")
                self.config = {}
                
        except Exception as e:
            logger.error(f"Error loading suggestion configuration: {str(e)}")
            self.config = {}
            
    def _setup_engine(self) -> None:
        """Setup suggestion engine"""
        try:
            # Load suggestion patterns
            self._load_suggestion_patterns()
            
            # Load best practices
            self._load_best_practices()
            
            # Load code smells
            self._load_code_smells()
            
        except Exception as e:
            logger.error(f"Error setting up suggestion engine: {str(e)}")
            
    def _load_suggestion_patterns(self) -> None:
        """Load patterns for code suggestions"""
        try:
            patterns_dir = Path("src/core/codegen/patterns")
            self.suggestion_patterns = defaultdict(list)
            
            for pattern_file in patterns_dir.glob("*.json"):
                with open(pattern_file, "r") as f:
                    patterns = json.load(f)
                    self.suggestion_patterns[pattern_file.stem] = patterns
                    
        except Exception as e:
            logger.error(f"Error loading suggestion patterns: {str(e)}")
            self.suggestion_patterns = defaultdict(list)
            
    def _load_best_practices(self) -> None:
        """Load best practices for different languages and frameworks"""
        try:
            practices_dir = Path("src/core/codegen/practices")
            self.best_practices = defaultdict(dict)
            
            for practice_file in practices_dir.glob("*.yaml"):
                with open(practice_file, "r") as f:
                    practices = yaml.safe_load(f)
                    self.best_practices[practice_file.stem] = practices
                    
        except Exception as e:
            logger.error(f"Error loading best practices: {str(e)}")
            self.best_practices = defaultdict(dict)
            
    def _load_code_smells(self) -> None:
        """Load code smell patterns and resolutions"""
        try:
            smells_dir = Path("src/core/codegen/smells")
            self.code_smells = defaultdict(list)
            
            for smell_file in smells_dir.glob("*.json"):
                with open(smell_file, "r") as f:
                    smells = json.load(f)
                    self.code_smells[smell_file.stem] = smells
                    
        except Exception as e:
            logger.error(f"Error loading code smells: {str(e)}")
            self.code_smells = defaultdict(list)
            
    def analyze_context(self, code: str, language: str, file_path: str) -> CodeContext:
        """Analyze code context for better suggestions"""
        try:
            # Parse code based on language
            if language == "python":
                context = self._analyze_python_context(code)
            elif language == "java":
                context = self._analyze_java_context(code)
            else:
                context = self._analyze_generic_context(code)
                
            # Add file information
            context["file_path"] = file_path
            context["language"] = language
            
            # Cache context
            self._context_cache[file_path] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing code context: {str(e)}")
            return {}
            
    def _analyze_python_context(self, code: str) -> CodeContext:
        """Analyze Python code context"""
        try:
            tree = ast.parse(code)
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
                    
            # Extract classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    
            # Extract functions
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    
            # Extract variables
            variables = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append(target.id)
                            
            return {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "variables": variables,
                "dependencies": self._extract_dependencies(imports),
                "patterns": self._detect_patterns(code),
                "style": self._analyze_style(code)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Python context: {str(e)}")
            return {}
            
    def _analyze_java_context(self, code: str) -> CodeContext:
        """Analyze Java code context"""
        try:
            tree = javalang.parse.parse(code)
            
            # Extract imports
            imports = [imp.path for imp in tree.imports]
            
            # Extract classes
            classes = [type_decl.name for type_decl in tree.types]
            
            # Extract methods
            methods = []
            for type_decl in tree.types:
                methods.extend(method.name for method in type_decl.methods)
                
            # Extract variables
            variables = []
            for type_decl in tree.types:
                variables.extend(field.name for field in type_decl.fields)
                
            return {
                "imports": imports,
                "classes": classes,
                "functions": methods,
                "variables": variables,
                "dependencies": self._extract_dependencies(imports),
                "patterns": self._detect_patterns(code),
                "style": self._analyze_style(code)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Java context: {str(e)}")
            return {}
            
    def _analyze_generic_context(self, code: str) -> CodeContext:
        """Analyze generic code context"""
        try:
            # Extract imports
            imports = re.findall(r'import\s+([^;]+)', code)
            
            # Extract classes
            classes = re.findall(r'class\s+(\w+)', code)
            
            # Extract functions
            functions = re.findall(r'function\s+(\w+)', code)
            
            # Extract variables
            variables = re.findall(r'var\s+(\w+)', code)
            
            return {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "variables": variables,
                "dependencies": self._extract_dependencies(imports),
                "patterns": self._detect_patterns(code),
                "style": self._analyze_style(code)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing generic context: {str(e)}")
            return {}
            
    def _extract_dependencies(self, imports: List[str]) -> List[str]:
        """Extract dependencies from imports"""
        try:
            dependencies = []
            
            for imp in imports:
                # Split import path
                parts = imp.split('.')
                
                # Add main package
                if parts:
                    dependencies.append(parts[0])
                    
                # Add framework packages
                if len(parts) > 1:
                    if parts[0] in ['react', 'vue', 'angular', 'django', 'flask', 'spring']:
                        dependencies.append(parts[0])
                        
            return list(set(dependencies))
            
        except Exception as e:
            logger.error(f"Error extracting dependencies: {str(e)}")
            return []
            
    def _detect_patterns(self, code: str) -> List[str]:
        """Detect design patterns in code"""
        try:
            patterns = []
            
            # Singleton pattern
            if re.search(r'private\s+static\s+\w+\s+instance', code):
                patterns.append("singleton")
                
            # Factory pattern
            if re.search(r'create\w+\([^)]*\)\s*{', code):
                patterns.append("factory")
                
            # Observer pattern
            if re.search(r'addEventListener|on\([^)]+\)', code):
                patterns.append("observer")
                
            # Strategy pattern
            if re.search(r'implements\s+\w+Strategy', code):
                patterns.append("strategy")
                
            # MVC pattern
            if re.search(r'class\s+\w+Controller|class\s+\w+Model|class\s+\w+View', code):
                patterns.append("mvc")
                
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {str(e)}")
            return []
            
    def _analyze_style(self, code: str) -> Dict[str, str]:
        """Analyze code style"""
        try:
            style = {}
            
            # Indentation style
            if re.search(r'^\s{4}', code, re.MULTILINE):
                style["indent"] = "spaces"
            elif re.search(r'^\t', code, re.MULTILINE):
                style["indent"] = "tabs"
                
            # Quote style
            if re.search(r"'[^']*'", code):
                style["quotes"] = "single"
            elif re.search(r'"[^"]*"', code):
                style["quotes"] = "double"
                
            # Brace style
            if re.search(r'{\s*$', code, re.MULTILINE):
                style["braces"] = "end_of_line"
            elif re.search(r'$\s*{', code, re.MULTILINE):
                style["braces"] = "next_line"
                
            return style
            
        except Exception as e:
            logger.error(f"Error analyzing style: {str(e)}")
            return {}
            
    def get_suggestions(self, code: str, language: str, file_path: str) -> List[Dict]:
        """Get context-aware code suggestions"""
        try:
            # Analyze context
            context = self.analyze_context(code, language, file_path)
            
            suggestions = []
            
            # Get language-specific suggestions
            lang_suggestions = self.language_generator.get_code_suggestions(language, code)
            suggestions.extend(lang_suggestions)
            
            # Get pattern-based suggestions
            pattern_suggestions = self._get_pattern_suggestions(context)
            suggestions.extend(pattern_suggestions)
            
            # Get best practice suggestions
            practice_suggestions = self._get_best_practice_suggestions(context)
            suggestions.extend(practice_suggestions)
            
            # Get code smell suggestions
            smell_suggestions = self._get_code_smell_suggestions(code, language)
            suggestions.extend(smell_suggestions)
            
            # Sort suggestions by priority
            suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
            
    def _get_pattern_suggestions(self, context: CodeContext) -> List[Dict]:
        """Get suggestions based on detected patterns"""
        try:
            suggestions = []
            
            # Get patterns for language
            patterns = self.suggestion_patterns.get(context["language"], [])
            
            # Check each pattern
            for pattern in patterns:
                if pattern["name"] in context["patterns"]:
                    suggestions.append({
                        "type": "pattern",
                        "pattern": pattern["name"],
                        "description": pattern["description"],
                        "code": pattern["suggestion"],
                        "priority": pattern.get("priority", 0)
                    })
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting pattern suggestions: {str(e)}")
            return []
            
    def _get_best_practice_suggestions(self, context: CodeContext) -> List[Dict]:
        """Get suggestions based on best practices"""
        try:
            suggestions = []
            
            # Get best practices for language
            practices = self.best_practices.get(context["language"], {})
            
            # Check each practice
            for practice, rule in practices.items():
                if not self._check_best_practice(context, practice, rule):
                    suggestions.append({
                        "type": "best_practice",
                        "practice": practice,
                        "description": rule["description"],
                        "code": rule["example"],
                        "priority": rule.get("priority", 0)
                    })
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting best practice suggestions: {str(e)}")
            return []
            
    def _get_code_smell_suggestions(self, code: str, language: str) -> List[Dict]:
        """Get suggestions for code smells"""
        try:
            suggestions = []
            
            # Get code smells for language
            smells = self.code_smells.get(language, [])
            
            # Check each smell
            for smell in smells:
                if re.search(smell["pattern"], code):
                    suggestions.append({
                        "type": "code_smell",
                        "smell": smell["name"],
                        "description": smell["description"],
                        "code": smell["resolution"],
                        "priority": smell.get("priority", 0)
                    })
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting code smell suggestions: {str(e)}")
            return []
            
    def _check_best_practice(self, context: CodeContext, practice: str, rule: Dict) -> bool:
        """Check if code follows a best practice"""
        try:
            if practice == "naming_convention":
                return self._check_naming_convention(context, rule)
            elif practice == "error_handling":
                return self._check_error_handling(context, rule)
            elif practice == "documentation":
                return self._check_documentation(context, rule)
            # Add more practice checks as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking best practice {practice}: {str(e)}")
            return True
            
    def _check_naming_convention(self, context: CodeContext, rule: Dict) -> bool:
        """Check if code follows naming convention"""
        try:
            convention = rule.get("convention", "camelCase")
            
            if convention == "camelCase":
                pattern = r'[a-z][a-zA-Z0-9]*'
            elif convention == "snake_case":
                pattern = r'[a-z][a-z0-9_]*'
            elif convention == "PascalCase":
                pattern = r'[A-Z][a-zA-Z0-9]*'
                
            for name in context["variables"] + context["functions"]:
                if not re.match(pattern, name):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking naming convention: {str(e)}")
            return True
            
    def _check_error_handling(self, context: CodeContext, rule: Dict) -> bool:
        """Check if code has proper error handling"""
        try:
            # Check for try-catch blocks
            if not re.search(r'try\s*{|catch\s*\([^)]+\)\s*{', context.get("code", "")):
                return False
                
            # Check for error logging
            if not re.search(r'logger\.error|console\.error', context.get("code", "")):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking error handling: {str(e)}")
            return True
            
    def _check_documentation(self, context: CodeContext, rule: Dict) -> bool:
        """Check if code has proper documentation"""
        try:
            # Check for function documentation
            for func in context["functions"]:
                if not re.search(rf'def\s+{func}\s*\([^)]*\)\s*:.*?""".*?"""', context.get("code", "")):
                    return False
                    
            # Check for class documentation
            for cls in context["classes"]:
                if not re.search(rf'class\s+{cls}\s*:.*?""".*?"""', context.get("code", "")):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error checking documentation: {str(e)}")
            return True 