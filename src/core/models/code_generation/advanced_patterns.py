"""
Advanced design patterns, enhanced analysis capabilities, and specialized documentation templates.
"""

from typing import Dict, List, Any, Optional, Type, Callable
from datetime import datetime
from .code_generation import (
    CodeTemplate, CodePattern, DocumentationTemplate,
    CodeGenerator, CodeAnalyzer
)

# Additional Design Patterns

factory_pattern = CodePattern(
    name="factory_pattern",
    description="Implementation of the Factory pattern with type safety and dependency injection",
    structure={
        "type": "class",
        "name": "{{ factory_name }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._creators: Dict[str, Type[{{ base_class }}]] = {}",
                    "self._dependencies: Dict[str, Any] = {}"
                ]
            },
            {
                "type": "method",
                "name": "register",
                "body": [
                    "def decorator(creator: Type[{{ base_class }}]) -> Type[{{ base_class }}]:",
                    "    self._creators[creator.__name__] = creator",
                    "    return creator",
                    "return decorator"
                ]
            },
            {
                "type": "method",
                "name": "create",
                "body": [
                    "if creator_name not in self._creators:",
                    "    raise ValueError(f'Unknown creator: {creator_name}')",
                    "creator = self._creators[creator_name]",
                    "return creator(**self._dependencies)"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "creator_registration",
            "description": "Ensure creators are properly registered",
            "check": "len(self._creators) > 0"
        },
        {
            "name": "type_safety",
            "description": "Ensure type safety in creator registration",
            "check": "all(issubclass(creator, {{ base_class }}) for creator in self._creators.values())"
        }
    ],
    examples=[
        """
class ProductFactory:
    def __init__(self):
        self._creators: Dict[str, Type[Product]] = {}
        self._dependencies: Dict[str, Any] = {}
        
    def register(self, creator_name: str):
        def decorator(creator: Type[Product]) -> Type[Product]:
            self._creators[creator_name] = creator
            return creator
        return decorator
        
    def create(self, creator_name: str) -> Product:
        if creator_name not in self._creators:
            raise ValueError(f'Unknown creator: {creator_name}')
        creator = self._creators[creator_name]
        return creator(**self._dependencies)
        """
    ],
    anti_patterns=[
        "Direct instantiation without factory",
        "Missing type hints",
        "No dependency injection"
    ],
    best_practices=[
        "Use type hints for better type safety",
        "Implement dependency injection",
        "Handle creation errors gracefully"
    ],
    language="python",
    category="design_pattern"
)

strategy_pattern = CodePattern(
    name="strategy_pattern",
    description="Implementation of the Strategy pattern with runtime strategy switching",
    structure={
        "type": "class",
        "name": "{{ context_name }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._strategy: Optional[{{ strategy_interface }}] = None",
                    "self._strategies: Dict[str, {{ strategy_interface }}] = {}"
                ]
            },
            {
                "type": "method",
                "name": "set_strategy",
                "body": [
                    "if strategy_name not in self._strategies:",
                    "    raise ValueError(f'Unknown strategy: {strategy_name}')",
                    "self._strategy = self._strategies[strategy_name]"
                ]
            },
            {
                "type": "method",
                "name": "execute_strategy",
                "body": [
                    "if self._strategy is None:",
                    "    raise RuntimeError('No strategy set')",
                    "return self._strategy.execute()"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "strategy_availability",
            "description": "Ensure strategies are available",
            "check": "len(self._strategies) > 0"
        },
        {
            "name": "strategy_interface",
            "description": "Ensure strategies implement the interface",
            "check": "all(isinstance(strategy, {{ strategy_interface }}) for strategy in self._strategies.values())"
        }
    ],
    examples=[
        """
class Context:
    def __init__(self):
        self._strategy: Optional[Strategy] = None
        self._strategies: Dict[str, Strategy] = {}
        
    def set_strategy(self, strategy_name: str) -> None:
        if strategy_name not in self._strategies:
            raise ValueError(f'Unknown strategy: {strategy_name}')
        self._strategy = self._strategies[strategy_name]
        
    def execute_strategy(self) -> Any:
        if self._strategy is None:
            raise RuntimeError('No strategy set')
        return self._strategy.execute()
        """
    ],
    anti_patterns=[
        "Hard-coded strategy selection",
        "Missing strategy interface",
        "No strategy validation"
    ],
    best_practices=[
        "Use dependency injection for strategies",
        "Implement strategy validation",
        "Handle strategy execution errors"
    ],
    language="python",
    category="design_pattern"
)

# Enhanced Code Analysis

class SecurityAnalyzer(CodeAnalyzer):
    """Enhanced security analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.security_checks = {
            'sql_injection': self._check_sql_injection,
            'xss_vulnerability': self._check_xss_vulnerability,
            'command_injection': self._check_command_injection,
            'insecure_deserialization': self._check_insecure_deserialization,
            'hardcoded_secrets': self._check_hardcoded_secrets
        }
        
    def _check_sql_injection(self, node: ast.Call) -> None:
        """Check for SQL injection vulnerabilities."""
        if isinstance(node.func, ast.Name) and node.func.id in ['execute', 'executemany']:
            for arg in node.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                    if arg.func.id == 'format' or arg.func.id == 'join':
                        self.analysis['security']['vulnerabilities'].append({
                            'type': 'sql_injection',
                            'line': node.lineno,
                            'description': 'Potential SQL injection vulnerability'
                        })
                        
    def _check_xss_vulnerability(self, node: ast.Call) -> None:
        """Check for XSS vulnerabilities."""
        if isinstance(node.func, ast.Name) and node.func.id in ['render_template', 'render']:
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    for key in arg.keys:
                        if isinstance(key, ast.Constant) and key.value == 'content':
                            self.analysis['security']['vulnerabilities'].append({
                                'type': 'xss_vulnerability',
                                'line': node.lineno,
                                'description': 'Potential XSS vulnerability'
                            })
                            
    def _check_command_injection(self, node: ast.Call) -> None:
        """Check for command injection vulnerabilities."""
        dangerous_functions = ['os.system', 'subprocess.call', 'subprocess.Popen']
        if isinstance(node.func, ast.Attribute):
            func_name = f"{node.func.value.id}.{node.func.attr}"
            if func_name in dangerous_functions:
                self.analysis['security']['vulnerabilities'].append({
                    'type': 'command_injection',
                    'line': node.lineno,
                    'description': 'Potential command injection vulnerability'
                })
                
    def _check_insecure_deserialization(self, node: ast.Call) -> None:
        """Check for insecure deserialization vulnerabilities."""
        if isinstance(node.func, ast.Name) and node.func.id in ['pickle.loads', 'yaml.load']:
            self.analysis['security']['vulnerabilities'].append({
                'type': 'insecure_deserialization',
                'line': node.lineno,
                'description': 'Potential insecure deserialization vulnerability'
            })
            
    def _check_hardcoded_secrets(self, node: ast.Assign) -> None:
        """Check for hardcoded secrets."""
        secret_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'key\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        for target in node.targets:
            if isinstance(target, ast.Name):
                for pattern in secret_patterns:
                    if re.match(pattern, target.id):
                        self.analysis['security']['vulnerabilities'].append({
                            'type': 'hardcoded_secret',
                            'line': node.lineno,
                            'description': 'Potential hardcoded secret'
                        })

class PerformanceAnalyzer(CodeAnalyzer):
    """Enhanced performance analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.performance_metrics = {
            'memory_usage': self._analyze_memory_usage,
            'cpu_usage': self._analyze_cpu_usage,
            'io_operations': self._analyze_io_operations,
            'network_calls': self._analyze_network_calls
        }
        
    def _analyze_memory_usage(self, node: ast.Call) -> None:
        """Analyze memory usage patterns."""
        if isinstance(node.func, ast.Name):
            if node.func.id in ['append', 'extend', 'update']:
                self.analysis['performance']['metrics']['memory_operations'] = \
                    self.analysis['performance']['metrics'].get('memory_operations', 0) + 1
                    
    def _analyze_cpu_usage(self, node: ast.Call) -> None:
        """Analyze CPU usage patterns."""
        cpu_intensive = ['sort', 'filter', 'map', 'reduce']
        if isinstance(node.func, ast.Name) and node.func.id in cpu_intensive:
            self.analysis['performance']['metrics']['cpu_operations'] = \
                self.analysis['performance']['metrics'].get('cpu_operations', 0) + 1
                
    def _analyze_io_operations(self, node: ast.Call) -> None:
        """Analyze I/O operation patterns."""
        io_operations = ['open', 'read', 'write', 'seek']
        if isinstance(node.func, ast.Name) and node.func.id in io_operations:
            self.analysis['performance']['metrics']['io_operations'] = \
                self.analysis['performance']['metrics'].get('io_operations', 0) + 1
                
    def _analyze_network_calls(self, node: ast.Call) -> None:
        """Analyze network call patterns."""
        network_calls = ['requests.get', 'requests.post', 'urllib.request.urlopen']
        if isinstance(node.func, ast.Attribute):
            func_name = f"{node.func.value.id}.{node.func.attr}"
            if func_name in network_calls:
                self.analysis['performance']['metrics']['network_calls'] = \
                    self.analysis['performance']['metrics'].get('network_calls', 0) + 1

# Specialized Documentation Templates

api_documentation_template = DocumentationTemplate(
    name="api_documentation",
    description="Template for generating API documentation with OpenAPI/Swagger support",
    content="""
# {{ title }} API Documentation

## Overview
{{ overview }}

## Base URL
{{ base_url }}

## Authentication
{{ authentication }}

## Endpoints

{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}
{{ endpoint.description }}

#### Parameters
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}) - {{ param.description }}
{% endfor %}

#### Request Body
{{ endpoint.request_body }}

#### Response
{{ endpoint.response }}

#### Example
```{{ endpoint.example_language }}
{{ endpoint.example }}
```
{% endfor %}

## Error Codes
{% for error in error_codes %}
- `{{ error.code }}`: {{ error.description }}
{% endfor %}

## Rate Limiting
{{ rate_limiting }}

## Version History
{% for version in versions %}
### {{ version.number }}
- {{ version.changes }}
{% endfor %}
""",
    parameters={
        "title": str,
        "overview": str,
        "base_url": str,
        "authentication": str,
        "endpoints": List[Dict[str, Any]],
        "error_codes": List[Dict[str, Any]],
        "rate_limiting": str,
        "versions": List[Dict[str, Any]]
    }
)

architecture_documentation_template = DocumentationTemplate(
    name="architecture_documentation",
    description="Template for generating system architecture documentation",
    content="""
# {{ system_name }} Architecture Documentation

## System Overview
{{ overview }}

## Architecture Diagram
{{ diagram }}

## Components

{% for component in components %}
### {{ component.name }}
{{ component.description }}

#### Responsibilities
{% for responsibility in component.responsibilities %}
- {{ responsibility }}
{% endfor %}

#### Dependencies
{% for dependency in component.dependencies %}
- {{ dependency }}
{% endfor %}

#### Interfaces
{% for interface in component.interfaces %}
- {{ interface }}
{% endfor %}
{% endfor %}

## Data Flow
{{ data_flow }}

## Security Architecture
{{ security_architecture }}

## Deployment Architecture
{{ deployment_architecture }}

## Scalability Considerations
{{ scalability }}

## Monitoring and Logging
{{ monitoring }}

## Disaster Recovery
{{ disaster_recovery }}
""",
    parameters={
        "system_name": str,
        "overview": str,
        "diagram": str,
        "components": List[Dict[str, Any]],
        "data_flow": str,
        "security_architecture": str,
        "deployment_architecture": str,
        "scalability": str,
        "monitoring": str,
        "disaster_recovery": str
    }
) 