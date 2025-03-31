from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import re
import json
import networkx as nx
from collections import defaultdict

logger = logging.getLogger(__name__)

class PatternCategory(Enum):
    DESIGN = "design"
    ANTI = "anti"
    CODE_SMELL = "code_smell"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    ARCHITECTURAL = "architectural"
    BEHAVIORAL = "behavioral"
    STRUCTURAL = "structural"
    CREATIONAL = "creational"
    CUSTOM = "custom"

@dataclass
class PatternRule:
    name: str
    description: str
    category: PatternCategory
    severity: str
    conditions: List[Dict[str, Any]]
    suggestions: List[str]
    metadata: Optional[Dict[str, Any]] = None

class CustomPatternManager:
    """Manages custom pattern definitions and circular dependency detection."""
    
    def __init__(self):
        """Initialize the custom pattern manager."""
        self.patterns: Dict[str, PatternRule] = {}
        self.dependency_graph = nx.DiGraph()
        self._load_custom_patterns()
        
    def _load_custom_patterns(self):
        """Load custom patterns from configuration."""
        try:
            config_path = Path("config/custom_patterns.json")
            if config_path.exists():
                with open(config_path) as f:
                    patterns_data = json.load(f)
                    for pattern_data in patterns_data:
                        self.add_pattern(PatternRule(**pattern_data))
        except Exception as e:
            logger.error(f"Error loading custom patterns: {e}")
            
    def add_pattern(self, pattern: PatternRule):
        """Add a new custom pattern."""
        self.patterns[pattern.name] = pattern
        logger.info(f"Added custom pattern: {pattern.name}")
        
    def remove_pattern(self, pattern_name: str):
        """Remove a custom pattern."""
        if pattern_name in self.patterns:
            del self.patterns[pattern_name]
            logger.info(f"Removed custom pattern: {pattern_name}")
            
    def get_pattern(self, pattern_name: str) -> Optional[PatternRule]:
        """Get a custom pattern by name."""
        return self.patterns.get(pattern_name)
        
    def list_patterns(self) -> List[PatternRule]:
        """List all custom patterns."""
        return list(self.patterns.values())
        
    def update_pattern(self, pattern_name: str, updated_pattern: PatternRule):
        """Update an existing custom pattern."""
        if pattern_name in self.patterns:
            self.patterns[pattern_name] = updated_pattern
            logger.info(f"Updated custom pattern: {pattern_name}")
            
    def analyze_circular_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Analyze code for circular dependencies."""
        try:
            # Build dependency graph
            self._build_dependency_graph(content)
            
            # Find cycles
            cycles = self._find_cycles()
            
            # Analyze cycle impact
            cycle_analysis = self._analyze_cycle_impact(cycles)
            
            return cycle_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing circular dependencies: {e}")
            return []
            
    def _build_dependency_graph(self, content: str):
        """Build a comprehensive dependency graph."""
        self.dependency_graph.clear()
        
        # Parse code
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        def traverse(node: tree_sitter.Node):
            if node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                self.dependency_graph.add_node(class_name)
                
                # Add inheritance edges
                for child in node.children:
                    if child.type == "superclass":
                        superclass = child.text.decode("utf8")
                        self.dependency_graph.add_edge(class_name, superclass, type="inheritance")
                        
                # Add composition edges
                for child in node.children:
                    if child.type == "field_declaration":
                        field_type = child.child_by_field_name("type").text.decode("utf8")
                        self.dependency_graph.add_edge(class_name, field_type, type="composition")
                        
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                self.dependency_graph.add_node(func_name)
                
                # Add function call edges
                for child in node.children:
                    if child.type == "call":
                        called_func = child.child_by_field_name("function").text.decode("utf8")
                        self.dependency_graph.add_edge(func_name, called_func, type="call")
                        
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        
    def _find_cycles(self) -> List[List[str]]:
        """Find all cycles in the dependency graph."""
        cycles = []
        
        # Find simple cycles
        simple_cycles = list(nx.simple_cycles(self.dependency_graph))
        cycles.extend(simple_cycles)
        
        # Find strongly connected components
        sccs = list(nx.strongly_connected_components(self.dependency_graph))
        for scc in sccs:
            if len(scc) > 1:
                subgraph = self.dependency_graph.subgraph(scc)
                scc_cycles = list(nx.simple_cycles(subgraph))
                cycles.extend(scc_cycles)
                
        return cycles
        
    def _analyze_cycle_impact(self, cycles: List[List[str]]) -> List[Dict[str, Any]]:
        """Analyze the impact of circular dependencies."""
        analysis = []
        
        for cycle in cycles:
            # Calculate cycle metrics
            cycle_length = len(cycle)
            cycle_edges = self._get_cycle_edges(cycle)
            edge_types = [self.dependency_graph.edges[e]["type"] for e in cycle_edges]
            
            # Determine cycle type
            cycle_type = self._determine_cycle_type(edge_types)
            
            # Calculate impact score
            impact_score = self._calculate_impact_score(cycle, edge_types)
            
            # Generate suggestions
            suggestions = self._generate_cycle_suggestions(cycle_type, edge_types)
            
            analysis.append({
                "cycle": cycle,
                "type": cycle_type,
                "length": cycle_length,
                "edge_types": edge_types,
                "impact_score": impact_score,
                "suggestions": suggestions
            })
            
        return analysis
        
    def _get_cycle_edges(self, cycle: List[str]) -> List[Tuple[str, str]]:
        """Get edges that form a cycle."""
        edges = []
        for i in range(len(cycle)):
            edges.append((cycle[i], cycle[(i + 1) % len(cycle)]))
        return edges
        
    def _determine_cycle_type(self, edge_types: List[str]) -> str:
        """Determine the type of circular dependency."""
        if all(t == "inheritance" for t in edge_types):
            return "inheritance_cycle"
        elif all(t == "composition" for t in edge_types):
            return "composition_cycle"
        elif all(t == "call" for t in edge_types):
            return "call_cycle"
        else:
            return "mixed_cycle"
            
    def _calculate_impact_score(self, cycle: List[str], edge_types: List[str]) -> float:
        """Calculate the impact score of a circular dependency."""
        score = 0.0
        
        # Base score from cycle length
        score += len(cycle) * 0.2
        
        # Impact from edge types
        type_weights = {
            "inheritance": 0.4,
            "composition": 0.3,
            "call": 0.2
        }
        for edge_type in edge_types:
            score += type_weights.get(edge_type, 0.1)
            
        # Normalize score
        return min(score, 1.0)
        
    def _generate_cycle_suggestions(self, cycle_type: str, edge_types: List[str]) -> List[str]:
        """Generate suggestions for resolving circular dependencies."""
        suggestions = []
        
        if cycle_type == "inheritance_cycle":
            suggestions.extend([
                "Consider using composition instead of inheritance",
                "Break the inheritance chain by introducing an interface",
                "Use dependency injection to decouple classes"
            ])
        elif cycle_type == "composition_cycle":
            suggestions.extend([
                "Introduce a mediator pattern to break the cycle",
                "Use event-driven architecture to decouple components",
                "Consider using a facade pattern to simplify dependencies"
            ])
        elif cycle_type == "call_cycle":
            suggestions.extend([
                "Introduce an observer pattern to break the cycle",
                "Use a command pattern to decouple function calls",
                "Consider using an event bus for communication"
            ])
        else:
            suggestions.extend([
                "Review and simplify the dependency structure",
                "Consider using a service locator pattern",
                "Implement dependency inversion principle"
            ])
            
        return suggestions
        
    def validate_pattern(self, pattern: PatternRule) -> List[str]:
        """Validate a custom pattern definition."""
        errors = []
        
        # Check required fields
        if not pattern.name:
            errors.append("Pattern name is required")
        if not pattern.description:
            errors.append("Pattern description is required")
        if not pattern.category:
            errors.append("Pattern category is required")
        if not pattern.severity:
            errors.append("Pattern severity is required")
        if not pattern.conditions:
            errors.append("Pattern must have at least one condition")
        if not pattern.suggestions:
            errors.append("Pattern must have at least one suggestion")
            
        # Validate conditions
        for condition in pattern.conditions:
            if "type" not in condition:
                errors.append("Each condition must have a type")
            if "value" not in condition:
                errors.append("Each condition must have a value")
                
        return errors
        
    def export_patterns(self, file_path: str):
        """Export custom patterns to a JSON file."""
        try:
            patterns_data = [
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "category": pattern.category.value,
                    "severity": pattern.severity,
                    "conditions": pattern.conditions,
                    "suggestions": pattern.suggestions,
                    "metadata": pattern.metadata
                }
                for pattern in self.patterns.values()
            ]
            
            with open(file_path, "w") as f:
                json.dump(patterns_data, f, indent=2)
                
            logger.info(f"Exported patterns to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting patterns: {e}")
            
    def import_patterns(self, file_path: str):
        """Import custom patterns from a JSON file."""
        try:
            with open(file_path) as f:
                patterns_data = json.load(f)
                
            for pattern_data in patterns_data:
                pattern_data["category"] = PatternCategory(pattern_data["category"])
                pattern = PatternRule(**pattern_data)
                errors = self.validate_pattern(pattern)
                if not errors:
                    self.add_pattern(pattern)
                else:
                    logger.warning(f"Invalid pattern definition: {errors}")
                    
        except Exception as e:
            logger.error(f"Error importing patterns: {e}") 