"""Enhanced code understanding capabilities for the ADE platform."""

from typing import Dict, List, Any, Optional, Set, Tuple, Union
import tree_sitter
from dataclasses import dataclass
from pathlib import Path
import networkx as nx
from collections import defaultdict
import re
import ast
from typing_extensions import TypeAlias
import json
import logging

@dataclass
class LanguageConfig:
    """Configuration for language-specific analysis."""
    name: str
    file_extensions: List[str]
    parser_name: str
    keywords: List[str]
    builtin_types: List[str]
    security_patterns: Dict[str, List[str]]
    performance_patterns: Dict[str, List[str]]
    style_patterns: Dict[str, List[str]]
    complexity_patterns: Dict[str, List[str]]

@dataclass
class CodeEntity:
    """Represents a code entity (class, function, variable, etc.)"""
    name: str
    type: str
    file_path: str
    line_number: int
    scope: str
    dependencies: List[str]
    references: List[str]
    docstring: Optional[str] = None
    complexity: Optional[int] = None
    maintainability: Optional[float] = None
    test_coverage: Optional[float] = None
    security_score: Optional[float] = None
    performance_impact: Optional[float] = None
    language: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class EnhancedCodeUnderstanding:
    """Enhanced code understanding system with comprehensive AST analysis and dependency tracking."""
    
    def __init__(self):
        self.ast_parser = tree_sitter.Parser()
        self.dependency_graph = nx.DiGraph()
        self.symbol_table = {}
        self.context_manager = {}
        self.file_entities = defaultdict(list)
        self.code_metrics = {}
        self.language_configs = self._load_language_configs()
        self.logger = logging.getLogger(__name__)
        
    def _load_language_configs(self) -> Dict[str, LanguageConfig]:
        """Load language-specific configurations."""
        configs = {}
        
        # Python configuration
        configs['python'] = LanguageConfig(
            name='Python',
            file_extensions=['.py'],
            parser_name='python',
            keywords=['def', 'class', 'import', 'from', 'return', 'yield', 'raise', 'try', 'except', 'finally', 'with', 'async', 'await'],
            builtin_types=['int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple', 'object'],
            security_patterns={
                'sql_injection': [
                    r'execute\(.*\+.*\)',
                    r'executemany\(.*\+.*\)',
                    r'cursor\.execute\(.*\+.*\)',
                    r'\.execute\(.*%s.*\)',
                    r'\.execute\(.*\?.*\)',
                    r'\.execute\(.*\{.*\}.*\)',
                    r'\.execute\(.*format\(.*\)',
                    r'\.execute\(.*f".*"',
                    r'\.execute\(.*\.join\(.*\)'
                ],
                'xss': [
                    r'\.innerHTML\s*=',
                    r'\.outerHTML\s*=',
                    r'document\.write\(',
                    r'\.insertAdjacentHTML\(',
                    r'\.insertAdjacentText\(',
                    r'\.setAttribute\(.*,.*\+.*\)',
                    r'\.setAttribute\(.*,.*format\(.*\)',
                    r'\.setAttribute\(.*,.*f".*"'
                ],
                'command_injection': [
                    r'os\.system\(.*\+.*\)',
                    r'subprocess\.call\(.*\+.*\)',
                    r'subprocess\.Popen\(.*\+.*\)',
                    r'subprocess\.run\(.*\+.*\)',
                    r'\.communicate\(.*\+.*\)',
                    r'\.check_output\(.*\+.*\)',
                    r'\.check_call\(.*\+.*\)',
                    r'\.run\(.*shell=True.*\)',
                    r'\.run\(.*executable=.*\+.*\)'
                ],
                'file_inclusion': [
                    r'open\(.*\+.*\)',
                    r'file\(.*\+.*\)',
                    r'\.read\(.*\+.*\)',
                    r'\.write\(.*\+.*\)',
                    r'\.readlines\(.*\+.*\)',
                    r'\.writelines\(.*\+.*\)',
                    r'\.readline\(.*\+.*\)',
                    r'\.read\(.*format\(.*\)',
                    r'\.read\(.*f".*"'
                ],
                'deserialization': [
                    r'pickle\.loads\(.*\)',
                    r'pickle\.load\(.*\)',
                    r'yaml\.load\(.*\)',
                    r'yaml\.safe_load\(.*\)',
                    r'json\.loads\(.*\)',
                    r'json\.load\(.*\)',
                    r'marshal\.loads\(.*\)',
                    r'marshal\.load\(.*\)'
                ],
                'crypto_weakness': [
                    r'random\.random\(\)',
                    r'random\.randint\(.*,.*\)',
                    r'random\.choice\(.*\)',
                    r'random\.randrange\(.*\)',
                    r'random\.sample\(.*\)',
                    r'random\.shuffle\(.*\)',
                    r'random\.uniform\(.*,.*\)',
                    r'random\.triangular\(.*,.*\)'
                ],
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'].*["\']',
                    r'secret\s*=\s*["\'].*["\']',
                    r'api_key\s*=\s*["\'].*["\']',
                    r'token\s*=\s*["\'].*["\']',
                    r'key\s*=\s*["\'].*["\']',
                    r'\.env\s*=\s*["\'].*["\']',
                    r'\.config\s*=\s*["\'].*["\']'
                ]
            },
            performance_patterns={
                'n_plus_one': [
                    r'for.*in.*:.*\.query\(',
                    r'for.*in.*:.*\.filter\(',
                    r'for.*in.*:.*\.get\(',
                    r'for.*in.*:.*\.filter_by\(',
                    r'for.*in.*:.*\.first\(',
                    r'for.*in.*:.*\.one\(',
                    r'for.*in.*:.*\.one_or_none\(',
                    r'for.*in.*:.*\.scalar\(',
                    r'for.*in.*:.*\.scalar_one\(',
                    r'for.*in.*:.*\.scalar_one_or_none\('
                ],
                'memory_leak': [
                    r'global.*=.*',
                    r'\.append\(.*\)',
                    r'\.extend\(.*\)',
                    r'\.insert\(.*\)',
                    r'\.pop\(.*\)',
                    r'\.remove\(.*\)',
                    r'\.clear\(.*\)',
                    r'\.update\(.*\)',
                    r'\.add\(.*\)',
                    r'\.discard\(.*\)',
                    r'\.union\(.*\)',
                    r'\.intersection\(.*\)',
                    r'\.difference\(.*\)',
                    r'\.symmetric_difference\(.*\)'
                ],
                'inefficient_loop': [
                    r'for.*in.*:.*\.append\(',
                    r'for.*in.*:.*\.extend\(',
                    r'for.*in.*:.*\.insert\(',
                    r'for.*in.*:.*\.pop\(',
                    r'for.*in.*:.*\.remove\(',
                    r'for.*in.*:.*\.clear\(',
                    r'for.*in.*:.*\.update\(',
                    r'for.*in.*:.*\.add\(',
                    r'for.*in.*:.*\.discard\(',
                    r'for.*in.*:.*\.union\(',
                    r'for.*in.*:.*\.intersection\(',
                    r'for.*in.*:.*\.difference\(',
                    r'for.*in.*:.*\.symmetric_difference\('
                ],
                'inefficient_data_structure': [
                    r'list\(.*\)\.index\(.*\)',
                    r'list\(.*\)\.count\(.*\)',
                    r'list\(.*\)\.remove\(.*\)',
                    r'list\(.*\)\.pop\(.*\)',
                    r'list\(.*\)\.insert\(.*\)',
                    r'list\(.*\)\.append\(.*\)',
                    r'list\(.*\)\.extend\(.*\)',
                    r'list\(.*\)\.clear\(.*\)',
                    r'list\(.*\)\.copy\(.*\)',
                    r'list\(.*\)\.sort\(.*\)',
                    r'list\(.*\)\.reverse\(.*\)'
                ],
                'inefficient_string_operation': [
                    r'\+.*\+.*\+',
                    r'\.join\(.*\+.*\)',
                    r'\.format\(.*\+.*\)',
                    r'f".*".*f".*"',
                    r'%s.*%s.*%s',
                    r'\.replace\(.*,.*\)\.replace\(.*,.*\)',
                    r'\.split\(.*\)\.join\(.*\)',
                    r'\.strip\(.*\)\.strip\(.*\)',
                    r'\.lower\(.*\)\.upper\(.*\)',
                    r'\.upper\(.*\)\.lower\(.*\)'
                ],
                'inefficient_file_operation': [
                    r'open\(.*\)\.read\(\)',
                    r'open\(.*\)\.readlines\(\)',
                    r'open\(.*\)\.readline\(\)',
                    r'open\(.*\)\.write\(.*\)',
                    r'open\(.*\)\.writelines\(.*\)',
                    r'open\(.*\)\.seek\(.*\)',
                    r'open\(.*\)\.tell\(.*\)',
                    r'open\(.*\)\.truncate\(.*\)',
                    r'open\(.*\)\.flush\(.*\)',
                    r'open\(.*\)\.close\(.*\)'
                ]
            },
            style_patterns={
                'naming_convention': [
                    r'^[a-z_][a-z0-9_]*$',  # variables and functions
                    r'^[A-Z][a-zA-Z0-9]*$',  # classes
                    r'^[A-Z_][A-Z0-9_]*$'   # constants
                ],
                'docstring': [
                    r'""".*?"""',
                    r"'''.*?'''"
                ],
                'type_hints': [
                    r':\s*[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?',
                    r'->\s*[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?'
                ]
            },
            complexity_patterns={
                'nesting': [
                    r'if.*:.*if.*:',
                    r'for.*:.*for.*:',
                    r'while.*:.*while.*:'
                ],
                'long_function': [
                    r'def\s+\w+\s*\([^)]*\):.*?(?=def|\Z)'
                ],
                'complex_condition': [
                    r'if.*and.*and.*:',
                    r'if.*or.*or.*:'
                ]
            }
        )
        
        # JavaScript configuration
        configs['javascript'] = LanguageConfig(
            name='JavaScript',
            file_extensions=['.js', '.jsx', '.ts', '.tsx'],
            parser_name='javascript',
            keywords=['function', 'class', 'const', 'let', 'var', 'return', 'throw', 'try', 'catch', 'finally', 'async', 'await'],
            builtin_types=['number', 'string', 'boolean', 'object', 'array', 'function'],
            security_patterns={
                'xss': [
                    r'\.innerHTML\s*=',
                    r'\.outerHTML\s*=',
                    r'document\.write\(',
                    r'\.insertAdjacentHTML\(',
                    r'\.insertAdjacentText\(',
                    r'\.setAttribute\(.*,.*\+.*\)',
                    r'\.setAttribute\(.*,.*format\(.*\)',
                    r'\.setAttribute\(.*,.*f".*"',
                    r'\.setAttribute\(.*,.*`.*`',
                    r'\.setAttribute\(.*,.*\$\{.*\}\)',
                    r'\.setAttribute\(.*,.*\.concat\(.*\)',
                    r'\.setAttribute\(.*,.*\.join\(.*\)',
                    r'\.setAttribute\(.*,.*\.replace\(.*\)',
                    r'\.setAttribute\(.*,.*\.replaceAll\(.*\)'
                ],
                'eval_injection': [
                    r'eval\(',
                    r'new Function\(',
                    r'setTimeout\(',
                    r'setInterval\(',
                    r'requestAnimationFrame\(',
                    r'requestIdleCallback\(',
                    r'\.addEventListener\(.*,.*\)',
                    r'\.attachEvent\(.*,.*\)',
                    r'\.on\(',
                    r'\.bind\(',
                    r'\.call\(',
                    r'\.apply\(',
                    r'\.exec\(',
                    r'\.test\(',
                    r'\.match\(',
                    r'\.replace\(.*,.*function.*\)',
                    r'\.replaceAll\(.*,.*function.*\)'
                ],
                'prototype_pollution': [
                    r'Object\.prototype\.',
                    r'__proto__\s*=',
                    r'constructor\.prototype\.',
                    r'\.prototype\.',
                    r'\.__proto__\.',
                    r'\.constructor\.',
                    r'\.hasOwnProperty\.',
                    r'\.isPrototypeOf\.',
                    r'\.propertyIsEnumerable\.',
                    r'\.toLocaleString\.',
                    r'\.toString\.',
                    r'\.valueOf\.'
                ],
                'dom_based_xss': [
                    r'document\.createElement\(.*\)\.innerHTML',
                    r'document\.createElement\(.*\)\.outerHTML',
                    r'document\.createElement\(.*\)\.setAttribute',
                    r'document\.createElement\(.*\)\.insertAdjacentHTML',
                    r'document\.createElement\(.*\)\.insertAdjacentText',
                    r'document\.createElement\(.*\)\.appendChild',
                    r'document\.createElement\(.*\)\.replaceChild',
                    r'document\.createElement\(.*\)\.insertBefore',
                    r'document\.createElement\(.*\)\.removeChild',
                    r'document\.createElement\(.*\)\.cloneNode'
                ],
                'local_storage': [
                    r'localStorage\.setItem\(.*,.*\)',
                    r'sessionStorage\.setItem\(.*,.*\)',
                    r'localStorage\.getItem\(.*\)',
                    r'sessionStorage\.getItem\(.*\)',
                    r'localStorage\.removeItem\(.*\)',
                    r'sessionStorage\.removeItem\(.*\)',
                    r'localStorage\.clear\(\)',
                    r'sessionStorage\.clear\(\)',
                    r'localStorage\.key\(.*\)',
                    r'sessionStorage\.key\(.*\)'
                ],
                'crypto_weakness': [
                    r'Math\.random\(\)',
                    r'Math\.floor\(.*Math\.random\(\)',
                    r'Math\.ceil\(.*Math\.random\(\)',
                    r'Math\.round\(.*Math\.random\(\)',
                    r'Math\.abs\(.*Math\.random\(\)',
                    r'Math\.max\(.*Math\.random\(\)',
                    r'Math\.min\(.*Math\.random\(\)',
                    r'Math\.pow\(.*Math\.random\(\)',
                    r'Math\.sqrt\(.*Math\.random\(\)'
                ],
                'hardcoded_secrets': [
                    r'password\s*=\s*["\'].*["\']',
                    r'secret\s*=\s*["\'].*["\']',
                    r'api_key\s*=\s*["\'].*["\']',
                    r'token\s*=\s*["\'].*["\']',
                    r'key\s*=\s*["\'].*["\']',
                    r'\.env\s*=\s*["\'].*["\']',
                    r'\.config\s*=\s*["\'].*["\']',
                    r'process\.env\.[A-Z_]+',
                    r'window\.__INITIAL_STATE__',
                    r'window\.__REDUX_DEVTOOLS_EXTENSION__'
                ]
            },
            performance_patterns={
                'memory_leak': [
                    r'addEventListener\(.*,.*\)',
                    r'setInterval\(',
                    r'setTimeout\(',
                    r'requestAnimationFrame\(',
                    r'requestIdleCallback\(',
                    r'\.addEventListener\(.*,.*\)',
                    r'\.attachEvent\(.*,.*\)',
                    r'\.on\(',
                    r'\.bind\(',
                    r'\.call\(',
                    r'\.apply\(',
                    r'\.exec\(',
                    r'\.test\(',
                    r'\.match\(',
                    r'\.replace\(.*,.*function.*\)',
                    r'\.replaceAll\(.*,.*function.*\)'
                ],
                'inefficient_loop': [
                    r'for\s*\(.*;.*;.*\)\s*{',
                    r'while\s*\(.*\)\s*{',
                    r'do\s*{.*}\s*while\s*\(.*\)',
                    r'\.forEach\(.*function.*\)',
                    r'\.map\(.*function.*\)',
                    r'\.filter\(.*function.*\)',
                    r'\.reduce\(.*function.*\)',
                    r'\.reduceRight\(.*function.*\)',
                    r'\.some\(.*function.*\)',
                    r'\.every\(.*function.*\)',
                    r'\.find\(.*function.*\)',
                    r'\.findIndex\(.*function.*\)',
                    r'\.includes\(.*function.*\)',
                    r'\.indexOf\(.*function.*\)',
                    r'\.lastIndexOf\(.*function.*\)'
                ],
                'inefficient_dom_operation': [
                    r'document\.getElementById\(.*\)\.style\.',
                    r'document\.getElementsByClassName\(.*\)\.style\.',
                    r'document\.getElementsByTagName\(.*\)\.style\.',
                    r'document\.querySelector\(.*\)\.style\.',
                    r'document\.querySelectorAll\(.*\)\.style\.',
                    r'document\.getElementById\(.*\)\.innerHTML',
                    r'document\.getElementsByClassName\(.*\)\.innerHTML',
                    r'document\.getElementsByTagName\(.*\)\.innerHTML',
                    r'document\.querySelector\(.*\)\.innerHTML',
                    r'document\.querySelectorAll\(.*\)\.innerHTML'
                ],
                'inefficient_array_operation': [
                    r'\.push\(.*\)\.push\(.*\)',
                    r'\.pop\(.*\)\.pop\(.*\)',
                    r'\.shift\(.*\)\.shift\(.*\)',
                    r'\.unshift\(.*\)\.unshift\(.*\)',
                    r'\.splice\(.*\)\.splice\(.*\)',
                    r'\.slice\(.*\)\.slice\(.*\)',
                    r'\.concat\(.*\)\.concat\(.*\)',
                    r'\.join\(.*\)\.join\(.*\)',
                    r'\.reverse\(.*\)\.reverse\(.*\)',
                    r'\.sort\(.*\)\.sort\(.*\)'
                ],
                'inefficient_string_operation': [
                    r'\+.*\+.*\+',
                    r'\.concat\(.*\)\.concat\(.*\)',
                    r'\.replace\(.*\)\.replace\(.*\)',
                    r'\.replaceAll\(.*\)\.replaceAll\(.*\)',
                    r'\.split\(.*\)\.join\(.*\)',
                    r'\.trim\(.*\)\.trim\(.*\)',
                    r'\.toLowerCase\(.*\)\.toUpperCase\(.*\)',
                    r'\.toUpperCase\(.*\)\.toLowerCase\(.*\)',
                    r'\.substring\(.*\)\.substring\(.*\)',
                    r'\.substr\(.*\)\.substr\(.*\)'
                ],
                'inefficient_object_operation': [
                    r'Object\.keys\(.*\)\.forEach\(.*\)',
                    r'Object\.values\(.*\)\.forEach\(.*\)',
                    r'Object\.entries\(.*\)\.forEach\(.*\)',
                    r'Object\.getOwnPropertyNames\(.*\)\.forEach\(.*\)',
                    r'Object\.getOwnPropertySymbols\(.*\)\.forEach\(.*\)',
                    r'Object\.assign\(.*\)\.assign\(.*\)',
                    r'Object\.create\(.*\)\.create\(.*\)',
                    r'Object\.defineProperty\(.*\)\.defineProperty\(.*\)',
                    r'Object\.defineProperties\(.*\)\.defineProperties\(.*\)',
                    r'Object\.freeze\(.*\)\.freeze\(.*\)'
                ]
            },
            style_patterns={
                'naming_convention': [
                    r'^[a-z][a-zA-Z0-9]*$',  # variables and functions
                    r'^[A-Z][a-zA-Z0-9]*$',  # classes
                    r'^[A-Z_][A-Z0-9_]*$'   # constants
                ],
                'arrow_function': [
                    r'const\s+\w+\s*=\s*\([^)]*\)\s*=>'
                ],
                'type_annotations': [
                    r':\s*[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?',
                    r'interface\s+\w+\s*{'
                ]
            },
            complexity_patterns={
                'nesting': [
                    r'if\s*\(.*\)\s*{.*if\s*\(.*\)\s*{',
                    r'for\s*\(.*\)\s*{.*for\s*\(.*\)\s*{',
                    r'while\s*\(.*\)\s*{.*while\s*\(.*\)\s*{'
                ],
                'long_function': [
                    r'function\s+\w+\s*\([^)]*\)\s*{.*?(?=function|\Z)'
                ],
                'complex_condition': [
                    r'if\s*\(.*&&.*&&.*\)',
                    r'if\s*\(.*\|\|.*\|\|.*\)'
                ]
            }
        )
        
        return configs
        
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect the programming language of a file."""
        extension = Path(file_path).suffix.lower()
        for lang, config in self.language_configs.items():
            if extension in config.file_extensions:
                return lang
        return None
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a single file."""
        language = self.detect_language(file_path)
        if not language:
            self.logger.warning(f"Unsupported file type: {file_path}")
            return {}
            
        with open(file_path, 'rb') as f:
            source_code = f.read()
            
        tree = self.ast_parser.parse(source_code)
        config = self.language_configs[language]
        
        analysis = {
            'language': language,
            'ast': self._extract_ast(tree),
            'syntax': self._analyze_syntax(tree, config),
            'semantics': self._analyze_semantics(tree, config),
            'control_flow': self._analyze_control_flow(tree, config),
            'data_flow': self._analyze_data_flow(tree, config),
            'entities': self._extract_entities(tree, file_path, config),
            'dependencies': self._analyze_dependencies(tree, file_path, config),
            'metrics': self._analyze_code_metrics(tree, config),
            'security': self._analyze_security(tree, config),
            'performance': self._analyze_performance(tree, config),
            'maintainability': self._analyze_maintainability(tree, config),
            'test_coverage': self._analyze_test_coverage(tree, config),
            'documentation': self._analyze_documentation(tree, config),
            'code_quality': self._analyze_code_quality(tree, config),
            'style': self._analyze_style(tree, config),
            'complexity': self._analyze_complexity(tree, config)
        }
        
        return analysis
        
    def _analyze_style(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code style and conventions."""
        style = {
            'naming_conventions': [],
            'docstrings': [],
            'type_annotations': [],
            'style_violations': []
        }
        
        source_code = tree.text.decode('utf8')
        
        # Check naming conventions
        for pattern in config.style_patterns['naming_convention']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                style['naming_conventions'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        # Check docstrings
        for pattern in config.style_patterns['docstring']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                style['docstrings'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        # Check type annotations
        for pattern in config.style_patterns['type_hints']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                style['type_annotations'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        return style
        
    def _analyze_complexity(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code complexity patterns."""
        complexity = {
            'nesting_levels': [],
            'long_functions': [],
            'complex_conditions': [],
            'complexity_score': 0
        }
        
        source_code = tree.text.decode('utf8')
        
        # Check nesting levels
        for pattern in config.complexity_patterns['nesting']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                complexity['nesting_levels'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        # Check long functions
        for pattern in config.complexity_patterns['long_function']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                complexity['long_functions'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        # Check complex conditions
        for pattern in config.complexity_patterns['complex_condition']:
            matches = re.finditer(pattern, source_code)
            for match in matches:
                complexity['complex_conditions'].append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': source_code[:match.start()].count('\n') + 1
                })
                
        # Calculate overall complexity score
        complexity['complexity_score'] = (
            len(complexity['nesting_levels']) * 2 +
            len(complexity['long_functions']) * 3 +
            len(complexity['complex_conditions']) * 1
        )
        
        return complexity
        
    def _analyze_security(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities."""
        security = {
            'vulnerabilities': [],
            'risk_level': 'low',
            'recommendations': []
        }
        
        source_code = tree.text.decode('utf8')
        
        for vuln_type, patterns in config.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code)
                for match in matches:
                    security['vulnerabilities'].append({
                        'type': vuln_type,
                        'line': source_code[:match.start()].count('\n') + 1,
                        'code': match.group(0)
                    })
                    
        if security['vulnerabilities']:
            security['risk_level'] = 'high'
            
        return security
        
    def _analyze_performance(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code for performance issues."""
        performance = {
            'issues': [],
            'impact_level': 'low',
            'recommendations': []
        }
        
        source_code = tree.text.decode('utf8')
        
        for issue_type, patterns in config.performance_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code)
                for match in matches:
                    performance['issues'].append({
                        'type': issue_type,
                        'line': source_code[:match.start()].count('\n') + 1,
                        'code': match.group(0)
                    })
                    
        if performance['issues']:
            performance['impact_level'] = 'high'
            
        return performance
        
    def _analyze_maintainability(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code maintainability."""
        maintainability = {
            'score': 0.0,
            'factors': [],
            'recommendations': []
        }
        
        # Calculate maintainability score based on various factors
        metrics = self._analyze_code_metrics(tree, config)
        
        # Complexity factor
        complexity_factor = 1.0 - (metrics['cyclomatic_complexity'] / 100)
        maintainability['score'] += complexity_factor * 0.3
        
        # Size factor
        size_factor = 1.0 - (metrics['lines_of_code'] / 1000)
        maintainability['score'] += size_factor * 0.2
        
        # Documentation factor
        doc_factor = metrics['comment_ratio']
        maintainability['score'] += doc_factor * 0.2
        
        # Structure factor
        structure_factor = 1.0 - (metrics['average_function_length'] / 50)
        maintainability['score'] += structure_factor * 0.3
        
        maintainability['score'] = max(0.0, min(1.0, maintainability['score']))
        
        return maintainability
        
    def _analyze_test_coverage(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code test coverage."""
        coverage = {
            'overall_coverage': 0.0,
            'function_coverage': {},
            'class_coverage': {},
            'missing_tests': []
        }
        
        # This would typically integrate with a test coverage tool
        # For now, we'll just identify untested functions and classes
        functions = self._extract_functions(tree)
        classes = self._extract_classes(tree)
        
        for func in functions:
            if not self._has_tests(func):
                coverage['missing_tests'].append({
                    'type': 'function',
                    'name': func['name'],
                    'line': func['line']
                })
                
        for cls in classes:
            if not self._has_tests(cls):
                coverage['missing_tests'].append({
                    'type': 'class',
                    'name': cls['name'],
                    'line': cls['line']
                })
                
        return coverage
        
    def _analyze_documentation(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze code documentation."""
        documentation = {
            'docstring_coverage': 0.0,
            'parameter_documentation': 0.0,
            'return_documentation': 0.0,
            'missing_docs': [],
            'quality_score': 0.0
        }
        
        functions = self._extract_functions(tree)
        classes = self._extract_classes(tree)
        
        total_entities = len(functions) + len(classes)
        documented_entities = 0
        
        for func in functions:
            if self._has_docstring(func):
                documented_entities += 1
            else:
                documentation['missing_docs'].append({
                    'type': 'function',
                    'name': func['name'],
                    'line': func['line']
                })
                
        for cls in classes:
            if self._has_docstring(cls):
                documented_entities += 1
            else:
                documentation['missing_docs'].append({
                    'type': 'class',
                    'name': cls['name'],
                    'line': cls['line']
                })
                
        documentation['docstring_coverage'] = documented_entities / total_entities if total_entities > 0 else 0.0
        
        return documentation
        
    def _analyze_code_quality(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze overall code quality."""
        quality = {
            'score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        # Combine various quality metrics
        metrics = self._analyze_code_metrics(tree, config)
        maintainability = self._analyze_maintainability(tree, config)
        documentation = self._analyze_documentation(tree, config)
        security = self._analyze_security(tree, config)
        performance = self._analyze_performance(tree, config)
        
        # Calculate overall quality score
        quality['score'] = (
            maintainability['score'] * 0.3 +
            documentation['docstring_coverage'] * 0.2 +
            (1.0 if security['risk_level'] == 'low' else 0.0) * 0.2 +
            (1.0 if performance['impact_level'] == 'low' else 0.0) * 0.2 +
            (1.0 - (metrics['cyclomatic_complexity'] / 100)) * 0.1
        )
        
        # Collect issues and recommendations
        quality['issues'].extend(security['vulnerabilities'])
        quality['issues'].extend(performance['issues'])
        quality['issues'].extend(documentation['missing_docs'])
        
        quality['recommendations'].extend(security['recommendations'])
        quality['recommendations'].extend(performance['recommendations'])
        quality['recommendations'].extend(maintainability['recommendations'])
        
        return quality
        
    def _calculate_cyclomatic_complexity(self, tree: tree_sitter.Tree) -> int:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1  # Base complexity
        
        def traverse(node: tree_sitter.Node):
            nonlocal complexity
            if node.type in ['if_statement', 'elif_clause', 'else_clause']:
                complexity += 1
            elif node.type in ['for_statement', 'while_statement']:
                complexity += 2
            elif node.type == 'try_statement':
                complexity += 1
            elif node.type == 'except_clause':
                complexity += 1
            elif node.type in ['and_operator', 'or_operator']:
                complexity += 1
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return complexity
        
    def _calculate_cognitive_complexity(self, tree: tree_sitter.Tree) -> int:
        """Calculate cognitive complexity of the code."""
        complexity = 0
        
        def traverse(node: tree_sitter.Node, nesting: int = 0):
            nonlocal complexity
            if node.type in ['if_statement', 'elif_clause', 'else_clause']:
                complexity += 2 + nesting
            elif node.type in ['for_statement', 'while_statement']:
                complexity += 4 + nesting
            elif node.type == 'try_statement':
                complexity += 2 + nesting
            elif node.type == 'except_clause':
                complexity += 2 + nesting
            elif node.type in ['and_operator', 'or_operator']:
                complexity += 1
                
            for child in node.children:
                traverse(child, nesting + 1)
                
        traverse(tree.root_node)
        return complexity
        
    def _calculate_maintainability_index(self, tree: tree_sitter.Tree) -> float:
        """Calculate maintainability index of the code."""
        metrics = self._analyze_code_metrics(tree)
        
        # Simplified maintainability index calculation
        halstead_volume = metrics['lines_of_code'] * 0.5
        cyclomatic_complexity = metrics['cyclomatic_complexity']
        comment_ratio = metrics['comment_ratio']
        
        maintainability = (
            171 - 5.2 * halstead_volume / 1000 -
            0.23 * cyclomatic_complexity -
            16.2 * (1 - comment_ratio)
        ) / 171
        
        return max(0.0, min(1.0, maintainability))
        
    def _count_lines_of_code(self, tree: tree_sitter.Tree) -> int:
        """Count lines of code."""
        return tree.root_node.end_point[0] + 1
        
    def _calculate_comment_ratio(self, tree: tree_sitter.Tree) -> float:
        """Calculate ratio of comments to code."""
        source_code = tree.text.decode('utf8')
        lines = source_code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        return comment_lines / len(lines) if lines else 0.0
        
    def _count_functions(self, tree: tree_sitter.Tree) -> int:
        """Count number of functions."""
        count = 0
        
        def traverse(node: tree_sitter.Node):
            nonlocal count
            if node.type == 'function_definition':
                count += 1
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return count
        
    def _count_classes(self, tree: tree_sitter.Tree) -> int:
        """Count number of classes."""
        count = 0
        
        def traverse(node: tree_sitter.Node):
            nonlocal count
            if node.type == 'class_definition':
                count += 1
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return count
        
    def _calculate_average_function_length(self, tree: tree_sitter.Tree) -> float:
        """Calculate average function length."""
        functions = self._extract_functions(tree)
        if not functions:
            return 0.0
        total_length = sum(func['end_line'] - func['start_line'] + 1 for func in functions)
        return total_length / len(functions)
        
    def _calculate_average_class_length(self, tree: tree_sitter.Tree) -> float:
        """Calculate average class length."""
        classes = self._extract_classes(tree)
        if not classes:
            return 0.0
        total_length = sum(cls['end_line'] - cls['start_line'] + 1 for cls in classes)
        return total_length / len(classes)
        
    def _extract_functions(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract function information."""
        functions = []
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'function_definition':
                functions.append({
                    'name': node.child_by_field_name('name').text.decode('utf8'),
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'parameters': self._extract_parameters(node),
                    'return_type': self._extract_return_type(node),
                    'docstring': self._extract_docstring(node)
                })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return functions
        
    def _extract_classes(self, tree: tree_sitter.Tree) -> List[Dict[str, Any]]:
        """Extract class information."""
        classes = []
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'class_definition':
                classes.append({
                    'name': node.child_by_field_name('name').text.decode('utf8'),
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'bases': self._extract_base_classes(node),
                    'docstring': self._extract_docstring(node)
                })
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return classes
        
    def _has_tests(self, entity: Dict[str, Any]) -> bool:
        """Check if an entity has associated tests."""
        # This would typically check for test files and test cases
        # For now, we'll just return False
        return False
        
    def _has_docstring(self, entity: Dict[str, Any]) -> bool:
        """Check if an entity has a docstring."""
        return bool(entity.get('docstring'))
        
    def _extract_ast(self, tree: tree_sitter.Tree) -> Dict[str, Any]:
        """Extract detailed AST structure with additional metadata."""
        def traverse(node: tree_sitter.Node) -> Dict[str, Any]:
            result = {
                'type': node.type,
                'start_point': node.start_point,
                'end_point': node.end_point,
                'text': node.text.decode('utf8'),
                'children': []
            }
            
            for child in node.children:
                result['children'].append(traverse(child))
                
            return result
            
        return traverse(tree.root_node)
        
    def _analyze_syntax(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze syntax structure with enhanced categorization."""
        analysis = {
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': [],
            'decorators': [],
            'type_annotations': [],
            'errors': []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'import_statement':
                analysis['imports'].append({
                    'text': node.text.decode('utf8'),
                    'line': node.start_point[0]
                })
            elif node.type == 'class_definition':
                analysis['classes'].append({
                    'name': node.child_by_field_name('name').text.decode('utf8'),
                    'line': node.start_point[0],
                    'bases': self._extract_base_classes(node)
                })
            elif node.type == 'function_definition':
                analysis['functions'].append({
                    'name': node.child_by_field_name('name').text.decode('utf8'),
                    'line': node.start_point[0],
                    'parameters': self._extract_parameters(node),
                    'return_type': self._extract_return_type(node)
                })
            elif node.type == 'variable_declaration':
                analysis['variables'].append({
                    'name': node.child_by_field_name('name').text.decode('utf8'),
                    'line': node.start_point[0],
                    'type': self._extract_type_annotation(node)
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_semantics(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze semantic meaning with scope tracking and type inference."""
        analysis = {
            'scope': {},
            'references': {},
            'definitions': {},
            'usage': {},
            'type_inference': {}
        }
        
        def traverse(node: tree_sitter.Node, scope: str = 'global'):
            if node.type == 'identifier':
                identifier = node.text.decode('utf8')
                if identifier not in analysis['references']:
                    analysis['references'][identifier] = []
                analysis['references'][identifier].append({
                    'node': node,
                    'scope': scope,
                    'line': node.start_point[0]
                })
                
            for child in node.children:
                traverse(child, scope)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_control_flow(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze control flow structure with enhanced path analysis."""
        analysis = {
            'branches': [],
            'loops': [],
            'exceptions': [],
            'returns': [],
            'control_paths': []
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type in ['if_statement', 'elif_clause', 'else_clause']:
                analysis['branches'].append({
                    'type': node.type,
                    'condition': self._extract_condition(node),
                    'line': node.start_point[0]
                })
            elif node.type in ['for_statement', 'while_statement']:
                analysis['loops'].append({
                    'type': node.type,
                    'condition': self._extract_condition(node),
                    'line': node.start_point[0]
                })
            elif node.type == 'try_statement':
                analysis['exceptions'].append({
                    'line': node.start_point[0],
                    'handlers': self._extract_exception_handlers(node)
                })
            elif node.type == 'return_statement':
                analysis['returns'].append({
                    'line': node.start_point[0],
                    'value': self._extract_return_value(node)
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _analyze_data_flow(self, tree: tree_sitter.Tree, config: LanguageConfig) -> Dict[str, Any]:
        """Analyze data flow with variable tracking and dependency analysis."""
        analysis = {
            'definitions': {},
            'uses': {},
            'dependencies': {},
            'variable_lifecycle': {}
        }
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'assignment':
                var_name = node.child_by_field_name('left').text.decode('utf8')
                if var_name not in analysis['definitions']:
                    analysis['definitions'][var_name] = []
                analysis['definitions'][var_name].append({
                    'line': node.start_point[0],
                    'value': self._extract_assignment_value(node)
                })
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return analysis
        
    def _extract_entities(self, tree: tree_sitter.Tree, file_path: str, config: LanguageConfig) -> List[CodeEntity]:
        """Extract code entities with their relationships."""
        entities = []
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'class_definition':
                name = node.child_by_field_name('name').text.decode('utf8')
                entities.append(CodeEntity(
                    name=name,
                    type='class',
                    file_path=file_path,
                    line_number=node.start_point[0],
                    scope=self._determine_scope(node),
                    dependencies=self._extract_dependencies(node),
                    references=self._extract_references(node),
                    docstring=self._extract_docstring(node),
                    language=config.name
                ))
            elif node.type == 'function_definition':
                name = node.child_by_field_name('name').text.decode('utf8')
                entities.append(CodeEntity(
                    name=name,
                    type='function',
                    file_path=file_path,
                    line_number=node.start_point[0],
                    scope=self._determine_scope(node),
                    dependencies=self._extract_dependencies(node),
                    references=self._extract_references(node),
                    docstring=self._extract_docstring(node),
                    language=config.name
                ))
                
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return entities
        
    def _analyze_dependencies(self, tree: tree_sitter.Tree, file_path: str, config: LanguageConfig) -> Dict[str, List[str]]:
        """Analyze dependencies between code entities."""
        dependencies = defaultdict(list)
        
        def traverse(node: tree_sitter.Node):
            if node.type == 'import_statement':
                module = self._extract_import_module(node)
                dependencies[file_path].append(module)
            elif node.type == 'call':
                target = self._extract_call_target(node)
                if target:
                    dependencies[file_path].append(target)
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return dict(dependencies)
        
    def _determine_scope(self, node: tree_sitter.Node) -> str:
        """Determine the scope of a code entity."""
        current = node
        while current.parent:
            if current.parent.type == 'function_definition':
                return 'function'
            elif current.parent.type == 'class_definition':
                return 'class'
            current = current.parent
        return 'module'
        
    def _extract_dependencies(self, node: tree_sitter.Node) -> List[str]:
        """Extract dependencies for a code entity."""
        dependencies = []
        
        def traverse(n: tree_sitter.Node):
            if n.type == 'identifier':
                dependencies.append(n.text.decode('utf8'))
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return dependencies
        
    def _extract_references(self, node: tree_sitter.Node) -> List[str]:
        """Extract references to a code entity."""
        references = []
        
        def traverse(n: tree_sitter.Node):
            if n.type == 'identifier' and n.text.decode('utf8') == node.child_by_field_name('name').text.decode('utf8'):
                references.append({
                    'line': n.start_point[0],
                    'column': n.start_point[1]
                })
            for child in n.children:
                traverse(child)
                
        traverse(node)
        return references
        
    def _extract_docstring(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract docstring from a code entity."""
        for child in node.children:
            if child.type == 'expression_statement':
                expr = child.child_by_field_name('expression')
                if expr.type == 'string':
                    return expr.text.decode('utf8')
        return None
        
    def _extract_base_classes(self, node: tree_sitter.Node) -> List[str]:
        """Extract base classes from a class definition."""
        bases = []
        inheritance = node.child_by_field_name('inheritance')
        if inheritance:
            for base in inheritance.children:
                if base.type == 'identifier':
                    bases.append(base.text.decode('utf8'))
        return bases
        
    def _extract_parameters(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        """Extract parameters from a function definition."""
        parameters = []
        params = node.child_by_field_name('parameters')
        if params:
            for param in params.children:
                if param.type == 'parameter':
                    param_info = {
                        'name': param.child_by_field_name('name').text.decode('utf8'),
                        'type': self._extract_type_annotation(param)
                    }
                    parameters.append(param_info)
        return parameters
        
    def _extract_return_type(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract return type from a function definition."""
        return_type = node.child_by_field_name('return_type')
        if return_type:
            return return_type.text.decode('utf8')
        return None
        
    def _extract_type_annotation(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract type annotation from a node."""
        type_annotation = node.child_by_field_name('type')
        if type_annotation:
            return type_annotation.text.decode('utf8')
        return None
        
    def _extract_condition(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract condition from a control flow node."""
        condition = node.child_by_field_name('condition')
        if condition:
            return condition.text.decode('utf8')
        return None
        
    def _extract_exception_handlers(self, node: tree_sitter.Node) -> List[Dict[str, Any]]:
        """Extract exception handlers from a try statement."""
        handlers = []
        for child in node.children:
            if child.type == 'except_clause':
                handler = {
                    'line': child.start_point[0],
                    'exception': self._extract_exception_type(child),
                    'body': child.child_by_field_name('body').text.decode('utf8')
                }
                handlers.append(handler)
        return handlers
        
    def _extract_exception_type(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract exception type from an except clause."""
        exception = node.child_by_field_name('exception')
        if exception:
            return exception.text.decode('utf8')
        return None
        
    def _extract_return_value(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract return value from a return statement."""
        value = node.child_by_field_name('value')
        if value:
            return value.text.decode('utf8')
        return None
        
    def _extract_assignment_value(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract value from an assignment statement."""
        value = node.child_by_field_name('right')
        if value:
            return value.text.decode('utf8')
        return None
        
    def _extract_import_module(self, node: tree_sitter.Node) -> str:
        """Extract module name from an import statement."""
        module = node.child_by_field_name('module')
        if module:
            return module.text.decode('utf8')
        return ''
        
    def _extract_call_target(self, node: tree_sitter.Node) -> Optional[str]:
        """Extract target from a function call."""
        target = node.child_by_field_name('function')
        if target and target.type == 'identifier':
            return target.text.decode('utf8')
        return None 