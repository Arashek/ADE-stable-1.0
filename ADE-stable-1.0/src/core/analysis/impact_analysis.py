from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import tree_sitter
from pathlib import Path
import re
import json
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np
from .custom_patterns import CustomPatternManager, PatternRule, PatternCategory

logger = logging.getLogger(__name__)

@dataclass
class ImpactAnalysis:
    affected_files: List[str]
    affected_classes: List[str]
    affected_methods: List[str]
    risk_score: float
    propagation_paths: List[List[str]]
    suggestions: List[str]
    metadata: Optional[Dict[str, Any]] = None

class ImpactAnalyzer:
    """Analyzes and visualizes the impact of code patterns and changes."""
    
    def __init__(self):
        """Initialize the impact analyzer."""
        self.dependency_graph = nx.DiGraph()
        self.pattern_manager = CustomPatternManager()
        self.impact_cache = {}
        
    def analyze_impact(self, file_path: str, content: str, pattern: PatternRule) -> ImpactAnalysis:
        """Analyze the impact of a pattern on the codebase."""
        try:
            # Build dependency graph
            self._build_dependency_graph(content)
            
            # Find affected components
            affected_files = self._find_affected_files(file_path)
            affected_classes = self._find_affected_classes(file_path)
            affected_methods = self._find_affected_methods(file_path)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                affected_files,
                affected_classes,
                affected_methods,
                pattern
            )
            
            # Find propagation paths
            propagation_paths = self._find_propagation_paths(file_path)
            
            # Generate suggestions
            suggestions = self._generate_impact_suggestions(
                risk_score,
                affected_files,
                affected_classes,
                affected_methods
            )
            
            return ImpactAnalysis(
                affected_files=affected_files,
                affected_classes=affected_classes,
                affected_methods=affected_methods,
                risk_score=risk_score,
                propagation_paths=propagation_paths,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}")
            return None
            
    def visualize_impact(self, analysis: ImpactAnalysis, output_path: str):
        """Visualize the impact analysis results."""
        try:
            # Create figure with multiple subplots
            fig = plt.figure(figsize=(15, 10))
            
            # 1. Dependency Graph
            ax1 = plt.subplot(221)
            self._plot_dependency_graph(ax1)
            
            # 2. Impact Heatmap
            ax2 = plt.subplot(222)
            self._plot_impact_heatmap(ax2, analysis)
            
            # 3. Risk Distribution
            ax3 = plt.subplot(223)
            self._plot_risk_distribution(ax3, analysis)
            
            # 4. Propagation Paths
            ax4 = plt.subplot(224)
            self._plot_propagation_paths(ax4, analysis)
            
            # Save the visualization
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            
    def _build_dependency_graph(self, content: str):
        """Build a comprehensive dependency graph."""
        self.dependency_graph.clear()
        
        # Parse code
        parser = tree_sitter.Parser()
        tree = parser.parse(bytes(content, "utf8"))
        
        def traverse(node: tree_sitter.Node):
            if node.type == "class_declaration":
                class_name = node.child_by_field_name("name").text.decode("utf8")
                self.dependency_graph.add_node(class_name, type="class")
                
                # Add inheritance edges
                for child in node.children:
                    if child.type == "superclass":
                        superclass = child.text.decode("utf8")
                        self.dependency_graph.add_edge(
                            class_name,
                            superclass,
                            type="inheritance"
                        )
                        
                # Add composition edges
                for child in node.children:
                    if child.type == "field_declaration":
                        field_type = child.child_by_field_name("type").text.decode("utf8")
                        self.dependency_graph.add_edge(
                            class_name,
                            field_type,
                            type="composition"
                        )
                        
            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode("utf8")
                self.dependency_graph.add_node(func_name, type="function")
                
                # Add function call edges
                for child in node.children:
                    if child.type == "call":
                        called_func = child.child_by_field_name("function").text.decode("utf8")
                        self.dependency_graph.add_edge(
                            func_name,
                            called_func,
                            type="call"
                        )
                        
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        
    def _find_affected_files(self, file_path: str) -> List[str]:
        """Find files affected by changes in the given file."""
        affected_files = {file_path}
        
        # Find files that depend on the given file
        for node in self.dependency_graph.nodes():
            if nx.has_path(self.dependency_graph, node, file_path):
                affected_files.add(node)
                
        return list(affected_files)
        
    def _find_affected_classes(self, file_path: str) -> List[str]:
        """Find classes affected by changes in the given file."""
        affected_classes = []
        
        # Find classes that depend on the given file
        for node in self.dependency_graph.nodes():
            if (
                self.dependency_graph.nodes[node].get("type") == "class"
                and nx.has_path(self.dependency_graph, node, file_path)
            ):
                affected_classes.append(node)
                
        return affected_classes
        
    def _find_affected_methods(self, file_path: str) -> List[str]:
        """Find methods affected by changes in the given file."""
        affected_methods = []
        
        # Find methods that depend on the given file
        for node in self.dependency_graph.nodes():
            if (
                self.dependency_graph.nodes[node].get("type") == "function"
                and nx.has_path(self.dependency_graph, node, file_path)
            ):
                affected_methods.append(node)
                
        return affected_methods
        
    def _calculate_risk_score(
        self,
        affected_files: List[str],
        affected_classes: List[str],
        affected_methods: List[str],
        pattern: PatternRule
    ) -> float:
        """Calculate the risk score of the impact."""
        score = 0.0
        
        # Base score from pattern severity
        severity_weights = {
            "error": 0.5,
            "warning": 0.3,
            "info": 0.1
        }
        score += severity_weights.get(pattern.severity, 0.1)
        
        # Impact from affected components
        score += len(affected_files) * 0.1
        score += len(affected_classes) * 0.2
        score += len(affected_methods) * 0.15
        
        # Impact from pattern type
        if pattern.category in [
            PatternCategory.SECURITY,
            PatternCategory.PERFORMANCE
        ]:
            score += 0.2
            
        # Normalize score
        return min(score, 1.0)
        
    def _find_propagation_paths(self, file_path: str) -> List[List[str]]:
        """Find all propagation paths from the given file."""
        paths = []
        
        # Find all paths to dependent nodes
        for node in self.dependency_graph.nodes():
            if node != file_path and nx.has_path(self.dependency_graph, file_path, node):
                path = nx.shortest_path(self.dependency_graph, file_path, node)
                paths.append(path)
                
        return paths
        
    def _generate_impact_suggestions(
        self,
        risk_score: float,
        affected_files: List[str],
        affected_classes: List[str],
        affected_methods: List[str]
    ) -> List[str]:
        """Generate suggestions based on impact analysis."""
        suggestions = []
        
        if risk_score > 0.8:
            suggestions.append("High risk impact detected. Consider breaking down changes into smaller, safer increments.")
            
        if len(affected_files) > 5:
            suggestions.append("Changes affect many files. Consider refactoring to reduce coupling.")
            
        if len(affected_classes) > 3:
            suggestions.append("Multiple classes affected. Consider using interfaces to reduce direct dependencies.")
            
        if len(affected_methods) > 10:
            suggestions.append("Many methods affected. Consider extracting common functionality into shared utilities.")
            
        return suggestions
        
    def _plot_dependency_graph(self, ax):
        """Plot the dependency graph."""
        pos = nx.spring_layout(self.dependency_graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.dependency_graph,
            pos,
            node_color="lightblue",
            node_size=1000,
            ax=ax
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.dependency_graph,
            pos,
            edge_color="gray",
            arrows=True,
            ax=ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.dependency_graph,
            pos,
            font_size=8,
            ax=ax
        )
        
        ax.set_title("Dependency Graph")
        ax.axis("off")
        
    def _plot_impact_heatmap(self, ax, analysis: ImpactAnalysis):
        """Plot impact heatmap."""
        # Create impact matrix
        matrix = np.zeros((len(analysis.affected_files), len(analysis.affected_files)))
        
        # Fill matrix with impact scores
        for i, file1 in enumerate(analysis.affected_files):
            for j, file2 in enumerate(analysis.affected_files):
                if nx.has_path(self.dependency_graph, file1, file2):
                    matrix[i, j] = 1
                    
        # Plot heatmap
        sns.heatmap(
            matrix,
            ax=ax,
            cmap="YlOrRd",
            xticklabels=analysis.affected_files,
            yticklabels=analysis.affected_files
        )
        
        ax.set_title("Impact Heatmap")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        
    def _plot_risk_distribution(self, ax, analysis: ImpactAnalysis):
        """Plot risk distribution."""
        # Calculate risk scores for each component
        risks = []
        labels = []
        
        for file in analysis.affected_files:
            risks.append(analysis.risk_score)
            labels.append(f"File: {file}")
            
        for cls in analysis.affected_classes:
            risks.append(analysis.risk_score * 0.8)
            labels.append(f"Class: {cls}")
            
        for method in analysis.affected_methods:
            risks.append(analysis.risk_score * 0.6)
            labels.append(f"Method: {method}")
            
        # Plot bar chart
        ax.bar(range(len(risks)), risks)
        ax.set_xticks(range(len(risks)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        
        ax.set_title("Risk Distribution")
        ax.set_ylabel("Risk Score")
        
    def _plot_propagation_paths(self, ax, analysis: ImpactAnalysis):
        """Plot propagation paths."""
        # Create a new graph for propagation paths
        path_graph = nx.DiGraph()
        
        # Add nodes and edges for each path
        for path in analysis.propagation_paths:
            for i in range(len(path) - 1):
                path_graph.add_edge(path[i], path[i + 1])
                
        # Draw the graph
        pos = nx.spring_layout(path_graph)
        
        nx.draw_networkx_nodes(
            path_graph,
            pos,
            node_color="lightgreen",
            node_size=1000,
            ax=ax
        )
        
        nx.draw_networkx_edges(
            path_graph,
            pos,
            edge_color="green",
            arrows=True,
            ax=ax
        )
        
        nx.draw_networkx_labels(
            path_graph,
            pos,
            font_size=8,
            ax=ax
        )
        
        ax.set_title("Propagation Paths")
        ax.axis("off")
        
    def export_analysis(self, analysis: ImpactAnalysis, file_path: str):
        """Export impact analysis results to JSON."""
        try:
            analysis_data = {
                "affected_files": analysis.affected_files,
                "affected_classes": analysis.affected_classes,
                "affected_methods": analysis.affected_methods,
                "risk_score": analysis.risk_score,
                "propagation_paths": analysis.propagation_paths,
                "suggestions": analysis.suggestions,
                "metadata": analysis.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(analysis_data, f, indent=2)
                
            logger.info(f"Exported analysis to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
            
    def import_analysis(self, file_path: str) -> Optional[ImpactAnalysis]:
        """Import impact analysis results from JSON."""
        try:
            with open(file_path) as f:
                analysis_data = json.load(f)
                
            return ImpactAnalysis(**analysis_data)
            
        except Exception as e:
            logger.error(f"Error importing analysis: {e}")
            return None 