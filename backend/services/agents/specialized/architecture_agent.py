from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import ast
import re
import logging
from pathlib import Path
from ...core.base_agent import BaseAgent

@dataclass
class ArchitectureComponent:
    name: str
    type: str
    dependencies: Set[str]
    interfaces: Set[str]
    metrics: Dict[str, float]
    location: str

@dataclass
class ArchitectureIssue:
    severity: str
    description: str
    component: str
    issue_type: str
    impact: str
    fix_suggestion: str

class ArchitectureAgent(BaseAgent):
    """Specialized agent for architecture analysis and design patterns"""
    
    def __init__(self):
        super().__init__("architecture_agent")
        self.logger = logging.getLogger(__name__)
        self.components: Dict[str, ArchitectureComponent] = {}
        self._load_patterns()

    def _load_patterns(self):
        """Load architecture patterns and anti-patterns"""
        self.patterns = {
            'clean_architecture': {
                'layers': ['entities', 'use_cases', 'interfaces', 'infrastructure'],
                'dependencies': 'inward',
                'max_coupling': 0.3
            },
            'microservices': {
                'characteristics': [
                    'service_independence',
                    'data_isolation',
                    'api_gateway',
                    'service_discovery'
                ],
                'max_service_size': 1000,
                'max_dependencies': 5
            },
            'event_driven': {
                'components': [
                    'event_bus',
                    'publishers',
                    'subscribers',
                    'event_store'
                ],
                'patterns': [
                    'pub_sub',
                    'event_sourcing',
                    'cqrs'
                ]
            }
        }

    async def analyze_architecture(self, project_path: str) -> List[ArchitectureIssue]:
        """Analyze project architecture"""
        issues = []
        
        # Build component graph
        await self._build_component_graph(project_path)
        
        # Analyze dependencies
        issues.extend(await self._analyze_dependencies())
        
        # Check architectural patterns
        issues.extend(await self._check_architecture_patterns())
        
        # Analyze metrics
        issues.extend(await self._analyze_architecture_metrics())
        
        return issues

    async def _build_component_graph(self, project_path: str):
        """Build a graph of project components and their relationships"""
        for file_path in Path(project_path).rglob('*.py'):
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                
                tree = ast.parse(code)
                
                # Find components (classes, modules)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self._add_component(node, str(file_path))
                    elif isinstance(node, ast.Module):
                        self._add_module(node, str(file_path))
                
                # Find dependencies
                self._analyze_imports(tree, str(file_path))
                
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")

    def _add_component(self, node: ast.ClassDef, file_path: str):
        """Add a component to the architecture graph"""
        interfaces = set()
        dependencies = set()
        
        # Find implemented interfaces
        for base in node.bases:
            if isinstance(base, ast.Name):
                interfaces.add(base.id)
        
        # Calculate metrics
        metrics = {
            'complexity': self._calculate_complexity(node),
            'cohesion': self._calculate_cohesion(node),
            'coupling': self._calculate_coupling(node)
        }
        
        self.components[node.name] = ArchitectureComponent(
            name=node.name,
            type='class',
            dependencies=dependencies,
            interfaces=interfaces,
            metrics=metrics,
            location=file_path
        )

    def _analyze_imports(self, tree: ast.AST, file_path: str):
        """Analyze import statements to find dependencies"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                for name in node.names:
                    if name.name in self.components:
                        component = self.components[name.name]
                        if module:
                            component.dependencies.add(module)
                        else:
                            component.dependencies.add(name.name)

    async def _analyze_dependencies(self) -> List[ArchitectureIssue]:
        """Analyze component dependencies for issues"""
        issues = []
        
        # Check for circular dependencies
        circular = self._find_circular_dependencies()
        for cycle in circular:
            issues.append(
                ArchitectureIssue(
                    severity="HIGH",
                    description=f"Circular dependency detected: {' -> '.join(cycle)}",
                    component=cycle[0],
                    issue_type="circular_dependency",
                    impact="Tight coupling and difficult maintenance",
                    fix_suggestion="Break the cycle using dependency inversion"
                )
            )
        
        # Check for high coupling
        for name, component in self.components.items():
            if len(component.dependencies) > 5:
                issues.append(
                    ArchitectureIssue(
                        severity="MEDIUM",
                        description=f"Component {name} has too many dependencies ({len(component.dependencies)})",
                        component=name,
                        issue_type="high_coupling",
                        impact="Reduced maintainability and testability",
                        fix_suggestion="Consider breaking down the component or using facade pattern"
                    )
                )
        
        return issues

    async def _check_architecture_patterns(self) -> List[ArchitectureIssue]:
        """Check if the codebase follows architectural patterns"""
        issues = []
        
        # Check Clean Architecture
        if not self._follows_clean_architecture():
            issues.append(
                ArchitectureIssue(
                    severity="MEDIUM",
                    description="Project structure doesn't follow Clean Architecture",
                    component="project",
                    issue_type="architecture_pattern",
                    impact="Harder to maintain and evolve",
                    fix_suggestion="Reorganize code into proper Clean Architecture layers"
                )
            )
        
        # Check Microservices patterns
        if self._is_microservices():
            issues.extend(self._check_microservices_patterns())
        
        # Check Event-Driven patterns
        if self._is_event_driven():
            issues.extend(self._check_event_driven_patterns())
        
        return issues

    async def _analyze_architecture_metrics(self) -> List[ArchitectureIssue]:
        """Analyze architecture metrics"""
        issues = []
        
        for name, component in self.components.items():
            # Check complexity
            if component.metrics['complexity'] > 10:
                issues.append(
                    ArchitectureIssue(
                        severity="MEDIUM",
                        description=f"Component {name} has high complexity ({component.metrics['complexity']})",
                        component=name,
                        issue_type="high_complexity",
                        impact="Difficult to understand and maintain",
                        fix_suggestion="Break down into smaller components"
                    )
                )
            
            # Check cohesion
            if component.metrics['cohesion'] < 0.5:
                issues.append(
                    ArchitectureIssue(
                        severity="MEDIUM",
                        description=f"Component {name} has low cohesion ({component.metrics['cohesion']})",
                        component=name,
                        issue_type="low_cohesion",
                        impact="Poor organization of responsibilities",
                        fix_suggestion="Group related functionality together"
                    )
                )
        
        return issues

    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the component graph"""
        cycles = []
        visited = set()
        path = []
        
        def dfs(component: str):
            if component in path:
                cycle_start = path.index(component)
                cycles.append(path[cycle_start:])
                return
            
            if component in visited:
                return
            
            visited.add(component)
            path.append(component)
            
            if component in self.components:
                for dep in self.components[component].dependencies:
                    dfs(dep)
            
            path.pop()
        
        for component in self.components:
            dfs(component)
        
        return cycles

    def _calculate_complexity(self, node: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _calculate_cohesion(self, node: ast.ClassDef) -> float:
        """Calculate class cohesion"""
        methods = []
        fields = set()
        
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(child)
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        fields.add(target.id)
        
        if not methods:
            return 1.0
        
        # Calculate LCOM (Lack of Cohesion of Methods)
        method_fields = []
        for method in methods:
            used_fields = set()
            for node in ast.walk(method):
                if isinstance(node, ast.Name) and node.id in fields:
                    used_fields.add(node.id)
            method_fields.append(used_fields)
        
        # Calculate pairs of methods that share fields
        shared = 0
        not_shared = 0
        
        for i in range(len(methods)):
            for j in range(i + 1, len(methods)):
                if method_fields[i] & method_fields[j]:
                    shared += 1
                else:
                    not_shared += 1
        
        if shared + not_shared == 0:
            return 1.0
        
        return shared / (shared + not_shared)

    def _calculate_coupling(self, node: ast.ClassDef) -> float:
        """Calculate coupling factor"""
        coupling = 0
        total_refs = 0
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in self.components:
                    coupling += 1
                total_refs += 1
        
        return coupling / total_refs if total_refs > 0 else 0

    def _follows_clean_architecture(self) -> bool:
        """Check if project follows Clean Architecture"""
        required_layers = self.patterns['clean_architecture']['layers']
        found_layers = set()
        
        for component in self.components.values():
            for layer in required_layers:
                if layer in component.location.lower():
                    found_layers.add(layer)
        
        return len(found_layers) == len(required_layers)

    def _is_microservices(self) -> bool:
        """Check if project uses microservices architecture"""
        service_indicators = ['service', 'api', 'gateway']
        service_count = 0
        
        for component in self.components.values():
            if any(indicator in component.name.lower() for indicator in service_indicators):
                service_count += 1
        
        return service_count >= 3

    def _is_event_driven(self) -> bool:
        """Check if project uses event-driven architecture"""
        event_indicators = ['event', 'publisher', 'subscriber', 'handler']
        event_components = 0
        
        for component in self.components.values():
            if any(indicator in component.name.lower() for indicator in event_indicators):
                event_components += 1
        
        return event_components >= 3

    def _check_microservices_patterns(self) -> List[ArchitectureIssue]:
        """Check microservices architectural patterns"""
        issues = []
        required = self.patterns['microservices']['characteristics']
        
        for req in required:
            if not self._has_microservice_pattern(req):
                issues.append(
                    ArchitectureIssue(
                        severity="MEDIUM",
                        description=f"Missing microservices pattern: {req}",
                        component="architecture",
                        issue_type="missing_pattern",
                        impact="Incomplete microservices implementation",
                        fix_suggestion=f"Implement {req} pattern"
                    )
                )
        
        return issues

    def _check_event_driven_patterns(self) -> List[ArchitectureIssue]:
        """Check event-driven architectural patterns"""
        issues = []
        required = self.patterns['event_driven']['patterns']
        
        for pattern in required:
            if not self._has_event_pattern(pattern):
                issues.append(
                    ArchitectureIssue(
                        severity="MEDIUM",
                        description=f"Missing event-driven pattern: {pattern}",
                        component="architecture",
                        issue_type="missing_pattern",
                        impact="Incomplete event-driven implementation",
                        fix_suggestion=f"Implement {pattern} pattern"
                    )
                )
        
        return issues

    def _has_microservice_pattern(self, pattern: str) -> bool:
        """Check if a specific microservice pattern is implemented"""
        pattern_indicators = {
            'service_independence': ['api', 'controller', 'service'],
            'data_isolation': ['repository', 'database', 'store'],
            'api_gateway': ['gateway', 'proxy', 'router'],
            'service_discovery': ['discovery', 'registry', 'locator']
        }
        
        indicators = pattern_indicators.get(pattern, [])
        for component in self.components.values():
            if any(indicator in component.name.lower() for indicator in indicators):
                return True
        
        return False

    def _has_event_pattern(self, pattern: str) -> bool:
        """Check if a specific event-driven pattern is implemented"""
        pattern_indicators = {
            'pub_sub': ['publisher', 'subscriber', 'topic'],
            'event_sourcing': ['event', 'store', 'aggregate'],
            'cqrs': ['command', 'query', 'handler']
        }
        
        indicators = pattern_indicators.get(pattern, [])
        for component in self.components.values():
            if any(indicator in component.name.lower() for indicator in indicators):
                return True
        
        return False
