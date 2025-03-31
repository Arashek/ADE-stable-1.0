from typing import Dict, List, Optional
from dataclasses import dataclass
import ast
import re
import logging
from ...core.base_agent import BaseAgent

@dataclass
class SecurityVulnerability:
    severity: str
    description: str
    location: str
    fix_suggestion: str
    cwe_id: Optional[str] = None

class SecurityAgent(BaseAgent):
    """Specialized agent for security analysis and vulnerability detection"""
    
    def __init__(self):
        super().__init__("security_agent")
        self.logger = logging.getLogger(__name__)
        self._load_security_patterns()

    def _load_security_patterns(self):
        """Load security patterns and vulnerability signatures"""
        self.patterns = {
            'sql_injection': [
                r'execute\s*\(\s*[\'"][^\']*%.*[\'"]\s*%',
                r'cursor\.execute\s*\(\s*[^,]+\s*%\s*\(',
            ],
            'xss': [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
            ],
            'csrf': [
                r'fetch\s*\(\s*[\'"][^\'"]+[\'"]\s*,\s*{\s*method:\s*[\'"]POST[\'"]\s*\}',
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
            ],
            'command_injection': [
                r'exec\s*\(',
                r'eval\s*\(',
                r'subprocess\.call\s*\(',
            ]
        }

    async def analyze_code(self, code: str, filename: str) -> List[SecurityVulnerability]:
        """Analyze code for security vulnerabilities"""
        vulnerabilities = []
        
        # Static Analysis
        vulnerabilities.extend(await self._perform_static_analysis(code, filename))
        
        # Dynamic Pattern Matching
        vulnerabilities.extend(await self._check_security_patterns(code, filename))
        
        # Dependency Analysis
        if filename.endswith(('requirements.txt', 'package.json')):
            vulnerabilities.extend(await self._analyze_dependencies(code))
        
        return vulnerabilities

    async def _perform_static_analysis(self, code: str, filename: str) -> List[SecurityVulnerability]:
        """Perform static code analysis for security issues"""
        vulnerabilities = []
        
        try:
            tree = ast.parse(code)
            
            # Check for dangerous function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'input']:
                            vulnerabilities.append(
                                SecurityVulnerability(
                                    severity="HIGH",
                                    description=f"Dangerous function call: {node.func.id}",
                                    location=f"{filename}:{node.lineno}",
                                    fix_suggestion="Avoid using dangerous functions. Use safer alternatives.",
                                    cwe_id="CWE-78"
                                )
                            )
        except SyntaxError:
            self.logger.warning(f"Could not parse {filename} for static analysis")
        
        return vulnerabilities

    async def _check_security_patterns(self, code: str, filename: str) -> List[SecurityVulnerability]:
        """Check code against known security vulnerability patterns"""
        vulnerabilities = []
        
        for vuln_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_no = code[:match.start()].count('\n') + 1
                    vulnerabilities.append(
                        SecurityVulnerability(
                            severity="MEDIUM",
                            description=f"Potential {vuln_type} vulnerability detected",
                            location=f"{filename}:{line_no}",
                            fix_suggestion=self._get_fix_suggestion(vuln_type),
                            cwe_id=self._get_cwe_id(vuln_type)
                        )
                    )
        
        return vulnerabilities

    async def _analyze_dependencies(self, code: str) -> List[SecurityVulnerability]:
        """Analyze project dependencies for known vulnerabilities"""
        vulnerabilities = []
        
        # Parse dependencies
        deps = self._parse_dependencies(code)
        
        # Check against vulnerability database
        for dep, version in deps.items():
            if await self._check_vulnerability_database(dep, version):
                vulnerabilities.append(
                    SecurityVulnerability(
                        severity="HIGH",
                        description=f"Vulnerable dependency: {dep}@{version}",
                        location="dependencies",
                        fix_suggestion=f"Update {dep} to latest secure version",
                        cwe_id="CWE-1104"
                    )
                )
        
        return vulnerabilities

    def _parse_dependencies(self, code: str) -> Dict[str, str]:
        """Parse dependencies from requirements.txt or package.json"""
        deps = {}
        
        try:
            if code.startswith('{'):  # package.json
                import json
                data = json.loads(code)
                deps.update(data.get('dependencies', {}))
                deps.update(data.get('devDependencies', {}))
            else:  # requirements.txt
                for line in code.splitlines():
                    if '==' in line:
                        name, version = line.split('==')
                        deps[name.strip()] = version.strip()
        except Exception as e:
            self.logger.error(f"Error parsing dependencies: {e}")
        
        return deps

    async def _check_vulnerability_database(self, dep: str, version: str) -> bool:
        """Check dependency against vulnerability database"""
        # Implementation would include checking against actual vulnerability databases
        return False

    def _get_fix_suggestion(self, vuln_type: str) -> str:
        """Get fix suggestion for vulnerability type"""
        suggestions = {
            'sql_injection': "Use parameterized queries or ORM",
            'xss': "Use safe templating or sanitize input",
            'csrf': "Implement CSRF tokens",
            'path_traversal': "Use path sanitization",
            'command_injection': "Use safe APIs or input validation"
        }
        return suggestions.get(vuln_type, "Review and fix security issue")

    def _get_cwe_id(self, vuln_type: str) -> str:
        """Get CWE ID for vulnerability type"""
        cwe_ids = {
            'sql_injection': "CWE-89",
            'xss': "CWE-79",
            'csrf': "CWE-352",
            'path_traversal': "CWE-22",
            'command_injection': "CWE-78"
        }
        return cwe_ids.get(vuln_type, "")

    async def suggest_security_improvements(self, code: str, domain_type: str) -> List[str]:
        """Suggest security improvements based on code and domain"""
        suggestions = []
        
        # Basic security improvements
        suggestions.extend([
            "Implement input validation",
            "Use secure headers",
            "Enable CORS properly",
            "Implement rate limiting"
        ])
        
        # Domain-specific security improvements
        if domain_type == "finance":
            suggestions.extend([
                "Implement transaction signing",
                "Add fraud detection",
                "Use secure payment gateway integration"
            ])
        elif domain_type == "healthcare":
            suggestions.extend([
                "Implement PHI encryption",
                "Add audit logging",
                "Use secure data transmission"
            ])
        
        return suggestions
