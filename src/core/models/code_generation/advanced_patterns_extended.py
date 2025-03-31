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

command_pattern = CodePattern(
    name="command_pattern",
    description="Implementation of the Command pattern with undo/redo support",
    structure={
        "type": "class",
        "name": "{{ command_base }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._receiver = receiver",
                    "self._history: List[Dict[str, Any]] = []"
                ]
            },
            {
                "type": "method",
                "name": "execute",
                "body": [
                    "result = self._receiver.{{ action }}(*args, **kwargs)",
                    "self._history.append({'action': '{{ action }}', 'args': args, 'kwargs': kwargs})",
                    "return result"
                ]
            },
            {
                "type": "method",
                "name": "undo",
                "body": [
                    "if not self._history:",
                    "    raise RuntimeError('No commands to undo')",
                    "last_command = self._history.pop()",
                    "return self._receiver.{{ undo_action }}(*last_command['args'], **last_command['kwargs'])"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "command_history",
            "description": "Ensure command history is maintained",
            "check": "len(self._history) >= 0"
        },
        {
            "name": "receiver_existence",
            "description": "Ensure receiver exists",
            "check": "self._receiver is not None"
        }
    ],
    examples=[
        """
class DocumentCommand:
    def __init__(self, document):
        self._document = document
        self._history = []
        
    def execute(self, text):
        result = self._document.insert(text)
        self._history.append({'action': 'insert', 'args': (text,)})
        return result
        
    def undo(self):
        if not self._history:
            raise RuntimeError('No commands to undo')
        last_command = self._history.pop()
        return self._document.delete(*last_command['args'])
        """
    ],
    anti_patterns=[
        "Missing undo functionality",
        "No command history",
        "Direct receiver manipulation"
    ],
    best_practices=[
        "Implement undo/redo functionality",
        "Maintain command history",
        "Use command composition"
    ],
    language="python",
    category="design_pattern"
)

state_pattern = CodePattern(
    name="state_pattern",
    description="Implementation of the State pattern with state transitions",
    structure={
        "type": "class",
        "name": "{{ context_name }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._state: Optional[{{ state_interface }}] = None",
                    "self._states: Dict[str, {{ state_interface }}] = {}"
                ]
            },
            {
                "type": "method",
                "name": "set_state",
                "body": [
                    "if state_name not in self._states:",
                    "    raise ValueError(f'Unknown state: {state_name}')",
                    "self._state = self._states[state_name]",
                    "self._state.on_enter()"
                ]
            },
            {
                "type": "method",
                "name": "handle_event",
                "body": [
                    "if self._state is None:",
                    "    raise RuntimeError('No state set')",
                    "return self._state.handle_event(event)"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "state_transition",
            "description": "Ensure valid state transitions",
            "check": "self._state in self._states.values()"
        },
        {
            "name": "state_interface",
            "description": "Ensure states implement the interface",
            "check": "all(isinstance(state, {{ state_interface }}) for state in self._states.values())"
        }
    ],
    examples=[
        """
class Context:
    def __init__(self):
        self._state: Optional[State] = None
        self._states: Dict[str, State] = {}
        
    def set_state(self, state_name: str) -> None:
        if state_name not in self._states:
            raise ValueError(f'Unknown state: {state_name}')
        self._state = self._states[state_name]
        self._state.on_enter()
        
    def handle_event(self, event: str) -> Any:
        if self._state is None:
            raise RuntimeError('No state set')
        return self._state.handle_event(event)
        """
    ],
    anti_patterns=[
        "Hard-coded state transitions",
        "Missing state interface",
        "No state validation"
    ],
    best_practices=[
        "Use state machine for transitions",
        "Implement state validation",
        "Handle state entry/exit"
    ],
    language="python",
    category="design_pattern"
)

template_method_pattern = CodePattern(
    name="template_method_pattern",
    description="Implementation of the Template Method pattern with hooks",
    structure={
        "type": "class",
        "name": "{{ abstract_class }}",
        "methods": [
            {
                "type": "method",
                "name": "template_method",
                "body": [
                    "self._before_hook()",
                    "self._primary_operation()",
                    "self._after_hook()"
                ]
            },
            {
                "type": "method",
                "name": "_before_hook",
                "body": [
                    "pass"
                ]
            },
            {
                "type": "method",
                "name": "_after_hook",
                "body": [
                    "pass"
                ]
            },
            {
                "type": "method",
                "name": "_primary_operation",
                "body": [
                    "raise NotImplementedError('Subclasses must implement _primary_operation')"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "hook_implementation",
            "description": "Ensure hooks are implemented",
            "check": "hasattr(self, '_before_hook') and hasattr(self, '_after_hook')"
        },
        {
            "name": "primary_operation",
            "description": "Ensure primary operation is implemented",
            "check": "hasattr(self, '_primary_operation')"
        }
    ],
    examples=[
        """
class AbstractClass:
    def template_method(self):
        self._before_hook()
        self._primary_operation()
        self._after_hook()
        
    def _before_hook(self):
        pass
        
    def _after_hook(self):
        pass
        
    def _primary_operation(self):
        raise NotImplementedError('Subclasses must implement _primary_operation')
        """
    ],
    anti_patterns=[
        "Overriding template method",
        "Missing hook methods",
        "No error handling"
    ],
    best_practices=[
        "Use hooks for customization",
        "Implement proper error handling",
        "Document hook purposes"
    ],
    language="python",
    category="design_pattern"
)

# Enhanced Security Analysis

class ExtendedSecurityAnalyzer(SecurityAnalyzer):
    """Extended security analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.security_checks.update({
            'authentication': self._check_authentication,
            'authorization': self._check_authorization,
            'encryption': self._check_encryption,
            'session_management': self._check_session_management,
            'input_validation': self._check_input_validation
        })
        
    def _check_authentication(self, node: ast.Call) -> None:
        """Check for authentication vulnerabilities."""
        auth_functions = ['login', 'authenticate', 'verify_token']
        if isinstance(node.func, ast.Name) and node.func.id in auth_functions:
            for arg in node.args:
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                    if arg.func.id == 'hash' and not any(
                        isinstance(a, ast.Constant) and a.value in ['sha256', 'bcrypt']
                        for a in arg.args
                    ):
                        self.analysis['security']['vulnerabilities'].append({
                            'type': 'weak_authentication',
                            'line': node.lineno,
                            'description': 'Potential weak authentication method'
                        })
                        
    def _check_authorization(self, node: ast.Call) -> None:
        """Check for authorization vulnerabilities."""
        authz_functions = ['check_permission', 'has_access', 'is_authorized']
        if isinstance(node.func, ast.Name) and node.func.id in authz_functions:
            if not any(
                isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                and arg.func.id in ['verify_role', 'validate_token']
                for arg in node.args
            ):
                self.analysis['security']['vulnerabilities'].append({
                    'type': 'weak_authorization',
                    'line': node.lineno,
                    'description': 'Potential weak authorization check'
                })
                
    def _check_encryption(self, node: ast.Call) -> None:
        """Check for encryption vulnerabilities."""
        crypto_functions = ['encrypt', 'decrypt', 'hash']
        if isinstance(node.func, ast.Name) and node.func.id in crypto_functions:
            if not any(
                isinstance(arg, ast.Constant) and arg.value in ['AES', 'RSA', 'SHA256']
                for arg in node.args
            ):
                self.analysis['security']['vulnerabilities'].append({
                    'type': 'weak_encryption',
                    'line': node.lineno,
                    'description': 'Potential weak encryption method'
                })
                
    def _check_session_management(self, node: ast.Call) -> None:
        """Check for session management vulnerabilities."""
        session_functions = ['create_session', 'get_session', 'destroy_session']
        if isinstance(node.func, ast.Name) and node.func.id in session_functions:
            if not any(
                isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                and arg.func.id in ['set_expiry', 'regenerate_id']
                for arg in node.args
            ):
                self.analysis['security']['vulnerabilities'].append({
                    'type': 'weak_session_management',
                    'line': node.lineno,
                    'description': 'Potential weak session management'
                })
                
    def _check_input_validation(self, node: ast.Call) -> None:
        """Check for input validation vulnerabilities."""
        validation_functions = ['validate', 'sanitize', 'clean']
        if isinstance(node.func, ast.Name) and node.func.id in validation_functions:
            if not any(
                isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name)
                and arg.func.id in ['escape', 'strip', 'validate_type']
                for arg in node.args
            ):
                self.analysis['security']['vulnerabilities'].append({
                    'type': 'weak_input_validation',
                    'line': node.lineno,
                    'description': 'Potential weak input validation'
                })

# Enhanced Performance Analysis

class ExtendedPerformanceAnalyzer(PerformanceAnalyzer):
    """Extended performance analysis capabilities."""
    
    def __init__(self):
        super().__init__()
        self.performance_metrics.update({
            'concurrency': self._analyze_concurrency,
            'caching': self._analyze_caching,
            'database': self._analyze_database,
            'resource_management': self._analyze_resource_management
        })
        
    def _analyze_concurrency(self, node: ast.Call) -> None:
        """Analyze concurrency patterns."""
        concurrency_patterns = {
            'threading': ['Thread', 'Lock', 'RLock'],
            'asyncio': ['create_task', 'gather', 'wait'],
            'multiprocessing': ['Process', 'Pool', 'Queue']
        }
        
        for category, patterns in concurrency_patterns.items():
            if isinstance(node.func, ast.Name) and node.func.id in patterns:
                self.analysis['performance']['metrics'][f'{category}_operations'] = \
                    self.analysis['performance']['metrics'].get(f'{category}_operations', 0) + 1
                    
    def _analyze_caching(self, node: ast.Call) -> None:
        """Analyze caching patterns."""
        caching_patterns = ['cache', 'memoize', 'lru_cache']
        if isinstance(node.func, ast.Name) and node.func.id in caching_patterns:
            self.analysis['performance']['metrics']['caching_operations'] = \
                self.analysis['performance']['metrics'].get('caching_operations', 0) + 1
                
    def _analyze_database(self, node: ast.Call) -> None:
        """Analyze database operations."""
        db_patterns = ['execute', 'commit', 'rollback', 'fetchall']
        if isinstance(node.func, ast.Name) and node.func.id in db_patterns:
            self.analysis['performance']['metrics']['database_operations'] = \
                self.analysis['performance']['metrics'].get('database_operations', 0) + 1
                
    def _analyze_resource_management(self, node: ast.Call) -> None:
        """Analyze resource management patterns."""
        resource_patterns = ['open', 'close', 'acquire', 'release']
        if isinstance(node.func, ast.Name) and node.func.id in resource_patterns:
            self.analysis['performance']['metrics']['resource_operations'] = \
                self.analysis['performance']['metrics'].get('resource_operations', 0) + 1

# Additional Documentation Templates

deployment_guide_template = DocumentationTemplate(
    name="deployment_guide",
    description="Template for generating deployment guides",
    content="""
# {{ system_name }} Deployment Guide

## Prerequisites
{{ prerequisites }}

## System Requirements
{{ system_requirements }}

## Installation Steps

{% for step in installation_steps %}
### {{ step.title }}
{{ step.description }}

#### Commands
```bash
{{ step.commands }}
```

#### Verification
{{ step.verification }}
{% endfor %}

## Configuration

{% for config in configurations %}
### {{ config.name }}
{{ config.description }}

#### Required Settings
{% for setting in config.settings %}
- `{{ setting.name }}`: {{ setting.description }}
{% endfor %}
{% endfor %}

## Environment Setup
{{ environment_setup }}

## Security Considerations
{{ security_considerations }}

## Monitoring Setup
{{ monitoring_setup }}

## Backup and Recovery
{{ backup_recovery }}

## Troubleshooting
{{ troubleshooting }}
""",
    parameters={
        "system_name": str,
        "prerequisites": str,
        "system_requirements": str,
        "installation_steps": List[Dict[str, Any]],
        "configurations": List[Dict[str, Any]],
        "environment_setup": str,
        "security_considerations": str,
        "monitoring_setup": str,
        "backup_recovery": str,
        "troubleshooting": str
    }
)

user_manual_template = DocumentationTemplate(
    name="user_manual",
    description="Template for generating user manuals",
    content="""
# {{ product_name }} User Manual

## Introduction
{{ introduction }}

## Getting Started

{% for step in getting_started %}
### {{ step.title }}
{{ step.description }}

{% if step.screenshot %}
![{{ step.title }}]({{ step.screenshot }})
{% endif %}
{% endfor %}

## Features

{% for feature in features %}
### {{ feature.name }}
{{ feature.description }}

#### Usage
{{ feature.usage }}

#### Examples
{% for example in feature.examples %}
```{{ example.language }}
{{ example.code }}
```
{% endfor %}
{% endfor %}

## Configuration

{% for config in configurations %}
### {{ config.name }}
{{ config.description }}

#### Options
{% for option in config.options %}
- `{{ option.name }}`: {{ option.description }}
{% endfor %}
{% endfor %}

## Troubleshooting

{% for issue in troubleshooting %}
### {{ issue.title }}
{{ issue.description }}

#### Solution
{{ issue.solution }}
{% endfor %}

## FAQ
{{ faq }}

## Support
{{ support }}
""",
    parameters={
        "product_name": str,
        "introduction": str,
        "getting_started": List[Dict[str, Any]],
        "features": List[Dict[str, Any]],
        "configurations": List[Dict[str, Any]],
        "troubleshooting": List[Dict[str, Any]],
        "faq": str,
        "support": str
    }
)

troubleshooting_guide_template = DocumentationTemplate(
    name="troubleshooting_guide",
    description="Template for generating troubleshooting guides",
    content="""
# {{ system_name }} Troubleshooting Guide

## Common Issues

{% for issue in common_issues %}
### {{ issue.title }}
{{ issue.description }}

#### Symptoms
{{ issue.symptoms }}

#### Causes
{{ issue.causes }}

#### Solutions
{% for solution in issue.solutions %}
1. {{ solution }}
{% endfor %}

#### Prevention
{{ issue.prevention }}
{% endfor %}

## Error Messages

{% for error in error_messages %}
### {{ error.code }}
{{ error.description }}

#### Possible Causes
{{ error.causes }}

#### Resolution Steps
{% for step in error.steps %}
1. {{ step }}
{% endfor %}
{% endfor %}

## Performance Issues

{% for issue in performance_issues %}
### {{ issue.title }}
{{ issue.description }}

#### Indicators
{{ issue.indicators }}

#### Diagnosis
{{ issue.diagnosis }}

#### Solutions
{% for solution in issue.solutions %}
1. {{ solution }}
{% endfor %}
{% endfor %}

## Network Issues

{% for issue in network_issues %}
### {{ issue.title }}
{{ issue.description }}

#### Symptoms
{{ issue.symptoms }}

#### Diagnosis Steps
{% for step in issue.diagnosis_steps %}
1. {{ step }}
{% endfor %}

#### Solutions
{% for solution in issue.solutions %}
1. {{ solution }}
{% endfor %}
{% endfor %}

## Support Resources
{{ support_resources }}
""",
    parameters={
        "system_name": str,
        "common_issues": List[Dict[str, Any]],
        "error_messages": List[Dict[str, Any]],
        "performance_issues": List[Dict[str, Any]],
        "network_issues": List[Dict[str, Any]],
        "support_resources": str
    }
) 