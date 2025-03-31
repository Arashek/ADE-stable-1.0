from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import ast
import re
import logging
import yaml
from pathlib import Path
from ...core.base_agent import BaseAgent

@dataclass
class ValidationIssue:
    category: str
    severity: str
    description: str
    location: str
    fix_suggestion: str
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None

class ValidationAgent(BaseAgent):
    """Specialized agent for code validation and quality assurance"""
    
    def __init__(self):
        super().__init__("validation_agent")
        self.logger = logging.getLogger(__name__)
        self._load_validation_rules()
        self._load_domain_patterns()

    def _load_validation_rules(self):
        """Load validation rules for different domains and technologies"""
        self.rules = {
            'general': {
                'naming_convention': {
                    'class': r'^[A-Z][a-zA-Z0-9]*$',
                    'function': r'^[a-z][a-zA-Z0-9]*$',
                    'constant': r'^[A-Z][A-Z0-9_]*$',
                    'variable': r'^[a-z][a-zA-Z0-9_]*$'
                },
                'complexity': {
                    'max_line_length': 100,
                    'max_function_length': 50,
                    'max_class_length': 300,
                    'max_parameters': 5,
                    'max_complexity': 10
                },
                'structure': {
                    'required_docstring': True,
                    'required_type_hints': True,
                    'required_tests': True
                }
            },
            'web': {
                'security': {
                    'required_headers': [
                        'X-Content-Type-Options',
                        'X-Frame-Options',
                        'Content-Security-Policy'
                    ],
                    'csrf_protection': True,
                    'secure_cookies': True
                },
                'performance': {
                    'max_bundle_size': 500000,
                    'max_image_size': 1000000,
                    'required_lazy_loading': True
                }
            },
            'api': {
                'rest': {
                    'required_methods': ['GET', 'POST', 'PUT', 'DELETE'],
                    'required_status_codes': [200, 201, 400, 401, 403, 404, 500],
                    'required_validation': True,
                    'required_rate_limiting': True
                },
                'graphql': {
                    'required_descriptions': True,
                    'required_input_validation': True,
                    'max_depth': 5
                }
            }
        }

    def _load_domain_patterns(self):
        """Load domain-specific patterns and requirements"""
        try:
            base_path = Path(__file__).parent.parent.parent.parent / 'config'
            
            # Load standard patterns
            with open(base_path / 'domain_patterns.yaml', 'r') as f:
                self.domain_patterns = yaml.safe_load(f)
            
            # Load extended patterns
            with open(base_path / 'domain_patterns_extended.yaml', 'r') as f:
                self.domain_patterns.update(yaml.safe_load(f))
                
        except Exception as e:
            self.logger.error(f"Failed to load domain patterns: {e}")
            self.domain_patterns = {}

    async def validate_code(self, code: str, filename: str, domain: str = None) -> List[ValidationIssue]:
        """Validate code against rules and patterns"""
        issues = []
        
        # Basic code validation
        issues.extend(await self._validate_syntax(code, filename))
        issues.extend(await self._validate_style(code, filename))
        issues.extend(await self._validate_complexity(code, filename))
        
        # Domain-specific validation
        if domain and domain in self.domain_patterns:
            issues.extend(await self._validate_domain_specific(code, filename, domain))
        
        # Technology-specific validation
        if self._is_web_file(filename):
            issues.extend(await self._validate_web_code(code, filename))
        elif self._is_api_file(filename):
            issues.extend(await self._validate_api_code(code, filename))
        
        return issues

    async def _validate_syntax(self, code: str, filename: str) -> List[ValidationIssue]:
        """Validate code syntax"""
        issues = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    category="syntax",
                    severity="HIGH",
                    description=f"Syntax error: {str(e)}",
                    location=f"{filename}:{e.lineno}",
                    fix_suggestion="Fix the syntax error according to language rules",
                    code_snippet=code.splitlines()[e.lineno-1] if e.lineno > 0 else None
                )
            )
        
        return issues

    async def _validate_style(self, code: str, filename: str) -> List[ValidationIssue]:
        """Validate code style"""
        issues = []
        
        # Check naming conventions
        for line_num, line in enumerate(code.splitlines(), 1):
            # Check class names
            class_matches = re.finditer(r'class\s+(\w+)', line)
            for match in class_matches:
                class_name = match.group(1)
                if not re.match(self.rules['general']['naming_convention']['class'], class_name):
                    issues.append(
                        ValidationIssue(
                            category="style",
                            severity="LOW",
                            description=f"Class name '{class_name}' doesn't follow naming convention",
                            location=f"{filename}:{line_num}",
                            fix_suggestion="Use PascalCase for class names",
                            code_snippet=line
                        )
                    )
            
            # Check function names
            func_matches = re.finditer(r'def\s+(\w+)', line)
            for match in func_matches:
                func_name = match.group(1)
                if not re.match(self.rules['general']['naming_convention']['function'], func_name):
                    issues.append(
                        ValidationIssue(
                            category="style",
                            severity="LOW",
                            description=f"Function name '{func_name}' doesn't follow naming convention",
                            location=f"{filename}:{line_num}",
                            fix_suggestion="Use snake_case for function names",
                            code_snippet=line
                        )
                    )
        
        return issues

    async def _validate_complexity(self, code: str, filename: str) -> List[ValidationIssue]:
        """Validate code complexity"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check function complexity
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check function length
                    func_lines = len(node.body)
                    if func_lines > self.rules['general']['complexity']['max_function_length']:
                        issues.append(
                            ValidationIssue(
                                category="complexity",
                                severity="MEDIUM",
                                description=f"Function '{node.name}' is too long ({func_lines} lines)",
                                location=f"{filename}:{node.lineno}",
                                fix_suggestion="Break down the function into smaller functions",
                                rule_id="FUNC_LENGTH"
                            )
                        )
                    
                    # Check number of parameters
                    param_count = len(node.args.args)
                    if param_count > self.rules['general']['complexity']['max_parameters']:
                        issues.append(
                            ValidationIssue(
                                category="complexity",
                                severity="MEDIUM",
                                description=f"Function '{node.name}' has too many parameters ({param_count})",
                                location=f"{filename}:{node.lineno}",
                                fix_suggestion="Use a configuration object or break down the function",
                                rule_id="PARAM_COUNT"
                            )
                        )
        
        except SyntaxError:
            self.logger.warning(f"Could not parse {filename} for complexity analysis")
        
        return issues

    async def _validate_domain_specific(self, code: str, filename: str, domain: str) -> List[ValidationIssue]:
        """Validate domain-specific requirements"""
        issues = []
        
        domain_patterns = self.domain_patterns.get(domain, [])
        for pattern in domain_patterns:
            # Check code patterns
            for code_pattern in pattern.get('code_patterns', []):
                if not self._check_pattern_implementation(code, code_pattern):
                    issues.append(
                        ValidationIssue(
                            category="domain",
                            severity="MEDIUM",
                            description=f"Missing required pattern: {code_pattern}",
                            location=filename,
                            fix_suggestion=f"Implement {code_pattern} according to domain requirements",
                            rule_id=f"DOMAIN_{code_pattern.upper()}"
                        )
                    )
            
            # Check security requirements
            for security_req in pattern.get('security_requirements', []):
                if not self._check_security_requirement(code, security_req):
                    issues.append(
                        ValidationIssue(
                            category="security",
                            severity="HIGH",
                            description=f"Missing security requirement: {security_req}",
                            location=filename,
                            fix_suggestion=f"Implement {security_req}",
                            rule_id=f"SEC_{security_req.upper()}"
                        )
                    )
        
        return issues

    def _is_web_file(self, filename: str) -> bool:
        """Check if file is a web-related file"""
        web_extensions = ['.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css']
        return any(filename.endswith(ext) for ext in web_extensions)

    def _is_api_file(self, filename: str) -> bool:
        """Check if file is an API-related file"""
        api_indicators = ['controller', 'route', 'api', 'endpoint']
        return any(indicator in filename.lower() for indicator in api_indicators)

    def _check_pattern_implementation(self, code: str, pattern: str) -> bool:
        """Check if a specific pattern is implemented"""
        # Implementation would include pattern matching logic
        return True

    def _check_security_requirement(self, code: str, requirement: str) -> bool:
        """Check if a security requirement is met"""
        # Implementation would include security requirement checking
        return True

    async def suggest_improvements(self, issues: List[ValidationIssue]) -> Dict[str, List[str]]:
        """Generate improvement suggestions based on validation issues"""
        suggestions = {
            "critical": [],
            "important": [],
            "nice_to_have": []
        }
        
        for issue in issues:
            if issue.severity == "HIGH":
                suggestions["critical"].append(issue.fix_suggestion)
            elif issue.severity == "MEDIUM":
                suggestions["important"].append(issue.fix_suggestion)
            else:
                suggestions["nice_to_have"].append(issue.fix_suggestion)
        
        return suggestions
