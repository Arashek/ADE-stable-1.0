from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import os
import logging
from collections import defaultdict
import networkx as nx
from .enhanced_code_analysis import EnhancedCodeAnalyzer
from .language_analyzers import LanguageAnalyzerFactory

logger = logging.getLogger(__name__)

@dataclass
class ProjectMetrics:
    """Metrics for project-level analysis."""
    total_files: int
    total_lines: int
    total_classes: int
    total_functions: int
    total_dependencies: int
    complexity_score: float
    maintainability_score: float
    testability_score: float
    reusability_score: float
    pattern_coverage: float
    code_quality_score: float

@dataclass
class ProjectPattern:
    """Pattern detected at project level."""
    name: str
    type: str
    confidence: float
    impact: float
    files: List[str]
    description: str
    recommendations: List[str]

class ProjectAnalyzer:
    """Analyzes code patterns and metrics at the project level."""
    
    def __init__(self):
        self.enhanced_analyzer = EnhancedCodeAnalyzer()
        self.dependency_graph = nx.DiGraph()
        self.pattern_graph = nx.Graph()
        self.file_metrics = {}
        self.pattern_occurrences = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Perform comprehensive project-level analysis."""
        try:
            # Initialize analysis results
            analysis = {
                "metrics": {},
                "patterns": [],
                "dependencies": {},
                "architecture": {},
                "code_quality": {},
                "recommendations": []
            }
            
            # Analyze all files in the project
            for root, _, files in os.walk(project_path):
                for file in files:
                    if self._is_code_file(file):
                        file_path = os.path.join(root, file)
                        self._analyze_file(file_path)
                        
            # Calculate project metrics
            analysis["metrics"] = self._calculate_project_metrics()
            
            # Detect project-level patterns
            analysis["patterns"] = self._detect_project_patterns()
            
            # Analyze project architecture
            analysis["architecture"] = self._analyze_architecture()
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze project: {e}")
            return {"error": str(e)}
            
    def _is_code_file(self, filename: str) -> bool:
        """Check if a file is a code file."""
        code_extensions = {
            ".py", ".java", ".ts", ".js", ".cpp", ".h", ".hpp", 
            ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt"
        }
        return os.path.splitext(filename)[1].lower() in code_extensions
        
    def _analyze_file(self, file_path: str):
        """Analyze a single file and update project metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            # Determine language
            language = self._detect_language(file_path)
            
            # Get language-specific analyzer
            analyzer = LanguageAnalyzerFactory.create_analyzer(language)
            
            # Parse code
            tree = self.enhanced_analyzer._parse_code(code, language)
            
            # Analyze code
            analysis = self.enhanced_analyzer.analyze_code(code, language, file_path)
            
            # Update file metrics
            self.file_metrics[file_path] = {
                "language": language,
                "metrics": analysis,
                "patterns": analysis["patterns"],
                "dependencies": analysis["dependencies"]
            }
            
            # Update dependency graph
            self._update_dependency_graph(file_path, analysis["dependencies"])
            
            # Update pattern graph
            self._update_pattern_graph(file_path, analysis["patterns"])
            
        except Exception as e:
            logger.error(f"Failed to analyze file {file_path}: {e}")
            
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            ".py": "python",
            ".java": "java",
            ".ts": "typescript",
            ".js": "javascript",
            ".cpp": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin"
        }
        return language_map.get(ext, "unknown")
        
    def _update_dependency_graph(self, file_path: str, dependencies: Dict[str, Any]):
        """Update project dependency graph."""
        # Add file node
        self.dependency_graph.add_node(file_path)
        
        # Add dependency edges
        for dep in dependencies.get("imports", []):
            dep_path = self._resolve_dependency_path(file_path, dep["module"])
            if dep_path:
                self.dependency_graph.add_edge(file_path, dep_path)
                
    def _update_pattern_graph(self, file_path: str, patterns: Dict[str, Any]):
        """Update pattern occurrence graph."""
        # Add file node
        self.pattern_graph.add_node(file_path)
        
        # Add pattern edges
        for pattern in patterns.get("design_patterns", []):
            pattern_name = pattern["type"]
            self.pattern_graph.add_edge(file_path, pattern_name)
            self.pattern_occurrences[pattern_name].append({
                "file": file_path,
                "confidence": pattern["confidence"],
                "location": pattern["location"]
            })
            
    def _resolve_dependency_path(self, source_file: str, module: str) -> Optional[str]:
        """Resolve dependency path to actual file path."""
        # Implementation for resolving module paths
        # This would need to handle different import styles and module resolution
        return None  # Placeholder
        
    def _calculate_project_metrics(self) -> ProjectMetrics:
        """Calculate project-level metrics."""
        total_files = len(self.file_metrics)
        total_lines = sum(metrics["metrics"].get("total_lines", 0) 
                         for metrics in self.file_metrics.values())
        total_classes = sum(len(metrics["metrics"].get("classes", []))
                          for metrics in self.file_metrics.values())
        total_functions = sum(len(metrics["metrics"].get("functions", []))
                            for metrics in self.file_metrics.values())
        total_dependencies = len(self.dependency_graph.edges)
        
        # Calculate average scores
        complexity_score = sum(metrics["metrics"].get("complexity", 0)
                             for metrics in self.file_metrics.values()) / total_files
        maintainability_score = sum(metrics["metrics"].get("maintainability", 0)
                                  for metrics in self.file_metrics.values()) / total_files
        testability_score = sum(metrics["metrics"].get("testability", 0)
                              for metrics in self.file_metrics.values()) / total_files
        reusability_score = sum(metrics["metrics"].get("reusability", 0)
                              for metrics in self.file_metrics.values()) / total_files
        
        # Calculate pattern coverage
        pattern_coverage = len(self.pattern_occurrences) / max(total_classes, 1)
        
        # Calculate overall code quality score
        code_quality_score = (
            maintainability_score * 0.3 +
            testability_score * 0.2 +
            reusability_score * 0.2 +
            (1 - complexity_score) * 0.3
        )
        
        return ProjectMetrics(
            total_files=total_files,
            total_lines=total_lines,
            total_classes=total_classes,
            total_functions=total_functions,
            total_dependencies=total_dependencies,
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            testability_score=testability_score,
            reusability_score=reusability_score,
            pattern_coverage=pattern_coverage,
            code_quality_score=code_quality_score
        )
        
    def _detect_project_patterns(self) -> List[ProjectPattern]:
        """Detect patterns at the project level."""
        patterns = []
        
        # Analyze pattern clusters
        pattern_clusters = self._analyze_pattern_clusters()
        
        # Detect architectural patterns
        arch_patterns = self._detect_architectural_patterns()
        patterns.extend(arch_patterns)
        
        # Detect design pattern clusters
        design_patterns = self._detect_design_pattern_clusters(pattern_clusters)
        patterns.extend(design_patterns)
        
        # Detect anti-pattern clusters
        anti_patterns = self._detect_anti_pattern_clusters()
        patterns.extend(anti_patterns)
        
        return patterns
        
    def _analyze_pattern_clusters(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze clusters of related patterns."""
        clusters = defaultdict(list)
        
        # Group patterns by type
        for pattern_name, occurrences in self.pattern_occurrences.items():
            pattern_type = self._get_pattern_type(pattern_name)
            clusters[pattern_type].extend(occurrences)
            
        return clusters
        
    def _detect_architectural_patterns(self) -> List[ProjectPattern]:
        """Detect architectural patterns in the project."""
        patterns = []
        
        # Analyze dependency structure
        if self._is_layered_architecture():
            patterns.append(ProjectPattern(
                name="Layered Architecture",
                type="architectural",
                confidence=0.8,
                impact=0.7,
                files=list(self.dependency_graph.nodes),
                description="Project follows a layered architecture pattern",
                recommendations=["Consider adding clear layer boundaries"]
            ))
            
        # Analyze component structure
        if self._is_microservices_architecture():
            patterns.append(ProjectPattern(
                name="Microservices Architecture",
                type="architectural",
                confidence=0.7,
                impact=0.6,
                files=list(self.dependency_graph.nodes),
                description="Project exhibits microservices characteristics",
                recommendations=["Consider service discovery mechanisms"]
            ))
            
        return patterns
        
    def _detect_design_pattern_clusters(self, clusters: Dict[str, List[Dict[str, Any]]]) -> List[ProjectPattern]:
        """Detect clusters of related design patterns."""
        patterns = []
        
        # Analyze pattern relationships
        for pattern_type, occurrences in clusters.items():
            if len(occurrences) >= 3:  # Significant pattern cluster
                confidence = self._calculate_pattern_cluster_confidence(occurrences)
                impact = self._calculate_pattern_cluster_impact(occurrences)
                
                patterns.append(ProjectPattern(
                    name=f"{pattern_type.title()} Pattern Cluster",
                    type="design",
                    confidence=confidence,
                    impact=impact,
                    files=[occ["file"] for occ in occurrences],
                    description=f"Significant cluster of {pattern_type} patterns",
                    recommendations=self._generate_pattern_recommendations(pattern_type, occurrences)
                ))
                
        return patterns
        
    def _detect_anti_pattern_clusters(self) -> List[ProjectPattern]:
        """Detect clusters of anti-patterns."""
        patterns = []
        
        # Analyze code smells
        smell_clusters = self._analyze_code_smell_clusters()
        
        for smell_type, occurrences in smell_clusters.items():
            if len(occurrences) >= 3:  # Significant smell cluster
                confidence = self._calculate_smell_cluster_confidence(occurrences)
                impact = self._calculate_smell_cluster_impact(occurrences)
                
                patterns.append(ProjectPattern(
                    name=f"{smell_type.title()} Anti-pattern Cluster",
                    type="anti-pattern",
                    confidence=confidence,
                    impact=impact,
                    files=[occ["file"] for occ in occurrences],
                    description=f"Significant cluster of {smell_type} anti-patterns",
                    recommendations=self._generate_anti_pattern_recommendations(smell_type, occurrences)
                ))
                
        return patterns
        
    def _is_layered_architecture(self) -> bool:
        """Check if project follows layered architecture."""
        # Analyze dependency graph for layer structure
        try:
            # Check for hierarchical structure
            layers = nx.topological_sort(self.dependency_graph)
            return len(list(layers)) > 1
        except nx.NetworkXUnfeasible:
            return False
            
    def _is_microservices_architecture(self) -> bool:
        """Check if project follows microservices architecture."""
        # Analyze component structure and dependencies
        components = nx.connected_components(self.dependency_graph.to_undirected())
        return len(list(components)) > 1
        
    def _calculate_pattern_cluster_confidence(self, occurrences: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for pattern cluster."""
        if not occurrences:
            return 0.0
            
        # Average confidence of individual occurrences
        avg_confidence = sum(occ["confidence"] for occ in occurrences) / len(occurrences)
        
        # Adjust based on cluster size
        size_factor = min(len(occurrences) / 5.0, 1.0)  # Cap at 5 occurrences
        
        return avg_confidence * (0.7 + 0.3 * size_factor)
        
    def _calculate_pattern_cluster_impact(self, occurrences: List[Dict[str, Any]]) -> float:
        """Calculate impact score for pattern cluster."""
        if not occurrences:
            return 0.0
            
        # Calculate impact based on pattern type and distribution
        pattern_type = self._get_pattern_type(occurrences[0]["pattern"])
        base_impact = self._get_pattern_base_impact(pattern_type)
        
        # Adjust based on cluster size and distribution
        size_factor = min(len(occurrences) / 5.0, 1.0)
        distribution_factor = self._calculate_distribution_factor(occurrences)
        
        return base_impact * (0.6 + 0.2 * size_factor + 0.2 * distribution_factor)
        
    def _get_pattern_type(self, pattern_name: str) -> str:
        """Get pattern type from pattern name."""
        pattern_types = {
            "singleton": "creational",
            "factory": "creational",
            "builder": "creational",
            "prototype": "creational",
            "adapter": "structural",
            "bridge": "structural",
            "composite": "structural",
            "decorator": "structural",
            "facade": "structural",
            "flyweight": "structural",
            "proxy": "structural",
            "chain": "behavioral",
            "command": "behavioral",
            "iterator": "behavioral",
            "mediator": "behavioral",
            "memento": "behavioral",
            "observer": "behavioral",
            "state": "behavioral",
            "strategy": "behavioral",
            "template": "behavioral",
            "visitor": "behavioral"
        }
        return pattern_types.get(pattern_name.lower(), "unknown")
        
    def _get_pattern_base_impact(self, pattern_type: str) -> float:
        """Get base impact score for pattern type."""
        impact_scores = {
            "creational": 0.6,
            "structural": 0.7,
            "behavioral": 0.8,
            "architectural": 0.9,
            "unknown": 0.5
        }
        return impact_scores.get(pattern_type, 0.5)
        
    def _calculate_distribution_factor(self, occurrences: List[Dict[str, Any]]) -> float:
        """Calculate distribution factor for pattern occurrences."""
        if not occurrences:
            return 0.0
            
        # Calculate how well distributed the patterns are across files
        files = set(occ["file"] for occ in occurrences)
        total_files = len(self.file_metrics)
        
        return len(files) / total_files
        
    def _generate_pattern_recommendations(self, pattern_type: str, occurrences: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for pattern usage."""
        recommendations = []
        
        # Pattern-specific recommendations
        if pattern_type == "creational":
            recommendations.extend([
                "Consider using dependency injection for better testability",
                "Review singleton usage for potential global state issues"
            ])
        elif pattern_type == "structural":
            recommendations.extend([
                "Consider simplifying complex inheritance hierarchies",
                "Review adapter usage for potential interface bloat"
            ])
        elif pattern_type == "behavioral":
            recommendations.extend([
                "Consider using event-driven patterns for better decoupling",
                "Review observer usage for potential memory leaks"
            ])
            
        # General recommendations
        if len(occurrences) > 5:
            recommendations.append("Consider reducing pattern density for better maintainability")
            
        return recommendations
        
    def _generate_anti_pattern_recommendations(self, smell_type: str, occurrences: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for anti-patterns."""
        recommendations = []
        
        # Smell-specific recommendations
        if smell_type == "god_class":
            recommendations.extend([
                "Break down large classes into smaller, focused classes",
                "Extract common functionality into utility classes"
            ])
        elif smell_type == "long_method":
            recommendations.extend([
                "Extract methods for better readability",
                "Consider using the Command pattern for complex operations"
            ])
        elif smell_type == "duplicate_code":
            recommendations.extend([
                "Create shared utility functions",
                "Consider using inheritance or composition"
            ])
            
        # General recommendations
        if len(occurrences) > 5:
            recommendations.append("Consider implementing automated code quality checks")
            
        return recommendations
        
    def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze project architecture."""
        architecture = {
            "components": [],
            "relationships": [],
            "layers": [],
            "metrics": {}
        }
        
        # Analyze component structure
        components = nx.connected_components(self.dependency_graph.to_undirected())
        for component in components:
            architecture["components"].append({
                "name": f"Component_{len(architecture['components'])}",
                "files": list(component),
                "size": len(component),
                "cohesion": self._calculate_component_cohesion(component)
            })
            
        # Analyze relationships
        for edge in self.dependency_graph.edges:
            architecture["relationships"].append({
                "source": edge[0],
                "target": edge[1],
                "type": self._determine_relationship_type(edge)
            })
            
        # Analyze layers
        try:
            layers = list(nx.topological_sort(self.dependency_graph))
            architecture["layers"] = [
                {
                    "name": f"Layer_{i}",
                    "files": list(layer),
                    "dependencies": self._get_layer_dependencies(layer)
                }
                for i, layer in enumerate(layers)
            ]
        except nx.NetworkXUnfeasible:
            architecture["layers"] = []
            
        # Calculate architecture metrics
        architecture["metrics"] = {
            "component_count": len(architecture["components"]),
            "relationship_count": len(architecture["relationships"]),
            "layer_count": len(architecture["layers"]),
            "coupling": self._calculate_architecture_coupling(),
            "cohesion": self._calculate_architecture_cohesion()
        }
        
        return architecture
        
    def _calculate_component_cohesion(self, component: Set[str]) -> float:
        """Calculate cohesion score for a component."""
        if not component:
            return 0.0
            
        # Calculate internal dependencies
        internal_deps = 0
        total_deps = 0
        
        for file in component:
            for edge in self.dependency_graph.edges(file):
                total_deps += 1
                if edge[1] in component:
                    internal_deps += 1
                    
        if total_deps == 0:
            return 0.0
            
        return internal_deps / total_deps
        
    def _determine_relationship_type(self, edge: Tuple[str, str]) -> str:
        """Determine type of relationship between files."""
        source_ext = os.path.splitext(edge[0])[1].lower()
        target_ext = os.path.splitext(edge[1])[1].lower()
        
        if source_ext == target_ext:
            return "internal"
        elif source_ext in [".h", ".hpp"] and target_ext in [".cpp"]:
            return "implementation"
        else:
            return "external"
            
    def _get_layer_dependencies(self, layer: Set[str]) -> List[str]:
        """Get dependencies for a layer."""
        dependencies = set()
        
        for file in layer:
            for edge in self.dependency_graph.edges(file):
                if edge[1] not in layer:
                    dependencies.add(edge[1])
                    
        return list(dependencies)
        
    def _calculate_architecture_coupling(self) -> float:
        """Calculate overall architecture coupling."""
        if not self.dependency_graph.edges:
            return 0.0
            
        # Calculate ratio of external to internal dependencies
        external_deps = 0
        internal_deps = 0
        
        for edge in self.dependency_graph.edges:
            if self._determine_relationship_type(edge) == "external":
                external_deps += 1
            else:
                internal_deps += 1
                
        total_deps = external_deps + internal_deps
        if total_deps == 0:
            return 0.0
            
        return external_deps / total_deps
        
    def _calculate_architecture_cohesion(self) -> float:
        """Calculate overall architecture cohesion."""
        if not self.dependency_graph.nodes:
            return 0.0
            
        # Calculate average component cohesion
        components = nx.connected_components(self.dependency_graph.to_undirected())
        cohesion_scores = [self._calculate_component_cohesion(component) for component in components]
        
        if not cohesion_scores:
            return 0.0
            
        return sum(cohesion_scores) / len(cohesion_scores)
        
    def _generate_recommendations(self) -> List[str]:
        """Generate project-level recommendations."""
        recommendations = []
        
        # Architecture recommendations
        if self._calculate_architecture_coupling() > 0.7:
            recommendations.append("High coupling detected. Consider implementing better module boundaries.")
            
        if self._calculate_architecture_cohesion() < 0.3:
            recommendations.append("Low cohesion detected. Consider reorganizing related functionality.")
            
        # Pattern recommendations
        pattern_coverage = len(self.pattern_occurrences) / max(len(self.file_metrics), 1)
        if pattern_coverage < 0.2:
            recommendations.append("Low pattern coverage. Consider applying more design patterns.")
            
        # Code quality recommendations
        if self._calculate_project_metrics().code_quality_score < 0.6:
            recommendations.append("Low code quality score. Consider improving code maintainability and testability.")
            
        return recommendations 