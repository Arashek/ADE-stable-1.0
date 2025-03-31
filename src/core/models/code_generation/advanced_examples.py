"""
Advanced examples and enhanced capabilities for the code generation system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .code_generation import (
    CodeTemplate, CodePattern, DocumentationTemplate,
    CodeGenerator, CodeAnalyzer
)

# Additional Template Examples

class_template_with_inheritance = CodeTemplate(
    name="class_with_inheritance",
    description="Template for generating Python classes with inheritance and mixins",
    content="""
class {{ class_name }}({% for base in bases %}{{ base }}{% if not loop.last %}, {% endif %}{% endfor %}):
    \"\"\"{{ docstring }}\"\"\"
    
    def __init__(self{% for param in parameters %}, {{ param }}{% endfor %}{% if parent_init %}, *args, **kwargs{% endif %}):
        {% if parent_init %}
        super().__init__(*args, **kwargs)
        {% endif %}
        {% for param in parameters %}
        self.{{ param }} = {{ param }}
        {% endfor %}
        
    {% for method in methods %}
    def {{ method.name }}(self{% for arg in method.args %}, {{ arg.name }}: {{ arg.type }}{% endfor %}) -> {{ method.return_type }}:
        \"\"\"{{ method.docstring }}\"\"\"
        {{ method.body }}
    {% endfor %}
    
    {% for property in properties %}
    @property
    def {{ property.name }}(self) -> {{ property.type }}:
        \"\"\"{{ property.docstring }}\"\"\"
        return {{ property.body }}
    {% endfor %}
""",
    parameters={
        "class_name": str,
        "bases": List[str],
        "docstring": str,
        "parameters": List[str],
        "parent_init": bool,
        "methods": List[Dict[str, Any]],
        "properties": List[Dict[str, Any]]
    },
    tags=["python", "class", "inheritance"],
    language="python",
    category="class",
    version="1.0.0",
    author="System",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

async_class_template = CodeTemplate(
    name="async_class",
    description="Template for generating asynchronous Python classes",
    content="""
import asyncio
from typing import {% for type in types %}{{ type }}{% if not loop.last %}, {% endif %}{% endfor %}

class {{ class_name }}:
    \"\"\"{{ docstring }}\"\"\"
    
    def __init__(self{% for param in parameters %}, {{ param }}{% endfor %}):
        {% for param in parameters %}
        self.{{ param }} = {{ param }}
        {% endfor %}
        self._lock = asyncio.Lock()
        
    {% for method in methods %}
    async def {{ method.name }}(self{% for arg in method.args %}, {{ arg.name }}: {{ arg.type }}{% endfor %}) -> {{ method.return_type }}:
        \"\"\"{{ method.docstring }}\"\"\"
        async with self._lock:
            {{ method.body }}
    {% endfor %}
    
    {% for property in properties %}
    @property
    async def {{ property.name }}(self) -> {{ property.type }}:
        \"\"\"{{ property.docstring }}\"\"\"
        async with self._lock:
            return {{ property.body }}
    {% endfor %}
""",
    parameters={
        "class_name": str,
        "docstring": str,
        "parameters": List[str],
        "types": List[str],
        "methods": List[Dict[str, Any]],
        "properties": List[Dict[str, Any]]
    },
    tags=["python", "class", "async"],
    language="python",
    category="class",
    version="1.0.0",
    author="System",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

# Additional Pattern Examples

observer_pattern = CodePattern(
    name="observer_pattern",
    description="Implementation of the Observer pattern with async support",
    structure={
        "type": "class",
        "name": "{{ subject_name }}",
        "methods": [
            {
                "type": "method",
                "name": "__init__",
                "body": [
                    "self._observers = set()",
                    "self._lock = asyncio.Lock()"
                ]
            },
            {
                "type": "method",
                "name": "add_observer",
                "body": [
                    "async with self._lock:",
                    "    self._observers.add(observer)"
                ]
            },
            {
                "type": "method",
                "name": "remove_observer",
                "body": [
                    "async with self._lock:",
                    "    self._observers.discard(observer)"
                ]
            },
            {
                "type": "method",
                "name": "notify_observers",
                "body": [
                    "async with self._lock:",
                    "    for observer in self._observers:",
                    "        await observer.update(self)"
                ]
            }
        ]
    },
    rules=[
        {
            "name": "observer_registration",
            "description": "Ensure observers are properly registered",
            "check": "len(self._observers) > 0"
        },
        {
            "name": "thread_safety",
            "description": "Ensure thread-safe observer management",
            "check": "isinstance(self._lock, asyncio.Lock)"
        }
    ],
    examples=[
        """
class DataSubject:
    def __init__(self):
        self._observers = set()
        self._lock = asyncio.Lock()
        
    async def add_observer(self, observer):
        async with self._lock:
            self._observers.add(observer)
            
    async def notify_observers(self):
        async with self._lock:
            for observer in self._observers:
                await observer.update(self)
        """
    ],
    anti_patterns=[
        "Not using locks for observer management",
        "Synchronous observer updates",
        "Direct observer list modification"
    ],
    best_practices=[
        "Use asyncio.Lock for thread safety",
        "Implement proper cleanup in remove_observer",
        "Handle observer errors gracefully"
    ],
    language="python",
    category="design_pattern"
)

# Enhanced Code Analysis

class EnhancedCodeAnalyzer(CodeAnalyzer):
    """Enhanced code analyzer with additional capabilities."""
    
    def __init__(self):
        super().__init__()
        self.analysis.update({
            'complexity': {
                'cyclomatic': 0,
                'cognitive': 0,
                'maintainability': 0
            },
            'security': {
                'vulnerabilities': [],
                'risks': [],
                'recommendations': []
            },
            'performance': {
                'bottlenecks': [],
                'optimizations': [],
                'metrics': {}
            },
            'dependencies': {
                'external': [],
                'internal': [],
                'versions': {}
            }
        })
        
    def visit_If(self, node: ast.If) -> None:
        """Visit if statements to calculate cyclomatic complexity."""
        self.analysis['complexity']['cyclomatic'] += 1
        self.generic_visit(node)
        
    def visit_For(self, node: ast.For) -> None:
        """Visit for loops to calculate cyclomatic complexity."""
        self.analysis['complexity']['cyclomatic'] += 1
        self.generic_visit(node)
        
    def visit_While(self, node: ast.While) -> None:
        """Visit while loops to calculate cyclomatic complexity."""
        self.analysis['complexity']['cyclomatic'] += 1
        self.generic_visit(node)
        
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to analyze dependencies and performance."""
        if isinstance(node.func, ast.Name):
            self._analyze_function_call(node.func.id, node)
        self.generic_visit(node)
        
    def _analyze_function_call(self, func_name: str, node: ast.Call) -> None:
        """Analyze function calls for security and performance."""
        # Check for security vulnerabilities
        if func_name in ['eval', 'exec', 'os.system']:
            self.analysis['security']['vulnerabilities'].append({
                'type': 'dangerous_function',
                'function': func_name,
                'line': node.lineno
            })
            
        # Check for performance bottlenecks
        if func_name in ['time.sleep', 'requests.get']:
            self.analysis['performance']['bottlenecks'].append({
                'type': 'blocking_operation',
                'function': func_name,
                'line': node.lineno
            })
            
    def visit_Import(self, node: ast.Import) -> None:
        """Visit imports to analyze dependencies."""
        super().visit_Import(node)
        for name in node.names:
            self._analyze_dependency(name.name)
            
    def _analyze_dependency(self, module_name: str) -> None:
        """Analyze module dependencies."""
        try:
            import pkg_resources
            version = pkg_resources.get_distribution(module_name).version
            self.analysis['dependencies']['versions'][module_name] = version
        except:
            self.analysis['dependencies']['external'].append(module_name)
            
    def calculate_complexity_metrics(self) -> None:
        """Calculate code complexity metrics."""
        # Calculate cognitive complexity
        self.analysis['complexity']['cognitive'] = self._calculate_cognitive_complexity()
        
        # Calculate maintainability index
        self.analysis['complexity']['maintainability'] = self._calculate_maintainability_index()
        
    def _calculate_cognitive_complexity(self) -> int:
        """Calculate cognitive complexity score."""
        score = 0
        # Add complexity based on nesting, control structures, etc.
        return score
        
    def _calculate_maintainability_index(self) -> float:
        """Calculate maintainability index."""
        # Implement maintainability index calculation
        return 0.0

# Enhanced Documentation Generation

class EnhancedDocumentationGenerator:
    """Enhanced documentation generator with additional features."""
    
    def __init__(self, generator: CodeGenerator):
        self.generator = generator
        self.analyzer = EnhancedCodeAnalyzer()
        
    def generate_comprehensive_doc(self, code: str, template_name: str,
                                 additional_info: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive documentation including analysis results."""
        # Analyze code
        self.analyzer.visit(ast.parse(code))
        self.analyzer.calculate_complexity_metrics()
        
        # Prepare documentation data
        doc_data = {
            'code_analysis': self.analyzer.get_analysis(),
            'timestamp': datetime.now(),
            'complexity': self.analyzer.analysis['complexity'],
            'security': self.analyzer.analysis['security'],
            'performance': self.analyzer.analysis['performance'],
            'dependencies': self.analyzer.analysis['dependencies'],
            **(additional_info or {})
        }
        
        # Generate documentation
        return self.generator.generate_documentation(template_name, code, doc_data)
        
    def generate_security_report(self, code: str) -> str:
        """Generate a security-focused documentation report."""
        self.analyzer.visit(ast.parse(code))
        
        security_data = {
            'vulnerabilities': self.analyzer.analysis['security']['vulnerabilities'],
            'risks': self.analyzer.analysis['security']['risks'],
            'recommendations': self.analyzer.analysis['security']['recommendations'],
            'timestamp': datetime.now()
        }
        
        return self.generator.generate_documentation(
            "security_report",
            code,
            security_data
        )
        
    def generate_performance_report(self, code: str) -> str:
        """Generate a performance-focused documentation report."""
        self.analyzer.visit(ast.parse(code))
        
        performance_data = {
            'bottlenecks': self.analyzer.analysis['performance']['bottlenecks'],
            'optimizations': self.analyzer.analysis['performance']['optimizations'],
            'metrics': self.analyzer.analysis['performance']['metrics'],
            'timestamp': datetime.now()
        }
        
        return self.generator.generate_documentation(
            "performance_report",
            code,
            performance_data
        )
        
    def generate_dependency_report(self, code: str) -> str:
        """Generate a dependency-focused documentation report."""
        self.analyzer.visit(ast.parse(code))
        
        dependency_data = {
            'external': self.analyzer.analysis['dependencies']['external'],
            'internal': self.analyzer.analysis['dependencies']['internal'],
            'versions': self.analyzer.analysis['dependencies']['versions'],
            'timestamp': datetime.now()
        }
        
        return self.generator.generate_documentation(
            "dependency_report",
            code,
            dependency_data
        ) 