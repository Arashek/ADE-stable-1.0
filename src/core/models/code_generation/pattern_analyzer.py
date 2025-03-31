from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import ast
import re
from datetime import datetime
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

@dataclass
class CodePattern:
    """Represents a code pattern with metadata"""
    name: str
    description: str
    category: str
    language: str
    template: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]
    best_practices: List[str]
    anti_patterns: List[str]
    created_at: datetime
    updated_at: datetime

class PatternAnalyzer:
    """Pattern analysis and application system"""
    
    def __init__(self, patterns_dir: str = "patterns"):
        self.patterns_dir = Path(patterns_dir)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # Load patterns
        self.patterns: Dict[str, CodePattern] = {}
        self._load_patterns()
        
        # Define pattern categories
        self.categories = {
            "creational": ["singleton", "factory", "builder", "prototype", "abstract_factory"],
            "structural": ["adapter", "bridge", "composite", "decorator", "facade", "flyweight", "proxy"],
            "behavioral": ["chain_of_responsibility", "command", "iterator", "mediator", "memento", "observer", "state", "strategy", "template_method", "visitor"]
        }
        
    def _load_patterns(self) -> None:
        """Load patterns from YAML files"""
        try:
            for pattern_file in self.patterns_dir.glob("**/*.yaml"):
                with open(pattern_file) as f:
                    pattern_data = yaml.safe_load(f)
                    
                pattern = CodePattern(
                    name=pattern_data["name"],
                    description=pattern_data["description"],
                    category=pattern_data["category"],
                    language=pattern_data["language"],
                    template=pattern_data["template"],
                    parameters=pattern_data["parameters"],
                    examples=pattern_data["examples"],
                    best_practices=pattern_data["best_practices"],
                    anti_patterns=pattern_data["anti_patterns"],
                    created_at=datetime.fromisoformat(pattern_data["created_at"]),
                    updated_at=datetime.fromisoformat(pattern_data["updated_at"])
                )
                
                self.patterns[pattern.name] = pattern
                
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            
    async def analyze_code(
        self,
        code: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze code for patterns"""
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Detect patterns
            detected_patterns = self._detect_patterns(tree)
            
            # Analyze pattern usage
            pattern_analysis = self._analyze_pattern_usage(detected_patterns)
            
            # Generate suggestions
            suggestions = self._generate_pattern_suggestions(
                detected_patterns,
                pattern_analysis,
                context
            )
            
            return {
                "detected_patterns": detected_patterns,
                "pattern_analysis": pattern_analysis,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code patterns: {e}")
            return {
                "detected_patterns": [],
                "pattern_analysis": {},
                "suggestions": []
            }
            
    def _detect_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect patterns in code"""
        patterns = []
        
        try:
            # Check for creational patterns
            patterns.extend(self._detect_creational_patterns(tree))
            
            # Check for structural patterns
            patterns.extend(self._detect_structural_patterns(tree))
            
            # Check for behavioral patterns
            patterns.extend(self._detect_behavioral_patterns(tree))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []
            
    def _detect_creational_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect creational patterns"""
        patterns = []
        
        try:
            # Check for singleton pattern
            if self._is_singleton(tree):
                patterns.append({
                    "type": "creational",
                    "name": "singleton",
                    "confidence": 0.9,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for factory pattern
            if self._is_factory(tree):
                patterns.append({
                    "type": "creational",
                    "name": "factory",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for builder pattern
            if self._is_builder(tree):
                patterns.append({
                    "type": "creational",
                    "name": "builder",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting creational patterns: {e}")
            return []
            
    def _detect_structural_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect structural patterns"""
        patterns = []
        
        try:
            # Check for adapter pattern
            if self._is_adapter(tree):
                patterns.append({
                    "type": "structural",
                    "name": "adapter",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for decorator pattern
            if self._is_decorator(tree):
                patterns.append({
                    "type": "structural",
                    "name": "decorator",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for facade pattern
            if self._is_facade(tree):
                patterns.append({
                    "type": "structural",
                    "name": "facade",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting structural patterns: {e}")
            return []
            
    def _detect_behavioral_patterns(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect behavioral patterns"""
        patterns = []
        
        try:
            # Check for observer pattern
            if self._is_observer(tree):
                patterns.append({
                    "type": "behavioral",
                    "name": "observer",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for strategy pattern
            if self._is_strategy(tree):
                patterns.append({
                    "type": "behavioral",
                    "name": "strategy",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            # Check for template method pattern
            if self._is_template_method(tree):
                patterns.append({
                    "type": "behavioral",
                    "name": "template_method",
                    "confidence": 0.8,
                    "location": self._get_pattern_location(tree)
                })
                
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting behavioral patterns: {e}")
            return []
            
    def _is_singleton(self, tree: ast.AST) -> bool:
        """Check if code implements singleton pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for private instance variable
                    has_instance = False
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id == "_instance":
                                    has_instance = True
                                    break
                                    
                    # Check for get_instance method
                    has_get_instance = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name == "get_instance":
                                has_get_instance = True
                                break
                                
                    if has_instance and has_get_instance:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking singleton pattern: {e}")
            return False
            
    def _is_factory(self, tree: ast.AST) -> bool:
        """Check if code implements factory pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for create/build/make methods
                    has_factory_method = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name in ["create", "build", "make"]:
                                has_factory_method = True
                                break
                                
                    if has_factory_method:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking factory pattern: {e}")
            return False
            
    def _is_builder(self, tree: ast.AST) -> bool:
        """Check if code implements builder pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for builder methods
                    has_builder_methods = False
                    method_names = set()
                    
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            method_names.add(child.name)
                            
                    # Check for common builder method names
                    builder_methods = {"build", "with", "add", "set"}
                    if any(method in builder_methods for method in method_names):
                        has_builder_methods = True
                        
                    if has_builder_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking builder pattern: {e}")
            return False
            
    def _is_adapter(self, tree: ast.AST) -> bool:
        """Check if code implements adapter pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for adaptee attribute
                    has_adaptee = False
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id == "adaptee":
                                    has_adaptee = True
                                    break
                                    
                    # Check for adapter methods
                    has_adapter_methods = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name.startswith("adapt_"):
                                has_adapter_methods = True
                                break
                                
                    if has_adaptee and has_adapter_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking adapter pattern: {e}")
            return False
            
    def _is_decorator(self, tree: ast.AST) -> bool:
        """Check if code implements decorator pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for component attribute
                    has_component = False
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id == "component":
                                    has_component = True
                                    break
                                    
                    # Check for decorator methods
                    has_decorator_methods = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name.startswith("decorate_"):
                                has_decorator_methods = True
                                break
                                
                    if has_component and has_decorator_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking decorator pattern: {e}")
            return False
            
    def _is_facade(self, tree: ast.AST) -> bool:
        """Check if code implements facade pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for subsystem attributes
                    has_subsystems = False
                    subsystem_names = {"subsystem", "service", "module"}
                    
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id in subsystem_names:
                                    has_subsystems = True
                                    break
                                    
                    # Check for facade methods
                    has_facade_methods = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name.startswith(("get_", "create_", "update_", "delete_")):
                                has_facade_methods = True
                                break
                                
                    if has_subsystems and has_facade_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking facade pattern: {e}")
            return False
            
    def _is_observer(self, tree: ast.AST) -> bool:
        """Check if code implements observer pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for observers list
                    has_observers = False
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id == "observers":
                                    has_observers = True
                                    break
                                    
                    # Check for observer methods
                    has_observer_methods = False
                    observer_methods = {"attach", "detach", "notify"}
                    
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name in observer_methods:
                                has_observer_methods = True
                                break
                                
                    if has_observers and has_observer_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking observer pattern: {e}")
            return False
            
    def _is_strategy(self, tree: ast.AST) -> bool:
        """Check if code implements strategy pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for strategy attribute
                    has_strategy = False
                    for child in node.body:
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name) and target.id == "strategy":
                                    has_strategy = True
                                    break
                                    
                    # Check for strategy methods
                    has_strategy_methods = False
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name == "execute_strategy":
                                has_strategy_methods = True
                                break
                                
                    if has_strategy and has_strategy_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking strategy pattern: {e}")
            return False
            
    def _is_template_method(self, tree: ast.AST) -> bool:
        """Check if code implements template method pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for template method
                    has_template_method = False
                    has_abstract_methods = False
                    
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            if child.name == "template_method":
                                has_template_method = True
                            elif child.name.startswith("_"):
                                has_abstract_methods = True
                                
                    if has_template_method and has_abstract_methods:
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking template method pattern: {e}")
            return False
            
    def _get_pattern_location(self, tree: ast.AST) -> Dict[str, Any]:
        """Get location information for a pattern"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    return {
                        "type": "class",
                        "name": node.name,
                        "line": node.lineno,
                        "column": node.col_offset
                    }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting pattern location: {e}")
            return {}
            
    def _analyze_pattern_usage(
        self,
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze pattern usage"""
        analysis = {
            "pattern_count": len(patterns),
            "pattern_types": {},
            "pattern_categories": {},
            "pattern_confidence": 0.0
        }
        
        try:
            # Count pattern types
            for pattern in patterns:
                pattern_type = pattern["type"]
                analysis["pattern_types"][pattern_type] = analysis["pattern_types"].get(pattern_type, 0) + 1
                
            # Count pattern categories
            for pattern in patterns:
                pattern_name = pattern["name"]
                for category, pattern_list in self.categories.items():
                    if pattern_name in pattern_list:
                        analysis["pattern_categories"][category] = analysis["pattern_categories"].get(category, 0) + 1
                        
            # Calculate average confidence
            if patterns:
                analysis["pattern_confidence"] = sum(p["confidence"] for p in patterns) / len(patterns)
                
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing pattern usage: {e}")
            return analysis
            
    def _generate_pattern_suggestions(
        self,
        patterns: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate pattern suggestions"""
        suggestions = []
        
        try:
            # Check for missing patterns
            for category, pattern_list in self.categories.items():
                if category not in analysis["pattern_categories"]:
                    suggestions.append({
                        "type": "missing_pattern",
                        "category": category,
                        "description": f"Consider using {category} patterns to improve code structure.",
                        "priority": "medium",
                        "impact": "architecture"
                    })
                    
            # Check for pattern overuse
            for pattern_type, count in analysis["pattern_types"].items():
                if count > 3:
                    suggestions.append({
                        "type": "pattern_overuse",
                        "pattern_type": pattern_type,
                        "description": f"High usage of {pattern_type} patterns. Consider using other patterns for variety.",
                        "priority": "low",
                        "impact": "maintainability"
                    })
                    
            # Check for pattern confidence
            if analysis["pattern_confidence"] < 0.7:
                suggestions.append({
                    "type": "pattern_confidence",
                    "description": "Low confidence in pattern detection. Review pattern implementation.",
                    "priority": "medium",
                    "impact": "reliability"
                })
                
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating pattern suggestions: {e}")
            return [] 