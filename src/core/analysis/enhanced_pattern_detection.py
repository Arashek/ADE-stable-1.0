from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import json
import networkx as nx
from collections import defaultdict
from .custom_patterns import CustomPatternManager, PatternRule, PatternCategory

logger = logging.getLogger(__name__)

class PatternType(Enum):
    DESIGN_PATTERN = "design_pattern"
    ANTI_PATTERN = "anti_pattern"
    CODE_SMELL = "code_smell"
    PERFORMANCE_PATTERN = "performance_pattern"
    SECURITY_PATTERN = "security_pattern"
    TESTING_PATTERN = "testing_pattern"
    ARCHITECTURAL_PATTERN = "architectural_pattern"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    STRUCTURAL_PATTERN = "structural_pattern"
    CREATIONAL_PATTERN = "creational_pattern"

@dataclass
class Pattern:
    type: PatternType
    name: str
    description: str
    severity: str
    confidence: float
    location: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    vector: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None

class EnhancedPatternDetector:
    """Enhanced pattern detection system with ML-based recognition."""
    
    def __init__(self):
        """Initialize the enhanced pattern detection system."""
        self.patterns = {}
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.cluster_model = DBSCAN(eps=0.3, min_samples=2)
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        self.custom_pattern_manager = CustomPatternManager()
        self._initialize_patterns()
        
    def _initialize_patterns(self):
        """Initialize known patterns and their detection rules."""
        self.patterns = {
            # Design Patterns
            "singleton": {
                "type": PatternType.DESIGN_PATTERN,
                "description": "Ensures a class has only one instance",
                "severity": "info",
                "rules": [
                    "private constructor",
                    "static instance",
                    "static getInstance method"
                ]
            },
            "factory": {
                "type": PatternType.DESIGN_PATTERN,
                "description": "Creates objects without exposing creation logic",
                "severity": "info",
                "rules": [
                    "static factory method",
                    "interface or abstract class",
                    "multiple concrete implementations"
                ]
            },
            # Anti-patterns
            "god_class": {
                "type": PatternType.ANTI_PATTERN,
                "description": "Class with too many responsibilities",
                "severity": "warning",
                "rules": [
                    "high number of methods",
                    "high number of fields",
                    "high cyclomatic complexity"
                ]
            },
            "spaghetti_code": {
                "type": PatternType.ANTI_PATTERN,
                "description": "Unstructured and difficult to maintain code",
                "severity": "error",
                "rules": [
                    "high nesting levels",
                    "long methods",
                    "many goto statements"
                ]
            },
            # Code Smells
            "long_method": {
                "type": PatternType.CODE_SMELL,
                "description": "Method with too many lines of code",
                "severity": "warning",
                "rules": [
                    "method length > 20 lines",
                    "high cyclomatic complexity"
                ]
            },
            "duplicate_code": {
                "type": PatternType.CODE_SMELL,
                "description": "Similar code blocks repeated in multiple places",
                "severity": "warning",
                "rules": [
                    "similar code blocks",
                    "high token similarity"
                ]
            },
            # Performance Patterns
            "n_plus_one": {
                "type": PatternType.PERFORMANCE_PATTERN,
                "description": "Inefficient database querying pattern",
                "severity": "warning",
                "rules": [
                    "loop with database queries",
                    "nested queries"
                ]
            },
            "memory_leak": {
                "type": PatternType.PERFORMANCE_PATTERN,
                "description": "Resource not properly released",
                "severity": "error",
                "rules": [
                    "unclosed resources",
                    "circular references"
                ]
            },
            # Security Patterns
            "sql_injection": {
                "type": PatternType.SECURITY_PATTERN,
                "description": "SQL injection vulnerability",
                "severity": "error",
                "rules": [
                    "string concatenation in SQL",
                    "unvalidated input"
                ]
            },
            "xss": {
                "type": PatternType.SECURITY_PATTERN,
                "description": "Cross-site scripting vulnerability",
                "severity": "error",
                "rules": [
                    "unvalidated output",
                    "raw HTML injection"
                ]
            }
        }
        
    def analyze_code(self, file_path: str, content: str) -> List[Pattern]:
        """Analyze code for patterns using multiple detection methods."""
        try:
            patterns = []
            
            # 1. Rule-based detection
            rule_patterns = self._detect_patterns_rules(content)
            patterns.extend(rule_patterns)
            
            # 2. ML-based detection
            ml_patterns = self._detect_patterns_ml(content)
            patterns.extend(ml_patterns)
            
            # 3. Graph-based detection
            graph_patterns = self._detect_patterns_graph(content)
            patterns.extend(graph_patterns)
            
            # 4. Semantic analysis
            semantic_patterns = self._detect_patterns_semantic(content)
            patterns.extend(semantic_patterns)
            
            # 5. Statistical analysis
            statistical_patterns = self._detect_patterns_statistical(content)
            patterns.extend(statistical_patterns)
            
            # 6. Custom pattern detection
            custom_patterns = self._detect_custom_patterns(content)
            patterns.extend(custom_patterns)
            
            # 7. Circular dependency analysis
            circular_patterns = self._detect_circular_dependencies(content)
            patterns.extend(circular_patterns)
            
            # Merge and deduplicate patterns
            merged_patterns = self._merge_patterns(patterns)
            
            return merged_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns in {file_path}: {e}")
            return []
            
    def _detect_patterns_rules(self, content: str) -> List[Pattern]:
        """Detect patterns using rule-based analysis."""
        patterns = []
        
        # Parse code using tree-sitter
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        # Analyze each node
        def traverse(node: tree_sitter.Node):
            # Check for singleton pattern
            if node.type == "class_declaration":
                if self._is_singleton(node):
                    patterns.append(Pattern(
                        type=PatternType.DESIGN_PATTERN,
                        name="singleton",
                        description="Ensures a class has only one instance",
                        severity="info",
                        confidence=0.8,
                        location={"line": node.start_point[0] + 1},
                        context={"class_name": node.child_by_field_name("name").text.decode("utf8")},
                        suggestions=["Consider using dependency injection instead"]
                    ))
                    
            # Check for god class
            if node.type == "class_declaration":
                if self._is_god_class(node):
                    patterns.append(Pattern(
                        type=PatternType.ANTI_PATTERN,
                        name="god_class",
                        description="Class with too many responsibilities",
                        severity="warning",
                        confidence=0.7,
                        location={"line": node.start_point[0] + 1},
                        context={"class_name": node.child_by_field_name("name").text.decode("utf8")},
                        suggestions=["Split into smaller classes", "Use composition over inheritance"]
                    ))
                    
            # Check for long method
            if node.type == "function_definition":
                if self._is_long_method(node):
                    patterns.append(Pattern(
                        type=PatternType.CODE_SMELL,
                        name="long_method",
                        description="Method with too many lines of code",
                        severity="warning",
                        confidence=0.6,
                        location={"line": node.start_point[0] + 1},
                        context={"method_name": node.child_by_field_name("name").text.decode("utf8")},
                        suggestions=["Extract methods", "Use composition"]
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _detect_patterns_ml(self, content: str) -> List[Pattern]:
        """Detect patterns using machine learning models."""
        patterns = []
        
        # 1. Extract features
        features = self._extract_ml_features(content)
        
        # 2. Generate embeddings
        embeddings = self._generate_embeddings(content)
        
        # 3. Cluster similar code blocks
        clusters = self._cluster_code_blocks(embeddings)
        
        # 4. Classify patterns
        classifications = self._classify_patterns(features)
        
        # 5. Generate patterns from results
        for cluster in clusters:
            if cluster["type"] == "duplicate_code":
                patterns.append(Pattern(
                    type=PatternType.CODE_SMELL,
                    name="duplicate_code",
                    description="Similar code blocks repeated in multiple places",
                    severity="warning",
                    confidence=cluster["confidence"],
                    location={"lines": cluster["lines"]},
                    context={"similarity": cluster["similarity"]},
                    suggestions=["Extract common code into a shared function"]
                ))
                
        for classification in classifications:
            if classification["type"] == "memory_leak":
                patterns.append(Pattern(
                    type=PatternType.PERFORMANCE_PATTERN,
                    name="memory_leak",
                    description="Resource not properly released",
                    severity="error",
                    confidence=classification["confidence"],
                    location={"line": classification["line"]},
                    context={"resource_type": classification["resource_type"]},
                    suggestions=["Use context managers", "Implement proper cleanup"]
                ))
                
        return patterns
        
    def _detect_patterns_graph(self, content: str) -> List[Pattern]:
        """Detect patterns using graph analysis."""
        patterns = []
        
        # 1. Build dependency graph
        graph = self._build_dependency_graph(content)
        
        # 2. Analyze graph structure
        cycles = nx.cycle_basis(graph)
        if cycles:
            patterns.append(Pattern(
                type=PatternType.ANTI_PATTERN,
                name="circular_dependency",
                description="Circular dependencies between components",
                severity="error",
                confidence=0.9,
                location={"cycles": cycles},
                context={"graph_size": graph.number_of_nodes()},
                suggestions=["Break circular dependencies", "Use dependency injection"]
            ))
            
        # 3. Analyze node centrality
        centrality = nx.degree_centrality(graph)
        high_centrality_nodes = [node for node, cent in centrality.items() if cent > 0.7]
        if high_centrality_nodes:
            patterns.append(Pattern(
                type=PatternType.ANTI_PATTERN,
                name="hub_class",
                description="Class with too many dependencies",
                severity="warning",
                confidence=0.7,
                location={"nodes": high_centrality_nodes},
                context={"centrality_scores": centrality},
                suggestions=["Reduce dependencies", "Use facade pattern"]
            ))
            
        return patterns
        
    def _detect_patterns_semantic(self, content: str) -> List[Pattern]:
        """Detect patterns using semantic analysis."""
        patterns = []
        
        # 1. Generate semantic embeddings
        embeddings = self._generate_semantic_embeddings(content)
        
        # 2. Analyze semantic relationships
        relationships = self._analyze_semantic_relationships(embeddings)
        
        # 3. Detect semantic patterns
        for rel in relationships:
            if rel["type"] == "violation_of_single_responsibility":
                patterns.append(Pattern(
                    type=PatternType.CODE_SMELL,
                    name="single_responsibility_violation",
                    description="Class or method violates single responsibility principle",
                    severity="warning",
                    confidence=rel["confidence"],
                    location={"line": rel["line"]},
                    context={"responsibilities": rel["responsibilities"]},
                    suggestions=["Split into smaller components", "Use composition"]
                ))
                
        return patterns
        
    def _detect_patterns_statistical(self, content: str) -> List[Pattern]:
        """Detect patterns using statistical analysis."""
        patterns = []
        
        # 1. Calculate code metrics
        metrics = self._calculate_code_metrics(content)
        
        # 2. Analyze statistical patterns
        if metrics["complexity"] > 10:
            patterns.append(Pattern(
                type=PatternType.CODE_SMELL,
                name="high_complexity",
                description="Code with high cyclomatic complexity",
                severity="warning",
                confidence=0.8,
                location={"file": "entire file"},
                context={"complexity": metrics["complexity"]},
                suggestions=["Reduce nesting", "Extract complex logic"]
            ))
            
        if metrics["duplication"] > 0.3:
            patterns.append(Pattern(
                type=PatternType.CODE_SMELL,
                name="high_duplication",
                description="High code duplication ratio",
                severity="warning",
                confidence=0.7,
                location={"file": "entire file"},
                context={"duplication_ratio": metrics["duplication"]},
                suggestions=["Extract common code", "Use inheritance or composition"]
            ))
            
        return patterns
        
    def _merge_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Merge and deduplicate patterns."""
        merged = {}
        
        for pattern in patterns:
            key = (pattern.type, pattern.name, pattern.location["line"])
            if key not in merged or pattern.confidence > merged[key].confidence:
                merged[key] = pattern
                
        return list(merged.values())
        
    def _is_singleton(self, node: tree_sitter.Node) -> bool:
        """Check if a class implements the singleton pattern."""
        has_private_constructor = False
        has_static_instance = False
        has_get_instance = False
        
        for child in node.children:
            if child.type == "constructor_declaration":
                modifiers = [c.text.decode("utf8") for c in child.children if c.type == "modifier"]
                if "private" in modifiers:
                    has_private_constructor = True
            elif child.type == "field_declaration":
                modifiers = [c.text.decode("utf8") for c in child.children if c.type == "modifier"]
                if "static" in modifiers and "private" in modifiers:
                    has_static_instance = True
            elif child.type == "method_declaration":
                name = child.child_by_field_name("name").text.decode("utf8")
                modifiers = [c.text.decode("utf8") for c in child.children if c.type == "modifier"]
                if name == "getInstance" and "static" in modifiers:
                    has_get_instance = True
                    
        return has_private_constructor and has_static_instance and has_get_instance
        
    def _is_god_class(self, node: tree_sitter.Node) -> bool:
        """Check if a class is a god class."""
        method_count = 0
        field_count = 0
        
        for child in node.children:
            if child.type == "method_declaration":
                method_count += 1
            elif child.type == "field_declaration":
                field_count += 1
                
        return method_count > 20 or field_count > 20
        
    def _is_long_method(self, node: tree_sitter.Node) -> bool:
        """Check if a method is too long."""
        return node.end_point[0] - node.start_point[0] > 20
        
    def _extract_ml_features(self, content: str) -> np.ndarray:
        """Extract features for ML-based pattern detection."""
        # Tokenize code
        tokens = self.tokenizer(content, return_tensors="pt", padding=True, truncation=True)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**tokens)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
        return embeddings.numpy()
        
    def _generate_embeddings(self, content: str) -> np.ndarray:
        """Generate embeddings for code blocks."""
        # Split into code blocks
        blocks = self._split_into_blocks(content)
        
        # Generate embeddings for each block
        embeddings = []
        for block in blocks:
            tokens = self.tokenizer(block, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**tokens)
                embedding = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(embedding.numpy())
                
        return np.vstack(embeddings)
        
    def _cluster_code_blocks(self, embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """Cluster similar code blocks."""
        # Scale embeddings
        scaled_embeddings = self.scaler.fit_transform(embeddings)
        
        # Perform clustering
        clusters = self.cluster_model.fit_predict(scaled_embeddings)
        
        # Process clusters
        results = []
        for i in range(len(set(clusters)) - (1 if -1 in clusters else 0)):
            cluster_indices = np.where(clusters == i)[0]
            if len(cluster_indices) > 1:
                results.append({
                    "type": "duplicate_code",
                    "confidence": len(cluster_indices) / len(clusters),
                    "lines": cluster_indices.tolist(),
                    "similarity": np.mean([
                        np.dot(embeddings[i], embeddings[j])
                        for i in cluster_indices
                        for j in cluster_indices
                        if i != j
                    ])
                })
                
        return results
        
    def _classify_patterns(self, features: np.ndarray) -> List[Dict[str, Any]]:
        """Classify patterns using ML models."""
        # Prepare features
        X = self.scaler.fit_transform(features)
        
        # Get predictions
        predictions = self.classifier.predict_proba(X)
        
        # Process predictions
        results = []
        for i, probs in enumerate(predictions):
            if probs[1] > 0.7:  # High confidence for positive class
                results.append({
                    "type": "memory_leak",
                    "confidence": probs[1],
                    "line": i + 1,
                    "resource_type": "unknown"  # Could be determined by additional analysis
                })
                
        return results
        
    def _build_dependency_graph(self, content: str) -> nx.DiGraph:
        """Build a dependency graph from code."""
        graph = nx.DiGraph()
        
        # Parse code
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        # Add nodes and edges
        def traverse(node: tree_sitter.Node):
            if node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                graph.add_node(class_name)
                
                # Add edges for inheritance
                for child in node.children:
                    if child.type == "superclass":
                        superclass = child.text.decode("utf8")
                        graph.add_edge(class_name, superclass)
                        
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return graph
        
    def _generate_semantic_embeddings(self, content: str) -> np.ndarray:
        """Generate semantic embeddings for code."""
        # Split into meaningful units
        units = self._split_into_units(content)
        
        # Generate embeddings
        embeddings = []
        for unit in units:
            tokens = self.tokenizer(unit, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**tokens)
                embedding = outputs.last_hidden_state.mean(dim=1)
                embeddings.append(embedding.numpy())
                
        return np.vstack(embeddings)
        
    def _analyze_semantic_relationships(self, embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze semantic relationships between code units."""
        results = []
        
        # Calculate similarities
        similarities = np.dot(embeddings, embeddings.T)
        
        # Find related units
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                if similarities[i, j] > 0.8:  # High similarity threshold
                    results.append({
                        "type": "violation_of_single_responsibility",
                        "confidence": similarities[i, j],
                        "line": i + 1,
                        "responsibilities": ["responsibility1", "responsibility2"]
                    })
                    
        return results
        
    def _calculate_code_metrics(self, content: str) -> Dict[str, float]:
        """Calculate various code metrics."""
        metrics = {
            "complexity": 0,
            "duplication": 0,
            "maintainability": 0
        }
        
        # Parse code
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        # Calculate cyclomatic complexity
        def count_complexity(node: tree_sitter.Node):
            if node.type in ["if_statement", "while_statement", "for_statement", "switch_statement"]:
                metrics["complexity"] += 1
            for child in node.children:
                count_complexity(child)
                
        count_complexity(tree.root_node)
        
        # Calculate code duplication
        blocks = self._split_into_blocks(content)
        if len(blocks) > 1:
            similarities = np.dot(
                self.vectorizer.fit_transform(blocks).toarray(),
                self.vectorizer.fit_transform(blocks).toarray().T
            )
            metrics["duplication"] = np.mean(similarities[np.triu_indices_from(similarities, k=1)])
            
        # Calculate maintainability index
        metrics["maintainability"] = 1 - (metrics["complexity"] / 100) - metrics["duplication"]
        
        return metrics
        
    def _split_into_blocks(self, content: str) -> List[str]:
        """Split code into logical blocks."""
        blocks = []
        current_block = []
        
        for line in content.split("\n"):
            if line.strip() and not line.startswith(" "):
                if current_block:
                    blocks.append("\n".join(current_block))
                current_block = [line]
            else:
                current_block.append(line)
                
        if current_block:
            blocks.append("\n".join(current_block))
            
        return blocks
        
    def _split_into_units(self, content: str) -> List[str]:
        """Split code into meaningful semantic units."""
        units = []
        
        # Parse code
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        # Extract units
        def extract_units(node: tree_sitter.Node):
            if node.type in ["function_definition", "class_definition", "method_definition"]:
                units.append(node.text.decode("utf8"))
            for child in node.children:
                extract_units(child)
                
        extract_units(tree.root_node)
        return units
        
    def _detect_custom_patterns(self, content: str) -> List[Pattern]:
        """Detect patterns using custom pattern definitions."""
        patterns = []
        
        # Parse code using tree-sitter
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        # Get all custom patterns
        custom_patterns = self.custom_pattern_manager.list_patterns()
        
        def traverse(node: tree_sitter.Node):
            for pattern in custom_patterns:
                if self._matches_custom_pattern(node, pattern):
                    patterns.append(Pattern(
                        type=PatternType(pattern.category.value),
                        name=pattern.name,
                        description=pattern.description,
                        severity=pattern.severity,
                        confidence=0.8,
                        location={"line": node.start_point[0] + 1},
                        context={"node_type": node.type},
                        suggestions=pattern.suggestions,
                        metadata=pattern.metadata
                    ))
                    
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return patterns
        
    def _matches_custom_pattern(self, node: tree_sitter.Node, pattern: PatternRule) -> bool:
        """Check if a node matches a custom pattern definition."""
        for condition in pattern.conditions:
            if not self._matches_condition(node, condition):
                return False
        return True
        
    def _matches_condition(self, node: tree_sitter.Node, condition: Dict[str, Any]) -> bool:
        """Check if a node matches a specific condition."""
        condition_type = condition["type"]
        value = condition["value"]
        
        if condition_type == "node_type":
            return node.type == value
        elif condition_type == "has_child":
            return any(child.type == value for child in node.children)
        elif condition_type == "has_modifier":
            return any(
                child.type == "modifier" and child.text.decode("utf8") == value
                for child in node.children
            )
        elif condition_type == "method_count":
            return len([
                child for child in node.children
                if child.type == "method_declaration"
            ]) >= value
        elif condition_type == "field_count":
            return len([
                child for child in node.children
                if child.type == "field_declaration"
            ]) >= value
        elif condition_type == "complexity":
            return self._calculate_node_complexity(node) >= value
            
        return False
        
    def _detect_circular_dependencies(self, content: str) -> List[Pattern]:
        """Detect circular dependencies using the custom pattern manager."""
        patterns = []
        
        # Analyze circular dependencies
        cycle_analysis = self.custom_pattern_manager.analyze_circular_dependencies(content)
        
        for analysis in cycle_analysis:
            patterns.append(Pattern(
                type=PatternType.ANTI_PATTERN,
                name=f"circular_dependency_{analysis['type']}",
                description=f"Circular dependency detected: {analysis['type']}",
                severity="error" if analysis["impact_score"] > 0.7 else "warning",
                confidence=analysis["impact_score"],
                location={"cycle": analysis["cycle"]},
                context={
                    "cycle_type": analysis["type"],
                    "length": analysis["length"],
                    "edge_types": analysis["edge_types"]
                },
                suggestions=analysis["suggestions"]
            ))
            
        return patterns
        
    def _calculate_node_complexity(self, node: tree_sitter.Node) -> int:
        """Calculate the cyclomatic complexity of a node."""
        complexity = 0
        
        if node.type in ["if_statement", "while_statement", "for_statement", "switch_statement"]:
            complexity += 1
            
        for child in node.children:
            complexity += self._calculate_node_complexity(child)
            
        return complexity 