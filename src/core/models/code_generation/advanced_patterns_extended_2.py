"""
Extended advanced patterns, security checks, performance metrics, and documentation templates.
"""

from typing import Dict, List, Any, Optional, Type, Callable, Protocol
from datetime import datetime
from .advanced_patterns import (
    CodePattern, SecurityAnalyzer, PerformanceAnalyzer,
    DocumentationTemplate
)

# Additional Design Patterns

chain_of_responsibility_pattern = CodePattern(
    name="chain_of_responsibility_pattern",
    description="Implementation of the Chain of Responsibility pattern with dynamic chain building",
    structure={
        "type": "class",
        "name": "{{ handler_base }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._next_handler: Optional[{{ handler_base }}] = None",
                    "self._handler_type: str = '{{ handler_type }}'"
                ]
            },
            {
                "type": "method",
                "name": "set_next",
                "body": [
                    "self._next_handler = handler",
                    "return handler"
                ]
            },
            {
                "type": "method",
                "name": "handle",
                "body": [
                    "if self._can_handle(request):",
                    "    return self._process_request(request)",
                    "if self._next_handler:",
                    "    return self._next_handler.handle(request)",
                    "raise RuntimeError('No handler can process the request')"
                ]
            },
            {
                "type": "method",
                "name": "_can_handle",
                "body": [
                    "raise NotImplementedError('Subclasses must implement _can_handle')"
                ]
            },
            {
                "type": "method",
                "name": "_process_request",
                "body": [
                    "raise NotImplementedError('Subclasses must implement _process_request')"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "handler_chain",
            "description": "Ensure handler chain is properly constructed",
            "check": "self._next_handler is None or isinstance(self._next_handler, {{ handler_base }})"
        },
        {
            "name": "handler_type",
            "description": "Ensure handler type is set",
            "check": "self._handler_type is not None"
        }
    ],
    examples=[
        """
class Handler:
    def __init__(self, handler_type: str):
        self._next_handler: Optional[Handler] = None
        self._handler_type = handler_type
        
    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler
        
    def handle(self, request: Any) -> Any:
        if self._can_handle(request):
            return self._process_request(request)
        if self._next_handler:
            return self._next_handler.handle(request)
        raise RuntimeError('No handler can process the request')
        
    def _can_handle(self, request: Any) -> bool:
        raise NotImplementedError('Subclasses must implement _can_handle')
        
    def _process_request(self, request: Any) -> Any:
        raise NotImplementedError('Subclasses must implement _process_request')
        """
    ],
    anti_patterns=[
        "Missing next handler check",
        "No handler type specification",
        "Incomplete chain"
    ],
    best_practices=[
        "Implement proper chain termination",
        "Use handler type for identification",
        "Handle all possible request types"
    ],
    language="python",
    category="design_pattern"
)

mediator_pattern = CodePattern(
    name="mediator_pattern",
    description="Implementation of the Mediator pattern with event handling",
    structure={
        "type": "class",
        "name": "{{ mediator_base }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._colleagues: Dict[str, {{ colleague_type }}] = {}",
                    "self._event_handlers: Dict[str, List[Callable]] = {}"
                ]
            },
            {
                "type": "method",
                "name": "register_colleague",
                "body": [
                    "self._colleagues[colleague.id] = colleague",
                    "colleague.set_mediator(self)"
                ]
            },
            {
                "type": "method",
                "name": "notify",
                "body": [
                    "event = event_data.get('event')",
                    "if event in self._event_handlers:",
                    "    for handler in self._event_handlers[event]:",
                    "        handler(event_data)"
                ]
            },
            {
                "type": "method",
                "name": "add_event_handler",
                "body": [
                    "if event not in self._event_handlers:",
                    "    self._event_handlers[event] = []",
                    "self._event_handlers[event].append(handler)"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "colleague_registration",
            "description": "Ensure colleagues are properly registered",
            "check": "all(isinstance(colleague, {{ colleague_type }}) for colleague in self._colleagues.values())"
        },
        {
            "name": "event_handlers",
            "description": "Ensure event handlers are properly registered",
            "check": "all(isinstance(handlers, list) for handlers in self._event_handlers.values())"
        }
    ],
    examples=[
        """
class Mediator:
    def __init__(self):
        self._colleagues: Dict[str, Colleague] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        
    def register_colleague(self, colleague: Colleague) -> None:
        self._colleagues[colleague.id] = colleague
        colleague.set_mediator(self)
        
    def notify(self, event_data: Dict[str, Any]) -> None:
        event = event_data.get('event')
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                handler(event_data)
                
    def add_event_handler(self, event: str, handler: Callable) -> None:
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        """
    ],
    anti_patterns=[
        "Direct colleague communication",
        "Missing event handlers",
        "Incomplete colleague registration"
    ],
    best_practices=[
        "Use event-based communication",
        "Implement proper error handling",
        "Maintain colleague references"
    ],
    language="python",
    category="design_pattern"
)

memento_pattern = CodePattern(
    name="memento_pattern",
    description="Implementation of the Memento pattern with state history",
    structure={
        "type": "class",
        "name": "{{ originator_base }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._state: Dict[str, Any] = {}",
                    "self._history: List[{{ memento_type }}] = []"
                ]
            },
            {
                "type": "method",
                "name": "create_memento",
                "body": [
                    "memento = {{ memento_type }}(self._state.copy())",
                    "self._history.append(memento)",
                    "return memento"
                ]
            },
            {
                "type": "method",
                "name": "restore_from_memento",
                "body": [
                    "if not self._history:",
                    "    raise RuntimeError('No mementos available')",
                    "memento = self._history.pop()",
                    "self._state = memento.get_state().copy()"
                ]
            },
            {
                "type": "method",
                "name": "get_state",
                "body": [
                    "return self._state.copy()"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "state_management",
            "description": "Ensure state is properly managed",
            "check": "isinstance(self._state, dict)"
        },
        {
            "name": "history_management",
            "description": "Ensure history is properly maintained",
            "check": "all(isinstance(memento, {{ memento_type }}) for memento in self._history)"
        }
    ],
    examples=[
        """
class Originator:
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._history: List[Memento] = []
        
    def create_memento(self) -> Memento:
        memento = Memento(self._state.copy())
        self._history.append(memento)
        return memento
        
    def restore_from_memento(self) -> None:
        if not self._history:
            raise RuntimeError('No mementos available')
        memento = self._history.pop()
        self._state = memento.get_state().copy()
        
    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()
        """
    ],
    anti_patterns=[
        "Direct state modification",
        "Missing state history",
        "Incomplete state restoration"
    ],
    best_practices=[
        "Use immutable state",
        "Implement proper history management",
        "Handle state restoration errors"
    ],
    language="python",
    category="design_pattern"
)

# Enhanced Security Analysis

class ExtendedSecurityAnalyzer2(SecurityAnalyzer):
    """Extended security analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.security_checks.update({
            'api_security': self._check_api_security,
            'file_system_security': self._check_file_system_security,
            'network_security': self._check_network_security,
            'data_security': self._check_data_security
        })
        
    def _check_api_security(self, node: ast.Call) -> None:
        """Check for API security vulnerabilities."""
        api_patterns = {
            'rate_limiting': ['rate_limit', 'throttle'],
            'input_validation': ['validate_input', 'sanitize_input'],
            'authentication': ['authenticate', 'verify_token'],
            'authorization': ['authorize', 'check_permission']
        }
        
        for category, patterns in api_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                if not any(
                    isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                    and arg.func.id in ['validate', 'sanitize', 'escape']
                    for arg in node.args
                ):
                    self.analysis['security']['vulnerabilities'].append({
                        'type': f'weak_api_{category}',
                        'line': node.lineno,
                        'description': f'Potential weak API {category}'
                    })
                    
    def _check_file_system_security(self, node: ast.Call) -> None:
        """Check for file system security vulnerabilities."""
        fs_patterns = {
            'file_operations': ['open', 'read', 'write'],
            'path_operations': ['join', 'abspath', 'realpath'],
            'permission_operations': ['chmod', 'chown']
        }
        
        for category, patterns in fs_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                if not any(
                    isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                    and arg.func.id in ['secure_path', 'validate_path']
                    for arg in node.args
                ):
                    self.analysis['security']['vulnerabilities'].append({
                        'type': f'weak_file_system_{category}',
                        'line': node.lineno,
                        'description': f'Potential weak file system {category}'
                    })
                    
    def _check_network_security(self, node: ast.Call) -> None:
        """Check for network security vulnerabilities."""
        network_patterns = {
            'connection': ['connect', 'bind', 'listen'],
            'data_transfer': ['send', 'receive', 'transfer'],
            'protocol': ['http', 'https', 'ftp']
        }
        
        for category, patterns in network_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                if not any(
                    isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                    and arg.func.id in ['secure_connection', 'validate_certificate']
                    for arg in node.args
                ):
                    self.analysis['security']['vulnerabilities'].append({
                        'type': f'weak_network_{category}',
                        'line': node.lineno,
                        'description': f'Potential weak network {category}'
                    })
                    
    def _check_data_security(self, node: ast.Call) -> None:
        """Check for data security vulnerabilities."""
        data_patterns = {
            'storage': ['store', 'save', 'persist'],
            'retrieval': ['get', 'fetch', 'retrieve'],
            'transmission': ['send', 'transmit', 'transfer']
        }
        
        for category, patterns in data_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                if not any(
                    isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                    and arg.func.id in ['encrypt', 'decrypt', 'hash']
                    for arg in node.args
                ):
                    self.analysis['security']['vulnerabilities'].append({
                        'type': f'weak_data_{category}',
                        'line': node.lineno,
                        'description': f'Potential weak data {category}'
                    })

# Enhanced Performance Analysis

class ExtendedPerformanceAnalyzer2(PerformanceAnalyzer):
    """Extended performance analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.performance_metrics.update({
            'memory_profiling': self._analyze_memory_profiling,
            'cpu_profiling': self._analyze_cpu_profiling,
            'io_profiling': self._analyze_io_profiling,
            'resource_usage': self._analyze_resource_usage
        })
        
    def _analyze_memory_profiling(self, node: ast.Call) -> None:
        """Analyze memory usage patterns."""
        memory_patterns = {
            'allocation': ['malloc', 'new', 'allocate'],
            'deallocation': ['free', 'delete', 'deallocate'],
            'garbage_collection': ['gc', 'collect', 'cleanup']
        }
        
        for category, patterns in memory_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                self.analysis['performance']['metrics'][f'memory_{category}'] = \
                    self.analysis['performance']['metrics'].get(f'memory_{category}', 0) + 1
                    
    def _analyze_cpu_profiling(self, node: ast.Call) -> None:
        """Analyze CPU usage patterns."""
        cpu_patterns = {
            'computation': ['compute', 'calculate', 'process'],
            'threading': ['thread', 'process', 'task'],
            'scheduling': ['schedule', 'plan', 'queue']
        }
        
        for category, patterns in cpu_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                self.analysis['performance']['metrics'][f'cpu_{category}'] = \
                    self.analysis['performance']['metrics'].get(f'cpu_{category}', 0) + 1
                    
    def _analyze_io_profiling(self, node: ast.Call) -> None:
        """Analyze I/O operation patterns."""
        io_patterns = {
            'file_io': ['read', 'write', 'open'],
            'network_io': ['send', 'receive', 'connect'],
            'database_io': ['query', 'execute', 'commit']
        }
        
        for category, patterns in io_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                self.analysis['performance']['metrics'][f'io_{category}'] = \
                    self.analysis['performance']['metrics'].get(f'io_{category}', 0) + 1
                    
    def _analyze_resource_usage(self, node: ast.Call) -> None:
        """Analyze resource usage patterns."""
        resource_patterns = {
            'connection_pooling': ['acquire', 'release', 'pool'],
            'caching': ['cache', 'memoize', 'store'],
            'resource_management': ['manage', 'allocate', 'deallocate']
        }
        
        for category, patterns in resource_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                self.analysis['performance']['metrics'][f'resource_{category}'] = \
                    self.analysis['performance']['metrics'].get(f'resource_{category}', 0) + 1

# Additional Documentation Templates

api_documentation_template = DocumentationTemplate(
    name="api_documentation",
    description="Template for generating API documentation",
    content="""
# {{ api_name }} API Documentation

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
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}

#### Request Body
```json
{{ endpoint.request_body }}
```

#### Response
```json
{{ endpoint.response }}
```

#### Error Codes
{% for error in endpoint.error_codes %}
- `{{ error.code }}`: {{ error.description }}
{% endfor %}
{% endfor %}

## Rate Limiting
{{ rate_limiting }}

## Version History
{{ version_history }}

## Examples
{{ examples }}
""",
    parameters={
        "api_name": str,
        "overview": str,
        "base_url": str,
        "authentication": str,
        "endpoints": List[Dict[str, Any]],
        "rate_limiting": str,
        "version_history": str,
        "examples": str
    }
)

architecture_documentation_template = DocumentationTemplate(
    name="architecture_documentation",
    description="Template for generating architecture documentation",
    content="""
# {{ system_name }} Architecture Documentation

## System Overview
{{ system_overview }}

## Architecture Diagram
{{ architecture_diagram }}

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
{{ scalability_considerations }}

## Monitoring and Logging
{{ monitoring_logging }}

## Disaster Recovery
{{ disaster_recovery }}
""",
    parameters={
        "system_name": str,
        "system_overview": str,
        "architecture_diagram": str,
        "components": List[Dict[str, Any]],
        "data_flow": str,
        "security_architecture": str,
        "deployment_architecture": str,
        "scalability_considerations": str,
        "monitoring_logging": str,
        "disaster_recovery": str
    }
)

development_guide_template = DocumentationTemplate(
    name="development_guide",
    description="Template for generating development guides",
    content="""
# {{ project_name }} Development Guide

## Development Environment Setup

{% for step in setup_steps %}
### {{ step.title }}
{{ step.description }}

#### Prerequisites
{% for prereq in step.prerequisites %}
- {{ prereq }}
{% endfor %}

#### Installation
{{ step.installation }}

#### Configuration
{{ step.configuration }}
{% endfor %}

## Code Style Guide
{{ code_style_guide }}

## Testing Guidelines

{% for guideline in testing_guidelines %}
### {{ guideline.title }}
{{ guideline.description }}

#### Examples
{{ guideline.examples }}
{% endfor %}

## Debugging Guide
{{ debugging_guide }}

## Performance Optimization
{{ performance_optimization }}

## Security Guidelines
{{ security_guidelines }}

## Deployment Process
{{ deployment_process }}

## Contributing Guidelines
{{ contributing_guidelines }}

## Troubleshooting
{{ troubleshooting }}
""",
    parameters={
        "project_name": str,
        "setup_steps": List[Dict[str, Any]],
        "code_style_guide": str,
        "testing_guidelines": List[Dict[str, Any]],
        "debugging_guide": str,
        "performance_optimization": str,
        "security_guidelines": str,
        "deployment_process": str,
        "contributing_guidelines": str,
        "troubleshooting": str
    }
) 